"""Compile/decode only, CPython 3.8+; executed inside a pinned container."""
from __future__ import annotations

import base64
import dis
import hashlib
import importlib.util
import io
import json
import marshal
import os
import pathlib
import py_compile
import resource
import signal
import subprocess
import sys
import tempfile
import types
import zlib
from .limits import LimitedList, reset

PROFILE = "native-dis-v1"
MAX_OUTPUT = 16 * 1024 * 1024


def graph_code(root, magic):
    reset(100000, 500000)
    nodes, edges = LimitedList("nodes"), LimitedList("edges")
    def node(kind, attrs):
        key = "n%d" % len(nodes)
        nodes.append({"id": key, "kind": kind, "attributes": attrs, "available": list(attrs)})
        if len(nodes) > 100000:
            raise ValueError("graph node cap exceeded")
        return key
    def edge(left, right, kind):
        edges.append({"source": left, "target": right, "kind": kind, "available": ["bytecode"]})
    def visit(code, parent=None):
        fn = node("core:function", {"semantic_kind": "function", "code_name": code.co_name})
        if parent is not None:
            edge(parent, fn, "contains")
        instructions = list(dis.get_instructions(code))
        offsets, branches = {}, []
        previous, terminal = None, False
        jumps = set(getattr(dis, "hasjabs", ())) | set(getattr(dis, "hasjrel", ())) | set(getattr(dis, "hasjump", ()))
        for ins in instructions:
            op = node("core:operation", {"semantic_kind": "operation", "opcode": ins.opname,
                      "argument_kind": type(ins.argval).__name__ if ins.argval is not None else "none"})
            offsets[ins.offset] = op
            edge(fn, op, "contains")
            if previous is not None and not terminal:
                edge(previous, op, "control_next")
            previous = op
            terminal = (ins.opname in {"RETURN_VALUE", "RETURN_CONST", "RAISE_VARARGS", "RERAISE"}
                        or (ins.opname.startswith("JUMP") and "IF" not in ins.opname))
            if ins.opcode in jumps and isinstance(ins.argval, int):
                branches.append((op, ins.argval))
            if ins.is_jump_target:
                edge(fn, op, "control_target")
        for op, target in branches:
            if target not in offsets:
                raise ValueError("branch target outside decoded instructions")
            edge(op, offsets[target], "control_branch")
        # Python 3.11+ exception tables replace some explicit setup opcodes.
        for entry in getattr(dis.Bytecode(code), "exception_entries", ()):
            if entry.target in offsets:
                for offset, op in offsets.items():
                    if entry.start <= offset < entry.end:
                        edge(op, offsets[entry.target], "control_exception")
        for constant in code.co_consts:
            if isinstance(constant, types.CodeType):
                visit(constant, fn)
    visit(root)
    return {"schema_version": 3, "unit_id": "compiled:module", "unit_kind": "module",
            "nodes": nodes, "edges": edges,
            "metadata": {"lane": "bytecode", "parse_status": "valid", "parser": PROFILE,
                         "runtime": "%d.%d" % sys.version_info[:2], "magic": magic,
                         "operand_values": "omitted", "nested_code_objects": "combined"}}


def decode(raw):
    if len(raw) < 16:
        raise ValueError("truncated header")
    if raw[:4] != importlib.util.MAGIC_NUMBER:
        raise ValueError("unsupported magic for this runtime")
    if int.from_bytes(raw[4:8], "little") not in (0, 1, 3):
        raise ValueError("invalid pyc flags")
    stream = io.BytesIO(raw[16:])
    code = marshal.load(stream)
    if not isinstance(code, types.CodeType) or stream.read(1):
        raise ValueError("invalid or trailing marshal payload")
    return graph_code(code, raw[:4].hex())

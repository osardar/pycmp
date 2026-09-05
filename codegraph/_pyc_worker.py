"""Isolated `.pyc` decoder. This module must only run as a subprocess."""
from __future__ import annotations

import dis
import importlib.util
import json
import marshal
import os
import resource
import sys
from types import CodeType


def _limit_resources() -> None:
    # The parent also enforces a wall-clock timeout. Limits cap malformed input.
    def cap(limit: int, desired: int) -> None:
        soft, hard = resource.getrlimit(limit)
        # Keep the inherited hard cap. macOS rejects lowering RLIMIT_AS's hard
        # limit even for the child process; lowering the soft cap is sufficient.
        bounded_soft = desired if hard == resource.RLIM_INFINITY else min(desired, hard)
        try:
            resource.setrlimit(limit, (bounded_soft, hard))
        except ValueError:
            # Darwin does not permit changing RLIMIT_AS in some sandboxed
            # processes. The parent timeout and file-size cap still apply.
            if limit != resource.RLIMIT_AS:
                raise

    cap(resource.RLIMIT_CPU, 5)
    cap(resource.RLIMIT_AS, 256 * 1024 * 1024)
    cap(resource.RLIMIT_FSIZE, 8 * 1024 * 1024)


def _decode_current_runtime(path: str) -> dict:
    raw = open(path, "rb").read()
    if len(raw) < 12:
        raise ValueError("truncated .pyc header")
    magic = raw[:4]
    if magic != importlib.util.MAGIC_NUMBER:
        return _decode_cross_version(path, magic.hex())
    # PEP 552 headers are 16 bytes for supported current CPython releases.
    code = marshal.loads(raw[16:], allow_code=True)
    if not isinstance(code, CodeType):
        raise ValueError(".pyc payload is not a code object")
    return _code_graph(code, path, magic.hex())


def _decode_cross_version(path: str, magic: str) -> dict:
    """Load foreign CPython bytecode through xdis, never the host marshal API."""
    try:
        from xdis.load import load_module
    except ImportError as exc:
        raise ValueError("xdis is required for bytecode from another CPython version") from exc
    version, _timestamp, _magic_int, code, implementation, _source_size, _sip_hash, _offsets = load_module(path)
    name = getattr(code, "co_name", getattr(code, "name", "<module>"))
    # Portable xdis code objects differ by CPython era. Preserve an explicitly
    # partial semantic graph rather than inventing host-runtime opcode meanings.
    graph = _code_graph(code, path, magic) if isinstance(code, CodeType) else {
        "schema_version": 1, "unit_id": f"{path}:bytecode", "unit_kind": "function",
        "nodes": [{"id": "n0", "kind": "core:function", "attributes": {"semantic_kind": "function", "code_name": name},
                   "available": ["semantic_kind", "code_name"]},
                  {"id": "n1", "kind": "core:operation", "attributes": {"semantic_kind": "operation", "opcode": "foreign_bytecode"},
                   "available": ["semantic_kind", "opcode"]}],
        "edges": [{"source": "n0", "target": "n1", "kind": "contains", "available": ["bytecode"]}],
        "metadata": {},
    }
    graph["metadata"].update({"lane": "bytecode", "origin": path, "parser": "xdis",
                              "bytecode_magic": magic, "bytecode_version": ".".join(map(str, version)),
                              "implementation": str(implementation), "parse_status": "partial",
                              "confidence": "medium"})
    return graph


def _code_graph(root: CodeType, origin: str, magic: str) -> dict:
    nodes: list[dict] = []
    edges: list[dict] = []
    next_id = 0

    def add(kind: str, attrs: dict, available: list[str]) -> str:
        nonlocal next_id
        value = f"n{next_id}"
        next_id += 1
        nodes.append({"id": value, "kind": kind, "attributes": attrs, "available": available})
        return value

    def add_code(code: CodeType, parent: str | None = None) -> str:
        fn = add("core:function", {"semantic_kind": "function", "code_name": code.co_name},
                 ["semantic_kind", "code_name"])
        if parent:
            edges.append({"source": parent, "target": fn, "kind": "contains", "available": ["bytecode"]})
        previous = None
        offsets: dict[int, str] = {}
        for instruction in dis.get_instructions(code):
            attrs = {
                "semantic_kind": "operation", "opcode": instruction.opname,
                "argument_kind": type(instruction.argval).__name__ if instruction.argval is not None else "none",
            }
            op = add("core:operation", attrs, list(attrs))
            offsets[instruction.offset] = op
            edges.append({"source": fn, "target": op, "kind": "contains", "available": ["bytecode"]})
            if previous:
                edges.append({"source": previous, "target": op, "kind": "control_next", "available": ["bytecode"]})
            previous = op
            if instruction.is_jump_target:
                edges.append({"source": fn, "target": op, "kind": "control_target", "available": ["bytecode"]})
        for constant in code.co_consts:
            if isinstance(constant, CodeType):
                add_code(constant, fn)
        return fn

    add_code(root)
    return {
        "schema_version": 1, "unit_id": f"{origin}:bytecode", "unit_kind": "function",
        "nodes": nodes, "edges": edges,
        "metadata": {"lane": "bytecode", "origin": origin, "parser": "isolated-cpython-dis",
                     "bytecode_magic": magic, "parse_status": "valid", "confidence": "medium"},
    }


def main() -> None:
    _limit_resources()
    try:
        result = _decode_current_runtime(sys.argv[1])
        print(json.dumps({"ok": True, "graph": result}))
    except Exception as exc:
        print(json.dumps({"ok": False, "error": str(exc)}))
        raise SystemExit(2)


if __name__ == "__main__":
    main()

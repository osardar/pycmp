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

PROFILE = "native-dis-v1"
MAX_OUTPUT = 16 * 1024 * 1024


def graph_code(root, magic):
    nodes, edges = [], []
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


def safe_input(relative):
    root = pathlib.Path("/inputs")
    path = (root / relative).resolve()
    if root not in path.parents or not path.is_file():
        raise ValueError("input outside staged directory")
    if path.stat().st_size > 8 * 1024 * 1024:
        raise ValueError("input size cap exceeded")
    return path


def item(request):
    resource.setrlimit(resource.RLIMIT_CPU, (20, 20))
    resource.setrlimit(resource.RLIMIT_AS, (384 * 1024**2, 384 * 1024**2))
    resource.setrlimit(resource.RLIMIT_FSIZE, (MAX_OUTPUT, MAX_OUTPUT))
    try:
        if request["mode"] == "compile":
            with tempfile.TemporaryDirectory() as directory:
                source = pathlib.Path(directory) / "source.py"
                source.write_bytes(safe_input(request["path"]).read_bytes())
                os.utime(str(source), (946684800, 946684800))
                target = str(pathlib.Path(directory) / "source.pyc")
                try:
                    py_compile.compile(str(source), cfile=target, dfile="source.py", doraise=True,
                                       optimize=int(request["optimization"]))
                except py_compile.PyCompileError as exc:
                    return {"status": "compile_gap", "reason": str(exc)[:2000]}
                raw = pathlib.Path(target).read_bytes()
        elif request["mode"] == "decode":
            raw = safe_input(request["path"]).read_bytes()
        else:
            raise ValueError("compile/decode modes only")
        result = {"artifact_sha256": hashlib.sha256(raw).hexdigest(),
                  "binary": base64.b64encode(raw).decode("ascii")}
        try:
            graph = decode(raw)
            result.update(status="decoded", graph=base64.b64encode(zlib.compress(
                json.dumps(graph, separators=(",", ":")).encode(), 6)).decode("ascii"))
        except Exception as exc:
            result.update(status="decode_failure", reason=str(exc)[:2000])
        return result
    except Exception as exc:
        return {"status": "invalid_input", "reason": str(exc)[:2000]}


def bounded_item(request, seconds=30):
    # Output goes to capped files, never an unbounded PIPE buffer. A new child
    # isolates malformed marshal/dis inputs from the reusable batch process.
    with tempfile.TemporaryFile() as out, tempfile.TemporaryFile() as err:
        proc = subprocess.Popen([sys.executable, __file__, "item"], stdin=subprocess.PIPE,
                                stdout=out, stderr=err, start_new_session=True)
        try:
            proc.communicate(json.dumps(request).encode(), timeout=seconds)
        except subprocess.TimeoutExpired:
            os.killpg(proc.pid, signal.SIGKILL)
            proc.wait()
            return {"status": "timeout"}
        out.seek(0); raw = out.read(MAX_OUTPUT + 1)
        if len(raw) > MAX_OUTPUT:
            return {"status": "output_limit"}
        if proc.returncode:
            return {"status": "worker_failure", "returncode": proc.returncode}
        try:
            return json.loads(raw)
        except ValueError:
            return {"status": "invalid_output"}


if __name__ == "__main__":
    if sys.argv[1:] == ["item"]:
        print(json.dumps(item(json.load(sys.stdin))))
    elif sys.argv[1:] == ["batch"]:
        for request in json.load(sys.stdin):
            print(json.dumps({"job_id": request["job_id"], **bounded_item(request)}), flush=True)
    else:
        raise SystemExit("compile/decode worker: item or batch required")

"""Pinned runtime inventory and bounded subprocess execution."""
import hashlib
import json
import os
from pathlib import Path
import signal
import subprocess
import sys
import tempfile
import time
import psutil

VERSIONS = ("3.8.20", "3.9.25", "3.10.21", "3.11.16", "3.12.14", "3.13.15", "3.14.7")
WORKER = Path(__file__).with_name("worker.py")


def sha(path):
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def implementation():
    root = WORKER.parent
    return hashlib.sha256(json.dumps({str(p.relative_to(root)): sha(p)
        for p in sorted(root.rglob("*.py"))}, sort_keys=True).encode()).hexdigest()


def verify_snapshot():
    root = WORKER.parent
    snapshot = json.loads((root / "SNAPSHOT.json").read_text())
    for row in snapshot["vendored"]:
        path = root / "vendor" / row["path"]
        if path.parent != root / "vendor" or sha(path) != row["sha256"]:
            raise ValueError("representation snapshot mismatch: " + row["path"])


def probe(executable):
    result = subprocess.run([str(executable), "-I", "-S", "-c",
        "import sys,importlib.util,json; print(json.dumps({'version':'.'.join(map(str,sys.version_info[:3])), 'magic':importlib.util.MAGIC_NUMBER.hex()}))"],
        capture_output=True, text=True, timeout=10, check=True)
    return {**json.loads(result.stdout), "executable": str(Path(executable).resolve()), "sha256": sha(executable)}


def inventory(manifest=None, *, require_all=False):
    verify_snapshot()
    manifest = manifest or os.environ.get("PYCMP_RUNTIME_MANIFEST")
    if manifest:
        value = json.loads(Path(manifest).read_text())
        if value.get("implementation") != implementation():
            raise ValueError("runtime implementation fingerprint mismatch")
        rows = value["runtimes"]
        for row in rows:
            if probe(row["executable"]) != row:
                raise ValueError("runtime fingerprint mismatch")
    else:
        rows = [probe(sys.executable)]
    if require_all and {r["version"] for r in rows} != set(VERSIONS):
        raise ValueError("all seven pinned runtimes required; use the container or a runtime manifest")
    if len({r["magic"] for r in rows}) != len(rows):
        raise ValueError("ambiguous bytecode runtime inventory")
    return rows


def parse(executable, mode, raw, *, timeout=30, output_path=None):
    with tempfile.TemporaryDirectory(prefix="pycmp-input-") as directory:
        path = Path(directory) / "input"
        path.write_bytes(raw)
        with tempfile.TemporaryFile() as out, tempfile.TemporaryFile() as err:
            proc = subprocess.Popen([executable, "-I", "-S", str(WORKER), mode, str(path)],
                stdout=out, stderr=err, stdin=subprocess.DEVNULL, start_new_session=True,
                cwd=directory, env={"PATH": "/usr/bin:/bin", "LANG": "C.UTF-8"})
            try:
                deadline = time.monotonic() + timeout
                monitor = psutil.Process(proc.pid)
                while proc.poll() is None:
                    if time.monotonic() >= deadline:
                        raise subprocess.TimeoutExpired(proc.args, timeout)
                    try:
                        if monitor.memory_info().rss > 512 * 1024**2:
                            os.killpg(proc.pid, signal.SIGKILL)
                            proc.wait()
                            return {"error": "memory_limit", "diagnostic": "parser RSS guard reached"}
                    except psutil.NoSuchProcess:
                        pass
                    time.sleep(min(.05, max(0, deadline - time.monotonic())))
            except (subprocess.TimeoutExpired, KeyboardInterrupt):
                os.killpg(proc.pid, signal.SIGKILL)
                proc.wait()
                if sys.exc_info()[0] is KeyboardInterrupt:
                    raise
                return {"error": "timeout", "diagnostic": "parser deadline exceeded"}
            out.seek(0)
            payload = out.read(16 * 1024**2 + 1)
            if len(payload) > 16 * 1024**2:
                return {"error": "output_limit", "diagnostic": "worker output exceeded limit"}
            if proc.returncode:
                return {"error": "worker_failure", "diagnostic": "parser exited %s" % proc.returncode}
            if output_path is not None:
                Path(output_path).write_bytes(payload)
                return {"ok": True}
            try:
                return json.loads(payload)
            except ValueError:
                return {"error": "invalid_output", "diagnostic": "worker returned invalid JSON"}

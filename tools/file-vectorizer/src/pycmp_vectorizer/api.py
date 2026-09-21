"""Streaming input admission, provenance and normalized file vectors."""
from collections import Counter, OrderedDict
import copy
import hashlib
import json
import os
from pathlib import Path
import stat
import tempfile

from . import runtime
from .inference import Encoder, canonical, digest

SUFFIXES = {".py", ".pyi", ".pyc"}
POLICY = {"input_limit", "node_limit", "edge_limit", "output_limit", "memory_limit"}


class Vectorizer:
    def __init__(self, checkpoint, *, runtime_manifest=None, host_runtime=False, include_units=False):
        self.runtimes = runtime.inventory(runtime_manifest, require_all=not host_runtime)
        sources = [r for r in self.runtimes if r["version"].startswith("3.14.")]
        if len(sources) != 1:
            raise ValueError("source parsing requires one Python 3.14 runtime")
        self.source_runtime = sources[0]
        self.by_magic = {r["magic"]: r for r in self.runtimes}
        self.implementation = runtime.implementation()
        self.include_units = include_units
        self.encoder = Encoder(checkpoint)
        self.cache, self.cache_bytes = OrderedDict(), 0
        self.summary = None

    def __enter__(self):
        return self

    def __exit__(self, *_):
        self.close()

    def close(self):
        self.encoder.close()

    def check(self):
        return {"status": "ok", "checkpoint_sha256": self.encoder.checkpoint_sha,
                "dimension": self.encoder.config["dimension"], "implementation_sha256": self.implementation,
                "runtimes": self.runtimes, "all_pinned_runtimes": {r["version"] for r in self.runtimes} == set(runtime.VERSIONS)}

    def profile(self, lane):
        return {"checkpoint_sha256": self.encoder.checkpoint_sha, "graph_schema": 3,
                "lane": lane, "parser_profile": "source-schema3-v1" if lane == "source" else "native-dis-v1",
                "implementation_sha256": self.implementation,
                "feature_keys": self.encoder.config["features"],
                "pooling": "normalized-mean-of-unit-vectors-v1", "normalization": "l2",
                "dimension": self.encoder.config["dimension"]}

    @staticmethod
    def failure(base, code, diagnostic):
        category = ("policy_rejection" if code in POLICY else
                    "unsupported" if code in {"unsupported_format", "unsupported_runtime", "symlink", "not_regular"} else
                    "malformed_input" if code in {"invalid_source", "invalid_input"} else code)
        return {**base, "status": "error", "error": {"category": category, "code": code,
                                                       "diagnostic": str(diagnostic)[:1000]}}

    def vectorize_file(self, path):
        path = Path(path).absolute()
        base = {"schema_version": 1, "record_type": "file", "input_path": str(path),
                "input_sha256": None, "checkpoint_sha256": self.encoder.checkpoint_sha,
                "implementation_sha256": self.implementation}
        if path.suffix not in SUFFIXES:
            return self.failure(base, "unsupported_format", "expected .py, .pyi or .pyc")
        lane = "bytecode" if path.suffix == ".pyc" else "source"
        profile = self.profile(lane)
        base.update(lane=lane, embedding_profile_id=digest(profile), embedding_profile=profile)
        cap = 8 * 1024**2 if lane == "bytecode" else 65536
        try:
            if any(p.is_symlink() for p in (path, *path.parents)):
                return self.failure(base, "symlink", "symlinks are not followed")
            descriptor = os.open(path, os.O_RDONLY | os.O_NONBLOCK | getattr(os, "O_NOFOLLOW", 0))
            with os.fdopen(descriptor, "rb") as handle:
                before = os.fstat(handle.fileno())
                if not stat.S_ISREG(before.st_mode):
                    return self.failure(base, "not_regular", "expected a regular file")
                if before.st_size > cap:
                    return self.failure(base, "input_limit", "input exceeds %d bytes" % cap)
                raw = handle.read(cap + 1)
                after = os.fstat(handle.fileno())
            if len(raw) > cap:
                return self.failure(base, "input_limit", "input exceeds %d bytes" % cap)
            if (before.st_size, before.st_mtime_ns) != (after.st_size, after.st_mtime_ns):
                return self.failure(base, "io_error", "input changed while reading")
        except OSError as exc:
            return self.failure(base, "io_error", exc)
        base["input_sha256"] = hashlib.sha256(raw).hexdigest()
        if lane == "bytecode":
            if len(raw) < 16:
                return self.failure(base, "invalid_input", "truncated bytecode header")
            selected = self.by_magic.get(raw[:4].hex())
            if selected is None:
                return self.failure(base, "unsupported_runtime", "no runtime for magic " + raw[:4].hex())
        else:
            selected = self.source_runtime
        base["runtime"] = {k: v for k, v in selected.items() if k != "executable"}
        base["dependencies"] = {"torch": self.encoder.config["torch"]}
        key = (base["input_sha256"], digest(profile), selected["sha256"], self.include_units)
        if key in self.cache:
            value, size = self.cache.pop(key)
            self.cache[key] = (value, size)
            return {**base, **copy.deepcopy(value), "cache_hit": True}
        with tempfile.TemporaryDirectory(prefix="pycmp-graph-") as directory:
            parsed = Path(directory) / "graphs.json"
            result = runtime.parse(selected["executable"], lane, raw, output_path=parsed)
            if result.get("ok"):
                result = self.encoder.encode(parsed, lane, self.include_units)
        if "error" in result:
            return self.failure(base, result["error"], result.get("diagnostic", "worker failure"))
        value = {"status": "ok", "diagnostics": [], **result}
        if lane == "bytecode":
            value["diagnostics"].append("experimental bytecode profile; operand values omitted")
        elif result["node_count"] == 1:
            value["diagnostics"].append("no substantive statements; similarity may be uninformative")
        size = len(canonical(value).encode())
        if size <= 32 * 1024**2:
            while self.cache and (len(self.cache) >= 128 or self.cache_bytes + size > 32 * 1024**2):
                _, (_, removed) = self.cache.popitem(last=False)
                self.cache_bytes -= removed
            self.cache[key] = (copy.deepcopy(value), size)
            self.cache_bytes += size
        return {**base, **value, "cache_hit": False}

    def vectorize_paths(self, paths, recursive=False):
        counts = {k: 0 for k in ("discovered", "attempted", "succeeded", "failed", "skipped", "cache_hits", "candidates")}
        reasons, failures = Counter(), Counter()
        self.summary = {"schema_version": 1, "record_type": "summary", "completion": "partial",
                        "counts": counts, "skip_reasons": reasons, "failure_reasons": failures}

        def walk(path, explicit=False):
            if path.is_symlink():
                if explicit:
                    yield path
                else:
                    counts["discovered"] += 1; counts["skipped"] += 1; reasons["symlink"] += 1
            elif path.is_dir():
                try:
                    children = sorted(path.iterdir())
                except OSError as exc:
                    yield self.failure({"schema_version": 1, "record_type": "file", "input_path": str(path)}, "io_error", exc)
                    return
                for child in children:
                    if child.is_symlink():
                        yield from walk(child)
                    elif child.is_dir():
                        if recursive:
                            yield from walk(child)
                        else:
                            counts["discovered"] += 1; counts["skipped"] += 1; reasons["directory_not_recursive"] += 1
                    elif child.suffix in SUFFIXES:
                        yield child
                    else:
                        counts["discovered"] += 1; counts["skipped"] += 1; reasons["unsupported_format"] += 1
            else:
                yield path

        for root in paths:
            path = Path(root).absolute()
            if any(p.is_symlink() for p in path.parents):
                items = [self.failure({"schema_version": 1, "record_type": "file", "input_path": str(path)}, "symlink", "symlink ancestor")]
            else:
                items = walk(path, True)
            for item in items:
                counts["discovered"] += 1
                counts["attempted"] += 1
                if isinstance(item, Path) and item.suffix in SUFFIXES:
                    counts["candidates"] += 1
                result = self.vectorize_file(item) if isinstance(item, Path) else item
                if result["status"] == "ok":
                    counts["succeeded"] += 1
                    counts["cache_hits"] += int(result["cache_hit"])
                else:
                    counts["failed"] += 1
                    failures[result["error"]["code"]] += 1
                yield result
        self.summary["completion"] = "complete"

"""Frozen, cross-runtime file and sampled-repository retrieval experiments."""
from __future__ import annotations

import base64
from collections import Counter, defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed
import hashlib
import importlib.metadata
import json
import math
import os
from pathlib import Path
import random
import shlex
import shutil
import sqlite3
import subprocess
import sys
import tempfile
import time
import uuid
import zlib

from .corpus_similarity import atomic_json, sha, _file_vector, _hashed_vector, _rss_bytes
from .bytecode_similarity import opcode_structure
from .semantic import ProgramGraph

RUNTIMES = tuple("3.%d" % minor for minor in range(8, 15))
CONFIGS = tuple((runtime, opt) for runtime in RUNTIMES for opt in range(3))
METHODS = ("trained-seed0", "trained-seed1", "trained-seed2", "untrained-seed0",
           "hashed_graph", "opcode_structure")
AGGREGATORS = ("maximum", "top5", "idf", "assignment")
WORKER = Path(__file__).with_name("_compiled_worker.py")
TOL = 1e-7
REMOVALS = (.1, .3, .5, .7)
INJECTIONS = (.1, .3, .5)
SENTINEL = '''from pathlib import Path
Path('/tmp/CORPUS_EXECUTED').write_text('executed')
def outer(x):
    """optimization evidence"""
    assert x != 0
    total = 0
    for i in range(3):
        if i < x:
            total += i * 2
        else:
            total -= i
    def inner(y):
        return total + y
    try:
        return [inner(i) for i in range(x)]
    except ValueError:
        return []
class Example:
    def values(self):
        yield from (i for i in range(3))
'''


def fingerprint(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def load(path):
    return json.loads(Path(path).read_text())


def lines(path):
    with Path(path).open() as handle:
        for line in handle:
            if line.strip():
                yield json.loads(line)


class Limit(RuntimeError):
    pass


class Budget:
    def __init__(self, root, seconds, disk=100 * 1024**3, rss=8 * 1024**3):
        self.root, self.deadline = root, time.monotonic() + seconds
        self.disk, self.rss, self.last = disk, rss, 0
    def check(self):
        if time.monotonic() >= self.deadline:
            raise Limit("invocation deadline reached")
        if _rss_bytes() > self.rss:
            raise Limit("8 GiB coordinator RSS guard reached")
        if time.monotonic() - self.last > 30:
            size = sum(p.stat().st_size for p in self.root.rglob("*") if p.is_file())
            if size >= self.disk:
                raise Limit("100 GiB cumulative artifact cap reached")
            self.last = time.monotonic()


class Ledger:
    def __init__(self, path):
        self.db = sqlite3.connect(path)
        self.db.execute("PRAGMA journal_mode=WAL")
        self.db.execute("PRAGMA synchronous=FULL")
        self.db.execute("CREATE TABLE IF NOT EXISTS records (stage TEXT, key TEXT, value TEXT, PRIMARY KEY(stage,key))")
    def get(self, stage, key):
        row = self.db.execute("SELECT value FROM records WHERE stage=? AND key=?", (stage, key)).fetchone()
        return json.loads(row[0]) if row else None
    def put(self, stage, key, value):
        with self.db:
            self.db.execute("INSERT OR REPLACE INTO records VALUES (?,?,?)",
                            (stage, key, json.dumps(value, separators=(",", ":"))))
    def rows(self, stage):
        for row in self.db.execute("SELECT value FROM records WHERE stage=? ORDER BY key", (stage,)):
            yield json.loads(row[0])
    def close(self):
        self.db.close()


def checked(args, **kwargs):
    return subprocess.run(args, check=True, capture_output=True, text=True, timeout=60, **kwargs)


def runtime_inventory(output):
    saved = output / "runtime-lock.json"
    if saved.exists():
        records = load(saved)
        for runtime, row in records.items():
            current = json.loads(checked(["docker", "image", "inspect", row["id"]]).stdout)[0]
            if current["Id"] != row["id"]:
                raise ValueError("runtime image mismatch: " + runtime)
        return records
    records = {}
    for runtime in RUNTIMES:
        tag = "python:3.8.20-slim" if runtime == "3.8" else "python:" + runtime + "-slim"
        image = json.loads(checked(["docker", "image", "inspect", tag]).stdout)[0]
        # Docker Desktop may expose the legacy image index without platform
        # fields. The existing release pins 3.8 to linux/amd64 explicitly.
        if runtime == "3.8" and not image.get("Architecture"):
            platform = "linux/amd64"
        else:
            platform = image["Os"] + "/" + image["Architecture"]
        if platform not in {"linux/amd64", "linux/arm64"}:
            raise ValueError("runtime image has unresolved platform metadata: " + runtime)
        version = checked(["docker", "run", "--rm", "--network", "none", "--read-only",
                           "--platform", platform, image["Id"], "python", "-c",
                           "import sys,json; print(json.dumps(list(sys.version_info[:3])))"]).stdout
        version = json.loads(version)
        if ".".join(map(str, version[:2])) != runtime:
            raise ValueError("runtime tag/version mismatch")
        records[runtime] = {"tag": tag, "id": image["Id"], "digests": image.get("RepoDigests", []),
                            "platform": platform, "version": version}
    atomic_json(saved, records)
    return records


def initialize(parent, output, checkpoints, resume):
    if parent == output or parent in output.parents:
        raise ValueError("use a separate output directory outside the input run")
    if output.exists() and not resume:
        raise ValueError("output exists; use --resume or a new directory")
    required = ["definition.json", "BUILD-expansion-COMPLETE.json", "EVALUATION-expansion-COMPLETE.json",
                "gallery.json", "variants-expansion.json", "variant-provenance-expansion.json", "jobs/compile.jsonl"]
    inputs = {p: sha(parent / p) for p in required}
    old = load(parent / "definition.json")
    if old.get("reserved_hardpair_families_accessed") is not False:
        raise ValueError("reserved-family provenance missing")
    actual = [sha(p) for p in checkpoints]
    if len(actual) != 3 or actual != [x["sha256"] for x in old["preflight"]["checkpoints"]]:
        raise ValueError("checkpoint mismatch")
    output.mkdir(parents=True, exist_ok=True)
    runtimes = runtime_inventory(output)
    definition = {"format": 1, "experiment": "expanded-compiled-retrieval", "parent": str(parent),
                  "inputs": inputs, "checkpoints": actual, "runtimes": runtimes,
                  "code": {p.name: sha(p) for p in sorted(WORKER.parent.glob("*.py"))},
                  "tests": sha(WORKER.parent.parent / "tests" / "test_compiled_retrieval.py"),
                  "environment": {"python": sys.version, **{name: importlib.metadata.version(name)
                                  for name in ("torch", "numpy", "scipy")}},
                  "configs": CONFIGS, "methods": METHODS, "aggregators": AGGREGATORS,
                  "decoder_profile": "native-dis-v1", "tie_tolerance": TOL,
                  "resources": {"workers": 4, "worker_mib": 512, "rss_gib": 8, "disk_gib": 100},
                  "removals": REMOVALS, "injections": INJECTIONS, "seeds": [0, 1, 2]}
    target = output / "definition.json"
    if target.exists() and fingerprint(load(target)) != fingerprint(definition):
        raise ValueError("definition fingerprint mismatch; use a new run directory")
    if not target.exists():
        atomic_json(target, definition)
    return definition


def stage_file(path, target, digest):
    if sha(path) != digest:
        raise ValueError("source/artifact checksum mismatch: " + str(path))
    if target.exists():
        if sha(target) != digest:
            raise ValueError("staged checksum mismatch")
        return
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(path, target)


def manifests(parent, output, budget):
    gallery = load(parent / "gallery.json")
    variants = load(parent / "variants-expansion.json")
    provenance = load(parent / "variant-provenance-expansion.json")
    sources = {row["source_sha256"]: row for row in gallery + variants}
    for digest, row in sources.items():
        budget.check()
        stage_file(parent / row["path"], output / "staged" / (digest + ".py"), digest)
    observations = {}
    for row in provenance:
        key = (row["query_gallery_id"], row["variant_sha256"])
        observations.setdefault(key, {"origin": key[0], "source": key[1], "owner": row["owner"], "recipes": []})
        observations[key]["recipes"].append({k: row.get(k) for k in
            ("family", "seed", "requested_dose", "actual_dose", "status")})
    bundles = {}
    for row in gallery:
        for owner in row["owners"]:
            if owner.get("fixture") != "source":
                continue
            key = owner["repository"]
            bundle = bundles.setdefault(key, {"repository": key, "owner": owner, "sources": []})
            if bundle["owner"]["split_group"] != owner["split_group"] or bundle["owner"]["split"] != owner["split"]:
                raise ValueError("repository split-group conflict: " + key)
            if row["source_sha256"] not in bundle["sources"]:
                bundle["sources"].append(row["source_sha256"])
    bundles = [x for x in bundles.values() if len(x["sources"]) >= 5]
    for x in bundles:
        x["sources"].sort()
    value = {"gallery": gallery, "observations": list(observations.values()),
             "sources": sorted(sources), "bundles": sorted(bundles, key=lambda x: x["repository"])}
    atomic_json(output / "manifests.json", value, compact=True)
    return value


class Worker:
    def __init__(self, image, staged):
        self.name = "pycmp-expanded-" + uuid.uuid4().hex
        self.closed = False
        self.deadline = float("inf")
        checked(["docker", "run", "-d", "--name", self.name, "--network", "none", "--read-only",
                 "--platform", image["platform"], "--user", "65534:65534", "--pids-limit", "64",
                 "--memory", "512m", "--cpus", "1", "--cap-drop", "ALL", "--security-opt", "no-new-privileges",
                 "--tmpfs", "/tmp:rw,size=128m", "-v", str(staged.resolve()) + ":/inputs:ro",
                 "-v", str(WORKER.resolve()) + ":/worker.py:ro", image["id"],
                 "python", "-c", "import time; time.sleep(86400)"])
    def batch(self, requests):
        with tempfile.TemporaryFile() as out, tempfile.TemporaryFile() as err:
            proc = subprocess.Popen(["docker", "exec", "-i", self.name, "python", "/worker.py", "batch"],
                                    stdin=subprocess.PIPE, stdout=out, stderr=err)
            try:
                proc.communicate(json.dumps(requests).encode(), timeout=max(.01, min(
                    35 * len(requests) + 20, self.deadline - time.monotonic())))
            except subprocess.TimeoutExpired:
                self.close()
                proc.kill(); proc.wait()
                return [{"job_id": r["job_id"], "status": "timeout"} for r in requests]
            out.seek(0)
            result = []
            for line in out:
                if len(line) > 16 * 1024**2:
                    raise ValueError("worker output cap")
                result.append(json.loads(line))
            by_id = {r["job_id"]: r for r in result}
            return [by_id.get(r["job_id"], {"job_id": r["job_id"], "status": "worker_failure"}) for r in requests]
    def close(self):
        if not self.closed:
            subprocess.run(["docker", "rm", "-f", self.name], capture_output=True, timeout=30)
            self.closed = True


def smoke(output, definition, ledger, budget):
    path = output / "staged" / "owned-sentinel.py"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(SENTINEL)
    for runtime in RUNTIMES:
        budget.check()
        if ledger.get("smoke", runtime):
            continue
        worker = Worker(definition["runtimes"][runtime], output / "staged")
        try:
            results = worker.batch([{"job_id": str(opt), "mode": "compile", "path": path.name,
                                     "optimization": opt} for opt in range(3)])
            if not all(x["status"] == "decoded" for x in results):
                raise ValueError("owned runtime smoke failed: " + runtime + " " + str(results))
            checked(["docker", "exec", worker.name, "python", "-c",
                     "import os; assert not os.path.exists('/tmp/CORPUS_EXECUTED')"])
            graph0 = json.loads(zlib.decompress(base64.b64decode(results[0]["graph"])))
            if not any(e["kind"] == "control_branch" for e in graph0["edges"]):
                raise ValueError("owned branch evidence missing")
            ledger.put("smoke", runtime, {"runtime": runtime, "status": "passed", "executed": False,
                       "artifacts": [x["artifact_sha256"] for x in results]})
        finally:
            worker.close()


def compile_key(source, runtime, opt):
    return fingerprint([source, runtime, opt])


def prepare(parent, output, definition, manifest, ledger, budget):
    old = load(parent / "definition.json")["preflight"]
    reusable = {}
    old_worker_ok = old["worker_hashes"].get("_compile_only_worker.py") == sha(WORKER.with_name("_compile_only_worker.py"))
    if old_worker_ok:
        for row in lines(parent / "jobs" / "compile.jsonl"):
            rt = row["runtime"]
            if rt in RUNTIMES and old["images"][rt]["id"] == definition["runtimes"][rt]["id"]:
                reusable[compile_key(row["source_sha256"], rt, row["optimization"])] = row
    for runtime in RUNTIMES:
        pending = []
        for source in manifest["sources"]:
            budget.check()
            for opt in range(3):
                key = compile_key(source, runtime, opt)
                if ledger.get("compile", key):
                    continue
                request = {"job_id": key, "source": source, "runtime": runtime, "optimization": opt,
                           "mode": "compile", "path": source + ".py"}
                old_row = reusable.get(key)
                if old_row and old_row["status"] == "compile_gap":
                    ledger.put("compile", key, {**request, "status": "compile_gap", "reused": True})
                    continue
                if old_row and old_row["status"] == "compiled":
                    artifact = old_row["artifact_sha256"]
                    target = output / "staged" / (artifact + ".pyc")
                    stage_file(parent / old_row["artifact_path"], target, artifact)
                    request.update(mode="decode", path=target.name, reused=True)
                pending.append(request)
        if not pending:
            continue
        print(json.dumps({"stage": "prepare", "runtime": runtime, "pending": len(pending)}), flush=True)
        workers = []
        try:
            for _ in range(4):
                worker = Worker(definition["runtimes"][runtime], output / "staged")
                worker.deadline = budget.deadline
                workers.append(worker)
            batches = iter([pending[i:i + 8] for i in range(0, len(pending), 8)])
            with ThreadPoolExecutor(max_workers=4) as pool:
                futures = {}
                for worker in workers:
                    batch = next(batches, None)
                    if batch:
                        futures[pool.submit(worker.batch, batch)] = (worker, batch)
                while futures:
                    budget.check()
                    future = next(as_completed(futures))
                    budget.check()
                    worker, batch = futures.pop(future)
                    for request, result in zip(batch, future.result()):
                        if "binary" in result:
                            binary = base64.b64decode(result.pop("binary"))
                            artifact = result["artifact_sha256"]
                            if hashlib.sha256(binary).hexdigest() != artifact:
                                raise ValueError("worker artifact checksum mismatch")
                            dest = output / "binaries" / (artifact + ".pyc")
                            dest.parent.mkdir(exist_ok=True)
                            if not dest.exists():
                                dest.write_bytes(binary)
                        if "graph" in result:
                            packed = base64.b64decode(result.pop("graph"))
                            graph = ProgramGraph.from_dict(json.loads(zlib.decompress(packed)))
                            if graph.metadata.get("runtime") != runtime or graph.metadata.get("parser") != "native-dis-v1":
                                raise ValueError("worker graph profile mismatch")
                            dest = output / "graphs" / (artifact + ".json.z")
                            dest.parent.mkdir(exist_ok=True)
                            if not dest.exists():
                                dest.write_bytes(packed)
                            result["graph_sha256"] = sha(dest)
                        ledger.put("compile", request["job_id"], {**request, **result})
                    if worker.closed:
                        raise Limit("worker terminated on timeout; resume pending jobs")
                    batch = next(batches, None)
                    if batch:
                        futures[pool.submit(worker.batch, batch)] = (worker, batch)
        finally:
            for worker in workers:
                worker.close()
    coverage = Counter((r["runtime"], r["status"]) for r in ledger.rows("compile"))
    if sum(coverage.values()) != len(manifest["sources"]) * len(CONFIGS):
        raise ValueError("incomplete preparation accounting")
    atomic_json(output / "PREPARED.json", {"status": "complete", "jobs": sum(coverage.values()),
                "expected": len(manifest["sources"]) * len(CONFIGS),
                "coverage": {"/".join(k): v for k, v in coverage.items()}})


def tensor_facts(graph, model):
    from .shared_model import FEATURE_KEYS, graph_tensors
    features = [[n.kind, {k: n.attributes[k] for k in FEATURE_KEYS if k in n.attributes}] for n in graph.nodes]
    positions = {n.id: i for i, n in enumerate(graph.nodes)}
    edges = [(positions[e.source], positions[e.target], e.kind, e.attributes) for e in graph.edges]
    tensors = graph_tensors(graph, node_buckets=model.node_buckets, relation_buckets=model.relation_buckets)
    return {"features": fingerprint([features, edges]),
            "tensors": fingerprint({k: v.tolist() for k, v in tensors.items()})}


def embed(output, ledger, checkpoints, budget):
    import torch
    from .shared_model import SharedGraphEncoder
    from .workflow import _load_model
    torch.set_num_threads(1)
    models = {"trained-seed%d" % i: _load_model(path).eval() for i, path in enumerate(checkpoints)}
    reference = models["trained-seed0"]
    torch.manual_seed(0)
    models["untrained-seed0"] = SharedGraphEncoder(dimension=reference.dimension, layers=len(reference.layers),
        node_buckets=reference.node_buckets, relation_buckets=reference.relation_buckets).eval()
    seen = set()
    for row in ledger.rows("compile"):
        budget.check()
        if row["status"] != "decoded" or row["artifact_sha256"] in seen:
            continue
        artifact = row["artifact_sha256"]
        seen.add(artifact)
        if ledger.get("embedding", artifact):
            continue
        path = output / "graphs" / (artifact + ".json.z")
        if sha(path) != row["graph_sha256"]:
            raise ValueError("graph checksum mismatch")
        graph = ProgramGraph.from_dict(json.loads(zlib.decompress(path.read_bytes())))
        vectors = {name: _file_vector(model, [graph])[0].tolist() for name, model in models.items()}
        vectors["hashed_graph"] = _hashed_vector([graph]).tolist()
        ledger.put("embedding", artifact, {"artifact": artifact, "vectors": vectors,
                    "opcode_structure": dict(opcode_structure(graph)), "facts": tensor_facts(graph, reference)})
        if len(seen) % 250 == 0:
            print(json.dumps({"stage": "embedding", "visited": len(seen)}), flush=True)


def ranked(scores, ids, origins, lineage):
    own = [i for i, key in enumerate(ids) if key in origins]
    if not own:
        return {"status": "missing_origin"}
    if not all(math.isfinite(float(x)) for x in scores):
        return {"status": "invalid_query"}
    score = max(float(scores[i]) for i in own)
    rank = 1 + sum(float(s) >= score - TOL for s, key in zip(scores, ids) if key not in origins)
    other = max((float(s) for s, key in zip(scores, ids) if key not in lineage), default=None)
    return {"status": "ok", "cosine": score, "rank": rank, "hit1": int(rank == 1),
            "hit5": int(rank <= 5), "hit10": int(rank <= 10), "mrr": 1 / rank,
            "margin": None if other is None else score - other,
            "tied_non_origins": sum(abs(float(s) - score) <= TOL for s, key in zip(scores, ids) if key not in origins)}


def matrices(embeddings, artifacts):
    import torch
    values = {method: torch.tensor([embeddings[a]["vectors"][method] for a in artifacts])
              for method in METHODS[:-1]}
    return values


def similarity(query_artifacts, candidate_artifacts, embeddings):
    import torch
    q = matrices(embeddings, query_artifacts)
    g = matrices(embeddings, candidate_artifacts)
    values = {method: (q[method] @ g[method].T).clamp(-1, 1).tolist() for method in METHODS[:-1]}
    # Sparse feature dot products through an inverted gallery index.
    inverted = defaultdict(list)
    norms = []
    for i, a in enumerate(candidate_artifacts):
        counts = embeddings[a]["opcode_structure"]
        norm = math.sqrt(sum(v*v for v in counts.values()))
        norms.append(norm)
        for k, v in counts.items():
            inverted[k].append((i, v / norm if norm else 0))
    sparse = []
    for a in query_artifacts:
        counts = embeddings[a]["opcode_structure"]
        norm = math.sqrt(sum(v*v for v in counts.values()))
        scores = [0.] * len(candidate_artifacts)
        if norm:
            for k, v in counts.items():
                for i, value in inverted.get(k, ()):
                    scores[i] += v / norm * value
        sparse.append([max(-1., min(1., s)) for s in scores])
    values["opcode_structure"] = sparse
    return values


def compile_index(ledger):
    return {(r["source"], r["runtime"], r["optimization"]): r for r in ledger.rows("compile")}


def artifact_for(index, source, config):
    row = index.get((source, *config), {})
    return row.get("artifact_sha256") if row.get("status") == "decoded" else None


def evaluate_files(manifest, ledger, budget, *, pilot=False):
    index = compile_index(ledger)
    embeddings = {r["artifact"]: r for r in ledger.rows("embedding")}
    small = {x["origin"] for x in manifest["observations"] if any(r["family"] == "unchanged" for r in x["recipes"])}
    gallery = manifest["gallery"]
    by_id = {x["gallery_id"]: x for x in gallery}
    group_ids = defaultdict(set)
    for row in gallery:
        for owner in row["owners"]:
            group_ids[owner["split_group"]].add(row["gallery_id"])
    observations = manifest["observations"]
    if pilot:
        chosen = {}
        for family in ("unchanged", "formatting", "rename", "literal", "operator", "structural", "partial", "combined"):
            eligible = [o for o in observations if any(r["family"] == family and r["status"] in
                        (("applied", "unchanged") if family in ("unchanged", "formatting") else ("applied",)) for r in o["recipes"])
                        and all(artifact_for(index, o["source"], c) and
                                artifact_for(index, by_id[o["origin"]]["source_sha256"], c) for c in CONFIGS)]
            if not eligible:
                raise ValueError("pilot recipe coverage gap: " + family)
            row = min(eligible, key=fingerprint)
            chosen[(row["origin"], row["source"])] = row
        observations = list(chosen.values())
    stage = "file-pilot" if pilot else "file"
    for qconfig in CONFIGS:
        dedup = {}
        for obs in observations:
            artifact = artifact_for(index, obs["source"], qconfig)
            key = (obs["origin"], artifact or obs["source"])
            row = dedup.setdefault(key, {**obs, "artifact": artifact, "recipes": []})
            row["recipes"].extend(obs["recipes"])
        for gconfig in CONFIGS:
            budget.check()
            cell = fingerprint([qconfig, gconfig])
            if ledger.get(stage + "-cell", cell):
                continue
            candidates = [r for r in gallery if artifact_for(index, r["source_sha256"], gconfig)]
            ids = [r["gallery_id"] for r in candidates]
            artifacts = [artifact_for(index, r["source_sha256"], gconfig) for r in candidates]
            matched = {r["gallery_id"] for r in candidates if artifact_for(index, r["source_sha256"], qconfig)}
            modes = {"full_available": list(range(len(ids))),
                     "full_matched": [i for i, gid in enumerate(ids) if gid in matched],
                     "small_paired": [i for i, gid in enumerate(ids) if gid in small and gid in matched]}
            # Controls exist for every query origin, independently of pilot recipe selection.
            controls = {}
            for origin in {x["origin"] for x in observations}:
                a = artifact_for(index, by_id[origin]["source_sha256"], qconfig)
                b = artifact_for(index, by_id[origin]["source_sha256"], gconfig)
                if a and b:
                    controls[origin] = {m: v[0][0] for m, v in similarity([a], [b], embeddings).items()}
            pending = []
            for obs in dedup.values():
                key = fingerprint([qconfig, gconfig, obs["origin"], obs["artifact"] or obs["source"]])
                if not ledger.get(stage, key):
                    pending.append((key, obs))
            for start in range(0, len(pending), 32):
                budget.check()
                batch = pending[start:start+32]
                valid = [(k, o) for k, o in batch if o["artifact"]]
                scores = similarity([o["artifact"] for _, o in valid], artifacts, embeddings) if valid and artifacts else {}
                scored = {k: i for i, (k, _) in enumerate(valid)}
                for key, obs in batch:
                    origin = obs["origin"]
                    own = artifact_for(index, by_id[origin]["source_sha256"], gconfig)
                    result = {"key": key, "query_config": qconfig, "gallery_config": gconfig,
                              "origin": origin, "owner": obs["owner"], "artifact": obs["artifact"],
                              "recipes": obs["recipes"], "scores": {},
                              "exact_binary": bool(own and own == obs["artifact"]),
                              "tensor_equal": None, "feature_equal": None}
                    if own and obs["artifact"]:
                        result["tensor_equal"] = embeddings[own]["facts"]["tensors"] == embeddings[obs["artifact"]]["facts"]["tensors"]
                        result["feature_equal"] = embeddings[own]["facts"]["features"] == embeddings[obs["artifact"]]["facts"]["features"]
                    for mode, positions in modes.items():
                        metrics = {}
                        for method in METHODS:
                            if not obs["artifact"]:
                                metric = {"status": "invalid_query"}
                            elif mode != "full_available" and origin not in matched:
                                metric = {"status": "missing_origin"}
                            elif not scores:
                                metric = {"status": "missing_origin"}
                            else:
                                metric = ranked([scores[method][scored[key]][i] for i in positions],
                                    [ids[i] for i in positions], {origin}, group_ids[obs["owner"]["split_group"]])
                            metric["gallery_size"] = len(positions)
                            metric["control_delta"] = (metric["cosine"] - controls[origin][method]
                                if metric["status"] == "ok" and origin in controls else None)
                            metrics[method] = metric
                        result["scores"][mode] = metrics
                    ledger.put(stage, key, result)
            ledger.put(stage + "-cell", cell, {"query": qconfig, "gallery": gconfig, "queries": len(dedup)})
            print(json.dumps({"stage": stage, "query": qconfig, "gallery": gconfig}), flush=True)


def ordered(values, seed):
    return sorted(set(values), key=lambda v: fingerprint([seed, v]))


def bundle_queries(manifest):
    mutations = {}
    for row in manifest["observations"]:
        if any(r["family"] == "combined" and r["seed"] == 0 and r["requested_dose"] == .3 and r["status"] == "applied" for r in row["recipes"]):
            origin = next(g["source_sha256"] for g in manifest["gallery"] if g["gallery_id"] == row["origin"])
            mutations[origin] = row["source"]
    queries = []
    for bundle in manifest["bundles"]:
        original = bundle["sources"]
        variants = [("unchanged", 0, 0., 0.)]
        for seed in range(3):
            variants += [("remove", seed, d, 0.) for d in REMOVALS]
            variants += [("inject", seed, 0., d) for d in INJECTIONS]
            variants += [("combined", seed, rem, inj) for rem, inj in zip(REMOVALS, (.1, .3, .5, .5))]
        donors = [b for b in manifest["bundles"] if b["owner"]["split"] == bundle["owner"]["split"] and
                  b["owner"]["split_group"] != bundle["owner"]["split_group"]]
        donor_sources = defaultdict(set)
        for donor in donors:
            for source in donor["sources"]:
                if source not in original:
                    donor_sources[source].add(donor["repository"])
        for family, seed, removal, injection in variants:
            removed = set(ordered(original, seed)[:min(len(original)-1, math.floor(len(original)*removal))])
            # The same ordered donor pool is reused across perturbations.
            injected = ordered(donor_sources, seed)[:math.ceil(len(original)*injection)]
            query = {"origin": bundle["repository"], "owner": bundle["owner"], "family": family,
                     "seed": seed, "removal": removal, "injection": injection,
                     "sources": sorted(set(original) - removed) + injected,
                     "injected": injected, "donors": sorted({d for s in injected for d in donor_sources[s]}),
                     "actual_removed": len(removed), "actual_injected": len(injected)}
            query["key"] = fingerprint(query)
            queries.append(query)
        changed = [mutations.get(s, s) for s in original]
        query = {"origin": bundle["repository"], "owner": bundle["owner"], "family": "mutated",
                 "seed": 0, "removal": 0., "injection": 0., "sources": changed, "injected": [], "donors": [],
                 "actual_replaced": sum(a != b for a, b in zip(original, changed))}
        query["key"] = fingerprint(query)
        queries.append(query)
    return queries


def assignment(matrix):
    """Maximum positive-weight rectangular assignment; unmatched rows score zero."""
    # scipy is optional; the Hungarian fallback keeps the runner self-contained.
    if not matrix or not matrix[0]:
        return []
    try:
        import numpy as np
        from scipy.optimize import linear_sum_assignment
        values = np.array(matrix)
        rows, cols = linear_sum_assignment(np.maximum(values, 0), maximize=True)
        return [(int(i), int(j), float(values[i, j])) for i, j in zip(rows, cols) if values[i, j] > 0]
    except ImportError:
        pass
    n, m = len(matrix), len(matrix[0])
    transpose = n > m
    a = list(map(list, zip(*matrix))) if transpose else matrix
    n, m = len(a), len(a[0])
    u, v, p, way = [0.]*(n+1), [0.]*(m+1), [0]*(m+1), [0]*(m+1)
    for i in range(1, n+1):
        p[0], j0 = i, 0
        minimum, used = [float("inf")]*(m+1), [False]*(m+1)
        while True:
            used[j0] = True
            i0, delta, j1 = p[j0], float("inf"), 0
            for j in range(1, m+1):
                if not used[j]:
                    cost = -max(0., a[i0-1][j-1]) - u[i0] - v[j]
                    if cost < minimum[j]:
                        minimum[j], way[j] = cost, j0
                    if minimum[j] < delta:
                        delta, j1 = minimum[j], j
            for j in range(m+1):
                if used[j]:
                    u[p[j]] += delta; v[j] -= delta
                else:
                    minimum[j] -= delta
            j0 = j1
            if p[j0] == 0:
                break
        while True:
            j1 = way[j0]; p[j0] = p[j1]; j0 = j1
            if j0 == 0:
                break
    result = []
    for j in range(1, m+1):
        if p[j] and a[p[j]-1][j-1] > 0:
            i0, j0 = p[j]-1, j-1
            result.append((j0, i0, a[i0][j0]) if transpose else (i0, j0, a[i0][j0]))
    return result


def aggregate(matrix, weights):
    if not matrix or not matrix[0]:
        return {name: None for name in AGGREGATORS}, []
    best = [max(row) for row in matrix]
    pairs = assignment(matrix)
    return {"maximum": max(best), "top5": sum(sorted(best, reverse=True)[:5])/min(5, len(best)),
            "idf": sum(a*b for a, b in zip(best, weights))/sum(weights),
            "assignment": sum(s for _, _, s in pairs)/len(matrix)}, pairs


def evaluate_bundles(manifest, ledger, budget, *, pilot=False):
    index = compile_index(ledger)
    embeddings = {r["artifact"]: r for r in ledger.rows("embedding")}
    queries = bundle_queries(manifest)
    if pilot:
        queries = [min((q for q in queries if q["family"] == f), key=lambda x: x["key"])
                   for f in ("unchanged", "remove", "inject", "combined", "mutated")]
    stage = "bundle-pilot" if pilot else "bundle"
    bundles = manifest["bundles"]
    frequency = Counter(s for b in bundles for s in set(b["sources"]))
    for qconfig in CONFIGS:
        for gconfig in CONFIGS:
            budget.check()
            cell = fingerprint([qconfig, gconfig])
            if ledger.get(stage + "-cell", cell):
                continue
            candidate_sources = {b["repository"]: [s for s in b["sources"] if artifact_for(index, s, gconfig)] for b in bundles}
            candidate_sources = {k: v for k, v in candidate_sources.items() if len(v) >= 5}
            ids = sorted(candidate_sources)
            for query in queries:
                budget.check()
                key = fingerprint([query["key"], qconfig, gconfig])
                if ledger.get(stage, key):
                    continue
                sources = sorted(set(s for s in query["sources"] if artifact_for(index, s, qconfig)))
                result = {"key": key, "query": query["key"], "origin": query["origin"], "owner": query["owner"],
                          "family": query["family"], "removal": query["removal"], "injection": query["injection"],
                          "actual_removed": query.get("actual_removed", 0),
                          "actual_injected": query.get("actual_injected", 0),
                          "actual_replaced": query.get("actual_replaced", 0),
                          "query_config": qconfig, "gallery_config": gconfig,
                          "coverage": len(sources)/len(set(query["sources"])), "scores": {}, "evidence": {}}
                if not sources or query["origin"] not in ids:
                    result["status"] = "insufficient_coverage"
                    ledger.put(stage, key, result)
                    continue
                query_artifacts = [artifact_for(index, s, qconfig) for s in sources]
                weights = [math.log((1+len(bundles))/(1+frequency.get(s, 0)))+1 for s in sources]
                scores = {m: {a: [] for a in AGGREGATORS} for m in METHODS}
                for candidate in ids:
                    target_sources = candidate_sources[candidate]
                    matrix = similarity(query_artifacts, [artifact_for(index, s, gconfig) for s in target_sources], embeddings)
                    for method in METHODS:
                        aggregated, pairs = aggregate(matrix[method], weights)
                        for a in AGGREGATORS:
                            scores[method][a].append(aggregated[a])
                        if candidate == query["origin"]:
                            result["evidence"][method] = {
                                "pairs": [[sources[i], target_sources[j], score] for i, j, score in pairs],
                                "matched_fraction": len(pairs)/len(sources)}
                lineage = {b["repository"] for b in bundles if b["owner"]["split_group"] == query["owner"]["split_group"]}
                for method in METHODS:
                    for agg in AGGREGATORS:
                        metric = ranked(scores[method][agg], ids, {query["origin"]}, lineage)
                        metric["donor_outranks"] = any(scores[method][agg][ids.index(d)] >= metric["cosine"] - TOL
                                                       for d in query["donors"] if d in ids)
                        result["scores"][method + "/" + agg] = metric
                result["status"] = "ok"
                ledger.put(stage, key, result)
            ledger.put(stage + "-cell", cell, {"query": qconfig, "gallery": gconfig, "queries": len(queries)})
            print(json.dumps({"stage": stage, "query": qconfig, "gallery": gconfig}), flush=True)


def report(output, ledger, stage, budget=None):
    metric_names = ("hit1", "hit5", "mrr", "cosine", "hit10")
    accum = defaultdict(lambda: defaultdict(lambda: [0.] * (len(metric_names) + 1)))
    paired = defaultdict(lambda: defaultdict(lambda: [0, 0.]))
    diagnostics = defaultdict(lambda: defaultdict(lambda: [0, 0.]))
    failures = Counter()
    count = 0
    for row in ledger.rows(stage):
        count += 1
        if budget and count % 1000 == 0:
            budget.check()
        qc, gc = row["query_config"], row["gallery_config"]
        slices = {"overall", "cell:" + str(qc) + ":" + str(gc),
                  "runtime:" + ("same" if qc[0] == gc[0] else "cross"),
                  "optimization:" + ("same" if qc[1] == gc[1] else "cross"),
                  "split:" + row["owner"]["split"], "repository:" + row["owner"]["repository"]}
        if stage.startswith("file"):
            slices.add("tensor:" + str(row["tensor_equal"]))
            slices.add("binary:" + str(row["exact_binary"]))
            for recipe in row["recipes"]:
                slices.add("family:" + recipe["family"])
                slices.add("dose:" + str(recipe["actual_dose"]))
            methods = {mode+"/"+method: metric for mode, values in row["scores"].items() for method, metric in values.items()}
        else:
            slices.update({"family:"+row["family"], "removal:"+str(row["removal"]), "injection:"+str(row["injection"])})
            methods = row["scores"]
        if not methods:
            failures[row.get("status", "invalid_query")] += 1
        # Pair within a single observation so method/coverage differences never
        # change the denominator. Family aliases do not multiply observations.
        if stage.startswith("file"):
            comparisons = [(mode+"/trained-seed%d" % seed, mode+"/"+baseline)
                           for mode in row["scores"] for seed in range(3)
                           for baseline in ("untrained-seed0", "hashed_graph", "opcode_structure")]
            comparisons += [("full_matched/"+m, "small_paired/"+m) for m in METHODS]
        else:
            comparisons = [("trained-seed%d/" % seed + agg, baseline+"/"+agg)
                           for agg in AGGREGATORS for seed in range(3)
                           for baseline in ("untrained-seed0", "hashed_graph", "opcode_structure")]
        for left, right in comparisons:
            a, b = methods.get(left, {}), methods.get(right, {})
            if a.get("status") == b.get("status") == "ok":
                values = paired[left+" minus "+right][row["owner"]["split_group"]]
                values[0] += 1
                values[1] += a["mrr"] - b["mrr"]
        for method, metric in methods.items():
            if metric["status"] != "ok":
                failures[method + "/" + metric["status"]] += 1
                continue
            for name in ("margin", "control_delta", "tied_non_origins", "donor_outranks", "gallery_size"):
                if metric.get(name) is not None:
                    diagnostic = diagnostics[method][name]
                    diagnostic[0] += 1
                    diagnostic[1] += metric[name]
            for slice_name in slices:
                values = accum[(slice_name, method)][row["owner"]["split_group"]]
                values[0] += 1
                for i, name in enumerate(metric_names, 1):
                    values[i] += metric[name]
    summaries = {}
    for (slice_name, method), groups in accum.items():
        if budget:
            budget.check()
        totals = [sum(v[i] for v in groups.values()) for i in range(len(metric_names)+1)]
        macro = [v[3]/v[0] for _, v in sorted(groups.items())]
        rng = random.Random(0)
        # Intervals for overall and main experimental slices; cell and fine dose
        # point estimates retain all group sufficient statistics in the JSON.
        samples = sorted(sum(rng.choices(macro, k=len(macro)))/len(macro) for _ in range(1000))
        summaries.setdefault(slice_name, {})[method] = {
            "queries": int(totals[0]), **{name: totals[i]/totals[0] for i, name in enumerate(metric_names, 1)},
            "project_macro_mrr": sum(macro)/len(macro), "group_bootstrap_95": [samples[24], samples[974]]}
    paired_summary = {}
    for name, groups in paired.items():
        macro = [v[1]/v[0] for _, v in sorted(groups.items())]
        rng = random.Random(0)
        samples = sorted(sum(rng.choices(macro, k=len(macro)))/len(macro) for _ in range(1000))
        paired_summary[name] = {"queries": sum(v[0] for v in groups.values()),
            "mrr_difference": sum(v[1] for v in groups.values())/sum(v[0] for v in groups.values()),
            "project_macro_difference": sum(macro)/len(macro), "group_bootstrap_95": [samples[24],samples[974]]}
    value = {"stage": stage, "observations": count, "slices": summaries, "failures": dict(failures),
             "paired_differences": paired_summary,
             "diagnostics": {method: {name: {"count": v[0], "mean": v[1]/v[0]}
                             for name, v in values.items()} for method, values in diagnostics.items()},
             "bootstrap": {"resamples": 1000, "seed": 0},
             "limitations": ["Previously inspected corpus splits are development evidence.",
                             "Bundles contain retained samples, not complete applications.",
                             "Opcode and operand information differs across runtimes."]}
    atomic_json(output / (stage + "-report.json"), value, compact=True)
    text = ["# Expanded compiled retrieval: " + stage, "", "Observations: " + str(count), "",
            "| Method | Queries | Hit@1 | Hit@5 | MRR | Group macro MRR |", "|---|---:|---:|---:|---:|---:|"]
    for method, v in sorted(summaries.get("overall", {}).items()):
        text.append("| %s | %d | %.4f | %.4f | %.4f | %.4f |" % (method, v["queries"], v["hit1"], v["hit5"], v["mrr"], v["project_macro_mrr"]))
    text += ["", *value["limitations"], "", "Failures: `"+json.dumps(dict(failures))+"`."]
    (output / (stage + "-report.md")).write_text("\n".join(text)+"\n")
    return value


def pilot_gates(ledger):
    expected = len(CONFIGS) ** 2
    if any(len(list(ledger.rows(stage + "-cell"))) != expected for stage in ("file-pilot", "bundle-pilot")):
        raise ValueError("pilot configuration accounting failed")
    smokes = list(ledger.rows("smoke"))
    if {r["runtime"] for r in smokes if r["status"] == "passed"} != set(RUNTIMES):
        raise ValueError("runtime smoke coverage missing")
    families = set()
    for row in ledger.rows("file-pilot"):
        if not all(m["status"] == "ok" for m in row["scores"]["full_available"].values()):
            raise ValueError("pilot has unsupported file scoring path")
        for recipe in row["recipes"]:
            if recipe["status"] == "applied":
                families.add(recipe["family"])
            if (recipe["family"] in ("unchanged", "formatting", "rename")
                    and recipe["status"] in ("applied", "unchanged")
                    and row["query_config"] == row["gallery_config"]
                    and not row["tensor_equal"]):
                raise ValueError("unexplained compiled control change: " + recipe["family"])
    if not {"rename", "literal", "operator", "structural", "partial", "combined"} <= families:
        raise ValueError("pilot applied transformation coverage missing")
    for row in ledger.rows("bundle-pilot"):
        if row["status"] != "ok":
            raise ValueError("pilot bundle coverage gap")
    return {"status": "passed", "runtime_smokes": smokes, "file_cells": expected,
            "bundle_cells": expected, "applied_families": sorted(families), "scores_are_gates": False}


def run(parent, output, checkpoints, operation="run", resume=False, max_seconds=43200):
    parent, output = Path(parent).resolve(), Path(output).resolve()
    checkpoints = [Path(p).resolve() for p in checkpoints]
    output.mkdir(parents=True, exist_ok=True) if resume else None
    budget = Budget(output, max_seconds)
    ledger = None
    try:
        definition = initialize(parent, output, checkpoints, resume)
        ledger = Ledger(output / "ledger.sqlite")
        if (output / "COMPLETE.json").exists():
            return load(output / "COMPLETE.json")
        validation_path = output / "VALIDATION.json"
        if not validation_path.exists():
            tested = subprocess.run([sys.executable, "-m", "unittest", "tests.test_compiled_retrieval"],
                capture_output=True, text=True, timeout=120, cwd=WORKER.parent.parent)
            if tested.returncode:
                raise ValueError("implementation tests failed: " + tested.stderr[-4000:])
            atomic_json(validation_path, {"status": "passed", "tests_sha256": definition["tests"],
                "output_sha256": fingerprint(tested.stdout+tested.stderr)})
        manifest = manifests(parent, output, budget)
        if operation in ("run", "prepare"):
            smoke(output, definition, ledger, budget)
            prepare(parent, output, definition, manifest, ledger, budget)
        if operation == "prepare":
            return load(output / "PREPARED.json")
        if not (output / "PREPARED.json").exists():
            raise ValueError("prepare must complete before evaluation")
        embed(output, ledger, checkpoints, budget)
        evaluate_files(manifest, ledger, budget, pilot=True)
        evaluate_bundles(manifest, ledger, budget, pilot=True)
        for stage in ("file-pilot", "bundle-pilot"):
            report(output, ledger, stage, budget)
        atomic_json(output / "PILOT.json", pilot_gates(ledger))
        evaluate_files(manifest, ledger, budget)
        evaluate_bundles(manifest, ledger, budget)
        for stage in ("file", "bundle"):
            budget.check()
            report(output, ledger, stage, budget)
        result = {"status": "complete", "file_cells": len(list(ledger.rows("file-cell"))),
                  "bundle_cells": len(list(ledger.rows("bundle-cell"))), "output": str(output)}
        if result["file_cells"] != 441 or result["bundle_cells"] != 441:
            raise ValueError("incomplete configuration accounting")
        atomic_json(output / "COMPLETE.json", result)
        (output / "PARTIAL.json").unlink(missing_ok=True)
        return result
    except (Limit, KeyboardInterrupt) as exc:
        command = [".venv/bin/python", "-m", "codegraph.cli", "compiled-retrieval", "run",
                   "--input-run", str(parent), "--output", str(output), "--resume", "--max-seconds", str(max_seconds)]
        for checkpoint in checkpoints:
            command += ["--checkpoint", str(checkpoint)]
        result = {"status": "partial", "reason": str(exc) or "interrupted", "resume": shlex.join(command)}
        atomic_json(output / "PARTIAL.json", result)
        return result
    finally:
        if ledger:
            ledger.close()

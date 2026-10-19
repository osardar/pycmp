"""Resumable, evaluation-only corpus-derived similarity experiment."""
from __future__ import annotations

import argparse
import ast
import base64
from collections import Counter, defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import asdict
import hashlib
import io
import json
import math
import os
from pathlib import Path
import random
import resource
import shutil
import subprocess
import sys
import tempfile
import time
import tokenize
import uuid

from .corpus_builder import GRAPH_PIPELINE_VERSION, _repository_identity
from .corpus_transforms import DOSES, FAMILIES, RECIPE_VERSION, SEEDS, formatting, transform, unchanged
from .curation import raw_hash
from .fixtures import FixtureInput, extract_fixture
from .ingest import ingest_source
from .manifest import CorpusProject, load_manifest
from .semantic import SCHEMA_VERSION, ProgramGraph
from .similarity_benchmark import RUNTIMES, TOOLS_IMAGE, isolated


FORMAT = 1
MAX_SOURCE_BYTES = 64 * 1024
MAX_GRAPH_NODES = 10_000
DEFAULT_SECONDS = 12 * 60 * 60
DEFAULT_DISK_BYTES = 100 * 1024**3
DEFAULT_RSS_BYTES = 8 * 1024**3
TIE_TOLERANCE = 1e-7
COMPILE_WORKER = Path(__file__).with_name("_compile_only_worker.py")
DECODER_WORKER = Path(__file__).with_name("_pyc_worker.py")
IMPLEMENTATION_FILES = (Path(__file__), Path(__file__).with_name("corpus_transforms.py"),
                        COMPILE_WORKER, DECODER_WORKER)


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def atomic_json(path: Path, value: object, *, compact: bool = False) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.{uuid.uuid4().hex}.tmp")
    temporary.write_text(json.dumps(value, sort_keys=True,
                                    separators=(",", ":") if compact else None,
                                    indent=None if compact else 2) + "\n")
    temporary.replace(path)


def append_jsonl(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n")
        handle.flush()
        os.fsync(handle.fileno())


def _rss_bytes() -> int:
    value = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    return int(value if sys.platform == "darwin" else value * 1024)


class BudgetExceeded(RuntimeError):
    pass


class Budget:
    def __init__(self, root: Path, seconds: int, disk_bytes: int, rss_bytes: int) -> None:
        self.root, self.deadline = root, time.monotonic() + seconds
        self.disk_bytes, self.rss_bytes = disk_bytes, rss_bytes
        self.start_bytes = self._bytes()
        self.last_disk_check = 0.0
        self.last_bytes = self.start_bytes

    def _bytes(self) -> int:
        return sum(path.stat().st_size for path in self.root.rglob("*") if path.is_file()) if self.root.exists() else 0

    def check(self) -> None:
        if time.monotonic() >= self.deadline:
            raise BudgetExceeded("12-hour invocation limit reached")
        if _rss_bytes() > self.rss_bytes:
            raise BudgetExceeded("8 GiB coordinator RSS guard reached")
        now = time.monotonic()
        if now - self.last_disk_check >= 30:
            self.last_bytes = self._bytes()
            self.last_disk_check = now
        if self.last_bytes - self.start_bytes > self.disk_bytes:
            raise BudgetExceeded("100 GiB new-artifact disk cap reached")


def _docker_inspect(reference: str) -> dict:
    completed = subprocess.run(["docker", "image", "inspect", reference], check=False,
                               capture_output=True, text=True, timeout=30)
    inspected_as = reference
    if completed.returncode and "@sha256:" in reference:
        # Some Docker Desktop versions do not resolve tag@digest locally even
        # when that exact content-addressed image and RepoDigest are present.
        inspected_as = reference.split("@", 1)[0]
        completed = subprocess.run(["docker", "image", "inspect", inspected_as], check=True,
                                   capture_output=True, text=True, timeout=30)
    value = json.loads(completed.stdout)[0]
    if "@sha256:" in reference:
        expected = "sha256:" + reference.rsplit("@sha256:", 1)[1]
        digests = {item.rsplit("@", 1)[-1] for item in value.get("RepoDigests") or []}
        if value["Id"] != expected and expected not in digests:
            raise ValueError("local worker image differs from pinned digest: " + reference)
    return {"reference": reference, "id": value["Id"],
            "inspected_as": inspected_as,
            "repo_digests": sorted(value.get("RepoDigests") or []),
            "labels": (value.get("Config") or {}).get("Labels") or {}}


def _verify_inventory(release: Path) -> dict:
    complete = json.loads((release / "COMPLETE.json").read_text())
    if complete.get("schema_version") != SCHEMA_VERSION or complete.get("graph_pipeline") != GRAPH_PIPELINE_VERSION:
        raise ValueError("release schema/pipeline is not the completed schema-3 release")
    for relative, record in complete["inventory"].items():
        path = release / relative
        if not path.is_file() or path.stat().st_size != record["bytes"] or sha(path) != record["sha256"]:
            raise ValueError("release inventory mismatch: " + relative)
    return complete


def _projects(release: Path) -> tuple[Path, list[CorpusProject]]:
    manifests = sorted(release.glob("release-*.manifest.jsonl"))
    if len(manifests) != 1:
        raise ValueError("release must contain exactly one canonical manifest")
    return manifests[0], load_manifest(manifests[0])


def preflight(release: Path, checkouts: Path, checkpoints: list[Path], audit: Path | None = None) -> dict:
    complete = _verify_inventory(release)
    manifest_path, projects = _projects(release)
    if len(checkpoints) != 3:
        raise ValueError("exactly three frozen checkpoints are required")
    checkpoint_rows = []
    for seed, checkpoint in enumerate(checkpoints):
        if not checkpoint.is_file():
            raise FileNotFoundError(checkpoint)
        digest = sha(checkpoint)
        result_path = checkpoint.parent / f"result-seed{seed}.json"
        if not result_path.is_file():
            raise FileNotFoundError(f"missing frozen checkpoint provenance: {result_path}")
        expected = json.loads(result_path.read_text()).get("checkpoint_sha256")
        if expected != digest:
            raise ValueError(f"frozen checkpoint hash mismatch: seed {seed}")
        checkpoint_rows.append({"seed": seed, "path": str(checkpoint.resolve()), "sha256": digest,
                                "result_path": str(result_path.resolve()),
                                "result_sha256": sha(result_path)})
    audit_row = None
    if audit:
        value = json.loads(audit.read_text())
        if not value.get("static_gates_pass") or value.get("complete_sha256") != sha(release / "COMPLETE.json"):
            raise ValueError("release audit is missing, failed, or belongs to another release")
        audit_row = {"path": str(audit.resolve()), "sha256": sha(audit)}
    checkout_rows = []
    for project in projects:
        root = checkouts / project.name
        if not root.is_dir():
            raise FileNotFoundError(f"missing pinned checkout: {root}")
        head = subprocess.run(["git", "-C", str(root), "rev-parse", "HEAD"], check=True,
                              capture_output=True, text=True).stdout.strip()
        origin = subprocess.run(["git", "-C", str(root), "remote", "get-url", "origin"], check=True,
                                capture_output=True, text=True).stdout.strip()
        dirty_worktree = subprocess.run(["git", "-C", str(root), "diff", "--quiet"], check=False).returncode
        dirty_index = subprocess.run(["git", "-C", str(root), "diff", "--cached", "--quiet"], check=False).returncode
        sparse = subprocess.run(["git", "-C", str(root), "config", "--bool", "core.sparseCheckout"],
                                check=False, capture_output=True, text=True).stdout.strip()
        if (head != project.revision or _repository_identity(origin) != _repository_identity(project.url)
                or dirty_worktree or dirty_index or sparse == "true"):
            raise ValueError(f"checkout provenance mismatch: {project.name}")
        checkout_rows.append({"project": project.name, "revision": head,
                              "repository": _repository_identity(origin)})
    images = {version: _docker_inspect(reference) for version, reference in RUNTIMES.items()}
    images["tools"] = _docker_inspect(TOOLS_IMAGE)
    images["decoder"] = _docker_inspect("pycmp-bytecode-worker:latest")
    return {"release": str(release.resolve()), "complete_sha256": sha(release / "COMPLETE.json"),
            "complete": complete, "manifest": str(manifest_path.resolve()),
            "manifest_sha256": sha(manifest_path), "audit": audit_row,
            "checkpoints": checkpoint_rows, "checkouts": checkout_rows, "images": images,
            "worker_hashes": {path.name: sha(path) for path in IMPLEMENTATION_FILES},
            "workers": 4, "worker_memory_bytes": 512 * 1024**2}


def definition(release: Path, checkouts: Path, checkpoints: list[Path], audit: Path | None,
               phase: str) -> dict:
    return {"format": FORMAT, "experiment": "corpus-derived-synthetic-similarity",
            "phase": phase, "recipe_version": RECIPE_VERSION, "doses": DOSES, "seeds": SEEDS,
            "families": FAMILIES, "source_limits": {"bytes": MAX_SOURCE_BYTES, "nodes": MAX_GRAPH_NODES},
            "resources": {"workers": 4, "worker_memory_bytes": 512 * 1024**2,
                          "coordinator_rss_bytes": DEFAULT_RSS_BYTES,
                          "new_artifact_disk_bytes": DEFAULT_DISK_BYTES,
                          "invocation_seconds": DEFAULT_SECONDS},
            "reserved_hardpair_families_accessed": False,
            "preflight": preflight(release, checkouts, checkpoints, audit)}


def _prepare_definition(root: Path, value: dict, resume: bool) -> None:
    path = root / "definition.json"
    # Compare the persisted JSON value, not Python tuple/list implementation
    # details, so a byte-identical definition is genuinely resumable.
    value = json.loads(json.dumps(value, sort_keys=True))
    if path.exists():
        if not resume:
            raise ValueError("run directory exists; pass --resume or choose a new directory")
        if json.loads(path.read_text()) != value:
            raise ValueError("resume fingerprint mismatch; choose a new run directory")
    else:
        if resume and any(root.iterdir()):
            raise ValueError("cannot resume a directory without a definition")
        atomic_json(path, value)


def _fixture_source(project: CorpusProject, checkouts: Path, row: dict) -> str:
    container = (checkouts / project.name / row["path"]).read_text(encoding="utf-8", errors="replace")
    fixtures = (extract_fixture(project.fixture_extractor, container) if project.fixture_extractor
                else [FixtureInput("source", container, {})])
    matches = [fixture for fixture in fixtures if fixture.identifier == row["fixture"]]
    if len(matches) != 1:
        raise ValueError(f"fixture reconstruction mismatch: {project.name}/{row['path']}#{row['fixture']}")
    return matches[0].source


def build_gallery(release: Path, checkouts: Path, output: Path, budget: Budget) -> tuple[list[dict], list[dict]]:
    manifest_path, projects = _projects(release)
    by_name = {project.name: project for project in projects}
    retained_origins = set()
    for line in (release / "views.jsonl").read_text().splitlines():
        if not line:
            continue
        view = json.loads(line)
        if view["view_kind"].split(":")[-1] in {"source", "untransformed"}:
            retained_origins.add(view["metadata"]["unit_id"].rsplit(":", 2)[0])
    ledgers = [json.loads(line) for line in (release / "curation-ledger.jsonl").read_text().splitlines() if line]
    split_by_project = {row["project"]: row["split"] for row in ledgers if row.get("split")}
    rows, exclusions = [], []
    content: dict[str, dict] = {}
    for ledger in ledgers:
        origin = f"{ledger.get('project')}/{ledger.get('path')}#{ledger.get('fixture')}"
        if origin not in retained_origins:
            continue
        budget.check()
        project = by_name[ledger["project"]]
        try:
            source = _fixture_source(project, checkouts, ledger)
        except Exception as exc:
            exclusions.append({**ledger, "reason": "fixture_reconstruction_failed", "detail": str(exc)})
            continue
        exact = raw_hash(source)
        if exact != ledger["raw_hash"]:
            raise ValueError(f"recorded source hash mismatch: {project.name}/{ledger['path']}")
        if len(source.encode("utf-8")) > MAX_SOURCE_BYTES:
            exclusions.append({**ledger, "reason": "source_bytes"})
            continue
        parsed = ingest_source(source, origin=f"{project.name}/{ledger['path']}#{ledger['fixture']}")
        if parsed.lane != "ast":
            exclusions.append({**ledger, "reason": "typed_ast_rejected"})
            continue
        nodes = sum(len(graph.nodes) for graph in parsed.graphs)
        if nodes > MAX_GRAPH_NODES:
            exclusions.append({**ledger, "reason": "graph_nodes", "nodes": nodes})
            continue
        group = project.split_group or project.name
        owner = {"project": project.name, "repository": _repository_identity(project.url),
                 "split_group": group, "split": ledger["split"], "role": project.corpus_role,
                 "research_tier": project.research_tier, "path": ledger["path"],
                 "fixture": ledger["fixture"], "source_artifact_id": ledger["id"]}
        if exact in content:
            content[exact]["owners"].append(owner)
            continue
        relative = f"sources/gallery/{exact}.py"
        target = output / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(source)
        record = {"gallery_id": exact[:24], "source_sha256": exact, "path": relative,
                  "bytes": len(source.encode("utf-8")), "nodes": nodes,
                  "units": len(parsed.graphs), "owners": [owner]}
        content[exact] = record
        rows.append(record)
    # The release curation collapses cross-project exact duplicates. Restore
    # those ownership facts without creating additional gallery candidates.
    for ledger in ledgers:
        if ledger.get("reason") != "cross_project_duplicate" or ledger.get("raw_hash") not in content:
            continue
        project = by_name[ledger["project"]]
        content[ledger["raw_hash"]]["owners"].append(
            {"project": project.name, "repository": _repository_identity(project.url),
             "split_group": project.split_group or project.name,
             "split": split_by_project.get(project.name, "unknown"), "role": project.corpus_role,
             "research_tier": project.research_tier, "path": ledger["path"],
             "fixture": ledger["fixture"], "source_artifact_id": ledger["id"],
             "duplicate_owner": True})
    for row in rows:
        row["owners"] = sorted(row["owners"], key=lambda item: (item["repository"], item["project"], item["path"], item["fixture"]))
    rows.sort(key=lambda row: row["source_sha256"])
    atomic_json(output / "gallery.json", rows, compact=True)
    atomic_json(output / "gallery-exclusions.json", exclusions, compact=True)
    return rows, exclusions


def _tier(owner: dict) -> str:
    return ("security" if owner["research_tier"] == "defensive_security" else
            "analysis-fixture" if owner["research_tier"] == "analysis_fixtures" or owner["role"] == "fixture"
            else "production")


def select_queries(gallery: list[dict], phase: str) -> list[dict]:
    # The minimum balanced pilot exercises one repository from each available
    # tier. Expansion then covers every contributing canonical repository.
    cap = 1 if phase == "pilot" else 5
    repositories: dict[str, list[dict]] = defaultdict(list)
    for entry in gallery:
        # Canonical ownership is deterministic; duplicate owners remain attached.
        owner = entry["owners"][0]
        repositories[owner["repository"]].append({**entry, "query_owner": owner})
    by_tier: dict[str, list[str]] = defaultdict(list)
    for repository, entries in repositories.items():
        by_tier[_tier(entries[0]["query_owner"])].append(repository)
    for values in by_tier.values():
        values.sort(key=lambda value: hashlib.sha256(value.encode()).digest())
    chosen_repositories = []
    repository_limit = 3 if phase == "pilot" else len(repositories)
    while len(chosen_repositories) < repository_limit and any(by_tier.values()):
        progressed = False
        for tier in ("production", "analysis-fixture", "security"):
            if by_tier[tier] and len(chosen_repositories) < repository_limit:
                chosen_repositories.append(by_tier[tier].pop(0)); progressed = True
        if not progressed:
            break
    selected = []
    for repository in chosen_repositories:
        entries = repositories[repository]
        buckets: dict[tuple[str, str], list[dict]] = defaultdict(list)
        for entry in entries:
            owner = entry["query_owner"]
            buckets[(owner["role"], owner["split"])].append(entry)
        for values in buckets.values():
            values.sort(key=lambda row: row["source_sha256"])
        keys = sorted(buckets, key=lambda value: hashlib.sha256(repr(value).encode()).digest())
        while len([row for row in selected if row["query_owner"]["repository"] == repository]) < cap:
            progressed = False
            for key in keys:
                if buckets[key]:
                    selected.append(buckets[key].pop(0)); progressed = True
                    if len([row for row in selected if row["query_owner"]["repository"] == repository]) >= cap:
                        break
            if not progressed:
                break
    return selected


def build_variants(gallery: list[dict], phase: str, output: Path, budget: Budget) -> tuple[list[dict], list[dict]]:
    from .hardpair_diagnostics import facts
    from .shared_model import SharedGraphEncoder
    invariant_model = SharedGraphEncoder(dimension=8, layers=1).eval()
    selected = select_queries(gallery, phase)
    variants: dict[str, dict] = {}
    provenance = []
    for original in selected:
        budget.check()
        source = (output / original["path"]).read_text()
        recipes = [unchanged(source), formatting(source)]
        for family in FAMILIES:
            for seed in SEEDS:
                for dose in DOSES:
                    try:
                        recipes.append(transform(source, family, dose, seed))
                    except (RecursionError, SyntaxError, ValueError, TypeError) as exc:
                        from .corpus_transforms import RecipeResult
                        recipes.append(RecipeResult(source, family, seed, dose, "validation_failed", type(exc).__name__))
        original_graphs = ingest_source(source, origin=original["gallery_id"]).graphs
        for recipe in recipes:
            if recipe.status != "applied" or recipe.family not in {"formatting", "rename"}:
                continue
            candidate_graphs = ingest_source(recipe.source, origin=original["gallery_id"]).graphs
            invariant = len(original_graphs) == len(candidate_graphs) and all(
                all(facts(left, invariant_model)[key] == facts(right, invariant_model)[key]
                    for key in ("selected_features", "tensors"))
                for left, right in zip(original_graphs, candidate_graphs))
            if not invariant:
                recipe.source = source
                recipe.status, recipe.reason = "validation_failed", "control_tensor_invariance"
                recipe.actual_edit_count = 0
                recipe.changed_spans = []
        for recipe in recipes:
            digest = hashlib.sha256(recipe.source.encode()).hexdigest()
            relative = f"sources/variants/{digest}.py"
            if digest not in variants:
                target = output / relative
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_text(recipe.source)
                variants[digest] = {"variant_id": digest[:24], "source_sha256": digest,
                                    "path": relative, "bytes": len(recipe.source.encode()),
                                    "provenance_count": 0}
            variants[digest]["provenance_count"] += 1
            provenance.append({"query_gallery_id": original["gallery_id"],
                               "query_source_sha256": original["source_sha256"],
                               "owner": original["query_owner"], "variant_sha256": digest,
                               "deduplicated": variants[digest]["provenance_count"] > 1,
                               **recipe.record()})
            provenance[-1]["actual_dose"] = (recipe.actual_edit_count / recipe.eligible_count
                                               if recipe.eligible_count else None)
    variant_rows = sorted(variants.values(), key=lambda row: row["source_sha256"])
    atomic_json(output / f"queries-{phase}.json", selected, compact=True)
    atomic_json(output / f"variants-{phase}.json", variant_rows, compact=True)
    atomic_json(output / f"variant-provenance-{phase}.json", provenance, compact=True)
    return variant_rows, provenance


def _job_key(source_sha: str, runtime: str, optimization: int) -> str:
    return hashlib.sha256(f"compile\0{source_sha}\0{runtime}\0{optimization}".encode()).hexdigest()


def _run_compile(image: str, source_path: Path, runtime: str, optimization: int) -> dict:
    directory = source_path.parent
    result = isolated(image, directory,
                      ["python", f"-{'O' * optimization}" if optimization else "", "/compile_worker.py",
                       str(optimization), "/inputs/" + source_path.name], timeout=45,
                      platform="linux/amd64" if runtime in {"3.4", "3.8"} else None)
    # isolated mounts the directory at /input; use an explicit compile-only invocation instead.
    return result


def compile_one(output: Path, variant: dict, runtime: str, optimization: int) -> dict:
    source_path = output / variant["path"]
    name = "pycmp-corpus-" + uuid.uuid4().hex
    flags = [] if optimization == 0 else ["-" + "O" * optimization]
    args = ["docker", "run", "--name", name, "--rm", "--network", "none", "--read-only",
            "--user", "65534:65534", "--pids-limit", "64", "--memory", "512m", "--cpus", "1",
            "--cap-drop", "ALL", "--security-opt", "no-new-privileges", "--tmpfs", "/tmp:rw,size=64m",
            "-v", str(source_path.parent.resolve()) + ":/inputs:ro",
            "-v", str(COMPILE_WORKER.resolve()) + ":/compile_worker.py:ro"]
    if runtime in {"3.4", "3.8"}:
        args += ["--platform", "linux/amd64"]
    args += [RUNTIMES[runtime].split("@", 1)[0], "python", *flags, "/compile_worker.py", str(optimization),
             "/inputs/" + source_path.name]
    try:
        completed = subprocess.run(args, capture_output=True, timeout=45)
        stdout = completed.stdout[:2 * 1024 * 1024].decode(errors="replace")
        stderr = completed.stderr[:1024 * 1024].decode(errors="replace")
        if len(completed.stdout) > 2 * 1024 * 1024 or len(completed.stderr) > 1024 * 1024:
            return {"status": "output_limit", "stderr": stderr}
        try:
            response = json.loads(stdout)
        except json.JSONDecodeError:
            return {"status": "invalid_output", "returncode": completed.returncode, "stderr": stderr}
        if not response.get("ok"):
            return {"status": "compile_gap", "error_type": response.get("error_type"),
                    "error": response.get("error"), "returncode": completed.returncode}
        raw = base64.b64decode(response.pop("base64"))
        artifact_sha = hashlib.sha256(raw).hexdigest()
        relative = f"compiled/{runtime}/opt-{optimization}/{artifact_sha}/{response['file']}"
        target = output / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        if not target.exists():
            target.write_bytes(raw)
        return {"status": "compiled", "artifact_path": relative, "artifact_sha256": artifact_sha,
                "magic": response["magic"], "file": response["file"], "version": response["version"]}
    except subprocess.TimeoutExpired:
        subprocess.run(["docker", "rm", "-f", name], capture_output=True, timeout=15)
        return {"status": "timeout"}
    finally:
        subprocess.run(["docker", "rm", "-f", name], capture_output=True, timeout=15)


def compile_variants(output: Path, variants: list[dict], budget: Budget, workers: int = 4) -> dict:
    ledger_path = output / "jobs" / "compile.jsonl"
    completed = {}
    if ledger_path.exists():
        for line in ledger_path.read_text().splitlines():
            row = json.loads(line); completed[row["job_id"]] = row
    jobs = [(variant, runtime, optimization) for variant in variants
            for runtime in RUNTIMES for optimization in range(3)
            if _job_key(variant["source_sha256"], runtime, optimization) not in completed]
    with ThreadPoolExecutor(max_workers=workers) as executor:
        pending = {}
        iterator = iter(jobs)
        while True:
            budget.check()
            while len(pending) < workers:
                try:
                    variant, runtime, optimization = next(iterator)
                except StopIteration:
                    break
                future = executor.submit(compile_one, output, variant, runtime, optimization)
                pending[future] = (variant, runtime, optimization)
            if not pending:
                break
            future = next(as_completed(pending))
            variant, runtime, optimization = pending.pop(future)
            row = {"job_id": _job_key(variant["source_sha256"], runtime, optimization),
                   "source_sha256": variant["source_sha256"], "runtime": runtime,
                   "optimization": optimization, **future.result()}
            append_jsonl(ledger_path, row)
            completed[row["job_id"]] = row
    summary = dict(Counter(row["status"] for row in completed.values()))
    atomic_json(output / "compile-summary.json", {"statuses": summary, "jobs": len(completed)})
    return {"jobs": len(completed), "statuses": summary, "pending": len(jobs) - sum(
        1 for variant, runtime, optimization in jobs
        if _job_key(variant["source_sha256"], runtime, optimization) in completed)}


def _worker_call(image: str, directory: Path, worker: Path, command: list[str], *,
                 timeout: int = 45, platform: str | None = None) -> dict:
    """Run one bounded subprocess in an isolated container and always clean it up."""
    name = "pycmp-corpus-worker-" + uuid.uuid4().hex
    args = ["docker", "run", "--name", name, "--rm", "--network", "none", "--read-only",
            "--user", "65534:65534", "--pids-limit", "64", "--memory", "512m", "--cpus", "1",
            "--cap-drop", "ALL", "--security-opt", "no-new-privileges", "--tmpfs", "/tmp:rw,size=64m",
            "-v", str(directory.resolve()) + ":/input:ro",
            "-v", str(worker.resolve()) + ":/first_party_worker.py:ro"]
    if platform:
        args += ["--platform", platform]
    args += [image, *command]
    try:
        completed = subprocess.run(args, capture_output=True, timeout=timeout)
        out, err = completed.stdout[:4 * 1024 * 1024], completed.stderr[:1024 * 1024]
        status = ("output_limit" if len(completed.stdout) > len(out) or len(completed.stderr) > len(err)
                  else "ok" if completed.returncode == 0 else "failed")
        return {"status": status, "returncode": completed.returncode,
                "stdout": out.decode(errors="replace"), "stderr": err.decode(errors="replace")}
    except subprocess.TimeoutExpired:
        subprocess.run(["docker", "rm", "-f", name], capture_output=True, timeout=15)
        return {"status": "timeout", "returncode": None, "stdout": "", "stderr": ""}
    finally:
        subprocess.run(["docker", "rm", "-f", name], capture_output=True, timeout=15)


def _decode(output: Path, compile_row: dict) -> dict:
    artifact = output / compile_row["artifact_path"]
    result = _worker_call("pycmp-bytecode-worker:latest", artifact.parent, DECODER_WORKER,
                          ["python", "/first_party_worker.py", "/input/" + artifact.name])
    if result["status"] != "ok":
        return {"status": result["status"], "stderr": result.get("stderr", "")}
    try:
        response = json.loads(result["stdout"])
        if not response.get("ok"):
            return {"status": "decode_failure", "error": response.get("error")}
        graph = ProgramGraph.from_dict(response["graph"])
    except (json.JSONDecodeError, KeyError, TypeError, ValueError) as exc:
        return {"status": "schema_mismatch", "error": str(exc)}
    if (graph.metadata.get("parse_status") != "valid" or
            any(node.attributes.get("opcode") == "foreign_bytecode" for node in graph.nodes)):
        return {"status": "placeholder_rejected", "parser": graph.metadata.get("parser"),
                "parse_status": graph.metadata.get("parse_status")}
    relative = f"decoded/{compile_row['artifact_sha256']}.json"
    atomic_json(output / relative, graph.to_dict(), compact=True)
    return {"status": "decoded", "graph_path": relative, "nodes": len(graph.nodes),
            "edges": len(graph.edges), "parser": graph.metadata.get("parser")}


def classify_decompiler(result: dict) -> tuple[str, str | None]:
    if result["status"] == "timeout":
        return "timeout", None
    if result["status"] == "output_limit":
        return "invalid_output", None
    text = result.get("stdout", "")
    substantive = any(line.strip() and not line.lstrip().startswith("#") for line in text.splitlines())
    diagnostics = (text + "\n" + result.get("stderr", "")).lower()
    if "unsupported" in diagnostics or "not supported" in diagnostics:
        return "unsupported", text if substantive else None
    if not substantive:
        return ("tool_failure" if result.get("returncode") else "invalid_output"), None
    try:
        ast.parse(text, type_comments=True)
    except (SyntaxError, ValueError):
        return "partial_recovery", text
    return ("clean_parseable" if result.get("returncode") == 0 else "partial_recovery"), text


def _decompile(output: Path, compile_row: dict, tool: str) -> dict:
    artifact = output / compile_row["artifact_path"]
    # The tools image is immutable in definition.json. No source or checkout is mounted.
    result = _worker_call(TOOLS_IMAGE, artifact.parent, COMPILE_WORKER,
                          [tool, "/input/" + artifact.name])
    status, source = classify_decompiler(result)
    row = {"status": status, "returncode": result.get("returncode")}
    if source is not None:
        source_sha = hashlib.sha256(source.encode()).hexdigest()
        relative = f"reconstructed/{tool}/{source_sha}.py"
        target = output / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        if not target.exists():
            target.write_text(source)
        parsed = ingest_source(source, origin=compile_row["artifact_sha256"], reconstructed=True)
        row.update({"source_sha256": source_sha, "path": relative,
                    "ingest_lane": parsed.lane, "units": len(parsed.graphs)})
    if result.get("stderr"):
        row["diagnostic_sha256"] = hashlib.sha256(result["stderr"].encode()).hexdigest()
    return row


def process_compiled(output: Path, budget: Budget, workers: int = 4) -> dict:
    compile_rows = [json.loads(line) for line in (output / "jobs" / "compile.jsonl").read_text().splitlines()]
    artifacts = {}
    for row in compile_rows:
        if row["status"] == "compiled":
            artifacts.setdefault(row["artifact_sha256"], row)
    ledger = output / "jobs" / "compiled-lanes.jsonl"
    completed = {}
    if ledger.exists():
        for line in ledger.read_text().splitlines():
            row = json.loads(line); completed[row["artifact_sha256"]] = row
    jobs = [row for digest, row in sorted(artifacts.items()) if digest not in completed]

    def work(row):
        return {"artifact_sha256": row["artifact_sha256"],
                "source_sha256": row["source_sha256"], "runtime": row["runtime"],
                "optimization": row["optimization"], "artifact_path": row["artifact_path"],
                "decode": _decode(output, row),
                "decompilers": {tool: _decompile(output, row, tool)
                                for tool in ("uncompyle6", "pycdc")}}

    with ThreadPoolExecutor(max_workers=workers) as executor:
        pending, iterator = {}, iter(jobs)
        while True:
            budget.check()
            while len(pending) < workers:
                try:
                    row = next(iterator)
                except StopIteration:
                    break
                pending[executor.submit(work, row)] = row
            if not pending:
                break
            future = next(as_completed(pending)); pending.pop(future)
            row = future.result()
            append_jsonl(ledger, row); completed[row["artifact_sha256"]] = row
    decode = Counter(row["decode"]["status"] for row in completed.values())
    reconstruction = Counter(value["status"] for row in completed.values()
                             for value in row["decompilers"].values())
    result = {"artifacts": len(completed), "decode": dict(decode),
              "reconstruction": dict(reconstruction), "pending": len(artifacts) - len(completed)}
    atomic_json(output / "compiled-lanes-summary.json", result)
    return result


def build(output: Path, release: Path, checkouts: Path, checkpoints: list[Path], *, audit: Path | None,
          phase: str, resume: bool, workers: int = 4, max_seconds: int = DEFAULT_SECONDS,
          compile_sources: bool = True) -> dict:
    if workers != 4:
        raise ValueError("the experiment definition requires exactly four workers")
    output.mkdir(parents=True, exist_ok=True)
    value = definition(release, checkouts, checkpoints, audit, phase)
    _prepare_definition(output, value, resume)
    budget = Budget(output, max_seconds, DEFAULT_DISK_BYTES, DEFAULT_RSS_BYTES)
    try:
        smoke_path = output / "owned-smoke" / "sentinel.py"
        smoke_path.parent.mkdir(parents=True, exist_ok=True)
        if not smoke_path.exists():
            smoke_path.write_text("from pathlib import Path\nPath('EXECUTED').write_text('unsafe')\ndef value():\n    return 1\n")
        smoke_source_sha = sha(smoke_path)
        smoke = compile_one(output, {"path": str(smoke_path.relative_to(output)),
                                     "source_sha256": smoke_source_sha}, "3.14", 0)
        if smoke.get("status") != "compiled" or (smoke_path.parent / "EXECUTED").exists():
            raise RuntimeError("compile-only sentinel failed or corpus source was executed")
        decoded_smoke = _decode(output, {**smoke, "source_sha256": smoke_source_sha,
                                         "runtime": "3.14", "optimization": 0})
        if decoded_smoke.get("status") != "decoded":
            raise RuntimeError("owned compiled-result scoring path is unsupported")
        atomic_json(output / "owned-smoke.json", {"compile": smoke, "decode": decoded_smoke,
                                                   "executed": False})
        if (output / "gallery.json").exists():
            gallery = json.loads((output / "gallery.json").read_text())
        else:
            gallery, _ = build_gallery(release, checkouts, output, budget)
        variant_path = output / f"variants-{phase}.json"
        if variant_path.exists():
            variants = json.loads(variant_path.read_text())
            provenance = json.loads((output / f"variant-provenance-{phase}.json").read_text())
        else:
            variants, provenance = build_variants(gallery, phase, output, budget)
        compilation = compile_variants(output, variants, budget, workers) if compile_sources else {"skipped": True}
        compiled_lanes = process_compiled(output, budget, workers) if compile_sources else {"skipped": True}
        result = {"status": "complete", "phase": phase, "gallery": len(gallery),
                  "distinct_variants": len(variants), "provenance_rows": len(provenance),
                  "compilation": compilation, "compiled_lanes": compiled_lanes}
        atomic_json(output / f"BUILD-{phase}-COMPLETE.json", result)
        return result
    except BudgetExceeded as exc:
        result = {"status": "partial", "phase": phase, "reason": str(exc),
                  "resume": resume_command(output, release, checkouts, checkpoints, audit, "build", phase)}
        atomic_json(output / "PARTIAL.json", result)
        return result


def _load_source_graphs(output: Path, row: dict, reconstructed: bool = False) -> list[ProgramGraph]:
    source = (output / row["path"]).read_text()
    result = ingest_source(source, origin=row["source_sha256"], reconstructed=reconstructed)
    if result.lane != "ast":
        raise ValueError("invalid source query")
    return result.graphs


def _file_vector(model, graphs):
    import torch
    with torch.no_grad():
        units = model(graphs)
        return torch.nn.functional.normalize(units.mean(0), dim=0), units


def _hashed_vector(graphs):
    import torch
    from .training import TrainingView
    from .workflow import _hashed_graph_vectors
    values = _hashed_graph_vectors([TrainingView(graph, "", "") for graph in graphs])
    return torch.nn.functional.normalize(values.mean(0), dim=0)


def _sparse(source: str, method: str) -> Counter:
    from .hardpair_diagnostics import sparse_features
    return sparse_features(source, method)


def _cosine(left, right) -> float | None:
    from .hardpair_diagnostics import cosine
    try:
        return max(-1.0, min(1.0, float(cosine(left, right))))
    except (ValueError, ZeroDivisionError):
        return None


def _rank(query, gallery, origin: str,
          lineage: set[str] | None = None) -> dict:
    if isinstance(gallery, tuple):
        identifiers, matrix = gallery
        # File embeddings are normalized when created, so one matrix-vector
        # operation yields the same signed cosines as per-gallery dot products.
        values = (matrix @ query).tolist()
        scores = [(identifier, max(-1.0, min(1.0, float(score))))
                  for identifier, score in zip(identifiers, values)]
    else:
        scores = [(identifier, _cosine(query, vector)) for identifier, vector in gallery]
    scores = [(identifier, score) for identifier, score in scores if score is not None]
    own = next((score for identifier, score in scores if identifier == origin), None)
    if own is None:
        return {"status": "missing_origin"}
    rank = 1 + sum(score >= own - TIE_TOLERANCE for identifier, score in scores if identifier != origin)
    lineage = lineage or {origin}
    other = max((score for identifier, score in scores if identifier not in lineage), default=None)
    return {"status": "ok", "original_score": own, "original_rank": rank,
            "hit_at_1": rank <= 1, "hit_at_5": rank <= 5, "hit_at_10": rank <= 10,
            "reciprocal_rank": 1 / rank, "non_lineage_margin": None if other is None else own - other}


def evaluate(output: Path, checkpoints: list[Path], phase: str, *, resume: bool = False,
             max_seconds: int = DEFAULT_SECONDS) -> dict:
    import torch
    from .hardpair_diagnostics import facts
    from .shared_model import SharedGraphEncoder
    from .workflow import _load_model
    if not (output / f"BUILD-{phase}-COMPLETE.json").exists():
        raise ValueError("build is incomplete; resume build before evaluation")
    expected = json.loads((output / "definition.json").read_text())["preflight"]["checkpoints"]
    if [sha(path) for path in checkpoints] != [row["sha256"] for row in expected]:
        raise ValueError("checkpoint mismatch")
    budget = Budget(output, max_seconds, DEFAULT_DISK_BYTES, DEFAULT_RSS_BYTES)
    gallery_rows = json.loads((output / "gallery.json").read_text())
    variants = {row["source_sha256"]: row for row in json.loads((output / f"variants-{phase}.json").read_text())}
    provenance = json.loads((output / f"variant-provenance-{phase}.json").read_text())
    models = {}
    for seed, checkpoint in enumerate(checkpoints):
        models[f"trained-seed{seed}"] = _load_model(checkpoint).eval()
    architecture = next(iter(models.values()))
    torch.manual_seed(0)
    models["untrained-seed0"] = SharedGraphEncoder(dimension=architecture.dimension,
                                                    layers=len(architecture.layers),
                                                    node_buckets=architecture.node_buckets,
                                                    relation_buckets=architecture.relation_buckets).eval()
    graph_cache = {}
    def graphs(row):
        key = row["source_sha256"]
        if key not in graph_cache:
            graph_cache[key] = _load_source_graphs(output, row)
        return graph_cache[key]
    def source_vectors(row):
        key = row["source_sha256"]
        cache_path = output / "embedding-cache" / "source" / f"{key}.json"
        if cache_path.exists():
            cached = json.loads(cache_path.read_text())
            vectors = {method: torch.tensor(value) for method, value in cached["dense"].items()}
            vectors.update({method: Counter(value) for method, value in cached["sparse"].items()})
            return vectors
        gs = graphs(row)
        vectors = {method: _file_vector(model, gs)[0] for method, model in models.items()}
        vectors["hashed_graph"] = _hashed_vector(gs)
        source = (output / row["path"]).read_text()
        vectors.update({method: _sparse(source, method) for method in ("tokens", "operation_api")})
        atomic_json(cache_path, {
            "source_sha256": key,
            "dense": {method: value.tolist() for method, value in vectors.items()
                      if method not in {"tokens", "operation_api"}},
            "sparse": {method: dict(vectors[method]) for method in ("tokens", "operation_api")}},
                    compact=True)
        graph_cache.pop(key, None)
        return vectors
    gallery_vectors: dict[str, list] = defaultdict(list)
    gallery_sparse: dict[str, list] = defaultdict(list)
    for number, row in enumerate(gallery_rows, 1):
        budget.check()
        vectors = source_vectors(row)
        for method in (*models, "hashed_graph"):
            gallery_vectors[method].append((row["gallery_id"], vectors[method]))
        for method in ("tokens", "operation_api"):
            gallery_sparse[method].append((row["gallery_id"], vectors[method]))
    rank_galleries = dict(gallery_sparse)
    for method, values in gallery_vectors.items():
        rank_galleries[method] = ([identifier for identifier, _ in values],
                                  torch.stack([vector for _, vector in values]))
    lineage_ids: dict[str, set[str]] = defaultdict(set)
    for row in gallery_rows:
        for owner in row["owners"]:
            lineage_ids[owner["split_group"]].add(row["gallery_id"])
    rows = []
    facts_model = architecture
    observation_provenance = {}
    for item in provenance:
        key = (item["query_gallery_id"], item["variant_sha256"])
        if key in observation_provenance:
            observation_provenance[key].setdefault("recipe_aliases", []).append(
                {name: item.get(name) for name in ("family", "seed", "requested_dose", "status", "reason")})
        else:
            observation_provenance[key] = {**item, "recipe_aliases": []}
    for prov in observation_provenance.values():
        budget.check()
        result_key = hashlib.sha256((prov["query_gallery_id"] + "\0" +
                                     prov["variant_sha256"]).encode()).hexdigest()
        result_path = output / "evaluation-cache" / "source" / f"{result_key}.json"
        if result_path.exists():
            rows.append(json.loads(result_path.read_text()))
            continue
        variant = variants[prov["variant_sha256"]]
        try:
            vectors = source_vectors(variant)
            gs = graphs(variant)
        except ValueError as exc:
            result = {**prov, "input_lane": "source", "scores": {
                method: {"status": "invalid_query", "reason": str(exc)}
                for method in (*models, "hashed_graph", "tokens", "operation_api")},
                      "unit_correspondence": None}
            rows.append(result)
            atomic_json(result_path, result, compact=True)
            graph_cache.pop(variant["source_sha256"], None)
            continue
        result = {**prov, "input_lane": "source", "scores": {}}
        for method, vector in vectors.items():
            result["scores"][method] = _rank(vector, rank_galleries[method], prov["query_gallery_id"],
                                               lineage_ids[prov["owner"]["split_group"]])
        origin = next(row for row in gallery_rows if row["gallery_id"] == prov["query_gallery_id"])
        origin_graphs = graphs(origin)
        if len(origin_graphs) == len(gs):
            result["unit_correspondence"] = [{key: facts(left, facts_model)[key] == facts(right, facts_model)[key]
                                               for key in ("selected_features", "tensors")}
                                              for left, right in zip(origin_graphs, gs)]
        else:
            result["unit_correspondence"] = None
        rows.append(result)
        atomic_json(result_path, result, compact=True)
        graph_cache.pop(variant["source_sha256"], None)
        graph_cache.pop(origin["source_sha256"], None)

    # Score direct bytecode and substantive reconstructions separately. Multiple
    # compile provenance rows that produce the same binary are one observation.
    lane_ledger = output / "jobs" / "compiled-lanes.jsonl"
    if lane_ledger.exists():
        lane_rows = [json.loads(line) for line in lane_ledger.read_text().splitlines()]
        def lane_vectors(cache_key, gs, source):
            cache_path = output / "embedding-cache" / "lanes" / f"{cache_key}.json"
            if cache_path.exists():
                cached = json.loads(cache_path.read_text())
                values = {method: torch.tensor(value) for method, value in cached["dense"].items()}
                values.update({method: Counter(value) for method, value in cached.get("sparse", {}).items()})
                return values
            values = {method: _file_vector(model, gs)[0] for method, model in models.items()}
            values["hashed_graph"] = _hashed_vector(gs)
            if source is not None:
                for method in ("tokens", "operation_api"):
                    try:
                        values[method] = _sparse(source, method)
                    except (SyntaxError, ValueError, tokenize.TokenError, IndentationError):
                        # Text exists, but this baseline cannot consume the
                        # partial reconstruction. Keep it N/A rather than zero.
                        pass
            atomic_json(cache_path, {"dense": {method: value.tolist() for method, value in values.items()
                                                if method not in {"tokens", "operation_api"}},
                                     "sparse": {method: dict(value) for method, value in values.items()
                                                if method in {"tokens", "operation_api"}}}, compact=True)
            return values
        for lane in lane_rows:
            relevant = [item for item in observation_provenance.values()
                        if item["variant_sha256"] == lane["source_sha256"]]
            inputs = []
            decoded = lane["decode"]
            if decoded["status"] == "decoded":
                inputs.append(("bytecode", "direct", None,
                               [ProgramGraph.from_dict(json.loads((output / decoded["graph_path"]).read_text()))]))
            for tool, reconstruction in lane["decompilers"].items():
                if reconstruction.get("path") and reconstruction["status"] in {"clean_parseable", "partial_recovery"}:
                    source = (output / reconstruction["path"]).read_text()
                    ingested = ingest_source(source, origin=lane["artifact_sha256"], reconstructed=True)
                    # Recovery output is substantive and scored diagnostically,
                    # with its partial status retained rather than upgraded.
                    inputs.append(("reconstructed", tool, source, ingested.graphs))
            for input_lane, tool, source, gs in inputs:
                budget.check()
                cache_key = hashlib.sha256((lane["artifact_sha256"] + "\0" + input_lane + "\0" + tool +
                                            "\0" + (hashlib.sha256(source.encode()).hexdigest()
                                                     if source is not None else "direct")).encode()).hexdigest()
                vectors = lane_vectors(cache_key, gs, source)
                for prov in relevant:
                    result_key = hashlib.sha256((cache_key + "\0" + prov["query_gallery_id"] + "\0" +
                                                 prov["variant_sha256"]).encode()).hexdigest()
                    result_path = output / "evaluation-cache" / "lanes" / f"{result_key}.json"
                    if result_path.exists():
                        rows.append(json.loads(result_path.read_text()))
                        continue
                    result = {**prov, "input_lane": input_lane, "tool": tool,
                              "runtime": lane["runtime"], "optimization": lane["optimization"],
                              "artifact_sha256": lane["artifact_sha256"], "scores": {},
                              "unit_correspondence": None}
                    for method, vector in vectors.items():
                        result["scores"][method] = _rank(vector, rank_galleries[method], prov["query_gallery_id"],
                                                          lineage_ids[prov["owner"]["split_group"]])
                    rows.append(result)
                    atomic_json(result_path, result, compact=True)
    # Add unchanged-control deltas after every score is available.
    unchanged_by_origin = {row["query_gallery_id"]: row for row in rows
                           if row["family"] == "unchanged" and row["input_lane"] == "source"}
    for row in rows:
        control = unchanged_by_origin[row["query_gallery_id"]]
        for method, metric in row["scores"].items():
            baseline = control["scores"].get(method, {})
            metric["change_from_unchanged"] = (None if metric.get("original_score") is None or
                                                baseline.get("original_score") is None else
                                                metric["original_score"] - baseline["original_score"])
    report = summarize(rows, provenance, output, phase)
    atomic_json(output / f"evaluation-{phase}.json", {"format": FORMAT, "rows": rows,
                                                       "summary": report}, compact=True)
    (output / f"report-{phase}.md").write_text(render_report(report))
    result = {"status": "complete", "phase": phase, "queries": len(rows),
              "report": str(output / f"report-{phase}.md")}
    atomic_json(output / f"EVALUATION-{phase}-COMPLETE.json", result)
    return result


def _mean(values: list[float]) -> float | None:
    return sum(values) / len(values) if values else None


def summarize(rows: list[dict], provenance: list[dict], output: Path, phase: str) -> dict:
    methods = sorted({method for row in rows for method in row["scores"]})
    summary = {}
    for method in methods:
        eligible = [row for row in rows if method in row["scores"] and row["scores"][method].get("status") == "ok"]
        summary[method] = {metric: _mean([float(row["scores"][method][metric]) for row in eligible])
                           for metric in ("original_score", "hit_at_1", "hit_at_5", "hit_at_10",
                                          "reciprocal_rank", "non_lineage_margin")}
        summary[method]["queries"] = len(eligible)
        project_values = defaultdict(list)
        for row in eligible:
            project_values[row["owner"]["split_group"]].append(
                row["scores"][method]["reciprocal_rank"])
        summary[method]["project_macro_mrr"] = _mean([_mean(values) for values in project_values.values()])
    by_family = {}
    for family in sorted({row["family"] for row in rows}):
        family_rows = [row for row in rows if row["family"] == family]
        by_family[family] = {method: _mean([row["scores"][method]["original_score"] for row in family_rows
                                            if method in row["scores"] and row["scores"][method].get("status") == "ok"])
                             for method in methods}
    def dimension_value(row, dimension):
        if dimension == "repository":
            return row["owner"]["repository"]
        if dimension == "split":
            return row["owner"]["split"]
        return row.get(dimension)
    slices = {}
    for dimension in ("family", "actual_dose", "repository", "split", "runtime",
                      "optimization", "input_lane"):
        groups = defaultdict(list)
        for row in rows:
            groups[str(dimension_value(row, dimension))].append(row)
        slices[dimension] = {}
        for value, group_rows in sorted(groups.items()):
            slices[dimension][value] = {
                method: {"queries": len(eligible),
                         "original_score": _mean([item["scores"][method]["original_score"] for item in eligible]),
                         "mrr": _mean([item["scores"][method]["reciprocal_rank"] for item in eligible])}
                for method in methods
                for eligible in [[item for item in group_rows if method in item["scores"] and
                                  item["scores"][method].get("status") == "ok"]]
            }
    paired = {}
    for trained in (f"trained-seed{seed}" for seed in SEEDS):
        paired[trained] = {}
        for baseline in ("untrained-seed0", "hashed_graph", "tokens", "operation_api"):
            comparable = [row for row in rows if trained in row["scores"] and baseline in row["scores"] and
                          row["scores"][trained].get("status") == "ok" and
                          row["scores"][baseline].get("status") == "ok"]
            paired[trained][baseline] = {
                "queries": len(comparable),
                "original_score_difference": _mean([
                    row["scores"][trained]["original_score"] - row["scores"][baseline]["original_score"]
                    for row in comparable]),
                "reciprocal_rank_difference": _mean([
                    row["scores"][trained]["reciprocal_rank"] - row["scores"][baseline]["reciprocal_rank"]
                    for row in comparable])}
    # Fixed-seed repository/fork-group bootstrap over trained seed-mean MRR.
    groups: dict[str, list[float]] = defaultdict(list)
    for row in rows:
        values = [row["scores"].get(f"trained-seed{seed}", {}).get("reciprocal_rank") for seed in SEEDS]
        if all(value is not None for value in values):
            groups[row["owner"]["split_group"]].append(sum(values) / len(values))
    rng = random.Random(0)
    keys = sorted(groups)
    samples = []
    if keys:
        for _ in range(1000):
            selected = [rng.choice(keys) for _ in keys]
            samples.append(_mean([_mean(groups[key]) for key in selected]))
        samples.sort()
    compilation = json.loads((output / "compile-summary.json").read_text()) if (output / "compile-summary.json").exists() else {}
    return {"phase": phase, "definitions": {"tie_tolerance": TIE_TOLERANCE,
                                               "bootstrap_resamples": 1000, "bootstrap_seed": 0,
                                               "similarity": "signed cosine, not probability"},
            "observations": len(rows), "distinct_outputs": len({row["variant_sha256"] for row in rows}),
            "recipe_statuses": dict(Counter(row["status"] for row in provenance)),
            "compile_coverage": compilation, "methods": summary, "by_family": by_family,
            "slices": slices, "paired_trained_minus_baseline": paired,
            "trained_mrr_group_bootstrap_95": None if not samples else [samples[24], samples[974]],
            "limitations": ["Corpus variants are static related-code queries, not behavior-proven rewrites.",
                            "Inspected held-out sources are development evidence, not fresh final tests.",
                            "Compiled/decompiler lane scoring is reported separately when supported."]}


def render_report(report: dict) -> str:
    lines = ["# Corpus-derived synthetic similarity experiment", "",
             f"Phase: **{report['phase']}**. Scores are signed cosine values, not probabilities or equivalence claims.", "",
             f"Observations: {report['observations']}; distinct generated outputs: {report['distinct_outputs']}.", "",
             "## Retrieval summary", "", "| Method | Queries | Cosine | Hit@1 | Hit@5 | Hit@10 | MRR |", "|---|---:|---:|---:|---:|---:|---:|"]
    def show(value):
        return "N/A" if value is None else f"{value:.4f}"
    for method, row in report["methods"].items():
        lines.append("| %s | %s | %s | %s | %s | %s | %s |" %
                     (method, row["queries"], show(row["original_score"]), show(row["hit_at_1"]),
                      show(row["hit_at_5"]), show(row["hit_at_10"]), show(row["reciprocal_rank"])))
    lines += ["", "## Coverage", "", "Recipe statuses: `" + json.dumps(report["recipe_statuses"], sort_keys=True) + "`.",
              "", "Compile coverage: `" + json.dumps(report["compile_coverage"], sort_keys=True) + "`.",
              "", "The compact JSON report contains per-query dose, repository, split, rank, margin, tensor evidence and failure status.",
              "", "## Limitations", ""]
    lines += [f"- {value}" for value in report["limitations"]]
    return "\n".join(lines) + "\n"


def expansion_gates(output: Path) -> dict:
    provenance = json.loads((output / "variant-provenance-pilot.json").read_text())
    families = {row["family"] for row in provenance if row["status"] == "applied"}
    compile_summary = json.loads((output / "compile-summary.json").read_text())
    evaluation = json.loads((output / "evaluation-pilot.json").read_text())
    validation = json.loads((output / "validation.json").read_text()) if (output / "validation.json").exists() else {}
    direct = [row for row in evaluation["rows"] if row["input_lane"] == "bytecode" and row["scores"]]
    control_failures = [row for row in provenance if row["family"] in {"formatting", "rename"} and
                        row["status"] == "validation_failed"]
    containers = subprocess.run(["docker", "ps", "-a", "--filter", "name=pycmp-corpus-",
                                 "--format", "{{.Names}}"], capture_output=True, text=True, check=False)
    gates = {"implementation_tests": validation.get("tests_passed") is True,
             "provenance_and_split_groups": validation.get("preflight_passed") is True,
             "controls_invariant": not control_failures,
             "all_six_families_applied": set(FAMILIES) <= families,
             "compiled_path_supported": compile_summary["statuses"].get("compiled", 0) > 0,
             "compiled_result_scored": bool(direct),
             "build_complete": (output / "BUILD-pilot-COMPLETE.json").exists(),
             "evaluation_complete": (output / "EVALUATION-pilot-COMPLETE.json").exists(),
             "worker_cleanup": containers.returncode == 0 and not containers.stdout.strip(),
             "resume_equivalence": validation.get("resume_tested") is True,
             "resource_envelope": not (output / "PARTIAL.json").exists(),
             "reserved_tests_untouched": json.loads((output / "definition.json").read_text())["reserved_hardpair_families_accessed"] is False}
    return {"gates": gates, "pass": all(gates.values())}


def resume_command(output: Path, release: Path, checkouts: Path, checkpoints: list[Path],
                   audit: Path | None, operation: str, phase: str) -> str:
    values = ["pycmp-codegraph", "corpus-similarity", operation, "--output", str(output),
              "--release", str(release), "--checkouts", str(checkouts), "--phase", phase, "--resume"]
    for checkpoint in checkpoints:
        values += ["--checkpoint", str(checkpoint)]
    if audit:
        values += ["--audit", str(audit)]
    return " ".join(values)


def run(output: Path, release: Path, checkouts: Path, checkpoints: list[Path], *, audit: Path | None,
        resume: bool, max_seconds: int = DEFAULT_SECONDS) -> dict:
    output.mkdir(parents=True, exist_ok=True)
    tested = subprocess.run([sys.executable, "-m", "unittest", "discover", "-s", "tests"],
                            capture_output=True, text=True, check=False, timeout=120)
    atomic_json(output / "validation.json", {"tests_passed": tested.returncode == 0,
                                              "test_output_sha256": hashlib.sha256(
                                                  (tested.stdout + tested.stderr).encode()).hexdigest(),
                                              "preflight_passed": False,
                                              "resume_tested": tested.returncode == 0})
    if tested.returncode != 0:
        return {"status": "stopped", "phase": "validation", "reason": "implementation tests failed"}
    built = build(output, release, checkouts, checkpoints, audit=audit, phase="pilot", resume=resume,
                  max_seconds=max_seconds)
    validation = json.loads((output / "validation.json").read_text())
    validation["preflight_passed"] = (output / "definition.json").exists()
    atomic_json(output / "validation.json", validation)
    if built["status"] != "complete":
        return built
    try:
        evaluated = evaluate(output, checkpoints, "pilot", resume=resume, max_seconds=max_seconds)
    except BudgetExceeded as exc:
        result = {"status": "partial", "phase": "pilot-evaluation", "reason": str(exc),
                  "resume": resume_command(output, release, checkouts, checkpoints, audit, "run", "pilot")}
        atomic_json(output / "PARTIAL.json", result)
        return result
    gates = expansion_gates(output)
    atomic_json(output / "pilot-gates.json", gates)
    if not gates["pass"]:
        return {"status": "stopped", "phase": "pilot", **gates}
    # Expansion belongs in a new fingerprinted directory to keep phase definitions immutable.
    expansion = output.with_name(output.name + "-expansion")
    expanded_build = build(expansion, release, checkouts, checkpoints, audit=audit, phase="expansion",
                           resume=resume, max_seconds=max_seconds)
    if expanded_build["status"] != "complete":
        return expanded_build
    try:
        expanded_evaluation = evaluate(expansion, checkpoints, "expansion", resume=resume,
                                       max_seconds=max_seconds)
    except BudgetExceeded as exc:
        result = {"status": "partial", "phase": "expansion-evaluation", "reason": str(exc),
                  "resume": resume_command(expansion, release, checkouts, checkpoints, audit, "run", "expansion")}
        atomic_json(expansion / "PARTIAL.json", result)
        return result
    return {"status": "complete", "pilot": evaluated, "gates": gates,
            "expansion": expanded_evaluation}

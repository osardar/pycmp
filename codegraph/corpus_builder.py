"""Manifest-driven source corpus construction without executing project code."""
from __future__ import annotations

import fnmatch
import json
import ast
import hashlib
import os
import tempfile
import warnings
import subprocess
from collections import Counter
from dataclasses import asdict, dataclass
from pathlib import Path

from .ingest import ingest_source
from .fixtures import FixtureInput, extract_fixture
from .manifest import CorpusProject, artifact_id, load_manifest, write_lock
from .semantic import ProgramGraph, SCHEMA_VERSION
from .synthetic import damaged_view, format_result, rename_result
from .curation import CuratedInput, canonical_hash, curated_inputs, load_release, raw_hash, write_report


GRAPH_PIPELINE_VERSION = "graph-v3-fields-bindings-v1-transform-v3"
RELEASE_VERSION = "v0.3"


def _repository_identity(url: str) -> str:
    value = url.strip().removesuffix(".git")
    if value.startswith("git@github.com:"):
        value = "github.com/" + value.removeprefix("git@github.com:")
    for prefix in ("https://", "http://", "ssh://git@"):
        if value.startswith(prefix):
            value = value.removeprefix(prefix)
    return value.lower().rstrip("/")


@dataclass(frozen=True)
class CorpusView:
    artifact_id: str
    project: str
    split: str
    view_kind: str
    graph_path: str
    metadata: dict


def _split(name: str) -> str:
    value = int(artifact_id(name)[:8], 16) % 100
    return "train" if value < 80 else "validation" if value < 90 else "test"


def _included(project: CorpusProject, relative: str) -> bool:
    def matches(pattern: str) -> bool:
        # `**/` means zero or more directories. fnmatch itself treats it as at
        # least one directory, which silently omitted package-root modules.
        variants = {pattern}
        pending = [pattern]
        while pending:
            value = pending.pop()
            start = value.find("**/")
            if start >= 0:
                reduced = value[:start] + value[start + 3:]
                if reduced not in variants:
                    variants.add(reduced)
                    pending.append(reduced)
        return any(fnmatch.fnmatchcase(relative, value) for value in variants)
    return any(matches(pattern) for pattern in project.include) and not any(
        matches(pattern) for pattern in project.exclude
    )


def _checkout(project: CorpusProject, checkout_root: Path) -> Path:
    checkout_root.mkdir(parents=True, exist_ok=True)
    destination = checkout_root / project.name
    if destination.resolve().parent != checkout_root.resolve():
        raise ValueError(f"unsafe checkout name: {project.name!r}")
    if destination.exists():
        completed = subprocess.run(["git", "-C", str(destination), "rev-parse", "HEAD"], check=False,
                                   capture_output=True, text=True)
        origin = subprocess.run(["git", "-C", str(destination), "remote", "get-url", "origin"],
                                check=False, capture_output=True, text=True)
        dirty_worktree = subprocess.run(["git", "-C", str(destination), "diff", "--quiet"],
                                        check=False, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        dirty_index = subprocess.run(["git", "-C", str(destination), "diff", "--cached", "--quiet"],
                                     check=False, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        sparse = subprocess.run(["git", "-C", str(destination), "config", "--bool", "core.sparseCheckout"],
                                check=False, capture_output=True, text=True)
        if (completed.returncode == 0 and completed.stdout.strip() == project.revision and
                origin.returncode == 0 and
                _repository_identity(origin.stdout) == _repository_identity(project.url) and
                dirty_worktree.returncode == 0 and dirty_index.returncode == 0 and
                sparse.stdout.strip() != "true"):
            return destination
        raise RuntimeError(
            f"refusing to replace stale, dirty, foreign, or sparse checkout {destination}; "
            "use a new release directory"
        )
    subprocess.run(["git", "clone", "--filter=blob:none", "--no-checkout", project.url, str(destination)], check=True)
    subprocess.run(["git", "-C", str(destination), "checkout", "--detach", project.revision], check=True)
    return destination


def _tracked_source_paths(project: CorpusProject, checkout: Path) -> list[Path]:
    """Select only committed files so local/untracked data cannot enter a release."""
    completed = subprocess.run(["git", "-C", str(checkout), "ls-files", "-z"], check=True,
                               capture_output=True)
    paths: list[Path] = []
    for raw in completed.stdout.split(b"\0"):
        if not raw:
            continue
        relative = raw.decode("utf-8", errors="surrogateescape")
        path = checkout / relative
        if path.is_file() and path.suffix in project.source_extensions and _included(project, relative):
            paths.append(path)
    return sorted(paths)


def _labels(project: CorpusProject, fixture: FixtureInput, source_hash: str, exact_hash: str = "") -> dict:
    labels = {"pair_id": source_hash, "python_min": project.python_min, "python_max": project.python_max,
              "research_tier": project.research_tier, "structural_source_hash": source_hash,
              "exact_source_hash": exact_hash, **fixture.metadata}
    if project.fixture_extractor == "mypy":
        labels.setdefault("diagnostic_family", "typing")
    elif project.fixture_extractor == "markdown" and labels.get("expected_outcome") == "diagnostic":
        labels.setdefault("diagnostic_family", "lint")
    elif project.fixture_extractor == "cpython":
        labels.setdefault("diagnostic_family", "syntax")
    elif project.fixture_extractor == "black":
        labels.setdefault("diagnostic_family", "formatting")
    return labels


def _uncurated_inputs(projects: list[CorpusProject], checkouts: Path) -> list[CuratedInput]:
    values: list[CuratedInput] = []
    for project in projects:
        checkout = _checkout(project, checkouts)
        split = project.partition if project.partition != "auto" else _split(project.split_group or project.name)
        for source_path in _tracked_source_paths(project, checkout):
            relative = source_path.relative_to(checkout).as_posix()
            if not _included(project, relative):
                continue
            container = source_path.read_text(encoding="utf-8", errors="replace")
            inputs = extract_fixture(project.fixture_extractor, container) if project.fixture_extractor else [FixtureInput("source", container, {})]
            values.extend(CuratedInput(project, relative, fixture, canonical_hash(fixture.source), split,
                                       raw_hash(fixture.source))
                          for fixture in inputs)
    return values


def _atomic_text(path: Path, value: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary_name = tempfile.mkstemp(prefix=f".{path.name}.", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
            handle.write(value)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary_name, path)
    finally:
        Path(temporary_name).unlink(missing_ok=True)


def _cap_graph_records(records: list[CorpusView], projects: list[CorpusProject],
                       cap: int) -> tuple[list[CorpusView], list[dict]]:
    """Apply the release cap to comparable graph units, preserving all views."""
    if cap < 1:
        raise ValueError("graph unit cap must be positive")
    repository = {project.name: _repository_identity(project.url) for project in projects}
    primary = {"source", "untransformed", "input:source", "output:source",
               "input:untransformed", "output:untransformed"}
    units: dict[str, dict[str, set[str]]] = {}
    for record in records:
        if record.view_kind not in primary:
            continue
        units.setdefault(repository[record.project], {}).setdefault(record.project, set()).add(record.artifact_id)
    selected: set[str] = set()
    ledger: list[dict] = []
    for repo, by_project in sorted(units.items()):
        floor = cap // len(by_project)
        chosen: set[str] = set()
        leftovers: list[tuple[str, str]] = []
        for project, identifiers in sorted(by_project.items()):
            ordered = sorted(identifiers, key=artifact_id)
            chosen.update(ordered[:floor])
            leftovers.extend((identifier, project) for identifier in ordered[floor:])
        capacity = cap - len(chosen)
        chosen.update(identifier for identifier, _ in sorted(
            leftovers, key=lambda item: artifact_id(item[0]))[:capacity])
        selected.update(chosen)
        for project, identifiers in sorted(by_project.items()):
            for identifier in sorted(identifiers):
                ledger.append({"repository": repo, "project": project, "artifact_id": identifier,
                               "disposition": "retained" if identifier in chosen else "excluded",
                               "reason": "" if identifier in chosen else "graph_unit_cap"})
    return [record for record in records if record.artifact_id in selected], ledger


def _compact_referenced_graphs(output: Path, records: list[CorpusView]) -> list[dict]:
    allowed: dict[str, set[str]] = {}
    for record in records:
        allowed.setdefault(record.graph_path, set()).add(record.metadata["unit_id"])
    manifest: list[dict] = []
    for relative, unit_ids in sorted(allowed.items()):
        path = output / relative
        kept = []
        for line in path.read_text().splitlines():
            if not line:
                continue
            value = json.loads(line)
            if value["unit_id"] in unit_ids:
                kept.append(line)
        if len(kept) != len(unit_ids):
            raise ValueError(f"graph compaction could not resolve every unit in {relative}")
        _atomic_text(path, "\n".join(kept) + "\n")
        manifest.append({"path": relative, "units": len(kept), "bytes": path.stat().st_size,
                         "sha256": hashlib.sha256(path.read_bytes()).hexdigest()})
    for path in (output / "graphs").rglob("*.jsonl"):
        if path.relative_to(output).as_posix() not in allowed:
            path.unlink()
    return manifest


def derive_unit_capped_release(source_root: str | Path, output_root: str | Path,
                               *, cap: int = 250) -> dict:
    """Derive a compact graph-unit-capped release from a completed schema-2 build."""
    source, output = Path(source_root), Path(output_root)
    if not (source / "COMPLETE.json").exists():
        raise ValueError("source release is incomplete")
    output.mkdir(parents=True, exist_ok=True)
    if (output / "COMPLETE.json").exists():
        raise RuntimeError(f"release is already complete and immutable: {output}")
    manifest_files = sorted(source.glob("release-*.manifest.jsonl"))
    if len(manifest_files) != 1:
        raise ValueError("source release must contain one canonical manifest")
    projects = load_manifest(manifest_files[0])
    records = [CorpusView(**json.loads(line)) for line in (source / "views.jsonl").read_text().splitlines()]
    original_views = len(records)
    records, ledger = _cap_graph_records(records, projects, cap)
    allowed: dict[str, set[str]] = {}
    for record in records:
        allowed.setdefault(record.graph_path, set()).add(record.metadata["unit_id"])
    graph_manifest = []
    for relative, unit_ids in sorted(allowed.items()):
        source_path, target = source / relative, output / relative
        kept = [line for line in source_path.read_text().splitlines()
                if line and json.loads(line)["unit_id"] in unit_ids]
        if len(kept) != len(unit_ids):
            raise ValueError(f"unable to materialize every selected unit from {relative}")
        _atomic_text(target, "\n".join(kept) + "\n")
        graph_manifest.append({"path": relative, "units": len(kept), "bytes": target.stat().st_size,
                               "sha256": hashlib.sha256(target.read_bytes()).hexdigest()})
    for name in ("curation-report.json", "curation-report.md", "curation-ledger.jsonl"):
        _atomic_text(output / name, (source / name).read_text())
    _atomic_text(output / manifest_files[0].name, manifest_files[0].read_text())
    _atomic_text(output / "views.jsonl", "".join(json.dumps(asdict(record), sort_keys=True) + "\n"
                                                  for record in records))
    _atomic_text(output / "graph-unit-ledger.jsonl", "".join(json.dumps(item, sort_keys=True) + "\n"
                                                               for item in ledger))
    _atomic_text(output / "graphs-manifest.jsonl", "".join(json.dumps(item, sort_keys=True) + "\n"
                                                             for item in graph_manifest))
    write_lock(output / "manifest.lock.json", projects)
    stats = {"projects": len(projects), "views": len(records), "uncapped_views": original_views,
             "retained_graph_units": len({record.artifact_id for record in records}),
             "by_view_kind": dict(sorted(Counter(record.view_kind for record in records).items())),
             "by_lane": dict(sorted(Counter(record.metadata["lane"] for record in records).items())),
             "by_split": dict(sorted(Counter(record.split for record in records).items())),
             "by_task_family": dict(sorted(Counter(
                 record.metadata.get("diagnostic_family", "transformation") for record in records).items()))}
    _atomic_text(output / "release-stats.json", json.dumps(stats, indent=2, sort_keys=True) + "\n")
    inventory_names = ["views.jsonl", "manifest.lock.json", "release-stats.json",
                       "curation-report.json", "curation-report.md", "curation-ledger.jsonl",
                       "graph-unit-ledger.jsonl", "graphs-manifest.jsonl", manifest_files[0].name]
    inventory = {name: {"bytes": (output / name).stat().st_size,
                        "sha256": hashlib.sha256((output / name).read_bytes()).hexdigest()}
                 for name in inventory_names}
    _atomic_text(output / "COMPLETE.json", json.dumps(
        {"format": 1, "graph_pipeline": GRAPH_PIPELINE_VERSION,
         "schema_version": SCHEMA_VERSION, "derived_from": str(source), "inventory": inventory},
        indent=2, sort_keys=True) + "\n")
    return {**stats, "output": str(output), "graph_files": len(graph_manifest)}


def build_corpus(manifest_path: str | Path, output_root: str | Path, *, checkout_root: str | Path | None = None,
                 curate: bool = False, max_units_per_project: int = 250) -> dict:
    projects = load_manifest(manifest_path)
    output = Path(output_root)
    output.mkdir(parents=True, exist_ok=True)
    if (output / "COMPLETE.json").exists():
        raise RuntimeError(f"release is already complete and immutable: {output}")
    checkouts = Path(checkout_root) if checkout_root else output / "checkouts"
    graphs_root = output / "graphs"
    if curate:
        for project in projects:
            _checkout(project, checkouts)
        inputs, report = curated_inputs(projects, checkouts, cap=max_units_per_project, release=RELEASE_VERSION)
        write_report(output / "curation-report.json", report)
    else:
        inputs, report = _uncurated_inputs(projects, checkouts), None
    records: list[CorpusView] = []
    for item in inputs:
        project, relative, fixture, split = item.project, item.relative, item.fixture, item.split
        source = fixture.source
        source_id = artifact_id(GRAPH_PIPELINE_VERSION, project.name, project.revision,
                                relative, fixture.identifier)
        base_metadata = _labels(project, fixture, item.source_hash, item.raw_hash)
        variants = [("source", source, dict(base_metadata))]
        try:
            # Never discard old-version/invalid fixture input merely because a
            # modern AST cannot safely transform it.
            with warnings.catch_warnings():
                warnings.simplefilter("ignore", SyntaxWarning)
                ast.parse(source)
            for transform_name, transform in (
                ("formatted", lambda: format_result(source)),
                ("renamed", lambda: rename_result(source, seed_material=source_id)),
            ):
                try:
                    transformed = transform()
                    if transformed.status == "applied":
                        variants.append((transform_name, transformed.source,
                                         {**base_metadata, "transform_status": "static_checked",
                                          "transform_policy": "v3_conservative",
                                          "changed_bindings": transformed.changed_bindings}))
                    else:
                        variants[0][2].setdefault("transformation_gaps", []).append(
                            {"view": transform_name, "status": transformed.status, "reason": transformed.reason})
                except (RecursionError, ValueError, TypeError) as exc:
                    variants[0][2].setdefault("transformation_gaps", []).append(
                        {"view": transform_name, "error": type(exc).__name__})
        except SyntaxError:
            variants.append(("untransformed", source, {**base_metadata, "transform_status": "unsupported_syntax"}))
        variants.append(("damaged", damaged_view(source), {**base_metadata, "severity": 1}))
        for view_kind, text, metadata in variants:
            file_path = graphs_root / project.name / f"{source_id}.{view_kind}.jsonl"
            file_path.parent.mkdir(parents=True, exist_ok=True)
            if file_path.exists():
                graphs = [ProgramGraph.from_dict(json.loads(line)) for line in file_path.read_text().splitlines() if line]
                try:
                    ast.parse(text)
                    lane = "ast"
                except SyntaxError:
                    lane = "recovery"
            else:
                result = ingest_source(text, origin=f"{project.name}/{relative}#{fixture.identifier}", reconstructed=view_kind == "damaged")
                graphs, lane = result.graphs, result.lane
                _atomic_text(file_path, "\n".join(json.dumps(graph.to_dict(), sort_keys=True) for graph in graphs) + "\n")
            for position, graph in enumerate(graphs):
                semantic_pair = metadata.get("semantic_pair")
                pair_scope = (artifact_id(project.name, project.revision, relative, str(semantic_pair))
                              if semantic_pair else source_id)
                unit_artifact_id = artifact_id(pair_scope, str(position))
                effective_view_kind = (f"{metadata['pair_role']}:{view_kind}"
                                       if semantic_pair else view_kind)
                records.append(CorpusView(unit_artifact_id, project.name, split, effective_view_kind,
                                          str(file_path.relative_to(output)),
                                          {"source_artifact_id": source_id, "unit_id": graph.unit_id,
                                           "lane": lane, "corpus_role": project.corpus_role,
                                           "split_group": project.split_group or project.name,
                                           "source_kind": Path(relative).suffix,
                                           "fixture_extractor": project.fixture_extractor or None,
                                           "semantic_trainable": lane == "ast" and view_kind in {"source", "formatted", "renamed"},
                                           **metadata}))
    uncapped_views = len(records)
    records, unit_ledger = _cap_graph_records(records, projects, max_units_per_project)
    graph_manifest = _compact_referenced_graphs(output, records)
    _atomic_text(output / "graph-unit-ledger.jsonl", "".join(
        json.dumps(item, sort_keys=True) + "\n" for item in unit_ledger))
    _atomic_text(output / "graphs-manifest.jsonl", "".join(
        json.dumps(item, sort_keys=True) + "\n" for item in graph_manifest))
    _atomic_text(output / "views.jsonl", "".join(json.dumps(asdict(record), sort_keys=True) + "\n" for record in records))
    write_lock(output / "manifest.lock.json", projects)
    view_counts = Counter(record.view_kind for record in records)
    lane_counts = Counter(record.metadata["lane"] for record in records)
    split_counts = Counter(record.split for record in records)
    task_counts = Counter(record.metadata.get("diagnostic_family", "transformation") for record in records)
    retained_graph_units = len({record.artifact_id for record in records})
    _atomic_text(output / "release-stats.json", json.dumps({"projects": len(projects), "views": len(records),
        "uncapped_views": uncapped_views, "retained_graph_units": retained_graph_units,
        "by_view_kind": dict(sorted(view_counts.items())), "by_lane": dict(sorted(lane_counts.items())),
        "by_split": dict(sorted(split_counts.items())), "by_task_family": dict(sorted(task_counts.items()))},
        indent=2, sort_keys=True) + "\n")
    inventory_names = ["views.jsonl", "manifest.lock.json", "release-stats.json",
                       "graph-unit-ledger.jsonl", "graphs-manifest.jsonl"]
    if report:
        inventory_names.extend(["curation-report.json", "curation-report.md", "curation-ledger.jsonl"])
    inventory = {}
    for name in inventory_names:
        path = output / name
        inventory[name] = {"bytes": path.stat().st_size,
                           "sha256": hashlib.sha256(path.read_bytes()).hexdigest()}
    _atomic_text(output / "COMPLETE.json", json.dumps(
        {"format": 1, "graph_pipeline": GRAPH_PIPELINE_VERSION,
         "schema_version": SCHEMA_VERSION, "inventory": inventory}, indent=2, sort_keys=True) + "\n")
    return {"projects": len(projects), "views": len(records), "output": str(output),
            "curated": curate, "retained_units": report.retained_units if report else None}


def build_release(manifest_paths: list[str | Path], output_root: str | Path, *, checkout_root: str | Path | None = None,
                  max_units_per_project: int = 250) -> dict:
    """Build the canonical schema-v2 release from reviewed manifests."""
    output = Path(output_root)
    output.mkdir(parents=True, exist_ok=True)
    projects = load_release(manifest_paths)
    canonical_manifest = output / f"release-{RELEASE_VERSION}.manifest.jsonl"
    _atomic_text(canonical_manifest, "".join(json.dumps(asdict(project), sort_keys=True) + "\n" for project in projects))
    return build_corpus(canonical_manifest, output, checkout_root=checkout_root, curate=True,
                        max_units_per_project=max_units_per_project)

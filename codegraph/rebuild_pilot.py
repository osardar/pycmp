"""Bounded static rebuild pilot using existing pinned checkouts only."""
from __future__ import annotations

import argparse
import ast
from collections import Counter
import hashlib
import json
from pathlib import Path
import resource
import sys
import time

from .corpus_builder import RELEASE_VERSION, _checkout, build_corpus
from .curation import curated_inputs
from .hardpair_diagnostics import facts
from .ingest import ingest_source
from .manifest import artifact_id, load_manifest
from .semantic import ProgramGraph, SCHEMA_VERSION
from .shared_model import FEATURE_KEYS, SharedGraphEncoder
from .synthetic import format_result, rename_result


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def transformation_findings(source, renamed, before, after):
    def type_facts(text):
        tree = ast.parse(text, type_comments=True)
        return sum(bool(getattr(n, "type_comment", None)) for n in ast.walk(tree)) + len(tree.type_ignores)
    left = {g.metadata["qualified_name"]: g for g in before}
    right = {g.metadata["qualified_name"]: g for g in after}
    units = []
    for name in sorted(left.keys() & right.keys()):
        a, b = left[name], right[name]
        changed = Counter()
        examples = []
        for na, nb in zip(a.nodes, b.nodes):
            for key in FEATURE_KEYS:
                if na.attributes.get(key) != nb.attributes.get(key):
                    changed[key] += 1
                    if key in {"binding_identity", "external_identity"} and len(examples) < 5:
                        examples.append({"source_line": na.attributes.get("line"), "feature": key,
                                         "before": na.attributes.get(key), "after": nb.attributes.get(key)})
        if changed or len(a.nodes) != len(b.nodes):
            units.append({"unit": name, "before_nodes": len(a.nodes), "after_nodes": len(b.nodes),
                          "feature_changes": dict(changed), "binding_examples": examples})
    return {"type_facts_before": type_facts(source), "type_facts_after": type_facts(renamed),
            "units": units,
            "caution": "node comparisons use traversal order; differing shapes are diagnostic only"}


def verify_release(root: Path) -> dict:
    complete = json.loads((root / "COMPLETE.json").read_text())
    if complete["schema_version"] != SCHEMA_VERSION:
        raise ValueError("wrong release schema")
    for relative, entry in complete["inventory"].items():
        path = root / relative
        if path.stat().st_size != entry["bytes"] or sha(path) != entry["sha256"]:
            raise ValueError("inventory mismatch: " + relative)
    totals = Counter()
    largest = {"nodes": 0, "edges": 0, "file_bytes": 0}
    for line in (root / "graphs-manifest.jsonl").read_text().splitlines():
        entry = json.loads(line)
        path = root / entry["path"]
        if path.stat().st_size != entry["bytes"] or sha(path) != entry["sha256"]:
            raise ValueError("graph checksum mismatch: " + entry["path"])
        graphs = [ProgramGraph.from_dict(json.loads(s)) for s in path.read_text().splitlines()]
        if len(graphs) != entry["units"]:
            raise ValueError("unit count mismatch")
        totals["graph_files"] += 1
        totals["serialized_bytes"] += entry["bytes"]
        largest["file_bytes"] = max(largest["file_bytes"], entry["bytes"])
        for graph in graphs:
            totals["graphs"] += 1
            totals["nodes"] += len(graph.nodes)
            totals["edges"] += len(graph.edges)
            largest["nodes"] = max(largest["nodes"], len(graph.nodes))
            largest["edges"] = max(largest["edges"], len(graph.edges))
    counts = Counter()
    units = set()
    for line in (root / "views.jsonl").read_text().splitlines():
        row = json.loads(line)
        key = (row["project"], row["artifact_id"])
        if key not in units:
            counts[row["project"]] += 1
            units.add(key)
    return {"totals": dict(totals), "largest": largest, "units_per_project": dict(counts)}


def verify_generated_transforms(root: Path, model) -> dict:
    rows = [json.loads(s) for s in (root / "views.jsonl").read_text().splitlines()]
    signatures = {}
    for relative in sorted({r["graph_path"] for r in rows}):
        for line in (root / relative).read_text().splitlines():
            graph = ProgramGraph.from_dict(json.loads(line))
            signatures[(relative, graph.unit_id)] = (graph.metadata.get("qualified_name"), facts(graph, model)["tensors"])
    originals = {}
    for row in rows:
        if row["view_kind"].split(":")[-1] == "source":
            name, signature = signatures[(row["graph_path"], row["metadata"]["unit_id"])]
            originals[(row["metadata"]["source_artifact_id"], name)] = signature
    checked = Counter()
    failures = []
    for row in rows:
        kind = row["view_kind"].split(":")[-1]
        if kind not in {"renamed", "formatted"}:
            continue
        name, signature = signatures[(row["graph_path"], row["metadata"]["unit_id"])]
        key = (row["metadata"]["source_artifact_id"], name)
        checked[kind] += 1
        if originals.get(key) != signature or row["metadata"].get("transform_status") != "static_checked":
            failures.append({"project": row["project"], "kind": kind, "unit": name,
                             "missing_source": key not in originals})
    return {"checked": dict(checked), "failures": failures}


def run(manifest: Path, checkouts: Path, output: Path, legacy: Path, cap: int = 50) -> dict:
    if output.exists():
        raise ValueError("choose a new pilot directory")
    projects = load_manifest(manifest)
    if len(projects) > 8 or not 1 <= cap <= 50:
        raise ValueError("pilot permits at most eight projects and cap <= 50")
    # Refuse to fetch new repositories in a resource-only pilot.
    for project in projects:
        if not (checkouts / project.name).is_dir():
            raise ValueError("pilot requires existing checkout: " + project.name)
        _checkout(project, checkouts)
    output.mkdir(parents=True)
    definition = {"schema": SCHEMA_VERSION, "manifest": str(manifest), "manifest_sha256": sha(manifest),
                  "cap": cap, "checkouts": str(checkouts), "legacy": str(legacy),
                  "budgets": {"wall_seconds": 300, "peak_rss_bytes": 1024**3,
                              "max_graph_file_bytes": 32*1024**2},
                  "network_fetch": False, "third_party_execution": False, "training": False,
                  "code_hashes": {name: sha(Path(__file__).with_name(name)) for name in
                                  ("rebuild_pilot.py", "corpus_builder.py", "ast_normalize.py", "source_evidence.py",
                                   "synthetic.py", "curation.py", "fixtures.py", "semantic.py", "shared_model.py")}}
    (output / "definition.json").write_text(json.dumps(definition, indent=2)+"\n")
    started = time.perf_counter()
    release = output / "release"
    build_corpus(manifest, release, checkout_root=checkouts, curate=True, max_units_per_project=cap)
    build_seconds = time.perf_counter()-started
    integrity = verify_release(release)
    inputs, curation = curated_inputs(projects, checkouts, cap=cap, release=RELEASE_VERSION)
    model = SharedGraphEncoder(dimension=8, layers=1).eval()  # buckets only, no embedding/scoring
    generated_transforms = verify_generated_transforms(release, model)
    profiles = []
    for index, item in enumerate(inputs, 1):
        begin = time.perf_counter()
        graphs = ingest_source(item.fixture.source, origin=item.relative).graphs
        elapsed = time.perf_counter()-begin
        serialized = "\n".join(json.dumps(g.to_dict(), sort_keys=True) for g in graphs)+"\n"
        profile = {"project": item.project.name, "path": item.relative, "fixture": item.fixture.identifier,
                   "raw_sha256": item.raw_hash, "source_bytes": len(item.fixture.source.encode()),
                   "normalize_seconds": elapsed, "units": len(graphs),
                   "nodes": sum(len(g.nodes) for g in graphs), "edges": sum(len(g.edges) for g in graphs),
                   "serialized_bytes": len(serialized.encode()),
                   "binding_edges": sum(e.kind in {"def_use", "may_def_use"} for g in graphs for e in g.edges),
                   "unresolved_references": sum(str(n.attributes.get("binding_identity", "")).startswith(
                       ("unresolved:", "dynamic_unresolved:", "unresolved_nonlocal:")) for g in graphs for n in g.nodes)}
        legacy_id = artifact_id("graph-v2-transform-v2", item.project.name, item.project.revision,
                                item.relative, item.fixture.identifier)
        old = legacy / "graphs" / item.project.name / (legacy_id+".source.jsonl")
        if old.is_file():
            # Read-only historical evidence; never load schema-2 graphs as schema 3.
            old_graphs = [json.loads(line) for line in old.read_text().splitlines()]
            profile["schema2_reference"] = {"path": str(old), "sha256": sha(old),
                "bytes": old.stat().st_size, "units": len(old_graphs),
                "nodes": sum(len(g["nodes"]) for g in old_graphs),
                "edges": sum(len(g["edges"]) for g in old_graphs)}
        if all(g.metadata["lane"] == "ast" for g in graphs):
            left = {g.metadata["qualified_name"]: facts(g, model)["tensors"] for g in graphs}
            for label, transformed in (("rename", rename_result(item.fixture.source, seed_material="schema3-pilot")),
                                       ("format", format_result(item.fixture.source))):
                profile[label+"_status"] = transformed.status
                profile[label+"_reason"] = transformed.reason
                if transformed.status != "applied":
                    continue
                others = ingest_source(transformed.source, origin=item.relative).graphs
                right = {g.metadata["qualified_name"]: facts(g, model)["tensors"] for g in others}
                profile[label+"_tensor_equal"] = left == right
                profile[label+"_changed_units"] = sorted(n for n in left.keys() | right.keys() if left.get(n) != right.get(n))
                if left != right:
                    profile[label+"_findings"] = transformation_findings(item.fixture.source, transformed.source, graphs, others)
        profiles.append(profile)
        if index % 10 == 0 or index == len(inputs):
            print(f"Profiled {index}/{len(inputs)} curated inputs", flush=True)
    total_seconds = time.perf_counter()-started
    rss = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    rss_bytes = int(rss if sys.platform == "darwin" else rss * 1024)
    failures = [p for p in profiles if p.get("rename_tensor_equal") is False]
    transformation_counts = {label: dict(Counter(p[label+"_status"] for p in profiles if label+"_status" in p))
                             for label in ("rename", "format")}
    gates = {"inventory_and_graph_checksums": True,
             "repository_cap": all(n <= cap for n in integrity["units_per_project"].values()),
             "time_budget": total_seconds <= definition["budgets"]["wall_seconds"],
             "memory_budget": rss_bytes <= definition["budgets"]["peak_rss_bytes"],
             "graph_file_budget": integrity["largest"]["file_bytes"] <= definition["budgets"]["max_graph_file_bytes"],
             "rename_invariance": not failures and transformation_counts["rename"].get("applied", 0) > 0,
             "format_invariance": not any(p.get("format_tensor_equal") is False for p in profiles)
                                   and transformation_counts["format"].get("applied", 0) > 0,
             "curation_version": curation.release == RELEASE_VERSION,
             "generated_transform_invariance": not generated_transforms["failures"]}
    report = {"definition": definition, "stats": json.loads((release / "release-stats.json").read_text()),
              "curation": curation.as_dict(), "integrity": integrity,
              "build_seconds": build_seconds, "total_seconds": total_seconds, "peak_rss_bytes": rss_bytes,
              "rss_scope": "single pilot process including imports/build/verification/profile; excludes child git processes",
              "gates": gates, "transformation_counts": transformation_counts,
              "generated_transforms": generated_transforms,
              "ready_for_full_rebuild": all(gates.values()), "profiles": profiles}
    (output / "pilot.json").write_text(json.dumps(report, indent=2, sort_keys=True)+"\n")
    return {k:v for k,v in report.items() if k not in {"profiles", "definition", "curation"}}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", type=Path, default=Path("corpus/schema3-pilot.jsonl"))
    parser.add_argument("--checkouts", type=Path, default=Path("corpus-runs/checkouts-v0.2"))
    parser.add_argument("--legacy", type=Path, default=Path("corpus-runs/release-v0.2"))
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(run(args.manifest, args.checkouts, args.output, args.legacy), sort_keys=True))


if __name__ == "__main__":
    main()

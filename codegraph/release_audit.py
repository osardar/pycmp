"""Static integrity and transform gate for a completed capped corpus release."""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import json
from pathlib import Path
import resource
import sys
import time

from .corpus_builder import GRAPH_PIPELINE_VERSION, RELEASE_VERSION, _repository_identity
from .manifest import load_manifest
from .rebuild_pilot import sha, verify_generated_transforms, verify_release
from .shared_model import SharedGraphEncoder


def coverage(rows):
    splits = defaultdict(set)
    gaps = Counter()
    sources = set()
    semantic = Counter()
    for row in rows:
        metadata = row["metadata"]
        splits[metadata["split_group"]].add(row["split"])
        if metadata.get("semantic_trainable"):
            semantic[row["split"]] += 1
        if row["view_kind"].split(":")[-1] == "source":
            key = (row["project"], metadata["source_artifact_id"])
            if key not in sources:
                sources.add(key)
                for gap in metadata.get("transformation_gaps", []):
                    gaps["/".join((gap["view"], gap.get("status", "error"),
                                   gap.get("reason", gap.get("error", "unknown"))))] += 1
    return {"retained_source_inputs": len(sources), "transformation_gaps": dict(sorted(gaps.items())),
            "semantic_views_by_split": dict(semantic),
            "split_group_leaks": {key: sorted(values) for key, values in splits.items() if len(values) > 1}}


def audit(root: Path, cap: int = 250) -> dict:
    start = time.perf_counter()
    complete = json.loads((root / "COMPLETE.json").read_text())
    integrity = verify_release(root)
    print("Inventory and graph checksums verified", flush=True)
    rows = [json.loads(line) for line in (root / "views.jsonl").read_text().splitlines()]
    summary = coverage(rows)
    transforms = verify_generated_transforms(root, SharedGraphEncoder(dimension=8, layers=1).eval())
    curation = json.loads((root / "curation-report.json").read_text())
    manifest = root / f"release-{RELEASE_VERSION}.manifest.jsonl"
    projects = load_manifest(manifest)
    repositories = {p.name: _repository_identity(p.url) for p in projects}
    repository_units = defaultdict(set)
    for row in rows:
        repository_units[repositories[row["project"]]].add(row["artifact_id"])
    integrity["units_per_repository"] = {key: len(value) for key, value in sorted(repository_units.items())}
    missing = sorted(p.name for p in projects if p.name not in integrity["units_per_project"])
    gates = {"inventory_and_graph_checksums": True,
             "pipeline_version": complete["graph_pipeline"] == GRAPH_PIPELINE_VERSION,
             "curation_version": curation["release"] == RELEASE_VERSION,
             "repository_cap": all(n <= cap for n in integrity["units_per_repository"].values()),
             "split_group_disjoint": not summary["split_group_leaks"],
             "generated_transform_invariance": not transforms["failures"] and
                 all(transforms["checked"].get(k, 0) > 0 for k in ("renamed", "formatted")),
             "semantic_split_coverage": all(summary["semantic_views_by_split"].get(k, 0) > 0
                                            for k in ("train", "validation", "test"))}
    rss = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    return {"release": str(root), "manifest_sha256": sha(manifest), "complete_sha256": sha(root / "COMPLETE.json"),
            "code_hashes": {name: sha(Path(__file__).with_name(name)) for name in
                            ("release_audit.py", "rebuild_pilot.py", "corpus_builder.py", "synthetic.py",
                             "curation.py", "fixtures.py", "ast_normalize.py", "source_evidence.py",
                             "semantic.py", "shared_model.py")},
            "integrity": integrity, "coverage": summary, "generated_transforms": transforms,
            "zero_contribution_projects": missing,
            "stats": json.loads((root / "release-stats.json").read_text()), "gates": gates,
            "static_gates_pass": all(gates.values()),
            "seconds": time.perf_counter() - start,
            "peak_rss_bytes": int(rss if sys.platform == "darwin" else rss * 1024),
            "limitations": ["Static transform consistency is not behavioral equivalence.",
                            "Coverage gaps and resource measurements require review before training.",
                            "This audit does not establish retrieval or classification accuracy."]}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("release", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--cap", type=int, default=250)
    args = parser.parse_args()
    if args.cap < 1 or args.output.exists():
        parser.error("cap must be positive and output must be new")
    result = audit(args.release, args.cap)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("x") as handle:
        handle.write(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"gates": result["gates"], "output": str(args.output)}, indent=2))
    return 0 if result["static_gates_pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())

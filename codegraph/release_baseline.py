"""Fixed small, three-seed baseline after a successful static release audit."""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
import resource
import sys
import time

import torch

from .hardpair_diagnostics import diagnose
from .rebuild_pilot import sha
from .workflow import train_corpus, write_benchmark_report


def run(release: Path, audit_path: Path, output: Path) -> dict:
    if output.exists():
        raise ValueError("choose a new baseline output directory")
    audit = json.loads(audit_path.read_text())
    if not audit.get("static_gates_pass") or not all(audit.get("gates", {}).values()):
        raise ValueError("release audit did not pass")
    if audit.get("complete_sha256") != sha(release / "COMPLETE.json"):
        raise ValueError("release differs from audited completion inventory")
    if Path(audit["release"]).resolve() != release.resolve():
        raise ValueError("audit belongs to another release")
    output.mkdir(parents=True)
    torch.set_num_threads(1)
    definition = {"release": str(release), "audit_sha256": sha(audit_path),
                  "complete_sha256": audit["complete_sha256"],
                  "seeds": [0, 1, 2], "epochs": 1, "dimension": 64, "layers": 2,
                  "batch_size": 32, "device": "cpu", "torch_threads": 1,
                  "hardpair_split": "train", "reserved_hardpair_test_scored": False,
                  "code_hashes": {name: sha(Path(__file__).with_name(name)) for name in
                                  ("release_baseline.py", "workflow.py", "training.py", "shared_model.py",
                                   "hardpair_diagnostics.py")}}
    (output / "definition.json").write_text(json.dumps(definition, indent=2) + "\n")
    results = []
    start = time.perf_counter()
    for seed in definition["seeds"]:
        print(f"Training fixed baseline seed {seed}", flush=True)
        started = time.perf_counter()
        checkpoint = output / f"model-seed{seed}.pt"
        training = train_corpus(release, checkpoint, epochs=1, batch_size=32,
                                seed=seed, dimension=64, layers=2)
        if not math.isfinite(training["loss"]):
            raise ValueError("non-finite training loss; do not use checkpoint")
        training_seconds = time.perf_counter() - started
        print(f"Evaluating seed {seed}; training took {training_seconds:.1f}s", flush=True)
        benchmark = write_benchmark_report(release, checkpoint, output / f"benchmark-seed{seed}.json")
        diagnose(checkpoint, output / f"hardpairs-train-seed{seed}", split="train")
        row = {"seed": seed, "training": training, "training_seconds": training_seconds,
               "checkpoint_sha256": sha(checkpoint), "benchmark": benchmark}
        (output / f"result-seed{seed}.json").write_text(json.dumps(row, indent=2) + "\n")
        results.append(row)
        print(f"Completed seed {seed}: paired Recall@5={benchmark.get('paired_recall_at_5')}", flush=True)
    rss = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    result = {"definition": definition, "results": results, "seconds": time.perf_counter() - start,
              "peak_rss_bytes": int(rss if sys.platform == "darwin" else rss * 1024),
              "limitations": ["One-epoch baseline, not a harder-training or model-promotion gate.",
                              "Corpus test retrieval is paired-query retrieval, not classification accuracy.",
                              "Development hard-pair results do not replace untouched final evaluation."]}
    (output / "summary.json").write_text(json.dumps(result, indent=2) + "\n")
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("release", type=Path)
    parser.add_argument("--audit", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    run(args.release, args.audit, args.output)


if __name__ == "__main__":
    main()

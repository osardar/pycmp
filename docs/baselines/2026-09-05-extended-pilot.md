# Extended corpus pilot baseline

Date: 2026-09-05

## Purpose

This is the first project-disjoint retrieval baseline using the newly added
extended-analysis sources. It validates the build, shared-encoder training, and
held-out retrieval path. It is intentionally small and is **not** a claim of
general clone-detection quality.

## Inputs

Manifest: `corpus/baseline-pilot.jsonl`

| Partition | Project | Immutable revision | Selected input |
|---|---|---|---|
| Train | Bandit | `1d3053df070c91fe0fde002a21536c277d67e5d9` | `examples/subprocess_shell.py` |
| Train | Hypothesis | `a8dcd7422a325926693b5464f73349e361562b7c` | `hypothesis/src/hypothesis/strategies/_internal/core.py` |
| Test | beartype | `b0275fa6b99a42e7fa6c8ce23d2d5513de1028a5` | `beartype/_decor/decorcore.py` |

All sources were cloned at their pinned revisions and parsed statically. No
third-party package, test suite, scanner, or source file was executed.

## Configuration

- Views: source, formatted, renamed, and damaged where applicable
- Encoder: `SharedGraphEncoder`, default 256-dimensional normalized vectors
- Optimizer: AdamW, learning rate `1e-3`
- Epochs: 1
- Batch size: 16
- Seed: 0
- Metric: paired-view Recall@5 on held-out project units

## Result

| Measure | Value |
|---|---:|
| Training views | 400 |
| Test views | 12 |
| Eligible held-out queries | 12 |
| Mean training loss | 1.62797 |
| Paired-view Recall@5 | 1.0000 |

## Interpretation

The pipeline retrieved a transformed view of the same held-out Beartype unit
within the first five nearest neighbors for all 12 eligible queries. This shows
that the shared encoder, corpus artifacts, and project-disjoint retrieval path
operate end-to-end.

The result is deliberately narrow: only one held-out source file contributed
test units, and positives are mechanically related views. It does not measure
semantic clone retrieval, linter-family retrieval, source-to-stub comparison,
or source-to-recovery comparison. It must not be represented as clone F1 or as
a full corpus benchmark.

## Next evaluation

Build a balanced multi-project holdout after fixture extractors and diagnostic
labels exist. Report Recall@1/5/10, MRR, label-family retrieval, and
cross-lane results with unavailable features masked.

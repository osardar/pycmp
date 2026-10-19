# Bytecode-to-bytecode similarity evaluation

Date: 2026-09-12. Status: implemented and measured.

Current interpretation: this is development-gallery evidence, not an estimate
of malware-family generalization. The strongest transparent baselines outperform
the trained checkpoints; current expanded cross-runtime work is tracked separately
in [COMPILED-RETRIEVAL-PLAN.md](COMPILED-RETRIEVAL-PLAN.md) and
[STATUS.md](STATUS.md).

This evaluation asks whether the three frozen schema-3 encoders can retrieve a
known compiled-code lineage when both query and gallery are direct bytecode.
It reuses the completed corpus-derived expansion without recompilation,
decompilation, corpus execution, retraining or index promotion.

The current decoder accepts only the 9,941 Python 3.14 artifacts. Python 3.4,
3.8 and 3.12 remain measured decoder gaps and are not represented by placeholder
graphs. The gallery contains the 179 supported unchanged originals at each of
optimization levels 0, 1 and 2. Queries are exact-binary deduplicated within
each optimization while retaining every source-recipe alias: 5,284 at level 0
and 5,209 each at levels 1 and 2.

Every query optimization is ranked against every gallery optimization. The
result therefore contains nine cells and 47,106 observations. Same-optimization
retrieval is primary; cross-optimization retrieval measures compiler-option
robustness. Candidate identity is the original gallery lineage, and conservative
ties use the existing `1e-7` tolerance.

The methods are the three trained checkpoints, the matching fixed untrained
encoder, hashed graph features and a transparent opcode-structure count
baseline. Source token and operation/API baselines are not applicable. Reports
include cosine, rank, Hit@1/5/10, MRR, non-lineage margin, unchanged-control
delta, binary identity and decoded feature/tensor equality. Results are sliced
by recipe family, dose, repository, split and both optimization levels, with
repository/fork-group bootstrap intervals and paired baseline differences.

The command is resumable and requires a distinct output directory:

```console
uv run pycmp-codegraph corpus-similarity bytecode-evaluate \
  --input-run corpus-runs/corpus-similarity-v3-expansion \
  --output corpus-runs/bytecode-similarity-v1 \
  --checkpoint corpus-runs/schema3-baseline-v1/model-seed0.pt \
  --checkpoint corpus-runs/schema3-baseline-v1/model-seed1.pt \
  --checkpoint corpus-runs/schema3-baseline-v1/model-seed2.pt \
  --resume
```

A deterministic pilot covers all recipe families, methods and optimization
cells before the full evaluation. Expansion gates concern integrity, coverage,
control invariance, resource use and resumability; model scores are findings,
never gates. The 179-lineage gallery is intentionally a preliminary benchmark
and is easier than the 2,270-entry source gallery. Results do not establish
behavioral equivalence, malware classification, attribution or unknown-family
detection.

## Measured result

The completed `corpus-runs/bytecode-similarity-v3/` run contains 15,702 unique
queries and all 47,106 planned rankings. Trained Hit@1 is 90.15–92.35% overall,
93.01–94.34% within the same optimization level and 88.72–91.51% across
optimization levels. The untrained encoder reaches 90.75% overall, hashed graphs
95.78%, and opcode structure 96.40%. Direct bytecode lineage retrieval is useful
in this supported lane, but the trained checkpoints do not beat the simple
baselines and therefore are not promotion candidates.

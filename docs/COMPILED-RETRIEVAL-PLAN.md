# Expanded compiled retrieval experiment

Current execution status (2026-10-19): implementation and owned pilot gates are
complete; the expanded experiment remains **partial**. Its ledger accounts for
all 159,768 preparation jobs, but only 69/441 full file-evaluation cells have
completed (all 441 pilot file and bundle cells are recorded). The run has
`PARTIAL.json`, not `COMPLETE.json`. See [STATUS.md](STATUS.md) for current counts
and use the run-specific resume command only with the matching ignored artifacts.

Approved scope: Python 3.8–3.14, all 2,270 frozen gallery inputs, existing source
variants, and sampled repository bundles containing at least five real source
files. Checkpoints remain frozen. Each runtime is pinned by image ID, digest,
platform and exact Python version before corpus work starts.

Compile at optimization 0/1/2 and decode using the matching runtime's `dis`.
Evaluate all 441 query/gallery configuration cells with trained seeds 0/1/2,
untrained seed 0, hashed graphs and opcode structure. Compare the original
179-lineage gallery and the expanded gallery on paired eligible queries. Report
available and matched coverage, binary controls, tensor equality and changing
queries separately; retain missing origins, duplicate ownership and ties.

Bundle experiments group real source files by canonical repository. Deterministic
seeds 0/1/2 remove 10/30/50/70 percent of files, inject 10/30/50 percent shared
modules from another group in the same split, and combine removal/injection at
10/10, 30/30, 50/50 and 70/50 percent. A separate condition uses existing combined
seed-0 dose-30-percent mutations where available. Bundles are sampled repository
contents, not complete applications. Aggregate file similarities using maximum,
top-five mean, inverse-repository-frequency weighted best matches, and maximum
weight one-to-one assignment normalized by query size. Preserve matched-file
evidence, coverage and injected-donor ranks.

The `compiled-retrieval prepare|evaluate|run` interface requires parent run,
output and three checkpoints; `--resume` verifies immutable fingerprints.
Each invocation shares a 12-hour deadline across stages. Four reusable workers
have 512 MiB each; coordinator RSS is capped at 8 GiB and cumulative output at
100 GiB. Workers have no network or privilege, mount staged inputs read-only,
and use per-item child-process deadlines and bounded output. Corpus code is
never imported or executed. A limit writes PARTIAL.json and an exact resume
command. Completed observations are durable and skipped on resume.

Owned fixtures and regression tests gate a runtime/recipe/configuration pilot.
Model scores never gate expansion. Reports include per-method group macro
metrics, 1,000 fixed-seed repository/fork bootstrap intervals, matched-query
baseline differences, all configuration cells and failure coverage. Fresh
external tests, packaging ingestion, abstention calibration, retraining and
promotion remain future work. Existing runs and their definitions are immutable.

## Invocation

Install the `benchmark` extra in the existing environment. Runtime images must
already be present locally; the runner never downloads images or corpus inputs.

```sh
.venv/bin/python -m codegraph.cli compiled-retrieval run \
  --input-run corpus-runs/corpus-similarity-v3-expansion \
  --output corpus-runs/compiled-retrieval-v1 \
  --checkpoint corpus-runs/schema3-baseline-v1/model-seed0.pt \
  --checkpoint corpus-runs/schema3-baseline-v1/model-seed1.pt \
  --checkpoint corpus-runs/schema3-baseline-v1/model-seed2.pt \
  --max-seconds 43200
```

Append `--resume` for subsequent invocations. Only `COMPLETE.json` denotes a
finished experiment; `PREPARED.json` and `PILOT.json` are intermediate gates.
The new `native-dis-v1` graph profile is experiment-specific, not a replacement
for the production decoder. Operand values are deliberately omitted; selected
encoder features do not include every decoded field. Results must not be merged
with the earlier decoder profile or interpreted as behavioral equivalence.

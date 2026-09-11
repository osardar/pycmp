# Schema-3 capped release and controlled baseline

Measured: 2026-09-11. This follows the [transform repair pilot](2026-09-10-transform-repair-pilot.md).
The full release is new; historical schema-1/2 and failed pilot artifacts are preserved.
Machine-readable [release audit](2026-09-11-schema3-capped-audit.json) records checksums,
implementation fingerprints, per-repository counts, gates and transformation gaps.

## Full rebuild and review

The three reviewed manifests (`lint-training-target`, `extended-analysis`,
`defensive-security`) resolve to 41 records / 39 URLs. All existing local checkouts
were verified against their pinned revisions before building; no fetch or execution
of upstream project code was needed. Output: `corpus-runs/release-v0.3-capped`.
The pipeline is `graph-v3-fields-bindings-v1-transform-v3`, with schema 3 and
curation release v0.3. The cap is 250 comparable units per canonical repository,
shared between source/fixture records for the same repository.

| Measurement | Result |
|---|---:|
| Curated source/fixture inputs before graph-unit cap | 4,302 |
| Retained source/fixture inputs represented after cap | 2,409 |
| Comparable graph units | 8,070 |
| Retained views | 25,687 |
| Views before graph-unit cap | 214,340 |
| Referenced graph files | 7,850 |
| Serialized graph bytes | 1,542,654,910 (1.44 GiB) |
| Graph nodes / edges | 2,500,300 / 2,740,752 |
| Largest retained graph | 36,385 nodes / 36,384 edges |
| Largest retained graph file | 12,039,181 bytes (11.48 MiB) |
| Build duration / peak RSS | 953.78 seconds / 1.37 GiB |
| Audit duration / peak RSS | 258.32 seconds / 536.19 MiB |

There are 40 Python-contributing records / 38 repository URLs. Certify is the
only zero-contribution record, consistent with its documented non-Python role.
The source curation ledger records 1,041 cross-project duplicate exclusions,
13,625 repository-cap exclusions, five generated/vendor-path exclusions and
one documented empty project. These are input-level counts, not graph-unit counts.
Temporary graph storage reached approximately 11 GiB before compaction; that
observation is not a precisely sampled peak. The final directory is about 1.5 GiB.

All seven static release gates pass: inventory/graph checksums, pipeline version,
curation version, repository cap, split-group disjointness, generated-transform
invariance and semantic coverage in all three splits. The maximum graph file
also remains below the pilot's 32 MiB budget. Full-release time/RSS measurements
are reported separately rather than reusing the small pilot's time/memory limits.

| Split | All views | Semantic-eligible views |
|---|---:|---:|
| Train | 17,813 | 14,083 |
| Validation | 3,765 | 3,002 |
| Test | 4,109 | 3,232 |

The lanes contain 25,317 AST and 370 recovery views. Semantic eligibility is
not the number of examples actually included in positive-bearing batches.
There is no direct-bytecode training evidence in this release.
Pipeline-version changes also change artifact identities used in deterministic
capping. This release is not an identical-unit sample to schema 2; benchmark
deltas must not be attributed solely to the new representation.

## Transform coverage

All 6,402 retained formatted views and 5,833 retained renamed views match their
source unit's encoder tensors, with zero failures. This covers 12,235 actual
generated unit views, not merely a fresh transform applied to a sample.

Gaps are counted once per retained source/fixture input, not once per nested unit:

| Transform gap | Inputs |
|---|---:|
| Formatting changes typed-AST evidence | 283 |
| Formatting recursion error | 1 |
| Already formatted | 7 |
| No eligible local rename bindings | 666 |
| Dynamic/reflective call | 100 |
| Dynamic scope | 67 |
| Frame/code introspection | 21 |
| Unverified annotation scope | 3 |

These gaps are explicit exclusions, not successful invariance checks. Counts
cover retained inputs; they do not describe every input discarded by capping.
Typed-AST/binding checks do not prove arbitrary runtime behavioral equivalence.

## Three-seed training and evaluation

The [baseline JSON](2026-09-11-schema3-baseline.json) records the definition,
checkpoint hashes, full-gallery metrics and development diagnostic summaries.
Output: `corpus-runs/schema3-baseline-v1`. Seeds 0, 1 and 2 each use one CPU epoch,
64 dimensions, two relational layers, batch size 32 and one Torch thread. This
matches the earlier small architecture; it is not a hyperparameter search.

Of 14,083 semantic-eligible training views, 13,653 enter positive-bearing batches
over 5,267 unit identities; 430 unpaired views are excluded by batching. The
existing trainer's `examples` field reports eligibility, not actual batched views.
The full three-seed train/evaluate/diagnose run took 237.52 seconds and peaked at
3.76 GiB process RSS. No checkpoint was selected for promotion.

There are 3,232 semantic test-gallery views and 3,215 eligible paired queries.
The untrained reference uses fixed seed 0 for every comparison; it is not three
independently seeded untrained baselines.

| Method | Recall@1 | Recall@5 | MRR | Development behavior top-1 |
|---|---:|---:|---:|---:|
| Trained seed 0 | 0.94246 | 0.97014 | 0.95509 | 3/8 |
| Trained seed 1 | 0.94121 | 0.97232 | 0.95492 | 2/8 |
| Trained seed 2 | 0.94184 | 0.97107 | 0.95492 | 2/8 |
| Fixed untrained encoder | 0.94152 | 0.97138 | 0.95498 | 2/8 |
| Hashed graph features | 0.93904 | 0.97014 | 0.95343 | 1/8 |

Training losses are 0.021856, 0.024996 and 0.025582. Training durations are 46.63,
53.07 and 52.00 seconds respectively. Lower loss is not a classifier-quality gate.
Development related-code top-1 is 4/8 for all three trained models and the fixed
untrained encoder; the token and operation/API baselines reach 5/8 and 6/8.
All eight development behavior changes remain observable; seed 0's diagnostic
flags pooling dilution for `helper_change` and `parameter_roles`.

The old 0.90 paired-retrieval threshold passes for all seeds, but there is **no
consistent learned advantage** over the untrained encoder. Most accepted positive
augmentations are deliberately tensor-identical, making this an easy invariance
test. The hard development results still fail to demonstrate reliable behavioral
ranking. Neither these percentages nor cosine similarities are maliciousness
probabilities. The eight development families are a tiny, already-inspected set,
not a final accuracy estimate. Reserved hard-pair test families were not executed
or scored. No project-bootstrap intervals or new unknown-family calibration were
produced, and direct-bytecode alignment remains unvalidated.

## Next experiment

1. Build a development-only training mix containing behavior-checked structural
   positives that actually change encoder inputs, plus explicitly labeled behavior
   negatives. Keep relatedness and behavior-preservation objectives separate.
2. Add project-balanced, node-budgeted batches and resumable checkpoints. The
   current soft view-count batch cap and in-memory loader remain scaling limits.
3. Compare at least three seeds with the same token/API/hashed/untrained galleries,
   project-macro metrics and repository-level intervals. Use validation for choices;
   preserve reserved test families until the final frozen evaluation.
4. Gate retrieval-index promotion on meaningful hard-case gains. Then validate
   direct bytecode, missing-feature profiles, explanations and unknown-family
   abstention. This run creates checkpoints, not a new operational retrieval index.

## Reproduction and artifacts

The build reused existing checkouts through the library entry point:

```python
from codegraph.corpus_builder import build_release
build_release(
    ["corpus/lint-training-target.jsonl", "corpus/extended-analysis.jsonl",
     "corpus/defensive-security.jsonl"],
    "corpus-runs/release-v0.3-capped",
    checkout_root="corpus-runs/checkouts-v0.2",
    max_units_per_project=250,
)
```

Use fresh output paths for another build/audit/baseline; completed evidence is
not overwritten:

```bash
.venv/bin/python -m codegraph.release_audit corpus-runs/release-v0.3-capped \
  --output corpus-runs/release-v0.3-capped/audit.json
.venv/bin/python -m codegraph.release_baseline corpus-runs/release-v0.3-capped \
  --audit corpus-runs/release-v0.3-capped/audit.json \
  --output corpus-runs/schema3-baseline-v1
```

Generated corpus, checkout and checkpoint files remain ignored by Git. Source,
manifests, tests and these Markdown/JSON reports are the versioned evidence.

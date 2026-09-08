# Synthetic similarity baseline — 2026-09-07

## Outcome

Implemented and executed a held-out, owned-code benchmark with ten concise Python projects,
60 behavior-preserving obfuscated variants (two levels × three seeds), and ten
behavior-changing near-copy controls. These are separate from the training corpus.

The frozen schema-2 checkpoint succeeds on many legacy reconstructions but does
not establish semantic equivalence or robust obfuscation resistance. Structural
obfuscation retrieval is weaker than the deterministic hashed-graph baseline.
Near-copy negatives make the weakness clearer.

## Executed coverage

- 296 source/runtime checks: 259 original/obfuscated checks passed; all 37
  negative-control checks failed at least one expected-behavior case.
- 111 project/runtime/optimization compilations, producing 123 bytecode files;
  all 111 sourceless bytecode behavior checks passed.
- 12 additional optimization probes passed, explicitly checking assertion,
  docstring, and `__debug__` behavior at optimization levels 0, 1, and 2.
- 222 project-level decompiler attempts: 63 verified successes, 84 unsupported,
  63 invalid outputs, 9 behavior mismatches, and 3 partial reconstructions.
- 1,624 pairwise comparisons across original, obfuscated, reconstructed, and
  negative variants. Failed/partial outputs are diagnostics, not positive pairs.

| Runtime | Successful decompiler attempts | Total attempts |
|---|---:|---:|
| Python 3.4 | 30 | 48 |
| Python 3.8 | 27 | 54 |
| Python 3.12 | 6 | 60 |
| Python 3.14 | 0 | 60 |

The optimized Python 3.4 artifacts are genuine `.pyo` files; newer interpreters
produce tagged `.pyc` files, including `.opt-1.pyc` and `.opt-2.pyc`.
No modern artifact is renamed to pretend it is legacy bytecode. The worker
creates temporary sourceless-import aliases only inside the verification container.

## Similarity scores

Numbers are **100 × cosine**, not probabilities or percentages of shared behavior.
Means use only oracle-passing obfuscations and complete, oracle-passing
decompilations. Each project has three seeds per obfuscation level. Decompiled
means pool compatible runtime/optimization/tool successes and are therefore
coverage-weighted. N/A means no successful reconstruction, not zero similarity.

| Project | Original ↔ decompiled | Original ↔ light | Original ↔ structural | Structural ↔ decompiled | Original ↔ negative |
|---|---:|---:|---:|---:|---:|
| async_queue | 99.23 | 100.00 | 87.44 | 86.60 | 99.99 |
| codec | 100.00 | 100.00 | 63.19 | 63.19 | 84.28 |
| dependencies | 99.72 | 100.00 | 75.37 | 74.66 | 85.65 |
| dispatch | 99.96 | 100.00 | 67.36 | 67.51 | 99.99 |
| events | 100.00 | 100.00 | 87.15 | 87.15 | 100.00 |
| inventory | 98.67 | 100.00 | 81.37 | 81.60 | 100.00 |
| invoice | 100.00 | 100.00 | 71.38 | 71.38 | 100.00 |
| memo | 100.00 | 100.00 | 80.35 | 80.35 | 99.99 |
| transaction | 100.00 | 100.00 | 90.57 | 90.57 | 97.23 |
| typed_router | N/A | 100.00 | 77.47 | N/A | 88.54 |

Light obfuscation changes text but leaves model inputs identical. Its 100% scores
measure normalization invariance, not learning. Structural seeds change identifiers
but not graph structure; the three seeds are reproducibility checks, not three
independent structural perturbations. Scores rounded to 100 can still reflect
different tensors and slightly different embeddings.

## Retrieval

Queries search ten originals (the matching project plus nine unrelated projects).
The harder setting adds the same project's behavior-changing near-copy as an
eleventh candidate. Ties within 1e-7 count against the correct original.

| Query kind | Queries | Trained top-1 | Untrained top-1 | Hashed graph top-1 | Trained + hard negative | Untrained + hard negative | Hashed + hard negative |
|---|---:|---:|---:|---:|---:|---:|---:|
| Light obfuscation | 30 | 30 | 30 | 30 | 30 | 30 | 30 |
| Structural obfuscation | 30 | 21 | 21 | 24 | 6 | 3 | 15 |
| Verified decompilation | 63 | 63 | 63 | 63 | 60 | 54 | 63 |

Negative controls themselves retrieve their related original in 10/10 trained
queries. This can be desirable for code-family similarity, but is not evidence
of identical behavior. No threshold was fitted to these ten projects. Repeated
optimization artifacts and seeds are correlated, so these query counts are not
independent statistical samples.

## Method and reproducibility

The existing 64-dimensional, two-layer, one-epoch checkpoint was frozen before
creating these fixtures; no retraining or test-set threshold tuning occurred.
Its SHA256 is `dd7eeefd810effc45aa990a42b317f4b5ab938d84921d1bc5a664494b9af6a9e`.

All three methods use the same ingested units. Normalize the mean unit embedding
per file, then normalize the equal-weighted mean of file embeddings per project.
Both modules in the invoice project contribute. Compare the trained model with
a seeded, architecture-matched untrained encoder and the hashed-graph baseline.

The benchmark actually decompiles compiled originals using uncompyle6 3.9.3
(xdis 6.1.8) and pycdc revision `b4289760970dbc399684f1e155ec6d1ea1cc787e`.
Reconstructed source is embedded through the source/recovery path. This measures
the decompile-to-source route, **not direct bytecode-lane embedding alignment**.
Original source is not mounted into the decompiler container; no hand repair or
source substitution is used to make a decompiler succeed.

Runtime images are digest-pinned and the tools image is resolved to an immutable
local image ID. Staged owned fixtures execute in read-only, non-root containers,
without networking, host corpus mounts, or capabilities, with memory/CPU/PID,
time, and output limits. This runner is for these owned fixtures, not arbitrary
malware execution. Behavior checks cover three cases per project and are not
proofs of full equivalence.

Build inputs, tool output, binaries, per-runtime oracles, source/AST/model-input
hashes, coverage, embeddings, and raw cosine values are retained locally in
`corpus-runs/similarity-v2/`. The COMPLETE inventory is checksum-verified before
evaluation. Build and evaluation code hashes are recorded separately: retrieval
hard-negative reporting was added after artifact generation, without changing
the completed artifacts.

- [Fixture inventory and reproduction commands](../../fixtures/similarity/README.md)
- [All pairwise scores and retrieval ranks](2026-09-07-synthetic-similarity-detail.md)
- [Machine-readable aggregate metrics and provenance](2026-09-07-synthetic-similarity.json)

Sources, generated obfuscated/negative sources, oracles, implementation, and these
reports are versioned. Compiled binaries, raw execution artifacts, full evaluation
JSON, embeddings, Docker images, and the existing checkpoint remain ignored/local.
The tools image build pins the base, pycdc revision and key Python packages, but
system/transitive packages can change on a fresh rebuild; compare the recorded
immutable image ID before claiming an identical environment.

## What this establishes—and what remains

The pipeline now supports reproducible, behavior-checked three-representation
experiments and reports honest decompiler coverage. It does not demonstrate
all-version decompilation, reliable unknown-family classification, or a general
semantic obfuscator. Python 3.14 and the modern typed-router project have no
verified reconstruction with these tools.

Next: improve hard-negative and structurally varied positive training; evaluate
on a new project-disjoint set without tuning on these ten fixtures; measure
direct bytecode-lane alignment separately; and expand decompiler coverage only
with verified runtime compatibility. Preserve this frozen baseline for comparison.

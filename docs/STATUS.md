# pycmp status

Last reviewed: 2026-10-19. The repository HEAD at review time is `13543fd`;
documentation and other working-tree changes are not necessarily committed.
This document contains dated experiment snapshots below; the current run state is
summarized first. See the [documentation map](README.md) for current entry points.

## Current delivery snapshot (2026-10-19)

The root research package uses graph schema 3. Three frozen checkpoints are
described in the [model cards](modelcards/README.md), but their weight files are
local ignored artifacts and are not included in a clone. The standalone
[`pycmp-vectorizer`](../tools/file-vectorizer/README.md) CLI/API is implemented
for local use; it currently requires Python 3.14 and an explicitly supplied
checkpoint. Full packaged Python 3.8–3.14 runtime support and a release container
are not delivered.

Measured retrieval remains experimental. Source-variant retrieval is strong on
the selected development gallery, but the trained checkpoints show no consistent
advantage over simple baselines. Direct bytecode-to-bytecode retrieval works for
known lineages in the 179-lineage development gallery, while hashed-graph and
opcode-structure baselines outperform the trained checkpoints. No current result
establishes source↔bytecode alignment, malware-family generalization, behavioral
equivalence, or production readiness.

The corpus-derived synthetic experiment and the original bytecode-to-bytecode
experiment are complete as development measurements; details and caveats are
linked below. The expanded cross-runtime/repository-bundle experiment remains
**partial** in ignored `corpus-runs/compiled-retrieval-v1/`: preparation accounted
for 159,768 compile jobs, and the ledger currently has 94,567 embeddings,
383,069 file rows, 69/441 file-evaluation cells, and 441/441 pilot file and bundle
cells. `PARTIAL.json` exists and `COMPLETE.json` does not. Resume only with the
matching command and fingerprints in [the experiment plan](COMPILED-RETRIEVAL-PLAN.md);
do not report the full evaluation as complete.

The separately maintained [vectorizer project](../tools/file-vectorizer/README.md)
is not yet a clone-and-run bundle: checkpoint weights are external, and the
seven-runtime Docker image and GKE example remain planned work. This is distinct
from the research repository's experiment workers.

## Active scope: similarity, not relation classification

The [September 11 scope decision](SIMILARITY-SCOPE.md) keeps the current objective
to shared embeddings, similarity scores and ranked retrieval. Classifying pairs
as textually, structurally, behaviorally or capability-similar is deferred. Retain
the existing diagnostic distinctions, but do not treat every behavior-changing
near-copy as unrelated code. Older classification-oriented milestones below are
research backlog, not current delivery requirements.

The active evaluation contract is the
[corpus-derived synthetic similarity experiment](SYNTHETIC-SIMILARITY-PLAN.md),
which freezes the current release and checkpoints while measuring controlled
source edits, compiled bytecode and reconstructions. Its implementation and
measured run status are summarized below.
The follow-on [bytecode-to-bytecode evaluation](BYTECODE-SIMILARITY-PLAN.md)
tests direct compiled-code lineage retrieval with the same frozen artifacts.

### Expanded compiled retrieval implementation (September 13)

The [expanded compiled retrieval runner](COMPILED-RETRIEVAL-PLAN.md) is implemented
with `prepare`, `evaluate`, `run` and fingerprint-checked `--resume`. All 79 tests
pass, including interrupted/resumed file-evaluation equivalence, conservative
ties, optimal assignment, malformed inputs and checkpoint/timeout checks.
Owned compile/decode smoke tests passed for Python 3.8–3.14 at optimization
0/1/2 without executing the sentinel's top-level side effect.

The frozen expanded manifest contains 2,270 gallery inputs, 5,519 distinct
origin/source query observations, 7,608 distinct source inputs in their union,
and 33 eligible sampled repository bundles. Preparation accounts for 159,768
source/runtime/optimization jobs. The design has 441 configuration cells for
files and bundles, with six methods and four bundle aggregators; only a subset of
the file cells has completed in the current partial run. The
experiment-specific `native-dis-v1` decoder profile is separate from the prior
production-decoder measurements; operand values remain omitted.

Execution has started in ignored `corpus-runs/compiled-retrieval-v1/`. This is
**not a completed experiment**, and no new retrieval-quality result is claimed.
A 120-second startup invocation reached its deadline, wrote `PARTIAL.json` and
removed its worker containers. A subsequent 43,200-second invocation resumed
successfully, skipping completed work. The ledger has progressed since this first
snapshot; current counts appear at the top of this document. Consult the ledger
and completion markers before resuming; the command and resume procedure are in
the linked plan. No checkpoint was retrained or promoted.

The corpus-derived pilot has now completed in the ignored
`corpus-runs/corpus-similarity-v3/` run directory. All 12 engineering expansion
gates passed: 66 tests passed; the release, checkouts, checkpoints and worker
images were verified; all six mutation families applied; accepted format/rename
controls retained selected features and tensors; the owned compile-only sentinel
did not execute; direct decoding scored at least one supported result; and worker
cleanup/resume checks passed. The frozen gallery contains 2,270 complete,
deduplicated inputs. Three balanced pilot originals produced 168 recipe records,
120 distinct outputs and 1,440 compile attempts: 1,212 compiled and 228 are
explicit version/syntax gaps. The 915 distinct binaries yielded 266 accepted
direct graphs and 649 rejected foreign placeholders. Of 1,830 decompiler
attempts, 364 were clean/parseable, 146 partial/recovery, 1,054 unsupported and
266 tool failures.

Across 120 distinct source observations, trained seed-0/1/2 Hit@1 is 99.17%,
97.50% and 98.33%, versus 97.50% untrained, 99.17% hashed graph, 95.00% token and
96.67% operation/API. Across 510 reconstruction observations, trained Hit@1 is
44.90–45.69%, versus 62.55% untrained, 65.10% hashed graph and 88.52% token on
the 366 applicable queries. All applicable graph-embedding methods have 0%
direct-bytecode Hit@1 across 266 accepted direct graphs, confirming that current
shared dimensions do not provide measured source↔bytecode alignment. These are
development findings, not a model promotion or behavioral-equivalence result.

The automatic expansion is complete in the ignored
`corpus-runs/corpus-similarity-v3-expansion/` directory. Its 181 selected inputs
produced 10,136 recipe records, 5,519 distinct sources and all 66,228 required
compile attempts: 52,728 compiled and 13,500 are explicit gaps. The 32,274
distinct binaries yielded 9,941 accepted direct graphs and 22,333 rejected
foreign placeholders. Uncompyle6 produced 6,534 clean and 4,892 partial
reconstructions; pycdc produced 3,682 clean and 3,035 partial reconstructions,
with unsupported, invalid, timeout and tool-failure outcomes retained in the
worker ledger.

The expansion report contains 33,603 observations: 5,519 source, 9,941 direct
bytecode and 18,143 reconstructed. Of the source observations, 5,291 were valid
queries; trained seed-0/1/2 Hit@1 is 97.58%, 97.22% and 97.54%, versus 96.39%
untrained, 97.54% hashed graph, 97.90% token and 95.88% operation/API. On
reconstructions, trained Hit@1 is 41.27–42.46%, versus 40.63% untrained, 43.51%
hashed graph and 85.69% token on 14,902 applicable queries. All applicable
graph-embedding methods again have 0% direct-bytecode Hit@1 across 9,941 accepted
graphs. The result confirms
strong source-variant retrieval, materially weaker reconstruction retrieval and
no measured direct source↔bytecode alignment for the frozen models. No score was
used as an expansion gate, and no model was retrained or promoted.

The follow-on direct bytecode↔bytecode evaluation is complete in the ignored
`corpus-runs/bytecode-similarity-v3/` directory. It reused the 9,941 accepted
Python 3.14 graphs without recompilation or execution. The three optimization
galleries each contain 179 unchanged-original lineages; 15,702 exact-binary-
deduplicated queries produced 47,106 rankings across all nine query/gallery
optimization cells. All pilot integrity gates passed. Overall trained seed-0/1/2
Hit@1 is 90.15%, 92.35% and 91.91%. Same-optimization Hit@1 is 93.01–94.34%;
cross-optimization Hit@1 is 88.72–91.51%. This demonstrates useful known-lineage
retrieval inside the supported bytecode lane, unlike the failed bytecode↔source
alignment test.

Training is not the strongest signal in this result. The frozen untrained encoder
reaches 90.75% overall Hit@1, hashed graphs reach 95.78%, and the transparent
opcode-structure baseline reaches 96.40% (97.73% same-optimization and 95.74%
cross-optimization). Trained seed 1 and 2 modestly exceed the untrained encoder
but all trained checkpoints trail both simple baselines. Python 3.4, 3.8 and 3.12
remain rejected placeholder gaps, and the 179-lineage gallery is easier than the
2,270-entry source gallery. These inspected splits remain development evidence,
not fresh malware-family classification or behavioral-equivalence evidence; no
model was retrained or promoted.

## Full schema-3 rebuild and baseline

The [full rebuild and measured baseline](baselines/2026-09-11-schema3-capped.md)
supersede the pilot-only status below. The fresh capped release contains 8,070
comparable units / 25,687 views from 40 contributing records / 38 repository URLs.
All seven static release gates pass. All 12,235 retained transformed-unit views
preserve encoder tensors; no split-group leaks or over-cap repositories were found.
The rebuild took 15.9 minutes and peaked at 1.37 GiB RSS. Referenced graphs occupy
1.44 GiB. Transformation exclusions are recorded in the linked audit.

Three schema-3 checkpoints were trained for one epoch, with fixed seeds 0/1/2,
64 dimensions and two layers. Paired Recall@5 is 97.01–97.23%, versus 97.14% for
the fixed untrained encoder. Behavior-match top-1 on eight development families
is 3/8, 2/8 and 2/8. These are experimental baselines, not promoted models.
Individual limitations, intended uses and measured lane results are recorded in
the [checkpoint model cards](modelcards/README.md).
No new retrieval index or unknown-family calibration was produced. The suite has
57 passing tests. The next work is hard-positive/hard-negative training and
project-level evaluation, not more repository collection. Reserved hard-pair test
families remain untouched. This execution's source/report changes are captured
in Git; generated corpus and checkpoint artifacts remain ignored by Git.

## Repaired-transform pilot: all gates pass

The [repair and final rerun](baselines/2026-09-10-transform-repair-pilot.md)
preserves lexical bindings, literal spelling, type comments and source lines for
accepted renames. Formatting must preserve the typed AST. Unsupported and
unchanged transforms are recorded without generating duplicate positives.
All 10 applied rename inputs, 45 applied formatting inputs and 284 retained
transformed-unit views preserve encoder tensors. The six-repository pilot retains
255 units / 700 views, uses 53.45 MiB of graphs, takes 7.57 seconds including
profiling and peaks at 345.88 MiB RSS. All nine gates pass; 53 tests pass.

At this pilot milestone, the next step was a fresh capped schema-3 full-corpus rebuild using
the transform-v3 pipeline, followed by integrity/coverage review before controlled
training. No new checkpoint or index was produced. Static transform checks are
not a universal behavioral-equivalence guarantee.

## Initial rebuild pilot: historical correctness blocker

The [six-repository pilot](baselines/2026-09-10-schema3-rebuild-pilot.md) completed:
255 units / 950 views, 68.54 MiB of graphs, 7.07 seconds including profiling,
and 355.22 MiB peak process RSS. Integrity and resource gates passed, but 14/49
valid inputs changed tensors after renaming. Type-comment loss and nested-scope
renaming defects were identified; an owned counterexample changes result 3 to 11.
Do not train on these older generated positives. The repair and rerun above
supersede this blocker; the old pilot remains diagnostic evidence.

## Schema-3 repair execution update

Typed literals, all available AST fields, recursive unit discovery, canonical
lexical binding candidates and external identity evidence were implemented at
this milestone. All eight development negatives change consumed tensors; 18
targeted mutations and six renaming families had regression coverage. There were
43 passing tests at that dated snapshot.
Independent three-seed architecture probes are untrained and do not justify a
default architecture change. See the [implementation and measured report](SOURCE-REPRESENTATION-V3.md).

The old schema-2 release remains historical evidence. Its graphs, model and index
are rejected by current compatibility checks. No schema-3 release model was
promoted; the rebuild and small trained baselines above now exist. Harder
training remains open. Bytecode worker images need
rebuilding for the new envelope; direct-bytecode alignment remains unvalidated.

## Steps 1–2 execution update

The new hard-pair contract contains 14 families (8 train, 3 validation, 3 reserved
test), 42 sources, explicit relatedness/behavior labels, a checksum lock and
test-scoring guards. Development/validation oracles pass their intended relations;
test families remain unexecuted and unscored. Five-baseline diagnostics on the
eight train families identify one normalization collision (literal values), two
feature-selection collisions (builtin/exception identities), and dilution of a
changed non-first function during file pooling. The suite now has 33 passing tests.

See the [measured diagnosis and repair handoff](baselines/2026-09-08-hardpair-diagnostics.md).
These steps establish evidence; they do not fix the identified model defects or
train a new checkpoint. The immediate next action is the targeted representation
repair described in that report, followed by the planned harder training run.

## Historical bottom line (2026-09-11 snapshot)

pycmp is a working research pipeline for comparing Python artifacts, with a
curated local corpus, a trained shared encoder, indexed files, and reproducible
similarity experiments. It is **not yet a validated behavioral or malware
classifier**. The next milestone is demonstrating useful learned retrieval on
hard transformations and across input lanes—not collecting more repositories.

The statements and next steps in this section were current at the September 11
snapshot, before the corpus-derived and direct-bytecode evaluations were completed.
Use the current delivery snapshot at the top of this document for today's state.

## Delivered and measured at that snapshot

| Area | Current evidence | Remaining boundary |
|---|---|---|
| Corpus | 41 manifest records / 39 repository URLs; 40 Python-contributing records / 38 URLs; Certify explicitly contributes no Python | License-file evidence, fixture adapters and label quality still need hardening |
| Capped schema-2 release | 8,066 comparable units, 29,647 views, at most 250 units per repository; inventory and graph checksums verified | Durable resume and canonical release naming remain operational work |
| Shared model | Trained 64-dimensional, two-layer encoder; one epoch over 17,088 semantic views | No demonstrated meaningful learned advantage; multi-lane training remains incomplete |
| Retrieval | 2,316 indexed source files; whole-file pooling, cosine scores, exact-match evidence and fingerprint checks | Matched-unit explanations, named-feature profiles and genuine unknown-family calibration remain open |
| Synthetic benchmark | Ten held-out projects, 60 obfuscations, ten behavior-changing near-copies; 1,624 comparisons | Small, correlated evaluation set; not a population-level accuracy estimate |
| Compiled artifacts | 111 project/runtime/optimization variants, 123 module binaries; all bytecode behavior checks and 12 optimization probes passed | Compilation success does not imply decompilation or embedding alignment |
| Decompilation | 63 of 222 attempts yielded complete, behavior-checked reconstructions | No verified Python 3.14 reconstruction in this matrix; only six successes on 3.12 |
| First-party tests | Last completed suite: 69 passing tests | Tests validate implemented behavior, not classifier accuracy |

The ten new similarity projects are separate from the earlier synthetic fixtures
and were not used to train the frozen baseline. Their 60 obfuscations mean two
levels × three seeds × ten projects; seeds change identifiers, not independent
structural recipes.

## What the measurements said at that snapshot

The [capped-corpus baseline](baselines/2026-09-07-schema2-capped.md) reported
Recall@5 of 0.8964 versus 0.8961 for hashed graphs and 0.8954 for the untrained
encoder, missing its 0.90 gate. That historical metric is paired-query hit rate,
not class-label accuracy.

The [synthetic baseline](baselines/2026-09-07-synthetic-similarity.md) is more
diagnostic:

| Query task | Trained top-1 | Hashed-graph top-1 |
|---|---:|---:|
| Light obfuscation, ten-original gallery | 30/30 | 30/30 |
| Structural obfuscation, ten-original gallery | 21/30 | 24/30 |
| Structural obfuscation, plus behavior-changing near-copy | 6/30 | 15/30 |
| Verified decompilation, ten-original gallery | 63/63 | 63/63 |
| Verified decompilation, plus behavior-changing near-copy | 60/63 | 63/63 |

Light obfuscation leaves model inputs identical, so its 100% cosine scores are
normalization invariance, not evidence of learning. Near-copies with changed
behavior can also score almost 100%. That can be useful for finding code
relatives, but cannot establish behavioral equivalence.

The successful decompilations are evaluated through source/recovery ingestion.
They **do not validate direct source↔bytecode-lane alignment**. Sharing an encoder
and vector dimension is necessary infrastructure, not evidence of comparable
meaning across lanes.

The fitted validation threshold of 0.8705617 used different-artifact proxy
negatives. It is not an unknown-family threshold or a calibrated probability.
No operational maliciousness decision should depend on it.

## Proposed next steps at that snapshot

Steps 1–2 below now have an initial implementation and measured report above.
Keep their safeguards active during the remaining representation repairs and
steps 3–5; the new small fixture set is not a complete training corpus.

1. **Freeze the next evaluation contract and create separate development pairs.**
   Preserve these ten projects and their baseline as regression evidence. Since
   their failures now inform development, reserve new untouched project families
   for the next final test. Define code-relatedness separately from behavioral
   discrimination; a changed operator can be a related file but a negative for
   behavior preservation. Add verified positive structural rewrites and controls
   for operators, branches, calls, ordering, exceptions and non-first functions.
   Keep every descendant of a source project in the same split.

2. **Diagnose representation versus learning failures.**
   Check whether each behavior-changing control changes model inputs, which units
   carry that change, and whether pooling dilutes it. Compare token, operation/API,
   hashed-graph and untrained/trained baselines with identical galleries. Repair
   demonstrated information loss before tuning the model; version preprocessing
   and rebuild affected artifacts when needed.

3. **Train and measure a harder shared encoder.**
   Use new, behavior-checked development positives and task-appropriate negatives,
   project-balanced/node-budget batches, and reproducible resumable checkpoints.
   Run at least three training seeds and report project-macro Hit@1/5, MRR,
   positive-versus-negative margins and project-level intervals. The gate is
   credible improvement over the strongest simple baseline on untouched hard
   cases—not more epochs or a lower training loss.

4. **Validate direct bytecode and feature-limited comparisons.**
   Reuse the compiled-artifact generator, but embed bytecode through the actual
   bytecode lane separately from decompiled-source ingestion. Record per-version
   decode, reconstruction and graph-coverage outcomes. Train matched source,
   bytecode and recovery views from development-only owned projects. Define a
   fixed common-core retrieval profile, named optional-feature masking before
   encoding, and compatible profile fingerprints; test feature dropout and
   missing-evidence slices. Do not mask arbitrary dimensions after embedding.
   Unsupported inputs must remain explicit, not scored placeholders.

5. **Make retrieval explainable and calibrate abstention.**
   Expose matched units/spans, query and candidate coverage, raw scores, margins,
   provenance and support limits. Evaluate classification only for explicit labels.
   Fit thresholds on validation families, then measure untouched known and novel
   families, benign lookalikes and incomplete inputs. Report false acceptance,
   precision and abstention coverage with intervals.

Steps 1–3 are the immediate model-quality milestone. Step 4 is required before
claiming lane-independent retrieval quality; step 5 is required before treating
the system as an unknown-file classifier. The detailed gates and remaining
operational work are in the [remediation plan](REMEDIATION-PLAN.md).

## Reproducibility, storage and safety

- Git contains manifests, first-party implementation, synthetic originals and
  generated source variants, oracles, tests, and measured reports.
- Local ignored artifacts include `corpus-runs/release-v0.2-capped/` (corpus,
  checkpoint and index) and `corpus-runs/similarity-v2/` (binaries, tool outputs,
  behavior checks, embeddings and full evaluation JSON). A clone alone does not
  include these artifacts or the Docker images.
- The completed corpus-derived runs in `corpus-runs/corpus-similarity-v3/` and
  `corpus-runs/corpus-similarity-v3-expansion/` are also local ignored artifacts;
  generated source, binaries, reconstructions, caches and full evaluation JSON
  retain their provenance there rather than entering Git.
- The completed direct-bytecode retrieval report and its resumable result ledger
  are local ignored artifacts under `corpus-runs/bytecode-similarity-v3/`.
- The interrupted schema-1 `corpus-runs/release-v0.1/` is historical diagnostic
  evidence and must not be reused for current model claims.
- Third-party corpus handling remains static-only. Runtime behavior checks execute
  owned synthetic fixtures in constrained containers, not third-party security
  tools or malware.
- Source↔stub comparisons describe interface evidence, not behavioral equivalence.
  Security-repository provenance is not a maliciousness label.

See the [classification strategy](CLASSIFICATION-STRATEGY.md) for the intended
decision semantics and the [fixture guide](../fixtures/similarity/README.md) for
benchmark reproduction commands.

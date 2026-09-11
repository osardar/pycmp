# Remediation plan and completion gates

Date: 2026-09-07. Evidence and finding IDs are in the [audit](AUDIT-2026-09-07.md); intended decisions are in the [classification strategy](CLASSIFICATION-STRATEGY.md).

Execution status updated: 2026-09-08. The phases below retain the original audit
scope; they are not a list of wholly unimplemented features. Use this ledger and
the [current status](STATUS.md) to distinguish delivered work from open gates.

## Execution ledger

September 10 update: the [schema-3 source repair](SOURCE-REPRESENTATION-V3.md)
implements typed literals, scalar-field preservation, recursive unit discovery,
lexical binding candidates, mutation/renaming tests, and independent untrained
architecture probes. All eight development negatives now differ at tensor input.
The earlier step-1/2 diagnosis is retained below as history. Corpus rebuild and
schema-3 training remain outstanding; schema-2 artifacts are intentionally rejected.

Steps 1–2 of the September 8 priority sequence are now implemented locally:
14 checksum-locked families with explicit 8/3/3 splits, test-scoring guards,
five baseline methods, and graph→feature→tensor→unit→file diagnostics. The
[execution report](baselines/2026-09-08-hardpair-diagnostics.md) confirms three
information-loss cases and one pooling-dilution case. Defect repairs and retraining
remain open; this closes the initial dataset-contract/diagnosis gates only.

| Area | Implemented now | Still required |
|---|---|---|
| Artifact boundary | Schema 2; graph/cache rejection; pipeline-versioned IDs; atomic graph/catalog/checkpoint/index writes | durable resume ledger and final completion marker |
| Graph | unique occurrence IDs; endpoint/unit validation; module/class/function units; spans; ordered fields; operator/API features; order-aware lexical def-use approximation | branch-sensitive scopes, CFG/exception/data flow, verified unit lineage |
| Transformations | parameters remain stable; assigned locals are renamed consistently; audit-owned behavior test | property tests for closures, comprehensions and unusual binding forms |
| Corpus | corrected paths; group-disjoint splits; hashes and item ledger; Certify disposition and fork lineage; derived 250-graph-unit-per-repository capped release | license-file evidence, richer unit-level sampling strata, remaining fixture adapters and label validation |
| Training | self-excluded multi-positive loss; no group truncation; initialization seed; schema/profile-bound atomic checkpoint | balanced/node-budget streaming, optimizer resume, multi-lane paired generation |
| Retrieval | whole-file mean aggregation; scored hits; exact-hash evidence; fingerprint rejection; abstention states; proxy-pair validation calibration and 2,316-file index | genuine unknown-family calibration, matched-unit explanations, named-feature profiles, filters, persisted ANN |
| Evaluation | full-gallery baselines; proxy calibrator; ten-project frozen synthetic benchmark with structural positives, behavior-changing controls, and hard-negative retrieval | independent development/test families, token/API baselines, unknown-family tests, macro metrics and intervals |
| Compiled similarity experiment | 111 compiled variants and 12 optimization probes verified; 63/222 decompiler attempts successful; all three source/obfuscated/decompiled pair directions scored | direct bytecode-lane alignment, broader verified runtime support, integration regression coverage |
| Release | complete expansion plus derived capped release; 8,066 units/29,647 views; graph checksums verified; bounded training/benchmark/index report published | repeated-seed hard-task model run and final release naming cleanup |

The last completed 43-test first-party suite passed in the repository environment, including a
schema-2 build→train→index→exact-search round trip. None of the
remaining quality gates should be inferred from that unit-test result.

## Objective and retained decisions

Deliver a reproducible corpus and an evaluated system for retrieving related known files, with optional labeled classification and explicit unknown rejection. Preserve all 41 selected records/39 repository identities in the release accounting. Security sources participate in training and evaluation, with separate provenance slices. Use a deterministic 250-unit cap per underlying repository after deduplication. Keep generated artifacts local under ignored `corpus-runs/`; version definitions, split assignments, tests and reports in Git.

Implementation should proceed in the order below. Each phase is a reviewable commit series with evidence for its gate. Do not call the release benchmark-ready when only infrastructure or test stubs exist. An excluded source remains in the audit ledger with a reason; unresolved licenses or no-Python records do not silently disappear.

## Phase 0 — Stop invalid artifact reuse and preserve evidence

Addresses G01–G03, C05–C06, operational gaps.

- Preserve the interrupted release and historical pilot as diagnostic artifacts. Mark their generated graphs/checkpoints unsuitable for new benchmark claims. Do not delete the directory or overwrite historical metrics.
- Remove automatic recursive replacement of external/dirty/mismatched checkouts. Validate path containment and ownership, preserve conflicts, and use new owned cache locations. Reject path traversal and symlink escapes.
- Disable broken renaming positives pending Phase 1. Add a compatibility error for old catalogs rather than silently filtering everything. Seed Python and Torch before model creation; fail on empty/no-pair training before writing a checkpoint.
- Add an audit index and distinguish committed functionality from the current unfinished curation work. Lock the supported developer runtime and test dependencies; add CI for first-party tests only.

Gate: mismatched/dirty/out-of-root checkout tests preserve user files; legacy corpus errors are actionable; empty training creates no checkpoint. Audit regressions reproduce the confirmed failures before their corresponding fixes.

## Phase 1 — Repair graphs and transformation truth

Addresses G01–G04, G05 unit boundaries.

- Allocate occurrence IDs from an independent monotonic counter; enforce uniqueness, valid endpoints, valid unit kinds, schema version, actual feature availability and finite tensors at serialization/load boundaries. Never silently drop invalid edges.
- Store source spans and ordered child positions, preserve operator/API/constant categories and distinguish modules/classes/functions. Retain executable module code even when functions exist. Define nested units by qualified lexical identity and keep containment references without uncontrolled subtree duplication.
- Replace final-definition hash lookup with scope-aware bindings. Model parameters, captures, globals/nonlocals and order; mark unresolved/data-flow approximations explicitly. Add CFG/exception edges incrementally with tested semantics.
- Implement a scope-aware renamer only for transformations whose binding behavior can be verified. Rename declarations and uses consistently; handle captures/keyword interfaces or exclude unsafe cases. Execute only audit-owned synthetic fixtures when validating behavioral preservation.
- Assign source-unit and pair identities before transformations. Match variants by explicit lineage/qualified units, not traversal index. Keep damaged/invalid examples out of semantic clone positives; Black input/output pairing requires an explicit relation and verified validity/equivalence.
- Bump the graph/preprocessing version and require artifact rebuilds.

Gate: no duplicate IDs/dangling edges; graph round trips preserve facts; operator/API/order negatives are distinguishable in encoded inputs; module/second-function changes remain observable; synthetic transformation tests preserve bindings and behavior.

## Phase 2 — Finish curation and trustworthy labels

Addresses C01–C04, C06.

- Freeze a canonical release definition referencing the selected manifests and computed explicit split assignments. Normalize repository identity across aliases; group related forks such as NetExec/CrackMapExec for leakage control. Preserve role selections without doubling repository caps.
- Use one path-matching contract supporting zero-directory `**`. Audit paths against each pinned Git tree. Keep sparse fetching an optimization that cannot change selection semantics. Correct the Hypothesis paths and restore standalone Python/stub selections alongside container extractors.
- Validate full commit IDs and fetch them explicitly. Record commit/tree IDs, license file evidence, selection revision and environment identity. Do not equate static-only handling with verified licensing. Unresolved records receive an explicit blocked/excluded disposition; Certify receives `no_python_inputs`.
- Extend fixture adapters using pinned upstream examples: MyPy multi-file cases, stubs, `[out]` and annotations; Markdown headings/settings/rule labels; Black flags/input/output; CPython argument-aware literal extraction including expressions and assigned constants; LibCST literal fixtures. Preserve emitted source exactly and document unsupported dynamic constructions. No `eval` of fixture expressions.
- Introduce a typed sample record: repository/commit/path/span, container and emitted source kind, fixture/unit/lineage IDs, raw and structural digests, label value/source/confidence, observed parser outcome/runtime, expected outcome and version constraints. Missing labels are `unknown`, never inferred accepted from absence. Extractor family is provenance, not diagnostic ground truth.
- Maintain raw-byte and structural fingerprints separately. Preserve whitespace for invalid-source hashes. Deduplicate at module/function level and group related duplicates before sampling/splitting; preserve all provenance owners and intentional pair relations. Check transformed artifacts too.
- Define a retained unit as a comparable function or module-level executable unit; keep fixture context as metadata. Apply the 250-unit cap per canonical repository, using stable hash ordering with role/label/size strata. Log oversized units and explicit resource exclusions. Preserve both members of supported evaluation pairs.
- Allocate train/validation/test with deterministic constrained 70/15/15 group counts, including holdouts for fixture, production and security groups where feasible. Commit the assignments. Validate counts on retained units and provide explicit infeasibility errors instead of an all-training stratum.
- Write a per-item ledger for candidate, retained, duplicate, capped, unsupported and excluded records, including zero-contribution sources. Stream progress and use atomic writes, checksums, stage manifests and a final completion marker. Cache keys include source, extractor, transformer, normalizer, schema and runtime versions.

Gate: every selected record has evidence-backed counts/disposition; each retained repository has at most 250 units; no leakage across source lineage or duplicates; multiple contributing validation/test groups cover the intended strata; diagnostic-bearing fixtures have golden expected labels. Interrupted runs and clean reruns yield the same release digests.

## Phase 3 — Make representation and learning useful across inputs

Addresses G02, G05, T01.

- Encode actual named feature values for operations, constants, APIs and control/data-flow relations. Use a fixed common-core projection and optional supplemental reranker with named masks, observed/unknown states and profile fingerprints. Measure feature dropout rather than assuming availability counts align lanes.
- Define a tested Python version support matrix. Decode foreign bytecode with version-aware xdis instructions, real branch/exception relationships and separate code-object units. Unsupported decoding is explicit; placeholder graphs cannot enter scored indexes. Align intact recovery constructs to common semantic kinds and retain error/coverage evidence.
- Produce paired source/compiled/recovered views from audited synthetic sources in pinned worker images, never execute external corpus programs. Add labeled stubs only for API/interface tasks with known correspondence; do not call them behavioral clones.
- Implement multi-positive contrastive learning with self exclusion and no false-negative treatment of known positives. The [supervised contrastive reference](https://arxiv.org/abs/2004.11362) provides a suitable formulation. Ensure group batches cover eligible examples without truncation; use balanced project sampling and node-budget batches.
- Save complete architecture/preprocessing/training configuration, random state, optimizer state, corpus identity and checkpoint hashes. Unify loaders across embed/train/evaluate/index/search. Bound memory with streamed/batched encoding and chunked ranking.

Gate: loss math matches hand-checked examples; every eligible group is sampled; seeded reruns are reproducible within documented tolerances; checkpoint round trips work through every CLI path; source↔bytecode/recovery tasks have trustworthy pair/coverage records for every claimed version.

## Phase 4 — Evaluate retrieval and introduce calibrated decisions

Addresses T02, R01–R02.

- Freeze task datasets and known reference galleries. Include hard negatives and novel families; keep gallery composition identical across baseline comparisons. Avoid classification labels based solely on repository or tier.
- Implement raw hash, normalized AST, token and operation/API-feature baselines plus untrained/trained GNN comparisons. Report learned improvements separately from AST-identical variants. Use at least three fixed seeds and project-level bootstrap intervals.
- Query all file units and module activity. Aggregate evidence with deterministic coverage-aware file scoring; discount boilerplate and expose matched spans. Defer learned attention pooling until independently trained and shown useful.
- Return scored candidates, coverage, supported labels, optional calibrated confidence, and explicit matched/unknown/insufficient-evidence/unsupported status. Fit similarity-weighted nearest-neighbor classification and rejection thresholds on validation data only.
- Publish Hit@1/5/10, Recall@k, MRR and project-macro results. Compute tier/lane/diagnostic query slices against the same full gallery. Add genuine label-family precision/recall/F1 and novel-family false acceptance; do not rename pair recall as classification accuracy.
- Enforce checkpoint/schema/feature-profile/corpus identities in index headers. Reject mixed model versions; validate vectors/limits and preserve metadata. Expose filters in CLI, persist exact indexes, and use atomic replacement so rebuilt indexes do not retain obsolete entries. Keep Vertex deployment out of this release; label exports/adapters accurately.

Gate: changing a non-first query function can change results; known matches include inspectable evidence; unrelated families can be rejected; global-gallery slices are consistent. Proposed research targets are at least 95% precision among non-abstained decisions and at most 5% unknown-family false acceptance, with intervals/coverage reported. Require statistically supported benefit over simple baselines before preferring the GNN. Failure or insufficient data produces a failed/inconclusive report, never a fabricated pass.

## Phase 5 — Publish the local release and close documentation

- Build corrected artifacts in a new ignored release directory. Complete the inventory, hashes, lock, explicit assignments, statistics, task manifests, checkpoint and index. Validate all references and completion gates before writing the completion marker.
- Harden worker input/output/time/resource boundaries; mount only staged inputs and guarantee container cleanup on timeout. Test Docker success, malformed input, unsupported versions and timeout paths in an explicit integration suite. Keep third-party source unexecuted.
- Commit canonical metadata, licenses/dispositions, reports, environment lock, regression tests and first-party implementation in reviewable commits. Preserve raw corpus/model output locally as agreed. Do not commit third-party source bundles by default.
- Update README/STATUS/CORPUS and annotate the historical pilot with superseding results. Label the legacy per-file GCN scripts as demonstrations, the vocabulary as grammar-version-specific, and unsupported cloud/bytecode/classification claims accurately.

Gate: a clean, documented local workflow reproduces release counts and passes integrity checks; benchmark evidence states supported tasks and limits. If a model fails the quality gate, ship the curated corpus and report the model failure separately. Corpus readiness and classification effectiveness are distinct completion criteria.

## Prioritization and implementation boundaries

The initial graph repairs, capped-corpus build, bounded training, indexing and
synthetic hard-negative experiment have been executed. The remaining priority is
now **demonstrating useful learned retrieval**, not repeating those milestones.

1. Freeze task semantics and new project-disjoint development/validation/test
   families. Preserve the existing ten-project experiment as regression evidence;
   do not train on it and still call it untouched. Separate related-code retrieval
   from behavior-preservation ranking when labeling near-copy negatives.
2. Diagnose input-feature collisions and pooling dilution on the observed failures.
   Add token and operation/API baselines and verified structural development pairs.
   Gate: relevant changes are observable, or missing evidence is explicitly marked.
3. Train with task-appropriate hard negatives, balanced/node-budget batches and
   complete resumable state. Compare at least three seeds on identical galleries,
   with project-macro metrics, margins and project-level confidence intervals.
   Gate: credible benefit over the strongest simple baseline on new held-out cases.
4. Evaluate actual source↔bytecode/recovery alignment by runtime and evidence
   coverage, using a common-core profile plus named optional-feature masks applied
   before encoding. Decompile-to-source successes do not satisfy this gate.
5. Add inspectable retrieval evidence and genuine novel-family calibration, then
   report the Phase 4 precision/false-acceptance/coverage gates honestly.

The current hard-negative structural top-1 is 6/30 for the trained model versus
15/30 for hashed graphs. This small, correlated test diagnoses a problem; it is
not a statistically powered target to optimize in place. See the
[synthetic report](baselines/2026-09-07-synthetic-similarity.md).

Continue license/label evidence, CI, worker timeout/failure regression tests,
environment locking and release-resume work as supporting reliability tasks.
Do not spend the next milestone primarily adding repositories or increasing epochs.

The audit itself made no automatic remediation; the execution ledger above now
records the subsequent implementation. Actual duration depends on upstream
fixture diversity and bytecode version support; use the explicit gates above
rather than an unsupported calendar estimate.

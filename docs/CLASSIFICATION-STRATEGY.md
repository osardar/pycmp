# Classifying unknown files against known files

## Implementation boundary

The schema-2 code now implements the first usable inference skeleton: all units
of a file are mean-pooled and normalized, the local index returns cosine scores
and enforces the checkpoint/preprocessing fingerprint, exact-byte matches are
identified, and inference returns `matched`, `unknown`, or
`insufficient_evidence`. The current `0.80` threshold is an uncalibrated default,
not a validated operating point. Class votes, capability labels, matched-unit
coverage, genuine unknown-family calibration/evaluation, and an `unsupported`
decoder result still need implementation before this is a full classifier. A
validation-only calibrator now exists for known positive pairs versus different-
artifact proxy negatives and labels that limitation in its output.

The first capped-corpus measurement does not yet justify the learned encoder:
trained Recall@5 was 0.8964, hashed graph cosine was 0.8961, and a matching-shape
untrained encoder was 0.8954. The trained model failed its 0.90 gate. Exact and
structural matching plus fixed graph features should remain first-class stages;
the GNN must prove incremental value on hard transformations, recovery, and
bytecode before it controls an unknown-file decision.

Assessment date: 2026-09-07. Read with the [project audit](AUDIT-2026-09-07.md) and [remediation plan](REMEDIATION-PLAN.md).

## What the system should decide

The useful product is evidence-backed retrieval followed by an optional, calibrated classification decision. An unknown input may be a known file, a modified relative, a file with a shared capability, or unrelated to every known class. These require different labels and tests.

| Question | Evidence needed | Current readiness |
|---|---|---|
| Is this an exact known file? | Byte digest match | Implemented and smoke-tested |
| Is this a renamed/reformatted relative? | Valid structural/token matches and verified transformations | Structural baseline implemented; broader transformation truth still needed |
| Does it share a capability or code family? | Labeled units, API/data/control flow and hard negatives | Not validated |
| Can source match compiled/reconstructed code? | Consistent unit boundaries and paired cross-lane training | Not validated |
| Is it malicious? | Contextual labels, benign lookalikes, calibrated operating point | Cannot be inferred from current corpus membership |
| Is it outside the known corpus? | Novel-family holdout and an abstention policy | Missing |

Security repositories are valuable sources of protocol handling, serialization, authentication, enumeration and other real implementation patterns. They do not provide an automatic maliciousness label for every function. The same parser, network client, or administrative operation can be legitimate or used during an attack. Retain the security tier as provenance and an evaluation slice, not a class target by itself.

## Keep the architecture, repair the information it learns from

One shared encoder is a reasonable hypothesis for learning structural relationships, but using the same vector dimension across lanes proves only numerical compatibility. Meaningful alignment requires common operations, tested correspondence, cross-lane positives, informative negatives and compatible checkpoint/preprocessing versions.

Use a common representation for operators, constants/categories, bindings, calls, ordered statements, control transfers and available data-flow facts. Retain file, class and function boundaries. AST should remain the primary parser for supported complete source. Tree-sitter should recover intact regions and preserve errors/confidence. LibCST can help when lossless formatting or transformations require it; adding it alone will not repair a model that ignores features. Bytecode needs real version-aware instruction and flow normalization.

API/type/name details are supplemental evidence. Retain resolvable import-qualified calls and operator identity; do not make arbitrary local spelling the only route to identity. Keep unresolved calls explicitly unresolved. Static data-flow information can support code representations; [GraphCodeBERT](https://arxiv.org/abs/2009.08366) motivates testing it, but its results do not validate this GNN or corpus.

Model availability with named feature masks, not counts. Distinguish absent, unknown and observed-empty. For efficient global retrieval, publish a fixed common-core index plus optional supplemental-feature reranking. Arbitrarily masking a fixed embedding after generation does not remove a specific source feature. A feature profile must change preprocessing/encoding and be fingerprinted with the index. Use feature dropout during training and evaluate each supported profile. Partial inputs should report observed coverage rather than being forced to match complete programs with high confidence.

## Retrieval and classification design

1. Identify input format and supported parser/runtime. Unsupported versions yield an explicit unsupported/insufficient-evidence result. Do not embed foreign bytecode placeholders as if they conveyed behavior.
2. Compute raw hashes and extract module, class, function and relationships. Preserve top-level activity and all query units.
3. Generate unit embeddings using a validated checkpoint and common feature profile. Retrieve candidates from an index with matching preprocessing/model fingerprints.
4. Aggregate unit evidence by known file/project. Weight informative matches, discount boilerplate, and report how much of the query and candidate is covered. Retain unit-level scores and spans so users can inspect the reason for a match.
5. Rerank candidates using token/structural, API and flow evidence where supported. Compare the same candidate gallery for all approaches.
6. Apply a classification rule only for classes with adequate labeled references. Use similarity-weighted nearest neighbors as the initial classifier, calibrate its score and margin on validation projects, and abstain below calibrated support thresholds.

Return `status` (`matched`, `unknown`, `insufficient_evidence`, or `unsupported`), query coverage, ranked candidate files with scores and matching spans, optional supported labels, and model/corpus/profile identities. A nearest-neighbor score is not a probability. The API must make that distinction explicit.

Use a coverage-aware deterministic pooling baseline before training attention pooling. A single high-scoring helper must not dominate file classification; match coverage and repeated boilerplate should be visible. Later learned pooling must be trained and evaluated, not randomly initialized at inference.

## Evaluation that answers the product question

Freeze repositories and related fork families into train/validation/test groups. Hold out whole unseen families for novelty tests. Keep all transformations, versions, fixtures and bytecode descendants of a source unit in the same group. Scan duplicates at function and file granularity before assigning labels and scoring. Explicit source↔bytecode pairs are evaluation relations, not an excuse to put one view in training and its counterpart in test.

Required baselines: raw hashes, normalized AST hashes, token similarity, bag-of-operation/API features, an untrained GNN, and the trained shared GNN. Add a code-pretrained model only after environment/compute/license feasibility is established. This determines whether the GNN offers value beyond easy structural lookup.

The benchmark must include:

- Exact/reformatted/verified-renamed pairs; AST-identical views reported separately.
- Behavior-changing hard negatives: operator changes, swapped argument/statement order, different calls, changed branch and exception behavior.
- Labeled capability/family examples with benign lookalikes and unrelated negatives. Do not assume every different artifact is a negative or every same-repository function shares behavior.
- Whole-file cases where only the second function or top-level code changes.
- Matched source/bytecode versions and partial-recovery cases with coverage labels.
- Novel-family and unsupported-input cases requiring abstention.

Report hit rate and true recall distinctly: the current “paired recall” counts whether any positive appears, so it is a hit-rate measure. Report Hit@1/5/10, Recall@k when multiple positives exist, MRR, macro metrics by project/family, and global-gallery slices by lane/tier/coverage. Classification needs per-class precision/recall/F1, confusion matrices, abstention coverage, calibration and false-positive rates on unknown/benign inputs. Give bootstrap intervals grouped by project and compare at least three fixed seeds.

Use validation data for thresholds and model selection; test once after freezing choices. As a proposed research milestone, target precision of at least 95% among non-abstained decisions and unknown-family false acceptance at most 5%, reporting confidence intervals and abstention coverage. These are acceptance targets for triage research, not current performance or sufficient assurance for automated security enforcement. If sample sizes cannot support them, report insufficient evidence rather than success.

## Expected effectiveness

Exact and near-copy detection are achievable first and may be solved adequately by simpler methods. A repaired shared GNN could add value for structural changes and partial reconstruction, but should earn that role through comparisons. General behavioral equivalence cannot be established by similarity alone. Cross-version bytecode, sparse stubs and heavy reconstruction are harder and need explicit quality limits.

The immediate investment should be graph correctness, trustworthy pairs and a hard-negative benchmark. Expanding repository count or increasing epochs before those repairs would produce more numbers without answering whether unknown-file decisions improve.

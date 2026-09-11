# Hard-pair development and reserved-test contract

Compatibility update: the source pipeline is now schema 3. The historical frozen
checkpoint command below requires matching schema-2 code. To measure the current
representation without a trained checkpoint, use `codegraph source-audit --output`
via `.venv/bin/python -m codegraph.cli`; see the
[schema-3 report](../../docs/SOURCE-REPRESENTATION-V3.md). The fixture lock and
reserved-test policy are unchanged.

Version: `hardpairs-v1`, frozen 2026-09-08. This is a separate first-party set
from `fixtures/similarity/`, whose observed failures motivated development.
There is no model training in this milestone.

## Splits and relations

The manifest explicitly assigns eight families to train/development, three to
validation, and three to reserved test. The seed is a provenance identifier;
splits are explicit, task-selected assignments, not randomized 70/15/15 sampling.
Every original, positive rewrite, negative mutation and oracle remains with its
family. There are 14 families, 42 source files and 42 oracle cases shared across
each family's three variants. `lock.json` pins the manifest, sources and oracles.

| Split | Families | Purpose |
|---|---|---|
| Train | checkout_charge, cutoff_gate, extremum, staged_math, safe_divide, helper_change, literal_limit, parameter_roles | Representation diagnosis and future development training |
| Validation | slug_text, positive_partition, reverse_segment | Future model selection; behavior checks only in this milestone |
| Reserved test | run_lengths, weighted_checksum, balanced_marks | No execution, embedding, scoring or model selection in this milestone |

Each family contains an original, a structural positive, and a behavior-changing
near-copy. Relation labels deliberately distinguish two questions:

- **Related code:** both positive and negative variants are related to the original.
- **Behavior preservation:** positive rewrites are intended to preserve behavior
  on the declared domain; negative mutations must fail at least one oracle case.

The manifest labels are authored intended relations, not proofs of equivalence.
Execution verifies finite examples for development/validation only. Reserved-test
labels remain unverified until the final evaluation. Test sources are visible
in Git: this is an unscored holdout, not a cryptographically blinded benchmark.
Static parsing and hash checks of test sources are allowed for integrity and
cross-family exact/AST duplicate detection. Do not inspect test embeddings or
outcomes while choosing changes. The diagnostic CLI rejects `--split test`.

Domains are JSON-compatible inputs illustrated by the oracles: integer operands
and lists for arithmetic, division, filtering, checksum and extrema; strings for
slug formatting; JSON lists for reversal; strings/lists of strings for run lengths;
and strings containing only `(` and `)` for balanced marks. No claim covers custom
objects, overloaded operators, side effects, arbitrary Unicode equivalences or
behavior outside these domains. Exactly matching raw/AST hashes are rejected
across new families; this is not a semantic-duplicate proof or exhaustive corpus
leakage audit.

## Fixed development measurement

Use the existing frozen 64-dimensional, two-layer checkpoint. No training,
threshold tuning, schema changes, or index replacement occurs here.

```bash
.venv/bin/python -m codegraph.cli hardpair-diagnose \
  --checkpoint corpus-runs/release-v0.2-capped/model-d64-l2-e1.pt \
  --split train --output corpus-runs/hardpairs-diagnosis-new
.venv/bin/python -m unittest discover -s tests -v
```

Only authored first-party development/validation fixtures are executed by the
oracle helper. It executes locally without a sandbox and must not be used with
untrusted replacements. Third-party corpus code is never executed. Checksums
detect accidental changes, not malicious modification of both files and lock.

For each structural-positive query, all originals **within the selected split**
form the gallery, plus that family's negative. Thus train has nine candidates.
Use that exact gallery for all five methods. All other families are different
authored tasks, not inferred malware/capability negatives. Count ties within
1e-7 against the expected original. For related-code ranking, the same-family
negative is also a correct reference; for behavior ranking, it is not.

Baselines: the frozen trained encoder, seed-0 architecture-matched untrained
encoder, repository hashed-graph features, lexical-token counts (comments and
formatting removed, spelling retained), and operation/API counts (operators,
call targets, literal values and selected control kinds). The last two use exact
sparse counters and cosine, not learned vectors or hash buckets. Bag baselines
do not encode full order or bindings. Every method includes the whole file.
GNN/hashed file vectors are normalized means of normalized unit vectors.

Compare original↔positive, original↔negative, and positive↔negative scores.
Report both ranking tasks and the positive-versus-negative cosine margin.
These tiny development results are diagnostic, not final accuracy claims.

## Failure attribution contract

For original↔negative, align units by qualified name, including module activity
and non-first functions. Preserve unmatched units explicitly.

1. Compare graph facts without source coordinates: identical facts with changed
   behavior indicate missing normalization evidence.
2. Compare actual selected, unbucketed encoder features and edges: graph differences
   absent here indicate feature-selection loss.
3. Compare consumed tensors: differences lost only here indicate hash collisions.
4. Observe the real encoder using hooks. Record per-layer node-state, pre-projection
   node-mean, and final unit-vector L2 differences; flag invariance at unit L2 <= 1e-6.
5. Compare file L2 against the largest changed-unit L2. Flag dilution below half
   that maximum. This threshold is a declared heuristic, not a learned threshold
   or a proof that pooling alone caused a retrieval failure. Layer distances use
   aligned node order and are omitted when shapes differ.

The report retains hashes, behavior checks, stage distances and all candidates.
Every completed output directory is retained; the CLI refuses to overwrite it.

## Gates and next handoff

Step 1 completes when splits/relations/hashes are fixed, original/positive checks
pass for development/validation, each development negative has a counterexample,
and the test-scoring guard is tested. Step 2 completes when every development
negative has attributable graph/feature/tensor/unit/file evidence and all baselines
use identical galleries. Neither gate requires that the current encoder succeeds.

Before step 3, repair demonstrated missing literals and external-call/exception
identity with bounded, named features while preserving local-rename invariance.
Consider pooling changes only against coverage/second-function tests. Any feature
change must version preprocessing and invalidate/rebuild affected artifacts.
Add broader independent development families before training; do not train on the
three reserved test families or claim three test families give reliable intervals.

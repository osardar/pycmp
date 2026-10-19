# Decision: similarity retrieval now, relation classification later

Date: 2026-09-11. Status: active scope decision.

Current status (2026-10-19): this scope remains active. Source variants and direct
bytecode-to-bytecode lineage have been measured on development galleries; the
trained checkpoints do not lead the strongest simple baselines in compiled
retrieval, and source↔bytecode alignment remains unproven. The expanded
cross-runtime/bundle run is partial. See [STATUS.md](STATUS.md) for exact metrics
and run progress, and [the vectorizer guide](../tools/file-vectorizer/README.md)
for what is currently usable as a CLI.

The active evaluation implementation is specified in the
[corpus-derived synthetic similarity plan](SYNTHETIC-SIMILARITY-PLAN.md).
The follow-on [expanded compiled retrieval plan](COMPILED-RETRIEVAL-PLAN.md)
tests cross-runtime file ranking and sampled repository-bundle matching without
retraining or promoting the frozen checkpoints.

## Current objective

Focus pycmp on producing comparable embeddings, ranking similar Python artifacts,
and exposing raw similarity scores. Do not currently classify why two artifacts
are similar. This decision supersedes classification-oriented next steps in older
strategy and remediation documents; it does not rewrite historical experiments.

Keep one shared encoder and compatible embedding space across input lanes. Query
and corpus embeddings must use the same checkpoint and preprocessing/profile.
Treat cross-lane alignment as an unvalidated hypothesis: shared dimensions alone
do not establish source/bytecode/reconstruction comparability, and current
measurements have not demonstrated source↔bytecode retrieval.

Current work should improve retrieval under meaningful code transformations,
literal/operator sensitivity, unit-to-file aggregation, and partial-input coverage.
Compare learned retrieval with token/API, hashed-graph and untrained baselines,
using project-separated evaluation and reserved final tests. Reporting matched
units, exact hashes or missing evidence can support inspection without assigning
a similarity-type class.

A cosine score is a ranking signal, not a probability, percentage of identical
code, proof of equivalent behavior, capability label or maliciousness judgment.
Existing threshold/status and exact/structural-match code is retained; this is a
documentation/scope change, not removal or redesign of inference behavior. Those
mechanisms do not demonstrate a validated relation classifier.

## How to interpret the current evidence

The [latest three-seed baseline](baselines/2026-09-11-schema3-capped.md) achieves
97.01–97.23% paired Hit@5, versus 97.14% for the fixed untrained encoder. Accepted
rename/format positives are tensor-identical; these results do not establish a
consistent learned advantage on harder similarity retrieval.

Hard development related-code top-1 is 4/8 for all three trained seeds. Behavior
top-1 is 2–3/8. Preserve both as diagnostics, not a new requirement to classify
similarity types. A behavior-changing near-copy may still be a valid related-code
match: do not automatically turn every behavior mutation into an unrelated-code
training negative. Keep task assumptions explicit in pair construction and metrics.
The eight development families are not a general accuracy estimate.

## Deferred research topic

Retain these overlapping notions for future investigation:

- Textual identity or near-textual similarity.
- Structural relatedness, including renamed or modified relatives.
- Behavioral similarity under a specified input/output contract.
- Shared capability despite different implementations.

The current single embedding/cosine score does not reliably distinguish these
relations. Do not now add relation-specific classifier heads, capability labels,
behavior-equivalence decisions, or a similarity-type API taxonomy. No separate
lane-specific embedding systems are proposed.

If relation classification is explicitly reopened, first test frozen-encoder
pairwise predictors on independently labeled, project-disjoint data. Determine
whether the embedding retains enough information before adding task-specific
training. Multiple relations could apply to one pair; missing evidence must allow
an uncertain result. Revisit this after meaningful similarity-retrieval gains or
a concrete user need for relation labels, not merely a higher easy-pair score.

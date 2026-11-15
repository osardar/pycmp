# Documentation map

This page separates current operating guidance from dated evidence. Generated
corpora, experiment ledgers, and checkpoint weights generally live in ignored
local directories; a Git checkout contains code, plans, model cards, and reports,
not necessarily the artifacts needed to rerun a measurement or produce vectors.

## Start here

- [Architecture, strengths, limitations and complete experiment review](PROJECT-REVIEW.md)
- [Project overview and quick start](../README.md)
- [Current status and run progress](STATUS.md)
- [Active scope and interpretation](SIMILARITY-SCOPE.md)
- [Standalone file-to-vector CLI/API](../tools/file-vectorizer/README.md)
- [Corpus data, splits, and provenance](CORPUS.md)
- [Source graph schema 3](SOURCE-REPRESENTATION-V3.md)
- [Frozen checkpoint cards and availability](modelcards/README.md)

## Current and recent experiments

- [Corpus-derived source/compiled/reconstruction similarity](SYNTHETIC-SIMILARITY-PLAN.md)
- [Direct bytecode-to-bytecode evaluation](BYTECODE-SIMILARITY-PLAN.md)
- [Expanded runtime and repository-bundle evaluation](COMPILED-RETRIEVAL-PLAN.md)
- [Vectorizer design and implementation decisions](FILE-TO-VECTOR-PLAN.md)
- [Measured schema-3 baseline](baselines/2026-09-11-schema3-capped.md)

The expanded compiled-retrieval run remains partial as of 2026-11-15. See `STATUS.md` and the run's
ignored `corpus-runs/compiled-retrieval-v1/PARTIAL.json` for the latest ledger
state; do not cite pilot coverage as a completed full evaluation.

## Historical audit and research context

- [September 2026 project audit](AUDIT-2026-09-07.md)
- [Remediation ledger](REMEDIATION-PLAN.md)
- [Deferred classification research](CLASSIFICATION-STRATEGY.md)
- [Historical schema-2 and schema-3 baseline reports](baselines/)
- [Reserved hard-pair fixtures](../fixtures/hardpairs/README.md)
- [Frozen schema-2 similarity fixtures](../fixtures/similarity/README.md)

Dated reports preserve the conditions and conclusions of their original runs.
When an older report says a feature, model, or gate is not yet available, read
that statement as of the report date and follow the links above for current
status. Historical scores are not interchangeable across schemas, decoder
profiles, galleries, or evaluation splits.

## Artifact availability

The three schema-3 checkpoint cards contain hashes and evaluation details, but
the `.pt` weight files are not tracked. The standalone vectorizer requires a
separately obtained compatible checkpoint. Generated corpora, indexes, caches,
and experiment outputs are also ignored; plans and reports do not imply those
artifacts can be reconstructed without the pinned local inputs and workers.

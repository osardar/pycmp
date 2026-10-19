# Corpus guide

## Current schema-3 release — 2026-09-11

The [full rebuilt release](baselines/2026-09-11-schema3-capped.md) is available at
`corpus-runs/release-v0.3-capped`: 8,070 comparable units, 25,687 views, 7,850 graph
files and 1.44 GiB of serialized graphs. It covers 40 Python-contributing records
across 38 repository URLs; Certify remains explicitly noncontributing. All release
checksums, split-group and cap checks pass, and all 12,235 generated transformed
unit views preserve encoder tensors. Conservative transform exclusions are logged.
Three small schema-3 checkpoints now exist, without a consistent learned advantage.
Older counts below are historical, not the current compatible release.

## Schema-2 curation update — 2026-09-07

The previous `release-v0.1` directory is preserved as an incomplete, invalidated
schema-1 artifact. The corrected dry run for v0.2 covers 41 manifest records and
39 repository URLs, retains 4,302 selected source/fixture inputs from 40
Python-contributing records, and records Certify as a documented zero-Python
source. These counts precede graph-unit expansion and are provisional until the
clean release completes. They must not be presented as trained examples or a
classification benchmark.

The builder now uses zero-or-more-directory globstar semantics, separate exact
and structural hashes, one role-balanced 250-input cap per canonical repository URL, broad
production/fixture/security holdouts, and lineage grouping for NetExec and
CrackMapExec, and an item-level inclusion/exclusion ledger. The remaining corpus
gate is applying the cap to true module/function graph units rather than source
containers, plus committing the resulting release evidence.

That gate has now been executed in the derived
`corpus-runs/release-v0.2-capped`: 8,066 graph units, 29,647 views, 38
contributing repository identities, maximum 250 units per repository, and zero
inventory/graph checksum errors. The original 231,686-view expansion is retained
as immutable evidence of the source-container cap failure and must not be used
for training. Future direct builds apply the graph-unit cap before publishing
their catalog and remove unreferenced generated graph files.

Audit note (2026-09-07): release curation remains unfinished. The audit's P0
graph, selection, and split defects are repaired in schema 2, while label depth,
unit-level capping, and benchmark gates remain open. Treat the workflow below as
experimental. See the [audit](AUDIT-2026-09-07.md) and
[remediation gates](REMEDIATION-PLAN.md) before publishing a benchmark.

## Goal

The research design uses one shared graph encoder across input lanes, rather than
separate lane-specific encoders. This is an architectural choice, not evidence
that the output spaces are aligned for every lane pair. In particular, measured
source↔bytecode retrieval has not demonstrated alignment. Always retain lane and
profile provenance and consult the relevant experiment before comparing vectors.

## Inputs and lanes

| Input | Lane | Notes |
|---|---|---|
| Valid `.py` source | `ast` | Semantic graph derived from the standard AST. |
| Malformed or reconstructed `.py` | `recovery` | Tree-sitter-backed partial graph; marked recovered. |
| `.pyc` | `bytecode` | Processed in the isolated Docker worker by default. |
| `.pyi` | `ast` plus `source_kind=.pyi` | Stub graph with type/API emphasis, not executable behavior. |

Every view carries provenance and lane metadata. Consumers must use these labels
when evaluating comparisons rather than assuming every lane exposes the same
features.

## Manifest requirements

Each JSONL record uses an immutable revision and declares its intended role.

```json
{
  "name": "example_fixtures",
  "url": "https://github.com/example/project.git",
  "revision": "40-character-commit-hash",
  "license": "MIT",
  "corpus_role": "fixture",
  "research_tier": "analysis_fixtures",
  "execution_policy": "static_only",
  "source_extensions": [".py", ".pyi"],
  "include": ["tests/fixtures/**/*.py", "tests/fixtures/**/*.pyi"],
  "split_group": "example"
}
```

`split_group` is required whenever multiple records refer to different portions
of the same repository. It prevents project leakage between train, validation,
and test partitions. Valid roles are `production`, `fixture`,
`educational_pair`, `reference`, and `general`.

## Build behavior

```bash
python -m codegraph.cli corpus build corpus/lint-training-target.jsonl \
  --output corpus-runs/lint-target
```

The builder clones the pinned source, checks out the supplied revision, reads
only declared source extensions, and never invokes the repository’s build or
test machinery. For each file it writes these views where possible:

- `source`
- `formatted`
- `renamed`
- `damaged`
- `untransformed` when modern AST transformations cannot parse legacy syntax

The output includes `views.jsonl`, per-view graph files, and a
`manifest.lock.json` snapshot.

For the complete CPU-first release, use `codegraph.cli corpus release` with the
core, extended-analysis, and defensive-security manifests. It assigns stable,
stratified project partitions; removes exact cross-project duplicates; excludes
generated/vendor paths; and caps each record at 250 source units. The generated
`curation-report.json` records all retained and excluded input decisions.

## Curation rules

- Keep production code, fixtures, educational pairs, and recovery-only inputs
  distinguishable through labels.
- Do not train a semantic equivalence objective directly on invalid syntax;
  retain it for parser/recovery evaluation.
- Remove vendored/generated duplicates and balance project contribution counts.
- Use immutable revisions and record source license information before a corpus
  release.
- Do not execute third-party source; the corpus workflow is static-only.

## Current limitations

The builder extracts standalone `.py` and explicitly declared `.pyi` files.
It also supports labeled extractors for MyPy case files, Python Markdown code
blocks, Black input/output pairs, and CPython parser-test strings. Snapshot and
other custom fixture formats still need dedicated extractors so their contents
receive the correct expected-outcome and provenance labels.

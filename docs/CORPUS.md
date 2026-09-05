# Corpus guide

## Goal

The corpus trains and evaluates one shared graph embedding space, rather than
separate lane-specific spaces. A comparison may filter or mask features that do
not exist in both inputs, but the encoder output remains comparable across
source, reconstructed source, bytecode, and declared stub inputs.

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

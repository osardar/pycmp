# pycmp status

Last updated: 2026-09-05

## Current outcome

pycmp has a working, manifest-driven **static** corpus and shared graph-encoder
prototype. It can ingest Python source, recover partial graphs from malformed or
reconstructed source, isolate untrusted bytecode processing in Docker, build
paired corpus views, train a shared encoder, and index embeddings for local
retrieval.

It does **not** yet have a trained and evaluated embedding model that should be
treated as a benchmark or production-quality retrieval system. The corpus target
is defined and pinned, but a complete build, curation pass, and evaluation run
remain outstanding.

## Implemented

- Semantic graph schema with normalized nodes, edges, graph metadata, and
  provenance.
- Source ingestion through the Python AST, with a tree-sitter recovery path for
  malformed or partial reconstructed source.
- `.pyc` ingestion that defaults to Docker isolation; the bytecode worker uses
  `xdis` for cross-version decoding and records unsupported decompilation gaps.
- One shared, normalized `SharedGraphEncoder` architecture for source, recovery,
  bytecode, and stub lanes. Its output dimension is 256 by default.
- Contrastive training helpers, local FAISS indexing, similarity search, and
  Vertex-compatible export.
- Corpus builder that clones immutable revisions, never runs project code, and
  writes source, formatted, renamed, and damaged graph views.
- Explicit support for `.pyi` input when a manifest declares it; views record a
  `source_kind` label so stubs can be filtered or masked at comparison time.
- Ten compact synthetic fixtures spanning Python 3.4 through 3.12 features.
- Three reviewed manifest sets: defensive-security research, analysis fixtures,
  and the 20-record lint/training target.

## Corpus status

`corpus/lint-training-target.jsonl` contains 20 immutable records:

- 10 production-source records: pytest, Pydantic, FastAPI, Flask, HTTPX,
  Requests, Django, mypy, Black, and LibCST.
- 10 fixture/reference records: Pylint, pyflakes, pycodestyle, Flake8, mypy,
  Black, two clean-code exercise sources, CPython grammar tests, and Ruff
  fixtures.

Mypy and Black intentionally appear as source and fixture records. Their shared
`split_group` ensures both records always use the same project-disjoint data
partition. The manifest excludes an unverified source and the separately
licensed QuantifiedCode anti-pattern collection from the default target.

A small static build using pyflakes and pycodestyle has successfully exercised
the build, train, index, and search workflow. A full target build has not yet
been retained as a corpus release.

## Validation completed

- Unit suite: 12 tests pass at this revision.
- Builder behavior: valid source, legacy syntax, malformed recovery input, and
  declared `.pyi` stubs are covered.
- Bytecode worker: built and smoke-tested for a current-runtime `.pyc`.
- Corpus workflow: smoke-tested from build through one CPU training epoch and
  local similarity search.

## Known gaps and next milestone

1. Build the target corpus and write a release report with file/function counts,
   parse outcomes, lane distribution, licensing, and content hashes.
2. Deduplicate copied/generated/vendor code and cap project contribution sizes so
   the largest projects do not dominate training.
3. Add fixture extractors for embedded strings, mypy test-data formats, and
   Markdown/mdtest inputs used by Ruff and other tooling projects.
4. Add explicit diagnostic labels: valid/invalid, expected parse outcome,
   diagnostic family, Python language level, and before/after pair identity.
5. Train a project-disjoint baseline and report clone retrieval,
   formatting-equivalence, lint-family, source-to-stub, and recovery-to-source
   metrics. Feature-availability masking must be applied to cross-lane metrics.

## Safety and scope

All third-party corpus ingestion is static: pycmp clones and parses files but
does not install dependencies, execute projects, authenticate, or target
external systems. The defensive-security set remains separately labeled and is
also static-only.

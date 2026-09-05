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
- Labeled fixture extraction for MyPy case files, Python Markdown blocks, Black
  input/output pairs, and CPython parser-test strings.
- Ten compact synthetic fixtures spanning Python 3.4 through 3.12 features.
- Four reviewed manifest sets: defensive-security research, analysis fixtures,
  the 20-record lint/training target, and an extended-analysis set.

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

`corpus/extended-analysis.jsonl` adds six pinned sources for the next corpus
increment: Bandit, Hypothesis, beartype, Refurb, capa, and BBOT. Their role and
license boundaries are recorded in the manifest; capa and BBOT are retained
only in the static defensive-security research tier.

## Validation completed

- Unit suite: 13 tests pass at this revision.
- Builder behavior: valid source, legacy syntax, malformed recovery input, and
  declared `.pyi` stubs are covered.
- Bytecode worker: built and smoke-tested for a current-runtime `.pyc`.
- Corpus workflow: smoke-tested from build through one CPU training epoch and
  local similarity search.
- A bounded project-disjoint baseline manifest is available at
  `corpus/baseline-pilot.jsonl`; its initial metric is paired-view recall only,
  pending a larger labeled evaluation set.
- The first extended pilot is recorded in
  `docs/baselines/2026-09-05-extended-pilot.md`: 400 training views, 12 held-out
  views, and paired-view Recall@5 of 1.0. This is a narrow end-to-end check, not
  a general retrieval benchmark.

## Known gaps and next milestone

1. Build the target corpus and write a release report with file/function counts,
   parse outcomes, lane distribution, licensing, and content hashes.
2. Deduplicate copied/generated/vendor code and cap project contribution sizes so
   the largest projects do not dominate training.
3. Extend fixture extraction to snapshots and remaining custom upstream formats,
   then validate extracted-record counts against each upstream suite.
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

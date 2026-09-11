# pycmp

`pycmp` is a research system for turning Python artifacts into comparable graph
embeddings, retrieving related known files, and studying when a system should
reject an unfamiliar file as unknown. Its inputs may be valid source, `.pyi`
stubs, incomplete/decompiler reconstructions, or isolated `.pyc` bytecode.

This project is developed entirely with AI assistance, specifically
`gpt-5.6-terra` at medium reasoning effort. It is deliberately an exploratory
environment for understanding graph embeddings and finding interesting, unique
applications of them. AI authorship is not evidence that its outputs are
correct: the tests, audit, corpus provenance, and measured benchmarks are the
evidence boundary.

## Current status

The latest local implementation is **schema 3**, with typed literals, complete
AST-field evidence, recursive declaration discovery and lexical binding candidates.
See the [source representation report](docs/SOURCE-REPRESENTATION-V3.md).
There is no trained schema-3 release checkpoint yet: the schema-2 results below
are historical, and their graphs/checkpoint/index are intentionally incompatible
with the new loader. The full first-party suite has 43 passing tests.

The schema-2 milestone repaired critical representation, training, corpus,
and retrieval defects found in the September 2026 audit. It now validates graph
identity, represents semantic feature values, emits module/class/function units,
uses a multi-positive loss, creates group-disjoint stratified splits, aggregates
whole-file embeddings, fingerprints indexes, returns scores, and can abstain.

It is still a research prototype, not a validated malware classifier or proof of
behavioral equivalence. The existing ignored `corpus-runs/release-v0.1` is an
interrupted schema-1 build and must not be reused. A capped schema-2 corpus and
trained baseline now exist, but the model has not met its acceptance gate.
The [synthetic similarity benchmark](docs/baselines/2026-09-07-synthetic-similarity.md)
tests ten held-out projects, 60 obfuscations, 111 compiled variants, and two
decompilers. Its hard-negative results expose weak behavioral discrimination.
Unknown-family calibration and direct source↔bytecode-lane validation remain open.

## Architecture

```text
valid .py/.pyi          -> CPython AST normalization -------+
partial/decompiled text -> tree-sitter recovery ------------+-> schema-3 graph
.pyc                    -> isolated version-aware worker ----+       |
                                                                  shared GNN
                                                                     |
                                               whole-file normalized embedding
                                                                     |
                                  exact hash + scored retrieval + unknown rejection
```

One shared `SharedGraphEncoder` is used for every lane. A lane-independent
semantic node kind is the primary feature. Named optional evidence—such as AST
operation type, constant category, attribute hash, and bytecode opcode—has a
bounded contribution; missing optional facts are not represented as a lane ID.
Every checkpoint and local index is tied to the graph schema and feature profile.

Source ingestion uses the authoritative CPython AST when possible. Tree-sitter
is an error-tolerant recovery path, not a substitute Python specification or a
pretend AST. Current-runtime bytecode receives instruction and branch edges in a
constrained worker; foreign-version support remains explicitly partial.

## Quick start

Create an environment and install the development dependencies:

```bash
python -m venv .venv
.venv/bin/pip install -r requirements.txt
```

Run the first-party suite:

```bash
.venv/bin/python -m unittest discover -s tests -v
```

Ingest source or bytecode:

```bash
.venv/bin/python -m codegraph.cli ingest sample.py --output sample.graphs.jsonl
docker build -f docker/bytecode-worker/Dockerfile -t pycmp-bytecode-worker:latest .
.venv/bin/python -m codegraph.cli ingest sample.pyc --output sample-pyc.graphs.jsonl
```

Build, train, evaluate, index, and query a reviewed corpus:

```bash
.venv/bin/python -m codegraph.cli corpus release \
  --manifest corpus/lint-training-target.jsonl \
  --manifest corpus/extended-analysis.jsonl \
  --manifest corpus/defensive-security.jsonl \
  --output corpus-runs/release-v0.3

.venv/bin/python -m codegraph.cli train corpus-runs/release-v0.3 \
  --checkpoint artifacts/model-v0.3.pt
.venv/bin/python -m codegraph.cli benchmark corpus-runs/release-v0.3 \
  --checkpoint artifacts/model-v0.3.pt --output artifacts/benchmark-v0.3.json
.venv/bin/python -m codegraph.cli calibrate corpus-runs/release-v0.3 \
  --checkpoint artifacts/model-v0.3.pt --target-precision 0.95
.venv/bin/python -m codegraph.cli corpus-index corpus-runs/release-v0.3 \
  --checkpoint artifacts/model-v0.3.pt --directory artifacts/index-v0.3
.venv/bin/python -m codegraph.cli search unknown.py \
  --checkpoint artifacts/model-v0.3.pt --directory artifacts/index-v0.3 \
  --threshold 0.80
```

The threshold above is only a CLI default. `calibrate` can fit a preliminary
validation threshold using different artifacts as proxy negatives; genuine novel
families are still required before its `matched`/`unknown` result is interpreted
as unknown-file performance.

## Corpus

The intended release has 41 manifest records representing 39 repository URLs:
production libraries, analysis/typing/lint fixtures, educational pairs, and a
separately labeled static-only defensive-security collection. MyPy and Black
appear in two roles but share one repository cap and split lineage. NetExec and
CrackMapExec share a lineage group. GhostPack Certify is retained in provenance
with a documented zero-Python disposition.

The builder never installs or executes third-party projects. It checks out full
pinned trees, applies one zero-or-more-directory glob contract, records exact and
structural hashes, caps each repository deterministically, and keeps repository
groups out of multiple splits. Generated corpora and checkpoints remain ignored;
canonical manifests, policies, tests, and reports belong in Git.

## Legacy prototype and vocabulary

`pycmp.py`, `ptg.py`, `gcn_model.py`, the GraphML samples, and `vocab.json` are
historical demonstrations. They train separate per-graph GCNs against placeholder
targets, so their embeddings are not comparable and must not be used by the
shared retrieval workflow. `vocab.json` describes tree-sitter-python grammar
0.23.4 node types; it is not the Python language specification and does not cover
all Python versions. The current encoder uses versioned hashed features instead.

## Documentation

- [Full project audit](docs/AUDIT-2026-09-07.md)
- [Remediation plan and execution ledger](docs/REMEDIATION-PLAN.md)
- [Unknown-file classification strategy](docs/CLASSIFICATION-STRATEGY.md)
- [Current status](docs/STATUS.md)
- [Corpus guide](docs/CORPUS.md)
- [First schema-2 capped baseline](docs/baselines/2026-09-07-schema2-capped.md)

## Safety and interpretation

Security-tool provenance is not a malicious label. Similarity is not proof of
authorship, intent, exploitability, or equivalent behavior. Low-coverage recovery
inputs return `insufficient_evidence`; below-threshold valid inputs return
`unknown`. Unsupported decoders must fail explicitly rather than enter a scored
index as placeholder evidence.

Untrusted `.pyc` decoding defaults to a network-disabled, read-only, non-root
Docker worker. Third-party corpus source is treated as data and is never imported
or executed.

## License

First-party project licensing and third-party corpus licensing are separate.
Each corpus record preserves its source-host license identifier and research
handling policy; that metadata is not a substitute for a legal license audit.

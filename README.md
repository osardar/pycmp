# pycmp

`pycmp` is an experimental Python-code similarity research project. It converts
source, stubs, reconstructions, and supported compiled Python into graph
representations and embeddings, then evaluates similarity ranking. It is not a
malware classifier, and a similarity score is not evidence of common behavior,
authorship, or intent.

The project is developed with AI assistance (`gpt-5.6-terra`, medium reasoning
effort). AI authorship is not evidence that outputs are correct; tests, provenance,
audits, and measured evaluation are the evidence boundary.

## Current state

The current representation is graph schema 3. Three frozen 64-dimensional
checkpoints are documented in [their model cards](docs/modelcards/README.md),
but the checkpoint files themselves are generated local artifacts and are not
included in a Git clone. On source-to-source retrieval, the trained checkpoints
do not show a consistent advantage over the untrained encoder or simple feature
baselines. Direct bytecode-to-bytecode retrieval finds known compiled lineages in
its development gallery, but the opcode-structure baseline currently outperforms
all trained checkpoints. The measurements are development evidence, not malware
family generalization or production validation. Cross-lane source↔bytecode
alignment has not been demonstrated.

There are two separate command-line projects:

- The research CLI (`codegraph.cli`) builds corpora, trains/evaluates models, and
  runs experiments. Its generated corpora, indexes, and weights are not generally
  shipped in Git.
- The independent [`pycmp-vectorizer`](tools/file-vectorizer/README.md) project
  accepts `.py`, `.pyi`, and supported `.pyc` files and emits JSONL vectors. Its
  local CPU CLI/API is implemented, but a clone does not include a checkpoint.
  The all-runtime release Docker image and complete Python 3.8–3.14 qualification
  are not yet delivered. See its README for the exact runtime and checkpoint
  requirements. Unlike the broader research ingestion pipeline, this standalone
  utility rejects malformed source instead of using the recovery parser.

## Run the standalone vectorizer locally

Use Python 3.14 and `uv`. From `tools/file-vectorizer`:

```sh
uv sync --locked --python 3.14
uv run --locked pycmp-vectorizer check \
  --host-runtime --checkpoint /path/to/model-seed0.pt
uv run --locked pycmp-vectorizer vectorize path/to/sample.py \
  --host-runtime --checkpoint /path/to/model-seed0.pt --output -
```

The checkpoint must be obtained separately and match the vectorizer's schema and
feature profile. `--host-runtime` only enables bytecode produced by the current
Python interpreter; it does not provide multi-version bytecode support. The full
interface, input limits, JSONL format, safety boundaries, and known collisions
are in the [vectorizer guide](tools/file-vectorizer/README.md).

## Research CLI

The root package is the research/development environment, not the standalone
distribution. Create an environment and install its requirements:

```sh
python -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/python -m codegraph.cli --help
```

For corpus provenance and supported workflows, start with the [documentation
index](docs/README.md). Do not reuse old schema-2 graphs, checkpoints, or indexes
with schema 3; the compatibility checks intentionally reject them.

## Architecture and interpretation

```text
source / stub / recovery text ─┐
                               ├─> schema-3 graph -> shared encoder -> file vector
supported isolated .pyc ──────┘                              │
                                                cosine ranking / retrieval
```

The encoder uses typed graph features and normalized mean pooling across units.
Source parsing uses the current CPython AST where accepted; tree-sitter is an
error-tolerant recovery path. Bytecode decoding is version-sensitive and only
accepted when the configured decoder recognizes the input. Same vector length
does not establish that two input lanes are meaningfully aligned.

Third-party corpus code is handled as data: it is not installed, imported, or
executed. Similarity retrieval is the active scope. Relation classification,
malware verdicts, model promotion, and production deployment remain out of scope.

## Key documents

- [Documentation map and current evidence](docs/README.md)
- [Current project status and experiment progress](docs/STATUS.md)
- [Similarity scope decision](docs/SIMILARITY-SCOPE.md)
- [Corpus and provenance guide](docs/CORPUS.md)
- [Schema-3 representation](docs/SOURCE-REPRESENTATION-V3.md)
- [Checkpoint model cards](docs/modelcards/README.md)
- [Standalone vectorizer](tools/file-vectorizer/README.md)

## Legacy prototype and vocabulary

`pycmp.py`, `ptg.py`, `gcn_model.py`, the GraphML samples, and `vocab.json` are
historical demonstrations. They train separate per-graph GCNs against placeholder
targets, so their vectors are not comparable and must not be used by the shared
retrieval workflow. `vocab.json` describes tree-sitter-python grammar 0.23.4 node
types; it is not a Python language specification.

## License

First-party project licensing and third-party corpus licensing are separate.
Corpus records preserve source-host license identifiers and handling policies;
that metadata is not a substitute for a legal license audit. Checkpoint artifacts
have no separately declared license in the recorded metadata.

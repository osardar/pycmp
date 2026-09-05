# pycmp

**Code-as-graph neural network experiment.**

This project is developed entirely with AI assistance, specifically
`gpt-5.6-terra` at medium reasoning effort. It is an exploratory environment for
understanding graph embeddings and identifying interesting, distinctive ways they
can be applied to code and other structured program artifacts.

`pycmp` parses Python source code into a syntax tree, converts that tree into a
graph, and runs it through a **Graph Convolutional Network (GCN)** built with
PyTorch Geometric to produce per-node embeddings. The goal is to learn a
representation of code structure that can be reused for downstream tasks such as
clone detection, similarity search, or vulnerability/defect analysis.

---

## Pipeline

```
Python source  ──►  tree-sitter parse  ──►  concrete syntax tree (CST)
        │
        ▼
networkx DiGraph  (one node per syntax element, edges = parent→child)
        │
        ▼
PyTorch Geometric Data (edge_index + node features x)
        │
        ▼
2-layer GCN  ──►  100-epoch train loop  ──►  node embeddings
```

1. **Parse** — `tree-sitter-python` turns source into a CST.
2. **Graphify** — each CST node becomes a `networkx.DiGraph` node, labeled by its
   syntax `type` (e.g. `import_statement`, `identifier`) with its source `text`;
   parent→child relations become directed edges.
3. **Features** — every node gets a fixed-size **one-hot vector over syntax-type
    labels**, so `data.x` lines up with `edge_index`. A global vocabulary
    (`vocab.json`) lets all graphs share one mapping; wiring it in is the active next
    step (today the mapping is still built per graph).
4. **To tensor** — `torch_geometric.utils.from_networkx()` produces a `Data`
   object (`edge_index` + node features `x`).
5. **Model** — a 2-layer `GCN` (`GCNConv → ReLU → GCNConv`), hidden dim 16,
   output dim 8.
6. **Train / embed** — Adam optimizer for 100 epochs, then a forward pass to emit
   per-node embeddings.

---

## Files

| File | Purpose |
|---|---|
| `pycmp.py` | **Main pipeline.** Parse a Python file → build graph → build GCN → train → print node embeddings. |
| `ptg.py` | **Variant.** Skips parsing; loads pre-built `*.graphml` graphs and runs a GCN on each. |
| `gcn_model.py` | **Shared module.** `GCN` model plus `build_node_features`, `graph_to_data`, `train_gnn`, and `gen_embeddings`, used by both entry points. |
| `test0`, `test1` | Two nearly-identical sample Python scripts used as input (they differ only in the URLs and the printed strings — useful as a "similar code" pair). |
| `test0.graphml`, `test1.graphml` | Graph-serialized versions of the two test scripts (133 nodes each), consumed by `ptg.py`. |
| `build_vocab.py` | **Tooling.** Builds the global feature vocabulary (below) either from the tree-sitter grammar (`--from-grammar`) or from a corpus of `.graphml` files. |
| `vocab.json` | **The global feature vocabulary** — a fixed label→index map (216 dims) that all graphs are meant to share. |
| `tree_sitter_python_node_types.json` | Vendored tree-sitter-python v0.23.4 grammar node types; the source for `vocab.json`. |
| `requirements.txt` | Pinned dependencies, plus unpinned `torch` / `torch_geometric`. |

---

## Install

```bash
pip install -r requirements.txt
```

`torch` and `torch_geometric` are listed in `requirements.txt` but left unpinned,
since the right build depends on your OS / CUDA. If the generic install doesn't
match your environment, install a build that does:

```bash
pip install torch
pip install torch_geometric   # or: pip install torch-geometric
```

---

## Usage

### `pycmp.py` — parse code, then graph + train

```bash
python pycmp.py test0
```

Reads the Python file given as `argv[1]`, parses it, builds the graph, trains the
GCN, and prints node embeddings.

### `ptg.py` — load pre-built graphs, then train

```bash
python ptg.py test0.graphml test1.graphml
```

Reads each `.graphml` file as a graph, runs a GCN on each, and prints embeddings.
Graphs loaded from graphml store the node type under the `label` key (rather than
`type`), which `build_node_features` handles.

---

## Feature vocabulary

For two files' embeddings to be comparable, every graph must be encoded against the
*same* label→index mapping. `build_vocab.py` produces that as a single, fixed
**global vocabulary** written to `vocab.json`.

- **Source.** The vocabulary is built from the tree-sitter-python grammar's
   `node-types.json` (vendored as `tree_sitter_python_node_types.json`, version
   `0.23.4` to match `requirements.txt`) rather than from the small test corpus, so
   it covers every syntax type the parser can emit — not just the 33 the two test
   files happen to use.
- **Contents.** 215 distinct node types + 1 reserved `<unknown>` slot = **216
   dimensions**. `<unknown>` (index 0) is a safety net for grammar-version drift or
   unseen tokens; the rest get indices in sorted order for stability.
- **Reproducible.** Because the mapping is fixed and corpus-independent, it does not
   shift as you add data, and `vocab.json` can be committed as an artifact.

Build it with:

```bash
# from the full grammar (recommended):
python build_vocab.py --from-grammar

# or inspect what a corpus of graphs actually uses:
python build_vocab.py test0.graphml test1.graphml
```

> The vocabulary is built but **not yet wired into** `build_node_features` — that is
> the top next step (see below).

---

## Current state

This is an early prototype that wires up the data path and the forward/backward
pass. It is **not** yet a trained or evaluated model.

### Known issues / rough edges

- **Training target is a placeholder.** `train_gnn()` falls back to
  `make_placeholder_target()`, a *seeded* (reproducible) random tensor, so the 100
  epochs exercise the pipeline deterministically but do not learn anything
  meaningful yet. Replace with a real target (labels, a reconstruction target, or
  a task loss).
- **Vocabulary not yet wired in.** `vocab.json` and `build_vocab.py` exist, but
   `build_node_features` still builds a per-graph mapping. Wiring the global vocab in
   (plus one shared `GCN`) is needed before embeddings from different files are
   comparable.
- **First commit pending.** The directory is now a git repository (initialized, with
   a `.gitignore`), but no commit has been made yet.

---

## Suggested next steps

- **Wire in the global vocabulary.** Have `build_node_features` load `vocab.json` and
   use one shared `GCN` across all graphs, so `test0`/`test1` embeddings live in a
   common space.
- Add a real training objective / loss and a way to load labels.
- Add a basic test comparing embeddings of `test0` vs `test1` (expecting them to be
   "close").
- Make the first git commit.

---

## Shared cross-lane embedding pipeline

The original CST-only experiment remains available in `pycmp.py`. New work lives
in `codegraph/` and establishes a single embedding space across inputs rather
than training a different GCN per file or lane.

```text
valid .py source       -> Python AST normalizer  --+
partial/decompiled .py -> Tree-sitter recovery   --+-> semantic program graph
.pyc (isolated worker) -> bytecode/CFG normalizer --+-> one shared relational GNN
```

- **Comparable units.** Functions and methods are embedded directly. A learned
  pooling layer produces module/project vectors; project retrieval combines that
  vector with top function-level matches.
- **Missing facts.** Graph nodes and edges carry availability masks. A missing
  source-only fact is not encoded as a false value, so recovery and bytecode
  graphs retain the same model input contract.
- **Safety.** Source and bytecode are never imported or executed. `.pyc` payloads
  are decoded only by a short-lived constrained subprocess. This current decoder
  accepts bytecode matching that worker's CPython runtime; a version-aware decoder
  adapter is required before ingesting a different `.pyc` runtime.
- **Training.** `codegraph.training` supplies paired-view contrastive training:
  source, bytecode, decompilation, damaged reconstructions, and semantic-preserving
  transformations of the same artifact are positives.
- **Corpus.** `LocalFaissIndex` persists stable record IDs and metadata locally.
  `VertexAIVectorSearchIndex` defines the compatible managed-search boundary.

Example:

```bash
python -m codegraph.cli ingest path/to/input.py --output artifact.graphs.jsonl
python -m codegraph.cli embed artifact.graphs.jsonl --output artifact.embeddings.jsonl
python -m codegraph.cli index artifact.embeddings.jsonl --directory corpus-index
```

Run the standard-library test suite with:

```bash
python -m unittest discover -s tests
```

---

## License

Not specified.

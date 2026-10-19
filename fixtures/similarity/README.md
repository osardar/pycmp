# Synthetic similarity projects

Compatibility update: the frozen results and checkpoint below use schema 2.
Current source ingestion uses schema 3 and deliberately rejects that checkpoint.
Compilation/decompilation generation remains available; evaluation needs a matching
schema-3 checkpoint or the matching historical schema-2 implementation. See the
[migration notes](../../docs/SOURCE-REPRESENTATION-V3.md).

Historical benchmark recipe: its pinned local checkpoint and runtime artifacts are
not distributed in a clone, and its results are superseded as current quality
evidence by the later schema-3 experiments. Do not run the schema-2 command below
against the current loader or present its scores as current model quality; see the
[current status](../../docs/STATUS.md).

Ten owned, concise projects reserved for evaluation, not training. Each exposes
`main.run(payload)` and three JSON oracle cases. The manifest lists every module
and minimum Python version; no third-party target code is executed.

| Project | Python minimum | Features |
|---|---|---|
| invoice | 3.4 | Two modules, imports, arithmetic, discounts |
| inventory | 3.4 | Inheritance, properties, mutable state |
| events | 3.4 | Generators, filtering, windows |
| transaction | 3.4 | Context managers, exceptions, rollback |
| memo | 3.4 | Decorators, closures, memoization |
| codec | 3.4 | JSON, encoding, comprehensions |
| dispatch | 3.4 | Callback dispatch, mappings |
| dependencies | 3.4 | Recursion, graph traversal, cycle handling |
| async_queue | 3.8 | Async functions and generators |
| typed_router | 3.12 | Generic syntax, type aliases, match, exception groups |

`generated/` contains deterministic light and structural obfuscations for seeds
0, 1, and 2, transformation maps, and a behavior-changing negative for each
project. Oracles live beside the originals and are shared by all variants.
Unit tests regenerate all obfuscations and check both stored output and behavior.

Light obfuscation renames owned local symbols and removes comments/docstrings,
then compacts formatting. Structural obfuscation also encodes string expressions,
inverts eligible branches, and wraps return expressions in an identity helper.
Imports, public entry points, and method APIs are preserved. This deliberately
limited transformer is validated against these fixtures, not arbitrary Python.
Different seeds vary identifiers, not the structural transformation recipe.

## Reproduce

Use Python 3.14 for the host environment with the repository requirements
installed. Docker must support linux/amd64 emulation for the legacy images.

```bash
docker build -f docker/similarity-tools/Dockerfile -t pycmp-similarity-tools:v1 .
.venv/bin/python -m codegraph.cli similarity-benchmark build \
  --output corpus-runs/similarity-new --workers 4
.venv/bin/python -m codegraph.cli similarity-benchmark evaluate \
  corpus-runs/similarity-new \
  --checkpoint corpus-runs/release-v0.2-capped/model-d64-l2-e1.pt
.venv/bin/python -m unittest discover -s tests -v
```

The evaluation command requires that existing local checkpoint; it does not
download or silently train one. Another checkpoint can be supplied, but produces
a different experiment. Runtime images are pulled by digest when absent.

The runtime matrix is 3.4/3.8/3.12/3.14 × optimization 0/1/2, skipping projects
below their declared minimum: 111 combinations, 123 module binaries, and 222
two-tool project reconstruction attempts. Additional probes verify actual compiler
optimization semantics. Optimized 3.4 outputs are genuine `.pyo`; modern outputs
use tagged `.pyc` names. Builds refuse to overwrite a completed run.

Every compilation and reconstruction retains diagnostics and behavior checks.
Evaluation verifies artifact checksums and produces `report.md`, `evaluation.json`,
and `embeddings.json` under the run directory. Similarity is signed cosine × 100,
not a probability. Failed reconstructions remain diagnostic-only and are not
counted as successful similarities. Full binary/execution outputs stay ignored;
the source fixtures and baseline reports are committed.

See the [measured baseline](../../docs/baselines/2026-09-07-synthetic-similarity.md).

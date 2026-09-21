# pycmp-vectorizer

Standalone, CPU-only Python file → JSONL vector CLI and Python API. It has no
runtime imports from the parent research package. A checkpoint is always supplied
explicitly; successful vectors are normalized, errors never get zero vectors.

## Current delivery status

The local CLI/API is implemented. Local verification covers source and **host
Python 3.14 bytecode**. The seven-runtime release container, GKE deployment example,
and full 3.8–3.14 integration qualification are **not yet delivered**. Runtime
dispatch supports an explicit fingerprinted inventory; do not interpret this as
completed multi-version validation. No checkpoint is distributed in this project.

## Install and run locally

Use Python 3.14. From this project directory:

```sh
uv sync --locked --python 3.14

uv run --locked pycmp-vectorizer check \
  --host-runtime --checkpoint /absolute/path/to/model-seed0.pt

uv run --locked pycmp-vectorizer vectorize examples/example.py \
  --host-runtime --checkpoint /absolute/path/to/model-seed0.pt --output -
```

From the repository root, the already-installed development environment can run:

```sh
tools/file-vectorizer/.venv/bin/pycmp-vectorizer vectorize \
  tools/file-vectorizer/examples/example.py \
  --host-runtime \
  --checkpoint corpus-runs/schema3-baseline-v1/model-seed0.pt \
  --output -
```

Pass multiple paths, or a directory plus `--recursive`. Supported extensions are
`.py`, `.pyi`, and `.pyc` (case-sensitive). Use `--include-units` for additional
per-unit vectors. Output files must be new and outside input directories.
`--output -` sends only JSONL to stdout; logs and summaries go to stderr.

`--host-runtime` is explicit development mode: only the current interpreter's
bytecode magic is available, not every Python version. Without it, preflight
requires all seven pinned runtimes via `--runtime-manifest` or
`PYCMP_RUNTIME_MANIFEST`. The manifest contains `implementation` (the hash reported
by `check`) and `runtimes` entries with absolute executable path, exact version,
magic hex, and executable SHA-256. Each entry is probed and verified at startup.
Source parsing always requires Python 3.14; the library's parent process also
requires Python 3.14. Missing inventory never falls back silently in release mode.

## JSONL contract

Each `record_type: file` record includes path, available input hash, lane,
checkpoint hash, embedding profile ID/details, runtime provenance, and status.
Successful records additionally contain `vector`, graph hash, dimension in the
profile, unit/node/edge counts, diagnostics, and a cache-hit indicator. With the
current frozen checkpoints, vectors contain 64 numbers. Unit IDs are canonical
file-relative IDs; the input path is recorded separately.

Error records omit the vector and include `error.category`, `error.code`, and a
bounded diagnostic. Bytes are hashed only after admission: an unreadable or
oversized input can have a null input hash. Content duplicates retain separate
path records while sharing a bounded 128-entry/32-MiB result cache.

The terminal `record_type: summary` contains traversal counts, skips, failures,
cache hits, and `completion: complete|partial`. Complete means traversal finished,
not that every input succeeded. Consumers must distinguish summaries from vectors.
A missing summary or truncated final line indicates an incomplete invocation.
Earlier complete lines remain usable; output append/resume is not supported.

Exit codes: **0** all attempted inputs succeeded; **2** file/traversal errors;
**1** configuration/infrastructure/output error or no candidates; **130** interrupt.
Noncandidate files encountered in directories are counted as skips. Explicit
unsupported paths are errors. No archives, URLs, or symlinks are followed; on
macOS use canonical `/private/tmp` paths instead of symlinked `/tmp` or `/var`.

## Safety and limits

Submission code is never imported or executed. Parsing/decoding happens in a
bounded child; graph validation and encoding use a persistent supervised child.
This is resource containment, **not a hostile multi-tenant security sandbox**.
Use read-only inputs/models and one submission trust boundary per isolated job.
Only load trusted, provenance-verified checkpoints, even with `weights_only=True`.

Admission limits: source 64 KiB, bytecode 8 MiB; source 10,000 nodes/100,000 edges,
bytecode 100,000 nodes/500,000 edges. Limits reject; they never truncate. Parser
and inference deadlines are 30 seconds each. Parser RSS guard is 512 MiB and
inference RSS guard 2 GiB, polled at most every 50 ms. Worker output is capped at
16 MiB. Linux parsers additionally enforce a 512-MiB address-space limit; macOS
local development uses only the RSS watchdog for memory. Watchdogs can overshoot;
deployment must also impose a container limit (initially 4 GiB). A container OOM
can end a batch without a terminal summary.

The encoder restarts after an inference crash or guard violation; the offending
file is not retried. Invalid source is not recovered silently. Bytecode magic
must match an inventoried runtime. Schema/profile errors fail explicitly.

## Python API

```python
from pycmp_vectorizer import Vectorizer

def main():
    with Vectorizer("/models/model.pt", host_runtime=True) as encoder:
        for result in encoder.vectorize_paths(["/inputs"], recursive=True):
            print(result)
        print(encoder.summary)

if __name__ == "__main__":
    main()
```

The main guard is required because inference uses multiprocessing spawn. Prefer
the CLI for notebooks or interactive sessions. A Vectorizer is sequential and
not thread-safe. Exhaust streams to obtain a complete summary; close the context
on cancellation. `vectorize_file` is also available for a single file.

## Representation limitations

This preserves a frozen encoder; it does not improve or promote its quality.
Source and bytecode use distinct profile IDs. Matching vector lengths do not
establish comparability; even matching profiles do not prove cross-runtime quality.
Bytecode operand values are omitted, and recorded argument kinds/code names do
not reach the encoder. Different constants or arithmetic operations may therefore
produce identical vectors. These expected collisions are regression-tested.

`src/pycmp_vectorizer/SNAPSHOT.json` records original and vendored hashes plus
deployment adaptations. Original graph/encoder files remain unchanged. No separate
license has been asserted for these first-party snapshot files or checkpoints.

## Tests

```sh
uv run --locked python -m unittest discover -s tests -v
```

Tests cover source parity, owned bytecode and side-effect sentinels, encoding,
malformed inputs, resource rejection, restart, symlinks/FIFOs, duplicates, summaries,
CLI exit/output handling, and a process launched outside the research repository.
No corpus programs are executed by these tests.

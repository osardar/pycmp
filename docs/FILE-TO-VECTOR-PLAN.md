# Standalone Python file vectorizer

Status: revised implementation plan. Supersedes the earlier proposal to extend
the research CLI. The existing standalone scaffold is incomplete; this document
does not claim implementation or validation is finished.

## Summary

Build an independent CPU-only project at `tools/file-vectorizer`, with package
and executable name `pycmp-vectorizer`. Its CLI and Python API accept supported
Python source or bytecode files and emit one normalized embedding per accepted
file. Package everything in one Docker image, with Python 3.8–3.14 decoding
runtimes and an explicitly mounted checkpoint.

No UI, HTTP server, BM25, database, search index, project-vector aggregation,
retraining, historical backfill, or cloud deployment is included. Bytecode
vectors use the experimental expanded decoder profile; cross-lane comparability
is not promised.

- Use a standard `pyproject.toml`, `src/` package layout, locked dependencies,
  independently runnable tests, and a standalone Docker build context.
- Vendor only the required graph schema, source normalization/binding analysis,
  encoder, and decoding implementation. Record original paths and SHA-256 hashes
  in a snapshot manifest and preserve applicable license notices. Runtime
  adaptations must be separately documented and covered by parity tests.
- Neither installed package nor image may import the parent research package or
  depend on its corpus/experiment directories. Do not alter the research CLI.

## Interface and output

- Provide separate preflight and vectorization commands:

  ```sh
  pycmp-vectorizer check --checkpoint /models/model.pt

  pycmp-vectorizer vectorize /inputs \
    --recursive \
    --checkpoint /models/model.pt \
    --output /outputs/vectors.jsonl
  ```

- Accept multiple file and directory paths. Directory traversal is deterministic;
  recursion requires `--recursive`. Support `.py`, `.pyi`, and `.pyc`; do not follow
  symlinks, unpack archives, fetch URLs, or extract embedded executables.
- Require a checkpoint explicitly. Validate its schema and feature configuration, load it once with the existing restricted loader, and record its SHA-256. Never substitute an untrained model.
- Expose a context-managed `Vectorizer` API with `vectorize_file(path)` and
  streaming `vectorize_paths(paths, recursive=False)` methods. The API and CLI
  share processing and result types; leaving the context terminates child workers.
- Emit versioned JSONL records containing input path/hash, status, lane, detected runtime where applicable, graph profile/fingerprint, checkpoint hash, vector dimension, unit count, diagnostics, and vector.
- Give each file record `record_type: file` and a stable `embedding_profile_id`:
  SHA-256 of canonical JSON containing checkpoint hash, graph-schema version,
  lane-specific parser/decoder implementation identity, selected-feature and
  encoder implementation identities, pooling policy, normalization, and dimension.
  A graph-content fingerprint identifies the particular input representation and
  is separate from this shared profile identifier.
- Record runtime version, image/build and dependency fingerprints separately.
  Equal dimensions are not compatibility evidence. Different profile IDs must
  not be silently mixed in downstream indexes; matching profile IDs still do not
  prove retrieval quality across runtimes. Document same-environment reproducibility
  separately from cross-build numerical tolerance.
- Successful records contain finite, L2-normalized vectors. Failed records contain no vector—not a zero vector. Preserve separate records for duplicate input paths/content, while sharing computation within the invocation.
- Reject zero-norm/nonfinite embeddings. Use `allow_nan=False`. Cache successful
  computed results only, with an LRU bounded by both 128 entries and 32 MiB of
  serialized results; oversized results bypass the cache. Cache keys include
  content hash, input lane, profile, runtime, and unit-output option. Do not cache
  entire source files, graphs, or transient failures across the batch.
- Default to file vectors; `--include-units` additionally emits unit identities and vectors inside each file record.
- Allow stdout output with `--output -`; send logs to stderr. Refuse to overwrite an existing output file. Flush complete records incrementally.
- End normally with one `record_type: summary` JSONL record: completion state,
  counts discovered/attempted/succeeded/failed/skipped/cache hits, and failures or
  skips grouped by reason. `complete` means traversal exhausted and all attempted
  files have outcomes, not that every file succeeded. The API exposes the same
  summary after stream exhaustion and the CLI repeats a concise summary to stderr.
- Report encountered noncandidate directory entries and symlinks as skipped
  counts, without reading or following them. Explicitly supplied unsupported files
  or symlinks produce error records. Unreadable files or traversal failures are
  explicit errors, not silent skips. Zero candidate files is an error.
- Exit codes: `0` for exhausted traversal with at least one candidate and all
  attempted files successful; `2` for per-file/traversal failures; `1` for fatal
  configuration/infrastructure/output failures or no candidate inputs; `130` for
  an interrupt. Skipped noncandidate directory entries alone do not fail a batch.
- On catchable interruption or fatal failure after output opens, attempt a partial
  summary and stop workers. A missing terminal summary or incomplete trailing line
  means interruption, never success. Earlier complete file records remain usable;
  v1 does not append/resume existing output or claim an undiscovered total.

## Accepted-input contract

- Acceptance requires a supported regular file, readable bytes, successful static
  parsing/decoding and graph validation, resource-policy compliance, and a valid
  embedding. File extension alone never establishes validity.
- Parse `.py`/`.pyi` using the pinned Python 3.14 grammar and typed-AST profile.
  The seven bytecode runtimes do not imply seven source parsers or acceptance of
  every historical Python grammar. Honor encoding declarations; reject decoding
  and syntax errors without replacement text or recovery-graph fallback.
- Accept CPython bytecode only when its magic maps unambiguously to a bundled
  runtime and the header/payload validate. Report unknown magic as unsupported
  runtime, not malformed source. Do not infer compatibility from `.pyc` alone.
- Use distinct error categories for unsupported format/runtime, malformed source
  or bytecode, I/O, policy rejection, timeout, worker failure, graph/schema failure,
  and invalid embedding. Preserve detailed bounded reasons such as `input_limit`,
  `node_limit`, `edge_limit`, and `memory_limit` within those categories.
- The 64 KiB source and 8 MiB bytecode limits are admission policy, not Python
  validity rules. A syntactically valid oversized file is explicitly rejected by
  policy. Empty/comment-only source may produce a valid module graph; label its
  lack of substantive statements as a diagnostic, not proof of useful similarity.

## Processing and packaging

- Source: honor Python encoding declarations, parse with the current typed-AST normalizer, and preserve existing binding/literal feature policy. Reject invalid source explicitly; no silent recovery-graph fallback in v1.
- Bytecode: inspect the header, select the exact compatible bundled interpreter by magic number, and decode without importing or executing the submitted program. Reject unknown magic, malformed payloads, placeholder graphs, and incompatible schemas.
- Preserve `native-dis-v1` decoding semantics in a deployment-specific worker. Verify parity against the experiment’s worker; do not silently mix this profile with historical decoder vectors.
- Use the existing normalized mean of unit embeddings for file vectors. Bytecode currently yields a combined module graph, not source-equivalent function decomposition.
- Process files sequentially with one Torch thread. Bound parser/decoder
  subprocesses to 30 seconds, 512 MiB address space, and 16 MiB output. Default
  input limits: 64 KiB source and 8 MiB bytecode. Across all units in one file,
  source graphs are capped at 10,000 nodes/100,000 edges and bytecode graphs at
  100,000 nodes/500,000 edges. Enforce counts during construction and revalidate
  at the consumer boundary. Never truncate an input, graph, or unit set to fit.
- Keep the coordinator lightweight. Graph JSON decoding/validation, tensor
  construction, encoding, and optional unit-output serialization all run in a
  supervised inference subprocess, with a 30-second per-file deadline and a
  2 GiB RSS guard sampled at most every 50 ms. Keep the checkpoint loaded in that
  worker between files; restart and reload after a per-file crash/limit violation.
  Initial model-load failure is fatal. Do not retry the offending input.
- Bound inference IPC/results to 16 MiB and never use an unbounded output pipe.
  Kill and reap process groups on timeout, memory guard, or interruption. The RSS
  watchdog is not a hard memory ceiling: the 4 GiB container cgroup limit is the
  final backstop. Container OOM may terminate the batch and must leave completion
  absent/partial. Measure the full admitted envelope before claiming reliable
  batch continuation under memory pressure.
- Build a Linux/amd64 image using CPU-only PyTorch and locked dependencies. Build all seven CPython runtimes against one pinned base distribution, using the exact patch versions recorded by the expanded experiment. Lock official source checksums; fail the build rather than substitute unavailable versions.
- Generate a runtime manifest containing interpreter versions, executable hashes,
  magic numbers, and worker hashes. `check` validates all seven pinned runtimes,
  the representation snapshot, and checkpoint compatibility. The release image
  must fail closed if its inventory is incomplete; no implicit host-runtime
  fallback in the supported container workflow.
- Run non-root with no Docker daemon/socket requirement. Document read-only input/model mounts, writable output, bounded temporary storage, disabled networking, and dropped privileges.
- Supply a local Docker invocation and a GKE Job example using GKE Sandbox, initially requesting 1 CPU/2 GiB and limiting 2 CPU/4 GiB. These are starting allocations, not throughput guarantees.

## Validation and acceptance

- Build/install/run with the parent research package unavailable. Verify the
  snapshot manifest and locked dependency/runtime checks; prevent silent drift.
- Verify source vectors match the existing evaluator for identical graphs/checkpoints; verify safe formatting/renaming invariance and declared literal sensitivity.
- Test owned bytecode fixtures for all seven runtimes and optimization levels 0/1/2. Compare graph and vector outputs with the expanded experimental profile.
- Document `native-dis-v1` blind spots: operand values are omitted and recorded
  `argument_kind`/`code_name` are not encoder-selected features. Add regression
  fixtures demonstrating expected feature/vector equality for changed return
  constants and, on applicable runtimes, arithmetic operations sharing `BINARY_OP`.
  Fixtures must avoid constant folding. These are known collisions, not passing
  behavioral-equivalence claims. Do not add operands or change features to make
  these tests distinguishable; that requires a new profile and evaluation.
- Use side-effect sentinels to prove submissions are never executed. Test malformed headers/payloads, unsupported magic, encoding declarations, invalid source, symlinks, size/node limits, timeouts, subprocess cleanup, and checkpoint mismatch.
- Verify mixed-success batches, deterministic traversal, duplicate provenance, JSONL validity, exit codes, optional unit vectors, finite normalization, and repeatability within a fixed environment.
- Test source grammar versus bytecode runtime coverage; valid-but-over-limit
  inputs; edge-heavy graphs; validation/tensor/inference timeouts and memory guard
  termination; inference-worker restart; bounded cache eviction; empty directories;
  skip/error accounting; summary counts; interrupted/truncated output; and output
  write failure. Include profile-ID separation and fingerprint mismatch tests.
- Run the finished image without networking, privileges, or writable root filesystem. Confirm it requires no host Python or Docker socket.
- Record measured image size, startup time, peak RSS, and per-file latency on owned fixtures and a fixed small corpus sample. Keep deployment parity tests separate from claims about retrieval quality.

## Safety and compatibility

- One image means parser subprocesses share the container’s security boundary. Document one submission/trust domain per sandboxed Job; do not present subprocess limits as tenant isolation.
- Keep source and bytecode lane/profile metadata visible so downstream indexes cannot accidentally treat matching dimensions as validated cross-lane alignment.
- Preserve the existing experiment and its immutable implementation fingerprints.
  Develop the standalone snapshot under `tools/file-vectorizer` without changing
  `codegraph/`, its dependencies, or checkpoint files. Tests must not mutate the
  research environment or experiment outputs; use independent environments and
  generated fixtures. Preserve all unrelated uncommitted work.
- Do not modify checkpoints, promote a model, commit, push, or deploy to GKE as part of implementation.

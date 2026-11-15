# Project review: architecture, evidence and readiness

Reviewed 2026-11-15 against source at `3b43a62`, committed reports, and local
experiment reports/completion markers. This is a documentation and evidence
review, not a rerun of the corpus experiments or a security audit. The local
expanded-run ledger was queried read-only. Historical measurements retain their
original environments and dates.

## What is usable today

pycmp can statically represent Python code and produce vectors for ranking
related files. Its strongest measured use is finding controlled variants of
known source files. It also retrieves known compiled lineages in the completed
Python 3.14 bytecode experiment. These are useful foundations for analyst triage:
submit a file, retrieve plausible relatives, then inspect the code and evidence.

The learned component is a small graph neural network encoder. It has no text
generation component and was not trained to predict malware labels. Three frozen
64-dimensional checkpoints exist locally; none has been promoted. The standalone
CLI emits vectors, while the research package supplies evaluation and local
search. A clone includes neither checkpoint weights nor the generated corpus.

| Use case | Evidence and practical boundary |
|---|---|
| Modified source → known source | 97.22–97.58% trained Hit@1 in the 2,270-entry development gallery; token baseline 97.90%. Strong related-file retrieval, without a consistent learned advantage. |
| Python 3.14 bytecode → bytecode | 90.15–92.35% trained Hit@1 across optimization cells and 179 known lineages; opcode structure 96.40%. Useful in this narrow setting. |
| Reconstructed source → source | 41.27–42.46% trained Hit@1; quality depends heavily on reconstruction. Token baseline 85.69% on its smaller applicable subset. |
| Direct bytecode → source | 0% trained Hit@1 in the completed corpus-derived experiment. Do not deploy a mixed-lane index on the assumption of alignment. |
| Cross-version bytecode and repository bundles | Python 3.8–3.14 engineering pilot completed; full scoring remains partial. Pilot findings below are materially weaker than the earlier narrow benchmark. |
| Historical archive of 1–2 million files | No measured ingestion throughput, production index sizing, recall/latency target, or end-to-end archive benchmark. |

Hit@1 means the expected original ranks first in that experiment's gallery.
It is not malware-detection accuracy. The source and bytecode galleries differ
greatly in size and composition; their percentages are not directly comparable.

## How the representation and encoder work

1. **Parse or decode statically.** Research ingestion uses CPython AST for valid
   source and tree-sitter recovery for damaged text. Bytecode is decoded in a
   worker. The standalone vectorizer has stricter admission: valid source under
   Python 3.14 or bytecode matching an inventoried interpreter, with no recovery
   fallback. Programs are not imported or executed to obtain embeddings.
2. **Construct schema-3 graphs.** Source produces module, class, function and
   lambda units, including nested declarations. Ordered AST edges and lexical
   binding candidates preserve structure. Raw evidence and spans are retained
   for provenance. Bytecode combines nested code objects into one graph using
   opcode, containment, sequential and branch edges; the expanded decoder also
   includes exception-table edges where available.
3. **Select and hash features.** Node kind is the core feature. The encoder adds
   the mean of available selected attributes at weight 0.25. Values are hashed
   into 2,048 learned node buckets; edge kind plus position uses 512 relation
   buckets. Hashes preserve repeatable identity, not numeric magnitude or natural
   language meaning, and collisions are possible.
4. **Pass messages and pool.** Each of the frozen checkpoints uses two relational
   layers. A node receives the mean of incoming source vectors plus edge-relation
   embeddings. Linear/ReLU/LayerNorm updates are followed by node-mean pooling,
   projection and L2 normalization. File vectors are the normalized mean of unit
   vectors. Two layers capture local neighborhoods; mean pooling can dilute a
   small but consequential change among many unchanged nodes or units.
5. **Rank by cosine.** Vectors from compatible profiles can be compared by dot
   product after normalization. Checkpoint/schema/profile identities travel with
   the result. Equal dimensions do not establish compatibility or retrieval quality.

The source of truth is [shared_model.py](../codegraph/shared_model.py), especially
`FEATURE_KEYS`, `graph_tensors` and `encode_graph`; source construction lives in
[ast_normalize.py](../codegraph/ast_normalize.py) and
[source_evidence.py](../codegraph/source_evidence.py).

| Evidence | What reaches the frozen encoder | Limitation |
|---|---|---|
| AST structure | Node kinds, AST types, edge relations and positions | No complete execution semantics, SSA, heap analysis or resolved call graph. |
| Source literals | Typed literal identity and category | Hashed identity does not express that 100 is numerically near 101. |
| Names and APIs | Canonical lexical binding and conservative external identities, attribute hashes | Local spelling is deliberately suppressed where resolved; reflection, dynamic dispatch and annotation scopes remain limited. |
| Source scalar fields | Composite `scalar_identity` and selected scope/context evidence | Storing all AST fields does not mean every field is independently modeled. |
| Bytecode | Opcode names and graph structure | Operand values are omitted; recorded `argument_kind` and `code_name` are not in `FEATURE_KEYS`. Different constants, names or `BINARY_OP` operations can collide exactly. |
| Missing evidence | Optional feature masks affect averaging | `graph_tensors` also emits an `availability` tensor, but `encode_graph` does not consume it. Tensor diagnostics can cover more than actual encoder inputs. |

`ProjectEmbeddingPool` and hybrid matching helpers exist in the source, but the
documented frozen file-vector pipeline uses normalized means. Their presence
does not establish a trained project encoder or validated project search.

## What training actually taught the models

The audited schema-3 release contains 8,070 units and 25,687 views from 38
contributing repository URLs (40 manifest records). Repository/fork groups stay
within a split. It contains AST and recovery views, with no direct-bytecode
training views. Security-tool provenance supplies code diversity, not malware
ground-truth labels.

Each checkpoint trained for one CPU epoch with seeds 0/1/2, batch size 32,
AdamW at `1e-3`, 64 dimensions and two layers (184,768 parameters). A multi-positive
contrastive objective pulls distinct views of the same artifact together against
other artifacts in the batch. Of 14,083 eligible train views, 13,653 over 5,267
unit identities entered positive-bearing batches. Training took about 47–53
seconds per seed in the recorded environment; this is not inference throughput.

All 12,235 retained format/rename unit views are tensor-identical to their source
units. This is a useful normalization guarantee, but much of the training and
paired retrieval task is consequently easy. High paired retrieval alone does
not establish that learning adds value. Details and hashes are in the
[training report](baselines/2026-09-11-schema3-capped.md) and
[model cards](modelcards/README.md); implementations are
[training.py](../codegraph/training.py) and [workflow.py](../codegraph/workflow.py).

## Experiment record

This inventory covers the documented measurement families and retained local
iterations. Rerun directories are not independent validation datasets.

| Experiment | Outcome | What it establishes |
|---|---|---|
| [September 5 extended pilot](baselines/2026-09-05-extended-pilot.md) | 12/12 eligible queries retrieved a pair in the top five; only one held-out source file. | Historical pipeline smoke check; later audit found representation and augmentation defects. |
| [September 7 schema-2 capped baseline](baselines/2026-09-07-schema2-capped.md) | 8,066 units / 29,647 views; trained Recall@5 89.64%, hashed 89.61%, untrained 89.54%. Failed its 90% gate. | Early learned model added little. Artifacts are incompatible with schema 3. |
| [Owned synthetic similarity](baselines/2026-09-07-synthetic-similarity.md), [details](baselines/2026-09-07-synthetic-similarity-detail.md) | Ten projects, 60 obfuscations, 111 compile combinations; 63/222 reconstruction attempts passed owned behavior checks. Trained structural top-1 fell from 21/30 to 6/30 with behavior-changing near-copies in the gallery. | Demonstrates sensitivity to the retrieval question and distractors. Reconstructed-source success is not direct-bytecode alignment. |
| [September 8 hard-pair diagnosis](baselines/2026-09-08-hardpair-diagnostics.md) | Eight development families exposed three exact information-loss cases and pooling dilution. | Identified omitted literal/builtin/exception evidence before retraining. Reserved test families were not scored. |
| [September 10 representation and architecture probes](SOURCE-REPRESENTATION-V3.md), [tables](baselines/2026-09-10-source-schema3-detail.md) | All eight development negatives became tensor-distinguishable. Untrained reverse-edge, relation-conditioned and unit-matching probes varied by seed without a consistent winner. | Repairs information availability; does not establish learned behavioral discrimination or select an architecture. |
| [Initial schema-3 rebuild pilot](baselines/2026-09-10-schema3-rebuild-pilot.md) | 255 units / 950 views; 14/49 valid inputs changed tensors on rename. Owned example changed result 3 to 11. | Failed correctness gate despite completed artifact construction; those positives are unsuitable for training. |
| [Repaired pilot](baselines/2026-09-10-transform-repair-pilot.md) | 255 units / 700 views; 284/284 retained transform views invariant; nine gates passed. | Conservative accepted renames/formats preserve evidence; excluded and unchanged inputs are not counted as successes. |
| [Full schema-3 rebuild and training](baselines/2026-09-11-schema3-capped.md) | Seven release gates pass; trained paired Recall@5 97.01–97.23%, untrained 97.14%; behavior top-1 only 2–3/8 development families. | Sounder release and working baselines, without consistent learned gains. |
| [Corpus-derived pilot](SYNTHETIC-SIMILARITY-PLAN.md) | Three selected originals, 120 distinct sources, 1,440 compile attempts; 12 engineering gates passed. Trained source Hit@1 97.50–99.17%; reconstructed 44.90–45.69%; direct bytecode→source 0%. | Proved the evaluation workflow could expand; model scores were not expansion gates. |
| Corpus-derived expansion | 181 selected inputs, 10,136 recipes, 5,519 distinct outputs, 66,228 compile attempts, 33,603 observations. | Completed source/compiled/reconstruction evaluation; per-lane results above. Source queries include controls and edits, not 5,519 independent programs. |
| [Direct bytecode retrieval](BYTECODE-SIMILARITY-PLAN.md) | 9,941 accepted Python 3.14 graphs; 15,702 deduplicated query observations ranked across nine optimization cells, producing 47,106 rankings. | Known-lineage retrieval works in a 179-lineage gallery; all trained models trail hashed/opcode baselines. |
| [Expanded compiled retrieval](COMPILED-RETRIEVAL-PLAN.md) | Seven runtimes × three optimization levels; 159,768 preparation jobs accounted for. Full file cells 69/441, full bundle cells 0/441. | Partial experiment. Runtime smoke tests and all pilot cells passed; full cross-version and project conclusions remain pending. |
| [Standalone vectorizer](../tools/file-vectorizer/README.md) | Independent CLI/API, parity and rejection tests, host Python 3.14 source/bytecode path. | Packaging/implementation evidence; no new model training or retrieval-quality improvement. Seven-runtime release image is pending. |

The expansion recorded 52,728 successful compiles and 13,500 compile gaps;
32,274 distinct binaries yielded 9,941 accepted direct graphs and 22,333 rejected
foreign placeholders with the older decoder. Source scoring has 5,291 valid
queries. Reconstruction scoring has 18,143 observations; token comparison applies
to 14,902. Those differing denominators prevent treating the raw headline
percentages as a paired method comparison. Use the JSON's paired eligible-query
differences and repository-group bootstrap summaries for comparative claims.

The bytecode experiment recorded 21,429/47,106 tensor-equal query/gallery-origin
comparisons and 1,103 exact-binary matches. Thus many successful cases reflect
representation invariance. Same-optimization trained Hit@1 is 93.01–94.34%;
cross-optimization is 88.72–91.51%. Opcode structure achieves 97.73% and 95.74%
respectively. Cosines near 1.0 do not demonstrate behavioral equivalence.

## Expanded runtime pilot: available findings and remaining work

Saved reports under `corpus-runs/compiled-retrieval-v1/` contain 3,528 file-pilot
observations and 2,205 bundle-pilot observations. The file pilot chooses at most
one eligible original/variant per recipe family and repeats them over 441 cells;
the row count is not a count of independent projects. The pilot checks coverage
and execution, so it is too small to select a production model.

In `file-pilot-report.md`, full-available-gallery Hit@1 is 34.78%, 33.48% and
40.84% for seeds 0/1/2, versus 37.84% untrained, 34.67% hashed and 38.72% opcode.
On the smaller paired gallery, trained Hit@1 is 58.13–66.95%, versus 72.56% opcode.
These results make gallery size and cross-runtime difficulty visible. They do
not contradict the narrower 179-lineage Python 3.14 result: both decoder and
evaluation conditions have changed.

In `bundle-pilot-report.md`, top-five-mean aggregation yields trained Hit@1
69.66–74.38% versus 78.46% opcode. Other aggregators perform differently. Bundles
are sampled repository files subjected to removal/injection/mutation, not whole
malware applications. Neither this pilot nor partial full rows establish general
project matching quality.

The November 15 ledger still has 94,567 embeddings, 383,069 full file rows,
69 full file cells and no full bundle cells. `PREPARED.json` and `PILOT.json`
are present, `PARTIAL.json` records an invocation deadline, and `COMPLETE.json`
is absent. The [run plan](COMPILED-RETRIEVAL-PLAN.md) documents resumption. Review
the immutable fingerprints before resuming; a documentation review does not
refresh the input/model/worker checks or complete the pending scoring.

## Boundaries that matter for deployment and interpretation

- **Decoder profiles differ.** The research `_pyc_worker.py` uses the older
  decoder and can produce foreign placeholders, rejected by these benchmarks.
  The expanded `_compiled_worker.py` uses `native-dis-v1` in matching Python
  3.8–3.14 runtimes. The vectorizer vendors an adapted version of that profile.
  Python-version coverage in one path does not imply coverage in another.
- **Quality is measured on inspected development data.** Group splits reduce
  leakage, but repeatedly inspected holdouts are no longer fresh final tests.
  There is no representative malware-family benchmark or validated benign/
  malicious decision threshold. Hard-pair behavior changes can remain related code.
- **Simple baselines remain essential.** The token method counts Python tokens;
  it is not Okapi BM25. No BM25 comparison or embedding-then-BM25 pipeline was
  evaluated. Graph-feature and opcode counts often match or beat trained vectors.
- **Search is a development implementation.** `LocalFaissIndex` stores JSONL
  records and reconstructs an exact `IndexFlatIP` on an unfiltered search when
  FAISS is installed; filtered/fallback search scans candidates. It is not a
  persistent approximate index. Cloud adapter boundaries are not a deployed
  service. See [corpus.py](../codegraph/corpus.py).
- **Large files and archives need additional work.** The vectorizer rejects source
  above 64 KiB or bytecode above 8 MiB and enforces graph limits. It does not unpack
  executables/archives, create project vectors, backfill a database, or resume an
  interrupted JSONL output. Errors carry no vector. Accepted empty source is
  not evidence of useful similarity.
- **Static processing still needs containment.** Standalone child-process limits
  are not hostile multi-tenant isolation. Read the vectorizer's deployment and
  checkpoint-trust requirements. Runtime/container availability is an engineering
  prerequisite, not a model-quality guarantee.

## Evidence locations and next milestones

Committed baseline reports and model cards are the portable evidence. Full local
JSON/SQLite results, weights and binary/source caches are ignored. Principal
completed runs are `schema3-baseline-v1`, `corpus-similarity-v3`,
`corpus-similarity-v3-expansion` and `bytecode-similarity-v3` under `corpus-runs/`.
Earlier `corpus-similarity-v1/v2` have build markers without completed evaluation;
bytecode v1/v2 have completion markers but are earlier iterations, not additional
independent samples. Rebuild pilot v1–v3, hard-pair/source-audit reruns and
similarity v1 are retained diagnostic history; the linked final reports identify
the authoritative repaired runs. `release-v0.1` is invalidated, and uncapped
`release-v0.2` preserves the cap failure rather than a current training release.

The useful next milestones are to finish expanded scoring and publish portable
results with coverage, deliver checkpoint/runtime packaging for a fresh clone,
and evaluate realistic external source and bytecode galleries with matched simple
baselines. A future training experiment needs positives that change encoder
inputs, project-balanced batches and fresh evaluation evidence. Operand-sensitive
bytecode features require a new profile and reevaluation. Million-file serving
requires its own ingestion, index and resource measurements. These are remaining
tasks; the current review neither executes them nor promotes a model.

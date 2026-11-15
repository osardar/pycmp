# Model card: schema-3 baseline seed 0

## Model details

| Field | Value |
|---|---|
| Checkpoint | `corpus-runs/schema3-baseline-v1/model-seed0.pt` |
| SHA-256 | `6977e90753a0a4a166e3ef3ab696b1c9bfe3a0385195585559c066590897f1db` |
| Status | Frozen research baseline; not promoted |
| Created | 2026-09-11 |
| Framework | PyTorch checkpoint format 2 |
| Graph contract | Schema 3, pipeline `graph-v3-fields-bindings-v1-transform-v3` |
| Architecture | `SharedGraphEncoder`, 184,768 parameters, 64 dimensions, 2 relational layers |
| Hash spaces | 2,048 node buckets; 512 relation buckets |
| Seed | 0 |

The encoder maps a semantic program graph to an L2-normalized vector. File-level
retrieval uses the normalized mean of unit vectors and signed cosine similarity.
Inputs are schema-3 graphs, not raw files; source and bytecode must first pass
their corresponding static ingestion path.

## Training data and procedure

Training used the audited capped release `corpus-runs/release-v0.3-capped`, built
from 40 Python-contributing manifest records representing 38 repository URLs.
The release contains 8,070 comparable units and 25,687 views across train,
validation and test. Of 14,083 semantic-eligible training views, 13,653 views
over 5,267 unit identities entered positive-bearing batches; 430 unpaired views
were excluded.

The model received one CPU epoch with batch size 32, AdamW at learning rate
`1e-3`, one Torch thread and multi-positive supervised contrastive loss. Training
took 46.63 seconds and ended at mean loss 0.021856. No direct bytecode views were
present in training. Many accepted formatting and rename positives are
intentionally tensor-identical, so training contains a large easy-invariance
component. Training-source licenses and provenance remain attached to the corpus
manifests; no standalone checkpoint license was recorded.

## Evaluation

| Evaluation | Queries | Hit@1 | Hit@5 | Hit@10 | MRR |
|---|---:|---:|---:|---:|---:|
| Schema-3 paired test retrieval | 3,215 | 94.25% | 97.01% | 98.32% | 95.51% |
| Controlled source variants, 2,270-entry gallery | 5,291 | 97.58% | 98.47% | 98.77% | 97.97% |
| Decompiler reconstructions, 2,270-entry gallery | 18,143 | 41.27% | 45.30% | 46.35% | 43.18% |
| Direct bytecode to source, 2,270-entry gallery | 9,941 | 0.00% | 0.12% | 0.12% | 0.23% |
| Python 3.14 bytecode to bytecode, 179 lineages | 47,106 | 90.15% | 93.30% | 94.32% | 91.65% |

Bytecode-to-bytecode Hit@1 is 93.01% within the same optimization level and
88.72% across optimization levels. Its project/fork-group macro MRR is 90.87%.
The fixed untrained encoder reaches 90.75% overall Hit@1; hashed graphs reach
95.78%, and opcode structure reaches 96.40%. This checkpoint is therefore 0.58
MRR percentage points below the untrained encoder and 4.95/5.44 points below the
hashed/opcode baselines on identical bytecode queries.

On eight already-inspected hard-pair development families, related-code top-1 is
4/8 and behavior-match top-1 is 3/8. This set is too small for a final estimate.
Cosine values are similarities, not probabilities. The reported test and held-out
splits have already been inspected and remain development evidence.

## Intended use

- Rank related source files within a known, provenance-controlled gallery.
- Prioritize Python 3.14 bytecode lineage candidates when both query and gallery
  are accepted direct-bytecode graphs.
- Compare model rankings with hashed, opcode and token baselines during research.
- Support analyst triage with scores, ranks, margins and provenance visible.

## Out-of-scope and unsafe use

- Do not use the checkpoint as a malware detector, benign/malicious classifier,
  behavioral-equivalence oracle, authorship or threat-actor attribution system.
- Do not interpret low similarity as proof that artifacts are unrelated, or high
  similarity as proof of shared behavior.
- Do not use it for autonomous blocking, prosecution, public attribution or other
  high-impact decisions.
- Do not claim source-to-bytecode matching: that evaluated lane failed.
- Do not execute untrusted inputs. Decode compiled artifacts only through the
  constrained worker, and load checkpoints through the schema/profile-validating
  `weights_only=True` loader.

## Limitations and recommendations

In the completed evaluations above, the older decoder rejected Python 3.4, 3.8
and 3.12 as foreign placeholders; only Python 3.14 contributed direct graphs.
The expanded Python 3.8–3.14 experiment uses a different decoder profile and is
still partial; see the [current review](../PROJECT-REVIEW.md). These metrics must
not be transferred to that profile or its standalone vectorizer without further
evaluation. Reconstruction quality depends on
decompiler coverage and is materially weaker than source retrieval. The
bytecode-to-bytecode gallery has only 179 known lineages and may overstate field
performance. Unknown-family calibration, representative malware-family labels,
fresh external tests and behavior-grounded evaluation are absent.

Use this seed only as one retrieval signal. Prefer the simple opcode or hashed
graph baselines for the measured Python 3.14 bytecode task, and require analyst
review. Do not promote this checkpoint without fresh, project-grouped evidence
showing a meaningful learned advantage.

## Provenance

- [Capped release and training report](../baselines/2026-09-11-schema3-capped.md)
- [Corpus-derived source/lane experiment](../SYNTHETIC-SIMILARITY-PLAN.md)
- [Bytecode-to-bytecode measured plan](../BYTECODE-SIMILARITY-PLAN.md)
- [Current project status](../STATUS.md)

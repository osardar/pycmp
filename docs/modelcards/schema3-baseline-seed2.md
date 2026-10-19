# Model card: schema-3 baseline seed 2

## Model details

| Field | Value |
|---|---|
| Checkpoint | `corpus-runs/schema3-baseline-v1/model-seed2.pt` |
| SHA-256 | `13bfabe9df059bc703d73bb19647c4f61f5375326bc012451105a40b81e26ae9` |
| Status | Frozen research baseline; not promoted |
| Created | 2026-09-11 |
| Framework | PyTorch checkpoint format 2 |
| Graph contract | Schema 3, pipeline `graph-v3-fields-bindings-v1-transform-v3` |
| Architecture | `SharedGraphEncoder`, 184,768 parameters, 64 dimensions, 2 relational layers |
| Hash spaces | 2,048 node buckets; 512 relation buckets |
| Seed | 2 |

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
took 52.00 seconds and ended at mean loss 0.025582. No direct bytecode views were
present in training. Many accepted formatting and rename positives are
intentionally tensor-identical, so training contains a large easy-invariance
component. Training-source licenses and provenance remain attached to the corpus
manifests; no standalone checkpoint license was recorded.

## Evaluation

| Evaluation | Queries | Hit@1 | Hit@5 | Hit@10 | MRR |
|---|---:|---:|---:|---:|---:|
| Schema-3 paired test retrieval | 3,215 | 94.18% | 97.11% | 98.29% | 95.49% |
| Controlled source variants, 2,270-entry gallery | 5,291 | 97.54% | 98.36% | 98.64% | 97.92% |
| Decompiler reconstructions, 2,270-entry gallery | 18,143 | 41.89% | 45.11% | 46.33% | 43.76% |
| Direct bytecode to source, 2,270-entry gallery | 9,941 | 0.00% | 0.14% | 0.16% | 0.19% |
| Python 3.14 bytecode to bytecode, 179 lineages | 47,106 | 91.91% | 94.35% | 95.17% | 93.10% |

Bytecode-to-bytecode Hit@1 is 94.34% within the same optimization level and
90.70% across optimization levels. Its project/fork-group macro MRR is 92.36%.
The fixed untrained encoder reaches 90.75% overall Hit@1; hashed graphs reach
95.78%, and opcode structure reaches 96.40%. This checkpoint is 0.87 MRR
percentage points above the untrained encoder but 3.50/3.99 points below the
hashed/opcode baselines on identical bytecode queries.

On eight already-inspected hard-pair development families, related-code top-1 is
4/8 and behavior-match top-1 is 2/8. This set is too small for a final estimate.
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

Python 3.4, 3.8 and 3.12 bytecode currently yields rejected foreign placeholders;
only Python 3.14 direct bytecode is supported. Reconstruction quality depends on
decompiler coverage and is materially weaker than source retrieval. The
bytecode-to-bytecode gallery has only 179 known lineages and may overstate field
performance. Unknown-family calibration, representative malware-family labels,
fresh external tests and behavior-grounded evaluation are absent.

Seed 2 is competitive with seed 1 on same-optimization bytecode retrieval but
still trails both simple structural baselines overall. Use it only as one
analyst-visible retrieval signal and do not promote it without fresh,
project-grouped evidence showing a meaningful learned advantage.

## Provenance

- [Capped release and training report](../baselines/2026-09-11-schema3-capped.md)
- [Corpus-derived source/lane experiment](../SYNTHETIC-SIMILARITY-PLAN.md)
- [Bytecode-to-bytecode measured plan](../BYTECODE-SIMILARITY-PLAN.md)
- [Current project status](../STATUS.md)

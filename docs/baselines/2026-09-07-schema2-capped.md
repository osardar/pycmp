# Schema-2 capped-corpus baseline — 2026-09-07

## Outcome

The first schema-2 baseline **failed the model acceptance gate** and does not
show a meaningful learned advantage. This is still a successful engineering
milestone: it exercises the repaired full-corpus path and prevents an easy-pair
score from being mistaken for classifier quality.

## Release evidence

- Input definition: 41 manifest records, 39 repository URLs.
- Python contributors: 40 records across 38 repository URLs; Certify is the
  documented no-Python record.
- Source/fixture inputs after container curation: 4,302.
- The first complete expansion produced 231,686 views and 63,565 graph units.
  Thirty repositories exceeded 250 units, proving that a source-container cap
  was insufficient.
- Derived graph-unit-capped release: `corpus-runs/release-v0.2-capped`.
- Retained comparable units: 8,066; maximum per repository: 250; over-cap
  repositories: 0.
- Retained views: 29,647 — train 20,821, validation 4,063, test 4,763.
- Referenced graph files: 9,034. Release size: approximately 1.0 GB.
- The completion inventory and every referenced graph checksum verified with
  zero errors.

Generated corpus and model artifacts are intentionally ignored by Git. The
manifests, implementation, tests, and this evidence report are versioned.

## Training

- Shared encoder: 64 dimensions, 2 relational layers.
- Epochs: 1; batch size: 32; seed: 0.
- Eligible semantic training views: 17,088.
- Mean training loss: 0.0186804938.

This bounded CPU configuration is a baseline, not a selected final
hyperparameter setting.

## Full-gallery paired retrieval

There were 3,861 eligible test queries. Slices used the same full gallery.

| Method | Recall@1 | Recall@5 | Recall@10 | MRR |
|---|---:|---:|---:|---:|
| Trained schema-2 GNN | 0.7752 | 0.8964 | 0.9311 | 0.8295 |
| Hashed graph-feature cosine | 0.7752 | 0.8961 | 0.9355 | 0.8282 |
| Seeded untrained shared GNN | 0.7765 | 0.8954 | 0.9363 | 0.8292 |

The trained model missed the predeclared 0.90 Recall@5 gate. Its Recall@5 gain
over the deterministic graph baseline was about 0.00026 and is not practically
meaningful without repeated seeds and confidence intervals.

| Test slice | Recall@5 |
|---|---:|
| Standard production | 0.9680 |
| Defensive security | 0.9013 |
| Analysis fixtures | 0.8252 |
| Formatting | 0.9486 |
| Transformation | 0.9084 |
| Lint | 0.6591 |

## Preliminary threshold and retrieval smoke tests

Validation proxy-pair calibration found threshold 0.8705617 at precision 0.9955
and recall 1.0 over 3,285 positive pairs and 100,000 sampled different-artifact
pairs. Different artifacts are proxy negatives, not genuine unseen families, so
this threshold is not unknown-family calibration.

The file index contains 2,316 source-file embeddings and enforces fingerprint
`d7c9138d…a01c090d`. A known Requests `api.py` query returned an exact match
with embedding score 0.9965. The legacy local `test0` sample had no exact or
structural match; its best score was 0.7760 and it correctly abstained as
`unknown` at the proxy threshold. These two examples validate behavior, not an
accuracy rate.

## Interpretation and next experiment

The graph repair made evaluation credible enough to expose that one epoch of
contrastive training adds almost nothing over fixed graph features. The next
experiment should focus on hard negatives, source↔bytecode/recovery pairs,
feature dropout, project-balanced batches, and lint/fixture labels. Run at least
three fixed seeds and bootstrap by repository. Do not spend the next cycle merely
increasing epochs unless the learned model separates those harder tasks from the
non-learned baselines.

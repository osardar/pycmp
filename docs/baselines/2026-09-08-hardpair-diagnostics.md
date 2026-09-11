# Steps 1–2: hard-pair contract and failure diagnosis

Date: 2026-09-08. Scope: dataset contract and diagnosis only; no retraining,
normalizer/schema changes, index rebuild, or direct-bytecode claim.

## Delivered

- Fourteen new owned families with 42 sources and 42 shared oracle cases.
- Explicit 8/3/3 train/validation/reserved-test split; all descendants stay together.
- Separate related-code and behavior-preservation relations; exact/AST cross-family
  duplicate guards, source/oracle checksum lock, and test-execution/scoring guards.
- Development and validation original/positive oracles pass; every corresponding
  negative has at least one observed counterexample: 33 source-variant checks,
  covering 99 input executions per full oracle-test pass. Reserved-test oracles
  were not executed.
- One frozen-checkpoint diagnostic run on **eight train/development families only**:
  24 pair comparisons and 40 retrieval queries across five identical-gallery methods.
- Per-unit graph/selected-feature/tensor comparisons and actual encoder hooks
  through both message-passing layers, node-mean pooling and final unit vectors.
- First-party suite: 33 tests passed, including the report/gallery round trip,
  test guard, duplicate rejection, behavioral relations and hook cleanup.

The [fixture contract](../../fixtures/hardpairs/README.md) fixes task definitions,
domains, gallery composition, tie handling and diagnosis thresholds. Test sources
are visible, statically parsed and checksummed, but not behavior-checked, embedded
or scored. The three reserved families are a small unscored holdout, not an
externally blinded or statistically sufficient benchmark. The old ten-family
similarity set remains separate regression evidence.

## Findings: where differences disappear

| Family | Earliest observed loss | Largest trained unit L2 | Trained file L2 | Dilution flag |
|---|---|---:|---:|---|
| checkout_charge | observable_change | 0.01804950 | 0.01234228 | false |
| cutoff_gate | observable_change | 0.00976943 | 0.00633152 | false |
| extremum | feature_selection_loss | 0.00000000 | 0.00000000 | false |
| staged_math | observable_change | 0.00823565 | 0.00613267 | false |
| safe_divide | feature_selection_loss | 0.00000000 | 0.00000000 | false |
| helper_change | observable_change | 0.05300684 | 0.01973328 | true |
| literal_limit | normalization_loss | 0.00000000 | 0.00000000 | false |
| parameter_roles | observable_change | 0.08477044 | 0.05166415 | false |

Concrete explanations verified against the implementation and trace output:

1. **Literal evidence is lost during normalization.** In `literal_limit`, changing
   40 to 41 changes the answer at the boundary. The normalizer records only
   `constant_category=number`; graph facts and consumed tensors are identical.
   Training cannot separate these two inputs without a representation change.

2. **Builtin and exception identity is lost during feature selection.** In
   `extremum`, `min` versus `max`, and in `safe_divide`,
   `ZeroDivisionError` versus `ValueError`, identifier hashes differ in graph
   attributes but are not among the encoder's selected features. Consumed tensors,
   hidden layers, unit vectors and file vectors are identical.
   This is not a bucket collision or a lack of training epochs.

3. **Changes to a non-first function survive, but pooling weakens them.**
   `helper_change.adjust` has unit L2 0.05300684; the whole file has L2
   0.01973328, about 37% of that unit distance. Unchanged module/functions contribute
   to equal-weight mean pooling. This is measured attenuation, not proof that
   replacing pooling alone solves retrieval. The report preserves which unit changed.

4. **The other five mutations are observable, not complete information loss.**
   Operators, branch boundaries, statement order and parameter roles change
   consumed tensors and embeddings. For parameter roles the first-layer states
   match, but the second layer differs: binding information does reach the model.
   Their bad ranking therefore cannot simply be blamed on identical input tensors.
   Positive-transform invariance and aggregation still require controlled ablations.

Graph fingerprints ignore source coordinates but retain semantic attributes;
selected-feature fingerprints are computed before bucket hashing. No hash-only
collision was observed in these eight negatives. The code does not silently
remove unsupported evidence to produce a favorable score.

## Same-gallery baseline measurements

Each structural-positive query searches eight originals plus its own family's
behavior-changing near-copy. Behavior ranking accepts only the original; related
ranking also accepts the near-copy. Ties within 1e-7 are conservative.

| Method | Behavior top-1 | Related-code top-1 |
|---|---:|---:|
| Frozen trained GNN | 0/8 | 4/8 |
| Seed-0 untrained GNN | 0/8 | 4/8 |
| Hashed graph features | 0/8 | 4/8 |
| Lexical token counts | 1/8 | 5/8 |
| Operation/API/literal counts | 1/8 | 6/8 |

These are deliberately selected **development failures**, not final accuracy or
evidence that any baseline is ready for classification. With only eight families,
do not interpret one additional hit as a statistically established advantage.
All five methods struggle to prioritize a structural rewrite over a syntactically
close mutation. A related near-copy is not a false positive for the related-code
task, even when it is a negative for behavior preservation.

## Repair handoff before training

The next implementation should address the confirmed representation gaps before
increasing training duration:

- Introduce bounded, named literal-value evidence; preserve category-only/common-core
  comparisons as a separate feature profile.
- Resolve builtin/import-qualified call and exception identities where possible.
  Do **not** simply enable every identifier hash: that would sacrifice local-rename
  invariance and encourage spelling shortcuts. Mark unresolved names explicitly.
- Add tests that each measured counterexample changes the appropriate consumed
  features while safe renaming remains invariant. Version preprocessing and
  rebuild affected graphs/checkpoints/indexes; preserve this baseline.
- Compare current pooling with coverage-aware matched-unit aggregation using the
  second-function control and broader development cases. Keep these as measured
  ablations, not an unvalidated automatic architecture replacement.
- Expand independent development rewrite families, then proceed to the planned
  three-seed hard-pair training experiment. Select on validation only; score reserved
  test families after choices are frozen, and enlarge the final test set before
  drawing general conclusions.

Steps 1 and 2 are complete at the declared contract/diagnosis gates. The confirmed
model defects are **documented, not repaired** by this milestone.

## Reproduction and provenance

```bash
.venv/bin/python -m codegraph.cli hardpair-diagnose \
  --checkpoint corpus-runs/release-v0.2-capped/model-d64-l2-e1.pt \
  --split train --output corpus-runs/hardpairs-diagnosis-new
.venv/bin/python -m unittest discover -s tests -v
```

Completed local run: `corpus-runs/hardpairs-diagnosis-v3/`.
Earlier v1/v2 directories are intermediate diagnostic outputs, retained locally.
The checkpoint SHA256 is `dd7eeefd810effc45aa990a42b317f4b5ab938d84921d1bc5a664494b9af6a9e`.
No artifact was trained from this fixture set.

The [full JSON evidence](2026-09-08-hardpair-diagnostics.json) includes checkpoint,
fixture-lock, manifest and diagnostic-code hashes; Python/Torch versions; selected
source hashes; per-unit L2 distances; all pair cosines, margins and candidate scores.
The source/oracle lock also covers unscored test files for integrity, not evaluation.

Only owned first-party development/validation snippets run locally in oracle
checks. The helper is not an untrusted-code sandbox. No third-party corpus code
or security tool was executed. Existing documentation changes from the prior
status update have been preserved.

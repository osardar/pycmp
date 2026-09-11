# pycmp status

Last updated: 2026-09-10. Latest pushed implementation: `d071b4c`;
subsequent diagnostics and schema-3 repairs are implemented locally, pending commit.

## Schema-3 repair execution update

Typed literals, all available AST fields, recursive unit discovery, canonical
lexical binding candidates and external identity evidence are now implemented.
All eight development negatives change consumed tensors; 18 targeted mutations
and six renaming families have regression coverage. There are 43 passing tests.
Independent three-seed architecture probes are untrained and do not justify a
default architecture change. See the [implementation and measured report](SOURCE-REPRESENTATION-V3.md).

The old schema-2 release remains historical evidence. Its graphs, model and index
are rejected by current compatibility checks. No trained schema-3 release model
exists yet. The next milestone is a new corpus build and controlled training,
after reviewing scope limitations and resource costs. Bytecode worker images need
rebuilding for the new envelope; direct-bytecode alignment remains unvalidated.

## Steps 1–2 execution update

The new hard-pair contract contains 14 families (8 train, 3 validation, 3 reserved
test), 42 sources, explicit relatedness/behavior labels, a checksum lock and
test-scoring guards. Development/validation oracles pass their intended relations;
test families remain unexecuted and unscored. Five-baseline diagnostics on the
eight train families identify one normalization collision (literal values), two
feature-selection collisions (builtin/exception identities), and dilution of a
changed non-first function during file pooling. The suite now has 33 passing tests.

See the [measured diagnosis and repair handoff](baselines/2026-09-08-hardpair-diagnostics.md).
These steps establish evidence; they do not fix the identified model defects or
train a new checkpoint. The immediate next action is the targeted representation
repair described in that report, followed by the planned harder training run.

## Bottom line

pycmp is a working research pipeline for comparing Python artifacts, with a
curated local corpus, a trained shared encoder, indexed files, and reproducible
similarity experiments. It is **not yet a validated behavioral or malware
classifier**. The next milestone is demonstrating useful learned retrieval on
hard transformations and across input lanes—not collecting more repositories.

This is the current status. Earlier milestones and their limitations are retained
in the [audit](AUDIT-2026-09-07.md) and dated baseline reports; historical counts
must not be treated as current release counts.

## Delivered and measured

| Area | Current evidence | Remaining boundary |
|---|---|---|
| Corpus | 41 manifest records / 39 repository URLs; 40 Python-contributing records / 38 URLs; Certify explicitly contributes no Python | License-file evidence, fixture adapters and label quality still need hardening |
| Capped schema-2 release | 8,066 comparable units, 29,647 views, at most 250 units per repository; inventory and graph checksums verified | Durable resume and canonical release naming remain operational work |
| Shared model | Trained 64-dimensional, two-layer encoder; one epoch over 17,088 semantic views | No demonstrated meaningful learned advantage; multi-lane training remains incomplete |
| Retrieval | 2,316 indexed source files; whole-file pooling, cosine scores, exact-match evidence and fingerprint checks | Matched-unit explanations, named-feature profiles and genuine unknown-family calibration remain open |
| Synthetic benchmark | Ten held-out projects, 60 obfuscations, ten behavior-changing near-copies; 1,624 comparisons | Small, correlated evaluation set; not a population-level accuracy estimate |
| Compiled artifacts | 111 project/runtime/optimization variants, 123 module binaries; all bytecode behavior checks and 12 optimization probes passed | Compilation success does not imply decompilation or embedding alignment |
| Decompilation | 63 of 222 attempts yielded complete, behavior-checked reconstructions | No verified Python 3.14 reconstruction in this matrix; only six successes on 3.12 |
| First-party tests | Last completed suite: 43 passing tests | Tests validate implemented behavior, not classifier accuracy |

The ten new similarity projects are separate from the earlier synthetic fixtures
and were not used to train the frozen baseline. Their 60 obfuscations mean two
levels × three seeds × ten projects; seeds change identifiers, not independent
structural recipes.

## What the measurements say

The [capped-corpus baseline](baselines/2026-09-07-schema2-capped.md) reported
Recall@5 of 0.8964 versus 0.8961 for hashed graphs and 0.8954 for the untrained
encoder, missing its 0.90 gate. That historical metric is paired-query hit rate,
not class-label accuracy.

The [synthetic baseline](baselines/2026-09-07-synthetic-similarity.md) is more
diagnostic:

| Query task | Trained top-1 | Hashed-graph top-1 |
|---|---:|---:|
| Light obfuscation, ten-original gallery | 30/30 | 30/30 |
| Structural obfuscation, ten-original gallery | 21/30 | 24/30 |
| Structural obfuscation, plus behavior-changing near-copy | 6/30 | 15/30 |
| Verified decompilation, ten-original gallery | 63/63 | 63/63 |
| Verified decompilation, plus behavior-changing near-copy | 60/63 | 63/63 |

Light obfuscation leaves model inputs identical, so its 100% cosine scores are
normalization invariance, not evidence of learning. Near-copies with changed
behavior can also score almost 100%. That can be useful for finding code
relatives, but cannot establish behavioral equivalence.

The successful decompilations are evaluated through source/recovery ingestion.
They **do not validate direct source↔bytecode-lane alignment**. Sharing an encoder
and vector dimension is necessary infrastructure, not evidence of comparable
meaning across lanes.

The fitted validation threshold of 0.8705617 used different-artifact proxy
negatives. It is not an unknown-family threshold or a calibrated probability.
No operational maliciousness decision should depend on it.

## Next steps, in order

Steps 1–2 below now have an initial implementation and measured report above.
Keep their safeguards active during the remaining representation repairs and
steps 3–5; the new small fixture set is not a complete training corpus.

1. **Freeze the next evaluation contract and create separate development pairs.**
   Preserve these ten projects and their baseline as regression evidence. Since
   their failures now inform development, reserve new untouched project families
   for the next final test. Define code-relatedness separately from behavioral
   discrimination; a changed operator can be a related file but a negative for
   behavior preservation. Add verified positive structural rewrites and controls
   for operators, branches, calls, ordering, exceptions and non-first functions.
   Keep every descendant of a source project in the same split.

2. **Diagnose representation versus learning failures.**
   Check whether each behavior-changing control changes model inputs, which units
   carry that change, and whether pooling dilutes it. Compare token, operation/API,
   hashed-graph and untrained/trained baselines with identical galleries. Repair
   demonstrated information loss before tuning the model; version preprocessing
   and rebuild affected artifacts when needed.

3. **Train and measure a harder shared encoder.**
   Use new, behavior-checked development positives and task-appropriate negatives,
   project-balanced/node-budget batches, and reproducible resumable checkpoints.
   Run at least three training seeds and report project-macro Hit@1/5, MRR,
   positive-versus-negative margins and project-level intervals. The gate is
   credible improvement over the strongest simple baseline on untouched hard
   cases—not more epochs or a lower training loss.

4. **Validate direct bytecode and feature-limited comparisons.**
   Reuse the compiled-artifact generator, but embed bytecode through the actual
   bytecode lane separately from decompiled-source ingestion. Record per-version
   decode, reconstruction and graph-coverage outcomes. Train matched source,
   bytecode and recovery views from development-only owned projects. Define a
   fixed common-core retrieval profile, named optional-feature masking before
   encoding, and compatible profile fingerprints; test feature dropout and
   missing-evidence slices. Do not mask arbitrary dimensions after embedding.
   Unsupported inputs must remain explicit, not scored placeholders.

5. **Make retrieval explainable and calibrate abstention.**
   Expose matched units/spans, query and candidate coverage, raw scores, margins,
   provenance and support limits. Evaluate classification only for explicit labels.
   Fit thresholds on validation families, then measure untouched known and novel
   families, benign lookalikes and incomplete inputs. Report false acceptance,
   precision and abstention coverage with intervals.

Steps 1–3 are the immediate model-quality milestone. Step 4 is required before
claiming lane-independent retrieval quality; step 5 is required before treating
the system as an unknown-file classifier. The detailed gates and remaining
operational work are in the [remediation plan](REMEDIATION-PLAN.md).

## Reproducibility, storage and safety

- Git contains manifests, first-party implementation, synthetic originals and
  generated source variants, oracles, tests, and measured reports.
- Local ignored artifacts include `corpus-runs/release-v0.2-capped/` (corpus,
  checkpoint and index) and `corpus-runs/similarity-v2/` (binaries, tool outputs,
  behavior checks, embeddings and full evaluation JSON). A clone alone does not
  include these artifacts or the Docker images.
- The interrupted schema-1 `corpus-runs/release-v0.1/` is historical diagnostic
  evidence and must not be reused for current model claims.
- Third-party corpus handling remains static-only. Runtime behavior checks execute
  owned synthetic fixtures in constrained containers, not third-party security
  tools or malware.
- Source↔stub comparisons describe interface evidence, not behavioral equivalence.
  Security-repository provenance is not a maliciousness label.

See the [classification strategy](CLASSIFICATION-STRATEGY.md) for the intended
decision semantics and the [fixture guide](../fixtures/similarity/README.md) for
benchmark reproduction commands.

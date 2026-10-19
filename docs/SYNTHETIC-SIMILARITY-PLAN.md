# Corpus-derived synthetic similarity experiment

Date: 2026-09-11. Status: implementation and evaluation plan.

Current status (2026-10-19): implementation, pilot, and automatic source/runtime
expansion are complete as evaluation-only development experiments. See the
[status report](STATUS.md) for coverage and results. The measurements do not
promote a checkpoint or establish behavioral equivalence; the plan below records
the frozen protocol and should be read together with those measured results.

The follow-on direct compiled-code evaluation is specified in the
[bytecode-to-bytecode similarity plan](BYTECODE-SIMILARITY-PLAN.md).

## Purpose and boundaries

This evaluation-only experiment measures how frozen similarity systems respond
when complete, real corpus inputs are changed. It covers source, compiled
bytecode and decompiler reconstructions. It does not retrain or promote a model,
classify why code is similar, expand bytecode normalization, execute corpus code,
or use the reserved hard-pair test families.

The completed schema-3 capped release, its pinned local checkouts, and the three
seed-0/1/2 checkpoints are immutable inputs. Every run records their checksums,
the implementation fingerprint, worker image IDs and the experiment definition.
A changed fingerprint requires a new run directory.

## Gallery and deterministic sampling

The runner reconstructs retained source and fixture inputs from the pinned
checkouts with the release's existing fixture adapters, verifies the recorded
exact-source hash, and parses complete inputs with the typed-AST parser. Inputs
larger than 64 KiB or 10,000 aggregate graph nodes are excluded. Exact-content
duplicates collapse to one gallery entry while every project/repository owner is
retained as provenance. Generated variants never enter the gallery.

Repository/fork split groups remain intact. Repositories and inputs are ordered
by stable hashes and selected round-robin across manifest role and split. The
pilot selects at most ten canonical repositories, balanced where available
across production, analysis-fixture and security tiers, with at most three inputs
per repository. Expansion includes the pilot and raises that limit to five.
Training-seen and held-out-source results are reported separately; inspected
holdouts are development evidence, not fresh final tests.

## Source recipes

Each selected original gets an unchanged control, a formatting control, and the
following families at requested doses 10%, 30% and 60%, with seeds 0, 1 and 2:

| Family | Controlled edit |
|---|---|
| Local renaming | Select bindings accepted by the repaired conservative renamer |
| Literal edits | Change numeric/string expression constants, excluding docstrings, annotations and pattern keys |
| Operator edits | Substitute only fixed supported arithmetic/comparison operators |
| Structural edits | Negate supported `if` conditions and swap nonempty branches |
| Partial overlap | Remove selected top-level function/class definitions while retaining at least one |
| Combined edits | Apply rename, structural and literal stages in that order |

Eligible locations use stable, nested selections for each seed. Each manifest
row records the requested dose, eligible and actual edit counts, changed spans,
stage records, source hashes, status and recipe version. Formatting and renaming
must retain their existing typed-AST/tensor invariance guarantees. Other recipes
must match their declared AST changes and remain parseable. Unsupported,
unchanged, validation-failed and budget-skipped outcomes remain explicit.
Identical output content shares cached compilation and scoring but retains all
recipe provenance and is counted once in aggregate observations. These static
rewrites are related-code queries; no corpus rewrite is described as
behavior-proven or used automatically as an unrelated-code negative.

## Compilation, decoding and reconstruction

Every distinct original/control/transformed source is submitted to the pinned
Python 3.4, 3.8, 3.12 and 3.14 images at optimization levels 0, 1 and 2. The
compile-only worker has no execution/oracle mode. Genuine legacy `.pyo` names are
kept; modern optimized `.pyc` files are not renamed. Syntax/version failures are
compile gaps and optimization remains a separate factor.

Successful binaries are decoded with the existing isolated decoder and passed
to pinned uncompyle6 and pycdc workers. Placeholder foreign-bytecode graphs and
schema-incompatible graphs are rejected rather than scored. Reconstruction is
classified as clean parseable, partial/recovery, unsupported, tool failure,
timeout or invalid output. Decompilation success is static evidence only, not
behavioral equivalence. Direct-bytecode and reconstructed-source scores remain
separate.

Workers are reusable isolated containers where supported, with four concurrent
512 MiB workers, no network, no privileges, read-only staged input, item
deadlines/output caps and cleanup on interruption. Preflight fails rather than
substituting or downloading a missing pinned runtime or tool image.

## Evaluation and reporting

The benchmark CLI exposes `build`, `evaluate` and `run`, always with an explicit
output directory and optional `--resume`. `run` builds and evaluates the pilot,
checks engineering gates, and expands automatically only when they pass.

The job ledger and completion markers make each operation restartable. A single
invocation is limited to 12 hours, 100 GiB of new artifacts and an 8 GiB
coordinator RSS guard. Reaching a limit checkpoints pending work, reports partial
completion and prints the exact resume command; it never writes a successful
completion marker.

Evaluation uses the frozen gallery and all three trained checkpoints, a fixed
seed-0 untrained encoder of matching architecture, hashed graph features, and
the existing token and operation/API baselines when source text exists. Text
baselines are not applicable to direct bytecode. File vectors are normalized
means of unit vectors; unit diagnostics are separate.

Reports include original-relative cosine and unchanged-control delta; original
rank, Hit@1/5/10, MRR and the highest non-lineage margin; exact selected-feature
and tensor equality where correspondence exists; eligibility, deduplication and
lane coverage; and explicit missing-origin/invalid-query conditions. Slices cover
family, actual dose, repository, split, runtime, optimization and lane. Project
macro estimates use 1,000 fixed-seed repository/fork-group bootstrap resamples.
Paired trained-versus-simple-baseline differences use identical eligible queries.
Ties use the existing conservative `1e-7` tolerance. Markdown and compact JSON
are published; generated sources, binaries, reconstructions and caches stay in
ignored run directories.

## Pilot gates

Expansion requires passing implementation tests, release/checkpoint/provenance
and split-group checks, unchanged accepted format/rename invariants, applied
examples from all six mutation families, one owned supported compiled-result
scoring smoke test, cleanup and resume tests, and the configured resource
envelope. Unsupported runtime/tool combinations remain measured gaps. Model
scores are findings, never expansion gates.

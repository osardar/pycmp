# Conservative transform repair and schema-3 pilot

Measured: 2026-09-10. Machine-readable evidence: [pilot JSON](2026-09-10-transform-repair-pilot.json).
This supersedes the correctness blocker in the [initial pilot](2026-09-10-schema3-rebuild-pilot.md),
not its historical measurements. No upstream corpus code was executed.

## Repair

- Renaming edits original UTF-8 source spans for eligible local bindings, using
  lexical binding identities rather than spelling alone. Parameters, imports,
  declarations, exception/pattern captures, class-sensitive names and
  global/nonlocal spellings are excluded. Names mentioned in strings or type
  comments are conservatively protected. Generated names avoid existing identifiers.
- Reflection/dynamic-scope and unverified annotation-scope cases are explicit
  exclusions. Accepted edits must match the intended AST change and preserve
  binding/external-identity correspondence. Comments, literal spelling and line
  structure are not round-tripped through an AST printer during renaming.
- Formatting parses with type comments enabled and requires an identical typed
  AST after printing, including type-ignore locations. Evidence-changing cases
  retain the original and are marked unsupported.
- The builder emits only applied transforms. Unsupported or unchanged cases
  become metadata gaps, not duplicate semantic positives. Accepted views are
  labeled `static_checked`, not behavior-proven.
- The cache pipeline is `graph-v3-fields-bindings-v1-transform-v3`; schema remains
  3. Curation now records release `v0.3`. Pilot fingerprints include transform,
  curation, fixture, semantic and encoder code. Existing runs are preserved.

## Final bounded rerun

Command: `.venv/bin/python -m codegraph.rebuild_pilot --output corpus-runs/schema3-rebuild-pilot-v4`

The pinned selection covers six repositories and eight paths, expanded into 53
curated inputs (49 valid AST inputs). Existing splits are retained; there is no
validation split in this small diagnostic selection. The cap is 50 units per
project. Reserved synthetic test families were not executed or scored.

| Measurement | Final result |
|---|---:|
| Retained units / graph views | 255 / 700 |
| Serialized graph files | 123 |
| Serialized graph bytes | 56,049,841 (53.45 MiB) |
| Build / total profiling time | 3.17 / 7.57 seconds |
| Peak process RSS | 345.88 MiB |
| Applied rename inputs with identical tensors | 10/10 |
| Applied formatting inputs with identical tensors | 45/45 |
| Actual retained transformed-unit views checked | 284/284 |
| First-party tests | 53 passed |

All nine gates pass: rename invariance, formatting invariance, actual generated
transform invariance, curation version, inventory/checksums, repository cap,
graph-file size, memory and elapsed time. Resource limits are post-run measured
gates, not operating-system-enforced limits.

Of the 49 valid inputs, renaming applies to 10, leaves 36 unchanged because no
eligible bindings remain, and excludes three reflective/dynamic-call inputs.
Formatting applies to 45 and excludes four AST-roundtrip evidence changes.
These are not 49 successful rename tests: unsupported/unchanged copies are not
counted as passes. The retained output contains 150 renamed and 134 formatted
unit views; checks compare their serialized graph tensors to the corresponding
source unit by source-artifact identity and qualified name, not traversal order.

The old pilot's 255 units remain, while views fall from 950 to 700 because unsafe
or unchanged augmentation copies are omitted. The owned nested-parameter
regression now returns 3 before and after renaming (previously 3 became 11).
Regression tests cover closures/defaults, lambda/comprehension shadowing, walrus,
global/nonlocal, captures, collisions, Unicode offsets, f-strings, type comments,
explicit exclusions and builder gap accounting. Only owned snippets are executed.

## Limits and next gate

Static binding/AST checks plus owned behavioral tests do not prove equivalence
for arbitrary Python introspection or external code. Conservative exclusions
reduce augmentation coverage; report those gaps in the full build. Tensor
invariance establishes preprocessing consistency, not learned similarity quality.

Proceed with a fresh capped full-corpus schema-3 build, review checksums, per-project
coverage, transform gaps and size budgets, then train controlled multi-seed
baselines against simple methods. No full rebuild, new trained model or retrieval
index was produced here. Schema-2 artifacts remain incompatible; direct-bytecode
alignment and unknown-family calibration remain unvalidated.

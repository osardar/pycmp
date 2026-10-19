# Python source representation, schema 3

Implemented and measured: 2026-09-10. This executes the source-field, unit,
binding, mutation-test and independent architecture-probe milestone. It is not
a claim of complete Python behavioral analysis or a newly trained classifier.

Historical implementation report: subsequent work completed a capped schema-3
rebuild and trained three small, frozen baseline checkpoints. See the
[current status](STATUS.md) and [model cards](modelcards/README.md) for current
availability and measured quality. The results below retain their original
September 2026 milestone scope; forward-looking statements are not current status.

Subsequent [production/fixture rebuild pilot](baselines/2026-09-10-schema3-rebuild-pilot.md)
found corpus-renamer defects not covered by the six owned renaming families below.
Those defects change nested bindings and drop type comments. The representation
repair remains useful evidence; the small invariance suite was not a general
guarantee. The subsequent [transform repair and rerun](baselines/2026-09-10-transform-repair-pilot.md)
passes all pilot gates using conservative binding-aware renaming and typed-AST
format checks. The [full rebuild and small trained baselines](baselines/2026-09-11-schema3-capped.md)
are now complete; the harder-training acceptance gate remains open.

## What changed

1. **All available AST fields are retained.** Every visited AST node stores an
   `ast_fields` mapping. Scalars use typed JSON-safe values; child nodes have type
   markers and ordered graph edges. Null positions and empty lists remain visible.
   Raw identifier spelling is retained as evidence even when excluded from encoding.
   Source coordinates remain provenance, not model features. Comments/whitespace
   are not AST facts and remain in source artifacts rather than semantic features.

2. **Literals retain type and exact value.** Integers use hexadecimal strings to
   avoid integer-to-decimal digit limits; floats use `float.hex()`, complex values
   retain both components, and bytes use hexadecimal. Booleans, None and Ellipsis
   stay distinct. Exact data remains in the graph; `literal_type` and
   `literal_identity` feed bounded embedding tables. Hash equality is useful for
   identity, not numeric distance. Numeric-magnitude and string-content encoders
   are not implemented here. Large values remain inline in graph evidence; their
   embedding token is fixed-size, but graph storage is not fixed-size.

3. **Scalar semantics now reach the encoder.** `scalar_identity` includes import
   modules/symbols/levels, keyword names, formatting conversions, pattern values,
   async-comprehension flags and other previously skipped fields. Constant values
   are deliberately excluded from this aggregate fingerprint and carried through
   their dedicated literal features instead. General scalar evidence is currently
   one composite fingerprint; arbitrary per-field masking is not yet implemented.

4. **Every declaration is discovered recursively.** Functions/classes inside
   conditionals, loops and exception handlers are units. Lambdas are units too.
   Repeated qualified names receive deterministic occurrence suffixes. Parent
   graphs retain declaration headers and `unit_ref` evidence while bodies live in
   their own units. Unit references describe syntactic ownership; they are not a
   resolved interprocedural call graph or proof of definition-time execution.

5. **Bindings are lexical candidates, not a single last-definition dictionary.**
   A two-pass analysis collects declarations before resolving uses. It assigns
   canonical scope/slot identities, handles parameters, imports, closures,
   global/nonlocal directives, class-scope skipping for methods, comprehension
   scopes and their outermost iterable, and comprehension assignment expressions.
   Safe local and import-alias renames preserve consumed tensor identities.

6. **External identities are conservative.** Builtins are distinguished unless
   shadowed. Unambiguous unconditional imports provide lexical module/symbol
   candidates, including attribute paths. Reassigned aliases are not treated as
   resolved imports. Star imports and detected eval/exec scopes remain dynamically
   unresolved. Every resolution is labeled a lexical candidate, not a runtime
   guarantee; monkey-patching, late rebinding and arbitrary dispatch remain open.

7. **Data-flow claims are qualified.** Parameter references retain `def_use` edges;
   other same-binding declarations connect via `may_def_use`, without claiming a
   reaching-definition solution. Branches are not merged using SSA, exception
   cleanup/lifetime is not proven, and neither CFG nor heap/alias analysis is added.
   Candidate edges can grow with repeated definitions and uses; full-corpus
   resource sizing still needs measurement before a large rebuild.

## Field policy and remaining unresolved semantics

The [runtime inventory](AST-FIELD-INVENTORY-3.14.json) lists each AST class/field,
its storage policy and encoding policy. The generator uses the installed Python
AST definitions, and tests check that no declared field lacks a policy. The
committed inventory is for the measured Python 3.14 runtime, not every historical
or future Python grammar.

Locally bound spellings are excluded from the scalar fingerprint and represented
through canonical bindings where supported. The raw fields still retain them.
Type-parameter and version-dependent annotation scopes are explicitly unresolved:
their fields are stored, but this implementation does not claim compiler-complete
typing-scope resolution or type-parameter renaming invariance. Metadata also marks
runtime dispatch and branch-sensitive data flow as unresolved analyses.

This separates **preserved evidence**, **selected features**, and **resolved
semantics**. Preserving every AST field does not imply that the GNN interprets
every Python construct correctly.

## Validation results

- 43 first-party tests pass, including the build/train/index/search smoke test.
- 18 targeted mutation pairs produce different consumed tensors: literal value
  and type, bytes/text, booleans, keywords, import module/symbol/level, formatting,
  conditional bodies, builtins, exceptions, match singletons, async comprehensions,
  global targets, parameter roles, decorators and defaults.
- Six renaming families preserve tensors: locals/functions, import aliases,
  closures, comprehensions, nonlocal bindings and a shadowed eval parameter.
- Declaration discovery, shadowing, binding resolution, JSON round trips,
  field coverage, and schema-2 rejection have dedicated tests.
- All eight development hard-pair negatives now change graph facts, selected
  features and consumed tensors. The three formerly exact collisions are repaired.
- The three reserved hard-pair test families were not executed or scored.

## Independent architecture probes

The production encoder defaults were not replaced. A separate experiment tests
one change at a time with the same initial weights and nine-candidate development
gallery within each of seeds 0, 1 and 2:

| Probe | Seed 0 top-1 / 8 | Seed 1 | Seed 2 |
|---|---:|---:|---:|
| Existing message/mean-pooling architecture | 2 | 4 | 0 |
| Reverse AST edges added | 2 | 3 | 1 |
| Relation-conditioned source messages | 3 | 1 | 1 |
| Symmetric best-unit matching instead of file mean cosine | 2 | 4 | 1 |

All encoders are **untrained**. These are wiring/sensitivity probes, not trained
ablations, selected architectures, or measured improvement over the old trained
checkpoint. Symmetric best-unit matching includes every unit but permits many-to-one
matches; it does not solve boilerplate dominance. Results vary by seed. Controlled
trained experiments, stronger coverage scoring and project-level intervals remain
necessary before choosing any architecture change. Deeper message passing was not
tested in this milestone.

- [Detailed tables](baselines/2026-09-10-source-schema3-detail.md)
- [Full hashes, input comparisons and architecture results](baselines/2026-09-10-source-schema3.json)

## Compatibility and reproduction

Graph schema is now **3**, the graph-pipeline identity changes, and the corpus
release version is `v0.3`. Model loaders reject schema-2 checkpoints; graph readers
reject schema-2 graphs. Index fingerprints include the new schema and feature keys.
Three schema-3 baseline checkpoints were later trained; they are small research
baselines, not promoted release models. Their local weight files are not tracked.
Existing schema-2 corpus, model, index and reports are preserved unchanged as
historical evidence.

```bash
.venv/bin/python -m codegraph.cli source-audit \
  --output corpus-runs/source-schema3-audit-new
.venv/bin/python -m unittest discover -s tests -v
```

The audit uses owned train/development fixtures only and needs no checkpoint.
It writes a field inventory, report JSON and Markdown. The measured run is
`corpus-runs/source-schema3-audit-v2/`; output directories are never overwritten.

Do not relabel old graphs/checkpoints as schema 3. Historical similarity commands
referencing the frozen schema-2 checkpoint must use matching historical source
code; they intentionally fail under the new loader. The schema bump does not
establish cross-lane alignment. See the current vectorizer documentation for its
separate packaging and runtime constraints.

## Next milestone

At the time of this report, the next milestone was a full corpus rebuild and
schema-3 baseline training. That rebuild and initial training are now complete;
harder project-balanced training, named optional-feature profiles, CFG/data flow,
calibrated unknown rejection, and improved cross-lane retrieval remain separate
research questions. Consult the current status before treating any historical
“next milestone” statement as active work.

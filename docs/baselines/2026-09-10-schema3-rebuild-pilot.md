# Schema-3 rebuild pilot — 2026-09-10

## Outcome

The existing schema-3 repairs and diagnostics were committed as `4fbf20f` before
this pilot. The bounded rebuild completed and passed its resource/integrity gates,
but **failed the rename-invariance gate**. Do not launch the full corpus rebuild
or train on this pilot's generated positives until the transformation issues below
are fixed. `COMPLETE.json` means artifact construction completed, not model/data
quality acceptance.

## Scope and reproducibility

[The pinned pilot manifest](../../corpus/schema3-pilot.jsonl) selects eight files
from six existing cached repositories: Requests, Pydantic, Hypothesis, Impacket,
Black fixtures and MyPy fixtures. It exercises larger production modules,
conditional/nested definitions, pattern matching and fixture extraction.
No repository was added or fetched, no third-party dependencies were installed,
and no third-party project code was executed. The legacy checkouts were verified
against their revision/origin/cleanliness before reuse.

Partitions are inherited from the completed schema-2 release, not reassigned to
make this small sample balanced. There are train/test records and no validation
records; this is an operational pilot, not a training/model-selection experiment.
The reserved synthetic test families are untouched.

```bash
.venv/bin/python -m codegraph.rebuild_pilot \
  --manifest corpus/schema3-pilot.jsonl \
  --checkouts corpus-runs/checkouts-v0.2 \
  --legacy corpus-runs/release-v0.2 \
  --output corpus-runs/schema3-rebuild-pilot-new
```

The command refuses a preexisting output directory or missing local checkouts.
The completed measured run is `corpus-runs/schema3-rebuild-pilot-v2/`; v1 is the
earlier run without detailed transformation attribution. Both remain ignored/local.
No trained model or index was created. The pilot's small model instance supplies
hash-bucket settings for tensor comparisons only; no embeddings are scored.

## Measured size, time and memory

| Measurement | Result |
|---|---:|
| Source containers | 8 |
| Curated inputs after extraction/capping | 53 |
| Comparable retained units | 255 |
| Retained graph views | 950 |
| Graph files | 163 |
| Nodes across retained views | 120,888 |
| Edges across retained views | 132,112 |
| Serialized graph bytes | 71,873,975 (68.54 MiB) |
| Largest graph file | 8,339,655 bytes (7.95 MiB) |
| Largest individual graph | 14,337 nodes; maximum edges across graphs: 14,336 |
| Build time | 3.99 seconds |
| Build + integrity verification + source profiling | 7.07 seconds |
| Process peak RSS | 372,473,856 bytes (355.22 MiB) |

RSS includes Python/Torch imports, build, verification and profiling in the pilot
process. It excludes child Git processes and is not whole-system memory. Timing
uses existing warm local checkouts and excludes preflight Git checks/import time.
Resource budgets are measured acceptance gates, not OS-enforced memory/time limits.

The repository unit counts are Pydantic 50, Requests 41, MyPy 50, Black 14,
Hypothesis 50, Impacket 50; all meet the pilot's 50-unit cap. Before capping,
1,546 views were generated, so the cap does not bound transient build work.
937 retained views use AST ingestion and 13 use recovery.

Eight curated inputs had corresponding historical schema-2 source graph files.
Their total serialized size grew from 11,437,499 to 25,125,334 bytes (2.20×),
with 276 old units versus 304 new units. This includes expanded unit discovery,
not just a fixed-unit serialization comparison. No schema-2 timing baseline was
rerun. This small convenience sample cannot predict full-corpus peak memory or
prove the absence of pathological binding-edge growth.

## Correctness findings

Of 53 curated inputs, 49 parsed as valid AST inputs and were checked for renamed
tensor identity. **35 passed; 14 differed.** Four non-AST inputs were not tested
for rename invariance. A mismatch is a diagnostic, not automatically proof of a
runtime behavior change.

The detailed report attributes the mismatches as follows (categories overlap):

- **12 inputs lose type comments or type-ignore evidence.** The transformation
  parser uses `ast.parse` without `type_comments=True`, whereas schema-3 ingestion
  preserves these facts. This affects nine MyPy cases plus Pydantic, Requests and
  Hypothesis. It is particularly consequential for typing/diagnostic labels even
  when runtime behavior is unchanged.
- **Four inputs show binding-identity changes.** Pydantic and Hypothesis include
  nested-scope changes. Black's input/output fixture contains dynamic resolution,
  where renamed unresolved spellings remain different evidence. Those two Black
  mismatches alone do not establish a behavioral defect.
- **The local renamer is unsafe for nested shadowing.** Its nested-scope walk and
  fallback through outer rename maps do not reliably respect inner parameters.
  The richer representation exposes the difference; this is not justification
  for masking that evidence to make the gate pass.

The following owned snippet was executed locally, then transformed using the
current `renamed_view`. No upstream code was executed:

```python
def outer():
    value = 10
    def inner(value):
        return value + 1
    return inner(2)
```

Original result: **3**. Transformed result: **11**. The transformed inner body
reads `local_0 + 1`, capturing the renamed outer variable instead of its parameter.
This proves that some generated "positive" pairs can change behavior. The
builder currently still marks eligible renamed AST views as semantic-trainable;
the failed pilot must not be mistaken for an approved training release.

An additional metadata inconsistency remains: the curation report defaults to
release label `v0.2`, although COMPLETE and graph records correctly declare schema
3 and the new pipeline identity. Fix that label before publishing a schema-3
release; do not infer schema from the stale descriptive field.

## Gates and next action

| Gate declared in the pilot definition | Outcome |
|---|---|
| Inventory and every graph checksum/validation | Pass |
| Maximum 50 units per repository | Pass |
| Under 300 seconds | Pass |
| Under 1 GiB process peak RSS | Pass |
| Graph files under 32 MiB | Pass |
| Valid-source rename tensor invariance | **Fail** |

Next implementation: replace or restrict the scope-unsafe renamer, preserve
type-comment evidence in transformations, and explicitly label/exclude unsupported
dynamic cases instead of treating them as verified semantic positives. Add the
owned shadowing counterexample as a preservation regression, then rerun this same
pilot in a fresh output directory. Also correct the stale curation release label.
The broader corpus rebuild and three-seed training remain deferred until those
checks pass or exclusions have a reviewed, evidence-backed policy.

The first-party suite has **46 passing tests** after adding pilot definition,
overwrite-protection and type-comment diagnostic checks. These do not mean the
unsafe renamer has been repaired; this task measured and documented it.

[Full JSON evidence](2026-09-10-schema3-rebuild-pilot.json) contains code/manifest
hashes, per-input timings and sizes, historical comparison paths/hashes, changed
units and binding examples, budgets and gate outcomes. The manifest, pilot code,
tests and report are versioned; generated graphs remain ignored/local.

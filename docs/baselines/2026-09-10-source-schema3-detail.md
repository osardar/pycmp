# Schema-3 source evidence audit

Development only; all encoders are untrained. No reserved test scoring.

| Family | Graph changed | Selected features changed | Tensors changed |
|---|---|---|---|
| checkout_charge | True | True | True |
| cutoff_gate | True | True | True |
| extremum | True | True | True |
| staged_math | True | True | True |
| safe_divide | True | True | True |
| helper_change | True | True | True |
| literal_limit | True | True | True |
| parameter_roles | True | True | True |

## One-factor architecture probes

Identical initial weights and galleries within each seed. No trained-quality claim or architecture selection.

| Seed | Variant | Behavior top-1 / 8 | Mean margin |
|---:|---|---:|---:|
| 0 | baseline | 2 | -0.000304 |
| 0 | reverse_ast | 2 | 0.000018 |
| 0 | conditioned_relation | 3 | -0.000298 |
| 0 | unit_matching | 2 | -0.000220 |
| 1 | baseline | 4 | 0.000623 |
| 1 | reverse_ast | 3 | 0.000526 |
| 1 | conditioned_relation | 1 | 0.000265 |
| 1 | unit_matching | 4 | 0.000831 |
| 2 | baseline | 0 | -0.000669 |
| 2 | reverse_ast | 1 | -0.000744 |
| 2 | conditioned_relation | 1 | -0.000683 |
| 2 | unit_matching | 1 | -0.000681 |

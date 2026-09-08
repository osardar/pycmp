# Synthetic project similarity experiment

Scores are 100 × cosine similarity, not probabilities or equivalence percentages.
The checkpoint was frozen; these projects were not used for training.

Checkpoint SHA256: `dd7eeefd810effc45aa990a42b317f4b5ab938d84921d1bc5a664494b9af6a9e`.

## Reconstruction coverage

| Status | Project/runtime/optimization/tool attempts |
|---|---:|
| behavior_mismatch | 9 |
| invalid_output | 63 |
| partial | 3 |
| success | 63 |
| unsupported | 84 |

## Original versus variants

Means below include only behavior-checked source variants and complete successful reconstructions.
Negative controls are intentionally behavior-changing. Missing successful reconstructions are N/A.

| Project | Decompiled % | Light % | Structural % | Negative % |
|---|---:|---:|---:|---:|
| async_queue | 99.23 | 100.00 | 87.44 | 99.99 |
| codec | 100.00 | 100.00 | 63.19 | 84.28 |
| dependencies | 99.72 | 100.00 | 75.37 | 85.65 |
| dispatch | 99.96 | 100.00 | 67.36 | 99.99 |
| events | 100.00 | 100.00 | 87.15 | 100.00 |
| inventory | 98.67 | 100.00 | 81.37 | 100.00 |
| invoice | 100.00 | 100.00 | 71.38 | 100.00 |
| memo | 100.00 | 100.00 | 80.35 | 99.99 |
| transaction | 100.00 | 100.00 | 90.57 | 97.23 |
| typed_router | N/A | 100.00 | 77.47 | 88.54 |

## Pairwise detail

Each row retains runtime, optimization, tool and obfuscation seed in its artifact paths.
Scores for failed/partial reconstructions are diagnostic only. See JSON for file/unit coverage.

| Project | Left | Right | Status | Behavior | GNN % | Untrained % | Graph % | Identical inputs |
|---|---|---|---|---|---:|---:|---:|---|
| invoice | invoice/original | invoice/obfuscated-light-0 | source | True | 100.00 | 100.00 | 100.00 | True |
| invoice | invoice/original | invoice/obfuscated-light-1 | source | True | 100.00 | 100.00 | 100.00 | True |
| invoice | invoice/original | invoice/obfuscated-light-2 | source | True | 100.00 | 100.00 | 100.00 | True |
| invoice | invoice/original | invoice/obfuscated-structural-0 | source | True | 71.38 | 96.16 | 96.75 | False |
| invoice | invoice/original | invoice/obfuscated-structural-1 | source | True | 71.38 | 96.16 | 96.75 | False |
| invoice | invoice/original | invoice/obfuscated-structural-2 | source | True | 71.38 | 96.16 | 96.75 | False |
| invoice | invoice/original | invoice/negative | source | False | 100.00 | 100.00 | 100.00 | False |
| inventory | inventory/original | inventory/obfuscated-light-0 | source | True | 100.00 | 100.00 | 100.00 | True |
| inventory | inventory/original | inventory/obfuscated-light-1 | source | True | 100.00 | 100.00 | 100.00 | True |
| inventory | inventory/original | inventory/obfuscated-light-2 | source | True | 100.00 | 100.00 | 100.00 | True |
| inventory | inventory/original | inventory/obfuscated-structural-0 | source | True | 81.37 | 98.70 | 99.03 | False |
| inventory | inventory/original | inventory/obfuscated-structural-1 | source | True | 81.37 | 98.70 | 99.03 | False |
| inventory | inventory/original | inventory/obfuscated-structural-2 | source | True | 81.37 | 98.70 | 99.03 | False |
| inventory | inventory/original | inventory/negative | source | False | 100.00 | 100.00 | 99.99 | False |
| events | events/original | events/obfuscated-light-0 | source | True | 100.00 | 100.00 | 100.00 | True |
| events | events/original | events/obfuscated-light-1 | source | True | 100.00 | 100.00 | 100.00 | True |
| events | events/original | events/obfuscated-light-2 | source | True | 100.00 | 100.00 | 100.00 | True |
| events | events/original | events/obfuscated-structural-0 | source | True | 87.15 | 98.29 | 98.78 | False |
| events | events/original | events/obfuscated-structural-1 | source | True | 87.15 | 98.29 | 98.78 | False |
| events | events/original | events/obfuscated-structural-2 | source | True | 87.15 | 98.29 | 98.78 | False |
| events | events/original | events/negative | source | False | 100.00 | 100.00 | 99.99 | False |
| transaction | transaction/original | transaction/obfuscated-light-0 | source | True | 100.00 | 100.00 | 100.00 | True |
| transaction | transaction/original | transaction/obfuscated-light-1 | source | True | 100.00 | 100.00 | 100.00 | True |
| transaction | transaction/original | transaction/obfuscated-light-2 | source | True | 100.00 | 100.00 | 100.00 | True |
| transaction | transaction/original | transaction/obfuscated-structural-0 | source | True | 90.57 | 98.76 | 99.21 | False |
| transaction | transaction/original | transaction/obfuscated-structural-1 | source | True | 90.57 | 98.76 | 99.21 | False |
| transaction | transaction/original | transaction/obfuscated-structural-2 | source | True | 90.57 | 98.76 | 99.21 | False |
| transaction | transaction/original | transaction/negative | source | False | 97.23 | 99.71 | 99.54 | False |
| memo | memo/original | memo/obfuscated-light-0 | source | True | 100.00 | 100.00 | 100.00 | True |
| memo | memo/original | memo/obfuscated-light-1 | source | True | 100.00 | 100.00 | 100.00 | True |
| memo | memo/original | memo/obfuscated-light-2 | source | True | 100.00 | 100.00 | 100.00 | True |
| memo | memo/original | memo/obfuscated-structural-0 | source | True | 80.35 | 98.37 | 99.25 | False |
| memo | memo/original | memo/obfuscated-structural-1 | source | True | 80.35 | 98.37 | 99.25 | False |
| memo | memo/original | memo/obfuscated-structural-2 | source | True | 80.35 | 98.37 | 99.25 | False |
| memo | memo/original | memo/negative | source | False | 99.99 | 100.00 | 99.97 | False |
| codec | codec/original | codec/obfuscated-light-0 | source | True | 100.00 | 100.00 | 100.00 | True |
| codec | codec/original | codec/obfuscated-light-1 | source | True | 100.00 | 100.00 | 100.00 | True |
| codec | codec/original | codec/obfuscated-light-2 | source | True | 100.00 | 100.00 | 100.00 | True |
| codec | codec/original | codec/obfuscated-structural-0 | source | True | 63.19 | 96.45 | 95.77 | False |
| codec | codec/original | codec/obfuscated-structural-1 | source | True | 63.19 | 96.45 | 95.77 | False |
| codec | codec/original | codec/obfuscated-structural-2 | source | True | 63.19 | 96.45 | 95.77 | False |
| codec | codec/original | codec/negative | source | False | 84.28 | 98.47 | 97.06 | False |
| dispatch | dispatch/original | dispatch/obfuscated-light-0 | source | True | 100.00 | 100.00 | 100.00 | True |
| dispatch | dispatch/original | dispatch/obfuscated-light-1 | source | True | 100.00 | 100.00 | 100.00 | True |
| dispatch | dispatch/original | dispatch/obfuscated-light-2 | source | True | 100.00 | 100.00 | 100.00 | True |
| dispatch | dispatch/original | dispatch/obfuscated-structural-0 | source | True | 67.36 | 96.11 | 98.42 | False |
| dispatch | dispatch/original | dispatch/obfuscated-structural-1 | source | True | 67.36 | 96.11 | 98.42 | False |
| dispatch | dispatch/original | dispatch/obfuscated-structural-2 | source | True | 67.36 | 96.11 | 98.42 | False |
| dispatch | dispatch/original | dispatch/negative | source | False | 99.99 | 100.00 | 99.90 | False |
| dependencies | dependencies/original | dependencies/obfuscated-light-0 | source | True | 100.00 | 100.00 | 100.00 | True |
| dependencies | dependencies/original | dependencies/obfuscated-light-1 | source | True | 100.00 | 100.00 | 100.00 | True |
| dependencies | dependencies/original | dependencies/obfuscated-light-2 | source | True | 100.00 | 100.00 | 100.00 | True |
| dependencies | dependencies/original | dependencies/obfuscated-structural-0 | source | True | 75.37 | 98.26 | 98.71 | False |
| dependencies | dependencies/original | dependencies/obfuscated-structural-1 | source | True | 75.37 | 98.26 | 98.71 | False |
| dependencies | dependencies/original | dependencies/obfuscated-structural-2 | source | True | 75.37 | 98.26 | 98.71 | False |
| dependencies | dependencies/original | dependencies/negative | source | False | 85.65 | 99.10 | 99.11 | False |
| async_queue | async_queue/original | async_queue/obfuscated-light-0 | source | True | 100.00 | 100.00 | 100.00 | True |
| async_queue | async_queue/original | async_queue/obfuscated-light-1 | source | True | 100.00 | 100.00 | 100.00 | True |
| async_queue | async_queue/original | async_queue/obfuscated-light-2 | source | True | 100.00 | 100.00 | 100.00 | True |
| async_queue | async_queue/original | async_queue/obfuscated-structural-0 | source | True | 87.44 | 98.68 | 99.24 | False |
| async_queue | async_queue/original | async_queue/obfuscated-structural-1 | source | True | 87.44 | 98.68 | 99.24 | False |
| async_queue | async_queue/original | async_queue/obfuscated-structural-2 | source | True | 87.44 | 98.68 | 99.24 | False |
| async_queue | async_queue/original | async_queue/negative | source | False | 99.99 | 100.00 | 99.99 | False |
| typed_router | typed_router/original | typed_router/obfuscated-light-0 | source | True | 100.00 | 100.00 | 100.00 | True |
| typed_router | typed_router/original | typed_router/obfuscated-light-1 | source | True | 100.00 | 100.00 | 100.00 | True |
| typed_router | typed_router/original | typed_router/obfuscated-light-2 | source | True | 100.00 | 100.00 | 100.00 | True |
| typed_router | typed_router/original | typed_router/obfuscated-structural-0 | source | True | 77.47 | 97.67 | 98.61 | False |
| typed_router | typed_router/original | typed_router/obfuscated-structural-1 | source | True | 77.47 | 97.67 | 98.61 | False |
| typed_router | typed_router/original | typed_router/obfuscated-structural-2 | source | True | 77.47 | 97.67 | 98.61 | False |
| typed_router | typed_router/original | typed_router/negative | source | False | 88.54 | 99.11 | 99.51 | False |
| async_queue | async_queue/original | async_queue/python-3.12/opt-0/uncompyle6 | unsupported | False | 30.05 | 34.19 | 0.52 | False |
| async_queue | async_queue/original | async_queue/python-3.12/opt-0/pycdc | unsupported | False | 54.10 | 87.95 | 90.18 | False |
| async_queue | async_queue/original | async_queue/python-3.12/opt-1/uncompyle6 | unsupported | False | 30.05 | 34.19 | 0.52 | False |
| async_queue | async_queue/original | async_queue/python-3.12/opt-1/pycdc | unsupported | False | 54.10 | 87.95 | 90.18 | False |
| async_queue | async_queue/original | async_queue/python-3.12/opt-2/uncompyle6 | unsupported | False | 30.05 | 34.19 | 0.52 | False |
| async_queue | async_queue/original | async_queue/python-3.12/opt-2/pycdc | unsupported | False | 54.10 | 87.95 | 90.18 | False |
| async_queue | async_queue/original | async_queue/python-3.14/opt-0/uncompyle6 | unsupported | False | 29.49 | 35.58 | 0.52 | False |
| async_queue | async_queue/original | async_queue/python-3.14/opt-0/pycdc | invalid_output | False | N/A | N/A | N/A | False |
| async_queue | async_queue/original | async_queue/python-3.14/opt-1/uncompyle6 | unsupported | False | 29.49 | 35.58 | 0.52 | False |
| async_queue | async_queue/original | async_queue/python-3.14/opt-1/pycdc | invalid_output | False | N/A | N/A | N/A | False |
| async_queue | async_queue/original | async_queue/python-3.14/opt-2/uncompyle6 | unsupported | False | 29.49 | 35.58 | 0.52 | False |
| async_queue | async_queue/original | async_queue/python-3.14/opt-2/pycdc | invalid_output | False | N/A | N/A | N/A | False |
| async_queue | async_queue/original | async_queue/python-3.8/opt-0/uncompyle6 | success | True | 99.23 | 99.97 | 99.99 | False |
| async_queue | async_queue/original | async_queue/python-3.8/opt-0/pycdc | unsupported | False | 83.13 | 97.98 | 98.83 | False |
| async_queue | async_queue/original | async_queue/python-3.8/opt-1/uncompyle6 | success | True | 99.23 | 99.97 | 99.99 | False |
| async_queue | async_queue/original | async_queue/python-3.8/opt-1/pycdc | unsupported | False | 83.13 | 97.98 | 98.83 | False |
| async_queue | async_queue/original | async_queue/python-3.8/opt-2/uncompyle6 | success | True | 99.23 | 99.97 | 99.99 | False |
| async_queue | async_queue/original | async_queue/python-3.8/opt-2/pycdc | unsupported | False | 83.13 | 97.98 | 98.83 | False |
| codec | codec/original | codec/python-3.12/opt-0/uncompyle6 | unsupported | False | 31.66 | 33.45 | 0.00 | False |
| codec | codec/original | codec/python-3.12/opt-0/pycdc | unsupported | False | 78.59 | 98.69 | 99.48 | False |
| codec | codec/original | codec/python-3.12/opt-1/uncompyle6 | unsupported | False | 31.66 | 33.45 | 0.00 | False |
| codec | codec/original | codec/python-3.12/opt-1/pycdc | unsupported | False | 78.59 | 98.69 | 99.48 | False |
| codec | codec/original | codec/python-3.12/opt-2/uncompyle6 | unsupported | False | 31.66 | 33.45 | 0.00 | False |
| codec | codec/original | codec/python-3.12/opt-2/pycdc | unsupported | False | 78.59 | 98.69 | 99.48 | False |
| codec | codec/original | codec/python-3.14/opt-0/uncompyle6 | unsupported | False | 30.74 | 35.09 | 0.00 | False |
| codec | codec/original | codec/python-3.14/opt-0/pycdc | invalid_output | False | N/A | N/A | N/A | False |
| codec | codec/original | codec/python-3.14/opt-1/uncompyle6 | unsupported | False | 30.74 | 35.09 | 0.00 | False |
| codec | codec/original | codec/python-3.14/opt-1/pycdc | invalid_output | False | N/A | N/A | N/A | False |
| codec | codec/original | codec/python-3.14/opt-2/uncompyle6 | unsupported | False | 30.74 | 35.09 | 0.00 | False |
| codec | codec/original | codec/python-3.14/opt-2/pycdc | invalid_output | False | N/A | N/A | N/A | False |
| codec | codec/original | codec/python-3.4/opt-0/uncompyle6 | success | True | 100.00 | 100.00 | 100.00 | True |
| codec | codec/original | codec/python-3.4/opt-0/pycdc | invalid_output | False | 29.69 | 40.22 | 0.00 | False |
| codec | codec/original | codec/python-3.4/opt-1/uncompyle6 | success | True | 100.00 | 100.00 | 100.00 | True |
| codec | codec/original | codec/python-3.4/opt-1/pycdc | invalid_output | False | 29.69 | 40.22 | 0.00 | False |
| codec | codec/original | codec/python-3.4/opt-2/uncompyle6 | success | True | 100.00 | 100.00 | 100.00 | True |
| codec | codec/original | codec/python-3.4/opt-2/pycdc | invalid_output | False | 29.69 | 40.22 | 0.00 | False |
| codec | codec/original | codec/python-3.8/opt-0/uncompyle6 | success | True | 100.00 | 100.00 | 100.00 | True |
| codec | codec/original | codec/python-3.8/opt-0/pycdc | invalid_output | False | 29.39 | 42.05 | 0.00 | False |
| codec | codec/original | codec/python-3.8/opt-1/uncompyle6 | success | True | 100.00 | 100.00 | 100.00 | True |
| codec | codec/original | codec/python-3.8/opt-1/pycdc | invalid_output | False | 29.39 | 42.05 | 0.00 | False |
| codec | codec/original | codec/python-3.8/opt-2/uncompyle6 | success | True | 100.00 | 100.00 | 100.00 | True |
| codec | codec/original | codec/python-3.8/opt-2/pycdc | invalid_output | False | 29.39 | 42.05 | 0.00 | False |
| dependencies | dependencies/original | dependencies/python-3.12/opt-0/uncompyle6 | unsupported | False | 19.71 | 33.55 | 1.10 | False |
| dependencies | dependencies/original | dependencies/python-3.12/opt-0/pycdc | success | True | 99.72 | 99.99 | 99.99 | False |
| dependencies | dependencies/original | dependencies/python-3.12/opt-1/uncompyle6 | unsupported | False | 19.71 | 33.55 | 1.10 | False |
| dependencies | dependencies/original | dependencies/python-3.12/opt-1/pycdc | success | True | 99.72 | 99.99 | 99.99 | False |
| dependencies | dependencies/original | dependencies/python-3.12/opt-2/uncompyle6 | unsupported | False | 19.71 | 33.55 | 1.10 | False |
| dependencies | dependencies/original | dependencies/python-3.12/opt-2/pycdc | success | True | 99.72 | 99.99 | 99.99 | False |
| dependencies | dependencies/original | dependencies/python-3.14/opt-0/uncompyle6 | unsupported | False | 18.94 | 35.11 | 1.09 | False |
| dependencies | dependencies/original | dependencies/python-3.14/opt-0/pycdc | invalid_output | False | N/A | N/A | N/A | False |
| dependencies | dependencies/original | dependencies/python-3.14/opt-1/uncompyle6 | unsupported | False | 18.94 | 35.11 | 1.09 | False |
| dependencies | dependencies/original | dependencies/python-3.14/opt-1/pycdc | invalid_output | False | N/A | N/A | N/A | False |
| dependencies | dependencies/original | dependencies/python-3.14/opt-2/uncompyle6 | unsupported | False | 18.94 | 35.11 | 1.09 | False |
| dependencies | dependencies/original | dependencies/python-3.14/opt-2/pycdc | invalid_output | False | N/A | N/A | N/A | False |
| dependencies | dependencies/original | dependencies/python-3.4/opt-0/uncompyle6 | success | True | 100.00 | 100.00 | 100.00 | True |
| dependencies | dependencies/original | dependencies/python-3.4/opt-0/pycdc | behavior_mismatch | False | 98.78 | 99.96 | 99.96 | False |
| dependencies | dependencies/original | dependencies/python-3.4/opt-1/uncompyle6 | success | True | 100.00 | 100.00 | 100.00 | True |
| dependencies | dependencies/original | dependencies/python-3.4/opt-1/pycdc | behavior_mismatch | False | 98.78 | 99.96 | 99.96 | False |
| dependencies | dependencies/original | dependencies/python-3.4/opt-2/uncompyle6 | success | True | 100.00 | 100.00 | 100.00 | True |
| dependencies | dependencies/original | dependencies/python-3.4/opt-2/pycdc | behavior_mismatch | False | 98.78 | 99.96 | 99.96 | False |
| dependencies | dependencies/original | dependencies/python-3.8/opt-0/uncompyle6 | success | True | 99.44 | 99.98 | 100.00 | False |
| dependencies | dependencies/original | dependencies/python-3.8/opt-0/pycdc | behavior_mismatch | False | 98.78 | 99.96 | 99.96 | False |
| dependencies | dependencies/original | dependencies/python-3.8/opt-1/uncompyle6 | success | True | 99.44 | 99.98 | 100.00 | False |
| dependencies | dependencies/original | dependencies/python-3.8/opt-1/pycdc | behavior_mismatch | False | 98.78 | 99.96 | 99.96 | False |
| dependencies | dependencies/original | dependencies/python-3.8/opt-2/uncompyle6 | success | True | 99.44 | 99.98 | 100.00 | False |
| dependencies | dependencies/original | dependencies/python-3.8/opt-2/pycdc | behavior_mismatch | False | 98.78 | 99.96 | 99.96 | False |
| dispatch | dispatch/original | dispatch/python-3.12/opt-0/uncompyle6 | unsupported | False | -0.69 | 23.23 | 0.00 | False |
| dispatch | dispatch/original | dispatch/python-3.12/opt-0/pycdc | success | True | 100.00 | 100.00 | 100.00 | True |
| dispatch | dispatch/original | dispatch/python-3.12/opt-1/uncompyle6 | unsupported | False | -0.69 | 23.23 | 0.00 | False |
| dispatch | dispatch/original | dispatch/python-3.12/opt-1/pycdc | success | True | 100.00 | 100.00 | 100.00 | True |
| dispatch | dispatch/original | dispatch/python-3.12/opt-2/uncompyle6 | unsupported | False | -0.69 | 23.23 | 0.00 | False |
| dispatch | dispatch/original | dispatch/python-3.12/opt-2/pycdc | success | True | 100.00 | 100.00 | 100.00 | True |
| dispatch | dispatch/original | dispatch/python-3.14/opt-0/uncompyle6 | unsupported | False | -2.43 | 24.56 | 0.00 | False |
| dispatch | dispatch/original | dispatch/python-3.14/opt-0/pycdc | invalid_output | False | N/A | N/A | N/A | False |
| dispatch | dispatch/original | dispatch/python-3.14/opt-1/uncompyle6 | unsupported | False | -2.43 | 24.56 | 0.00 | False |
| dispatch | dispatch/original | dispatch/python-3.14/opt-1/pycdc | invalid_output | False | N/A | N/A | N/A | False |
| dispatch | dispatch/original | dispatch/python-3.14/opt-2/uncompyle6 | unsupported | False | -2.43 | 24.56 | 0.00 | False |
| dispatch | dispatch/original | dispatch/python-3.14/opt-2/pycdc | invalid_output | False | N/A | N/A | N/A | False |
| dispatch | dispatch/original | dispatch/python-3.4/opt-0/uncompyle6 | success | True | 100.00 | 100.00 | 100.00 | True |
| dispatch | dispatch/original | dispatch/python-3.4/opt-0/pycdc | success | True | 100.00 | 100.00 | 100.00 | True |
| dispatch | dispatch/original | dispatch/python-3.4/opt-1/uncompyle6 | success | True | 100.00 | 100.00 | 100.00 | True |
| dispatch | dispatch/original | dispatch/python-3.4/opt-1/pycdc | success | True | 100.00 | 100.00 | 100.00 | True |
| dispatch | dispatch/original | dispatch/python-3.4/opt-2/uncompyle6 | success | True | 100.00 | 100.00 | 100.00 | True |
| dispatch | dispatch/original | dispatch/python-3.4/opt-2/pycdc | success | True | 100.00 | 100.00 | 100.00 | True |
| dispatch | dispatch/original | dispatch/python-3.8/opt-0/uncompyle6 | success | True | 99.79 | 99.98 | 100.00 | False |
| dispatch | dispatch/original | dispatch/python-3.8/opt-0/pycdc | success | True | 100.00 | 100.00 | 100.00 | True |
| dispatch | dispatch/original | dispatch/python-3.8/opt-1/uncompyle6 | success | True | 99.79 | 99.98 | 100.00 | False |
| dispatch | dispatch/original | dispatch/python-3.8/opt-1/pycdc | success | True | 100.00 | 100.00 | 100.00 | True |
| dispatch | dispatch/original | dispatch/python-3.8/opt-2/uncompyle6 | success | True | 99.79 | 99.98 | 100.00 | False |
| dispatch | dispatch/original | dispatch/python-3.8/opt-2/pycdc | success | True | 100.00 | 100.00 | 100.00 | True |
| events | events/original | events/python-3.12/opt-0/uncompyle6 | unsupported | False | 28.01 | 34.55 | 0.00 | False |
| events | events/original | events/python-3.12/opt-0/pycdc | unsupported | False | 9.08 | 86.77 | 90.38 | False |
| events | events/original | events/python-3.12/opt-1/uncompyle6 | unsupported | False | 28.01 | 34.55 | 0.00 | False |
| events | events/original | events/python-3.12/opt-1/pycdc | unsupported | False | 9.08 | 86.77 | 90.38 | False |
| events | events/original | events/python-3.12/opt-2/uncompyle6 | unsupported | False | 28.01 | 34.55 | 0.00 | False |
| events | events/original | events/python-3.12/opt-2/pycdc | unsupported | False | 9.08 | 86.77 | 90.38 | False |
| events | events/original | events/python-3.14/opt-0/uncompyle6 | unsupported | False | 27.24 | 36.03 | 0.00 | False |
| events | events/original | events/python-3.14/opt-0/pycdc | invalid_output | False | N/A | N/A | N/A | False |
| events | events/original | events/python-3.14/opt-1/uncompyle6 | unsupported | False | 27.24 | 36.03 | 0.00 | False |
| events | events/original | events/python-3.14/opt-1/pycdc | invalid_output | False | N/A | N/A | N/A | False |
| events | events/original | events/python-3.14/opt-2/uncompyle6 | unsupported | False | 27.24 | 36.03 | 0.00 | False |
| events | events/original | events/python-3.14/opt-2/pycdc | invalid_output | False | N/A | N/A | N/A | False |
| events | events/original | events/python-3.4/opt-0/uncompyle6 | success | True | 100.00 | 100.00 | 100.00 | True |
| events | events/original | events/python-3.4/opt-0/pycdc | invalid_output | False | 27.25 | 40.64 | 0.00 | False |
| events | events/original | events/python-3.4/opt-1/uncompyle6 | success | True | 100.00 | 100.00 | 100.00 | True |
| events | events/original | events/python-3.4/opt-1/pycdc | invalid_output | False | 27.25 | 40.64 | 0.00 | False |
| events | events/original | events/python-3.4/opt-2/uncompyle6 | success | True | 100.00 | 100.00 | 100.00 | True |
| events | events/original | events/python-3.4/opt-2/pycdc | invalid_output | False | 27.25 | 40.64 | 0.00 | False |
| events | events/original | events/python-3.8/opt-0/uncompyle6 | invalid_output | False | 26.97 | 41.42 | 0.00 | False |
| events | events/original | events/python-3.8/opt-0/pycdc | invalid_output | False | 27.76 | 39.34 | 0.00 | False |
| events | events/original | events/python-3.8/opt-1/uncompyle6 | invalid_output | False | 26.97 | 41.42 | 0.00 | False |
| events | events/original | events/python-3.8/opt-1/pycdc | invalid_output | False | 27.76 | 39.34 | 0.00 | False |
| events | events/original | events/python-3.8/opt-2/uncompyle6 | invalid_output | False | 26.97 | 41.42 | 0.00 | False |
| events | events/original | events/python-3.8/opt-2/pycdc | invalid_output | False | 27.76 | 39.34 | 0.00 | False |
| inventory | inventory/original | inventory/python-3.12/opt-0/uncompyle6 | unsupported | False | 15.01 | 29.22 | 0.21 | False |
| inventory | inventory/original | inventory/python-3.12/opt-0/pycdc | partial | False | 93.70 | 99.14 | 99.35 | False |
| inventory | inventory/original | inventory/python-3.12/opt-1/uncompyle6 | unsupported | False | 15.01 | 29.22 | 0.21 | False |
| inventory | inventory/original | inventory/python-3.12/opt-1/pycdc | partial | False | 93.70 | 99.14 | 99.35 | False |
| inventory | inventory/original | inventory/python-3.12/opt-2/uncompyle6 | unsupported | False | 15.01 | 29.22 | 0.21 | False |
| inventory | inventory/original | inventory/python-3.12/opt-2/pycdc | partial | False | 93.70 | 99.14 | 99.35 | False |
| inventory | inventory/original | inventory/python-3.14/opt-0/uncompyle6 | unsupported | False | 15.35 | 30.72 | 0.22 | False |
| inventory | inventory/original | inventory/python-3.14/opt-0/pycdc | invalid_output | False | N/A | N/A | N/A | False |
| inventory | inventory/original | inventory/python-3.14/opt-1/uncompyle6 | unsupported | False | 15.35 | 30.72 | 0.22 | False |
| inventory | inventory/original | inventory/python-3.14/opt-1/pycdc | invalid_output | False | N/A | N/A | N/A | False |
| inventory | inventory/original | inventory/python-3.14/opt-2/uncompyle6 | unsupported | False | 15.35 | 30.72 | 0.22 | False |
| inventory | inventory/original | inventory/python-3.14/opt-2/pycdc | invalid_output | False | N/A | N/A | N/A | False |
| inventory | inventory/original | inventory/python-3.4/opt-0/uncompyle6 | success | True | 100.00 | 100.00 | 100.00 | True |
| inventory | inventory/original | inventory/python-3.4/opt-0/pycdc | success | True | 97.43 | 99.28 | 99.41 | False |
| inventory | inventory/original | inventory/python-3.4/opt-1/uncompyle6 | success | True | 100.00 | 100.00 | 100.00 | True |
| inventory | inventory/original | inventory/python-3.4/opt-1/pycdc | success | True | 97.43 | 99.28 | 99.41 | False |
| inventory | inventory/original | inventory/python-3.4/opt-2/uncompyle6 | success | True | 100.00 | 100.00 | 100.00 | True |
| inventory | inventory/original | inventory/python-3.4/opt-2/pycdc | success | True | 97.43 | 99.28 | 99.41 | False |
| inventory | inventory/original | inventory/python-3.8/opt-0/uncompyle6 | success | True | 99.82 | 99.99 | 100.00 | False |
| inventory | inventory/original | inventory/python-3.8/opt-0/pycdc | success | True | 97.43 | 99.28 | 99.41 | False |
| inventory | inventory/original | inventory/python-3.8/opt-1/uncompyle6 | success | True | 99.82 | 99.99 | 100.00 | False |
| inventory | inventory/original | inventory/python-3.8/opt-1/pycdc | success | True | 97.43 | 99.28 | 99.41 | False |
| inventory | inventory/original | inventory/python-3.8/opt-2/uncompyle6 | success | True | 99.82 | 99.99 | 100.00 | False |
| inventory | inventory/original | inventory/python-3.8/opt-2/pycdc | success | True | 97.43 | 99.28 | 99.41 | False |
| invoice | invoice/original | invoice/python-3.12/opt-0/uncompyle6 | unsupported | False | 11.07 | 21.62 | 0.00 | False |
| invoice | invoice/original | invoice/python-3.12/opt-0/pycdc | unsupported | False | 85.39 | 96.13 | 96.97 | False |
| invoice | invoice/original | invoice/python-3.12/opt-1/uncompyle6 | unsupported | False | 11.07 | 21.62 | 0.00 | False |
| invoice | invoice/original | invoice/python-3.12/opt-1/pycdc | unsupported | False | 85.39 | 96.13 | 96.97 | False |
| invoice | invoice/original | invoice/python-3.12/opt-2/uncompyle6 | unsupported | False | 11.07 | 21.62 | 0.00 | False |
| invoice | invoice/original | invoice/python-3.12/opt-2/pycdc | unsupported | False | 85.39 | 96.13 | 96.97 | False |
| invoice | invoice/original | invoice/python-3.14/opt-0/uncompyle6 | unsupported | False | 9.48 | 23.93 | 0.00 | False |
| invoice | invoice/original | invoice/python-3.14/opt-0/pycdc | invalid_output | False | N/A | N/A | N/A | False |
| invoice | invoice/original | invoice/python-3.14/opt-1/uncompyle6 | unsupported | False | 9.48 | 23.93 | 0.00 | False |
| invoice | invoice/original | invoice/python-3.14/opt-1/pycdc | invalid_output | False | N/A | N/A | N/A | False |
| invoice | invoice/original | invoice/python-3.14/opt-2/uncompyle6 | unsupported | False | 9.48 | 23.93 | 0.00 | False |
| invoice | invoice/original | invoice/python-3.14/opt-2/pycdc | invalid_output | False | N/A | N/A | N/A | False |
| invoice | invoice/original | invoice/python-3.4/opt-0/uncompyle6 | success | True | 100.00 | 100.00 | 100.00 | True |
| invoice | invoice/original | invoice/python-3.4/opt-0/pycdc | invalid_output | False | 75.35 | 82.36 | 68.51 | False |
| invoice | invoice/original | invoice/python-3.4/opt-1/uncompyle6 | success | True | 100.00 | 100.00 | 100.00 | True |
| invoice | invoice/original | invoice/python-3.4/opt-1/pycdc | invalid_output | False | 75.35 | 82.36 | 68.51 | False |
| invoice | invoice/original | invoice/python-3.4/opt-2/uncompyle6 | success | True | 100.00 | 100.00 | 100.00 | True |
| invoice | invoice/original | invoice/python-3.4/opt-2/pycdc | invalid_output | False | 75.35 | 82.36 | 68.51 | False |
| invoice | invoice/original | invoice/python-3.8/opt-0/uncompyle6 | success | True | 100.00 | 100.00 | 100.00 | True |
| invoice | invoice/original | invoice/python-3.8/opt-0/pycdc | invalid_output | False | 75.45 | 82.22 | 68.51 | False |
| invoice | invoice/original | invoice/python-3.8/opt-1/uncompyle6 | success | True | 100.00 | 100.00 | 100.00 | True |
| invoice | invoice/original | invoice/python-3.8/opt-1/pycdc | invalid_output | False | 75.45 | 82.22 | 68.51 | False |
| invoice | invoice/original | invoice/python-3.8/opt-2/uncompyle6 | success | True | 100.00 | 100.00 | 100.00 | True |
| invoice | invoice/original | invoice/python-3.8/opt-2/pycdc | invalid_output | False | 75.45 | 82.22 | 68.51 | False |
| memo | memo/original | memo/python-3.12/opt-0/uncompyle6 | unsupported | False | 11.77 | 26.63 | 1.10 | False |
| memo | memo/original | memo/python-3.12/opt-0/pycdc | unsupported | False | 56.52 | 90.92 | 89.26 | False |
| memo | memo/original | memo/python-3.12/opt-1/uncompyle6 | unsupported | False | 11.77 | 26.63 | 1.10 | False |
| memo | memo/original | memo/python-3.12/opt-1/pycdc | unsupported | False | 56.52 | 90.92 | 89.26 | False |
| memo | memo/original | memo/python-3.12/opt-2/uncompyle6 | unsupported | False | 11.77 | 26.63 | 1.10 | False |
| memo | memo/original | memo/python-3.12/opt-2/pycdc | unsupported | False | 56.52 | 90.92 | 89.26 | False |
| memo | memo/original | memo/python-3.14/opt-0/uncompyle6 | unsupported | False | 10.69 | 27.98 | 1.09 | False |
| memo | memo/original | memo/python-3.14/opt-0/pycdc | invalid_output | False | N/A | N/A | N/A | False |
| memo | memo/original | memo/python-3.14/opt-1/uncompyle6 | unsupported | False | 10.69 | 27.98 | 1.09 | False |
| memo | memo/original | memo/python-3.14/opt-1/pycdc | invalid_output | False | N/A | N/A | N/A | False |
| memo | memo/original | memo/python-3.14/opt-2/uncompyle6 | unsupported | False | 10.69 | 27.98 | 1.09 | False |
| memo | memo/original | memo/python-3.14/opt-2/pycdc | invalid_output | False | N/A | N/A | N/A | False |
| memo | memo/original | memo/python-3.4/opt-0/uncompyle6 | success | True | 100.00 | 100.00 | 100.00 | True |
| memo | memo/original | memo/python-3.4/opt-0/pycdc | invalid_output | False | 14.16 | 33.55 | 1.12 | False |
| memo | memo/original | memo/python-3.4/opt-1/uncompyle6 | success | True | 100.00 | 100.00 | 100.00 | True |
| memo | memo/original | memo/python-3.4/opt-1/pycdc | invalid_output | False | 14.16 | 33.55 | 1.12 | False |
| memo | memo/original | memo/python-3.4/opt-2/uncompyle6 | success | True | 100.00 | 100.00 | 100.00 | True |
| memo | memo/original | memo/python-3.4/opt-2/pycdc | invalid_output | False | 14.16 | 33.55 | 1.12 | False |
| memo | memo/original | memo/python-3.8/opt-0/uncompyle6 | success | True | 100.00 | 100.00 | 100.00 | True |
| memo | memo/original | memo/python-3.8/opt-0/pycdc | invalid_output | False | 14.23 | 33.35 | 1.12 | False |
| memo | memo/original | memo/python-3.8/opt-1/uncompyle6 | success | True | 100.00 | 100.00 | 100.00 | True |
| memo | memo/original | memo/python-3.8/opt-1/pycdc | invalid_output | False | 14.23 | 33.35 | 1.12 | False |
| memo | memo/original | memo/python-3.8/opt-2/uncompyle6 | success | True | 100.00 | 100.00 | 100.00 | True |
| memo | memo/original | memo/python-3.8/opt-2/pycdc | invalid_output | False | 14.23 | 33.35 | 1.12 | False |
| transaction | transaction/original | transaction/python-3.12/opt-0/uncompyle6 | unsupported | False | 24.26 | 33.24 | 0.00 | False |
| transaction | transaction/original | transaction/python-3.12/opt-0/pycdc | unsupported | False | 94.27 | 98.36 | 98.89 | False |
| transaction | transaction/original | transaction/python-3.12/opt-1/uncompyle6 | unsupported | False | 24.26 | 33.24 | 0.00 | False |
| transaction | transaction/original | transaction/python-3.12/opt-1/pycdc | unsupported | False | 94.27 | 98.36 | 98.89 | False |
| transaction | transaction/original | transaction/python-3.12/opt-2/uncompyle6 | unsupported | False | 24.26 | 33.24 | 0.00 | False |
| transaction | transaction/original | transaction/python-3.12/opt-2/pycdc | unsupported | False | 94.27 | 98.36 | 98.89 | False |
| transaction | transaction/original | transaction/python-3.14/opt-0/uncompyle6 | invalid_output | False | N/A | N/A | N/A | False |
| transaction | transaction/original | transaction/python-3.14/opt-0/pycdc | invalid_output | False | N/A | N/A | N/A | False |
| transaction | transaction/original | transaction/python-3.14/opt-1/uncompyle6 | invalid_output | False | N/A | N/A | N/A | False |
| transaction | transaction/original | transaction/python-3.14/opt-1/pycdc | invalid_output | False | N/A | N/A | N/A | False |
| transaction | transaction/original | transaction/python-3.14/opt-2/uncompyle6 | invalid_output | False | N/A | N/A | N/A | False |
| transaction | transaction/original | transaction/python-3.14/opt-2/pycdc | invalid_output | False | N/A | N/A | N/A | False |
| transaction | transaction/original | transaction/python-3.4/opt-0/uncompyle6 | success | True | 100.00 | 100.00 | 100.00 | True |
| transaction | transaction/original | transaction/python-3.4/opt-0/pycdc | invalid_output | False | 27.02 | 39.09 | 0.00 | False |
| transaction | transaction/original | transaction/python-3.4/opt-1/uncompyle6 | success | True | 100.00 | 100.00 | 100.00 | True |
| transaction | transaction/original | transaction/python-3.4/opt-1/pycdc | invalid_output | False | 27.02 | 39.09 | 0.00 | False |
| transaction | transaction/original | transaction/python-3.4/opt-2/uncompyle6 | success | True | 100.00 | 100.00 | 100.00 | True |
| transaction | transaction/original | transaction/python-3.4/opt-2/pycdc | invalid_output | False | 27.02 | 39.09 | 0.00 | False |
| transaction | transaction/original | transaction/python-3.8/opt-0/uncompyle6 | behavior_mismatch | False | 99.19 | 99.97 | 99.97 | False |
| transaction | transaction/original | transaction/python-3.8/opt-0/pycdc | unsupported | False | 96.00 | 99.73 | 99.88 | False |
| transaction | transaction/original | transaction/python-3.8/opt-1/uncompyle6 | behavior_mismatch | False | 99.19 | 99.97 | 99.97 | False |
| transaction | transaction/original | transaction/python-3.8/opt-1/pycdc | unsupported | False | 96.00 | 99.73 | 99.88 | False |
| transaction | transaction/original | transaction/python-3.8/opt-2/uncompyle6 | behavior_mismatch | False | 99.19 | 99.97 | 99.97 | False |
| transaction | transaction/original | transaction/python-3.8/opt-2/pycdc | unsupported | False | 96.00 | 99.73 | 99.88 | False |
| typed_router | typed_router/original | typed_router/python-3.12/opt-0/uncompyle6 | unsupported | False | 22.30 | 20.48 | 0.44 | False |
| typed_router | typed_router/original | typed_router/python-3.12/opt-0/pycdc | unsupported | False | 24.83 | 26.56 | 0.45 | False |
| typed_router | typed_router/original | typed_router/python-3.12/opt-1/uncompyle6 | unsupported | False | 22.30 | 20.48 | 0.44 | False |
| typed_router | typed_router/original | typed_router/python-3.12/opt-1/pycdc | unsupported | False | 24.83 | 26.56 | 0.45 | False |
| typed_router | typed_router/original | typed_router/python-3.12/opt-2/uncompyle6 | unsupported | False | 22.30 | 20.48 | 0.44 | False |
| typed_router | typed_router/original | typed_router/python-3.12/opt-2/pycdc | unsupported | False | 24.83 | 26.56 | 0.45 | False |
| typed_router | typed_router/original | typed_router/python-3.14/opt-0/uncompyle6 | unsupported | False | 18.89 | 22.00 | 0.44 | False |
| typed_router | typed_router/original | typed_router/python-3.14/opt-0/pycdc | invalid_output | False | N/A | N/A | N/A | False |
| typed_router | typed_router/original | typed_router/python-3.14/opt-1/uncompyle6 | unsupported | False | 18.89 | 22.00 | 0.44 | False |
| typed_router | typed_router/original | typed_router/python-3.14/opt-1/pycdc | invalid_output | False | N/A | N/A | N/A | False |
| typed_router | typed_router/original | typed_router/python-3.14/opt-2/uncompyle6 | unsupported | False | 18.89 | 22.00 | 0.44 | False |
| typed_router | typed_router/original | typed_router/python-3.14/opt-2/pycdc | invalid_output | False | N/A | N/A | N/A | False |
| async_queue | async_queue/obfuscated-light-0 | async_queue/python-3.12/opt-0/uncompyle6 | unsupported | False | 30.05 | 34.19 | 0.52 | False |
| async_queue | async_queue/obfuscated-light-1 | async_queue/python-3.12/opt-0/uncompyle6 | unsupported | False | 30.05 | 34.19 | 0.52 | False |
| async_queue | async_queue/obfuscated-light-2 | async_queue/python-3.12/opt-0/uncompyle6 | unsupported | False | 30.05 | 34.19 | 0.52 | False |
| async_queue | async_queue/obfuscated-structural-0 | async_queue/python-3.12/opt-0/uncompyle6 | unsupported | False | 20.74 | 34.89 | 0.73 | False |
| async_queue | async_queue/obfuscated-structural-1 | async_queue/python-3.12/opt-0/uncompyle6 | unsupported | False | 20.74 | 34.89 | 0.73 | False |
| async_queue | async_queue/obfuscated-structural-2 | async_queue/python-3.12/opt-0/uncompyle6 | unsupported | False | 20.74 | 34.89 | 0.73 | False |
| async_queue | async_queue/obfuscated-light-0 | async_queue/python-3.12/opt-0/pycdc | unsupported | False | 54.10 | 87.95 | 90.18 | False |
| async_queue | async_queue/obfuscated-light-1 | async_queue/python-3.12/opt-0/pycdc | unsupported | False | 54.10 | 87.95 | 90.18 | False |
| async_queue | async_queue/obfuscated-light-2 | async_queue/python-3.12/opt-0/pycdc | unsupported | False | 54.10 | 87.95 | 90.18 | False |
| async_queue | async_queue/obfuscated-structural-0 | async_queue/python-3.12/opt-0/pycdc | unsupported | False | 56.94 | 91.04 | 90.24 | False |
| async_queue | async_queue/obfuscated-structural-1 | async_queue/python-3.12/opt-0/pycdc | unsupported | False | 56.94 | 91.04 | 90.24 | False |
| async_queue | async_queue/obfuscated-structural-2 | async_queue/python-3.12/opt-0/pycdc | unsupported | False | 56.94 | 91.04 | 90.24 | False |
| async_queue | async_queue/obfuscated-light-0 | async_queue/python-3.12/opt-1/uncompyle6 | unsupported | False | 30.05 | 34.19 | 0.52 | False |
| async_queue | async_queue/obfuscated-light-1 | async_queue/python-3.12/opt-1/uncompyle6 | unsupported | False | 30.05 | 34.19 | 0.52 | False |
| async_queue | async_queue/obfuscated-light-2 | async_queue/python-3.12/opt-1/uncompyle6 | unsupported | False | 30.05 | 34.19 | 0.52 | False |
| async_queue | async_queue/obfuscated-structural-0 | async_queue/python-3.12/opt-1/uncompyle6 | unsupported | False | 20.74 | 34.89 | 0.73 | False |
| async_queue | async_queue/obfuscated-structural-1 | async_queue/python-3.12/opt-1/uncompyle6 | unsupported | False | 20.74 | 34.89 | 0.73 | False |
| async_queue | async_queue/obfuscated-structural-2 | async_queue/python-3.12/opt-1/uncompyle6 | unsupported | False | 20.74 | 34.89 | 0.73 | False |
| async_queue | async_queue/obfuscated-light-0 | async_queue/python-3.12/opt-1/pycdc | unsupported | False | 54.10 | 87.95 | 90.18 | False |
| async_queue | async_queue/obfuscated-light-1 | async_queue/python-3.12/opt-1/pycdc | unsupported | False | 54.10 | 87.95 | 90.18 | False |
| async_queue | async_queue/obfuscated-light-2 | async_queue/python-3.12/opt-1/pycdc | unsupported | False | 54.10 | 87.95 | 90.18 | False |
| async_queue | async_queue/obfuscated-structural-0 | async_queue/python-3.12/opt-1/pycdc | unsupported | False | 56.94 | 91.04 | 90.24 | False |
| async_queue | async_queue/obfuscated-structural-1 | async_queue/python-3.12/opt-1/pycdc | unsupported | False | 56.94 | 91.04 | 90.24 | False |
| async_queue | async_queue/obfuscated-structural-2 | async_queue/python-3.12/opt-1/pycdc | unsupported | False | 56.94 | 91.04 | 90.24 | False |
| async_queue | async_queue/obfuscated-light-0 | async_queue/python-3.12/opt-2/uncompyle6 | unsupported | False | 30.05 | 34.19 | 0.52 | False |
| async_queue | async_queue/obfuscated-light-1 | async_queue/python-3.12/opt-2/uncompyle6 | unsupported | False | 30.05 | 34.19 | 0.52 | False |
| async_queue | async_queue/obfuscated-light-2 | async_queue/python-3.12/opt-2/uncompyle6 | unsupported | False | 30.05 | 34.19 | 0.52 | False |
| async_queue | async_queue/obfuscated-structural-0 | async_queue/python-3.12/opt-2/uncompyle6 | unsupported | False | 20.74 | 34.89 | 0.73 | False |
| async_queue | async_queue/obfuscated-structural-1 | async_queue/python-3.12/opt-2/uncompyle6 | unsupported | False | 20.74 | 34.89 | 0.73 | False |
| async_queue | async_queue/obfuscated-structural-2 | async_queue/python-3.12/opt-2/uncompyle6 | unsupported | False | 20.74 | 34.89 | 0.73 | False |
| async_queue | async_queue/obfuscated-light-0 | async_queue/python-3.12/opt-2/pycdc | unsupported | False | 54.10 | 87.95 | 90.18 | False |
| async_queue | async_queue/obfuscated-light-1 | async_queue/python-3.12/opt-2/pycdc | unsupported | False | 54.10 | 87.95 | 90.18 | False |
| async_queue | async_queue/obfuscated-light-2 | async_queue/python-3.12/opt-2/pycdc | unsupported | False | 54.10 | 87.95 | 90.18 | False |
| async_queue | async_queue/obfuscated-structural-0 | async_queue/python-3.12/opt-2/pycdc | unsupported | False | 56.94 | 91.04 | 90.24 | False |
| async_queue | async_queue/obfuscated-structural-1 | async_queue/python-3.12/opt-2/pycdc | unsupported | False | 56.94 | 91.04 | 90.24 | False |
| async_queue | async_queue/obfuscated-structural-2 | async_queue/python-3.12/opt-2/pycdc | unsupported | False | 56.94 | 91.04 | 90.24 | False |
| async_queue | async_queue/obfuscated-light-0 | async_queue/python-3.14/opt-0/uncompyle6 | unsupported | False | 29.49 | 35.58 | 0.52 | False |
| async_queue | async_queue/obfuscated-light-1 | async_queue/python-3.14/opt-0/uncompyle6 | unsupported | False | 29.49 | 35.58 | 0.52 | False |
| async_queue | async_queue/obfuscated-light-2 | async_queue/python-3.14/opt-0/uncompyle6 | unsupported | False | 29.49 | 35.58 | 0.52 | False |
| async_queue | async_queue/obfuscated-structural-0 | async_queue/python-3.14/opt-0/uncompyle6 | unsupported | False | 19.48 | 36.15 | 0.73 | False |
| async_queue | async_queue/obfuscated-structural-1 | async_queue/python-3.14/opt-0/uncompyle6 | unsupported | False | 19.48 | 36.15 | 0.73 | False |
| async_queue | async_queue/obfuscated-structural-2 | async_queue/python-3.14/opt-0/uncompyle6 | unsupported | False | 19.48 | 36.15 | 0.73 | False |
| async_queue | async_queue/obfuscated-light-0 | async_queue/python-3.14/opt-0/pycdc | invalid_output | False | N/A | N/A | N/A | False |
| async_queue | async_queue/obfuscated-light-1 | async_queue/python-3.14/opt-0/pycdc | invalid_output | False | N/A | N/A | N/A | False |
| async_queue | async_queue/obfuscated-light-2 | async_queue/python-3.14/opt-0/pycdc | invalid_output | False | N/A | N/A | N/A | False |
| async_queue | async_queue/obfuscated-structural-0 | async_queue/python-3.14/opt-0/pycdc | invalid_output | False | N/A | N/A | N/A | False |
| async_queue | async_queue/obfuscated-structural-1 | async_queue/python-3.14/opt-0/pycdc | invalid_output | False | N/A | N/A | N/A | False |
| async_queue | async_queue/obfuscated-structural-2 | async_queue/python-3.14/opt-0/pycdc | invalid_output | False | N/A | N/A | N/A | False |
| async_queue | async_queue/obfuscated-light-0 | async_queue/python-3.14/opt-1/uncompyle6 | unsupported | False | 29.49 | 35.58 | 0.52 | False |
| async_queue | async_queue/obfuscated-light-1 | async_queue/python-3.14/opt-1/uncompyle6 | unsupported | False | 29.49 | 35.58 | 0.52 | False |
| async_queue | async_queue/obfuscated-light-2 | async_queue/python-3.14/opt-1/uncompyle6 | unsupported | False | 29.49 | 35.58 | 0.52 | False |
| async_queue | async_queue/obfuscated-structural-0 | async_queue/python-3.14/opt-1/uncompyle6 | unsupported | False | 19.48 | 36.15 | 0.73 | False |
| async_queue | async_queue/obfuscated-structural-1 | async_queue/python-3.14/opt-1/uncompyle6 | unsupported | False | 19.48 | 36.15 | 0.73 | False |
| async_queue | async_queue/obfuscated-structural-2 | async_queue/python-3.14/opt-1/uncompyle6 | unsupported | False | 19.48 | 36.15 | 0.73 | False |
| async_queue | async_queue/obfuscated-light-0 | async_queue/python-3.14/opt-1/pycdc | invalid_output | False | N/A | N/A | N/A | False |
| async_queue | async_queue/obfuscated-light-1 | async_queue/python-3.14/opt-1/pycdc | invalid_output | False | N/A | N/A | N/A | False |
| async_queue | async_queue/obfuscated-light-2 | async_queue/python-3.14/opt-1/pycdc | invalid_output | False | N/A | N/A | N/A | False |
| async_queue | async_queue/obfuscated-structural-0 | async_queue/python-3.14/opt-1/pycdc | invalid_output | False | N/A | N/A | N/A | False |
| async_queue | async_queue/obfuscated-structural-1 | async_queue/python-3.14/opt-1/pycdc | invalid_output | False | N/A | N/A | N/A | False |
| async_queue | async_queue/obfuscated-structural-2 | async_queue/python-3.14/opt-1/pycdc | invalid_output | False | N/A | N/A | N/A | False |
| async_queue | async_queue/obfuscated-light-0 | async_queue/python-3.14/opt-2/uncompyle6 | unsupported | False | 29.49 | 35.58 | 0.52 | False |
| async_queue | async_queue/obfuscated-light-1 | async_queue/python-3.14/opt-2/uncompyle6 | unsupported | False | 29.49 | 35.58 | 0.52 | False |
| async_queue | async_queue/obfuscated-light-2 | async_queue/python-3.14/opt-2/uncompyle6 | unsupported | False | 29.49 | 35.58 | 0.52 | False |
| async_queue | async_queue/obfuscated-structural-0 | async_queue/python-3.14/opt-2/uncompyle6 | unsupported | False | 19.48 | 36.15 | 0.73 | False |
| async_queue | async_queue/obfuscated-structural-1 | async_queue/python-3.14/opt-2/uncompyle6 | unsupported | False | 19.48 | 36.15 | 0.73 | False |
| async_queue | async_queue/obfuscated-structural-2 | async_queue/python-3.14/opt-2/uncompyle6 | unsupported | False | 19.48 | 36.15 | 0.73 | False |
| async_queue | async_queue/obfuscated-light-0 | async_queue/python-3.14/opt-2/pycdc | invalid_output | False | N/A | N/A | N/A | False |
| async_queue | async_queue/obfuscated-light-1 | async_queue/python-3.14/opt-2/pycdc | invalid_output | False | N/A | N/A | N/A | False |
| async_queue | async_queue/obfuscated-light-2 | async_queue/python-3.14/opt-2/pycdc | invalid_output | False | N/A | N/A | N/A | False |
| async_queue | async_queue/obfuscated-structural-0 | async_queue/python-3.14/opt-2/pycdc | invalid_output | False | N/A | N/A | N/A | False |
| async_queue | async_queue/obfuscated-structural-1 | async_queue/python-3.14/opt-2/pycdc | invalid_output | False | N/A | N/A | N/A | False |
| async_queue | async_queue/obfuscated-structural-2 | async_queue/python-3.14/opt-2/pycdc | invalid_output | False | N/A | N/A | N/A | False |
| async_queue | async_queue/obfuscated-light-0 | async_queue/python-3.8/opt-0/uncompyle6 | success | True | 99.23 | 99.97 | 99.99 | False |
| async_queue | async_queue/obfuscated-light-1 | async_queue/python-3.8/opt-0/uncompyle6 | success | True | 99.23 | 99.97 | 99.99 | False |
| async_queue | async_queue/obfuscated-light-2 | async_queue/python-3.8/opt-0/uncompyle6 | success | True | 99.23 | 99.97 | 99.99 | False |
| async_queue | async_queue/obfuscated-structural-0 | async_queue/python-3.8/opt-0/uncompyle6 | success | True | 86.60 | 98.63 | 99.25 | False |
| async_queue | async_queue/obfuscated-structural-1 | async_queue/python-3.8/opt-0/uncompyle6 | success | True | 86.60 | 98.63 | 99.25 | False |
| async_queue | async_queue/obfuscated-structural-2 | async_queue/python-3.8/opt-0/uncompyle6 | success | True | 86.60 | 98.63 | 99.25 | False |
| async_queue | async_queue/obfuscated-light-0 | async_queue/python-3.8/opt-0/pycdc | unsupported | False | 83.13 | 97.98 | 98.83 | False |
| async_queue | async_queue/obfuscated-light-1 | async_queue/python-3.8/opt-0/pycdc | unsupported | False | 83.13 | 97.98 | 98.83 | False |
| async_queue | async_queue/obfuscated-light-2 | async_queue/python-3.8/opt-0/pycdc | unsupported | False | 83.13 | 97.98 | 98.83 | False |
| async_queue | async_queue/obfuscated-structural-0 | async_queue/python-3.8/opt-0/pycdc | unsupported | False | 73.85 | 97.80 | 98.36 | False |
| async_queue | async_queue/obfuscated-structural-1 | async_queue/python-3.8/opt-0/pycdc | unsupported | False | 73.85 | 97.80 | 98.36 | False |
| async_queue | async_queue/obfuscated-structural-2 | async_queue/python-3.8/opt-0/pycdc | unsupported | False | 73.85 | 97.80 | 98.36 | False |
| async_queue | async_queue/obfuscated-light-0 | async_queue/python-3.8/opt-1/uncompyle6 | success | True | 99.23 | 99.97 | 99.99 | False |
| async_queue | async_queue/obfuscated-light-1 | async_queue/python-3.8/opt-1/uncompyle6 | success | True | 99.23 | 99.97 | 99.99 | False |
| async_queue | async_queue/obfuscated-light-2 | async_queue/python-3.8/opt-1/uncompyle6 | success | True | 99.23 | 99.97 | 99.99 | False |
| async_queue | async_queue/obfuscated-structural-0 | async_queue/python-3.8/opt-1/uncompyle6 | success | True | 86.60 | 98.63 | 99.25 | False |
| async_queue | async_queue/obfuscated-structural-1 | async_queue/python-3.8/opt-1/uncompyle6 | success | True | 86.60 | 98.63 | 99.25 | False |
| async_queue | async_queue/obfuscated-structural-2 | async_queue/python-3.8/opt-1/uncompyle6 | success | True | 86.60 | 98.63 | 99.25 | False |
| async_queue | async_queue/obfuscated-light-0 | async_queue/python-3.8/opt-1/pycdc | unsupported | False | 83.13 | 97.98 | 98.83 | False |
| async_queue | async_queue/obfuscated-light-1 | async_queue/python-3.8/opt-1/pycdc | unsupported | False | 83.13 | 97.98 | 98.83 | False |
| async_queue | async_queue/obfuscated-light-2 | async_queue/python-3.8/opt-1/pycdc | unsupported | False | 83.13 | 97.98 | 98.83 | False |
| async_queue | async_queue/obfuscated-structural-0 | async_queue/python-3.8/opt-1/pycdc | unsupported | False | 73.85 | 97.80 | 98.36 | False |
| async_queue | async_queue/obfuscated-structural-1 | async_queue/python-3.8/opt-1/pycdc | unsupported | False | 73.85 | 97.80 | 98.36 | False |
| async_queue | async_queue/obfuscated-structural-2 | async_queue/python-3.8/opt-1/pycdc | unsupported | False | 73.85 | 97.80 | 98.36 | False |
| async_queue | async_queue/obfuscated-light-0 | async_queue/python-3.8/opt-2/uncompyle6 | success | True | 99.23 | 99.97 | 99.99 | False |
| async_queue | async_queue/obfuscated-light-1 | async_queue/python-3.8/opt-2/uncompyle6 | success | True | 99.23 | 99.97 | 99.99 | False |
| async_queue | async_queue/obfuscated-light-2 | async_queue/python-3.8/opt-2/uncompyle6 | success | True | 99.23 | 99.97 | 99.99 | False |
| async_queue | async_queue/obfuscated-structural-0 | async_queue/python-3.8/opt-2/uncompyle6 | success | True | 86.60 | 98.63 | 99.25 | False |
| async_queue | async_queue/obfuscated-structural-1 | async_queue/python-3.8/opt-2/uncompyle6 | success | True | 86.60 | 98.63 | 99.25 | False |
| async_queue | async_queue/obfuscated-structural-2 | async_queue/python-3.8/opt-2/uncompyle6 | success | True | 86.60 | 98.63 | 99.25 | False |
| async_queue | async_queue/obfuscated-light-0 | async_queue/python-3.8/opt-2/pycdc | unsupported | False | 83.13 | 97.98 | 98.83 | False |
| async_queue | async_queue/obfuscated-light-1 | async_queue/python-3.8/opt-2/pycdc | unsupported | False | 83.13 | 97.98 | 98.83 | False |
| async_queue | async_queue/obfuscated-light-2 | async_queue/python-3.8/opt-2/pycdc | unsupported | False | 83.13 | 97.98 | 98.83 | False |
| async_queue | async_queue/obfuscated-structural-0 | async_queue/python-3.8/opt-2/pycdc | unsupported | False | 73.85 | 97.80 | 98.36 | False |
| async_queue | async_queue/obfuscated-structural-1 | async_queue/python-3.8/opt-2/pycdc | unsupported | False | 73.85 | 97.80 | 98.36 | False |
| async_queue | async_queue/obfuscated-structural-2 | async_queue/python-3.8/opt-2/pycdc | unsupported | False | 73.85 | 97.80 | 98.36 | False |
| codec | codec/obfuscated-light-0 | codec/python-3.12/opt-0/uncompyle6 | unsupported | False | 31.66 | 33.45 | 0.00 | False |
| codec | codec/obfuscated-light-1 | codec/python-3.12/opt-0/uncompyle6 | unsupported | False | 31.66 | 33.45 | 0.00 | False |
| codec | codec/obfuscated-light-2 | codec/python-3.12/opt-0/uncompyle6 | unsupported | False | 31.66 | 33.45 | 0.00 | False |
| codec | codec/obfuscated-structural-0 | codec/python-3.12/opt-0/uncompyle6 | unsupported | False | 34.92 | 34.94 | 0.70 | False |
| codec | codec/obfuscated-structural-1 | codec/python-3.12/opt-0/uncompyle6 | unsupported | False | 34.92 | 34.94 | 0.70 | False |
| codec | codec/obfuscated-structural-2 | codec/python-3.12/opt-0/uncompyle6 | unsupported | False | 34.92 | 34.94 | 0.70 | False |
| codec | codec/obfuscated-light-0 | codec/python-3.12/opt-0/pycdc | unsupported | False | 78.59 | 98.69 | 99.48 | False |
| codec | codec/obfuscated-light-1 | codec/python-3.12/opt-0/pycdc | unsupported | False | 78.59 | 98.69 | 99.48 | False |
| codec | codec/obfuscated-light-2 | codec/python-3.12/opt-0/pycdc | unsupported | False | 78.59 | 98.69 | 99.48 | False |
| codec | codec/obfuscated-structural-0 | codec/python-3.12/opt-0/pycdc | unsupported | False | 41.30 | 95.59 | 95.03 | False |
| codec | codec/obfuscated-structural-1 | codec/python-3.12/opt-0/pycdc | unsupported | False | 41.30 | 95.59 | 95.03 | False |
| codec | codec/obfuscated-structural-2 | codec/python-3.12/opt-0/pycdc | unsupported | False | 41.30 | 95.59 | 95.03 | False |
| codec | codec/obfuscated-light-0 | codec/python-3.12/opt-1/uncompyle6 | unsupported | False | 31.66 | 33.45 | 0.00 | False |
| codec | codec/obfuscated-light-1 | codec/python-3.12/opt-1/uncompyle6 | unsupported | False | 31.66 | 33.45 | 0.00 | False |
| codec | codec/obfuscated-light-2 | codec/python-3.12/opt-1/uncompyle6 | unsupported | False | 31.66 | 33.45 | 0.00 | False |
| codec | codec/obfuscated-structural-0 | codec/python-3.12/opt-1/uncompyle6 | unsupported | False | 34.92 | 34.94 | 0.70 | False |
| codec | codec/obfuscated-structural-1 | codec/python-3.12/opt-1/uncompyle6 | unsupported | False | 34.92 | 34.94 | 0.70 | False |
| codec | codec/obfuscated-structural-2 | codec/python-3.12/opt-1/uncompyle6 | unsupported | False | 34.92 | 34.94 | 0.70 | False |
| codec | codec/obfuscated-light-0 | codec/python-3.12/opt-1/pycdc | unsupported | False | 78.59 | 98.69 | 99.48 | False |
| codec | codec/obfuscated-light-1 | codec/python-3.12/opt-1/pycdc | unsupported | False | 78.59 | 98.69 | 99.48 | False |
| codec | codec/obfuscated-light-2 | codec/python-3.12/opt-1/pycdc | unsupported | False | 78.59 | 98.69 | 99.48 | False |
| codec | codec/obfuscated-structural-0 | codec/python-3.12/opt-1/pycdc | unsupported | False | 41.30 | 95.59 | 95.03 | False |
| codec | codec/obfuscated-structural-1 | codec/python-3.12/opt-1/pycdc | unsupported | False | 41.30 | 95.59 | 95.03 | False |
| codec | codec/obfuscated-structural-2 | codec/python-3.12/opt-1/pycdc | unsupported | False | 41.30 | 95.59 | 95.03 | False |
| codec | codec/obfuscated-light-0 | codec/python-3.12/opt-2/uncompyle6 | unsupported | False | 31.66 | 33.45 | 0.00 | False |
| codec | codec/obfuscated-light-1 | codec/python-3.12/opt-2/uncompyle6 | unsupported | False | 31.66 | 33.45 | 0.00 | False |
| codec | codec/obfuscated-light-2 | codec/python-3.12/opt-2/uncompyle6 | unsupported | False | 31.66 | 33.45 | 0.00 | False |
| codec | codec/obfuscated-structural-0 | codec/python-3.12/opt-2/uncompyle6 | unsupported | False | 34.92 | 34.94 | 0.70 | False |
| codec | codec/obfuscated-structural-1 | codec/python-3.12/opt-2/uncompyle6 | unsupported | False | 34.92 | 34.94 | 0.70 | False |
| codec | codec/obfuscated-structural-2 | codec/python-3.12/opt-2/uncompyle6 | unsupported | False | 34.92 | 34.94 | 0.70 | False |
| codec | codec/obfuscated-light-0 | codec/python-3.12/opt-2/pycdc | unsupported | False | 78.59 | 98.69 | 99.48 | False |
| codec | codec/obfuscated-light-1 | codec/python-3.12/opt-2/pycdc | unsupported | False | 78.59 | 98.69 | 99.48 | False |
| codec | codec/obfuscated-light-2 | codec/python-3.12/opt-2/pycdc | unsupported | False | 78.59 | 98.69 | 99.48 | False |
| codec | codec/obfuscated-structural-0 | codec/python-3.12/opt-2/pycdc | unsupported | False | 41.30 | 95.59 | 95.03 | False |
| codec | codec/obfuscated-structural-1 | codec/python-3.12/opt-2/pycdc | unsupported | False | 41.30 | 95.59 | 95.03 | False |
| codec | codec/obfuscated-structural-2 | codec/python-3.12/opt-2/pycdc | unsupported | False | 41.30 | 95.59 | 95.03 | False |
| codec | codec/obfuscated-light-0 | codec/python-3.14/opt-0/uncompyle6 | unsupported | False | 30.74 | 35.09 | 0.00 | False |
| codec | codec/obfuscated-light-1 | codec/python-3.14/opt-0/uncompyle6 | unsupported | False | 30.74 | 35.09 | 0.00 | False |
| codec | codec/obfuscated-light-2 | codec/python-3.14/opt-0/uncompyle6 | unsupported | False | 30.74 | 35.09 | 0.00 | False |
| codec | codec/obfuscated-structural-0 | codec/python-3.14/opt-0/uncompyle6 | unsupported | False | 33.30 | 36.23 | 0.69 | False |
| codec | codec/obfuscated-structural-1 | codec/python-3.14/opt-0/uncompyle6 | unsupported | False | 33.30 | 36.23 | 0.69 | False |
| codec | codec/obfuscated-structural-2 | codec/python-3.14/opt-0/uncompyle6 | unsupported | False | 33.30 | 36.23 | 0.69 | False |
| codec | codec/obfuscated-light-0 | codec/python-3.14/opt-0/pycdc | invalid_output | False | N/A | N/A | N/A | False |
| codec | codec/obfuscated-light-1 | codec/python-3.14/opt-0/pycdc | invalid_output | False | N/A | N/A | N/A | False |
| codec | codec/obfuscated-light-2 | codec/python-3.14/opt-0/pycdc | invalid_output | False | N/A | N/A | N/A | False |
| codec | codec/obfuscated-structural-0 | codec/python-3.14/opt-0/pycdc | invalid_output | False | N/A | N/A | N/A | False |
| codec | codec/obfuscated-structural-1 | codec/python-3.14/opt-0/pycdc | invalid_output | False | N/A | N/A | N/A | False |
| codec | codec/obfuscated-structural-2 | codec/python-3.14/opt-0/pycdc | invalid_output | False | N/A | N/A | N/A | False |
| codec | codec/obfuscated-light-0 | codec/python-3.14/opt-1/uncompyle6 | unsupported | False | 30.74 | 35.09 | 0.00 | False |
| codec | codec/obfuscated-light-1 | codec/python-3.14/opt-1/uncompyle6 | unsupported | False | 30.74 | 35.09 | 0.00 | False |
| codec | codec/obfuscated-light-2 | codec/python-3.14/opt-1/uncompyle6 | unsupported | False | 30.74 | 35.09 | 0.00 | False |
| codec | codec/obfuscated-structural-0 | codec/python-3.14/opt-1/uncompyle6 | unsupported | False | 33.30 | 36.23 | 0.69 | False |
| codec | codec/obfuscated-structural-1 | codec/python-3.14/opt-1/uncompyle6 | unsupported | False | 33.30 | 36.23 | 0.69 | False |
| codec | codec/obfuscated-structural-2 | codec/python-3.14/opt-1/uncompyle6 | unsupported | False | 33.30 | 36.23 | 0.69 | False |
| codec | codec/obfuscated-light-0 | codec/python-3.14/opt-1/pycdc | invalid_output | False | N/A | N/A | N/A | False |
| codec | codec/obfuscated-light-1 | codec/python-3.14/opt-1/pycdc | invalid_output | False | N/A | N/A | N/A | False |
| codec | codec/obfuscated-light-2 | codec/python-3.14/opt-1/pycdc | invalid_output | False | N/A | N/A | N/A | False |
| codec | codec/obfuscated-structural-0 | codec/python-3.14/opt-1/pycdc | invalid_output | False | N/A | N/A | N/A | False |
| codec | codec/obfuscated-structural-1 | codec/python-3.14/opt-1/pycdc | invalid_output | False | N/A | N/A | N/A | False |
| codec | codec/obfuscated-structural-2 | codec/python-3.14/opt-1/pycdc | invalid_output | False | N/A | N/A | N/A | False |
| codec | codec/obfuscated-light-0 | codec/python-3.14/opt-2/uncompyle6 | unsupported | False | 30.74 | 35.09 | 0.00 | False |
| codec | codec/obfuscated-light-1 | codec/python-3.14/opt-2/uncompyle6 | unsupported | False | 30.74 | 35.09 | 0.00 | False |
| codec | codec/obfuscated-light-2 | codec/python-3.14/opt-2/uncompyle6 | unsupported | False | 30.74 | 35.09 | 0.00 | False |
| codec | codec/obfuscated-structural-0 | codec/python-3.14/opt-2/uncompyle6 | unsupported | False | 33.30 | 36.23 | 0.69 | False |
| codec | codec/obfuscated-structural-1 | codec/python-3.14/opt-2/uncompyle6 | unsupported | False | 33.30 | 36.23 | 0.69 | False |
| codec | codec/obfuscated-structural-2 | codec/python-3.14/opt-2/uncompyle6 | unsupported | False | 33.30 | 36.23 | 0.69 | False |
| codec | codec/obfuscated-light-0 | codec/python-3.14/opt-2/pycdc | invalid_output | False | N/A | N/A | N/A | False |
| codec | codec/obfuscated-light-1 | codec/python-3.14/opt-2/pycdc | invalid_output | False | N/A | N/A | N/A | False |
| codec | codec/obfuscated-light-2 | codec/python-3.14/opt-2/pycdc | invalid_output | False | N/A | N/A | N/A | False |
| codec | codec/obfuscated-structural-0 | codec/python-3.14/opt-2/pycdc | invalid_output | False | N/A | N/A | N/A | False |
| codec | codec/obfuscated-structural-1 | codec/python-3.14/opt-2/pycdc | invalid_output | False | N/A | N/A | N/A | False |
| codec | codec/obfuscated-structural-2 | codec/python-3.14/opt-2/pycdc | invalid_output | False | N/A | N/A | N/A | False |
| codec | codec/obfuscated-light-0 | codec/python-3.4/opt-0/uncompyle6 | success | True | 100.00 | 100.00 | 100.00 | True |
| codec | codec/obfuscated-light-1 | codec/python-3.4/opt-0/uncompyle6 | success | True | 100.00 | 100.00 | 100.00 | True |
| codec | codec/obfuscated-light-2 | codec/python-3.4/opt-0/uncompyle6 | success | True | 100.00 | 100.00 | 100.00 | True |
| codec | codec/obfuscated-structural-0 | codec/python-3.4/opt-0/uncompyle6 | success | True | 63.19 | 96.45 | 95.77 | False |
| codec | codec/obfuscated-structural-1 | codec/python-3.4/opt-0/uncompyle6 | success | True | 63.19 | 96.45 | 95.77 | False |
| codec | codec/obfuscated-structural-2 | codec/python-3.4/opt-0/uncompyle6 | success | True | 63.19 | 96.45 | 95.77 | False |
| codec | codec/obfuscated-light-0 | codec/python-3.4/opt-0/pycdc | invalid_output | False | 29.69 | 40.22 | 0.00 | False |
| codec | codec/obfuscated-light-1 | codec/python-3.4/opt-0/pycdc | invalid_output | False | 29.69 | 40.22 | 0.00 | False |
| codec | codec/obfuscated-light-2 | codec/python-3.4/opt-0/pycdc | invalid_output | False | 29.69 | 40.22 | 0.00 | False |
| codec | codec/obfuscated-structural-0 | codec/python-3.4/opt-0/pycdc | invalid_output | False | 31.43 | 39.11 | 0.73 | False |
| codec | codec/obfuscated-structural-1 | codec/python-3.4/opt-0/pycdc | invalid_output | False | 31.43 | 39.11 | 0.73 | False |
| codec | codec/obfuscated-structural-2 | codec/python-3.4/opt-0/pycdc | invalid_output | False | 31.43 | 39.11 | 0.73 | False |
| codec | codec/obfuscated-light-0 | codec/python-3.4/opt-1/uncompyle6 | success | True | 100.00 | 100.00 | 100.00 | True |
| codec | codec/obfuscated-light-1 | codec/python-3.4/opt-1/uncompyle6 | success | True | 100.00 | 100.00 | 100.00 | True |
| codec | codec/obfuscated-light-2 | codec/python-3.4/opt-1/uncompyle6 | success | True | 100.00 | 100.00 | 100.00 | True |
| codec | codec/obfuscated-structural-0 | codec/python-3.4/opt-1/uncompyle6 | success | True | 63.19 | 96.45 | 95.77 | False |
| codec | codec/obfuscated-structural-1 | codec/python-3.4/opt-1/uncompyle6 | success | True | 63.19 | 96.45 | 95.77 | False |
| codec | codec/obfuscated-structural-2 | codec/python-3.4/opt-1/uncompyle6 | success | True | 63.19 | 96.45 | 95.77 | False |
| codec | codec/obfuscated-light-0 | codec/python-3.4/opt-1/pycdc | invalid_output | False | 29.69 | 40.22 | 0.00 | False |
| codec | codec/obfuscated-light-1 | codec/python-3.4/opt-1/pycdc | invalid_output | False | 29.69 | 40.22 | 0.00 | False |
| codec | codec/obfuscated-light-2 | codec/python-3.4/opt-1/pycdc | invalid_output | False | 29.69 | 40.22 | 0.00 | False |
| codec | codec/obfuscated-structural-0 | codec/python-3.4/opt-1/pycdc | invalid_output | False | 31.43 | 39.11 | 0.73 | False |
| codec | codec/obfuscated-structural-1 | codec/python-3.4/opt-1/pycdc | invalid_output | False | 31.43 | 39.11 | 0.73 | False |
| codec | codec/obfuscated-structural-2 | codec/python-3.4/opt-1/pycdc | invalid_output | False | 31.43 | 39.11 | 0.73 | False |
| codec | codec/obfuscated-light-0 | codec/python-3.4/opt-2/uncompyle6 | success | True | 100.00 | 100.00 | 100.00 | True |
| codec | codec/obfuscated-light-1 | codec/python-3.4/opt-2/uncompyle6 | success | True | 100.00 | 100.00 | 100.00 | True |
| codec | codec/obfuscated-light-2 | codec/python-3.4/opt-2/uncompyle6 | success | True | 100.00 | 100.00 | 100.00 | True |
| codec | codec/obfuscated-structural-0 | codec/python-3.4/opt-2/uncompyle6 | success | True | 63.19 | 96.45 | 95.77 | False |
| codec | codec/obfuscated-structural-1 | codec/python-3.4/opt-2/uncompyle6 | success | True | 63.19 | 96.45 | 95.77 | False |
| codec | codec/obfuscated-structural-2 | codec/python-3.4/opt-2/uncompyle6 | success | True | 63.19 | 96.45 | 95.77 | False |
| codec | codec/obfuscated-light-0 | codec/python-3.4/opt-2/pycdc | invalid_output | False | 29.69 | 40.22 | 0.00 | False |
| codec | codec/obfuscated-light-1 | codec/python-3.4/opt-2/pycdc | invalid_output | False | 29.69 | 40.22 | 0.00 | False |
| codec | codec/obfuscated-light-2 | codec/python-3.4/opt-2/pycdc | invalid_output | False | 29.69 | 40.22 | 0.00 | False |
| codec | codec/obfuscated-structural-0 | codec/python-3.4/opt-2/pycdc | invalid_output | False | 31.43 | 39.11 | 0.73 | False |
| codec | codec/obfuscated-structural-1 | codec/python-3.4/opt-2/pycdc | invalid_output | False | 31.43 | 39.11 | 0.73 | False |
| codec | codec/obfuscated-structural-2 | codec/python-3.4/opt-2/pycdc | invalid_output | False | 31.43 | 39.11 | 0.73 | False |
| codec | codec/obfuscated-light-0 | codec/python-3.8/opt-0/uncompyle6 | success | True | 100.00 | 100.00 | 100.00 | True |
| codec | codec/obfuscated-light-1 | codec/python-3.8/opt-0/uncompyle6 | success | True | 100.00 | 100.00 | 100.00 | True |
| codec | codec/obfuscated-light-2 | codec/python-3.8/opt-0/uncompyle6 | success | True | 100.00 | 100.00 | 100.00 | True |
| codec | codec/obfuscated-structural-0 | codec/python-3.8/opt-0/uncompyle6 | success | True | 63.19 | 96.45 | 95.77 | False |
| codec | codec/obfuscated-structural-1 | codec/python-3.8/opt-0/uncompyle6 | success | True | 63.19 | 96.45 | 95.77 | False |
| codec | codec/obfuscated-structural-2 | codec/python-3.8/opt-0/uncompyle6 | success | True | 63.19 | 96.45 | 95.77 | False |
| codec | codec/obfuscated-light-0 | codec/python-3.8/opt-0/pycdc | invalid_output | False | 29.39 | 42.05 | 0.00 | False |
| codec | codec/obfuscated-light-1 | codec/python-3.8/opt-0/pycdc | invalid_output | False | 29.39 | 42.05 | 0.00 | False |
| codec | codec/obfuscated-light-2 | codec/python-3.8/opt-0/pycdc | invalid_output | False | 29.39 | 42.05 | 0.00 | False |
| codec | codec/obfuscated-structural-0 | codec/python-3.8/opt-0/pycdc | invalid_output | False | 33.29 | 40.55 | 0.71 | False |
| codec | codec/obfuscated-structural-1 | codec/python-3.8/opt-0/pycdc | invalid_output | False | 33.29 | 40.55 | 0.71 | False |
| codec | codec/obfuscated-structural-2 | codec/python-3.8/opt-0/pycdc | invalid_output | False | 33.29 | 40.55 | 0.71 | False |
| codec | codec/obfuscated-light-0 | codec/python-3.8/opt-1/uncompyle6 | success | True | 100.00 | 100.00 | 100.00 | True |
| codec | codec/obfuscated-light-1 | codec/python-3.8/opt-1/uncompyle6 | success | True | 100.00 | 100.00 | 100.00 | True |
| codec | codec/obfuscated-light-2 | codec/python-3.8/opt-1/uncompyle6 | success | True | 100.00 | 100.00 | 100.00 | True |
| codec | codec/obfuscated-structural-0 | codec/python-3.8/opt-1/uncompyle6 | success | True | 63.19 | 96.45 | 95.77 | False |
| codec | codec/obfuscated-structural-1 | codec/python-3.8/opt-1/uncompyle6 | success | True | 63.19 | 96.45 | 95.77 | False |
| codec | codec/obfuscated-structural-2 | codec/python-3.8/opt-1/uncompyle6 | success | True | 63.19 | 96.45 | 95.77 | False |
| codec | codec/obfuscated-light-0 | codec/python-3.8/opt-1/pycdc | invalid_output | False | 29.39 | 42.05 | 0.00 | False |
| codec | codec/obfuscated-light-1 | codec/python-3.8/opt-1/pycdc | invalid_output | False | 29.39 | 42.05 | 0.00 | False |
| codec | codec/obfuscated-light-2 | codec/python-3.8/opt-1/pycdc | invalid_output | False | 29.39 | 42.05 | 0.00 | False |
| codec | codec/obfuscated-structural-0 | codec/python-3.8/opt-1/pycdc | invalid_output | False | 33.29 | 40.55 | 0.71 | False |
| codec | codec/obfuscated-structural-1 | codec/python-3.8/opt-1/pycdc | invalid_output | False | 33.29 | 40.55 | 0.71 | False |
| codec | codec/obfuscated-structural-2 | codec/python-3.8/opt-1/pycdc | invalid_output | False | 33.29 | 40.55 | 0.71 | False |
| codec | codec/obfuscated-light-0 | codec/python-3.8/opt-2/uncompyle6 | success | True | 100.00 | 100.00 | 100.00 | True |
| codec | codec/obfuscated-light-1 | codec/python-3.8/opt-2/uncompyle6 | success | True | 100.00 | 100.00 | 100.00 | True |
| codec | codec/obfuscated-light-2 | codec/python-3.8/opt-2/uncompyle6 | success | True | 100.00 | 100.00 | 100.00 | True |
| codec | codec/obfuscated-structural-0 | codec/python-3.8/opt-2/uncompyle6 | success | True | 63.19 | 96.45 | 95.77 | False |
| codec | codec/obfuscated-structural-1 | codec/python-3.8/opt-2/uncompyle6 | success | True | 63.19 | 96.45 | 95.77 | False |
| codec | codec/obfuscated-structural-2 | codec/python-3.8/opt-2/uncompyle6 | success | True | 63.19 | 96.45 | 95.77 | False |
| codec | codec/obfuscated-light-0 | codec/python-3.8/opt-2/pycdc | invalid_output | False | 29.39 | 42.05 | 0.00 | False |
| codec | codec/obfuscated-light-1 | codec/python-3.8/opt-2/pycdc | invalid_output | False | 29.39 | 42.05 | 0.00 | False |
| codec | codec/obfuscated-light-2 | codec/python-3.8/opt-2/pycdc | invalid_output | False | 29.39 | 42.05 | 0.00 | False |
| codec | codec/obfuscated-structural-0 | codec/python-3.8/opt-2/pycdc | invalid_output | False | 33.29 | 40.55 | 0.71 | False |
| codec | codec/obfuscated-structural-1 | codec/python-3.8/opt-2/pycdc | invalid_output | False | 33.29 | 40.55 | 0.71 | False |
| codec | codec/obfuscated-structural-2 | codec/python-3.8/opt-2/pycdc | invalid_output | False | 33.29 | 40.55 | 0.71 | False |
| dependencies | dependencies/obfuscated-light-0 | dependencies/python-3.12/opt-0/uncompyle6 | unsupported | False | 19.71 | 33.55 | 1.10 | False |
| dependencies | dependencies/obfuscated-light-1 | dependencies/python-3.12/opt-0/uncompyle6 | unsupported | False | 19.71 | 33.55 | 1.10 | False |
| dependencies | dependencies/obfuscated-light-2 | dependencies/python-3.12/opt-0/uncompyle6 | unsupported | False | 19.71 | 33.55 | 1.10 | False |
| dependencies | dependencies/obfuscated-structural-0 | dependencies/python-3.12/opt-0/uncompyle6 | unsupported | False | 21.39 | 33.83 | 1.04 | False |
| dependencies | dependencies/obfuscated-structural-1 | dependencies/python-3.12/opt-0/uncompyle6 | unsupported | False | 21.39 | 33.83 | 1.04 | False |
| dependencies | dependencies/obfuscated-structural-2 | dependencies/python-3.12/opt-0/uncompyle6 | unsupported | False | 21.39 | 33.83 | 1.04 | False |
| dependencies | dependencies/obfuscated-light-0 | dependencies/python-3.12/opt-0/pycdc | success | True | 99.72 | 99.99 | 99.99 | False |
| dependencies | dependencies/obfuscated-light-1 | dependencies/python-3.12/opt-0/pycdc | success | True | 99.72 | 99.99 | 99.99 | False |
| dependencies | dependencies/obfuscated-light-2 | dependencies/python-3.12/opt-0/pycdc | success | True | 99.72 | 99.99 | 99.99 | False |
| dependencies | dependencies/obfuscated-structural-0 | dependencies/python-3.12/opt-0/pycdc | success | True | 73.88 | 98.25 | 98.75 | False |
| dependencies | dependencies/obfuscated-structural-1 | dependencies/python-3.12/opt-0/pycdc | success | True | 73.88 | 98.25 | 98.75 | False |
| dependencies | dependencies/obfuscated-structural-2 | dependencies/python-3.12/opt-0/pycdc | success | True | 73.88 | 98.25 | 98.75 | False |
| dependencies | dependencies/obfuscated-light-0 | dependencies/python-3.12/opt-1/uncompyle6 | unsupported | False | 19.71 | 33.55 | 1.10 | False |
| dependencies | dependencies/obfuscated-light-1 | dependencies/python-3.12/opt-1/uncompyle6 | unsupported | False | 19.71 | 33.55 | 1.10 | False |
| dependencies | dependencies/obfuscated-light-2 | dependencies/python-3.12/opt-1/uncompyle6 | unsupported | False | 19.71 | 33.55 | 1.10 | False |
| dependencies | dependencies/obfuscated-structural-0 | dependencies/python-3.12/opt-1/uncompyle6 | unsupported | False | 21.39 | 33.83 | 1.04 | False |
| dependencies | dependencies/obfuscated-structural-1 | dependencies/python-3.12/opt-1/uncompyle6 | unsupported | False | 21.39 | 33.83 | 1.04 | False |
| dependencies | dependencies/obfuscated-structural-2 | dependencies/python-3.12/opt-1/uncompyle6 | unsupported | False | 21.39 | 33.83 | 1.04 | False |
| dependencies | dependencies/obfuscated-light-0 | dependencies/python-3.12/opt-1/pycdc | success | True | 99.72 | 99.99 | 99.99 | False |
| dependencies | dependencies/obfuscated-light-1 | dependencies/python-3.12/opt-1/pycdc | success | True | 99.72 | 99.99 | 99.99 | False |
| dependencies | dependencies/obfuscated-light-2 | dependencies/python-3.12/opt-1/pycdc | success | True | 99.72 | 99.99 | 99.99 | False |
| dependencies | dependencies/obfuscated-structural-0 | dependencies/python-3.12/opt-1/pycdc | success | True | 73.88 | 98.25 | 98.75 | False |
| dependencies | dependencies/obfuscated-structural-1 | dependencies/python-3.12/opt-1/pycdc | success | True | 73.88 | 98.25 | 98.75 | False |
| dependencies | dependencies/obfuscated-structural-2 | dependencies/python-3.12/opt-1/pycdc | success | True | 73.88 | 98.25 | 98.75 | False |
| dependencies | dependencies/obfuscated-light-0 | dependencies/python-3.12/opt-2/uncompyle6 | unsupported | False | 19.71 | 33.55 | 1.10 | False |
| dependencies | dependencies/obfuscated-light-1 | dependencies/python-3.12/opt-2/uncompyle6 | unsupported | False | 19.71 | 33.55 | 1.10 | False |
| dependencies | dependencies/obfuscated-light-2 | dependencies/python-3.12/opt-2/uncompyle6 | unsupported | False | 19.71 | 33.55 | 1.10 | False |
| dependencies | dependencies/obfuscated-structural-0 | dependencies/python-3.12/opt-2/uncompyle6 | unsupported | False | 21.39 | 33.83 | 1.04 | False |
| dependencies | dependencies/obfuscated-structural-1 | dependencies/python-3.12/opt-2/uncompyle6 | unsupported | False | 21.39 | 33.83 | 1.04 | False |
| dependencies | dependencies/obfuscated-structural-2 | dependencies/python-3.12/opt-2/uncompyle6 | unsupported | False | 21.39 | 33.83 | 1.04 | False |
| dependencies | dependencies/obfuscated-light-0 | dependencies/python-3.12/opt-2/pycdc | success | True | 99.72 | 99.99 | 99.99 | False |
| dependencies | dependencies/obfuscated-light-1 | dependencies/python-3.12/opt-2/pycdc | success | True | 99.72 | 99.99 | 99.99 | False |
| dependencies | dependencies/obfuscated-light-2 | dependencies/python-3.12/opt-2/pycdc | success | True | 99.72 | 99.99 | 99.99 | False |
| dependencies | dependencies/obfuscated-structural-0 | dependencies/python-3.12/opt-2/pycdc | success | True | 73.88 | 98.25 | 98.75 | False |
| dependencies | dependencies/obfuscated-structural-1 | dependencies/python-3.12/opt-2/pycdc | success | True | 73.88 | 98.25 | 98.75 | False |
| dependencies | dependencies/obfuscated-structural-2 | dependencies/python-3.12/opt-2/pycdc | success | True | 73.88 | 98.25 | 98.75 | False |
| dependencies | dependencies/obfuscated-light-0 | dependencies/python-3.14/opt-0/uncompyle6 | unsupported | False | 18.94 | 35.11 | 1.09 | False |
| dependencies | dependencies/obfuscated-light-1 | dependencies/python-3.14/opt-0/uncompyle6 | unsupported | False | 18.94 | 35.11 | 1.09 | False |
| dependencies | dependencies/obfuscated-light-2 | dependencies/python-3.14/opt-0/uncompyle6 | unsupported | False | 18.94 | 35.11 | 1.09 | False |
| dependencies | dependencies/obfuscated-structural-0 | dependencies/python-3.14/opt-0/uncompyle6 | unsupported | False | 20.05 | 35.10 | 1.04 | False |
| dependencies | dependencies/obfuscated-structural-1 | dependencies/python-3.14/opt-0/uncompyle6 | unsupported | False | 20.05 | 35.10 | 1.04 | False |
| dependencies | dependencies/obfuscated-structural-2 | dependencies/python-3.14/opt-0/uncompyle6 | unsupported | False | 20.05 | 35.10 | 1.04 | False |
| dependencies | dependencies/obfuscated-light-0 | dependencies/python-3.14/opt-0/pycdc | invalid_output | False | N/A | N/A | N/A | False |
| dependencies | dependencies/obfuscated-light-1 | dependencies/python-3.14/opt-0/pycdc | invalid_output | False | N/A | N/A | N/A | False |
| dependencies | dependencies/obfuscated-light-2 | dependencies/python-3.14/opt-0/pycdc | invalid_output | False | N/A | N/A | N/A | False |
| dependencies | dependencies/obfuscated-structural-0 | dependencies/python-3.14/opt-0/pycdc | invalid_output | False | N/A | N/A | N/A | False |
| dependencies | dependencies/obfuscated-structural-1 | dependencies/python-3.14/opt-0/pycdc | invalid_output | False | N/A | N/A | N/A | False |
| dependencies | dependencies/obfuscated-structural-2 | dependencies/python-3.14/opt-0/pycdc | invalid_output | False | N/A | N/A | N/A | False |
| dependencies | dependencies/obfuscated-light-0 | dependencies/python-3.14/opt-1/uncompyle6 | unsupported | False | 18.94 | 35.11 | 1.09 | False |
| dependencies | dependencies/obfuscated-light-1 | dependencies/python-3.14/opt-1/uncompyle6 | unsupported | False | 18.94 | 35.11 | 1.09 | False |
| dependencies | dependencies/obfuscated-light-2 | dependencies/python-3.14/opt-1/uncompyle6 | unsupported | False | 18.94 | 35.11 | 1.09 | False |
| dependencies | dependencies/obfuscated-structural-0 | dependencies/python-3.14/opt-1/uncompyle6 | unsupported | False | 20.05 | 35.10 | 1.04 | False |
| dependencies | dependencies/obfuscated-structural-1 | dependencies/python-3.14/opt-1/uncompyle6 | unsupported | False | 20.05 | 35.10 | 1.04 | False |
| dependencies | dependencies/obfuscated-structural-2 | dependencies/python-3.14/opt-1/uncompyle6 | unsupported | False | 20.05 | 35.10 | 1.04 | False |
| dependencies | dependencies/obfuscated-light-0 | dependencies/python-3.14/opt-1/pycdc | invalid_output | False | N/A | N/A | N/A | False |
| dependencies | dependencies/obfuscated-light-1 | dependencies/python-3.14/opt-1/pycdc | invalid_output | False | N/A | N/A | N/A | False |
| dependencies | dependencies/obfuscated-light-2 | dependencies/python-3.14/opt-1/pycdc | invalid_output | False | N/A | N/A | N/A | False |
| dependencies | dependencies/obfuscated-structural-0 | dependencies/python-3.14/opt-1/pycdc | invalid_output | False | N/A | N/A | N/A | False |
| dependencies | dependencies/obfuscated-structural-1 | dependencies/python-3.14/opt-1/pycdc | invalid_output | False | N/A | N/A | N/A | False |
| dependencies | dependencies/obfuscated-structural-2 | dependencies/python-3.14/opt-1/pycdc | invalid_output | False | N/A | N/A | N/A | False |
| dependencies | dependencies/obfuscated-light-0 | dependencies/python-3.14/opt-2/uncompyle6 | unsupported | False | 18.94 | 35.11 | 1.09 | False |
| dependencies | dependencies/obfuscated-light-1 | dependencies/python-3.14/opt-2/uncompyle6 | unsupported | False | 18.94 | 35.11 | 1.09 | False |
| dependencies | dependencies/obfuscated-light-2 | dependencies/python-3.14/opt-2/uncompyle6 | unsupported | False | 18.94 | 35.11 | 1.09 | False |
| dependencies | dependencies/obfuscated-structural-0 | dependencies/python-3.14/opt-2/uncompyle6 | unsupported | False | 20.05 | 35.10 | 1.04 | False |
| dependencies | dependencies/obfuscated-structural-1 | dependencies/python-3.14/opt-2/uncompyle6 | unsupported | False | 20.05 | 35.10 | 1.04 | False |
| dependencies | dependencies/obfuscated-structural-2 | dependencies/python-3.14/opt-2/uncompyle6 | unsupported | False | 20.05 | 35.10 | 1.04 | False |
| dependencies | dependencies/obfuscated-light-0 | dependencies/python-3.14/opt-2/pycdc | invalid_output | False | N/A | N/A | N/A | False |
| dependencies | dependencies/obfuscated-light-1 | dependencies/python-3.14/opt-2/pycdc | invalid_output | False | N/A | N/A | N/A | False |
| dependencies | dependencies/obfuscated-light-2 | dependencies/python-3.14/opt-2/pycdc | invalid_output | False | N/A | N/A | N/A | False |
| dependencies | dependencies/obfuscated-structural-0 | dependencies/python-3.14/opt-2/pycdc | invalid_output | False | N/A | N/A | N/A | False |
| dependencies | dependencies/obfuscated-structural-1 | dependencies/python-3.14/opt-2/pycdc | invalid_output | False | N/A | N/A | N/A | False |
| dependencies | dependencies/obfuscated-structural-2 | dependencies/python-3.14/opt-2/pycdc | invalid_output | False | N/A | N/A | N/A | False |
| dependencies | dependencies/obfuscated-light-0 | dependencies/python-3.4/opt-0/uncompyle6 | success | True | 100.00 | 100.00 | 100.00 | True |
| dependencies | dependencies/obfuscated-light-1 | dependencies/python-3.4/opt-0/uncompyle6 | success | True | 100.00 | 100.00 | 100.00 | True |
| dependencies | dependencies/obfuscated-light-2 | dependencies/python-3.4/opt-0/uncompyle6 | success | True | 100.00 | 100.00 | 100.00 | True |
| dependencies | dependencies/obfuscated-structural-0 | dependencies/python-3.4/opt-0/uncompyle6 | success | True | 75.37 | 98.26 | 98.71 | False |
| dependencies | dependencies/obfuscated-structural-1 | dependencies/python-3.4/opt-0/uncompyle6 | success | True | 75.37 | 98.26 | 98.71 | False |
| dependencies | dependencies/obfuscated-structural-2 | dependencies/python-3.4/opt-0/uncompyle6 | success | True | 75.37 | 98.26 | 98.71 | False |
| dependencies | dependencies/obfuscated-light-0 | dependencies/python-3.4/opt-0/pycdc | behavior_mismatch | False | 98.78 | 99.96 | 99.96 | False |
| dependencies | dependencies/obfuscated-light-1 | dependencies/python-3.4/opt-0/pycdc | behavior_mismatch | False | 98.78 | 99.96 | 99.96 | False |
| dependencies | dependencies/obfuscated-light-2 | dependencies/python-3.4/opt-0/pycdc | behavior_mismatch | False | 98.78 | 99.96 | 99.96 | False |
| dependencies | dependencies/obfuscated-structural-0 | dependencies/python-3.4/opt-0/pycdc | behavior_mismatch | False | 73.74 | 98.38 | 98.80 | False |
| dependencies | dependencies/obfuscated-structural-1 | dependencies/python-3.4/opt-0/pycdc | behavior_mismatch | False | 73.74 | 98.38 | 98.80 | False |
| dependencies | dependencies/obfuscated-structural-2 | dependencies/python-3.4/opt-0/pycdc | behavior_mismatch | False | 73.74 | 98.38 | 98.80 | False |
| dependencies | dependencies/obfuscated-light-0 | dependencies/python-3.4/opt-1/uncompyle6 | success | True | 100.00 | 100.00 | 100.00 | True |
| dependencies | dependencies/obfuscated-light-1 | dependencies/python-3.4/opt-1/uncompyle6 | success | True | 100.00 | 100.00 | 100.00 | True |
| dependencies | dependencies/obfuscated-light-2 | dependencies/python-3.4/opt-1/uncompyle6 | success | True | 100.00 | 100.00 | 100.00 | True |
| dependencies | dependencies/obfuscated-structural-0 | dependencies/python-3.4/opt-1/uncompyle6 | success | True | 75.37 | 98.26 | 98.71 | False |
| dependencies | dependencies/obfuscated-structural-1 | dependencies/python-3.4/opt-1/uncompyle6 | success | True | 75.37 | 98.26 | 98.71 | False |
| dependencies | dependencies/obfuscated-structural-2 | dependencies/python-3.4/opt-1/uncompyle6 | success | True | 75.37 | 98.26 | 98.71 | False |
| dependencies | dependencies/obfuscated-light-0 | dependencies/python-3.4/opt-1/pycdc | behavior_mismatch | False | 98.78 | 99.96 | 99.96 | False |
| dependencies | dependencies/obfuscated-light-1 | dependencies/python-3.4/opt-1/pycdc | behavior_mismatch | False | 98.78 | 99.96 | 99.96 | False |
| dependencies | dependencies/obfuscated-light-2 | dependencies/python-3.4/opt-1/pycdc | behavior_mismatch | False | 98.78 | 99.96 | 99.96 | False |
| dependencies | dependencies/obfuscated-structural-0 | dependencies/python-3.4/opt-1/pycdc | behavior_mismatch | False | 73.74 | 98.38 | 98.80 | False |
| dependencies | dependencies/obfuscated-structural-1 | dependencies/python-3.4/opt-1/pycdc | behavior_mismatch | False | 73.74 | 98.38 | 98.80 | False |
| dependencies | dependencies/obfuscated-structural-2 | dependencies/python-3.4/opt-1/pycdc | behavior_mismatch | False | 73.74 | 98.38 | 98.80 | False |
| dependencies | dependencies/obfuscated-light-0 | dependencies/python-3.4/opt-2/uncompyle6 | success | True | 100.00 | 100.00 | 100.00 | True |
| dependencies | dependencies/obfuscated-light-1 | dependencies/python-3.4/opt-2/uncompyle6 | success | True | 100.00 | 100.00 | 100.00 | True |
| dependencies | dependencies/obfuscated-light-2 | dependencies/python-3.4/opt-2/uncompyle6 | success | True | 100.00 | 100.00 | 100.00 | True |
| dependencies | dependencies/obfuscated-structural-0 | dependencies/python-3.4/opt-2/uncompyle6 | success | True | 75.37 | 98.26 | 98.71 | False |
| dependencies | dependencies/obfuscated-structural-1 | dependencies/python-3.4/opt-2/uncompyle6 | success | True | 75.37 | 98.26 | 98.71 | False |
| dependencies | dependencies/obfuscated-structural-2 | dependencies/python-3.4/opt-2/uncompyle6 | success | True | 75.37 | 98.26 | 98.71 | False |
| dependencies | dependencies/obfuscated-light-0 | dependencies/python-3.4/opt-2/pycdc | behavior_mismatch | False | 98.78 | 99.96 | 99.96 | False |
| dependencies | dependencies/obfuscated-light-1 | dependencies/python-3.4/opt-2/pycdc | behavior_mismatch | False | 98.78 | 99.96 | 99.96 | False |
| dependencies | dependencies/obfuscated-light-2 | dependencies/python-3.4/opt-2/pycdc | behavior_mismatch | False | 98.78 | 99.96 | 99.96 | False |
| dependencies | dependencies/obfuscated-structural-0 | dependencies/python-3.4/opt-2/pycdc | behavior_mismatch | False | 73.74 | 98.38 | 98.80 | False |
| dependencies | dependencies/obfuscated-structural-1 | dependencies/python-3.4/opt-2/pycdc | behavior_mismatch | False | 73.74 | 98.38 | 98.80 | False |
| dependencies | dependencies/obfuscated-structural-2 | dependencies/python-3.4/opt-2/pycdc | behavior_mismatch | False | 73.74 | 98.38 | 98.80 | False |
| dependencies | dependencies/obfuscated-light-0 | dependencies/python-3.8/opt-0/uncompyle6 | success | True | 99.44 | 99.98 | 100.00 | False |
| dependencies | dependencies/obfuscated-light-1 | dependencies/python-3.8/opt-0/uncompyle6 | success | True | 99.44 | 99.98 | 100.00 | False |
| dependencies | dependencies/obfuscated-light-2 | dependencies/python-3.8/opt-0/uncompyle6 | success | True | 99.44 | 99.98 | 100.00 | False |
| dependencies | dependencies/obfuscated-structural-0 | dependencies/python-3.8/opt-0/uncompyle6 | success | True | 74.72 | 98.21 | 98.70 | False |
| dependencies | dependencies/obfuscated-structural-1 | dependencies/python-3.8/opt-0/uncompyle6 | success | True | 74.72 | 98.21 | 98.70 | False |
| dependencies | dependencies/obfuscated-structural-2 | dependencies/python-3.8/opt-0/uncompyle6 | success | True | 74.72 | 98.21 | 98.70 | False |
| dependencies | dependencies/obfuscated-light-0 | dependencies/python-3.8/opt-0/pycdc | behavior_mismatch | False | 98.78 | 99.96 | 99.96 | False |
| dependencies | dependencies/obfuscated-light-1 | dependencies/python-3.8/opt-0/pycdc | behavior_mismatch | False | 98.78 | 99.96 | 99.96 | False |
| dependencies | dependencies/obfuscated-light-2 | dependencies/python-3.8/opt-0/pycdc | behavior_mismatch | False | 98.78 | 99.96 | 99.96 | False |
| dependencies | dependencies/obfuscated-structural-0 | dependencies/python-3.8/opt-0/pycdc | behavior_mismatch | False | 73.74 | 98.38 | 98.80 | False |
| dependencies | dependencies/obfuscated-structural-1 | dependencies/python-3.8/opt-0/pycdc | behavior_mismatch | False | 73.74 | 98.38 | 98.80 | False |
| dependencies | dependencies/obfuscated-structural-2 | dependencies/python-3.8/opt-0/pycdc | behavior_mismatch | False | 73.74 | 98.38 | 98.80 | False |
| dependencies | dependencies/obfuscated-light-0 | dependencies/python-3.8/opt-1/uncompyle6 | success | True | 99.44 | 99.98 | 100.00 | False |
| dependencies | dependencies/obfuscated-light-1 | dependencies/python-3.8/opt-1/uncompyle6 | success | True | 99.44 | 99.98 | 100.00 | False |
| dependencies | dependencies/obfuscated-light-2 | dependencies/python-3.8/opt-1/uncompyle6 | success | True | 99.44 | 99.98 | 100.00 | False |
| dependencies | dependencies/obfuscated-structural-0 | dependencies/python-3.8/opt-1/uncompyle6 | success | True | 74.72 | 98.21 | 98.70 | False |
| dependencies | dependencies/obfuscated-structural-1 | dependencies/python-3.8/opt-1/uncompyle6 | success | True | 74.72 | 98.21 | 98.70 | False |
| dependencies | dependencies/obfuscated-structural-2 | dependencies/python-3.8/opt-1/uncompyle6 | success | True | 74.72 | 98.21 | 98.70 | False |
| dependencies | dependencies/obfuscated-light-0 | dependencies/python-3.8/opt-1/pycdc | behavior_mismatch | False | 98.78 | 99.96 | 99.96 | False |
| dependencies | dependencies/obfuscated-light-1 | dependencies/python-3.8/opt-1/pycdc | behavior_mismatch | False | 98.78 | 99.96 | 99.96 | False |
| dependencies | dependencies/obfuscated-light-2 | dependencies/python-3.8/opt-1/pycdc | behavior_mismatch | False | 98.78 | 99.96 | 99.96 | False |
| dependencies | dependencies/obfuscated-structural-0 | dependencies/python-3.8/opt-1/pycdc | behavior_mismatch | False | 73.74 | 98.38 | 98.80 | False |
| dependencies | dependencies/obfuscated-structural-1 | dependencies/python-3.8/opt-1/pycdc | behavior_mismatch | False | 73.74 | 98.38 | 98.80 | False |
| dependencies | dependencies/obfuscated-structural-2 | dependencies/python-3.8/opt-1/pycdc | behavior_mismatch | False | 73.74 | 98.38 | 98.80 | False |
| dependencies | dependencies/obfuscated-light-0 | dependencies/python-3.8/opt-2/uncompyle6 | success | True | 99.44 | 99.98 | 100.00 | False |
| dependencies | dependencies/obfuscated-light-1 | dependencies/python-3.8/opt-2/uncompyle6 | success | True | 99.44 | 99.98 | 100.00 | False |
| dependencies | dependencies/obfuscated-light-2 | dependencies/python-3.8/opt-2/uncompyle6 | success | True | 99.44 | 99.98 | 100.00 | False |
| dependencies | dependencies/obfuscated-structural-0 | dependencies/python-3.8/opt-2/uncompyle6 | success | True | 74.72 | 98.21 | 98.70 | False |
| dependencies | dependencies/obfuscated-structural-1 | dependencies/python-3.8/opt-2/uncompyle6 | success | True | 74.72 | 98.21 | 98.70 | False |
| dependencies | dependencies/obfuscated-structural-2 | dependencies/python-3.8/opt-2/uncompyle6 | success | True | 74.72 | 98.21 | 98.70 | False |
| dependencies | dependencies/obfuscated-light-0 | dependencies/python-3.8/opt-2/pycdc | behavior_mismatch | False | 98.78 | 99.96 | 99.96 | False |
| dependencies | dependencies/obfuscated-light-1 | dependencies/python-3.8/opt-2/pycdc | behavior_mismatch | False | 98.78 | 99.96 | 99.96 | False |
| dependencies | dependencies/obfuscated-light-2 | dependencies/python-3.8/opt-2/pycdc | behavior_mismatch | False | 98.78 | 99.96 | 99.96 | False |
| dependencies | dependencies/obfuscated-structural-0 | dependencies/python-3.8/opt-2/pycdc | behavior_mismatch | False | 73.74 | 98.38 | 98.80 | False |
| dependencies | dependencies/obfuscated-structural-1 | dependencies/python-3.8/opt-2/pycdc | behavior_mismatch | False | 73.74 | 98.38 | 98.80 | False |
| dependencies | dependencies/obfuscated-structural-2 | dependencies/python-3.8/opt-2/pycdc | behavior_mismatch | False | 73.74 | 98.38 | 98.80 | False |
| dispatch | dispatch/obfuscated-light-0 | dispatch/python-3.12/opt-0/uncompyle6 | unsupported | False | -0.69 | 23.23 | 0.00 | False |
| dispatch | dispatch/obfuscated-light-1 | dispatch/python-3.12/opt-0/uncompyle6 | unsupported | False | -0.69 | 23.23 | 0.00 | False |
| dispatch | dispatch/obfuscated-light-2 | dispatch/python-3.12/opt-0/uncompyle6 | unsupported | False | -0.69 | 23.23 | 0.00 | False |
| dispatch | dispatch/obfuscated-structural-0 | dispatch/python-3.12/opt-0/uncompyle6 | unsupported | False | 11.17 | 31.67 | 0.46 | False |
| dispatch | dispatch/obfuscated-structural-1 | dispatch/python-3.12/opt-0/uncompyle6 | unsupported | False | 11.17 | 31.67 | 0.46 | False |
| dispatch | dispatch/obfuscated-structural-2 | dispatch/python-3.12/opt-0/uncompyle6 | unsupported | False | 11.17 | 31.67 | 0.46 | False |
| dispatch | dispatch/obfuscated-light-0 | dispatch/python-3.12/opt-0/pycdc | success | True | 100.00 | 100.00 | 100.00 | True |
| dispatch | dispatch/obfuscated-light-1 | dispatch/python-3.12/opt-0/pycdc | success | True | 100.00 | 100.00 | 100.00 | True |
| dispatch | dispatch/obfuscated-light-2 | dispatch/python-3.12/opt-0/pycdc | success | True | 100.00 | 100.00 | 100.00 | True |
| dispatch | dispatch/obfuscated-structural-0 | dispatch/python-3.12/opt-0/pycdc | success | True | 67.36 | 96.11 | 98.42 | False |
| dispatch | dispatch/obfuscated-structural-1 | dispatch/python-3.12/opt-0/pycdc | success | True | 67.36 | 96.11 | 98.42 | False |
| dispatch | dispatch/obfuscated-structural-2 | dispatch/python-3.12/opt-0/pycdc | success | True | 67.36 | 96.11 | 98.42 | False |
| dispatch | dispatch/obfuscated-light-0 | dispatch/python-3.12/opt-1/uncompyle6 | unsupported | False | -0.69 | 23.23 | 0.00 | False |
| dispatch | dispatch/obfuscated-light-1 | dispatch/python-3.12/opt-1/uncompyle6 | unsupported | False | -0.69 | 23.23 | 0.00 | False |
| dispatch | dispatch/obfuscated-light-2 | dispatch/python-3.12/opt-1/uncompyle6 | unsupported | False | -0.69 | 23.23 | 0.00 | False |
| dispatch | dispatch/obfuscated-structural-0 | dispatch/python-3.12/opt-1/uncompyle6 | unsupported | False | 11.17 | 31.67 | 0.46 | False |
| dispatch | dispatch/obfuscated-structural-1 | dispatch/python-3.12/opt-1/uncompyle6 | unsupported | False | 11.17 | 31.67 | 0.46 | False |
| dispatch | dispatch/obfuscated-structural-2 | dispatch/python-3.12/opt-1/uncompyle6 | unsupported | False | 11.17 | 31.67 | 0.46 | False |
| dispatch | dispatch/obfuscated-light-0 | dispatch/python-3.12/opt-1/pycdc | success | True | 100.00 | 100.00 | 100.00 | True |
| dispatch | dispatch/obfuscated-light-1 | dispatch/python-3.12/opt-1/pycdc | success | True | 100.00 | 100.00 | 100.00 | True |
| dispatch | dispatch/obfuscated-light-2 | dispatch/python-3.12/opt-1/pycdc | success | True | 100.00 | 100.00 | 100.00 | True |
| dispatch | dispatch/obfuscated-structural-0 | dispatch/python-3.12/opt-1/pycdc | success | True | 67.36 | 96.11 | 98.42 | False |
| dispatch | dispatch/obfuscated-structural-1 | dispatch/python-3.12/opt-1/pycdc | success | True | 67.36 | 96.11 | 98.42 | False |
| dispatch | dispatch/obfuscated-structural-2 | dispatch/python-3.12/opt-1/pycdc | success | True | 67.36 | 96.11 | 98.42 | False |
| dispatch | dispatch/obfuscated-light-0 | dispatch/python-3.12/opt-2/uncompyle6 | unsupported | False | -0.69 | 23.23 | 0.00 | False |
| dispatch | dispatch/obfuscated-light-1 | dispatch/python-3.12/opt-2/uncompyle6 | unsupported | False | -0.69 | 23.23 | 0.00 | False |
| dispatch | dispatch/obfuscated-light-2 | dispatch/python-3.12/opt-2/uncompyle6 | unsupported | False | -0.69 | 23.23 | 0.00 | False |
| dispatch | dispatch/obfuscated-structural-0 | dispatch/python-3.12/opt-2/uncompyle6 | unsupported | False | 11.17 | 31.67 | 0.46 | False |
| dispatch | dispatch/obfuscated-structural-1 | dispatch/python-3.12/opt-2/uncompyle6 | unsupported | False | 11.17 | 31.67 | 0.46 | False |
| dispatch | dispatch/obfuscated-structural-2 | dispatch/python-3.12/opt-2/uncompyle6 | unsupported | False | 11.17 | 31.67 | 0.46 | False |
| dispatch | dispatch/obfuscated-light-0 | dispatch/python-3.12/opt-2/pycdc | success | True | 100.00 | 100.00 | 100.00 | True |
| dispatch | dispatch/obfuscated-light-1 | dispatch/python-3.12/opt-2/pycdc | success | True | 100.00 | 100.00 | 100.00 | True |
| dispatch | dispatch/obfuscated-light-2 | dispatch/python-3.12/opt-2/pycdc | success | True | 100.00 | 100.00 | 100.00 | True |
| dispatch | dispatch/obfuscated-structural-0 | dispatch/python-3.12/opt-2/pycdc | success | True | 67.36 | 96.11 | 98.42 | False |
| dispatch | dispatch/obfuscated-structural-1 | dispatch/python-3.12/opt-2/pycdc | success | True | 67.36 | 96.11 | 98.42 | False |
| dispatch | dispatch/obfuscated-structural-2 | dispatch/python-3.12/opt-2/pycdc | success | True | 67.36 | 96.11 | 98.42 | False |
| dispatch | dispatch/obfuscated-light-0 | dispatch/python-3.14/opt-0/uncompyle6 | unsupported | False | -2.43 | 24.56 | 0.00 | False |
| dispatch | dispatch/obfuscated-light-1 | dispatch/python-3.14/opt-0/uncompyle6 | unsupported | False | -2.43 | 24.56 | 0.00 | False |
| dispatch | dispatch/obfuscated-light-2 | dispatch/python-3.14/opt-0/uncompyle6 | unsupported | False | -2.43 | 24.56 | 0.00 | False |
| dispatch | dispatch/obfuscated-structural-0 | dispatch/python-3.14/opt-0/uncompyle6 | unsupported | False | 10.15 | 33.15 | 0.46 | False |
| dispatch | dispatch/obfuscated-structural-1 | dispatch/python-3.14/opt-0/uncompyle6 | unsupported | False | 10.15 | 33.15 | 0.46 | False |
| dispatch | dispatch/obfuscated-structural-2 | dispatch/python-3.14/opt-0/uncompyle6 | unsupported | False | 10.15 | 33.15 | 0.46 | False |
| dispatch | dispatch/obfuscated-light-0 | dispatch/python-3.14/opt-0/pycdc | invalid_output | False | N/A | N/A | N/A | False |
| dispatch | dispatch/obfuscated-light-1 | dispatch/python-3.14/opt-0/pycdc | invalid_output | False | N/A | N/A | N/A | False |
| dispatch | dispatch/obfuscated-light-2 | dispatch/python-3.14/opt-0/pycdc | invalid_output | False | N/A | N/A | N/A | False |
| dispatch | dispatch/obfuscated-structural-0 | dispatch/python-3.14/opt-0/pycdc | invalid_output | False | N/A | N/A | N/A | False |
| dispatch | dispatch/obfuscated-structural-1 | dispatch/python-3.14/opt-0/pycdc | invalid_output | False | N/A | N/A | N/A | False |
| dispatch | dispatch/obfuscated-structural-2 | dispatch/python-3.14/opt-0/pycdc | invalid_output | False | N/A | N/A | N/A | False |
| dispatch | dispatch/obfuscated-light-0 | dispatch/python-3.14/opt-1/uncompyle6 | unsupported | False | -2.43 | 24.56 | 0.00 | False |
| dispatch | dispatch/obfuscated-light-1 | dispatch/python-3.14/opt-1/uncompyle6 | unsupported | False | -2.43 | 24.56 | 0.00 | False |
| dispatch | dispatch/obfuscated-light-2 | dispatch/python-3.14/opt-1/uncompyle6 | unsupported | False | -2.43 | 24.56 | 0.00 | False |
| dispatch | dispatch/obfuscated-structural-0 | dispatch/python-3.14/opt-1/uncompyle6 | unsupported | False | 10.15 | 33.15 | 0.46 | False |
| dispatch | dispatch/obfuscated-structural-1 | dispatch/python-3.14/opt-1/uncompyle6 | unsupported | False | 10.15 | 33.15 | 0.46 | False |
| dispatch | dispatch/obfuscated-structural-2 | dispatch/python-3.14/opt-1/uncompyle6 | unsupported | False | 10.15 | 33.15 | 0.46 | False |
| dispatch | dispatch/obfuscated-light-0 | dispatch/python-3.14/opt-1/pycdc | invalid_output | False | N/A | N/A | N/A | False |
| dispatch | dispatch/obfuscated-light-1 | dispatch/python-3.14/opt-1/pycdc | invalid_output | False | N/A | N/A | N/A | False |
| dispatch | dispatch/obfuscated-light-2 | dispatch/python-3.14/opt-1/pycdc | invalid_output | False | N/A | N/A | N/A | False |
| dispatch | dispatch/obfuscated-structural-0 | dispatch/python-3.14/opt-1/pycdc | invalid_output | False | N/A | N/A | N/A | False |
| dispatch | dispatch/obfuscated-structural-1 | dispatch/python-3.14/opt-1/pycdc | invalid_output | False | N/A | N/A | N/A | False |
| dispatch | dispatch/obfuscated-structural-2 | dispatch/python-3.14/opt-1/pycdc | invalid_output | False | N/A | N/A | N/A | False |
| dispatch | dispatch/obfuscated-light-0 | dispatch/python-3.14/opt-2/uncompyle6 | unsupported | False | -2.43 | 24.56 | 0.00 | False |
| dispatch | dispatch/obfuscated-light-1 | dispatch/python-3.14/opt-2/uncompyle6 | unsupported | False | -2.43 | 24.56 | 0.00 | False |
| dispatch | dispatch/obfuscated-light-2 | dispatch/python-3.14/opt-2/uncompyle6 | unsupported | False | -2.43 | 24.56 | 0.00 | False |
| dispatch | dispatch/obfuscated-structural-0 | dispatch/python-3.14/opt-2/uncompyle6 | unsupported | False | 10.15 | 33.15 | 0.46 | False |
| dispatch | dispatch/obfuscated-structural-1 | dispatch/python-3.14/opt-2/uncompyle6 | unsupported | False | 10.15 | 33.15 | 0.46 | False |
| dispatch | dispatch/obfuscated-structural-2 | dispatch/python-3.14/opt-2/uncompyle6 | unsupported | False | 10.15 | 33.15 | 0.46 | False |
| dispatch | dispatch/obfuscated-light-0 | dispatch/python-3.14/opt-2/pycdc | invalid_output | False | N/A | N/A | N/A | False |
| dispatch | dispatch/obfuscated-light-1 | dispatch/python-3.14/opt-2/pycdc | invalid_output | False | N/A | N/A | N/A | False |
| dispatch | dispatch/obfuscated-light-2 | dispatch/python-3.14/opt-2/pycdc | invalid_output | False | N/A | N/A | N/A | False |
| dispatch | dispatch/obfuscated-structural-0 | dispatch/python-3.14/opt-2/pycdc | invalid_output | False | N/A | N/A | N/A | False |
| dispatch | dispatch/obfuscated-structural-1 | dispatch/python-3.14/opt-2/pycdc | invalid_output | False | N/A | N/A | N/A | False |
| dispatch | dispatch/obfuscated-structural-2 | dispatch/python-3.14/opt-2/pycdc | invalid_output | False | N/A | N/A | N/A | False |
| dispatch | dispatch/obfuscated-light-0 | dispatch/python-3.4/opt-0/uncompyle6 | success | True | 100.00 | 100.00 | 100.00 | True |
| dispatch | dispatch/obfuscated-light-1 | dispatch/python-3.4/opt-0/uncompyle6 | success | True | 100.00 | 100.00 | 100.00 | True |
| dispatch | dispatch/obfuscated-light-2 | dispatch/python-3.4/opt-0/uncompyle6 | success | True | 100.00 | 100.00 | 100.00 | True |
| dispatch | dispatch/obfuscated-structural-0 | dispatch/python-3.4/opt-0/uncompyle6 | success | True | 67.36 | 96.11 | 98.42 | False |
| dispatch | dispatch/obfuscated-structural-1 | dispatch/python-3.4/opt-0/uncompyle6 | success | True | 67.36 | 96.11 | 98.42 | False |
| dispatch | dispatch/obfuscated-structural-2 | dispatch/python-3.4/opt-0/uncompyle6 | success | True | 67.36 | 96.11 | 98.42 | False |
| dispatch | dispatch/obfuscated-light-0 | dispatch/python-3.4/opt-0/pycdc | success | True | 100.00 | 100.00 | 100.00 | True |
| dispatch | dispatch/obfuscated-light-1 | dispatch/python-3.4/opt-0/pycdc | success | True | 100.00 | 100.00 | 100.00 | True |
| dispatch | dispatch/obfuscated-light-2 | dispatch/python-3.4/opt-0/pycdc | success | True | 100.00 | 100.00 | 100.00 | True |
| dispatch | dispatch/obfuscated-structural-0 | dispatch/python-3.4/opt-0/pycdc | success | True | 67.36 | 96.11 | 98.42 | False |
| dispatch | dispatch/obfuscated-structural-1 | dispatch/python-3.4/opt-0/pycdc | success | True | 67.36 | 96.11 | 98.42 | False |
| dispatch | dispatch/obfuscated-structural-2 | dispatch/python-3.4/opt-0/pycdc | success | True | 67.36 | 96.11 | 98.42 | False |
| dispatch | dispatch/obfuscated-light-0 | dispatch/python-3.4/opt-1/uncompyle6 | success | True | 100.00 | 100.00 | 100.00 | True |
| dispatch | dispatch/obfuscated-light-1 | dispatch/python-3.4/opt-1/uncompyle6 | success | True | 100.00 | 100.00 | 100.00 | True |
| dispatch | dispatch/obfuscated-light-2 | dispatch/python-3.4/opt-1/uncompyle6 | success | True | 100.00 | 100.00 | 100.00 | True |
| dispatch | dispatch/obfuscated-structural-0 | dispatch/python-3.4/opt-1/uncompyle6 | success | True | 67.36 | 96.11 | 98.42 | False |
| dispatch | dispatch/obfuscated-structural-1 | dispatch/python-3.4/opt-1/uncompyle6 | success | True | 67.36 | 96.11 | 98.42 | False |
| dispatch | dispatch/obfuscated-structural-2 | dispatch/python-3.4/opt-1/uncompyle6 | success | True | 67.36 | 96.11 | 98.42 | False |
| dispatch | dispatch/obfuscated-light-0 | dispatch/python-3.4/opt-1/pycdc | success | True | 100.00 | 100.00 | 100.00 | True |
| dispatch | dispatch/obfuscated-light-1 | dispatch/python-3.4/opt-1/pycdc | success | True | 100.00 | 100.00 | 100.00 | True |
| dispatch | dispatch/obfuscated-light-2 | dispatch/python-3.4/opt-1/pycdc | success | True | 100.00 | 100.00 | 100.00 | True |
| dispatch | dispatch/obfuscated-structural-0 | dispatch/python-3.4/opt-1/pycdc | success | True | 67.36 | 96.11 | 98.42 | False |
| dispatch | dispatch/obfuscated-structural-1 | dispatch/python-3.4/opt-1/pycdc | success | True | 67.36 | 96.11 | 98.42 | False |
| dispatch | dispatch/obfuscated-structural-2 | dispatch/python-3.4/opt-1/pycdc | success | True | 67.36 | 96.11 | 98.42 | False |
| dispatch | dispatch/obfuscated-light-0 | dispatch/python-3.4/opt-2/uncompyle6 | success | True | 100.00 | 100.00 | 100.00 | True |
| dispatch | dispatch/obfuscated-light-1 | dispatch/python-3.4/opt-2/uncompyle6 | success | True | 100.00 | 100.00 | 100.00 | True |
| dispatch | dispatch/obfuscated-light-2 | dispatch/python-3.4/opt-2/uncompyle6 | success | True | 100.00 | 100.00 | 100.00 | True |
| dispatch | dispatch/obfuscated-structural-0 | dispatch/python-3.4/opt-2/uncompyle6 | success | True | 67.36 | 96.11 | 98.42 | False |
| dispatch | dispatch/obfuscated-structural-1 | dispatch/python-3.4/opt-2/uncompyle6 | success | True | 67.36 | 96.11 | 98.42 | False |
| dispatch | dispatch/obfuscated-structural-2 | dispatch/python-3.4/opt-2/uncompyle6 | success | True | 67.36 | 96.11 | 98.42 | False |
| dispatch | dispatch/obfuscated-light-0 | dispatch/python-3.4/opt-2/pycdc | success | True | 100.00 | 100.00 | 100.00 | True |
| dispatch | dispatch/obfuscated-light-1 | dispatch/python-3.4/opt-2/pycdc | success | True | 100.00 | 100.00 | 100.00 | True |
| dispatch | dispatch/obfuscated-light-2 | dispatch/python-3.4/opt-2/pycdc | success | True | 100.00 | 100.00 | 100.00 | True |
| dispatch | dispatch/obfuscated-structural-0 | dispatch/python-3.4/opt-2/pycdc | success | True | 67.36 | 96.11 | 98.42 | False |
| dispatch | dispatch/obfuscated-structural-1 | dispatch/python-3.4/opt-2/pycdc | success | True | 67.36 | 96.11 | 98.42 | False |
| dispatch | dispatch/obfuscated-structural-2 | dispatch/python-3.4/opt-2/pycdc | success | True | 67.36 | 96.11 | 98.42 | False |
| dispatch | dispatch/obfuscated-light-0 | dispatch/python-3.8/opt-0/uncompyle6 | success | True | 99.79 | 99.98 | 100.00 | False |
| dispatch | dispatch/obfuscated-light-1 | dispatch/python-3.8/opt-0/uncompyle6 | success | True | 99.79 | 99.98 | 100.00 | False |
| dispatch | dispatch/obfuscated-light-2 | dispatch/python-3.8/opt-0/uncompyle6 | success | True | 99.79 | 99.98 | 100.00 | False |
| dispatch | dispatch/obfuscated-structural-0 | dispatch/python-3.8/opt-0/uncompyle6 | success | True | 68.12 | 96.18 | 98.40 | False |
| dispatch | dispatch/obfuscated-structural-1 | dispatch/python-3.8/opt-0/uncompyle6 | success | True | 68.12 | 96.18 | 98.40 | False |
| dispatch | dispatch/obfuscated-structural-2 | dispatch/python-3.8/opt-0/uncompyle6 | success | True | 68.12 | 96.18 | 98.40 | False |
| dispatch | dispatch/obfuscated-light-0 | dispatch/python-3.8/opt-0/pycdc | success | True | 100.00 | 100.00 | 100.00 | True |
| dispatch | dispatch/obfuscated-light-1 | dispatch/python-3.8/opt-0/pycdc | success | True | 100.00 | 100.00 | 100.00 | True |
| dispatch | dispatch/obfuscated-light-2 | dispatch/python-3.8/opt-0/pycdc | success | True | 100.00 | 100.00 | 100.00 | True |
| dispatch | dispatch/obfuscated-structural-0 | dispatch/python-3.8/opt-0/pycdc | success | True | 67.36 | 96.11 | 98.42 | False |
| dispatch | dispatch/obfuscated-structural-1 | dispatch/python-3.8/opt-0/pycdc | success | True | 67.36 | 96.11 | 98.42 | False |
| dispatch | dispatch/obfuscated-structural-2 | dispatch/python-3.8/opt-0/pycdc | success | True | 67.36 | 96.11 | 98.42 | False |
| dispatch | dispatch/obfuscated-light-0 | dispatch/python-3.8/opt-1/uncompyle6 | success | True | 99.79 | 99.98 | 100.00 | False |
| dispatch | dispatch/obfuscated-light-1 | dispatch/python-3.8/opt-1/uncompyle6 | success | True | 99.79 | 99.98 | 100.00 | False |
| dispatch | dispatch/obfuscated-light-2 | dispatch/python-3.8/opt-1/uncompyle6 | success | True | 99.79 | 99.98 | 100.00 | False |
| dispatch | dispatch/obfuscated-structural-0 | dispatch/python-3.8/opt-1/uncompyle6 | success | True | 68.12 | 96.18 | 98.40 | False |
| dispatch | dispatch/obfuscated-structural-1 | dispatch/python-3.8/opt-1/uncompyle6 | success | True | 68.12 | 96.18 | 98.40 | False |
| dispatch | dispatch/obfuscated-structural-2 | dispatch/python-3.8/opt-1/uncompyle6 | success | True | 68.12 | 96.18 | 98.40 | False |
| dispatch | dispatch/obfuscated-light-0 | dispatch/python-3.8/opt-1/pycdc | success | True | 100.00 | 100.00 | 100.00 | True |
| dispatch | dispatch/obfuscated-light-1 | dispatch/python-3.8/opt-1/pycdc | success | True | 100.00 | 100.00 | 100.00 | True |
| dispatch | dispatch/obfuscated-light-2 | dispatch/python-3.8/opt-1/pycdc | success | True | 100.00 | 100.00 | 100.00 | True |
| dispatch | dispatch/obfuscated-structural-0 | dispatch/python-3.8/opt-1/pycdc | success | True | 67.36 | 96.11 | 98.42 | False |
| dispatch | dispatch/obfuscated-structural-1 | dispatch/python-3.8/opt-1/pycdc | success | True | 67.36 | 96.11 | 98.42 | False |
| dispatch | dispatch/obfuscated-structural-2 | dispatch/python-3.8/opt-1/pycdc | success | True | 67.36 | 96.11 | 98.42 | False |
| dispatch | dispatch/obfuscated-light-0 | dispatch/python-3.8/opt-2/uncompyle6 | success | True | 99.79 | 99.98 | 100.00 | False |
| dispatch | dispatch/obfuscated-light-1 | dispatch/python-3.8/opt-2/uncompyle6 | success | True | 99.79 | 99.98 | 100.00 | False |
| dispatch | dispatch/obfuscated-light-2 | dispatch/python-3.8/opt-2/uncompyle6 | success | True | 99.79 | 99.98 | 100.00 | False |
| dispatch | dispatch/obfuscated-structural-0 | dispatch/python-3.8/opt-2/uncompyle6 | success | True | 68.12 | 96.18 | 98.40 | False |
| dispatch | dispatch/obfuscated-structural-1 | dispatch/python-3.8/opt-2/uncompyle6 | success | True | 68.12 | 96.18 | 98.40 | False |
| dispatch | dispatch/obfuscated-structural-2 | dispatch/python-3.8/opt-2/uncompyle6 | success | True | 68.12 | 96.18 | 98.40 | False |
| dispatch | dispatch/obfuscated-light-0 | dispatch/python-3.8/opt-2/pycdc | success | True | 100.00 | 100.00 | 100.00 | True |
| dispatch | dispatch/obfuscated-light-1 | dispatch/python-3.8/opt-2/pycdc | success | True | 100.00 | 100.00 | 100.00 | True |
| dispatch | dispatch/obfuscated-light-2 | dispatch/python-3.8/opt-2/pycdc | success | True | 100.00 | 100.00 | 100.00 | True |
| dispatch | dispatch/obfuscated-structural-0 | dispatch/python-3.8/opt-2/pycdc | success | True | 67.36 | 96.11 | 98.42 | False |
| dispatch | dispatch/obfuscated-structural-1 | dispatch/python-3.8/opt-2/pycdc | success | True | 67.36 | 96.11 | 98.42 | False |
| dispatch | dispatch/obfuscated-structural-2 | dispatch/python-3.8/opt-2/pycdc | success | True | 67.36 | 96.11 | 98.42 | False |
| events | events/obfuscated-light-0 | events/python-3.12/opt-0/uncompyle6 | unsupported | False | 28.01 | 34.55 | 0.00 | False |
| events | events/obfuscated-light-1 | events/python-3.12/opt-0/uncompyle6 | unsupported | False | 28.01 | 34.55 | 0.00 | False |
| events | events/obfuscated-light-2 | events/python-3.12/opt-0/uncompyle6 | unsupported | False | 28.01 | 34.55 | 0.00 | False |
| events | events/obfuscated-structural-0 | events/python-3.12/opt-0/uncompyle6 | unsupported | False | 22.22 | 34.32 | 0.29 | False |
| events | events/obfuscated-structural-1 | events/python-3.12/opt-0/uncompyle6 | unsupported | False | 22.22 | 34.32 | 0.29 | False |
| events | events/obfuscated-structural-2 | events/python-3.12/opt-0/uncompyle6 | unsupported | False | 22.22 | 34.32 | 0.29 | False |
| events | events/obfuscated-light-0 | events/python-3.12/opt-0/pycdc | unsupported | False | 9.08 | 86.77 | 90.38 | False |
| events | events/obfuscated-light-1 | events/python-3.12/opt-0/pycdc | unsupported | False | 9.08 | 86.77 | 90.38 | False |
| events | events/obfuscated-light-2 | events/python-3.12/opt-0/pycdc | unsupported | False | 9.08 | 86.77 | 90.38 | False |
| events | events/obfuscated-structural-0 | events/python-3.12/opt-0/pycdc | unsupported | False | 29.55 | 90.60 | 91.16 | False |
| events | events/obfuscated-structural-1 | events/python-3.12/opt-0/pycdc | unsupported | False | 29.55 | 90.60 | 91.16 | False |
| events | events/obfuscated-structural-2 | events/python-3.12/opt-0/pycdc | unsupported | False | 29.55 | 90.60 | 91.16 | False |
| events | events/obfuscated-light-0 | events/python-3.12/opt-1/uncompyle6 | unsupported | False | 28.01 | 34.55 | 0.00 | False |
| events | events/obfuscated-light-1 | events/python-3.12/opt-1/uncompyle6 | unsupported | False | 28.01 | 34.55 | 0.00 | False |
| events | events/obfuscated-light-2 | events/python-3.12/opt-1/uncompyle6 | unsupported | False | 28.01 | 34.55 | 0.00 | False |
| events | events/obfuscated-structural-0 | events/python-3.12/opt-1/uncompyle6 | unsupported | False | 22.22 | 34.32 | 0.29 | False |
| events | events/obfuscated-structural-1 | events/python-3.12/opt-1/uncompyle6 | unsupported | False | 22.22 | 34.32 | 0.29 | False |
| events | events/obfuscated-structural-2 | events/python-3.12/opt-1/uncompyle6 | unsupported | False | 22.22 | 34.32 | 0.29 | False |
| events | events/obfuscated-light-0 | events/python-3.12/opt-1/pycdc | unsupported | False | 9.08 | 86.77 | 90.38 | False |
| events | events/obfuscated-light-1 | events/python-3.12/opt-1/pycdc | unsupported | False | 9.08 | 86.77 | 90.38 | False |
| events | events/obfuscated-light-2 | events/python-3.12/opt-1/pycdc | unsupported | False | 9.08 | 86.77 | 90.38 | False |
| events | events/obfuscated-structural-0 | events/python-3.12/opt-1/pycdc | unsupported | False | 29.55 | 90.60 | 91.16 | False |
| events | events/obfuscated-structural-1 | events/python-3.12/opt-1/pycdc | unsupported | False | 29.55 | 90.60 | 91.16 | False |
| events | events/obfuscated-structural-2 | events/python-3.12/opt-1/pycdc | unsupported | False | 29.55 | 90.60 | 91.16 | False |
| events | events/obfuscated-light-0 | events/python-3.12/opt-2/uncompyle6 | unsupported | False | 28.01 | 34.55 | 0.00 | False |
| events | events/obfuscated-light-1 | events/python-3.12/opt-2/uncompyle6 | unsupported | False | 28.01 | 34.55 | 0.00 | False |
| events | events/obfuscated-light-2 | events/python-3.12/opt-2/uncompyle6 | unsupported | False | 28.01 | 34.55 | 0.00 | False |
| events | events/obfuscated-structural-0 | events/python-3.12/opt-2/uncompyle6 | unsupported | False | 22.22 | 34.32 | 0.29 | False |
| events | events/obfuscated-structural-1 | events/python-3.12/opt-2/uncompyle6 | unsupported | False | 22.22 | 34.32 | 0.29 | False |
| events | events/obfuscated-structural-2 | events/python-3.12/opt-2/uncompyle6 | unsupported | False | 22.22 | 34.32 | 0.29 | False |
| events | events/obfuscated-light-0 | events/python-3.12/opt-2/pycdc | unsupported | False | 9.08 | 86.77 | 90.38 | False |
| events | events/obfuscated-light-1 | events/python-3.12/opt-2/pycdc | unsupported | False | 9.08 | 86.77 | 90.38 | False |
| events | events/obfuscated-light-2 | events/python-3.12/opt-2/pycdc | unsupported | False | 9.08 | 86.77 | 90.38 | False |
| events | events/obfuscated-structural-0 | events/python-3.12/opt-2/pycdc | unsupported | False | 29.55 | 90.60 | 91.16 | False |
| events | events/obfuscated-structural-1 | events/python-3.12/opt-2/pycdc | unsupported | False | 29.55 | 90.60 | 91.16 | False |
| events | events/obfuscated-structural-2 | events/python-3.12/opt-2/pycdc | unsupported | False | 29.55 | 90.60 | 91.16 | False |
| events | events/obfuscated-light-0 | events/python-3.14/opt-0/uncompyle6 | unsupported | False | 27.24 | 36.03 | 0.00 | False |
| events | events/obfuscated-light-1 | events/python-3.14/opt-0/uncompyle6 | unsupported | False | 27.24 | 36.03 | 0.00 | False |
| events | events/obfuscated-light-2 | events/python-3.14/opt-0/uncompyle6 | unsupported | False | 27.24 | 36.03 | 0.00 | False |
| events | events/obfuscated-structural-0 | events/python-3.14/opt-0/uncompyle6 | unsupported | False | 21.13 | 35.49 | 0.29 | False |
| events | events/obfuscated-structural-1 | events/python-3.14/opt-0/uncompyle6 | unsupported | False | 21.13 | 35.49 | 0.29 | False |
| events | events/obfuscated-structural-2 | events/python-3.14/opt-0/uncompyle6 | unsupported | False | 21.13 | 35.49 | 0.29 | False |
| events | events/obfuscated-light-0 | events/python-3.14/opt-0/pycdc | invalid_output | False | N/A | N/A | N/A | False |
| events | events/obfuscated-light-1 | events/python-3.14/opt-0/pycdc | invalid_output | False | N/A | N/A | N/A | False |
| events | events/obfuscated-light-2 | events/python-3.14/opt-0/pycdc | invalid_output | False | N/A | N/A | N/A | False |
| events | events/obfuscated-structural-0 | events/python-3.14/opt-0/pycdc | invalid_output | False | N/A | N/A | N/A | False |
| events | events/obfuscated-structural-1 | events/python-3.14/opt-0/pycdc | invalid_output | False | N/A | N/A | N/A | False |
| events | events/obfuscated-structural-2 | events/python-3.14/opt-0/pycdc | invalid_output | False | N/A | N/A | N/A | False |
| events | events/obfuscated-light-0 | events/python-3.14/opt-1/uncompyle6 | unsupported | False | 27.24 | 36.03 | 0.00 | False |
| events | events/obfuscated-light-1 | events/python-3.14/opt-1/uncompyle6 | unsupported | False | 27.24 | 36.03 | 0.00 | False |
| events | events/obfuscated-light-2 | events/python-3.14/opt-1/uncompyle6 | unsupported | False | 27.24 | 36.03 | 0.00 | False |
| events | events/obfuscated-structural-0 | events/python-3.14/opt-1/uncompyle6 | unsupported | False | 21.13 | 35.49 | 0.29 | False |
| events | events/obfuscated-structural-1 | events/python-3.14/opt-1/uncompyle6 | unsupported | False | 21.13 | 35.49 | 0.29 | False |
| events | events/obfuscated-structural-2 | events/python-3.14/opt-1/uncompyle6 | unsupported | False | 21.13 | 35.49 | 0.29 | False |
| events | events/obfuscated-light-0 | events/python-3.14/opt-1/pycdc | invalid_output | False | N/A | N/A | N/A | False |
| events | events/obfuscated-light-1 | events/python-3.14/opt-1/pycdc | invalid_output | False | N/A | N/A | N/A | False |
| events | events/obfuscated-light-2 | events/python-3.14/opt-1/pycdc | invalid_output | False | N/A | N/A | N/A | False |
| events | events/obfuscated-structural-0 | events/python-3.14/opt-1/pycdc | invalid_output | False | N/A | N/A | N/A | False |
| events | events/obfuscated-structural-1 | events/python-3.14/opt-1/pycdc | invalid_output | False | N/A | N/A | N/A | False |
| events | events/obfuscated-structural-2 | events/python-3.14/opt-1/pycdc | invalid_output | False | N/A | N/A | N/A | False |
| events | events/obfuscated-light-0 | events/python-3.14/opt-2/uncompyle6 | unsupported | False | 27.24 | 36.03 | 0.00 | False |
| events | events/obfuscated-light-1 | events/python-3.14/opt-2/uncompyle6 | unsupported | False | 27.24 | 36.03 | 0.00 | False |
| events | events/obfuscated-light-2 | events/python-3.14/opt-2/uncompyle6 | unsupported | False | 27.24 | 36.03 | 0.00 | False |
| events | events/obfuscated-structural-0 | events/python-3.14/opt-2/uncompyle6 | unsupported | False | 21.13 | 35.49 | 0.29 | False |
| events | events/obfuscated-structural-1 | events/python-3.14/opt-2/uncompyle6 | unsupported | False | 21.13 | 35.49 | 0.29 | False |
| events | events/obfuscated-structural-2 | events/python-3.14/opt-2/uncompyle6 | unsupported | False | 21.13 | 35.49 | 0.29 | False |
| events | events/obfuscated-light-0 | events/python-3.14/opt-2/pycdc | invalid_output | False | N/A | N/A | N/A | False |
| events | events/obfuscated-light-1 | events/python-3.14/opt-2/pycdc | invalid_output | False | N/A | N/A | N/A | False |
| events | events/obfuscated-light-2 | events/python-3.14/opt-2/pycdc | invalid_output | False | N/A | N/A | N/A | False |
| events | events/obfuscated-structural-0 | events/python-3.14/opt-2/pycdc | invalid_output | False | N/A | N/A | N/A | False |
| events | events/obfuscated-structural-1 | events/python-3.14/opt-2/pycdc | invalid_output | False | N/A | N/A | N/A | False |
| events | events/obfuscated-structural-2 | events/python-3.14/opt-2/pycdc | invalid_output | False | N/A | N/A | N/A | False |
| events | events/obfuscated-light-0 | events/python-3.4/opt-0/uncompyle6 | success | True | 100.00 | 100.00 | 100.00 | True |
| events | events/obfuscated-light-1 | events/python-3.4/opt-0/uncompyle6 | success | True | 100.00 | 100.00 | 100.00 | True |
| events | events/obfuscated-light-2 | events/python-3.4/opt-0/uncompyle6 | success | True | 100.00 | 100.00 | 100.00 | True |
| events | events/obfuscated-structural-0 | events/python-3.4/opt-0/uncompyle6 | success | True | 87.15 | 98.29 | 98.78 | False |
| events | events/obfuscated-structural-1 | events/python-3.4/opt-0/uncompyle6 | success | True | 87.15 | 98.29 | 98.78 | False |
| events | events/obfuscated-structural-2 | events/python-3.4/opt-0/uncompyle6 | success | True | 87.15 | 98.29 | 98.78 | False |
| events | events/obfuscated-light-0 | events/python-3.4/opt-0/pycdc | invalid_output | False | 27.25 | 40.64 | 0.00 | False |
| events | events/obfuscated-light-1 | events/python-3.4/opt-0/pycdc | invalid_output | False | 27.25 | 40.64 | 0.00 | False |
| events | events/obfuscated-light-2 | events/python-3.4/opt-0/pycdc | invalid_output | False | 27.25 | 40.64 | 0.00 | False |
| events | events/obfuscated-structural-0 | events/python-3.4/opt-0/pycdc | invalid_output | False | 20.14 | 38.84 | 0.29 | False |
| events | events/obfuscated-structural-1 | events/python-3.4/opt-0/pycdc | invalid_output | False | 20.14 | 38.84 | 0.29 | False |
| events | events/obfuscated-structural-2 | events/python-3.4/opt-0/pycdc | invalid_output | False | 20.14 | 38.84 | 0.29 | False |
| events | events/obfuscated-light-0 | events/python-3.4/opt-1/uncompyle6 | success | True | 100.00 | 100.00 | 100.00 | True |
| events | events/obfuscated-light-1 | events/python-3.4/opt-1/uncompyle6 | success | True | 100.00 | 100.00 | 100.00 | True |
| events | events/obfuscated-light-2 | events/python-3.4/opt-1/uncompyle6 | success | True | 100.00 | 100.00 | 100.00 | True |
| events | events/obfuscated-structural-0 | events/python-3.4/opt-1/uncompyle6 | success | True | 87.15 | 98.29 | 98.78 | False |
| events | events/obfuscated-structural-1 | events/python-3.4/opt-1/uncompyle6 | success | True | 87.15 | 98.29 | 98.78 | False |
| events | events/obfuscated-structural-2 | events/python-3.4/opt-1/uncompyle6 | success | True | 87.15 | 98.29 | 98.78 | False |
| events | events/obfuscated-light-0 | events/python-3.4/opt-1/pycdc | invalid_output | False | 27.25 | 40.64 | 0.00 | False |
| events | events/obfuscated-light-1 | events/python-3.4/opt-1/pycdc | invalid_output | False | 27.25 | 40.64 | 0.00 | False |
| events | events/obfuscated-light-2 | events/python-3.4/opt-1/pycdc | invalid_output | False | 27.25 | 40.64 | 0.00 | False |
| events | events/obfuscated-structural-0 | events/python-3.4/opt-1/pycdc | invalid_output | False | 20.14 | 38.84 | 0.29 | False |
| events | events/obfuscated-structural-1 | events/python-3.4/opt-1/pycdc | invalid_output | False | 20.14 | 38.84 | 0.29 | False |
| events | events/obfuscated-structural-2 | events/python-3.4/opt-1/pycdc | invalid_output | False | 20.14 | 38.84 | 0.29 | False |
| events | events/obfuscated-light-0 | events/python-3.4/opt-2/uncompyle6 | success | True | 100.00 | 100.00 | 100.00 | True |
| events | events/obfuscated-light-1 | events/python-3.4/opt-2/uncompyle6 | success | True | 100.00 | 100.00 | 100.00 | True |
| events | events/obfuscated-light-2 | events/python-3.4/opt-2/uncompyle6 | success | True | 100.00 | 100.00 | 100.00 | True |
| events | events/obfuscated-structural-0 | events/python-3.4/opt-2/uncompyle6 | success | True | 87.15 | 98.29 | 98.78 | False |
| events | events/obfuscated-structural-1 | events/python-3.4/opt-2/uncompyle6 | success | True | 87.15 | 98.29 | 98.78 | False |
| events | events/obfuscated-structural-2 | events/python-3.4/opt-2/uncompyle6 | success | True | 87.15 | 98.29 | 98.78 | False |
| events | events/obfuscated-light-0 | events/python-3.4/opt-2/pycdc | invalid_output | False | 27.25 | 40.64 | 0.00 | False |
| events | events/obfuscated-light-1 | events/python-3.4/opt-2/pycdc | invalid_output | False | 27.25 | 40.64 | 0.00 | False |
| events | events/obfuscated-light-2 | events/python-3.4/opt-2/pycdc | invalid_output | False | 27.25 | 40.64 | 0.00 | False |
| events | events/obfuscated-structural-0 | events/python-3.4/opt-2/pycdc | invalid_output | False | 20.14 | 38.84 | 0.29 | False |
| events | events/obfuscated-structural-1 | events/python-3.4/opt-2/pycdc | invalid_output | False | 20.14 | 38.84 | 0.29 | False |
| events | events/obfuscated-structural-2 | events/python-3.4/opt-2/pycdc | invalid_output | False | 20.14 | 38.84 | 0.29 | False |
| events | events/obfuscated-light-0 | events/python-3.8/opt-0/uncompyle6 | invalid_output | False | 26.97 | 41.42 | 0.00 | False |
| events | events/obfuscated-light-1 | events/python-3.8/opt-0/uncompyle6 | invalid_output | False | 26.97 | 41.42 | 0.00 | False |
| events | events/obfuscated-light-2 | events/python-3.8/opt-0/uncompyle6 | invalid_output | False | 26.97 | 41.42 | 0.00 | False |
| events | events/obfuscated-structural-0 | events/python-3.8/opt-0/uncompyle6 | invalid_output | False | 19.67 | 39.47 | 0.29 | False |
| events | events/obfuscated-structural-1 | events/python-3.8/opt-0/uncompyle6 | invalid_output | False | 19.67 | 39.47 | 0.29 | False |
| events | events/obfuscated-structural-2 | events/python-3.8/opt-0/uncompyle6 | invalid_output | False | 19.67 | 39.47 | 0.29 | False |
| events | events/obfuscated-light-0 | events/python-3.8/opt-0/pycdc | invalid_output | False | 27.76 | 39.34 | 0.00 | False |
| events | events/obfuscated-light-1 | events/python-3.8/opt-0/pycdc | invalid_output | False | 27.76 | 39.34 | 0.00 | False |
| events | events/obfuscated-light-2 | events/python-3.8/opt-0/pycdc | invalid_output | False | 27.76 | 39.34 | 0.00 | False |
| events | events/obfuscated-structural-0 | events/python-3.8/opt-0/pycdc | invalid_output | False | 20.87 | 37.83 | 0.29 | False |
| events | events/obfuscated-structural-1 | events/python-3.8/opt-0/pycdc | invalid_output | False | 20.87 | 37.83 | 0.29 | False |
| events | events/obfuscated-structural-2 | events/python-3.8/opt-0/pycdc | invalid_output | False | 20.87 | 37.83 | 0.29 | False |
| events | events/obfuscated-light-0 | events/python-3.8/opt-1/uncompyle6 | invalid_output | False | 26.97 | 41.42 | 0.00 | False |
| events | events/obfuscated-light-1 | events/python-3.8/opt-1/uncompyle6 | invalid_output | False | 26.97 | 41.42 | 0.00 | False |
| events | events/obfuscated-light-2 | events/python-3.8/opt-1/uncompyle6 | invalid_output | False | 26.97 | 41.42 | 0.00 | False |
| events | events/obfuscated-structural-0 | events/python-3.8/opt-1/uncompyle6 | invalid_output | False | 19.67 | 39.47 | 0.29 | False |
| events | events/obfuscated-structural-1 | events/python-3.8/opt-1/uncompyle6 | invalid_output | False | 19.67 | 39.47 | 0.29 | False |
| events | events/obfuscated-structural-2 | events/python-3.8/opt-1/uncompyle6 | invalid_output | False | 19.67 | 39.47 | 0.29 | False |
| events | events/obfuscated-light-0 | events/python-3.8/opt-1/pycdc | invalid_output | False | 27.76 | 39.34 | 0.00 | False |
| events | events/obfuscated-light-1 | events/python-3.8/opt-1/pycdc | invalid_output | False | 27.76 | 39.34 | 0.00 | False |
| events | events/obfuscated-light-2 | events/python-3.8/opt-1/pycdc | invalid_output | False | 27.76 | 39.34 | 0.00 | False |
| events | events/obfuscated-structural-0 | events/python-3.8/opt-1/pycdc | invalid_output | False | 20.87 | 37.83 | 0.29 | False |
| events | events/obfuscated-structural-1 | events/python-3.8/opt-1/pycdc | invalid_output | False | 20.87 | 37.83 | 0.29 | False |
| events | events/obfuscated-structural-2 | events/python-3.8/opt-1/pycdc | invalid_output | False | 20.87 | 37.83 | 0.29 | False |
| events | events/obfuscated-light-0 | events/python-3.8/opt-2/uncompyle6 | invalid_output | False | 26.97 | 41.42 | 0.00 | False |
| events | events/obfuscated-light-1 | events/python-3.8/opt-2/uncompyle6 | invalid_output | False | 26.97 | 41.42 | 0.00 | False |
| events | events/obfuscated-light-2 | events/python-3.8/opt-2/uncompyle6 | invalid_output | False | 26.97 | 41.42 | 0.00 | False |
| events | events/obfuscated-structural-0 | events/python-3.8/opt-2/uncompyle6 | invalid_output | False | 19.67 | 39.47 | 0.29 | False |
| events | events/obfuscated-structural-1 | events/python-3.8/opt-2/uncompyle6 | invalid_output | False | 19.67 | 39.47 | 0.29 | False |
| events | events/obfuscated-structural-2 | events/python-3.8/opt-2/uncompyle6 | invalid_output | False | 19.67 | 39.47 | 0.29 | False |
| events | events/obfuscated-light-0 | events/python-3.8/opt-2/pycdc | invalid_output | False | 27.76 | 39.34 | 0.00 | False |
| events | events/obfuscated-light-1 | events/python-3.8/opt-2/pycdc | invalid_output | False | 27.76 | 39.34 | 0.00 | False |
| events | events/obfuscated-light-2 | events/python-3.8/opt-2/pycdc | invalid_output | False | 27.76 | 39.34 | 0.00 | False |
| events | events/obfuscated-structural-0 | events/python-3.8/opt-2/pycdc | invalid_output | False | 20.87 | 37.83 | 0.29 | False |
| events | events/obfuscated-structural-1 | events/python-3.8/opt-2/pycdc | invalid_output | False | 20.87 | 37.83 | 0.29 | False |
| events | events/obfuscated-structural-2 | events/python-3.8/opt-2/pycdc | invalid_output | False | 20.87 | 37.83 | 0.29 | False |
| inventory | inventory/obfuscated-light-0 | inventory/python-3.12/opt-0/uncompyle6 | unsupported | False | 15.01 | 29.22 | 0.21 | False |
| inventory | inventory/obfuscated-light-1 | inventory/python-3.12/opt-0/uncompyle6 | unsupported | False | 15.01 | 29.22 | 0.21 | False |
| inventory | inventory/obfuscated-light-2 | inventory/python-3.12/opt-0/uncompyle6 | unsupported | False | 15.01 | 29.22 | 0.21 | False |
| inventory | inventory/obfuscated-structural-0 | inventory/python-3.12/opt-0/uncompyle6 | unsupported | False | 28.53 | 32.79 | 0.44 | False |
| inventory | inventory/obfuscated-structural-1 | inventory/python-3.12/opt-0/uncompyle6 | unsupported | False | 28.53 | 32.79 | 0.44 | False |
| inventory | inventory/obfuscated-structural-2 | inventory/python-3.12/opt-0/uncompyle6 | unsupported | False | 28.53 | 32.79 | 0.44 | False |
| inventory | inventory/obfuscated-light-0 | inventory/python-3.12/opt-0/pycdc | partial | False | 93.70 | 99.14 | 99.35 | False |
| inventory | inventory/obfuscated-light-1 | inventory/python-3.12/opt-0/pycdc | partial | False | 93.70 | 99.14 | 99.35 | False |
| inventory | inventory/obfuscated-light-2 | inventory/python-3.12/opt-0/pycdc | partial | False | 93.70 | 99.14 | 99.35 | False |
| inventory | inventory/obfuscated-structural-0 | inventory/python-3.12/opt-0/pycdc | partial | False | 77.36 | 98.43 | 98.40 | False |
| inventory | inventory/obfuscated-structural-1 | inventory/python-3.12/opt-0/pycdc | partial | False | 77.36 | 98.43 | 98.40 | False |
| inventory | inventory/obfuscated-structural-2 | inventory/python-3.12/opt-0/pycdc | partial | False | 77.36 | 98.43 | 98.40 | False |
| inventory | inventory/obfuscated-light-0 | inventory/python-3.12/opt-1/uncompyle6 | unsupported | False | 15.01 | 29.22 | 0.21 | False |
| inventory | inventory/obfuscated-light-1 | inventory/python-3.12/opt-1/uncompyle6 | unsupported | False | 15.01 | 29.22 | 0.21 | False |
| inventory | inventory/obfuscated-light-2 | inventory/python-3.12/opt-1/uncompyle6 | unsupported | False | 15.01 | 29.22 | 0.21 | False |
| inventory | inventory/obfuscated-structural-0 | inventory/python-3.12/opt-1/uncompyle6 | unsupported | False | 28.53 | 32.79 | 0.44 | False |
| inventory | inventory/obfuscated-structural-1 | inventory/python-3.12/opt-1/uncompyle6 | unsupported | False | 28.53 | 32.79 | 0.44 | False |
| inventory | inventory/obfuscated-structural-2 | inventory/python-3.12/opt-1/uncompyle6 | unsupported | False | 28.53 | 32.79 | 0.44 | False |
| inventory | inventory/obfuscated-light-0 | inventory/python-3.12/opt-1/pycdc | partial | False | 93.70 | 99.14 | 99.35 | False |
| inventory | inventory/obfuscated-light-1 | inventory/python-3.12/opt-1/pycdc | partial | False | 93.70 | 99.14 | 99.35 | False |
| inventory | inventory/obfuscated-light-2 | inventory/python-3.12/opt-1/pycdc | partial | False | 93.70 | 99.14 | 99.35 | False |
| inventory | inventory/obfuscated-structural-0 | inventory/python-3.12/opt-1/pycdc | partial | False | 77.36 | 98.43 | 98.40 | False |
| inventory | inventory/obfuscated-structural-1 | inventory/python-3.12/opt-1/pycdc | partial | False | 77.36 | 98.43 | 98.40 | False |
| inventory | inventory/obfuscated-structural-2 | inventory/python-3.12/opt-1/pycdc | partial | False | 77.36 | 98.43 | 98.40 | False |
| inventory | inventory/obfuscated-light-0 | inventory/python-3.12/opt-2/uncompyle6 | unsupported | False | 15.01 | 29.22 | 0.21 | False |
| inventory | inventory/obfuscated-light-1 | inventory/python-3.12/opt-2/uncompyle6 | unsupported | False | 15.01 | 29.22 | 0.21 | False |
| inventory | inventory/obfuscated-light-2 | inventory/python-3.12/opt-2/uncompyle6 | unsupported | False | 15.01 | 29.22 | 0.21 | False |
| inventory | inventory/obfuscated-structural-0 | inventory/python-3.12/opt-2/uncompyle6 | unsupported | False | 28.53 | 32.79 | 0.44 | False |
| inventory | inventory/obfuscated-structural-1 | inventory/python-3.12/opt-2/uncompyle6 | unsupported | False | 28.53 | 32.79 | 0.44 | False |
| inventory | inventory/obfuscated-structural-2 | inventory/python-3.12/opt-2/uncompyle6 | unsupported | False | 28.53 | 32.79 | 0.44 | False |
| inventory | inventory/obfuscated-light-0 | inventory/python-3.12/opt-2/pycdc | partial | False | 93.70 | 99.14 | 99.35 | False |
| inventory | inventory/obfuscated-light-1 | inventory/python-3.12/opt-2/pycdc | partial | False | 93.70 | 99.14 | 99.35 | False |
| inventory | inventory/obfuscated-light-2 | inventory/python-3.12/opt-2/pycdc | partial | False | 93.70 | 99.14 | 99.35 | False |
| inventory | inventory/obfuscated-structural-0 | inventory/python-3.12/opt-2/pycdc | partial | False | 77.36 | 98.43 | 98.40 | False |
| inventory | inventory/obfuscated-structural-1 | inventory/python-3.12/opt-2/pycdc | partial | False | 77.36 | 98.43 | 98.40 | False |
| inventory | inventory/obfuscated-structural-2 | inventory/python-3.12/opt-2/pycdc | partial | False | 77.36 | 98.43 | 98.40 | False |
| inventory | inventory/obfuscated-light-0 | inventory/python-3.14/opt-0/uncompyle6 | unsupported | False | 15.35 | 30.72 | 0.22 | False |
| inventory | inventory/obfuscated-light-1 | inventory/python-3.14/opt-0/uncompyle6 | unsupported | False | 15.35 | 30.72 | 0.22 | False |
| inventory | inventory/obfuscated-light-2 | inventory/python-3.14/opt-0/uncompyle6 | unsupported | False | 15.35 | 30.72 | 0.22 | False |
| inventory | inventory/obfuscated-structural-0 | inventory/python-3.14/opt-0/uncompyle6 | unsupported | False | 28.26 | 34.40 | 0.44 | False |
| inventory | inventory/obfuscated-structural-1 | inventory/python-3.14/opt-0/uncompyle6 | unsupported | False | 28.26 | 34.40 | 0.44 | False |
| inventory | inventory/obfuscated-structural-2 | inventory/python-3.14/opt-0/uncompyle6 | unsupported | False | 28.26 | 34.40 | 0.44 | False |
| inventory | inventory/obfuscated-light-0 | inventory/python-3.14/opt-0/pycdc | invalid_output | False | N/A | N/A | N/A | False |
| inventory | inventory/obfuscated-light-1 | inventory/python-3.14/opt-0/pycdc | invalid_output | False | N/A | N/A | N/A | False |
| inventory | inventory/obfuscated-light-2 | inventory/python-3.14/opt-0/pycdc | invalid_output | False | N/A | N/A | N/A | False |
| inventory | inventory/obfuscated-structural-0 | inventory/python-3.14/opt-0/pycdc | invalid_output | False | N/A | N/A | N/A | False |
| inventory | inventory/obfuscated-structural-1 | inventory/python-3.14/opt-0/pycdc | invalid_output | False | N/A | N/A | N/A | False |
| inventory | inventory/obfuscated-structural-2 | inventory/python-3.14/opt-0/pycdc | invalid_output | False | N/A | N/A | N/A | False |
| inventory | inventory/obfuscated-light-0 | inventory/python-3.14/opt-1/uncompyle6 | unsupported | False | 15.35 | 30.72 | 0.22 | False |
| inventory | inventory/obfuscated-light-1 | inventory/python-3.14/opt-1/uncompyle6 | unsupported | False | 15.35 | 30.72 | 0.22 | False |
| inventory | inventory/obfuscated-light-2 | inventory/python-3.14/opt-1/uncompyle6 | unsupported | False | 15.35 | 30.72 | 0.22 | False |
| inventory | inventory/obfuscated-structural-0 | inventory/python-3.14/opt-1/uncompyle6 | unsupported | False | 28.26 | 34.40 | 0.44 | False |
| inventory | inventory/obfuscated-structural-1 | inventory/python-3.14/opt-1/uncompyle6 | unsupported | False | 28.26 | 34.40 | 0.44 | False |
| inventory | inventory/obfuscated-structural-2 | inventory/python-3.14/opt-1/uncompyle6 | unsupported | False | 28.26 | 34.40 | 0.44 | False |
| inventory | inventory/obfuscated-light-0 | inventory/python-3.14/opt-1/pycdc | invalid_output | False | N/A | N/A | N/A | False |
| inventory | inventory/obfuscated-light-1 | inventory/python-3.14/opt-1/pycdc | invalid_output | False | N/A | N/A | N/A | False |
| inventory | inventory/obfuscated-light-2 | inventory/python-3.14/opt-1/pycdc | invalid_output | False | N/A | N/A | N/A | False |
| inventory | inventory/obfuscated-structural-0 | inventory/python-3.14/opt-1/pycdc | invalid_output | False | N/A | N/A | N/A | False |
| inventory | inventory/obfuscated-structural-1 | inventory/python-3.14/opt-1/pycdc | invalid_output | False | N/A | N/A | N/A | False |
| inventory | inventory/obfuscated-structural-2 | inventory/python-3.14/opt-1/pycdc | invalid_output | False | N/A | N/A | N/A | False |
| inventory | inventory/obfuscated-light-0 | inventory/python-3.14/opt-2/uncompyle6 | unsupported | False | 15.35 | 30.72 | 0.22 | False |
| inventory | inventory/obfuscated-light-1 | inventory/python-3.14/opt-2/uncompyle6 | unsupported | False | 15.35 | 30.72 | 0.22 | False |
| inventory | inventory/obfuscated-light-2 | inventory/python-3.14/opt-2/uncompyle6 | unsupported | False | 15.35 | 30.72 | 0.22 | False |
| inventory | inventory/obfuscated-structural-0 | inventory/python-3.14/opt-2/uncompyle6 | unsupported | False | 28.26 | 34.40 | 0.44 | False |
| inventory | inventory/obfuscated-structural-1 | inventory/python-3.14/opt-2/uncompyle6 | unsupported | False | 28.26 | 34.40 | 0.44 | False |
| inventory | inventory/obfuscated-structural-2 | inventory/python-3.14/opt-2/uncompyle6 | unsupported | False | 28.26 | 34.40 | 0.44 | False |
| inventory | inventory/obfuscated-light-0 | inventory/python-3.14/opt-2/pycdc | invalid_output | False | N/A | N/A | N/A | False |
| inventory | inventory/obfuscated-light-1 | inventory/python-3.14/opt-2/pycdc | invalid_output | False | N/A | N/A | N/A | False |
| inventory | inventory/obfuscated-light-2 | inventory/python-3.14/opt-2/pycdc | invalid_output | False | N/A | N/A | N/A | False |
| inventory | inventory/obfuscated-structural-0 | inventory/python-3.14/opt-2/pycdc | invalid_output | False | N/A | N/A | N/A | False |
| inventory | inventory/obfuscated-structural-1 | inventory/python-3.14/opt-2/pycdc | invalid_output | False | N/A | N/A | N/A | False |
| inventory | inventory/obfuscated-structural-2 | inventory/python-3.14/opt-2/pycdc | invalid_output | False | N/A | N/A | N/A | False |
| inventory | inventory/obfuscated-light-0 | inventory/python-3.4/opt-0/uncompyle6 | success | True | 100.00 | 100.00 | 100.00 | True |
| inventory | inventory/obfuscated-light-1 | inventory/python-3.4/opt-0/uncompyle6 | success | True | 100.00 | 100.00 | 100.00 | True |
| inventory | inventory/obfuscated-light-2 | inventory/python-3.4/opt-0/uncompyle6 | success | True | 100.00 | 100.00 | 100.00 | True |
| inventory | inventory/obfuscated-structural-0 | inventory/python-3.4/opt-0/uncompyle6 | success | True | 81.37 | 98.70 | 99.03 | False |
| inventory | inventory/obfuscated-structural-1 | inventory/python-3.4/opt-0/uncompyle6 | success | True | 81.37 | 98.70 | 99.03 | False |
| inventory | inventory/obfuscated-structural-2 | inventory/python-3.4/opt-0/uncompyle6 | success | True | 81.37 | 98.70 | 99.03 | False |
| inventory | inventory/obfuscated-light-0 | inventory/python-3.4/opt-0/pycdc | success | True | 97.43 | 99.28 | 99.41 | False |
| inventory | inventory/obfuscated-light-1 | inventory/python-3.4/opt-0/pycdc | success | True | 97.43 | 99.28 | 99.41 | False |
| inventory | inventory/obfuscated-light-2 | inventory/python-3.4/opt-0/pycdc | success | True | 97.43 | 99.28 | 99.41 | False |
| inventory | inventory/obfuscated-structural-0 | inventory/python-3.4/opt-0/pycdc | success | True | 81.90 | 98.55 | 98.52 | False |
| inventory | inventory/obfuscated-structural-1 | inventory/python-3.4/opt-0/pycdc | success | True | 81.90 | 98.55 | 98.52 | False |
| inventory | inventory/obfuscated-structural-2 | inventory/python-3.4/opt-0/pycdc | success | True | 81.90 | 98.55 | 98.52 | False |
| inventory | inventory/obfuscated-light-0 | inventory/python-3.4/opt-1/uncompyle6 | success | True | 100.00 | 100.00 | 100.00 | True |
| inventory | inventory/obfuscated-light-1 | inventory/python-3.4/opt-1/uncompyle6 | success | True | 100.00 | 100.00 | 100.00 | True |
| inventory | inventory/obfuscated-light-2 | inventory/python-3.4/opt-1/uncompyle6 | success | True | 100.00 | 100.00 | 100.00 | True |
| inventory | inventory/obfuscated-structural-0 | inventory/python-3.4/opt-1/uncompyle6 | success | True | 81.37 | 98.70 | 99.03 | False |
| inventory | inventory/obfuscated-structural-1 | inventory/python-3.4/opt-1/uncompyle6 | success | True | 81.37 | 98.70 | 99.03 | False |
| inventory | inventory/obfuscated-structural-2 | inventory/python-3.4/opt-1/uncompyle6 | success | True | 81.37 | 98.70 | 99.03 | False |
| inventory | inventory/obfuscated-light-0 | inventory/python-3.4/opt-1/pycdc | success | True | 97.43 | 99.28 | 99.41 | False |
| inventory | inventory/obfuscated-light-1 | inventory/python-3.4/opt-1/pycdc | success | True | 97.43 | 99.28 | 99.41 | False |
| inventory | inventory/obfuscated-light-2 | inventory/python-3.4/opt-1/pycdc | success | True | 97.43 | 99.28 | 99.41 | False |
| inventory | inventory/obfuscated-structural-0 | inventory/python-3.4/opt-1/pycdc | success | True | 81.90 | 98.55 | 98.52 | False |
| inventory | inventory/obfuscated-structural-1 | inventory/python-3.4/opt-1/pycdc | success | True | 81.90 | 98.55 | 98.52 | False |
| inventory | inventory/obfuscated-structural-2 | inventory/python-3.4/opt-1/pycdc | success | True | 81.90 | 98.55 | 98.52 | False |
| inventory | inventory/obfuscated-light-0 | inventory/python-3.4/opt-2/uncompyle6 | success | True | 100.00 | 100.00 | 100.00 | True |
| inventory | inventory/obfuscated-light-1 | inventory/python-3.4/opt-2/uncompyle6 | success | True | 100.00 | 100.00 | 100.00 | True |
| inventory | inventory/obfuscated-light-2 | inventory/python-3.4/opt-2/uncompyle6 | success | True | 100.00 | 100.00 | 100.00 | True |
| inventory | inventory/obfuscated-structural-0 | inventory/python-3.4/opt-2/uncompyle6 | success | True | 81.37 | 98.70 | 99.03 | False |
| inventory | inventory/obfuscated-structural-1 | inventory/python-3.4/opt-2/uncompyle6 | success | True | 81.37 | 98.70 | 99.03 | False |
| inventory | inventory/obfuscated-structural-2 | inventory/python-3.4/opt-2/uncompyle6 | success | True | 81.37 | 98.70 | 99.03 | False |
| inventory | inventory/obfuscated-light-0 | inventory/python-3.4/opt-2/pycdc | success | True | 97.43 | 99.28 | 99.41 | False |
| inventory | inventory/obfuscated-light-1 | inventory/python-3.4/opt-2/pycdc | success | True | 97.43 | 99.28 | 99.41 | False |
| inventory | inventory/obfuscated-light-2 | inventory/python-3.4/opt-2/pycdc | success | True | 97.43 | 99.28 | 99.41 | False |
| inventory | inventory/obfuscated-structural-0 | inventory/python-3.4/opt-2/pycdc | success | True | 81.90 | 98.55 | 98.52 | False |
| inventory | inventory/obfuscated-structural-1 | inventory/python-3.4/opt-2/pycdc | success | True | 81.90 | 98.55 | 98.52 | False |
| inventory | inventory/obfuscated-structural-2 | inventory/python-3.4/opt-2/pycdc | success | True | 81.90 | 98.55 | 98.52 | False |
| inventory | inventory/obfuscated-light-0 | inventory/python-3.8/opt-0/uncompyle6 | success | True | 99.82 | 99.99 | 100.00 | False |
| inventory | inventory/obfuscated-light-1 | inventory/python-3.8/opt-0/uncompyle6 | success | True | 99.82 | 99.99 | 100.00 | False |
| inventory | inventory/obfuscated-light-2 | inventory/python-3.8/opt-0/uncompyle6 | success | True | 99.82 | 99.99 | 100.00 | False |
| inventory | inventory/obfuscated-structural-0 | inventory/python-3.8/opt-0/uncompyle6 | success | True | 81.24 | 98.71 | 99.03 | False |
| inventory | inventory/obfuscated-structural-1 | inventory/python-3.8/opt-0/uncompyle6 | success | True | 81.24 | 98.71 | 99.03 | False |
| inventory | inventory/obfuscated-structural-2 | inventory/python-3.8/opt-0/uncompyle6 | success | True | 81.24 | 98.71 | 99.03 | False |
| inventory | inventory/obfuscated-light-0 | inventory/python-3.8/opt-0/pycdc | success | True | 97.43 | 99.28 | 99.41 | False |
| inventory | inventory/obfuscated-light-1 | inventory/python-3.8/opt-0/pycdc | success | True | 97.43 | 99.28 | 99.41 | False |
| inventory | inventory/obfuscated-light-2 | inventory/python-3.8/opt-0/pycdc | success | True | 97.43 | 99.28 | 99.41 | False |
| inventory | inventory/obfuscated-structural-0 | inventory/python-3.8/opt-0/pycdc | success | True | 81.90 | 98.55 | 98.52 | False |
| inventory | inventory/obfuscated-structural-1 | inventory/python-3.8/opt-0/pycdc | success | True | 81.90 | 98.55 | 98.52 | False |
| inventory | inventory/obfuscated-structural-2 | inventory/python-3.8/opt-0/pycdc | success | True | 81.90 | 98.55 | 98.52 | False |
| inventory | inventory/obfuscated-light-0 | inventory/python-3.8/opt-1/uncompyle6 | success | True | 99.82 | 99.99 | 100.00 | False |
| inventory | inventory/obfuscated-light-1 | inventory/python-3.8/opt-1/uncompyle6 | success | True | 99.82 | 99.99 | 100.00 | False |
| inventory | inventory/obfuscated-light-2 | inventory/python-3.8/opt-1/uncompyle6 | success | True | 99.82 | 99.99 | 100.00 | False |
| inventory | inventory/obfuscated-structural-0 | inventory/python-3.8/opt-1/uncompyle6 | success | True | 81.24 | 98.71 | 99.03 | False |
| inventory | inventory/obfuscated-structural-1 | inventory/python-3.8/opt-1/uncompyle6 | success | True | 81.24 | 98.71 | 99.03 | False |
| inventory | inventory/obfuscated-structural-2 | inventory/python-3.8/opt-1/uncompyle6 | success | True | 81.24 | 98.71 | 99.03 | False |
| inventory | inventory/obfuscated-light-0 | inventory/python-3.8/opt-1/pycdc | success | True | 97.43 | 99.28 | 99.41 | False |
| inventory | inventory/obfuscated-light-1 | inventory/python-3.8/opt-1/pycdc | success | True | 97.43 | 99.28 | 99.41 | False |
| inventory | inventory/obfuscated-light-2 | inventory/python-3.8/opt-1/pycdc | success | True | 97.43 | 99.28 | 99.41 | False |
| inventory | inventory/obfuscated-structural-0 | inventory/python-3.8/opt-1/pycdc | success | True | 81.90 | 98.55 | 98.52 | False |
| inventory | inventory/obfuscated-structural-1 | inventory/python-3.8/opt-1/pycdc | success | True | 81.90 | 98.55 | 98.52 | False |
| inventory | inventory/obfuscated-structural-2 | inventory/python-3.8/opt-1/pycdc | success | True | 81.90 | 98.55 | 98.52 | False |
| inventory | inventory/obfuscated-light-0 | inventory/python-3.8/opt-2/uncompyle6 | success | True | 99.82 | 99.99 | 100.00 | False |
| inventory | inventory/obfuscated-light-1 | inventory/python-3.8/opt-2/uncompyle6 | success | True | 99.82 | 99.99 | 100.00 | False |
| inventory | inventory/obfuscated-light-2 | inventory/python-3.8/opt-2/uncompyle6 | success | True | 99.82 | 99.99 | 100.00 | False |
| inventory | inventory/obfuscated-structural-0 | inventory/python-3.8/opt-2/uncompyle6 | success | True | 81.24 | 98.71 | 99.03 | False |
| inventory | inventory/obfuscated-structural-1 | inventory/python-3.8/opt-2/uncompyle6 | success | True | 81.24 | 98.71 | 99.03 | False |
| inventory | inventory/obfuscated-structural-2 | inventory/python-3.8/opt-2/uncompyle6 | success | True | 81.24 | 98.71 | 99.03 | False |
| inventory | inventory/obfuscated-light-0 | inventory/python-3.8/opt-2/pycdc | success | True | 97.43 | 99.28 | 99.41 | False |
| inventory | inventory/obfuscated-light-1 | inventory/python-3.8/opt-2/pycdc | success | True | 97.43 | 99.28 | 99.41 | False |
| inventory | inventory/obfuscated-light-2 | inventory/python-3.8/opt-2/pycdc | success | True | 97.43 | 99.28 | 99.41 | False |
| inventory | inventory/obfuscated-structural-0 | inventory/python-3.8/opt-2/pycdc | success | True | 81.90 | 98.55 | 98.52 | False |
| inventory | inventory/obfuscated-structural-1 | inventory/python-3.8/opt-2/pycdc | success | True | 81.90 | 98.55 | 98.52 | False |
| inventory | inventory/obfuscated-structural-2 | inventory/python-3.8/opt-2/pycdc | success | True | 81.90 | 98.55 | 98.52 | False |
| invoice | invoice/obfuscated-light-0 | invoice/python-3.12/opt-0/uncompyle6 | unsupported | False | 11.07 | 21.62 | 0.00 | False |
| invoice | invoice/obfuscated-light-1 | invoice/python-3.12/opt-0/uncompyle6 | unsupported | False | 11.07 | 21.62 | 0.00 | False |
| invoice | invoice/obfuscated-light-2 | invoice/python-3.12/opt-0/uncompyle6 | unsupported | False | 11.07 | 21.62 | 0.00 | False |
| invoice | invoice/obfuscated-structural-0 | invoice/python-3.12/opt-0/uncompyle6 | unsupported | False | 16.53 | 29.61 | 0.36 | False |
| invoice | invoice/obfuscated-structural-1 | invoice/python-3.12/opt-0/uncompyle6 | unsupported | False | 16.53 | 29.61 | 0.36 | False |
| invoice | invoice/obfuscated-structural-2 | invoice/python-3.12/opt-0/uncompyle6 | unsupported | False | 16.53 | 29.61 | 0.36 | False |
| invoice | invoice/obfuscated-light-0 | invoice/python-3.12/opt-0/pycdc | unsupported | False | 85.39 | 96.13 | 96.97 | False |
| invoice | invoice/obfuscated-light-1 | invoice/python-3.12/opt-0/pycdc | unsupported | False | 85.39 | 96.13 | 96.97 | False |
| invoice | invoice/obfuscated-light-2 | invoice/python-3.12/opt-0/pycdc | unsupported | False | 85.39 | 96.13 | 96.97 | False |
| invoice | invoice/obfuscated-structural-0 | invoice/python-3.12/opt-0/pycdc | unsupported | False | 75.15 | 95.18 | 93.81 | False |
| invoice | invoice/obfuscated-structural-1 | invoice/python-3.12/opt-0/pycdc | unsupported | False | 75.15 | 95.18 | 93.81 | False |
| invoice | invoice/obfuscated-structural-2 | invoice/python-3.12/opt-0/pycdc | unsupported | False | 75.15 | 95.18 | 93.81 | False |
| invoice | invoice/obfuscated-light-0 | invoice/python-3.12/opt-1/uncompyle6 | unsupported | False | 11.07 | 21.62 | 0.00 | False |
| invoice | invoice/obfuscated-light-1 | invoice/python-3.12/opt-1/uncompyle6 | unsupported | False | 11.07 | 21.62 | 0.00 | False |
| invoice | invoice/obfuscated-light-2 | invoice/python-3.12/opt-1/uncompyle6 | unsupported | False | 11.07 | 21.62 | 0.00 | False |
| invoice | invoice/obfuscated-structural-0 | invoice/python-3.12/opt-1/uncompyle6 | unsupported | False | 16.53 | 29.61 | 0.36 | False |
| invoice | invoice/obfuscated-structural-1 | invoice/python-3.12/opt-1/uncompyle6 | unsupported | False | 16.53 | 29.61 | 0.36 | False |
| invoice | invoice/obfuscated-structural-2 | invoice/python-3.12/opt-1/uncompyle6 | unsupported | False | 16.53 | 29.61 | 0.36 | False |
| invoice | invoice/obfuscated-light-0 | invoice/python-3.12/opt-1/pycdc | unsupported | False | 85.39 | 96.13 | 96.97 | False |
| invoice | invoice/obfuscated-light-1 | invoice/python-3.12/opt-1/pycdc | unsupported | False | 85.39 | 96.13 | 96.97 | False |
| invoice | invoice/obfuscated-light-2 | invoice/python-3.12/opt-1/pycdc | unsupported | False | 85.39 | 96.13 | 96.97 | False |
| invoice | invoice/obfuscated-structural-0 | invoice/python-3.12/opt-1/pycdc | unsupported | False | 75.15 | 95.18 | 93.81 | False |
| invoice | invoice/obfuscated-structural-1 | invoice/python-3.12/opt-1/pycdc | unsupported | False | 75.15 | 95.18 | 93.81 | False |
| invoice | invoice/obfuscated-structural-2 | invoice/python-3.12/opt-1/pycdc | unsupported | False | 75.15 | 95.18 | 93.81 | False |
| invoice | invoice/obfuscated-light-0 | invoice/python-3.12/opt-2/uncompyle6 | unsupported | False | 11.07 | 21.62 | 0.00 | False |
| invoice | invoice/obfuscated-light-1 | invoice/python-3.12/opt-2/uncompyle6 | unsupported | False | 11.07 | 21.62 | 0.00 | False |
| invoice | invoice/obfuscated-light-2 | invoice/python-3.12/opt-2/uncompyle6 | unsupported | False | 11.07 | 21.62 | 0.00 | False |
| invoice | invoice/obfuscated-structural-0 | invoice/python-3.12/opt-2/uncompyle6 | unsupported | False | 16.53 | 29.61 | 0.36 | False |
| invoice | invoice/obfuscated-structural-1 | invoice/python-3.12/opt-2/uncompyle6 | unsupported | False | 16.53 | 29.61 | 0.36 | False |
| invoice | invoice/obfuscated-structural-2 | invoice/python-3.12/opt-2/uncompyle6 | unsupported | False | 16.53 | 29.61 | 0.36 | False |
| invoice | invoice/obfuscated-light-0 | invoice/python-3.12/opt-2/pycdc | unsupported | False | 85.39 | 96.13 | 96.97 | False |
| invoice | invoice/obfuscated-light-1 | invoice/python-3.12/opt-2/pycdc | unsupported | False | 85.39 | 96.13 | 96.97 | False |
| invoice | invoice/obfuscated-light-2 | invoice/python-3.12/opt-2/pycdc | unsupported | False | 85.39 | 96.13 | 96.97 | False |
| invoice | invoice/obfuscated-structural-0 | invoice/python-3.12/opt-2/pycdc | unsupported | False | 75.15 | 95.18 | 93.81 | False |
| invoice | invoice/obfuscated-structural-1 | invoice/python-3.12/opt-2/pycdc | unsupported | False | 75.15 | 95.18 | 93.81 | False |
| invoice | invoice/obfuscated-structural-2 | invoice/python-3.12/opt-2/pycdc | unsupported | False | 75.15 | 95.18 | 93.81 | False |
| invoice | invoice/obfuscated-light-0 | invoice/python-3.14/opt-0/uncompyle6 | unsupported | False | 9.48 | 23.93 | 0.00 | False |
| invoice | invoice/obfuscated-light-1 | invoice/python-3.14/opt-0/uncompyle6 | unsupported | False | 9.48 | 23.93 | 0.00 | False |
| invoice | invoice/obfuscated-light-2 | invoice/python-3.14/opt-0/uncompyle6 | unsupported | False | 9.48 | 23.93 | 0.00 | False |
| invoice | invoice/obfuscated-structural-0 | invoice/python-3.14/opt-0/uncompyle6 | unsupported | False | 14.67 | 31.12 | 0.36 | False |
| invoice | invoice/obfuscated-structural-1 | invoice/python-3.14/opt-0/uncompyle6 | unsupported | False | 14.67 | 31.12 | 0.36 | False |
| invoice | invoice/obfuscated-structural-2 | invoice/python-3.14/opt-0/uncompyle6 | unsupported | False | 14.67 | 31.12 | 0.36 | False |
| invoice | invoice/obfuscated-light-0 | invoice/python-3.14/opt-0/pycdc | invalid_output | False | N/A | N/A | N/A | False |
| invoice | invoice/obfuscated-light-1 | invoice/python-3.14/opt-0/pycdc | invalid_output | False | N/A | N/A | N/A | False |
| invoice | invoice/obfuscated-light-2 | invoice/python-3.14/opt-0/pycdc | invalid_output | False | N/A | N/A | N/A | False |
| invoice | invoice/obfuscated-structural-0 | invoice/python-3.14/opt-0/pycdc | invalid_output | False | N/A | N/A | N/A | False |
| invoice | invoice/obfuscated-structural-1 | invoice/python-3.14/opt-0/pycdc | invalid_output | False | N/A | N/A | N/A | False |
| invoice | invoice/obfuscated-structural-2 | invoice/python-3.14/opt-0/pycdc | invalid_output | False | N/A | N/A | N/A | False |
| invoice | invoice/obfuscated-light-0 | invoice/python-3.14/opt-1/uncompyle6 | unsupported | False | 9.48 | 23.93 | 0.00 | False |
| invoice | invoice/obfuscated-light-1 | invoice/python-3.14/opt-1/uncompyle6 | unsupported | False | 9.48 | 23.93 | 0.00 | False |
| invoice | invoice/obfuscated-light-2 | invoice/python-3.14/opt-1/uncompyle6 | unsupported | False | 9.48 | 23.93 | 0.00 | False |
| invoice | invoice/obfuscated-structural-0 | invoice/python-3.14/opt-1/uncompyle6 | unsupported | False | 14.67 | 31.12 | 0.36 | False |
| invoice | invoice/obfuscated-structural-1 | invoice/python-3.14/opt-1/uncompyle6 | unsupported | False | 14.67 | 31.12 | 0.36 | False |
| invoice | invoice/obfuscated-structural-2 | invoice/python-3.14/opt-1/uncompyle6 | unsupported | False | 14.67 | 31.12 | 0.36 | False |
| invoice | invoice/obfuscated-light-0 | invoice/python-3.14/opt-1/pycdc | invalid_output | False | N/A | N/A | N/A | False |
| invoice | invoice/obfuscated-light-1 | invoice/python-3.14/opt-1/pycdc | invalid_output | False | N/A | N/A | N/A | False |
| invoice | invoice/obfuscated-light-2 | invoice/python-3.14/opt-1/pycdc | invalid_output | False | N/A | N/A | N/A | False |
| invoice | invoice/obfuscated-structural-0 | invoice/python-3.14/opt-1/pycdc | invalid_output | False | N/A | N/A | N/A | False |
| invoice | invoice/obfuscated-structural-1 | invoice/python-3.14/opt-1/pycdc | invalid_output | False | N/A | N/A | N/A | False |
| invoice | invoice/obfuscated-structural-2 | invoice/python-3.14/opt-1/pycdc | invalid_output | False | N/A | N/A | N/A | False |
| invoice | invoice/obfuscated-light-0 | invoice/python-3.14/opt-2/uncompyle6 | unsupported | False | 9.48 | 23.93 | 0.00 | False |
| invoice | invoice/obfuscated-light-1 | invoice/python-3.14/opt-2/uncompyle6 | unsupported | False | 9.48 | 23.93 | 0.00 | False |
| invoice | invoice/obfuscated-light-2 | invoice/python-3.14/opt-2/uncompyle6 | unsupported | False | 9.48 | 23.93 | 0.00 | False |
| invoice | invoice/obfuscated-structural-0 | invoice/python-3.14/opt-2/uncompyle6 | unsupported | False | 14.67 | 31.12 | 0.36 | False |
| invoice | invoice/obfuscated-structural-1 | invoice/python-3.14/opt-2/uncompyle6 | unsupported | False | 14.67 | 31.12 | 0.36 | False |
| invoice | invoice/obfuscated-structural-2 | invoice/python-3.14/opt-2/uncompyle6 | unsupported | False | 14.67 | 31.12 | 0.36 | False |
| invoice | invoice/obfuscated-light-0 | invoice/python-3.14/opt-2/pycdc | invalid_output | False | N/A | N/A | N/A | False |
| invoice | invoice/obfuscated-light-1 | invoice/python-3.14/opt-2/pycdc | invalid_output | False | N/A | N/A | N/A | False |
| invoice | invoice/obfuscated-light-2 | invoice/python-3.14/opt-2/pycdc | invalid_output | False | N/A | N/A | N/A | False |
| invoice | invoice/obfuscated-structural-0 | invoice/python-3.14/opt-2/pycdc | invalid_output | False | N/A | N/A | N/A | False |
| invoice | invoice/obfuscated-structural-1 | invoice/python-3.14/opt-2/pycdc | invalid_output | False | N/A | N/A | N/A | False |
| invoice | invoice/obfuscated-structural-2 | invoice/python-3.14/opt-2/pycdc | invalid_output | False | N/A | N/A | N/A | False |
| invoice | invoice/obfuscated-light-0 | invoice/python-3.4/opt-0/uncompyle6 | success | True | 100.00 | 100.00 | 100.00 | True |
| invoice | invoice/obfuscated-light-1 | invoice/python-3.4/opt-0/uncompyle6 | success | True | 100.00 | 100.00 | 100.00 | True |
| invoice | invoice/obfuscated-light-2 | invoice/python-3.4/opt-0/uncompyle6 | success | True | 100.00 | 100.00 | 100.00 | True |
| invoice | invoice/obfuscated-structural-0 | invoice/python-3.4/opt-0/uncompyle6 | success | True | 71.38 | 96.16 | 96.75 | False |
| invoice | invoice/obfuscated-structural-1 | invoice/python-3.4/opt-0/uncompyle6 | success | True | 71.38 | 96.16 | 96.75 | False |
| invoice | invoice/obfuscated-structural-2 | invoice/python-3.4/opt-0/uncompyle6 | success | True | 71.38 | 96.16 | 96.75 | False |
| invoice | invoice/obfuscated-light-0 | invoice/python-3.4/opt-0/pycdc | invalid_output | False | 75.35 | 82.36 | 68.51 | False |
| invoice | invoice/obfuscated-light-1 | invoice/python-3.4/opt-0/pycdc | invalid_output | False | 75.35 | 82.36 | 68.51 | False |
| invoice | invoice/obfuscated-light-2 | invoice/python-3.4/opt-0/pycdc | invalid_output | False | 75.35 | 82.36 | 68.51 | False |
| invoice | invoice/obfuscated-structural-0 | invoice/python-3.4/opt-0/pycdc | invalid_output | False | 57.09 | 82.46 | 66.93 | False |
| invoice | invoice/obfuscated-structural-1 | invoice/python-3.4/opt-0/pycdc | invalid_output | False | 57.09 | 82.46 | 66.93 | False |
| invoice | invoice/obfuscated-structural-2 | invoice/python-3.4/opt-0/pycdc | invalid_output | False | 57.09 | 82.46 | 66.93 | False |
| invoice | invoice/obfuscated-light-0 | invoice/python-3.4/opt-1/uncompyle6 | success | True | 100.00 | 100.00 | 100.00 | True |
| invoice | invoice/obfuscated-light-1 | invoice/python-3.4/opt-1/uncompyle6 | success | True | 100.00 | 100.00 | 100.00 | True |
| invoice | invoice/obfuscated-light-2 | invoice/python-3.4/opt-1/uncompyle6 | success | True | 100.00 | 100.00 | 100.00 | True |
| invoice | invoice/obfuscated-structural-0 | invoice/python-3.4/opt-1/uncompyle6 | success | True | 71.38 | 96.16 | 96.75 | False |
| invoice | invoice/obfuscated-structural-1 | invoice/python-3.4/opt-1/uncompyle6 | success | True | 71.38 | 96.16 | 96.75 | False |
| invoice | invoice/obfuscated-structural-2 | invoice/python-3.4/opt-1/uncompyle6 | success | True | 71.38 | 96.16 | 96.75 | False |
| invoice | invoice/obfuscated-light-0 | invoice/python-3.4/opt-1/pycdc | invalid_output | False | 75.35 | 82.36 | 68.51 | False |
| invoice | invoice/obfuscated-light-1 | invoice/python-3.4/opt-1/pycdc | invalid_output | False | 75.35 | 82.36 | 68.51 | False |
| invoice | invoice/obfuscated-light-2 | invoice/python-3.4/opt-1/pycdc | invalid_output | False | 75.35 | 82.36 | 68.51 | False |
| invoice | invoice/obfuscated-structural-0 | invoice/python-3.4/opt-1/pycdc | invalid_output | False | 57.09 | 82.46 | 66.93 | False |
| invoice | invoice/obfuscated-structural-1 | invoice/python-3.4/opt-1/pycdc | invalid_output | False | 57.09 | 82.46 | 66.93 | False |
| invoice | invoice/obfuscated-structural-2 | invoice/python-3.4/opt-1/pycdc | invalid_output | False | 57.09 | 82.46 | 66.93 | False |
| invoice | invoice/obfuscated-light-0 | invoice/python-3.4/opt-2/uncompyle6 | success | True | 100.00 | 100.00 | 100.00 | True |
| invoice | invoice/obfuscated-light-1 | invoice/python-3.4/opt-2/uncompyle6 | success | True | 100.00 | 100.00 | 100.00 | True |
| invoice | invoice/obfuscated-light-2 | invoice/python-3.4/opt-2/uncompyle6 | success | True | 100.00 | 100.00 | 100.00 | True |
| invoice | invoice/obfuscated-structural-0 | invoice/python-3.4/opt-2/uncompyle6 | success | True | 71.38 | 96.16 | 96.75 | False |
| invoice | invoice/obfuscated-structural-1 | invoice/python-3.4/opt-2/uncompyle6 | success | True | 71.38 | 96.16 | 96.75 | False |
| invoice | invoice/obfuscated-structural-2 | invoice/python-3.4/opt-2/uncompyle6 | success | True | 71.38 | 96.16 | 96.75 | False |
| invoice | invoice/obfuscated-light-0 | invoice/python-3.4/opt-2/pycdc | invalid_output | False | 75.35 | 82.36 | 68.51 | False |
| invoice | invoice/obfuscated-light-1 | invoice/python-3.4/opt-2/pycdc | invalid_output | False | 75.35 | 82.36 | 68.51 | False |
| invoice | invoice/obfuscated-light-2 | invoice/python-3.4/opt-2/pycdc | invalid_output | False | 75.35 | 82.36 | 68.51 | False |
| invoice | invoice/obfuscated-structural-0 | invoice/python-3.4/opt-2/pycdc | invalid_output | False | 57.09 | 82.46 | 66.93 | False |
| invoice | invoice/obfuscated-structural-1 | invoice/python-3.4/opt-2/pycdc | invalid_output | False | 57.09 | 82.46 | 66.93 | False |
| invoice | invoice/obfuscated-structural-2 | invoice/python-3.4/opt-2/pycdc | invalid_output | False | 57.09 | 82.46 | 66.93 | False |
| invoice | invoice/obfuscated-light-0 | invoice/python-3.8/opt-0/uncompyle6 | success | True | 100.00 | 100.00 | 100.00 | True |
| invoice | invoice/obfuscated-light-1 | invoice/python-3.8/opt-0/uncompyle6 | success | True | 100.00 | 100.00 | 100.00 | True |
| invoice | invoice/obfuscated-light-2 | invoice/python-3.8/opt-0/uncompyle6 | success | True | 100.00 | 100.00 | 100.00 | True |
| invoice | invoice/obfuscated-structural-0 | invoice/python-3.8/opt-0/uncompyle6 | success | True | 71.38 | 96.16 | 96.75 | False |
| invoice | invoice/obfuscated-structural-1 | invoice/python-3.8/opt-0/uncompyle6 | success | True | 71.38 | 96.16 | 96.75 | False |
| invoice | invoice/obfuscated-structural-2 | invoice/python-3.8/opt-0/uncompyle6 | success | True | 71.38 | 96.16 | 96.75 | False |
| invoice | invoice/obfuscated-light-0 | invoice/python-3.8/opt-0/pycdc | invalid_output | False | 75.45 | 82.22 | 68.51 | False |
| invoice | invoice/obfuscated-light-1 | invoice/python-3.8/opt-0/pycdc | invalid_output | False | 75.45 | 82.22 | 68.51 | False |
| invoice | invoice/obfuscated-light-2 | invoice/python-3.8/opt-0/pycdc | invalid_output | False | 75.45 | 82.22 | 68.51 | False |
| invoice | invoice/obfuscated-structural-0 | invoice/python-3.8/opt-0/pycdc | invalid_output | False | 57.33 | 82.45 | 66.93 | False |
| invoice | invoice/obfuscated-structural-1 | invoice/python-3.8/opt-0/pycdc | invalid_output | False | 57.33 | 82.45 | 66.93 | False |
| invoice | invoice/obfuscated-structural-2 | invoice/python-3.8/opt-0/pycdc | invalid_output | False | 57.33 | 82.45 | 66.93 | False |
| invoice | invoice/obfuscated-light-0 | invoice/python-3.8/opt-1/uncompyle6 | success | True | 100.00 | 100.00 | 100.00 | True |
| invoice | invoice/obfuscated-light-1 | invoice/python-3.8/opt-1/uncompyle6 | success | True | 100.00 | 100.00 | 100.00 | True |
| invoice | invoice/obfuscated-light-2 | invoice/python-3.8/opt-1/uncompyle6 | success | True | 100.00 | 100.00 | 100.00 | True |
| invoice | invoice/obfuscated-structural-0 | invoice/python-3.8/opt-1/uncompyle6 | success | True | 71.38 | 96.16 | 96.75 | False |
| invoice | invoice/obfuscated-structural-1 | invoice/python-3.8/opt-1/uncompyle6 | success | True | 71.38 | 96.16 | 96.75 | False |
| invoice | invoice/obfuscated-structural-2 | invoice/python-3.8/opt-1/uncompyle6 | success | True | 71.38 | 96.16 | 96.75 | False |
| invoice | invoice/obfuscated-light-0 | invoice/python-3.8/opt-1/pycdc | invalid_output | False | 75.45 | 82.22 | 68.51 | False |
| invoice | invoice/obfuscated-light-1 | invoice/python-3.8/opt-1/pycdc | invalid_output | False | 75.45 | 82.22 | 68.51 | False |
| invoice | invoice/obfuscated-light-2 | invoice/python-3.8/opt-1/pycdc | invalid_output | False | 75.45 | 82.22 | 68.51 | False |
| invoice | invoice/obfuscated-structural-0 | invoice/python-3.8/opt-1/pycdc | invalid_output | False | 57.33 | 82.45 | 66.93 | False |
| invoice | invoice/obfuscated-structural-1 | invoice/python-3.8/opt-1/pycdc | invalid_output | False | 57.33 | 82.45 | 66.93 | False |
| invoice | invoice/obfuscated-structural-2 | invoice/python-3.8/opt-1/pycdc | invalid_output | False | 57.33 | 82.45 | 66.93 | False |
| invoice | invoice/obfuscated-light-0 | invoice/python-3.8/opt-2/uncompyle6 | success | True | 100.00 | 100.00 | 100.00 | True |
| invoice | invoice/obfuscated-light-1 | invoice/python-3.8/opt-2/uncompyle6 | success | True | 100.00 | 100.00 | 100.00 | True |
| invoice | invoice/obfuscated-light-2 | invoice/python-3.8/opt-2/uncompyle6 | success | True | 100.00 | 100.00 | 100.00 | True |
| invoice | invoice/obfuscated-structural-0 | invoice/python-3.8/opt-2/uncompyle6 | success | True | 71.38 | 96.16 | 96.75 | False |
| invoice | invoice/obfuscated-structural-1 | invoice/python-3.8/opt-2/uncompyle6 | success | True | 71.38 | 96.16 | 96.75 | False |
| invoice | invoice/obfuscated-structural-2 | invoice/python-3.8/opt-2/uncompyle6 | success | True | 71.38 | 96.16 | 96.75 | False |
| invoice | invoice/obfuscated-light-0 | invoice/python-3.8/opt-2/pycdc | invalid_output | False | 75.45 | 82.22 | 68.51 | False |
| invoice | invoice/obfuscated-light-1 | invoice/python-3.8/opt-2/pycdc | invalid_output | False | 75.45 | 82.22 | 68.51 | False |
| invoice | invoice/obfuscated-light-2 | invoice/python-3.8/opt-2/pycdc | invalid_output | False | 75.45 | 82.22 | 68.51 | False |
| invoice | invoice/obfuscated-structural-0 | invoice/python-3.8/opt-2/pycdc | invalid_output | False | 57.33 | 82.45 | 66.93 | False |
| invoice | invoice/obfuscated-structural-1 | invoice/python-3.8/opt-2/pycdc | invalid_output | False | 57.33 | 82.45 | 66.93 | False |
| invoice | invoice/obfuscated-structural-2 | invoice/python-3.8/opt-2/pycdc | invalid_output | False | 57.33 | 82.45 | 66.93 | False |
| memo | memo/obfuscated-light-0 | memo/python-3.12/opt-0/uncompyle6 | unsupported | False | 11.77 | 26.63 | 1.10 | False |
| memo | memo/obfuscated-light-1 | memo/python-3.12/opt-0/uncompyle6 | unsupported | False | 11.77 | 26.63 | 1.10 | False |
| memo | memo/obfuscated-light-2 | memo/python-3.12/opt-0/uncompyle6 | unsupported | False | 11.77 | 26.63 | 1.10 | False |
| memo | memo/obfuscated-structural-0 | memo/python-3.12/opt-0/uncompyle6 | unsupported | False | 10.70 | 31.38 | 1.11 | False |
| memo | memo/obfuscated-structural-1 | memo/python-3.12/opt-0/uncompyle6 | unsupported | False | 10.70 | 31.38 | 1.11 | False |
| memo | memo/obfuscated-structural-2 | memo/python-3.12/opt-0/uncompyle6 | unsupported | False | 10.70 | 31.38 | 1.11 | False |
| memo | memo/obfuscated-light-0 | memo/python-3.12/opt-0/pycdc | unsupported | False | 56.52 | 90.92 | 89.26 | False |
| memo | memo/obfuscated-light-1 | memo/python-3.12/opt-0/pycdc | unsupported | False | 56.52 | 90.92 | 89.26 | False |
| memo | memo/obfuscated-light-2 | memo/python-3.12/opt-0/pycdc | unsupported | False | 56.52 | 90.92 | 89.26 | False |
| memo | memo/obfuscated-structural-0 | memo/python-3.12/opt-0/pycdc | unsupported | False | 56.68 | 91.48 | 87.64 | False |
| memo | memo/obfuscated-structural-1 | memo/python-3.12/opt-0/pycdc | unsupported | False | 56.68 | 91.48 | 87.64 | False |
| memo | memo/obfuscated-structural-2 | memo/python-3.12/opt-0/pycdc | unsupported | False | 56.68 | 91.48 | 87.64 | False |
| memo | memo/obfuscated-light-0 | memo/python-3.12/opt-1/uncompyle6 | unsupported | False | 11.77 | 26.63 | 1.10 | False |
| memo | memo/obfuscated-light-1 | memo/python-3.12/opt-1/uncompyle6 | unsupported | False | 11.77 | 26.63 | 1.10 | False |
| memo | memo/obfuscated-light-2 | memo/python-3.12/opt-1/uncompyle6 | unsupported | False | 11.77 | 26.63 | 1.10 | False |
| memo | memo/obfuscated-structural-0 | memo/python-3.12/opt-1/uncompyle6 | unsupported | False | 10.70 | 31.38 | 1.11 | False |
| memo | memo/obfuscated-structural-1 | memo/python-3.12/opt-1/uncompyle6 | unsupported | False | 10.70 | 31.38 | 1.11 | False |
| memo | memo/obfuscated-structural-2 | memo/python-3.12/opt-1/uncompyle6 | unsupported | False | 10.70 | 31.38 | 1.11 | False |
| memo | memo/obfuscated-light-0 | memo/python-3.12/opt-1/pycdc | unsupported | False | 56.52 | 90.92 | 89.26 | False |
| memo | memo/obfuscated-light-1 | memo/python-3.12/opt-1/pycdc | unsupported | False | 56.52 | 90.92 | 89.26 | False |
| memo | memo/obfuscated-light-2 | memo/python-3.12/opt-1/pycdc | unsupported | False | 56.52 | 90.92 | 89.26 | False |
| memo | memo/obfuscated-structural-0 | memo/python-3.12/opt-1/pycdc | unsupported | False | 56.68 | 91.48 | 87.64 | False |
| memo | memo/obfuscated-structural-1 | memo/python-3.12/opt-1/pycdc | unsupported | False | 56.68 | 91.48 | 87.64 | False |
| memo | memo/obfuscated-structural-2 | memo/python-3.12/opt-1/pycdc | unsupported | False | 56.68 | 91.48 | 87.64 | False |
| memo | memo/obfuscated-light-0 | memo/python-3.12/opt-2/uncompyle6 | unsupported | False | 11.77 | 26.63 | 1.10 | False |
| memo | memo/obfuscated-light-1 | memo/python-3.12/opt-2/uncompyle6 | unsupported | False | 11.77 | 26.63 | 1.10 | False |
| memo | memo/obfuscated-light-2 | memo/python-3.12/opt-2/uncompyle6 | unsupported | False | 11.77 | 26.63 | 1.10 | False |
| memo | memo/obfuscated-structural-0 | memo/python-3.12/opt-2/uncompyle6 | unsupported | False | 10.70 | 31.38 | 1.11 | False |
| memo | memo/obfuscated-structural-1 | memo/python-3.12/opt-2/uncompyle6 | unsupported | False | 10.70 | 31.38 | 1.11 | False |
| memo | memo/obfuscated-structural-2 | memo/python-3.12/opt-2/uncompyle6 | unsupported | False | 10.70 | 31.38 | 1.11 | False |
| memo | memo/obfuscated-light-0 | memo/python-3.12/opt-2/pycdc | unsupported | False | 56.52 | 90.92 | 89.26 | False |
| memo | memo/obfuscated-light-1 | memo/python-3.12/opt-2/pycdc | unsupported | False | 56.52 | 90.92 | 89.26 | False |
| memo | memo/obfuscated-light-2 | memo/python-3.12/opt-2/pycdc | unsupported | False | 56.52 | 90.92 | 89.26 | False |
| memo | memo/obfuscated-structural-0 | memo/python-3.12/opt-2/pycdc | unsupported | False | 56.68 | 91.48 | 87.64 | False |
| memo | memo/obfuscated-structural-1 | memo/python-3.12/opt-2/pycdc | unsupported | False | 56.68 | 91.48 | 87.64 | False |
| memo | memo/obfuscated-structural-2 | memo/python-3.12/opt-2/pycdc | unsupported | False | 56.68 | 91.48 | 87.64 | False |
| memo | memo/obfuscated-light-0 | memo/python-3.14/opt-0/uncompyle6 | unsupported | False | 10.69 | 27.98 | 1.09 | False |
| memo | memo/obfuscated-light-1 | memo/python-3.14/opt-0/uncompyle6 | unsupported | False | 10.69 | 27.98 | 1.09 | False |
| memo | memo/obfuscated-light-2 | memo/python-3.14/opt-0/uncompyle6 | unsupported | False | 10.69 | 27.98 | 1.09 | False |
| memo | memo/obfuscated-structural-0 | memo/python-3.14/opt-0/uncompyle6 | unsupported | False | 9.74 | 32.64 | 1.11 | False |
| memo | memo/obfuscated-structural-1 | memo/python-3.14/opt-0/uncompyle6 | unsupported | False | 9.74 | 32.64 | 1.11 | False |
| memo | memo/obfuscated-structural-2 | memo/python-3.14/opt-0/uncompyle6 | unsupported | False | 9.74 | 32.64 | 1.11 | False |
| memo | memo/obfuscated-light-0 | memo/python-3.14/opt-0/pycdc | invalid_output | False | N/A | N/A | N/A | False |
| memo | memo/obfuscated-light-1 | memo/python-3.14/opt-0/pycdc | invalid_output | False | N/A | N/A | N/A | False |
| memo | memo/obfuscated-light-2 | memo/python-3.14/opt-0/pycdc | invalid_output | False | N/A | N/A | N/A | False |
| memo | memo/obfuscated-structural-0 | memo/python-3.14/opt-0/pycdc | invalid_output | False | N/A | N/A | N/A | False |
| memo | memo/obfuscated-structural-1 | memo/python-3.14/opt-0/pycdc | invalid_output | False | N/A | N/A | N/A | False |
| memo | memo/obfuscated-structural-2 | memo/python-3.14/opt-0/pycdc | invalid_output | False | N/A | N/A | N/A | False |
| memo | memo/obfuscated-light-0 | memo/python-3.14/opt-1/uncompyle6 | unsupported | False | 10.69 | 27.98 | 1.09 | False |
| memo | memo/obfuscated-light-1 | memo/python-3.14/opt-1/uncompyle6 | unsupported | False | 10.69 | 27.98 | 1.09 | False |
| memo | memo/obfuscated-light-2 | memo/python-3.14/opt-1/uncompyle6 | unsupported | False | 10.69 | 27.98 | 1.09 | False |
| memo | memo/obfuscated-structural-0 | memo/python-3.14/opt-1/uncompyle6 | unsupported | False | 9.74 | 32.64 | 1.11 | False |
| memo | memo/obfuscated-structural-1 | memo/python-3.14/opt-1/uncompyle6 | unsupported | False | 9.74 | 32.64 | 1.11 | False |
| memo | memo/obfuscated-structural-2 | memo/python-3.14/opt-1/uncompyle6 | unsupported | False | 9.74 | 32.64 | 1.11 | False |
| memo | memo/obfuscated-light-0 | memo/python-3.14/opt-1/pycdc | invalid_output | False | N/A | N/A | N/A | False |
| memo | memo/obfuscated-light-1 | memo/python-3.14/opt-1/pycdc | invalid_output | False | N/A | N/A | N/A | False |
| memo | memo/obfuscated-light-2 | memo/python-3.14/opt-1/pycdc | invalid_output | False | N/A | N/A | N/A | False |
| memo | memo/obfuscated-structural-0 | memo/python-3.14/opt-1/pycdc | invalid_output | False | N/A | N/A | N/A | False |
| memo | memo/obfuscated-structural-1 | memo/python-3.14/opt-1/pycdc | invalid_output | False | N/A | N/A | N/A | False |
| memo | memo/obfuscated-structural-2 | memo/python-3.14/opt-1/pycdc | invalid_output | False | N/A | N/A | N/A | False |
| memo | memo/obfuscated-light-0 | memo/python-3.14/opt-2/uncompyle6 | unsupported | False | 10.69 | 27.98 | 1.09 | False |
| memo | memo/obfuscated-light-1 | memo/python-3.14/opt-2/uncompyle6 | unsupported | False | 10.69 | 27.98 | 1.09 | False |
| memo | memo/obfuscated-light-2 | memo/python-3.14/opt-2/uncompyle6 | unsupported | False | 10.69 | 27.98 | 1.09 | False |
| memo | memo/obfuscated-structural-0 | memo/python-3.14/opt-2/uncompyle6 | unsupported | False | 9.74 | 32.64 | 1.11 | False |
| memo | memo/obfuscated-structural-1 | memo/python-3.14/opt-2/uncompyle6 | unsupported | False | 9.74 | 32.64 | 1.11 | False |
| memo | memo/obfuscated-structural-2 | memo/python-3.14/opt-2/uncompyle6 | unsupported | False | 9.74 | 32.64 | 1.11 | False |
| memo | memo/obfuscated-light-0 | memo/python-3.14/opt-2/pycdc | invalid_output | False | N/A | N/A | N/A | False |
| memo | memo/obfuscated-light-1 | memo/python-3.14/opt-2/pycdc | invalid_output | False | N/A | N/A | N/A | False |
| memo | memo/obfuscated-light-2 | memo/python-3.14/opt-2/pycdc | invalid_output | False | N/A | N/A | N/A | False |
| memo | memo/obfuscated-structural-0 | memo/python-3.14/opt-2/pycdc | invalid_output | False | N/A | N/A | N/A | False |
| memo | memo/obfuscated-structural-1 | memo/python-3.14/opt-2/pycdc | invalid_output | False | N/A | N/A | N/A | False |
| memo | memo/obfuscated-structural-2 | memo/python-3.14/opt-2/pycdc | invalid_output | False | N/A | N/A | N/A | False |
| memo | memo/obfuscated-light-0 | memo/python-3.4/opt-0/uncompyle6 | success | True | 100.00 | 100.00 | 100.00 | True |
| memo | memo/obfuscated-light-1 | memo/python-3.4/opt-0/uncompyle6 | success | True | 100.00 | 100.00 | 100.00 | True |
| memo | memo/obfuscated-light-2 | memo/python-3.4/opt-0/uncompyle6 | success | True | 100.00 | 100.00 | 100.00 | True |
| memo | memo/obfuscated-structural-0 | memo/python-3.4/opt-0/uncompyle6 | success | True | 80.35 | 98.37 | 99.25 | False |
| memo | memo/obfuscated-structural-1 | memo/python-3.4/opt-0/uncompyle6 | success | True | 80.35 | 98.37 | 99.25 | False |
| memo | memo/obfuscated-structural-2 | memo/python-3.4/opt-0/uncompyle6 | success | True | 80.35 | 98.37 | 99.25 | False |
| memo | memo/obfuscated-light-0 | memo/python-3.4/opt-0/pycdc | invalid_output | False | 14.16 | 33.55 | 1.12 | False |
| memo | memo/obfuscated-light-1 | memo/python-3.4/opt-0/pycdc | invalid_output | False | 14.16 | 33.55 | 1.12 | False |
| memo | memo/obfuscated-light-2 | memo/python-3.4/opt-0/pycdc | invalid_output | False | 14.16 | 33.55 | 1.12 | False |
| memo | memo/obfuscated-structural-0 | memo/python-3.4/opt-0/pycdc | invalid_output | False | 5.50 | 35.53 | 1.13 | False |
| memo | memo/obfuscated-structural-1 | memo/python-3.4/opt-0/pycdc | invalid_output | False | 5.50 | 35.53 | 1.13 | False |
| memo | memo/obfuscated-structural-2 | memo/python-3.4/opt-0/pycdc | invalid_output | False | 5.50 | 35.53 | 1.13 | False |
| memo | memo/obfuscated-light-0 | memo/python-3.4/opt-1/uncompyle6 | success | True | 100.00 | 100.00 | 100.00 | True |
| memo | memo/obfuscated-light-1 | memo/python-3.4/opt-1/uncompyle6 | success | True | 100.00 | 100.00 | 100.00 | True |
| memo | memo/obfuscated-light-2 | memo/python-3.4/opt-1/uncompyle6 | success | True | 100.00 | 100.00 | 100.00 | True |
| memo | memo/obfuscated-structural-0 | memo/python-3.4/opt-1/uncompyle6 | success | True | 80.35 | 98.37 | 99.25 | False |
| memo | memo/obfuscated-structural-1 | memo/python-3.4/opt-1/uncompyle6 | success | True | 80.35 | 98.37 | 99.25 | False |
| memo | memo/obfuscated-structural-2 | memo/python-3.4/opt-1/uncompyle6 | success | True | 80.35 | 98.37 | 99.25 | False |
| memo | memo/obfuscated-light-0 | memo/python-3.4/opt-1/pycdc | invalid_output | False | 14.16 | 33.55 | 1.12 | False |
| memo | memo/obfuscated-light-1 | memo/python-3.4/opt-1/pycdc | invalid_output | False | 14.16 | 33.55 | 1.12 | False |
| memo | memo/obfuscated-light-2 | memo/python-3.4/opt-1/pycdc | invalid_output | False | 14.16 | 33.55 | 1.12 | False |
| memo | memo/obfuscated-structural-0 | memo/python-3.4/opt-1/pycdc | invalid_output | False | 5.50 | 35.53 | 1.13 | False |
| memo | memo/obfuscated-structural-1 | memo/python-3.4/opt-1/pycdc | invalid_output | False | 5.50 | 35.53 | 1.13 | False |
| memo | memo/obfuscated-structural-2 | memo/python-3.4/opt-1/pycdc | invalid_output | False | 5.50 | 35.53 | 1.13 | False |
| memo | memo/obfuscated-light-0 | memo/python-3.4/opt-2/uncompyle6 | success | True | 100.00 | 100.00 | 100.00 | True |
| memo | memo/obfuscated-light-1 | memo/python-3.4/opt-2/uncompyle6 | success | True | 100.00 | 100.00 | 100.00 | True |
| memo | memo/obfuscated-light-2 | memo/python-3.4/opt-2/uncompyle6 | success | True | 100.00 | 100.00 | 100.00 | True |
| memo | memo/obfuscated-structural-0 | memo/python-3.4/opt-2/uncompyle6 | success | True | 80.35 | 98.37 | 99.25 | False |
| memo | memo/obfuscated-structural-1 | memo/python-3.4/opt-2/uncompyle6 | success | True | 80.35 | 98.37 | 99.25 | False |
| memo | memo/obfuscated-structural-2 | memo/python-3.4/opt-2/uncompyle6 | success | True | 80.35 | 98.37 | 99.25 | False |
| memo | memo/obfuscated-light-0 | memo/python-3.4/opt-2/pycdc | invalid_output | False | 14.16 | 33.55 | 1.12 | False |
| memo | memo/obfuscated-light-1 | memo/python-3.4/opt-2/pycdc | invalid_output | False | 14.16 | 33.55 | 1.12 | False |
| memo | memo/obfuscated-light-2 | memo/python-3.4/opt-2/pycdc | invalid_output | False | 14.16 | 33.55 | 1.12 | False |
| memo | memo/obfuscated-structural-0 | memo/python-3.4/opt-2/pycdc | invalid_output | False | 5.50 | 35.53 | 1.13 | False |
| memo | memo/obfuscated-structural-1 | memo/python-3.4/opt-2/pycdc | invalid_output | False | 5.50 | 35.53 | 1.13 | False |
| memo | memo/obfuscated-structural-2 | memo/python-3.4/opt-2/pycdc | invalid_output | False | 5.50 | 35.53 | 1.13 | False |
| memo | memo/obfuscated-light-0 | memo/python-3.8/opt-0/uncompyle6 | success | True | 100.00 | 100.00 | 100.00 | True |
| memo | memo/obfuscated-light-1 | memo/python-3.8/opt-0/uncompyle6 | success | True | 100.00 | 100.00 | 100.00 | True |
| memo | memo/obfuscated-light-2 | memo/python-3.8/opt-0/uncompyle6 | success | True | 100.00 | 100.00 | 100.00 | True |
| memo | memo/obfuscated-structural-0 | memo/python-3.8/opt-0/uncompyle6 | success | True | 80.35 | 98.37 | 99.25 | False |
| memo | memo/obfuscated-structural-1 | memo/python-3.8/opt-0/uncompyle6 | success | True | 80.35 | 98.37 | 99.25 | False |
| memo | memo/obfuscated-structural-2 | memo/python-3.8/opt-0/uncompyle6 | success | True | 80.35 | 98.37 | 99.25 | False |
| memo | memo/obfuscated-light-0 | memo/python-3.8/opt-0/pycdc | invalid_output | False | 14.23 | 33.35 | 1.12 | False |
| memo | memo/obfuscated-light-1 | memo/python-3.8/opt-0/pycdc | invalid_output | False | 14.23 | 33.35 | 1.12 | False |
| memo | memo/obfuscated-light-2 | memo/python-3.8/opt-0/pycdc | invalid_output | False | 14.23 | 33.35 | 1.12 | False |
| memo | memo/obfuscated-structural-0 | memo/python-3.8/opt-0/pycdc | invalid_output | False | 5.67 | 35.38 | 1.13 | False |
| memo | memo/obfuscated-structural-1 | memo/python-3.8/opt-0/pycdc | invalid_output | False | 5.67 | 35.38 | 1.13 | False |
| memo | memo/obfuscated-structural-2 | memo/python-3.8/opt-0/pycdc | invalid_output | False | 5.67 | 35.38 | 1.13 | False |
| memo | memo/obfuscated-light-0 | memo/python-3.8/opt-1/uncompyle6 | success | True | 100.00 | 100.00 | 100.00 | True |
| memo | memo/obfuscated-light-1 | memo/python-3.8/opt-1/uncompyle6 | success | True | 100.00 | 100.00 | 100.00 | True |
| memo | memo/obfuscated-light-2 | memo/python-3.8/opt-1/uncompyle6 | success | True | 100.00 | 100.00 | 100.00 | True |
| memo | memo/obfuscated-structural-0 | memo/python-3.8/opt-1/uncompyle6 | success | True | 80.35 | 98.37 | 99.25 | False |
| memo | memo/obfuscated-structural-1 | memo/python-3.8/opt-1/uncompyle6 | success | True | 80.35 | 98.37 | 99.25 | False |
| memo | memo/obfuscated-structural-2 | memo/python-3.8/opt-1/uncompyle6 | success | True | 80.35 | 98.37 | 99.25 | False |
| memo | memo/obfuscated-light-0 | memo/python-3.8/opt-1/pycdc | invalid_output | False | 14.23 | 33.35 | 1.12 | False |
| memo | memo/obfuscated-light-1 | memo/python-3.8/opt-1/pycdc | invalid_output | False | 14.23 | 33.35 | 1.12 | False |
| memo | memo/obfuscated-light-2 | memo/python-3.8/opt-1/pycdc | invalid_output | False | 14.23 | 33.35 | 1.12 | False |
| memo | memo/obfuscated-structural-0 | memo/python-3.8/opt-1/pycdc | invalid_output | False | 5.67 | 35.38 | 1.13 | False |
| memo | memo/obfuscated-structural-1 | memo/python-3.8/opt-1/pycdc | invalid_output | False | 5.67 | 35.38 | 1.13 | False |
| memo | memo/obfuscated-structural-2 | memo/python-3.8/opt-1/pycdc | invalid_output | False | 5.67 | 35.38 | 1.13 | False |
| memo | memo/obfuscated-light-0 | memo/python-3.8/opt-2/uncompyle6 | success | True | 100.00 | 100.00 | 100.00 | True |
| memo | memo/obfuscated-light-1 | memo/python-3.8/opt-2/uncompyle6 | success | True | 100.00 | 100.00 | 100.00 | True |
| memo | memo/obfuscated-light-2 | memo/python-3.8/opt-2/uncompyle6 | success | True | 100.00 | 100.00 | 100.00 | True |
| memo | memo/obfuscated-structural-0 | memo/python-3.8/opt-2/uncompyle6 | success | True | 80.35 | 98.37 | 99.25 | False |
| memo | memo/obfuscated-structural-1 | memo/python-3.8/opt-2/uncompyle6 | success | True | 80.35 | 98.37 | 99.25 | False |
| memo | memo/obfuscated-structural-2 | memo/python-3.8/opt-2/uncompyle6 | success | True | 80.35 | 98.37 | 99.25 | False |
| memo | memo/obfuscated-light-0 | memo/python-3.8/opt-2/pycdc | invalid_output | False | 14.23 | 33.35 | 1.12 | False |
| memo | memo/obfuscated-light-1 | memo/python-3.8/opt-2/pycdc | invalid_output | False | 14.23 | 33.35 | 1.12 | False |
| memo | memo/obfuscated-light-2 | memo/python-3.8/opt-2/pycdc | invalid_output | False | 14.23 | 33.35 | 1.12 | False |
| memo | memo/obfuscated-structural-0 | memo/python-3.8/opt-2/pycdc | invalid_output | False | 5.67 | 35.38 | 1.13 | False |
| memo | memo/obfuscated-structural-1 | memo/python-3.8/opt-2/pycdc | invalid_output | False | 5.67 | 35.38 | 1.13 | False |
| memo | memo/obfuscated-structural-2 | memo/python-3.8/opt-2/pycdc | invalid_output | False | 5.67 | 35.38 | 1.13 | False |
| transaction | transaction/obfuscated-light-0 | transaction/python-3.12/opt-0/uncompyle6 | unsupported | False | 24.26 | 33.24 | 0.00 | False |
| transaction | transaction/obfuscated-light-1 | transaction/python-3.12/opt-0/uncompyle6 | unsupported | False | 24.26 | 33.24 | 0.00 | False |
| transaction | transaction/obfuscated-light-2 | transaction/python-3.12/opt-0/uncompyle6 | unsupported | False | 24.26 | 33.24 | 0.00 | False |
| transaction | transaction/obfuscated-structural-0 | transaction/python-3.12/opt-0/uncompyle6 | unsupported | False | 23.46 | 35.90 | 0.30 | False |
| transaction | transaction/obfuscated-structural-1 | transaction/python-3.12/opt-0/uncompyle6 | unsupported | False | 23.46 | 35.90 | 0.30 | False |
| transaction | transaction/obfuscated-structural-2 | transaction/python-3.12/opt-0/uncompyle6 | unsupported | False | 23.46 | 35.90 | 0.30 | False |
| transaction | transaction/obfuscated-light-0 | transaction/python-3.12/opt-0/pycdc | unsupported | False | 94.27 | 98.36 | 98.89 | False |
| transaction | transaction/obfuscated-light-1 | transaction/python-3.12/opt-0/pycdc | unsupported | False | 94.27 | 98.36 | 98.89 | False |
| transaction | transaction/obfuscated-light-2 | transaction/python-3.12/opt-0/pycdc | unsupported | False | 94.27 | 98.36 | 98.89 | False |
| transaction | transaction/obfuscated-structural-0 | transaction/python-3.12/opt-0/pycdc | unsupported | False | 85.58 | 97.58 | 98.29 | False |
| transaction | transaction/obfuscated-structural-1 | transaction/python-3.12/opt-0/pycdc | unsupported | False | 85.58 | 97.58 | 98.29 | False |
| transaction | transaction/obfuscated-structural-2 | transaction/python-3.12/opt-0/pycdc | unsupported | False | 85.58 | 97.58 | 98.29 | False |
| transaction | transaction/obfuscated-light-0 | transaction/python-3.12/opt-1/uncompyle6 | unsupported | False | 24.26 | 33.24 | 0.00 | False |
| transaction | transaction/obfuscated-light-1 | transaction/python-3.12/opt-1/uncompyle6 | unsupported | False | 24.26 | 33.24 | 0.00 | False |
| transaction | transaction/obfuscated-light-2 | transaction/python-3.12/opt-1/uncompyle6 | unsupported | False | 24.26 | 33.24 | 0.00 | False |
| transaction | transaction/obfuscated-structural-0 | transaction/python-3.12/opt-1/uncompyle6 | unsupported | False | 23.46 | 35.90 | 0.30 | False |
| transaction | transaction/obfuscated-structural-1 | transaction/python-3.12/opt-1/uncompyle6 | unsupported | False | 23.46 | 35.90 | 0.30 | False |
| transaction | transaction/obfuscated-structural-2 | transaction/python-3.12/opt-1/uncompyle6 | unsupported | False | 23.46 | 35.90 | 0.30 | False |
| transaction | transaction/obfuscated-light-0 | transaction/python-3.12/opt-1/pycdc | unsupported | False | 94.27 | 98.36 | 98.89 | False |
| transaction | transaction/obfuscated-light-1 | transaction/python-3.12/opt-1/pycdc | unsupported | False | 94.27 | 98.36 | 98.89 | False |
| transaction | transaction/obfuscated-light-2 | transaction/python-3.12/opt-1/pycdc | unsupported | False | 94.27 | 98.36 | 98.89 | False |
| transaction | transaction/obfuscated-structural-0 | transaction/python-3.12/opt-1/pycdc | unsupported | False | 85.58 | 97.58 | 98.29 | False |
| transaction | transaction/obfuscated-structural-1 | transaction/python-3.12/opt-1/pycdc | unsupported | False | 85.58 | 97.58 | 98.29 | False |
| transaction | transaction/obfuscated-structural-2 | transaction/python-3.12/opt-1/pycdc | unsupported | False | 85.58 | 97.58 | 98.29 | False |
| transaction | transaction/obfuscated-light-0 | transaction/python-3.12/opt-2/uncompyle6 | unsupported | False | 24.26 | 33.24 | 0.00 | False |
| transaction | transaction/obfuscated-light-1 | transaction/python-3.12/opt-2/uncompyle6 | unsupported | False | 24.26 | 33.24 | 0.00 | False |
| transaction | transaction/obfuscated-light-2 | transaction/python-3.12/opt-2/uncompyle6 | unsupported | False | 24.26 | 33.24 | 0.00 | False |
| transaction | transaction/obfuscated-structural-0 | transaction/python-3.12/opt-2/uncompyle6 | unsupported | False | 23.46 | 35.90 | 0.30 | False |
| transaction | transaction/obfuscated-structural-1 | transaction/python-3.12/opt-2/uncompyle6 | unsupported | False | 23.46 | 35.90 | 0.30 | False |
| transaction | transaction/obfuscated-structural-2 | transaction/python-3.12/opt-2/uncompyle6 | unsupported | False | 23.46 | 35.90 | 0.30 | False |
| transaction | transaction/obfuscated-light-0 | transaction/python-3.12/opt-2/pycdc | unsupported | False | 94.27 | 98.36 | 98.89 | False |
| transaction | transaction/obfuscated-light-1 | transaction/python-3.12/opt-2/pycdc | unsupported | False | 94.27 | 98.36 | 98.89 | False |
| transaction | transaction/obfuscated-light-2 | transaction/python-3.12/opt-2/pycdc | unsupported | False | 94.27 | 98.36 | 98.89 | False |
| transaction | transaction/obfuscated-structural-0 | transaction/python-3.12/opt-2/pycdc | unsupported | False | 85.58 | 97.58 | 98.29 | False |
| transaction | transaction/obfuscated-structural-1 | transaction/python-3.12/opt-2/pycdc | unsupported | False | 85.58 | 97.58 | 98.29 | False |
| transaction | transaction/obfuscated-structural-2 | transaction/python-3.12/opt-2/pycdc | unsupported | False | 85.58 | 97.58 | 98.29 | False |
| transaction | transaction/obfuscated-light-0 | transaction/python-3.14/opt-0/uncompyle6 | invalid_output | False | N/A | N/A | N/A | False |
| transaction | transaction/obfuscated-light-1 | transaction/python-3.14/opt-0/uncompyle6 | invalid_output | False | N/A | N/A | N/A | False |
| transaction | transaction/obfuscated-light-2 | transaction/python-3.14/opt-0/uncompyle6 | invalid_output | False | N/A | N/A | N/A | False |
| transaction | transaction/obfuscated-structural-0 | transaction/python-3.14/opt-0/uncompyle6 | invalid_output | False | N/A | N/A | N/A | False |
| transaction | transaction/obfuscated-structural-1 | transaction/python-3.14/opt-0/uncompyle6 | invalid_output | False | N/A | N/A | N/A | False |
| transaction | transaction/obfuscated-structural-2 | transaction/python-3.14/opt-0/uncompyle6 | invalid_output | False | N/A | N/A | N/A | False |
| transaction | transaction/obfuscated-light-0 | transaction/python-3.14/opt-0/pycdc | invalid_output | False | N/A | N/A | N/A | False |
| transaction | transaction/obfuscated-light-1 | transaction/python-3.14/opt-0/pycdc | invalid_output | False | N/A | N/A | N/A | False |
| transaction | transaction/obfuscated-light-2 | transaction/python-3.14/opt-0/pycdc | invalid_output | False | N/A | N/A | N/A | False |
| transaction | transaction/obfuscated-structural-0 | transaction/python-3.14/opt-0/pycdc | invalid_output | False | N/A | N/A | N/A | False |
| transaction | transaction/obfuscated-structural-1 | transaction/python-3.14/opt-0/pycdc | invalid_output | False | N/A | N/A | N/A | False |
| transaction | transaction/obfuscated-structural-2 | transaction/python-3.14/opt-0/pycdc | invalid_output | False | N/A | N/A | N/A | False |
| transaction | transaction/obfuscated-light-0 | transaction/python-3.14/opt-1/uncompyle6 | invalid_output | False | N/A | N/A | N/A | False |
| transaction | transaction/obfuscated-light-1 | transaction/python-3.14/opt-1/uncompyle6 | invalid_output | False | N/A | N/A | N/A | False |
| transaction | transaction/obfuscated-light-2 | transaction/python-3.14/opt-1/uncompyle6 | invalid_output | False | N/A | N/A | N/A | False |
| transaction | transaction/obfuscated-structural-0 | transaction/python-3.14/opt-1/uncompyle6 | invalid_output | False | N/A | N/A | N/A | False |
| transaction | transaction/obfuscated-structural-1 | transaction/python-3.14/opt-1/uncompyle6 | invalid_output | False | N/A | N/A | N/A | False |
| transaction | transaction/obfuscated-structural-2 | transaction/python-3.14/opt-1/uncompyle6 | invalid_output | False | N/A | N/A | N/A | False |
| transaction | transaction/obfuscated-light-0 | transaction/python-3.14/opt-1/pycdc | invalid_output | False | N/A | N/A | N/A | False |
| transaction | transaction/obfuscated-light-1 | transaction/python-3.14/opt-1/pycdc | invalid_output | False | N/A | N/A | N/A | False |
| transaction | transaction/obfuscated-light-2 | transaction/python-3.14/opt-1/pycdc | invalid_output | False | N/A | N/A | N/A | False |
| transaction | transaction/obfuscated-structural-0 | transaction/python-3.14/opt-1/pycdc | invalid_output | False | N/A | N/A | N/A | False |
| transaction | transaction/obfuscated-structural-1 | transaction/python-3.14/opt-1/pycdc | invalid_output | False | N/A | N/A | N/A | False |
| transaction | transaction/obfuscated-structural-2 | transaction/python-3.14/opt-1/pycdc | invalid_output | False | N/A | N/A | N/A | False |
| transaction | transaction/obfuscated-light-0 | transaction/python-3.14/opt-2/uncompyle6 | invalid_output | False | N/A | N/A | N/A | False |
| transaction | transaction/obfuscated-light-1 | transaction/python-3.14/opt-2/uncompyle6 | invalid_output | False | N/A | N/A | N/A | False |
| transaction | transaction/obfuscated-light-2 | transaction/python-3.14/opt-2/uncompyle6 | invalid_output | False | N/A | N/A | N/A | False |
| transaction | transaction/obfuscated-structural-0 | transaction/python-3.14/opt-2/uncompyle6 | invalid_output | False | N/A | N/A | N/A | False |
| transaction | transaction/obfuscated-structural-1 | transaction/python-3.14/opt-2/uncompyle6 | invalid_output | False | N/A | N/A | N/A | False |
| transaction | transaction/obfuscated-structural-2 | transaction/python-3.14/opt-2/uncompyle6 | invalid_output | False | N/A | N/A | N/A | False |
| transaction | transaction/obfuscated-light-0 | transaction/python-3.14/opt-2/pycdc | invalid_output | False | N/A | N/A | N/A | False |
| transaction | transaction/obfuscated-light-1 | transaction/python-3.14/opt-2/pycdc | invalid_output | False | N/A | N/A | N/A | False |
| transaction | transaction/obfuscated-light-2 | transaction/python-3.14/opt-2/pycdc | invalid_output | False | N/A | N/A | N/A | False |
| transaction | transaction/obfuscated-structural-0 | transaction/python-3.14/opt-2/pycdc | invalid_output | False | N/A | N/A | N/A | False |
| transaction | transaction/obfuscated-structural-1 | transaction/python-3.14/opt-2/pycdc | invalid_output | False | N/A | N/A | N/A | False |
| transaction | transaction/obfuscated-structural-2 | transaction/python-3.14/opt-2/pycdc | invalid_output | False | N/A | N/A | N/A | False |
| transaction | transaction/obfuscated-light-0 | transaction/python-3.4/opt-0/uncompyle6 | success | True | 100.00 | 100.00 | 100.00 | True |
| transaction | transaction/obfuscated-light-1 | transaction/python-3.4/opt-0/uncompyle6 | success | True | 100.00 | 100.00 | 100.00 | True |
| transaction | transaction/obfuscated-light-2 | transaction/python-3.4/opt-0/uncompyle6 | success | True | 100.00 | 100.00 | 100.00 | True |
| transaction | transaction/obfuscated-structural-0 | transaction/python-3.4/opt-0/uncompyle6 | success | True | 90.57 | 98.76 | 99.21 | False |
| transaction | transaction/obfuscated-structural-1 | transaction/python-3.4/opt-0/uncompyle6 | success | True | 90.57 | 98.76 | 99.21 | False |
| transaction | transaction/obfuscated-structural-2 | transaction/python-3.4/opt-0/uncompyle6 | success | True | 90.57 | 98.76 | 99.21 | False |
| transaction | transaction/obfuscated-light-0 | transaction/python-3.4/opt-0/pycdc | invalid_output | False | 27.02 | 39.09 | 0.00 | False |
| transaction | transaction/obfuscated-light-1 | transaction/python-3.4/opt-0/pycdc | invalid_output | False | 27.02 | 39.09 | 0.00 | False |
| transaction | transaction/obfuscated-light-2 | transaction/python-3.4/opt-0/pycdc | invalid_output | False | 27.02 | 39.09 | 0.00 | False |
| transaction | transaction/obfuscated-structural-0 | transaction/python-3.4/opt-0/pycdc | invalid_output | False | 21.20 | 39.38 | 0.30 | False |
| transaction | transaction/obfuscated-structural-1 | transaction/python-3.4/opt-0/pycdc | invalid_output | False | 21.20 | 39.38 | 0.30 | False |
| transaction | transaction/obfuscated-structural-2 | transaction/python-3.4/opt-0/pycdc | invalid_output | False | 21.20 | 39.38 | 0.30 | False |
| transaction | transaction/obfuscated-light-0 | transaction/python-3.4/opt-1/uncompyle6 | success | True | 100.00 | 100.00 | 100.00 | True |
| transaction | transaction/obfuscated-light-1 | transaction/python-3.4/opt-1/uncompyle6 | success | True | 100.00 | 100.00 | 100.00 | True |
| transaction | transaction/obfuscated-light-2 | transaction/python-3.4/opt-1/uncompyle6 | success | True | 100.00 | 100.00 | 100.00 | True |
| transaction | transaction/obfuscated-structural-0 | transaction/python-3.4/opt-1/uncompyle6 | success | True | 90.57 | 98.76 | 99.21 | False |
| transaction | transaction/obfuscated-structural-1 | transaction/python-3.4/opt-1/uncompyle6 | success | True | 90.57 | 98.76 | 99.21 | False |
| transaction | transaction/obfuscated-structural-2 | transaction/python-3.4/opt-1/uncompyle6 | success | True | 90.57 | 98.76 | 99.21 | False |
| transaction | transaction/obfuscated-light-0 | transaction/python-3.4/opt-1/pycdc | invalid_output | False | 27.02 | 39.09 | 0.00 | False |
| transaction | transaction/obfuscated-light-1 | transaction/python-3.4/opt-1/pycdc | invalid_output | False | 27.02 | 39.09 | 0.00 | False |
| transaction | transaction/obfuscated-light-2 | transaction/python-3.4/opt-1/pycdc | invalid_output | False | 27.02 | 39.09 | 0.00 | False |
| transaction | transaction/obfuscated-structural-0 | transaction/python-3.4/opt-1/pycdc | invalid_output | False | 21.20 | 39.38 | 0.30 | False |
| transaction | transaction/obfuscated-structural-1 | transaction/python-3.4/opt-1/pycdc | invalid_output | False | 21.20 | 39.38 | 0.30 | False |
| transaction | transaction/obfuscated-structural-2 | transaction/python-3.4/opt-1/pycdc | invalid_output | False | 21.20 | 39.38 | 0.30 | False |
| transaction | transaction/obfuscated-light-0 | transaction/python-3.4/opt-2/uncompyle6 | success | True | 100.00 | 100.00 | 100.00 | True |
| transaction | transaction/obfuscated-light-1 | transaction/python-3.4/opt-2/uncompyle6 | success | True | 100.00 | 100.00 | 100.00 | True |
| transaction | transaction/obfuscated-light-2 | transaction/python-3.4/opt-2/uncompyle6 | success | True | 100.00 | 100.00 | 100.00 | True |
| transaction | transaction/obfuscated-structural-0 | transaction/python-3.4/opt-2/uncompyle6 | success | True | 90.57 | 98.76 | 99.21 | False |
| transaction | transaction/obfuscated-structural-1 | transaction/python-3.4/opt-2/uncompyle6 | success | True | 90.57 | 98.76 | 99.21 | False |
| transaction | transaction/obfuscated-structural-2 | transaction/python-3.4/opt-2/uncompyle6 | success | True | 90.57 | 98.76 | 99.21 | False |
| transaction | transaction/obfuscated-light-0 | transaction/python-3.4/opt-2/pycdc | invalid_output | False | 27.02 | 39.09 | 0.00 | False |
| transaction | transaction/obfuscated-light-1 | transaction/python-3.4/opt-2/pycdc | invalid_output | False | 27.02 | 39.09 | 0.00 | False |
| transaction | transaction/obfuscated-light-2 | transaction/python-3.4/opt-2/pycdc | invalid_output | False | 27.02 | 39.09 | 0.00 | False |
| transaction | transaction/obfuscated-structural-0 | transaction/python-3.4/opt-2/pycdc | invalid_output | False | 21.20 | 39.38 | 0.30 | False |
| transaction | transaction/obfuscated-structural-1 | transaction/python-3.4/opt-2/pycdc | invalid_output | False | 21.20 | 39.38 | 0.30 | False |
| transaction | transaction/obfuscated-structural-2 | transaction/python-3.4/opt-2/pycdc | invalid_output | False | 21.20 | 39.38 | 0.30 | False |
| transaction | transaction/obfuscated-light-0 | transaction/python-3.8/opt-0/uncompyle6 | behavior_mismatch | False | 99.19 | 99.97 | 99.97 | False |
| transaction | transaction/obfuscated-light-1 | transaction/python-3.8/opt-0/uncompyle6 | behavior_mismatch | False | 99.19 | 99.97 | 99.97 | False |
| transaction | transaction/obfuscated-light-2 | transaction/python-3.8/opt-0/uncompyle6 | behavior_mismatch | False | 99.19 | 99.97 | 99.97 | False |
| transaction | transaction/obfuscated-structural-0 | transaction/python-3.8/opt-0/uncompyle6 | behavior_mismatch | False | 89.19 | 98.58 | 99.24 | False |
| transaction | transaction/obfuscated-structural-1 | transaction/python-3.8/opt-0/uncompyle6 | behavior_mismatch | False | 89.19 | 98.58 | 99.24 | False |
| transaction | transaction/obfuscated-structural-2 | transaction/python-3.8/opt-0/uncompyle6 | behavior_mismatch | False | 89.19 | 98.58 | 99.24 | False |
| transaction | transaction/obfuscated-light-0 | transaction/python-3.8/opt-0/pycdc | unsupported | False | 96.00 | 99.73 | 99.88 | False |
| transaction | transaction/obfuscated-light-1 | transaction/python-3.8/opt-0/pycdc | unsupported | False | 96.00 | 99.73 | 99.88 | False |
| transaction | transaction/obfuscated-light-2 | transaction/python-3.8/opt-0/pycdc | unsupported | False | 96.00 | 99.73 | 99.88 | False |
| transaction | transaction/obfuscated-structural-0 | transaction/python-3.8/opt-0/pycdc | unsupported | False | 90.21 | 98.79 | 99.07 | False |
| transaction | transaction/obfuscated-structural-1 | transaction/python-3.8/opt-0/pycdc | unsupported | False | 90.21 | 98.79 | 99.07 | False |
| transaction | transaction/obfuscated-structural-2 | transaction/python-3.8/opt-0/pycdc | unsupported | False | 90.21 | 98.79 | 99.07 | False |
| transaction | transaction/obfuscated-light-0 | transaction/python-3.8/opt-1/uncompyle6 | behavior_mismatch | False | 99.19 | 99.97 | 99.97 | False |
| transaction | transaction/obfuscated-light-1 | transaction/python-3.8/opt-1/uncompyle6 | behavior_mismatch | False | 99.19 | 99.97 | 99.97 | False |
| transaction | transaction/obfuscated-light-2 | transaction/python-3.8/opt-1/uncompyle6 | behavior_mismatch | False | 99.19 | 99.97 | 99.97 | False |
| transaction | transaction/obfuscated-structural-0 | transaction/python-3.8/opt-1/uncompyle6 | behavior_mismatch | False | 89.19 | 98.58 | 99.24 | False |
| transaction | transaction/obfuscated-structural-1 | transaction/python-3.8/opt-1/uncompyle6 | behavior_mismatch | False | 89.19 | 98.58 | 99.24 | False |
| transaction | transaction/obfuscated-structural-2 | transaction/python-3.8/opt-1/uncompyle6 | behavior_mismatch | False | 89.19 | 98.58 | 99.24 | False |
| transaction | transaction/obfuscated-light-0 | transaction/python-3.8/opt-1/pycdc | unsupported | False | 96.00 | 99.73 | 99.88 | False |
| transaction | transaction/obfuscated-light-1 | transaction/python-3.8/opt-1/pycdc | unsupported | False | 96.00 | 99.73 | 99.88 | False |
| transaction | transaction/obfuscated-light-2 | transaction/python-3.8/opt-1/pycdc | unsupported | False | 96.00 | 99.73 | 99.88 | False |
| transaction | transaction/obfuscated-structural-0 | transaction/python-3.8/opt-1/pycdc | unsupported | False | 90.21 | 98.79 | 99.07 | False |
| transaction | transaction/obfuscated-structural-1 | transaction/python-3.8/opt-1/pycdc | unsupported | False | 90.21 | 98.79 | 99.07 | False |
| transaction | transaction/obfuscated-structural-2 | transaction/python-3.8/opt-1/pycdc | unsupported | False | 90.21 | 98.79 | 99.07 | False |
| transaction | transaction/obfuscated-light-0 | transaction/python-3.8/opt-2/uncompyle6 | behavior_mismatch | False | 99.19 | 99.97 | 99.97 | False |
| transaction | transaction/obfuscated-light-1 | transaction/python-3.8/opt-2/uncompyle6 | behavior_mismatch | False | 99.19 | 99.97 | 99.97 | False |
| transaction | transaction/obfuscated-light-2 | transaction/python-3.8/opt-2/uncompyle6 | behavior_mismatch | False | 99.19 | 99.97 | 99.97 | False |
| transaction | transaction/obfuscated-structural-0 | transaction/python-3.8/opt-2/uncompyle6 | behavior_mismatch | False | 89.19 | 98.58 | 99.24 | False |
| transaction | transaction/obfuscated-structural-1 | transaction/python-3.8/opt-2/uncompyle6 | behavior_mismatch | False | 89.19 | 98.58 | 99.24 | False |
| transaction | transaction/obfuscated-structural-2 | transaction/python-3.8/opt-2/uncompyle6 | behavior_mismatch | False | 89.19 | 98.58 | 99.24 | False |
| transaction | transaction/obfuscated-light-0 | transaction/python-3.8/opt-2/pycdc | unsupported | False | 96.00 | 99.73 | 99.88 | False |
| transaction | transaction/obfuscated-light-1 | transaction/python-3.8/opt-2/pycdc | unsupported | False | 96.00 | 99.73 | 99.88 | False |
| transaction | transaction/obfuscated-light-2 | transaction/python-3.8/opt-2/pycdc | unsupported | False | 96.00 | 99.73 | 99.88 | False |
| transaction | transaction/obfuscated-structural-0 | transaction/python-3.8/opt-2/pycdc | unsupported | False | 90.21 | 98.79 | 99.07 | False |
| transaction | transaction/obfuscated-structural-1 | transaction/python-3.8/opt-2/pycdc | unsupported | False | 90.21 | 98.79 | 99.07 | False |
| transaction | transaction/obfuscated-structural-2 | transaction/python-3.8/opt-2/pycdc | unsupported | False | 90.21 | 98.79 | 99.07 | False |
| typed_router | typed_router/obfuscated-light-0 | typed_router/python-3.12/opt-0/uncompyle6 | unsupported | False | 22.30 | 20.48 | 0.44 | False |
| typed_router | typed_router/obfuscated-light-1 | typed_router/python-3.12/opt-0/uncompyle6 | unsupported | False | 22.30 | 20.48 | 0.44 | False |
| typed_router | typed_router/obfuscated-light-2 | typed_router/python-3.12/opt-0/uncompyle6 | unsupported | False | 22.30 | 20.48 | 0.44 | False |
| typed_router | typed_router/obfuscated-structural-0 | typed_router/python-3.12/opt-0/uncompyle6 | unsupported | False | 17.38 | 25.63 | 0.50 | False |
| typed_router | typed_router/obfuscated-structural-1 | typed_router/python-3.12/opt-0/uncompyle6 | unsupported | False | 17.38 | 25.63 | 0.50 | False |
| typed_router | typed_router/obfuscated-structural-2 | typed_router/python-3.12/opt-0/uncompyle6 | unsupported | False | 17.38 | 25.63 | 0.50 | False |
| typed_router | typed_router/obfuscated-light-0 | typed_router/python-3.12/opt-0/pycdc | unsupported | False | 24.83 | 26.56 | 0.45 | False |
| typed_router | typed_router/obfuscated-light-1 | typed_router/python-3.12/opt-0/pycdc | unsupported | False | 24.83 | 26.56 | 0.45 | False |
| typed_router | typed_router/obfuscated-light-2 | typed_router/python-3.12/opt-0/pycdc | unsupported | False | 24.83 | 26.56 | 0.45 | False |
| typed_router | typed_router/obfuscated-structural-0 | typed_router/python-3.12/opt-0/pycdc | unsupported | False | 14.96 | 29.78 | 0.50 | False |
| typed_router | typed_router/obfuscated-structural-1 | typed_router/python-3.12/opt-0/pycdc | unsupported | False | 14.96 | 29.78 | 0.50 | False |
| typed_router | typed_router/obfuscated-structural-2 | typed_router/python-3.12/opt-0/pycdc | unsupported | False | 14.96 | 29.78 | 0.50 | False |
| typed_router | typed_router/obfuscated-light-0 | typed_router/python-3.12/opt-1/uncompyle6 | unsupported | False | 22.30 | 20.48 | 0.44 | False |
| typed_router | typed_router/obfuscated-light-1 | typed_router/python-3.12/opt-1/uncompyle6 | unsupported | False | 22.30 | 20.48 | 0.44 | False |
| typed_router | typed_router/obfuscated-light-2 | typed_router/python-3.12/opt-1/uncompyle6 | unsupported | False | 22.30 | 20.48 | 0.44 | False |
| typed_router | typed_router/obfuscated-structural-0 | typed_router/python-3.12/opt-1/uncompyle6 | unsupported | False | 17.38 | 25.63 | 0.50 | False |
| typed_router | typed_router/obfuscated-structural-1 | typed_router/python-3.12/opt-1/uncompyle6 | unsupported | False | 17.38 | 25.63 | 0.50 | False |
| typed_router | typed_router/obfuscated-structural-2 | typed_router/python-3.12/opt-1/uncompyle6 | unsupported | False | 17.38 | 25.63 | 0.50 | False |
| typed_router | typed_router/obfuscated-light-0 | typed_router/python-3.12/opt-1/pycdc | unsupported | False | 24.83 | 26.56 | 0.45 | False |
| typed_router | typed_router/obfuscated-light-1 | typed_router/python-3.12/opt-1/pycdc | unsupported | False | 24.83 | 26.56 | 0.45 | False |
| typed_router | typed_router/obfuscated-light-2 | typed_router/python-3.12/opt-1/pycdc | unsupported | False | 24.83 | 26.56 | 0.45 | False |
| typed_router | typed_router/obfuscated-structural-0 | typed_router/python-3.12/opt-1/pycdc | unsupported | False | 14.96 | 29.78 | 0.50 | False |
| typed_router | typed_router/obfuscated-structural-1 | typed_router/python-3.12/opt-1/pycdc | unsupported | False | 14.96 | 29.78 | 0.50 | False |
| typed_router | typed_router/obfuscated-structural-2 | typed_router/python-3.12/opt-1/pycdc | unsupported | False | 14.96 | 29.78 | 0.50 | False |
| typed_router | typed_router/obfuscated-light-0 | typed_router/python-3.12/opt-2/uncompyle6 | unsupported | False | 22.30 | 20.48 | 0.44 | False |
| typed_router | typed_router/obfuscated-light-1 | typed_router/python-3.12/opt-2/uncompyle6 | unsupported | False | 22.30 | 20.48 | 0.44 | False |
| typed_router | typed_router/obfuscated-light-2 | typed_router/python-3.12/opt-2/uncompyle6 | unsupported | False | 22.30 | 20.48 | 0.44 | False |
| typed_router | typed_router/obfuscated-structural-0 | typed_router/python-3.12/opt-2/uncompyle6 | unsupported | False | 17.38 | 25.63 | 0.50 | False |
| typed_router | typed_router/obfuscated-structural-1 | typed_router/python-3.12/opt-2/uncompyle6 | unsupported | False | 17.38 | 25.63 | 0.50 | False |
| typed_router | typed_router/obfuscated-structural-2 | typed_router/python-3.12/opt-2/uncompyle6 | unsupported | False | 17.38 | 25.63 | 0.50 | False |
| typed_router | typed_router/obfuscated-light-0 | typed_router/python-3.12/opt-2/pycdc | unsupported | False | 24.83 | 26.56 | 0.45 | False |
| typed_router | typed_router/obfuscated-light-1 | typed_router/python-3.12/opt-2/pycdc | unsupported | False | 24.83 | 26.56 | 0.45 | False |
| typed_router | typed_router/obfuscated-light-2 | typed_router/python-3.12/opt-2/pycdc | unsupported | False | 24.83 | 26.56 | 0.45 | False |
| typed_router | typed_router/obfuscated-structural-0 | typed_router/python-3.12/opt-2/pycdc | unsupported | False | 14.96 | 29.78 | 0.50 | False |
| typed_router | typed_router/obfuscated-structural-1 | typed_router/python-3.12/opt-2/pycdc | unsupported | False | 14.96 | 29.78 | 0.50 | False |
| typed_router | typed_router/obfuscated-structural-2 | typed_router/python-3.12/opt-2/pycdc | unsupported | False | 14.96 | 29.78 | 0.50 | False |
| typed_router | typed_router/obfuscated-light-0 | typed_router/python-3.14/opt-0/uncompyle6 | unsupported | False | 18.89 | 22.00 | 0.44 | False |
| typed_router | typed_router/obfuscated-light-1 | typed_router/python-3.14/opt-0/uncompyle6 | unsupported | False | 18.89 | 22.00 | 0.44 | False |
| typed_router | typed_router/obfuscated-light-2 | typed_router/python-3.14/opt-0/uncompyle6 | unsupported | False | 18.89 | 22.00 | 0.44 | False |
| typed_router | typed_router/obfuscated-structural-0 | typed_router/python-3.14/opt-0/uncompyle6 | unsupported | False | 14.41 | 27.12 | 0.49 | False |
| typed_router | typed_router/obfuscated-structural-1 | typed_router/python-3.14/opt-0/uncompyle6 | unsupported | False | 14.41 | 27.12 | 0.49 | False |
| typed_router | typed_router/obfuscated-structural-2 | typed_router/python-3.14/opt-0/uncompyle6 | unsupported | False | 14.41 | 27.12 | 0.49 | False |
| typed_router | typed_router/obfuscated-light-0 | typed_router/python-3.14/opt-0/pycdc | invalid_output | False | N/A | N/A | N/A | False |
| typed_router | typed_router/obfuscated-light-1 | typed_router/python-3.14/opt-0/pycdc | invalid_output | False | N/A | N/A | N/A | False |
| typed_router | typed_router/obfuscated-light-2 | typed_router/python-3.14/opt-0/pycdc | invalid_output | False | N/A | N/A | N/A | False |
| typed_router | typed_router/obfuscated-structural-0 | typed_router/python-3.14/opt-0/pycdc | invalid_output | False | N/A | N/A | N/A | False |
| typed_router | typed_router/obfuscated-structural-1 | typed_router/python-3.14/opt-0/pycdc | invalid_output | False | N/A | N/A | N/A | False |
| typed_router | typed_router/obfuscated-structural-2 | typed_router/python-3.14/opt-0/pycdc | invalid_output | False | N/A | N/A | N/A | False |
| typed_router | typed_router/obfuscated-light-0 | typed_router/python-3.14/opt-1/uncompyle6 | unsupported | False | 18.89 | 22.00 | 0.44 | False |
| typed_router | typed_router/obfuscated-light-1 | typed_router/python-3.14/opt-1/uncompyle6 | unsupported | False | 18.89 | 22.00 | 0.44 | False |
| typed_router | typed_router/obfuscated-light-2 | typed_router/python-3.14/opt-1/uncompyle6 | unsupported | False | 18.89 | 22.00 | 0.44 | False |
| typed_router | typed_router/obfuscated-structural-0 | typed_router/python-3.14/opt-1/uncompyle6 | unsupported | False | 14.41 | 27.12 | 0.49 | False |
| typed_router | typed_router/obfuscated-structural-1 | typed_router/python-3.14/opt-1/uncompyle6 | unsupported | False | 14.41 | 27.12 | 0.49 | False |
| typed_router | typed_router/obfuscated-structural-2 | typed_router/python-3.14/opt-1/uncompyle6 | unsupported | False | 14.41 | 27.12 | 0.49 | False |
| typed_router | typed_router/obfuscated-light-0 | typed_router/python-3.14/opt-1/pycdc | invalid_output | False | N/A | N/A | N/A | False |
| typed_router | typed_router/obfuscated-light-1 | typed_router/python-3.14/opt-1/pycdc | invalid_output | False | N/A | N/A | N/A | False |
| typed_router | typed_router/obfuscated-light-2 | typed_router/python-3.14/opt-1/pycdc | invalid_output | False | N/A | N/A | N/A | False |
| typed_router | typed_router/obfuscated-structural-0 | typed_router/python-3.14/opt-1/pycdc | invalid_output | False | N/A | N/A | N/A | False |
| typed_router | typed_router/obfuscated-structural-1 | typed_router/python-3.14/opt-1/pycdc | invalid_output | False | N/A | N/A | N/A | False |
| typed_router | typed_router/obfuscated-structural-2 | typed_router/python-3.14/opt-1/pycdc | invalid_output | False | N/A | N/A | N/A | False |
| typed_router | typed_router/obfuscated-light-0 | typed_router/python-3.14/opt-2/uncompyle6 | unsupported | False | 18.89 | 22.00 | 0.44 | False |
| typed_router | typed_router/obfuscated-light-1 | typed_router/python-3.14/opt-2/uncompyle6 | unsupported | False | 18.89 | 22.00 | 0.44 | False |
| typed_router | typed_router/obfuscated-light-2 | typed_router/python-3.14/opt-2/uncompyle6 | unsupported | False | 18.89 | 22.00 | 0.44 | False |
| typed_router | typed_router/obfuscated-structural-0 | typed_router/python-3.14/opt-2/uncompyle6 | unsupported | False | 14.41 | 27.12 | 0.49 | False |
| typed_router | typed_router/obfuscated-structural-1 | typed_router/python-3.14/opt-2/uncompyle6 | unsupported | False | 14.41 | 27.12 | 0.49 | False |
| typed_router | typed_router/obfuscated-structural-2 | typed_router/python-3.14/opt-2/uncompyle6 | unsupported | False | 14.41 | 27.12 | 0.49 | False |
| typed_router | typed_router/obfuscated-light-0 | typed_router/python-3.14/opt-2/pycdc | invalid_output | False | N/A | N/A | N/A | False |
| typed_router | typed_router/obfuscated-light-1 | typed_router/python-3.14/opt-2/pycdc | invalid_output | False | N/A | N/A | N/A | False |
| typed_router | typed_router/obfuscated-light-2 | typed_router/python-3.14/opt-2/pycdc | invalid_output | False | N/A | N/A | N/A | False |
| typed_router | typed_router/obfuscated-structural-0 | typed_router/python-3.14/opt-2/pycdc | invalid_output | False | N/A | N/A | N/A | False |
| typed_router | typed_router/obfuscated-structural-1 | typed_router/python-3.14/opt-2/pycdc | invalid_output | False | N/A | N/A | N/A | False |
| typed_router | typed_router/obfuscated-structural-2 | typed_router/python-3.14/opt-2/pycdc | invalid_output | False | N/A | N/A | N/A | False |

## Retrieval ranks against ten originals

The extra hard-negative candidate is the query project's behavior-changing near-copy.

| Variant | Method | Original rank (ties conservative) | Rank with hard negative |
|---|---|---:|---:|
| invoice/original | trained | 1 | 1 |
| invoice/original | untrained | 1 | 1 |
| invoice/original | hashed_graph | 1 | 1 |
| invoice/obfuscated-light-0 | trained | 1 | 1 |
| invoice/obfuscated-light-0 | untrained | 1 | 1 |
| invoice/obfuscated-light-0 | hashed_graph | 1 | 1 |
| invoice/obfuscated-light-1 | trained | 1 | 1 |
| invoice/obfuscated-light-1 | untrained | 1 | 1 |
| invoice/obfuscated-light-1 | hashed_graph | 1 | 1 |
| invoice/obfuscated-light-2 | trained | 1 | 1 |
| invoice/obfuscated-light-2 | untrained | 1 | 1 |
| invoice/obfuscated-light-2 | hashed_graph | 1 | 1 |
| invoice/obfuscated-structural-0 | trained | 2 | 2 |
| invoice/obfuscated-structural-0 | untrained | 4 | 4 |
| invoice/obfuscated-structural-0 | hashed_graph | 2 | 3 |
| invoice/obfuscated-structural-1 | trained | 2 | 2 |
| invoice/obfuscated-structural-1 | untrained | 4 | 4 |
| invoice/obfuscated-structural-1 | hashed_graph | 2 | 3 |
| invoice/obfuscated-structural-2 | trained | 2 | 2 |
| invoice/obfuscated-structural-2 | untrained | 4 | 4 |
| invoice/obfuscated-structural-2 | hashed_graph | 2 | 3 |
| invoice/negative | trained | 1 | N/A |
| invoice/negative | untrained | 1 | N/A |
| invoice/negative | hashed_graph | 1 | N/A |
| inventory/original | trained | 1 | 1 |
| inventory/original | untrained | 1 | 1 |
| inventory/original | hashed_graph | 1 | 1 |
| inventory/obfuscated-light-0 | trained | 1 | 1 |
| inventory/obfuscated-light-0 | untrained | 1 | 1 |
| inventory/obfuscated-light-0 | hashed_graph | 1 | 1 |
| inventory/obfuscated-light-1 | trained | 1 | 1 |
| inventory/obfuscated-light-1 | untrained | 1 | 1 |
| inventory/obfuscated-light-1 | hashed_graph | 1 | 1 |
| inventory/obfuscated-light-2 | trained | 1 | 1 |
| inventory/obfuscated-light-2 | untrained | 1 | 1 |
| inventory/obfuscated-light-2 | hashed_graph | 1 | 1 |
| inventory/obfuscated-structural-0 | trained | 1 | 1 |
| inventory/obfuscated-structural-0 | untrained | 1 | 2 |
| inventory/obfuscated-structural-0 | hashed_graph | 1 | 1 |
| inventory/obfuscated-structural-1 | trained | 1 | 1 |
| inventory/obfuscated-structural-1 | untrained | 1 | 2 |
| inventory/obfuscated-structural-1 | hashed_graph | 1 | 1 |
| inventory/obfuscated-structural-2 | trained | 1 | 1 |
| inventory/obfuscated-structural-2 | untrained | 1 | 2 |
| inventory/obfuscated-structural-2 | hashed_graph | 1 | 1 |
| inventory/negative | trained | 1 | N/A |
| inventory/negative | untrained | 1 | N/A |
| inventory/negative | hashed_graph | 1 | N/A |
| events/original | trained | 1 | 1 |
| events/original | untrained | 1 | 1 |
| events/original | hashed_graph | 1 | 1 |
| events/obfuscated-light-0 | trained | 1 | 1 |
| events/obfuscated-light-0 | untrained | 1 | 1 |
| events/obfuscated-light-0 | hashed_graph | 1 | 1 |
| events/obfuscated-light-1 | trained | 1 | 1 |
| events/obfuscated-light-1 | untrained | 1 | 1 |
| events/obfuscated-light-1 | hashed_graph | 1 | 1 |
| events/obfuscated-light-2 | trained | 1 | 1 |
| events/obfuscated-light-2 | untrained | 1 | 1 |
| events/obfuscated-light-2 | hashed_graph | 1 | 1 |
| events/obfuscated-structural-0 | trained | 1 | 2 |
| events/obfuscated-structural-0 | untrained | 1 | 2 |
| events/obfuscated-structural-0 | hashed_graph | 1 | 1 |
| events/obfuscated-structural-1 | trained | 1 | 2 |
| events/obfuscated-structural-1 | untrained | 1 | 2 |
| events/obfuscated-structural-1 | hashed_graph | 1 | 1 |
| events/obfuscated-structural-2 | trained | 1 | 2 |
| events/obfuscated-structural-2 | untrained | 1 | 2 |
| events/obfuscated-structural-2 | hashed_graph | 1 | 1 |
| events/negative | trained | 1 | N/A |
| events/negative | untrained | 1 | N/A |
| events/negative | hashed_graph | 1 | N/A |
| transaction/original | trained | 1 | 1 |
| transaction/original | untrained | 1 | 1 |
| transaction/original | hashed_graph | 1 | 1 |
| transaction/obfuscated-light-0 | trained | 1 | 1 |
| transaction/obfuscated-light-0 | untrained | 1 | 1 |
| transaction/obfuscated-light-0 | hashed_graph | 1 | 1 |
| transaction/obfuscated-light-1 | trained | 1 | 1 |
| transaction/obfuscated-light-1 | untrained | 1 | 1 |
| transaction/obfuscated-light-1 | hashed_graph | 1 | 1 |
| transaction/obfuscated-light-2 | trained | 1 | 1 |
| transaction/obfuscated-light-2 | untrained | 1 | 1 |
| transaction/obfuscated-light-2 | hashed_graph | 1 | 1 |
| transaction/obfuscated-structural-0 | trained | 1 | 2 |
| transaction/obfuscated-structural-0 | untrained | 1 | 2 |
| transaction/obfuscated-structural-0 | hashed_graph | 1 | 2 |
| transaction/obfuscated-structural-1 | trained | 1 | 2 |
| transaction/obfuscated-structural-1 | untrained | 1 | 2 |
| transaction/obfuscated-structural-1 | hashed_graph | 1 | 2 |
| transaction/obfuscated-structural-2 | trained | 1 | 2 |
| transaction/obfuscated-structural-2 | untrained | 1 | 2 |
| transaction/obfuscated-structural-2 | hashed_graph | 1 | 2 |
| transaction/negative | trained | 1 | N/A |
| transaction/negative | untrained | 1 | N/A |
| transaction/negative | hashed_graph | 1 | N/A |
| memo/original | trained | 1 | 1 |
| memo/original | untrained | 1 | 1 |
| memo/original | hashed_graph | 1 | 1 |
| memo/obfuscated-light-0 | trained | 1 | 1 |
| memo/obfuscated-light-0 | untrained | 1 | 1 |
| memo/obfuscated-light-0 | hashed_graph | 1 | 1 |
| memo/obfuscated-light-1 | trained | 1 | 1 |
| memo/obfuscated-light-1 | untrained | 1 | 1 |
| memo/obfuscated-light-1 | hashed_graph | 1 | 1 |
| memo/obfuscated-light-2 | trained | 1 | 1 |
| memo/obfuscated-light-2 | untrained | 1 | 1 |
| memo/obfuscated-light-2 | hashed_graph | 1 | 1 |
| memo/obfuscated-structural-0 | trained | 1 | 1 |
| memo/obfuscated-structural-0 | untrained | 1 | 1 |
| memo/obfuscated-structural-0 | hashed_graph | 1 | 1 |
| memo/obfuscated-structural-1 | trained | 1 | 1 |
| memo/obfuscated-structural-1 | untrained | 1 | 1 |
| memo/obfuscated-structural-1 | hashed_graph | 1 | 1 |
| memo/obfuscated-structural-2 | trained | 1 | 1 |
| memo/obfuscated-structural-2 | untrained | 1 | 1 |
| memo/obfuscated-structural-2 | hashed_graph | 1 | 1 |
| memo/negative | trained | 1 | N/A |
| memo/negative | untrained | 1 | N/A |
| memo/negative | hashed_graph | 1 | N/A |
| codec/original | trained | 1 | 1 |
| codec/original | untrained | 1 | 1 |
| codec/original | hashed_graph | 1 | 1 |
| codec/obfuscated-light-0 | trained | 1 | 1 |
| codec/obfuscated-light-0 | untrained | 1 | 1 |
| codec/obfuscated-light-0 | hashed_graph | 1 | 1 |
| codec/obfuscated-light-1 | trained | 1 | 1 |
| codec/obfuscated-light-1 | untrained | 1 | 1 |
| codec/obfuscated-light-1 | hashed_graph | 1 | 1 |
| codec/obfuscated-light-2 | trained | 1 | 1 |
| codec/obfuscated-light-2 | untrained | 1 | 1 |
| codec/obfuscated-light-2 | hashed_graph | 1 | 1 |
| codec/obfuscated-structural-0 | trained | 5 | 6 |
| codec/obfuscated-structural-0 | untrained | 2 | 3 |
| codec/obfuscated-structural-0 | hashed_graph | 4 | 5 |
| codec/obfuscated-structural-1 | trained | 5 | 6 |
| codec/obfuscated-structural-1 | untrained | 2 | 3 |
| codec/obfuscated-structural-1 | hashed_graph | 4 | 5 |
| codec/obfuscated-structural-2 | trained | 5 | 6 |
| codec/obfuscated-structural-2 | untrained | 2 | 3 |
| codec/obfuscated-structural-2 | hashed_graph | 4 | 5 |
| codec/negative | trained | 1 | N/A |
| codec/negative | untrained | 1 | N/A |
| codec/negative | hashed_graph | 2 | N/A |
| dispatch/original | trained | 1 | 1 |
| dispatch/original | untrained | 1 | 1 |
| dispatch/original | hashed_graph | 1 | 1 |
| dispatch/obfuscated-light-0 | trained | 1 | 1 |
| dispatch/obfuscated-light-0 | untrained | 1 | 1 |
| dispatch/obfuscated-light-0 | hashed_graph | 1 | 1 |
| dispatch/obfuscated-light-1 | trained | 1 | 1 |
| dispatch/obfuscated-light-1 | untrained | 1 | 1 |
| dispatch/obfuscated-light-1 | hashed_graph | 1 | 1 |
| dispatch/obfuscated-light-2 | trained | 1 | 1 |
| dispatch/obfuscated-light-2 | untrained | 1 | 1 |
| dispatch/obfuscated-light-2 | hashed_graph | 1 | 1 |
| dispatch/obfuscated-structural-0 | trained | 2 | 3 |
| dispatch/obfuscated-structural-0 | untrained | 1 | 2 |
| dispatch/obfuscated-structural-0 | hashed_graph | 1 | 1 |
| dispatch/obfuscated-structural-1 | trained | 2 | 3 |
| dispatch/obfuscated-structural-1 | untrained | 1 | 2 |
| dispatch/obfuscated-structural-1 | hashed_graph | 1 | 1 |
| dispatch/obfuscated-structural-2 | trained | 2 | 3 |
| dispatch/obfuscated-structural-2 | untrained | 1 | 2 |
| dispatch/obfuscated-structural-2 | hashed_graph | 1 | 1 |
| dispatch/negative | trained | 1 | N/A |
| dispatch/negative | untrained | 1 | N/A |
| dispatch/negative | hashed_graph | 1 | N/A |
| dependencies/original | trained | 1 | 1 |
| dependencies/original | untrained | 1 | 1 |
| dependencies/original | hashed_graph | 1 | 1 |
| dependencies/obfuscated-light-0 | trained | 1 | 1 |
| dependencies/obfuscated-light-0 | untrained | 1 | 1 |
| dependencies/obfuscated-light-0 | hashed_graph | 1 | 1 |
| dependencies/obfuscated-light-1 | trained | 1 | 1 |
| dependencies/obfuscated-light-1 | untrained | 1 | 1 |
| dependencies/obfuscated-light-1 | hashed_graph | 1 | 1 |
| dependencies/obfuscated-light-2 | trained | 1 | 1 |
| dependencies/obfuscated-light-2 | untrained | 1 | 1 |
| dependencies/obfuscated-light-2 | hashed_graph | 1 | 1 |
| dependencies/obfuscated-structural-0 | trained | 1 | 2 |
| dependencies/obfuscated-structural-0 | untrained | 1 | 2 |
| dependencies/obfuscated-structural-0 | hashed_graph | 1 | 2 |
| dependencies/obfuscated-structural-1 | trained | 1 | 2 |
| dependencies/obfuscated-structural-1 | untrained | 1 | 2 |
| dependencies/obfuscated-structural-1 | hashed_graph | 1 | 2 |
| dependencies/obfuscated-structural-2 | trained | 1 | 2 |
| dependencies/obfuscated-structural-2 | untrained | 1 | 2 |
| dependencies/obfuscated-structural-2 | hashed_graph | 1 | 2 |
| dependencies/negative | trained | 1 | N/A |
| dependencies/negative | untrained | 1 | N/A |
| dependencies/negative | hashed_graph | 1 | N/A |
| async_queue/original | trained | 1 | 1 |
| async_queue/original | untrained | 1 | 1 |
| async_queue/original | hashed_graph | 1 | 1 |
| async_queue/obfuscated-light-0 | trained | 1 | 1 |
| async_queue/obfuscated-light-0 | untrained | 1 | 1 |
| async_queue/obfuscated-light-0 | hashed_graph | 1 | 1 |
| async_queue/obfuscated-light-1 | trained | 1 | 1 |
| async_queue/obfuscated-light-1 | untrained | 1 | 1 |
| async_queue/obfuscated-light-1 | hashed_graph | 1 | 1 |
| async_queue/obfuscated-light-2 | trained | 1 | 1 |
| async_queue/obfuscated-light-2 | untrained | 1 | 1 |
| async_queue/obfuscated-light-2 | hashed_graph | 1 | 1 |
| async_queue/obfuscated-structural-0 | trained | 1 | 2 |
| async_queue/obfuscated-structural-0 | untrained | 1 | 2 |
| async_queue/obfuscated-structural-0 | hashed_graph | 1 | 1 |
| async_queue/obfuscated-structural-1 | trained | 1 | 2 |
| async_queue/obfuscated-structural-1 | untrained | 1 | 2 |
| async_queue/obfuscated-structural-1 | hashed_graph | 1 | 1 |
| async_queue/obfuscated-structural-2 | trained | 1 | 2 |
| async_queue/obfuscated-structural-2 | untrained | 1 | 2 |
| async_queue/obfuscated-structural-2 | hashed_graph | 1 | 1 |
| async_queue/negative | trained | 1 | N/A |
| async_queue/negative | untrained | 1 | N/A |
| async_queue/negative | hashed_graph | 1 | N/A |
| typed_router/original | trained | 1 | 1 |
| typed_router/original | untrained | 1 | 1 |
| typed_router/original | hashed_graph | 1 | 1 |
| typed_router/obfuscated-light-0 | trained | 1 | 1 |
| typed_router/obfuscated-light-0 | untrained | 1 | 1 |
| typed_router/obfuscated-light-0 | hashed_graph | 1 | 1 |
| typed_router/obfuscated-light-1 | trained | 1 | 1 |
| typed_router/obfuscated-light-1 | untrained | 1 | 1 |
| typed_router/obfuscated-light-1 | hashed_graph | 1 | 1 |
| typed_router/obfuscated-light-2 | trained | 1 | 1 |
| typed_router/obfuscated-light-2 | untrained | 1 | 1 |
| typed_router/obfuscated-light-2 | hashed_graph | 1 | 1 |
| typed_router/obfuscated-structural-0 | trained | 1 | 2 |
| typed_router/obfuscated-structural-0 | untrained | 2 | 3 |
| typed_router/obfuscated-structural-0 | hashed_graph | 1 | 2 |
| typed_router/obfuscated-structural-1 | trained | 1 | 2 |
| typed_router/obfuscated-structural-1 | untrained | 2 | 3 |
| typed_router/obfuscated-structural-1 | hashed_graph | 1 | 2 |
| typed_router/obfuscated-structural-2 | trained | 1 | 2 |
| typed_router/obfuscated-structural-2 | untrained | 2 | 3 |
| typed_router/obfuscated-structural-2 | hashed_graph | 1 | 2 |
| typed_router/negative | trained | 1 | N/A |
| typed_router/negative | untrained | 1 | N/A |
| typed_router/negative | hashed_graph | 1 | N/A |
| async_queue/python-3.12/opt-0/uncompyle6 | trained | 2 | 2 |
| async_queue/python-3.12/opt-0/uncompyle6 | untrained | 2 | 2 |
| async_queue/python-3.12/opt-0/uncompyle6 | hashed_graph | 3 | 4 |
| async_queue/python-3.12/opt-0/pycdc | trained | 4 | 4 |
| async_queue/python-3.12/opt-0/pycdc | untrained | 6 | 6 |
| async_queue/python-3.12/opt-0/pycdc | hashed_graph | 3 | 4 |
| async_queue/python-3.12/opt-1/uncompyle6 | trained | 2 | 2 |
| async_queue/python-3.12/opt-1/uncompyle6 | untrained | 2 | 2 |
| async_queue/python-3.12/opt-1/uncompyle6 | hashed_graph | 3 | 4 |
| async_queue/python-3.12/opt-1/pycdc | trained | 4 | 4 |
| async_queue/python-3.12/opt-1/pycdc | untrained | 6 | 6 |
| async_queue/python-3.12/opt-1/pycdc | hashed_graph | 3 | 4 |
| async_queue/python-3.12/opt-2/uncompyle6 | trained | 2 | 2 |
| async_queue/python-3.12/opt-2/uncompyle6 | untrained | 2 | 2 |
| async_queue/python-3.12/opt-2/uncompyle6 | hashed_graph | 3 | 4 |
| async_queue/python-3.12/opt-2/pycdc | trained | 4 | 4 |
| async_queue/python-3.12/opt-2/pycdc | untrained | 6 | 6 |
| async_queue/python-3.12/opt-2/pycdc | hashed_graph | 3 | 4 |
| async_queue/python-3.14/opt-0/uncompyle6 | trained | 2 | 2 |
| async_queue/python-3.14/opt-0/uncompyle6 | untrained | 2 | 2 |
| async_queue/python-3.14/opt-0/uncompyle6 | hashed_graph | 3 | 4 |
| async_queue/python-3.14/opt-1/uncompyle6 | trained | 2 | 2 |
| async_queue/python-3.14/opt-1/uncompyle6 | untrained | 2 | 2 |
| async_queue/python-3.14/opt-1/uncompyle6 | hashed_graph | 3 | 4 |
| async_queue/python-3.14/opt-2/uncompyle6 | trained | 2 | 2 |
| async_queue/python-3.14/opt-2/uncompyle6 | untrained | 2 | 2 |
| async_queue/python-3.14/opt-2/uncompyle6 | hashed_graph | 3 | 4 |
| async_queue/python-3.8/opt-0/uncompyle6 | trained | 1 | 1 |
| async_queue/python-3.8/opt-0/uncompyle6 | untrained | 1 | 1 |
| async_queue/python-3.8/opt-0/uncompyle6 | hashed_graph | 1 | 1 |
| async_queue/python-3.8/opt-0/pycdc | trained | 1 | 1 |
| async_queue/python-3.8/opt-0/pycdc | untrained | 1 | 1 |
| async_queue/python-3.8/opt-0/pycdc | hashed_graph | 1 | 2 |
| async_queue/python-3.8/opt-1/uncompyle6 | trained | 1 | 1 |
| async_queue/python-3.8/opt-1/uncompyle6 | untrained | 1 | 1 |
| async_queue/python-3.8/opt-1/uncompyle6 | hashed_graph | 1 | 1 |
| async_queue/python-3.8/opt-1/pycdc | trained | 1 | 1 |
| async_queue/python-3.8/opt-1/pycdc | untrained | 1 | 1 |
| async_queue/python-3.8/opt-1/pycdc | hashed_graph | 1 | 2 |
| async_queue/python-3.8/opt-2/uncompyle6 | trained | 1 | 1 |
| async_queue/python-3.8/opt-2/uncompyle6 | untrained | 1 | 1 |
| async_queue/python-3.8/opt-2/uncompyle6 | hashed_graph | 1 | 1 |
| async_queue/python-3.8/opt-2/pycdc | trained | 1 | 1 |
| async_queue/python-3.8/opt-2/pycdc | untrained | 1 | 1 |
| async_queue/python-3.8/opt-2/pycdc | hashed_graph | 1 | 2 |
| codec/python-3.12/opt-0/uncompyle6 | trained | 1 | 1 |
| codec/python-3.12/opt-0/uncompyle6 | untrained | 4 | 5 |
| codec/python-3.12/opt-0/uncompyle6 | hashed_graph | 10 | 11 |
| codec/python-3.12/opt-0/pycdc | trained | 1 | 1 |
| codec/python-3.12/opt-0/pycdc | untrained | 1 | 1 |
| codec/python-3.12/opt-0/pycdc | hashed_graph | 1 | 1 |
| codec/python-3.12/opt-1/uncompyle6 | trained | 1 | 1 |
| codec/python-3.12/opt-1/uncompyle6 | untrained | 4 | 5 |
| codec/python-3.12/opt-1/uncompyle6 | hashed_graph | 10 | 11 |
| codec/python-3.12/opt-1/pycdc | trained | 1 | 1 |
| codec/python-3.12/opt-1/pycdc | untrained | 1 | 1 |
| codec/python-3.12/opt-1/pycdc | hashed_graph | 1 | 1 |
| codec/python-3.12/opt-2/uncompyle6 | trained | 1 | 1 |
| codec/python-3.12/opt-2/uncompyle6 | untrained | 4 | 5 |
| codec/python-3.12/opt-2/uncompyle6 | hashed_graph | 10 | 11 |
| codec/python-3.12/opt-2/pycdc | trained | 1 | 1 |
| codec/python-3.12/opt-2/pycdc | untrained | 1 | 1 |
| codec/python-3.12/opt-2/pycdc | hashed_graph | 1 | 1 |
| codec/python-3.14/opt-0/uncompyle6 | trained | 1 | 1 |
| codec/python-3.14/opt-0/uncompyle6 | untrained | 4 | 4 |
| codec/python-3.14/opt-0/uncompyle6 | hashed_graph | 10 | 11 |
| codec/python-3.14/opt-1/uncompyle6 | trained | 1 | 1 |
| codec/python-3.14/opt-1/uncompyle6 | untrained | 4 | 4 |
| codec/python-3.14/opt-1/uncompyle6 | hashed_graph | 10 | 11 |
| codec/python-3.14/opt-2/uncompyle6 | trained | 1 | 1 |
| codec/python-3.14/opt-2/uncompyle6 | untrained | 4 | 4 |
| codec/python-3.14/opt-2/uncompyle6 | hashed_graph | 10 | 11 |
| codec/python-3.4/opt-0/uncompyle6 | trained | 1 | 1 |
| codec/python-3.4/opt-0/uncompyle6 | untrained | 1 | 1 |
| codec/python-3.4/opt-0/uncompyle6 | hashed_graph | 1 | 1 |
| codec/python-3.4/opt-0/pycdc | trained | 1 | 1 |
| codec/python-3.4/opt-0/pycdc | untrained | 1 | 1 |
| codec/python-3.4/opt-0/pycdc | hashed_graph | 10 | 11 |
| codec/python-3.4/opt-1/uncompyle6 | trained | 1 | 1 |
| codec/python-3.4/opt-1/uncompyle6 | untrained | 1 | 1 |
| codec/python-3.4/opt-1/uncompyle6 | hashed_graph | 1 | 1 |
| codec/python-3.4/opt-1/pycdc | trained | 1 | 1 |
| codec/python-3.4/opt-1/pycdc | untrained | 1 | 1 |
| codec/python-3.4/opt-1/pycdc | hashed_graph | 10 | 11 |
| codec/python-3.4/opt-2/uncompyle6 | trained | 1 | 1 |
| codec/python-3.4/opt-2/uncompyle6 | untrained | 1 | 1 |
| codec/python-3.4/opt-2/uncompyle6 | hashed_graph | 1 | 1 |
| codec/python-3.4/opt-2/pycdc | trained | 1 | 1 |
| codec/python-3.4/opt-2/pycdc | untrained | 1 | 1 |
| codec/python-3.4/opt-2/pycdc | hashed_graph | 10 | 11 |
| codec/python-3.8/opt-0/uncompyle6 | trained | 1 | 1 |
| codec/python-3.8/opt-0/uncompyle6 | untrained | 1 | 1 |
| codec/python-3.8/opt-0/uncompyle6 | hashed_graph | 1 | 1 |
| codec/python-3.8/opt-0/pycdc | trained | 1 | 1 |
| codec/python-3.8/opt-0/pycdc | untrained | 1 | 1 |
| codec/python-3.8/opt-0/pycdc | hashed_graph | 10 | 11 |
| codec/python-3.8/opt-1/uncompyle6 | trained | 1 | 1 |
| codec/python-3.8/opt-1/uncompyle6 | untrained | 1 | 1 |
| codec/python-3.8/opt-1/uncompyle6 | hashed_graph | 1 | 1 |
| codec/python-3.8/opt-1/pycdc | trained | 1 | 1 |
| codec/python-3.8/opt-1/pycdc | untrained | 1 | 1 |
| codec/python-3.8/opt-1/pycdc | hashed_graph | 10 | 11 |
| codec/python-3.8/opt-2/uncompyle6 | trained | 1 | 1 |
| codec/python-3.8/opt-2/uncompyle6 | untrained | 1 | 1 |
| codec/python-3.8/opt-2/uncompyle6 | hashed_graph | 1 | 1 |
| codec/python-3.8/opt-2/pycdc | trained | 1 | 1 |
| codec/python-3.8/opt-2/pycdc | untrained | 1 | 1 |
| codec/python-3.8/opt-2/pycdc | hashed_graph | 10 | 11 |
| dependencies/python-3.12/opt-0/uncompyle6 | trained | 6 | 6 |
| dependencies/python-3.12/opt-0/uncompyle6 | untrained | 3 | 4 |
| dependencies/python-3.12/opt-0/uncompyle6 | hashed_graph | 2 | 3 |
| dependencies/python-3.12/opt-0/pycdc | trained | 1 | 1 |
| dependencies/python-3.12/opt-0/pycdc | untrained | 1 | 1 |
| dependencies/python-3.12/opt-0/pycdc | hashed_graph | 1 | 1 |
| dependencies/python-3.12/opt-1/uncompyle6 | trained | 6 | 6 |
| dependencies/python-3.12/opt-1/uncompyle6 | untrained | 3 | 4 |
| dependencies/python-3.12/opt-1/uncompyle6 | hashed_graph | 2 | 3 |
| dependencies/python-3.12/opt-1/pycdc | trained | 1 | 1 |
| dependencies/python-3.12/opt-1/pycdc | untrained | 1 | 1 |
| dependencies/python-3.12/opt-1/pycdc | hashed_graph | 1 | 1 |
| dependencies/python-3.12/opt-2/uncompyle6 | trained | 6 | 6 |
| dependencies/python-3.12/opt-2/uncompyle6 | untrained | 3 | 4 |
| dependencies/python-3.12/opt-2/uncompyle6 | hashed_graph | 2 | 3 |
| dependencies/python-3.12/opt-2/pycdc | trained | 1 | 1 |
| dependencies/python-3.12/opt-2/pycdc | untrained | 1 | 1 |
| dependencies/python-3.12/opt-2/pycdc | hashed_graph | 1 | 1 |
| dependencies/python-3.14/opt-0/uncompyle6 | trained | 5 | 5 |
| dependencies/python-3.14/opt-0/uncompyle6 | untrained | 3 | 3 |
| dependencies/python-3.14/opt-0/uncompyle6 | hashed_graph | 2 | 3 |
| dependencies/python-3.14/opt-1/uncompyle6 | trained | 5 | 5 |
| dependencies/python-3.14/opt-1/uncompyle6 | untrained | 3 | 3 |
| dependencies/python-3.14/opt-1/uncompyle6 | hashed_graph | 2 | 3 |
| dependencies/python-3.14/opt-2/uncompyle6 | trained | 5 | 5 |
| dependencies/python-3.14/opt-2/uncompyle6 | untrained | 3 | 3 |
| dependencies/python-3.14/opt-2/uncompyle6 | hashed_graph | 2 | 3 |
| dependencies/python-3.4/opt-0/uncompyle6 | trained | 1 | 1 |
| dependencies/python-3.4/opt-0/uncompyle6 | untrained | 1 | 1 |
| dependencies/python-3.4/opt-0/uncompyle6 | hashed_graph | 1 | 1 |
| dependencies/python-3.4/opt-0/pycdc | trained | 1 | 1 |
| dependencies/python-3.4/opt-0/pycdc | untrained | 1 | 1 |
| dependencies/python-3.4/opt-0/pycdc | hashed_graph | 1 | 1 |
| dependencies/python-3.4/opt-1/uncompyle6 | trained | 1 | 1 |
| dependencies/python-3.4/opt-1/uncompyle6 | untrained | 1 | 1 |
| dependencies/python-3.4/opt-1/uncompyle6 | hashed_graph | 1 | 1 |
| dependencies/python-3.4/opt-1/pycdc | trained | 1 | 1 |
| dependencies/python-3.4/opt-1/pycdc | untrained | 1 | 1 |
| dependencies/python-3.4/opt-1/pycdc | hashed_graph | 1 | 1 |
| dependencies/python-3.4/opt-2/uncompyle6 | trained | 1 | 1 |
| dependencies/python-3.4/opt-2/uncompyle6 | untrained | 1 | 1 |
| dependencies/python-3.4/opt-2/uncompyle6 | hashed_graph | 1 | 1 |
| dependencies/python-3.4/opt-2/pycdc | trained | 1 | 1 |
| dependencies/python-3.4/opt-2/pycdc | untrained | 1 | 1 |
| dependencies/python-3.4/opt-2/pycdc | hashed_graph | 1 | 1 |
| dependencies/python-3.8/opt-0/uncompyle6 | trained | 1 | 1 |
| dependencies/python-3.8/opt-0/uncompyle6 | untrained | 1 | 1 |
| dependencies/python-3.8/opt-0/uncompyle6 | hashed_graph | 1 | 1 |
| dependencies/python-3.8/opt-0/pycdc | trained | 1 | 1 |
| dependencies/python-3.8/opt-0/pycdc | untrained | 1 | 1 |
| dependencies/python-3.8/opt-0/pycdc | hashed_graph | 1 | 1 |
| dependencies/python-3.8/opt-1/uncompyle6 | trained | 1 | 1 |
| dependencies/python-3.8/opt-1/uncompyle6 | untrained | 1 | 1 |
| dependencies/python-3.8/opt-1/uncompyle6 | hashed_graph | 1 | 1 |
| dependencies/python-3.8/opt-1/pycdc | trained | 1 | 1 |
| dependencies/python-3.8/opt-1/pycdc | untrained | 1 | 1 |
| dependencies/python-3.8/opt-1/pycdc | hashed_graph | 1 | 1 |
| dependencies/python-3.8/opt-2/uncompyle6 | trained | 1 | 1 |
| dependencies/python-3.8/opt-2/uncompyle6 | untrained | 1 | 1 |
| dependencies/python-3.8/opt-2/uncompyle6 | hashed_graph | 1 | 1 |
| dependencies/python-3.8/opt-2/pycdc | trained | 1 | 1 |
| dependencies/python-3.8/opt-2/pycdc | untrained | 1 | 1 |
| dependencies/python-3.8/opt-2/pycdc | hashed_graph | 1 | 1 |
| dispatch/python-3.12/opt-0/uncompyle6 | trained | 10 | 11 |
| dispatch/python-3.12/opt-0/uncompyle6 | untrained | 8 | 9 |
| dispatch/python-3.12/opt-0/uncompyle6 | hashed_graph | 10 | 11 |
| dispatch/python-3.12/opt-0/pycdc | trained | 1 | 1 |
| dispatch/python-3.12/opt-0/pycdc | untrained | 1 | 1 |
| dispatch/python-3.12/opt-0/pycdc | hashed_graph | 1 | 1 |
| dispatch/python-3.12/opt-1/uncompyle6 | trained | 10 | 11 |
| dispatch/python-3.12/opt-1/uncompyle6 | untrained | 8 | 9 |
| dispatch/python-3.12/opt-1/uncompyle6 | hashed_graph | 10 | 11 |
| dispatch/python-3.12/opt-1/pycdc | trained | 1 | 1 |
| dispatch/python-3.12/opt-1/pycdc | untrained | 1 | 1 |
| dispatch/python-3.12/opt-1/pycdc | hashed_graph | 1 | 1 |
| dispatch/python-3.12/opt-2/uncompyle6 | trained | 10 | 11 |
| dispatch/python-3.12/opt-2/uncompyle6 | untrained | 8 | 9 |
| dispatch/python-3.12/opt-2/uncompyle6 | hashed_graph | 10 | 11 |
| dispatch/python-3.12/opt-2/pycdc | trained | 1 | 1 |
| dispatch/python-3.12/opt-2/pycdc | untrained | 1 | 1 |
| dispatch/python-3.12/opt-2/pycdc | hashed_graph | 1 | 1 |
| dispatch/python-3.14/opt-0/uncompyle6 | trained | 10 | 11 |
| dispatch/python-3.14/opt-0/uncompyle6 | untrained | 8 | 9 |
| dispatch/python-3.14/opt-0/uncompyle6 | hashed_graph | 10 | 11 |
| dispatch/python-3.14/opt-1/uncompyle6 | trained | 10 | 11 |
| dispatch/python-3.14/opt-1/uncompyle6 | untrained | 8 | 9 |
| dispatch/python-3.14/opt-1/uncompyle6 | hashed_graph | 10 | 11 |
| dispatch/python-3.14/opt-2/uncompyle6 | trained | 10 | 11 |
| dispatch/python-3.14/opt-2/uncompyle6 | untrained | 8 | 9 |
| dispatch/python-3.14/opt-2/uncompyle6 | hashed_graph | 10 | 11 |
| dispatch/python-3.4/opt-0/uncompyle6 | trained | 1 | 1 |
| dispatch/python-3.4/opt-0/uncompyle6 | untrained | 1 | 1 |
| dispatch/python-3.4/opt-0/uncompyle6 | hashed_graph | 1 | 1 |
| dispatch/python-3.4/opt-0/pycdc | trained | 1 | 1 |
| dispatch/python-3.4/opt-0/pycdc | untrained | 1 | 1 |
| dispatch/python-3.4/opt-0/pycdc | hashed_graph | 1 | 1 |
| dispatch/python-3.4/opt-1/uncompyle6 | trained | 1 | 1 |
| dispatch/python-3.4/opt-1/uncompyle6 | untrained | 1 | 1 |
| dispatch/python-3.4/opt-1/uncompyle6 | hashed_graph | 1 | 1 |
| dispatch/python-3.4/opt-1/pycdc | trained | 1 | 1 |
| dispatch/python-3.4/opt-1/pycdc | untrained | 1 | 1 |
| dispatch/python-3.4/opt-1/pycdc | hashed_graph | 1 | 1 |
| dispatch/python-3.4/opt-2/uncompyle6 | trained | 1 | 1 |
| dispatch/python-3.4/opt-2/uncompyle6 | untrained | 1 | 1 |
| dispatch/python-3.4/opt-2/uncompyle6 | hashed_graph | 1 | 1 |
| dispatch/python-3.4/opt-2/pycdc | trained | 1 | 1 |
| dispatch/python-3.4/opt-2/pycdc | untrained | 1 | 1 |
| dispatch/python-3.4/opt-2/pycdc | hashed_graph | 1 | 1 |
| dispatch/python-3.8/opt-0/uncompyle6 | trained | 1 | 1 |
| dispatch/python-3.8/opt-0/uncompyle6 | untrained | 1 | 1 |
| dispatch/python-3.8/opt-0/uncompyle6 | hashed_graph | 1 | 1 |
| dispatch/python-3.8/opt-0/pycdc | trained | 1 | 1 |
| dispatch/python-3.8/opt-0/pycdc | untrained | 1 | 1 |
| dispatch/python-3.8/opt-0/pycdc | hashed_graph | 1 | 1 |
| dispatch/python-3.8/opt-1/uncompyle6 | trained | 1 | 1 |
| dispatch/python-3.8/opt-1/uncompyle6 | untrained | 1 | 1 |
| dispatch/python-3.8/opt-1/uncompyle6 | hashed_graph | 1 | 1 |
| dispatch/python-3.8/opt-1/pycdc | trained | 1 | 1 |
| dispatch/python-3.8/opt-1/pycdc | untrained | 1 | 1 |
| dispatch/python-3.8/opt-1/pycdc | hashed_graph | 1 | 1 |
| dispatch/python-3.8/opt-2/uncompyle6 | trained | 1 | 1 |
| dispatch/python-3.8/opt-2/uncompyle6 | untrained | 1 | 1 |
| dispatch/python-3.8/opt-2/uncompyle6 | hashed_graph | 1 | 1 |
| dispatch/python-3.8/opt-2/pycdc | trained | 1 | 1 |
| dispatch/python-3.8/opt-2/pycdc | untrained | 1 | 1 |
| dispatch/python-3.8/opt-2/pycdc | hashed_graph | 1 | 1 |
| events/python-3.12/opt-0/uncompyle6 | trained | 3 | 4 |
| events/python-3.12/opt-0/uncompyle6 | untrained | 1 | 2 |
| events/python-3.12/opt-0/uncompyle6 | hashed_graph | 10 | 11 |
| events/python-3.12/opt-0/pycdc | trained | 9 | 10 |
| events/python-3.12/opt-0/pycdc | untrained | 9 | 9 |
| events/python-3.12/opt-0/pycdc | hashed_graph | 6 | 7 |
| events/python-3.12/opt-1/uncompyle6 | trained | 3 | 4 |
| events/python-3.12/opt-1/uncompyle6 | untrained | 1 | 2 |
| events/python-3.12/opt-1/uncompyle6 | hashed_graph | 10 | 11 |
| events/python-3.12/opt-1/pycdc | trained | 9 | 10 |
| events/python-3.12/opt-1/pycdc | untrained | 9 | 9 |
| events/python-3.12/opt-1/pycdc | hashed_graph | 6 | 7 |
| events/python-3.12/opt-2/uncompyle6 | trained | 3 | 4 |
| events/python-3.12/opt-2/uncompyle6 | untrained | 1 | 2 |
| events/python-3.12/opt-2/uncompyle6 | hashed_graph | 10 | 11 |
| events/python-3.12/opt-2/pycdc | trained | 9 | 10 |
| events/python-3.12/opt-2/pycdc | untrained | 9 | 9 |
| events/python-3.12/opt-2/pycdc | hashed_graph | 6 | 7 |
| events/python-3.14/opt-0/uncompyle6 | trained | 3 | 4 |
| events/python-3.14/opt-0/uncompyle6 | untrained | 1 | 2 |
| events/python-3.14/opt-0/uncompyle6 | hashed_graph | 10 | 11 |
| events/python-3.14/opt-1/uncompyle6 | trained | 3 | 4 |
| events/python-3.14/opt-1/uncompyle6 | untrained | 1 | 2 |
| events/python-3.14/opt-1/uncompyle6 | hashed_graph | 10 | 11 |
| events/python-3.14/opt-2/uncompyle6 | trained | 3 | 4 |
| events/python-3.14/opt-2/uncompyle6 | untrained | 1 | 2 |
| events/python-3.14/opt-2/uncompyle6 | hashed_graph | 10 | 11 |
| events/python-3.4/opt-0/uncompyle6 | trained | 1 | 1 |
| events/python-3.4/opt-0/uncompyle6 | untrained | 1 | 1 |
| events/python-3.4/opt-0/uncompyle6 | hashed_graph | 1 | 1 |
| events/python-3.4/opt-0/pycdc | trained | 2 | 3 |
| events/python-3.4/opt-0/pycdc | untrained | 2 | 3 |
| events/python-3.4/opt-0/pycdc | hashed_graph | 10 | 11 |
| events/python-3.4/opt-1/uncompyle6 | trained | 1 | 1 |
| events/python-3.4/opt-1/uncompyle6 | untrained | 1 | 1 |
| events/python-3.4/opt-1/uncompyle6 | hashed_graph | 1 | 1 |
| events/python-3.4/opt-1/pycdc | trained | 2 | 3 |
| events/python-3.4/opt-1/pycdc | untrained | 2 | 3 |
| events/python-3.4/opt-1/pycdc | hashed_graph | 10 | 11 |
| events/python-3.4/opt-2/uncompyle6 | trained | 1 | 1 |
| events/python-3.4/opt-2/uncompyle6 | untrained | 1 | 1 |
| events/python-3.4/opt-2/uncompyle6 | hashed_graph | 1 | 1 |
| events/python-3.4/opt-2/pycdc | trained | 2 | 3 |
| events/python-3.4/opt-2/pycdc | untrained | 2 | 3 |
| events/python-3.4/opt-2/pycdc | hashed_graph | 10 | 11 |
| events/python-3.8/opt-0/uncompyle6 | trained | 2 | 3 |
| events/python-3.8/opt-0/uncompyle6 | untrained | 2 | 3 |
| events/python-3.8/opt-0/uncompyle6 | hashed_graph | 10 | 11 |
| events/python-3.8/opt-0/pycdc | trained | 2 | 3 |
| events/python-3.8/opt-0/pycdc | untrained | 2 | 3 |
| events/python-3.8/opt-0/pycdc | hashed_graph | 10 | 11 |
| events/python-3.8/opt-1/uncompyle6 | trained | 2 | 3 |
| events/python-3.8/opt-1/uncompyle6 | untrained | 2 | 3 |
| events/python-3.8/opt-1/uncompyle6 | hashed_graph | 10 | 11 |
| events/python-3.8/opt-1/pycdc | trained | 2 | 3 |
| events/python-3.8/opt-1/pycdc | untrained | 2 | 3 |
| events/python-3.8/opt-1/pycdc | hashed_graph | 10 | 11 |
| events/python-3.8/opt-2/uncompyle6 | trained | 2 | 3 |
| events/python-3.8/opt-2/uncompyle6 | untrained | 2 | 3 |
| events/python-3.8/opt-2/uncompyle6 | hashed_graph | 10 | 11 |
| events/python-3.8/opt-2/pycdc | trained | 2 | 3 |
| events/python-3.8/opt-2/pycdc | untrained | 2 | 3 |
| events/python-3.8/opt-2/pycdc | hashed_graph | 10 | 11 |
| inventory/python-3.12/opt-0/uncompyle6 | trained | 7 | 7 |
| inventory/python-3.12/opt-0/uncompyle6 | untrained | 6 | 6 |
| inventory/python-3.12/opt-0/uncompyle6 | hashed_graph | 5 | 6 |
| inventory/python-3.12/opt-0/pycdc | trained | 1 | 2 |
| inventory/python-3.12/opt-0/pycdc | untrained | 1 | 2 |
| inventory/python-3.12/opt-0/pycdc | hashed_graph | 1 | 1 |
| inventory/python-3.12/opt-1/uncompyle6 | trained | 7 | 7 |
| inventory/python-3.12/opt-1/uncompyle6 | untrained | 6 | 6 |
| inventory/python-3.12/opt-1/uncompyle6 | hashed_graph | 5 | 6 |
| inventory/python-3.12/opt-1/pycdc | trained | 1 | 2 |
| inventory/python-3.12/opt-1/pycdc | untrained | 1 | 2 |
| inventory/python-3.12/opt-1/pycdc | hashed_graph | 1 | 1 |
| inventory/python-3.12/opt-2/uncompyle6 | trained | 7 | 7 |
| inventory/python-3.12/opt-2/uncompyle6 | untrained | 6 | 6 |
| inventory/python-3.12/opt-2/uncompyle6 | hashed_graph | 5 | 6 |
| inventory/python-3.12/opt-2/pycdc | trained | 1 | 2 |
| inventory/python-3.12/opt-2/pycdc | untrained | 1 | 2 |
| inventory/python-3.12/opt-2/pycdc | hashed_graph | 1 | 1 |
| inventory/python-3.14/opt-0/uncompyle6 | trained | 7 | 7 |
| inventory/python-3.14/opt-0/uncompyle6 | untrained | 6 | 6 |
| inventory/python-3.14/opt-0/uncompyle6 | hashed_graph | 5 | 6 |
| inventory/python-3.14/opt-1/uncompyle6 | trained | 7 | 7 |
| inventory/python-3.14/opt-1/uncompyle6 | untrained | 6 | 6 |
| inventory/python-3.14/opt-1/uncompyle6 | hashed_graph | 5 | 6 |
| inventory/python-3.14/opt-2/uncompyle6 | trained | 7 | 7 |
| inventory/python-3.14/opt-2/uncompyle6 | untrained | 6 | 6 |
| inventory/python-3.14/opt-2/uncompyle6 | hashed_graph | 5 | 6 |
| inventory/python-3.4/opt-0/uncompyle6 | trained | 1 | 1 |
| inventory/python-3.4/opt-0/uncompyle6 | untrained | 1 | 1 |
| inventory/python-3.4/opt-0/uncompyle6 | hashed_graph | 1 | 1 |
| inventory/python-3.4/opt-0/pycdc | trained | 1 | 1 |
| inventory/python-3.4/opt-0/pycdc | untrained | 1 | 2 |
| inventory/python-3.4/opt-0/pycdc | hashed_graph | 1 | 1 |
| inventory/python-3.4/opt-1/uncompyle6 | trained | 1 | 1 |
| inventory/python-3.4/opt-1/uncompyle6 | untrained | 1 | 1 |
| inventory/python-3.4/opt-1/uncompyle6 | hashed_graph | 1 | 1 |
| inventory/python-3.4/opt-1/pycdc | trained | 1 | 1 |
| inventory/python-3.4/opt-1/pycdc | untrained | 1 | 2 |
| inventory/python-3.4/opt-1/pycdc | hashed_graph | 1 | 1 |
| inventory/python-3.4/opt-2/uncompyle6 | trained | 1 | 1 |
| inventory/python-3.4/opt-2/uncompyle6 | untrained | 1 | 1 |
| inventory/python-3.4/opt-2/uncompyle6 | hashed_graph | 1 | 1 |
| inventory/python-3.4/opt-2/pycdc | trained | 1 | 1 |
| inventory/python-3.4/opt-2/pycdc | untrained | 1 | 2 |
| inventory/python-3.4/opt-2/pycdc | hashed_graph | 1 | 1 |
| inventory/python-3.8/opt-0/uncompyle6 | trained | 1 | 2 |
| inventory/python-3.8/opt-0/uncompyle6 | untrained | 1 | 2 |
| inventory/python-3.8/opt-0/uncompyle6 | hashed_graph | 1 | 1 |
| inventory/python-3.8/opt-0/pycdc | trained | 1 | 1 |
| inventory/python-3.8/opt-0/pycdc | untrained | 1 | 2 |
| inventory/python-3.8/opt-0/pycdc | hashed_graph | 1 | 1 |
| inventory/python-3.8/opt-1/uncompyle6 | trained | 1 | 2 |
| inventory/python-3.8/opt-1/uncompyle6 | untrained | 1 | 2 |
| inventory/python-3.8/opt-1/uncompyle6 | hashed_graph | 1 | 1 |
| inventory/python-3.8/opt-1/pycdc | trained | 1 | 1 |
| inventory/python-3.8/opt-1/pycdc | untrained | 1 | 2 |
| inventory/python-3.8/opt-1/pycdc | hashed_graph | 1 | 1 |
| inventory/python-3.8/opt-2/uncompyle6 | trained | 1 | 2 |
| inventory/python-3.8/opt-2/uncompyle6 | untrained | 1 | 2 |
| inventory/python-3.8/opt-2/uncompyle6 | hashed_graph | 1 | 1 |
| inventory/python-3.8/opt-2/pycdc | trained | 1 | 1 |
| inventory/python-3.8/opt-2/pycdc | untrained | 1 | 2 |
| inventory/python-3.8/opt-2/pycdc | hashed_graph | 1 | 1 |
| invoice/python-3.12/opt-0/uncompyle6 | trained | 9 | 9 |
| invoice/python-3.12/opt-0/uncompyle6 | untrained | 9 | 9 |
| invoice/python-3.12/opt-0/uncompyle6 | hashed_graph | 10 | 11 |
| invoice/python-3.12/opt-0/pycdc | trained | 1 | 1 |
| invoice/python-3.12/opt-0/pycdc | untrained | 1 | 1 |
| invoice/python-3.12/opt-0/pycdc | hashed_graph | 1 | 2 |
| invoice/python-3.12/opt-1/uncompyle6 | trained | 9 | 9 |
| invoice/python-3.12/opt-1/uncompyle6 | untrained | 9 | 9 |
| invoice/python-3.12/opt-1/uncompyle6 | hashed_graph | 10 | 11 |
| invoice/python-3.12/opt-1/pycdc | trained | 1 | 1 |
| invoice/python-3.12/opt-1/pycdc | untrained | 1 | 1 |
| invoice/python-3.12/opt-1/pycdc | hashed_graph | 1 | 2 |
| invoice/python-3.12/opt-2/uncompyle6 | trained | 9 | 9 |
| invoice/python-3.12/opt-2/uncompyle6 | untrained | 9 | 9 |
| invoice/python-3.12/opt-2/uncompyle6 | hashed_graph | 10 | 11 |
| invoice/python-3.12/opt-2/pycdc | trained | 1 | 1 |
| invoice/python-3.12/opt-2/pycdc | untrained | 1 | 1 |
| invoice/python-3.12/opt-2/pycdc | hashed_graph | 1 | 2 |
| invoice/python-3.14/opt-0/uncompyle6 | trained | 9 | 9 |
| invoice/python-3.14/opt-0/uncompyle6 | untrained | 9 | 9 |
| invoice/python-3.14/opt-0/uncompyle6 | hashed_graph | 10 | 11 |
| invoice/python-3.14/opt-1/uncompyle6 | trained | 9 | 9 |
| invoice/python-3.14/opt-1/uncompyle6 | untrained | 9 | 9 |
| invoice/python-3.14/opt-1/uncompyle6 | hashed_graph | 10 | 11 |
| invoice/python-3.14/opt-2/uncompyle6 | trained | 9 | 9 |
| invoice/python-3.14/opt-2/uncompyle6 | untrained | 9 | 9 |
| invoice/python-3.14/opt-2/uncompyle6 | hashed_graph | 10 | 11 |
| invoice/python-3.4/opt-0/uncompyle6 | trained | 1 | 1 |
| invoice/python-3.4/opt-0/uncompyle6 | untrained | 1 | 1 |
| invoice/python-3.4/opt-0/uncompyle6 | hashed_graph | 1 | 1 |
| invoice/python-3.4/opt-0/pycdc | trained | 1 | 1 |
| invoice/python-3.4/opt-0/pycdc | untrained | 5 | 5 |
| invoice/python-3.4/opt-0/pycdc | hashed_graph | 1 | 1 |
| invoice/python-3.4/opt-1/uncompyle6 | trained | 1 | 1 |
| invoice/python-3.4/opt-1/uncompyle6 | untrained | 1 | 1 |
| invoice/python-3.4/opt-1/uncompyle6 | hashed_graph | 1 | 1 |
| invoice/python-3.4/opt-1/pycdc | trained | 1 | 1 |
| invoice/python-3.4/opt-1/pycdc | untrained | 5 | 5 |
| invoice/python-3.4/opt-1/pycdc | hashed_graph | 1 | 1 |
| invoice/python-3.4/opt-2/uncompyle6 | trained | 1 | 1 |
| invoice/python-3.4/opt-2/uncompyle6 | untrained | 1 | 1 |
| invoice/python-3.4/opt-2/uncompyle6 | hashed_graph | 1 | 1 |
| invoice/python-3.4/opt-2/pycdc | trained | 1 | 1 |
| invoice/python-3.4/opt-2/pycdc | untrained | 5 | 5 |
| invoice/python-3.4/opt-2/pycdc | hashed_graph | 1 | 1 |
| invoice/python-3.8/opt-0/uncompyle6 | trained | 1 | 1 |
| invoice/python-3.8/opt-0/uncompyle6 | untrained | 1 | 1 |
| invoice/python-3.8/opt-0/uncompyle6 | hashed_graph | 1 | 1 |
| invoice/python-3.8/opt-0/pycdc | trained | 1 | 1 |
| invoice/python-3.8/opt-0/pycdc | untrained | 5 | 5 |
| invoice/python-3.8/opt-0/pycdc | hashed_graph | 1 | 1 |
| invoice/python-3.8/opt-1/uncompyle6 | trained | 1 | 1 |
| invoice/python-3.8/opt-1/uncompyle6 | untrained | 1 | 1 |
| invoice/python-3.8/opt-1/uncompyle6 | hashed_graph | 1 | 1 |
| invoice/python-3.8/opt-1/pycdc | trained | 1 | 1 |
| invoice/python-3.8/opt-1/pycdc | untrained | 5 | 5 |
| invoice/python-3.8/opt-1/pycdc | hashed_graph | 1 | 1 |
| invoice/python-3.8/opt-2/uncompyle6 | trained | 1 | 1 |
| invoice/python-3.8/opt-2/uncompyle6 | untrained | 1 | 1 |
| invoice/python-3.8/opt-2/uncompyle6 | hashed_graph | 1 | 1 |
| invoice/python-3.8/opt-2/pycdc | trained | 1 | 1 |
| invoice/python-3.8/opt-2/pycdc | untrained | 5 | 5 |
| invoice/python-3.8/opt-2/pycdc | hashed_graph | 1 | 1 |
| memo/python-3.12/opt-0/uncompyle6 | trained | 8 | 8 |
| memo/python-3.12/opt-0/uncompyle6 | untrained | 7 | 7 |
| memo/python-3.12/opt-0/uncompyle6 | hashed_graph | 1 | 1 |
| memo/python-3.12/opt-0/pycdc | trained | 4 | 4 |
| memo/python-3.12/opt-0/pycdc | untrained | 3 | 3 |
| memo/python-3.12/opt-0/pycdc | hashed_graph | 5 | 5 |
| memo/python-3.12/opt-1/uncompyle6 | trained | 8 | 8 |
| memo/python-3.12/opt-1/uncompyle6 | untrained | 7 | 7 |
| memo/python-3.12/opt-1/uncompyle6 | hashed_graph | 1 | 1 |
| memo/python-3.12/opt-1/pycdc | trained | 4 | 4 |
| memo/python-3.12/opt-1/pycdc | untrained | 3 | 3 |
| memo/python-3.12/opt-1/pycdc | hashed_graph | 5 | 5 |
| memo/python-3.12/opt-2/uncompyle6 | trained | 8 | 8 |
| memo/python-3.12/opt-2/uncompyle6 | untrained | 7 | 7 |
| memo/python-3.12/opt-2/uncompyle6 | hashed_graph | 1 | 1 |
| memo/python-3.12/opt-2/pycdc | trained | 4 | 4 |
| memo/python-3.12/opt-2/pycdc | untrained | 3 | 3 |
| memo/python-3.12/opt-2/pycdc | hashed_graph | 5 | 5 |
| memo/python-3.14/opt-0/uncompyle6 | trained | 8 | 8 |
| memo/python-3.14/opt-0/uncompyle6 | untrained | 7 | 7 |
| memo/python-3.14/opt-0/uncompyle6 | hashed_graph | 1 | 1 |
| memo/python-3.14/opt-1/uncompyle6 | trained | 8 | 8 |
| memo/python-3.14/opt-1/uncompyle6 | untrained | 7 | 7 |
| memo/python-3.14/opt-1/uncompyle6 | hashed_graph | 1 | 1 |
| memo/python-3.14/opt-2/uncompyle6 | trained | 8 | 8 |
| memo/python-3.14/opt-2/uncompyle6 | untrained | 7 | 7 |
| memo/python-3.14/opt-2/uncompyle6 | hashed_graph | 1 | 1 |
| memo/python-3.4/opt-0/uncompyle6 | trained | 1 | 1 |
| memo/python-3.4/opt-0/uncompyle6 | untrained | 1 | 1 |
| memo/python-3.4/opt-0/uncompyle6 | hashed_graph | 1 | 1 |
| memo/python-3.4/opt-0/pycdc | trained | 8 | 8 |
| memo/python-3.4/opt-0/pycdc | untrained | 7 | 7 |
| memo/python-3.4/opt-0/pycdc | hashed_graph | 1 | 1 |
| memo/python-3.4/opt-1/uncompyle6 | trained | 1 | 1 |
| memo/python-3.4/opt-1/uncompyle6 | untrained | 1 | 1 |
| memo/python-3.4/opt-1/uncompyle6 | hashed_graph | 1 | 1 |
| memo/python-3.4/opt-1/pycdc | trained | 8 | 8 |
| memo/python-3.4/opt-1/pycdc | untrained | 7 | 7 |
| memo/python-3.4/opt-1/pycdc | hashed_graph | 1 | 1 |
| memo/python-3.4/opt-2/uncompyle6 | trained | 1 | 1 |
| memo/python-3.4/opt-2/uncompyle6 | untrained | 1 | 1 |
| memo/python-3.4/opt-2/uncompyle6 | hashed_graph | 1 | 1 |
| memo/python-3.4/opt-2/pycdc | trained | 8 | 8 |
| memo/python-3.4/opt-2/pycdc | untrained | 7 | 7 |
| memo/python-3.4/opt-2/pycdc | hashed_graph | 1 | 1 |
| memo/python-3.8/opt-0/uncompyle6 | trained | 1 | 1 |
| memo/python-3.8/opt-0/uncompyle6 | untrained | 1 | 1 |
| memo/python-3.8/opt-0/uncompyle6 | hashed_graph | 1 | 1 |
| memo/python-3.8/opt-0/pycdc | trained | 8 | 8 |
| memo/python-3.8/opt-0/pycdc | untrained | 7 | 7 |
| memo/python-3.8/opt-0/pycdc | hashed_graph | 1 | 1 |
| memo/python-3.8/opt-1/uncompyle6 | trained | 1 | 1 |
| memo/python-3.8/opt-1/uncompyle6 | untrained | 1 | 1 |
| memo/python-3.8/opt-1/uncompyle6 | hashed_graph | 1 | 1 |
| memo/python-3.8/opt-1/pycdc | trained | 8 | 8 |
| memo/python-3.8/opt-1/pycdc | untrained | 7 | 7 |
| memo/python-3.8/opt-1/pycdc | hashed_graph | 1 | 1 |
| memo/python-3.8/opt-2/uncompyle6 | trained | 1 | 1 |
| memo/python-3.8/opt-2/uncompyle6 | untrained | 1 | 1 |
| memo/python-3.8/opt-2/uncompyle6 | hashed_graph | 1 | 1 |
| memo/python-3.8/opt-2/pycdc | trained | 8 | 8 |
| memo/python-3.8/opt-2/pycdc | untrained | 7 | 7 |
| memo/python-3.8/opt-2/pycdc | hashed_graph | 1 | 1 |
| transaction/python-3.12/opt-0/uncompyle6 | trained | 4 | 4 |
| transaction/python-3.12/opt-0/uncompyle6 | untrained | 5 | 5 |
| transaction/python-3.12/opt-0/uncompyle6 | hashed_graph | 10 | 11 |
| transaction/python-3.12/opt-0/pycdc | trained | 1 | 1 |
| transaction/python-3.12/opt-0/pycdc | untrained | 1 | 1 |
| transaction/python-3.12/opt-0/pycdc | hashed_graph | 1 | 1 |
| transaction/python-3.12/opt-1/uncompyle6 | trained | 4 | 4 |
| transaction/python-3.12/opt-1/uncompyle6 | untrained | 5 | 5 |
| transaction/python-3.12/opt-1/uncompyle6 | hashed_graph | 10 | 11 |
| transaction/python-3.12/opt-1/pycdc | trained | 1 | 1 |
| transaction/python-3.12/opt-1/pycdc | untrained | 1 | 1 |
| transaction/python-3.12/opt-1/pycdc | hashed_graph | 1 | 1 |
| transaction/python-3.12/opt-2/uncompyle6 | trained | 4 | 4 |
| transaction/python-3.12/opt-2/uncompyle6 | untrained | 5 | 5 |
| transaction/python-3.12/opt-2/uncompyle6 | hashed_graph | 10 | 11 |
| transaction/python-3.12/opt-2/pycdc | trained | 1 | 1 |
| transaction/python-3.12/opt-2/pycdc | untrained | 1 | 1 |
| transaction/python-3.12/opt-2/pycdc | hashed_graph | 1 | 1 |
| transaction/python-3.4/opt-0/uncompyle6 | trained | 1 | 1 |
| transaction/python-3.4/opt-0/uncompyle6 | untrained | 1 | 1 |
| transaction/python-3.4/opt-0/uncompyle6 | hashed_graph | 1 | 1 |
| transaction/python-3.4/opt-0/pycdc | trained | 2 | 2 |
| transaction/python-3.4/opt-0/pycdc | untrained | 5 | 5 |
| transaction/python-3.4/opt-0/pycdc | hashed_graph | 10 | 11 |
| transaction/python-3.4/opt-1/uncompyle6 | trained | 1 | 1 |
| transaction/python-3.4/opt-1/uncompyle6 | untrained | 1 | 1 |
| transaction/python-3.4/opt-1/uncompyle6 | hashed_graph | 1 | 1 |
| transaction/python-3.4/opt-1/pycdc | trained | 2 | 2 |
| transaction/python-3.4/opt-1/pycdc | untrained | 5 | 5 |
| transaction/python-3.4/opt-1/pycdc | hashed_graph | 10 | 11 |
| transaction/python-3.4/opt-2/uncompyle6 | trained | 1 | 1 |
| transaction/python-3.4/opt-2/uncompyle6 | untrained | 1 | 1 |
| transaction/python-3.4/opt-2/uncompyle6 | hashed_graph | 1 | 1 |
| transaction/python-3.4/opt-2/pycdc | trained | 2 | 2 |
| transaction/python-3.4/opt-2/pycdc | untrained | 5 | 5 |
| transaction/python-3.4/opt-2/pycdc | hashed_graph | 10 | 11 |
| transaction/python-3.8/opt-0/uncompyle6 | trained | 1 | 1 |
| transaction/python-3.8/opt-0/uncompyle6 | untrained | 1 | 1 |
| transaction/python-3.8/opt-0/uncompyle6 | hashed_graph | 1 | 1 |
| transaction/python-3.8/opt-0/pycdc | trained | 1 | 1 |
| transaction/python-3.8/opt-0/pycdc | untrained | 1 | 1 |
| transaction/python-3.8/opt-0/pycdc | hashed_graph | 1 | 1 |
| transaction/python-3.8/opt-1/uncompyle6 | trained | 1 | 1 |
| transaction/python-3.8/opt-1/uncompyle6 | untrained | 1 | 1 |
| transaction/python-3.8/opt-1/uncompyle6 | hashed_graph | 1 | 1 |
| transaction/python-3.8/opt-1/pycdc | trained | 1 | 1 |
| transaction/python-3.8/opt-1/pycdc | untrained | 1 | 1 |
| transaction/python-3.8/opt-1/pycdc | hashed_graph | 1 | 1 |
| transaction/python-3.8/opt-2/uncompyle6 | trained | 1 | 1 |
| transaction/python-3.8/opt-2/uncompyle6 | untrained | 1 | 1 |
| transaction/python-3.8/opt-2/uncompyle6 | hashed_graph | 1 | 1 |
| transaction/python-3.8/opt-2/pycdc | trained | 1 | 1 |
| transaction/python-3.8/opt-2/pycdc | untrained | 1 | 1 |
| transaction/python-3.8/opt-2/pycdc | hashed_graph | 1 | 1 |
| typed_router/python-3.12/opt-0/uncompyle6 | trained | 5 | 6 |
| typed_router/python-3.12/opt-0/uncompyle6 | untrained | 10 | 11 |
| typed_router/python-3.12/opt-0/uncompyle6 | hashed_graph | 4 | 5 |
| typed_router/python-3.12/opt-0/pycdc | trained | 5 | 6 |
| typed_router/python-3.12/opt-0/pycdc | untrained | 10 | 11 |
| typed_router/python-3.12/opt-0/pycdc | hashed_graph | 4 | 5 |
| typed_router/python-3.12/opt-1/uncompyle6 | trained | 5 | 6 |
| typed_router/python-3.12/opt-1/uncompyle6 | untrained | 10 | 11 |
| typed_router/python-3.12/opt-1/uncompyle6 | hashed_graph | 4 | 5 |
| typed_router/python-3.12/opt-1/pycdc | trained | 5 | 6 |
| typed_router/python-3.12/opt-1/pycdc | untrained | 10 | 11 |
| typed_router/python-3.12/opt-1/pycdc | hashed_graph | 4 | 5 |
| typed_router/python-3.12/opt-2/uncompyle6 | trained | 5 | 6 |
| typed_router/python-3.12/opt-2/uncompyle6 | untrained | 10 | 11 |
| typed_router/python-3.12/opt-2/uncompyle6 | hashed_graph | 4 | 5 |
| typed_router/python-3.12/opt-2/pycdc | trained | 5 | 6 |
| typed_router/python-3.12/opt-2/pycdc | untrained | 10 | 11 |
| typed_router/python-3.12/opt-2/pycdc | hashed_graph | 4 | 5 |
| typed_router/python-3.14/opt-0/uncompyle6 | trained | 6 | 7 |
| typed_router/python-3.14/opt-0/uncompyle6 | untrained | 10 | 11 |
| typed_router/python-3.14/opt-0/uncompyle6 | hashed_graph | 4 | 5 |
| typed_router/python-3.14/opt-1/uncompyle6 | trained | 6 | 7 |
| typed_router/python-3.14/opt-1/uncompyle6 | untrained | 10 | 11 |
| typed_router/python-3.14/opt-1/uncompyle6 | hashed_graph | 4 | 5 |
| typed_router/python-3.14/opt-2/uncompyle6 | trained | 6 | 7 |
| typed_router/python-3.14/opt-2/uncompyle6 | untrained | 10 | 11 |
| typed_router/python-3.14/opt-2/uncompyle6 | hashed_graph | 4 | 5 |

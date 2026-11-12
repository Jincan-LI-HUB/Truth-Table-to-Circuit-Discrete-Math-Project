# Round 6.0 — WSL local reproduction

## Acceptance

- Paired runs: 2; reference and Round 6.0 tested in alternating orders.
- Official functional PASS: 25/25 and 25/25.
- Official delay targets: 25/25 and 25/25.
- Area sums: 529014 → 528738 in run 1; 529014 → 528744 in run 2.
- Median runtime averaged across the two runs: 52.344 ms → 115.481 ms (+120.62%).
- First-run outputs byte-identical: 16/25 (rewriting should change some outputs).

## Holdout distributions

| Group | Functional PASS | Target Met | Area before → after | Median before → after (ms) |
|---|---:|---:|---:|---:|
| holdout_round60_v1 | 40/40 | 40/40 | 9709 → 9496 | 10.557 → 14.383 |
| previous_holdout_v1 | 80/80 | 80/80 | 22821 → 22579 | 7.623 → 12.787 |
| previous_holdout_large_v1 | 16/16 | 16/16 | 157944 → 157440 | 81.428 → 200.952 |

## Area improvement per official case

| Case | Baseline Area | Round 6.0 Area | Saving | Delay baseline → new |
|---|---:|---:|---:|---:|
| case_001.txt | 61952 | 61950 | 2 | 62 → 62 |
| case_002.txt | 18897 | 18897 | 0 | 60 → 60 |
| case_003.txt | 24251 | 24235 | 16 | 56 → 56 |
| case_004.txt | 4550 | 4550 | 0 | 47 → 47 |
| case_005.txt | 700 | 700 | 0 | 31 → 31 |
| case_006.txt | 5962 | 5960 | 2 | 46 → 46 |
| case_007.txt | 78042 | 78042 | 0 | 71 → 71 |
| case_008.txt | 8637 | 8637 | 0 | 50 → 50 |
| case_009.txt | 14584 | 14584 | 0 | 46 → 46 |
| case_010.txt | 4712 | 4574 | 138 | 32 → 32 |
| case_011.txt | 464 | 464 | 0 | 33 → 33 |
| case_012.txt | 5359 | 5289 | 70 | 25 → 25 |
| case_013.txt | 11252 | 11248 | 4 | 60 → 60 |
| case_014.txt | 11662 | 11650 | 12 | 61 → 61 |
| case_015.txt | 33374 | 33374 | 0 | 64 → 64 |
| case_016.txt | 2149 | 2149 | 0 | 40 → 40 |
| case_017.txt | 440 | 440 | 0 | 22 → 22 |
| case_018.txt | 1232 | 1232 | 0 | 31 → 31 |
| case_019.txt | 5319 | 5289 | 30 | 57 → 57 |
| case_020.txt | 766 | 766 | 0 | 30 → 30 |
| case_021.txt | 28104 | 28104 | 0 | 60 → 60 |
| case_022.txt | 1320 | 1320 | 0 | 31 → 31 |
| case_023.txt | 125 | 125 | 0 | 22 → 22 |
| case_024.txt | 124475 | 124475 | 0 | 70 → 70 |
| case_025.txt | 80686 | 80684 | 2 | 60 → 60 |

## Interpretation

This prototype is a bounded post-mapping Cut Rewriter. It is not an optimal 4-input Boolean synthesizer.
It ranks local candidates using a conservative private-cone cost estimate and makes its final decision using complete, exact Gate Area and critical-path Delay.
Runtime is a cost of the synthesis procedure, not the circuit delay. If the extra Area reduction is not worth the time, keep the frozen Round 5.1 executable.
The new 40-case holdout functions were fixed before formal performance measurements; their input-line encoding was corrected without altering the Boolean functions.
The prior 96-case suite is reused from Round 5.1; neither collection guarantees generalization to hidden Stage 2.

## Independent evidence

See `benchmark/independent_verification.log` and the CSVs/logs in this local run.

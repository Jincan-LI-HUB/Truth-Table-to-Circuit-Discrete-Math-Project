# Round 6.1 — WSL Local Reproduction Report

## Two official paired runs

| Metric | Run 1: Reference | Run 1: Round 6.1 | Run 2: Reference | Run 2: Round 6.1 |
|---|---:|---:|---:|---:|
| Functional PASS | 25 | 25 | 25 | 25 |
| Target Met | 25 | 25 | 25 | 25 |
| Area Sum | 529014 | 528854 | 529014 | 528839 |
| Median Runtime (ms) | 54.572 | 80.731 | 50.224 | 74.083 |
| Sum Runtime (ms) | 7371.348 | 6154.935 | 5182.265 | 5875.605 |

Average of pairwise median runtimes: 52.398 ms → 77.407 ms (+47.73%).
Pass/Target status is distinct from Area and synthesis runtime. Median runtime is not an amortized estimate.
Both programs are rebuilt under the same compiler/environment. The order of the two executable modes is reversed in the second paired run.
Candidate cutoff is based on wall-clock time, hence two successful runs can emit different equivalent netlists.

## New holdouts (not used for algorithm or threshold selection)

| Distribution | PASS | Target | Reference Area | R6.1 Area | Reference Median | R6.1 Median |
|---|---:|---:|---:|---:|---:|---:|
| holdout_round61_fresh_v1 | 40/40 | 40/40 | 11186 | 10858 | 7.852 | 10.762 |
| holdout_round61_large_v1 | 8/8 | 8/8 | 67275 | 67047 | 68.093 | 94.327 |

## Per-case official comparison

| Case | Reference Area | R6.1 Area | Saving | Delay baseline → R6.1 |
|---|---:|---:|---:|---:|
| case_001.txt | 61952 | 61950 | 2 | 62 → 62 |
| case_002.txt | 18897 | 18897 | 0 | 60 → 60 |
| case_003.txt | 24251 | 24235 | 16 | 56 → 56 |
| case_004.txt | 4550 | 4550 | 0 | 47 → 47 |
| case_005.txt | 700 | 698 | 2 | 31 → 31 |
| case_006.txt | 5962 | 5960 | 2 | 46 → 46 |
| case_007.txt | 78042 | 78042 | 0 | 71 → 71 |
| case_008.txt | 8637 | 8637 | 0 | 50 → 50 |
| case_009.txt | 14584 | 14584 | 0 | 46 → 46 |
| case_010.txt | 4712 | 4661 | 51 | 32 → 32 |
| case_011.txt | 464 | 464 | 0 | 33 → 33 |
| case_012.txt | 5359 | 5309 | 50 | 25 → 25 |
| case_013.txt | 11252 | 11248 | 4 | 60 → 60 |
| case_014.txt | 11662 | 11650 | 12 | 61 → 61 |
| case_015.txt | 33374 | 33374 | 0 | 64 → 64 |
| case_016.txt | 2149 | 2149 | 0 | 40 → 40 |
| case_017.txt | 440 | 440 | 0 | 22 → 22 |
| case_018.txt | 1232 | 1232 | 0 | 31 → 31 |
| case_019.txt | 5319 | 5299 | 20 | 57 → 57 |
| case_020.txt | 766 | 766 | 0 | 30 → 30 |
| case_021.txt | 28104 | 28104 | 0 | 60 → 60 |
| case_022.txt | 1320 | 1320 | 0 | 31 → 31 |
| case_023.txt | 125 | 124 | 1 | 22 → 22 |
| case_024.txt | 124475 | 124475 | 0 | 70 → 70 |
| case_025.txt | 80686 | 80686 | 0 | 60 → 60 |

## Interpretation / stop condition

Freeze Round 5.1 as the default baseline. Round 6.1 is a bounded optional area-improvement branch. A default switch is justified only if an externally known scoring formula makes its small area improvement worthwhile.
Correctness is supported by the official evaluator and by independent exhaustive/sampled netlist simulation. A finite synthetic holdout cannot prove performance on unknown Stage 2.
This is a heuristic local rewriting engine, not exhaustive 4-input technology mapping, and its Area improvement is not guaranteed on every benchmark seed.
See `benchmark/independent_verification.log`, `cases_sha256.txt`, `holdout_cases_sha256.txt`, `environment.txt`, saved outputs and the raw CSV files.

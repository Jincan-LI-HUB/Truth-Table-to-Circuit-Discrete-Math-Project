# Round 6.1 — Reference Experiment and Go/No-Go Review

Date: 2026-11-11. All figures in this document are from the current Linux experiment, **not** from the user's WSL. Official statuses are produced by the supplied evaluator; independent simulation checks are reported separately.

## 1. Predefined decision rule

A conditional research **GO** requires all 25 published cases to PASS and meet timing, a strict positive Area improvement over Round 5.1, extra holdout function validity, and a median synthesis runtime no more than **1.3 times Round 5.1** on the paired platform. The final default solver should change only if the course's actual scoring formula rewards the area gain enough to justify the runtime penalty. Otherwise retain Round 5.1.

## 2. Public Stage 1: two matched runs

| Run | Version | PASS | Target met | Area sum | Median runtime (ms) |
|---|---|---:|---:|---:|---:|
| 1 | Round 5.1 reference | 25/25 | 25/25 | 529,014 | 80.635 |
| 1 | Round 6.1 | 25/25 | 25/25 | **528,864** | 99.740 |
| 2 | Round 5.1 reference | 25/25 | 25/25 | 529,014 | 77.324 |
| 2 | Round 6.1 | 25/25 | 25/25 | **528,886** | 100.979 |

Round 6.1 saves 150 / 128 area units; the average of the two median runtime ratios is approximately 1.27, inside the threshold of 1.3. Area is reduced in a minority of cases; most outputs are unchanged. These are measured, not guaranteed, runtime statistics.

### Run-to-run differences

The source includes wall-clock budget checks inherited from earlier rounds. It follows that the number of completed portfolio candidates and the final choice can depend on host scheduling. A difference of 22 Area units across two Run 6.1 replicates does **not** by itself indicate a function or timing error: all were officially evaluated and both runs remained within target. Exact output determinism is not promised for a time-limited search.

## 3. New independent holdouts (not used for threshold selection)

| Set | Cases | PASS | Target | Area before | Area after | Saving | Median runtime before → after |
|---|---:|---:|---:|---:|---:|---:|---:|
| Fresh mixed seed `661061` | 40 | 40/40 | 40/40 | 11,186 | 10,858 | 328 (2.93%) | 6.978 → 10.368 ms |
| Fresh large seed `0x615A7E11` | 8 | 8/8 | 8/8 | 67,275 | 67,098 | 177 (0.26%) | 97.032 → 115.847 ms |

21 of the 48 new cases reduced Area; none showed an Area increase in this one evaluation. Small-case runtime increased more sharply in percentage terms due to the fixed cost of starting a cut search. These tests give evidence beyond the 25 public cases but cannot predict hidden-case distributions.

All 73 Stage 1 and fresh-holdout Round 6.1 output netlists passed an independent area/delay/function check: 55 exhaustive, 18 deterministic sampled. The official evaluator independently passed all 73. An *independent sample* for larger inputs is not an exhaustive correctness proof; the formal equivalence of the rewriting transformations supplies the mathematical argument.

## 4. Cut-time budget ablation — development evidence

The new cover cache and structural cut ordering were first examined with a 45 ms cap. On Stage 1, that exploratory run obtained 25/25 PASS and an Area sum of 528,750, but median runtime was 121.285 ms; it failed the 1.3x runtime threshold. This public result contributed to selecting the 25 ms engineering cap, and must not be cited as a blind evaluation.

We also ran the **standalone postprocessor** on the previously frozen 16-case large-development set using the same saved Round 5.1 input netlists. These are local postprocessing statistics, not the complete evaluator runtime:

| Cut budget | Development Area saved | Accepted cases / 16 | Median postprocessor wall time |
|---|---:|---:|---:|
| 25 ms | 358 | 10 | 31.66 ms |
| 35 ms | 408 | 12 | 40.89 ms |
| 45 ms | 501 | 12 | 52.38 ms |

The older Round 6.0 40-case development set had identical postprocessor Area results across these three budgets; it does not support generalizing the larger-case trend. Full Stage 1 syntheses include variable-order portfolio search, gate mapping and other postprocessing, and must not be equated to these isolated wall times.

## 5. Comparison against the Round 6.0 prototype

The previously reported Round 6.0 WSL result achieved Area 528,738 / 528,744 with medians 114.610 / 116.351 ms, while the frozen Round 5.1 counterpart was about 51–53 ms. The current **container** 6.1 figures cannot be compared directly to those WSL milliseconds. The new WSL runner includes a simultaneous Round 5.1 control and alternated pair order specifically to establish a fair local comparison. A separate frozen Round 6.0 binary is provided for optional extra study.

## 6. Decision and limitations

**Research decision: Conditional GO, default solver remains Round 5.1.** Cut-based rewriting demonstrably finds valid improvements on new functions, and the 25 ms cap keeps the public-case median within the predetermined 1.3x threshold. But the absolute public Area improvement is small (0.024–0.028%) and the runtime penalty remains 23–31% depending on replicate. The score-oriented adoption decision should be made only after seeing the official scoring objective and the user's WSL paired measurements. Do not make per-case budget exceptions or repeatedly tune toward the 25 public functions.

Recommending no further 6.2 search enlargement unless a scoring analysis shows high value from area, or another genuinely structural efficiency breakthrough appears. Detailed evidence is located under `results/official`, `results/holdout`, `results/independent_verification.json`, and `results/development_budget_ablation_large.json`.

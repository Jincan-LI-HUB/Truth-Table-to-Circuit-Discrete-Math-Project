# Round 6.0 — Reference Experiment and Go/No-Go Review

**Tested version:** the source hashes in `results/frozen_algorithm_and_holdout_sha256.txt`; **control:** frozen Round 5.1 source compiled with identical flags. The experiment used the official evaluator and an independent netlist simulator. Times below are from this Linux container, not the user's WSL2.

## Stage 1 — Public 25 cases

| Metric | Round 5.1 control | Round 6.0 prototype |
|---|---:|---:|
| Official functional PASS | 25/25 | **25/25** |
| Target Delay Met | 25/25 | **25/25** |
| Area Sum | 529,014 | **528,825** |
| Area saving | — | **189 (0.0357%)** |
| Median synthesis runtime | 78.726 ms | **138.390 ms** |
| Sum synthesis runtime | 7,913.362 ms | **9,897.922 ms** |
| Independent circuit verification | preexisting reference | **25/25** |

The 25 reference cases were run in one official evaluator batch. The Round 6.0 result was completed as a **23-case prefix plus two isolated single-case evaluator runs**, after the first all-cases batch was interrupted by the execution environment. The two isolated cases (024 and 025) are independently valid official `PASS` results. `results/official_round60_complete.csv` combines all 25; retain original logs and the two one-case CSVs. The standalone Round 6.0 program also independently completed the large case 024 in ~2.68 s, supporting the interpretation that the earlier interruption was not an algorithmic hang.

Area strictly decreased in **9 of 25 cases**, stayed equal in 16, and never increased in this trial. Most gains were small. `case_010` saved 85; `case_012` saved 44; `case_019` saved 22; other gains ranged 2–16. This is a **modest improvement with a substantial runtime penalty**. Avoid extrapolating the exact percentage to other machines or runs; wall-clock-budget-based selection can also cause nondeterministic candidate completion.

## New, separately frozen 40-case holdout

Generation seed `602106`; source and SHA-256 per-case manifest are supplied. Five functional families rotate across cases: affine/parity, MUX-like, thresholds, sparse DNF, and random shallow shared-DAG functions. Number of variables 8–13, 3–5 outputs. All have an ample synthetic target-delay budget.

| Metric | Round 5.1 | Round 6.0 |
|---|---:|---:|
| Official PASS | 40/40 | 40/40 |
| Target Delay | 40/40 | 40/40 |
| Area Sum | 9,709 | **9,496** |
| Area saving | — | **213 (2.19%)** |
| Median Runtime | 6.897 ms | **14.013 ms** |
| Independent verification | — | **40/40 exhaustive** |

About 20/40 cases showed strict Area improvement, the rest were unchanged. Unlike the public benchmark, the proportional Area benefit on this group was materially larger, suggesting that the rewriting does discover general local Boolean opportunities; it does **not** indicate that the hidden competition has the same distribution.

## Reused Round 5.1 holdouts (96 cases)

These test sets predate the Round 6.0 source and were not used to select its search budget or rewrite thresholds.

| Group | Correctness / Target | Area before | Area after | Saving | Median time before → after |
|---|---:|---:|---:|---:|---:|
| 80 mixed functions | 80/80 | 22,821 | **22,579** | 242 | 4.764 → 11.147 ms |
| 16 larger structured | 16/16 | 157,944 | **157,530** | 414 | 96.440 → 213.727 ms |

Independent netlist simulation confirmed all 96. Of these, 74 were verified exhaustively and 22 by deterministic sampling (the sampling procedure is not an exhaustive mathematical guarantee).

## Conclusion and decision

The precise prototype hypothesis **is supported**: bounded 4-feasible-cut refactoring discovers strict Area improvements across three input groups while preserving functionality and checked timing. The *practical acceptance hypothesis* is **not supported yet**: the small gain on the 25 public cases comes with a material Runtime increase (public median roughly +76%).

**Recommendation: do not promote Round 6.0 to the default submission.** Retain Round 5.1 as the frozen efficiency baseline, and archive Round 6.0 as a positive algorithmic / negative efficiency ablation. Do not automatically enter Round 6.1 by increasing `k` or adding more candidates; any Round 6.1 should focus first on candidate prioritization and shared-gate-aware incremental evaluation, with an independent non-tuning holdout.

## Reproducibility

- Exact sources in `src/`; compilation flags in `Makefile`.
- Stage 1 reference and Round 6.0 CSVs and logs in `results/`.
- 40-case new synthetic holdout plus prior 96 holdouts in `tests/`.
- Offline, no-sudo WSL runner `run_round6_0_local.sh` produces a two-pair benchmark and `local_runs/YYYYMMDD_HHMMSS_Round6.0/report_ready/` folder.
- Frozen algorithm / test hashes in `results/frozen_algorithm_and_holdout_sha256.txt`.
- All measured Runtime figures must be regarded as environment-dependent.

## Follow-up paired official experiment (same source; no retuning)

A second container experiment ran Round 5.1 and Round 6.0 **twice each**, alternating their evaluation order. Both versions scored **25/25 PASS** and **25/25 target met** on both passes:

| Paired pass | Round 5.1 Area | Round 6.0 Area | Round 5.1 Median (ms) | Round 6.0 Median (ms) |
|---|---:|---:|---:|---:|
| 1 | 529,014 | 528,822 | 77.822 | 134.384 |
| 2 | 529,014 | 528,805 | 74.006 | 135.084 |

The slightly different Round 6.0 Area sums (**−192** and **−209** from the common reference) are attributable to elapsed-time-based candidate completion in the frozen synthesizer; neither is an area regression. These paired data supersede the initial single-run time estimate for decision-making but do **not** invalidate the initial observed 528,825 result. A saved `local_runs/` record includes the complete paired CSVs.

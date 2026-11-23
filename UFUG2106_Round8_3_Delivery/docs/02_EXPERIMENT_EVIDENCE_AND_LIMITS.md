# Round 8.3 — Evidence, Ablation, Negative Results

## 1. Local public Stage2 exhaustive verification

All 25 real Stage2 data files were extracted from the user's previously uploaded archive and read directly; the unmodified data are NOT repackaged. Round8.3 Stable Dual outputs were compared against the original truth tables for all `2^n` assignments via an independent C++ bit-parallel verifier. Result: **25/25 PASS**, all satisfy Target Delay, area total **500,072**, delay sum **1,169**, no cut-level wall-hit events in that particular run. A same-container R8.2.1 Dual Area reference produced 25/25 PASS, area **499,793**, with the **same delay for every case**. Relative to that reference, the stable 900-root configuration was 279 area units worse, despite its intended stability benefit.

The positive case_005 delta is 107754 -> 106771 (Area -983), whereas case_003 is 16359 -> 17283 (Area +924). Other, smaller differences are listed in `evidence/stage2_25_exact_local.csv` (and the reference sum is recorded here). These are single local runs, NOT official evaluator measurements and NOT directly comparable to prior WSL runs because time-based parent candidates can vary.

## 2. Root cap ablation (local)

Direct tests of case_003 show 600/900/1100/1250 roots yield areas 18034/17283/16633/16184 at delay 65, with no wall hit in that run. In case_005, the same requested budgets yield 109021/106771/106168/105070 at delay 67, but the 1100/1250 variants experienced watchdog interruption and hence are NOT guaranteed to reach that exact number of completed roots. The 900-root choice is deliberately conservative; the last few hundred roots can clearly contain valuable improvements.

This demonstrates a trade-off, not a mathematical monotonicity theorem: a larger, fixed quota can alter the search trajectory, and a time-guarded run can produce a different realization depending on the schedule. See `evidence/budget_matrix_3_cases.csv`.

## 3. Repeated executions

Four public probes (`case_003`,`case_005`,`case_017`,`case_021`), three runs per configuration, two configurations (default and 1100), generated 24 independent outputs. In the default group, each case had one unique output SHA256 and no R83 wall hit. In the 1100 group, case_017 produced two distinct hashes and one watchdog hit. No claim of universal repeatability follows from 3 runs. See `evidence/repeat_stability_24_runs.csv`.

## 4. Already-used synthetic cases

The frozen 24 structured holdout tests from Round8.2 were **re-used** as a regression set; both comparator and R8.3 synthesized 24/24 exactly equivalent outputs, aggregate area 13,897 and delay sum 613. This is not new blind testing. See `evidence/structured_holdout_24.csv`.

## 5. Discarded experiments and what they taught

Early code set `UFUG_R82_POLICY=off` to switch in R83. The inherited policy defaults thereby activated R8.0 Iterative Rewriting and R8.1 Branch Rewriting, invalidating the supposed independent R83 results and producing unexpectedly large apparent improvements. All such results were removed from conclusions. The new source forces R8.0, R8.1 and R8.2 inactive whenever R83 is active, even if conflicting environment variables are present, and includes an explicit isolation test.

The 1100-root candidate sometimes still reaches the wall watchdog, so "deterministic roots" must not be presented as fully deterministic wall-time behavior. Similarly, the larger fixed quota does not prove better final score under unknown grading weights.

## 6. What we still cannot claim

- No course evaluator results in the current container: WSL official testing remains necessary.
- No verified hidden-test distribution or optimality certificate.
- Round8.3 does not eliminate upstream time-limited candidate-selection variability.
- The course's positive-RAM evaluator discrepancy remains an **unresolved separate problem**, originally raised by a teammate on GitHub Issue #2, not a ruling by instructors.
- Runtime ratios should be measured on the same WSL evaluator, not extrapolated from isolated local process wall time.

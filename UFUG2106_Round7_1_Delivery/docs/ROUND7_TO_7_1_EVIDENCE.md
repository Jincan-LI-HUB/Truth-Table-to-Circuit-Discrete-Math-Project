# Round 7 → Round 7.1: Evidence, Diagnosis, and Decision Record

**Recorded on:** 2026-11-21 (Asia/Shanghai)  
**Project:** UFUG2106 Truth Table to Circuit  
**Status:** Completed analysis of user's Round 7 experiment; Round 7.1 has not yet been evaluated on the user's official evaluator.  
**Data provenance:** `results.rar` (run directory `20261121_140841` and diagnostic directory `20261121_140830`, supplied by project member); previous `round51_stage1.csv` and `round51_stage2.csv`.

## E1. Scope and integrity of the evidence

Two independently relevant experiment types appear in the archive:

1. **Official runs:** The instructor-provided evaluator launches the synthesizer and enforces per-case runtime limits. The CSV status `PASS` is definitive for these observations; a failed case does not have a valid area or delay score.
2. **Direct profiling:** The synthesizer runs without the official 100 ms limit with `UFUG_ROUND5_PROFILE=1`. Its runtime includes logging and may differ from the evaluator's runtime; use it to attribute costs and observe candidate count, **not to claim official PASS**.

There are two official repetitions per variant and stage. This is meaningful evidence, but not a statistical guarantee of low timeout probability. Benchmark order was reversed on repetition 2 to mitigate order bias. Full source paths and historical frozen baseline are described in the parent `README.md`.

## E2. Official Round 7 ablation matrix

| Implementation | Stage 1, run 1 | Stage 1, run 2 | Stage 2, run 1 | Stage 2, run 2 |
|---|---:|---:|---:|---:|
| Round 5.1 | 25/25 | 25/25 | 24/25 | 25/25 |
| Round 7 default (both fast kernels) | 25/25 | 25/25 | 24/25 | 24/25 |
| Round 7 old merge + fast greedy | 25/25 | 25/25 | **25/25** | **25/25** |
| Round 7 fast merge + old greedy | 25/25 | 25/25 | **25/25** | **25/25** |
| Round 7 old merge + old greedy | 25/25 | 25/25 | **25/25** | **25/25** |

All Stage 1 variants reported aggregate area **529,014** in both runs. The Round 7 variants that passed all of Stage 2 reported aggregate area **508,535**; when `case_016` failed, the partial sum was **506,754**. Their difference, **1,781**, is exactly the missing area of the failed case and **not an optimization**.

The jointly successful Stage 1 and Stage 2 cases had identical reported area and delay in this archive. Equality of area/delay is not proof of netlist identity, since multiple implementations may share those metrics. Direct `case_016` netlist SHA-256 measurements were identical in the 15 saved diagnostic runs.

## E3. The key outlier, `case_016`

Input: \(n=9\), \(m=8\), \(2^n=512\) truth-table rows. All eight output functions depend on all nine input variables. AND2 area/delay = 2/2, OR2 = 8/3, NOT = 1/1; target delay = 42, declared runtime limit = **100 ms**.

The selected, functionally verified output in diagnostic runs: **Area 1,781; Delay 36**. Its live gate counts: 661 AND2, 459 NOT, 0 OR2 (area check: \(661\cdot 2+459\cdot 1=1781\)). The selected implementation is feasible with six units of timing slack, \(42-36=6\).

**Official case_016 timings** (successful runs only):

| Variant | Run 1 (ms) | Run 2 (ms) | Stability evidence |
|---|---:|---:|---|
| Round 5.1 | FAIL (TIME_LIMIT) | 97.558 | Borderline |
| R7 default | FAIL | FAIL | Consistently unsuccessful |
| R7 old merge + fast greedy | **86.125** | **82.801** | Both PASS |
| R7 fast merge + old greedy | **85.019** | **83.682** | Both PASS |
| R7 old merge + old greedy | **98.050** | **99.821** | Both PASS but almost no reserve |

A prior paired experiment (`20261121_135745`) also recorded one Round 5.1 successful run at 98.409 ms and another failure; the observed instability precedes Round 7.1.

## E4. Primitive operations and direct profiling

The saved diagnostic logs show:

| Operation | Unoptimized | Accelerated | Count reduction |
|---|---:|---:|---:|
| Merge candidate probes | 58,249,307 | 444,241 | approximately 131× fewer probes |
| Greedy cover count probes | 37,556,736 | 586,824 | approximately 64× fewer probes |

Selected direct run 1 (not official):

| Configuration | Merge time | Greedy time | Completed candidates | Direct elapsed |
|---|---:|---:|---:|---:|
| R7 default | 9.316 ms | 1.136 ms | **8** | 119.547 ms |
| Old merge + fast greedy | 26.471 ms | 1.215 ms | 6 | 91.423 ms |
| Fast merge + old greedy | 9.480 ms | 18.475 ms | 6 | 89.861 ms |
| Old merge + old greedy | 25.017 ms | 17.865 ms | 6 | 105.057 ms |

The first **five primary** candidates in the default trace cost approximately 14.464, 1.456, 0.767, 1.882, and 1.727 ms respectively. The chosen final candidate was primary index **2**, with area 1,781 and delay 36. Nevertheless, default R7 completed **eight** candidates, versus **six** in variants with one slower cover kernel. Therefore faster initial computations enabled additional lower-priority legacy work without improving the final selected circuit.

**Interpretation:** The raw micro-optimization is real, but more total portfolio work can erase its savings. The source confirms that the old 72% budget guard is evaluated **before** starting legacy candidates and that legacy synthesis has no cooperative per-candidate abort. The instrumented logs do not measure exact time for each legacy candidate; attributing every extra millisecond to one specific legacy method would exceed the evidence. This motivates candidate-by-candidate trace instrumentation in R7.1.

## E5. What is established, inferred, and untested?

**Established by measurements:** (i) the two cover kernels reduce their own operation counts; (ii) the old search portfolio is budget-sensitive; (iii) default R7 failed case_016 twice, while one-fast-kernel ablations passed twice; (iv) all fifteen independently verified diagnostic netlists match the truth table, with identical fingerprints; (v) area/delay on common PASS cases remained unchanged.

**Supported causal hypothesis:** Saved time permits extra legacy candidates and/or postprocessing, which consumes the narrow 100 ms budget. This mechanism is strongly supported by candidate counts, source guards, and equal final outputs, but the precise per-legacy-candidate cost remains to be measured.

**Not yet established:** Stability of any 7.1 candidate; 50/50 official PASS for 7.1; no Stage 1 regressions after changing candidate dispatch; effect on the hidden dataset; any official grade improvement; whether `case_016` is intrinsically difficult to synthesize in other representations.

## E6. Decision and objective for Round 7.1

1. Retain the verified exact-cover acceleration from R7, rather than reverting the mathematics.
2. Keep the primary portfolio and incumbent rank unchanged.
3. For *short declared time budgets*, stop optional legacy search when an incumbent satisfying the target delay exists; this is a general input-budget policy, **not case-number lookup**.
4. Add an ablation mode that restores R7's old dispatch behavior, permitting paired isolation of the change.
5. Record each primary and legacy candidate's elapsed time and improvement status in direct profiling; keep trace logging disabled during official timing runs.
6. Keep frozen Stage 1 results and all current source fingerprints available for paper drafting.

## E7. Paper-ready narrative (draft, not a result claim)

> The initial Round 7 reduced the computational complexity of cube merging and greedy covering while preserving the truth-table covering decisions. However, profiling revealed an interaction with the existing deadline-blind candidate portfolio: faster covers allowed additional low-value synthesis attempts, causing intermittent deadline violations on a tight-budget benchmark. Consequently, Round 7.1 investigates budget-aware candidate dispatch as an orthogonal optimization to Boolean minimization. Its correctness is inherited from the unchanged synthesis transformations and incumbent selection; its performance benefit must be established through paired official evaluations and held-out tests.

**Traceability:** The underlying official CSVs and representative direct traces are bundled under `evidence/round7_user_run/`. Do not substitute this draft for the still-uncollected R7.1 benchmark results.

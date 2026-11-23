# UFUG2106 — Round 8.0 Official WSL Audit and Research Decision

**Experiment:** `Round8_Prototype_Feedback_20261121_154508_384189.zip` (user's own WSL evaluator runs, 2026-11-21).  
**Frozen comparator:** Round 7.2. **Prototype:** Round 8.0 Structural Rewriting.  
**Scope:** 2 runs × 2 stages × 7 variants × 25 cases = 700 evaluator case-results.  
**Epistemic status:** Measured results are clearly distinguished from hypotheses; this is not a proof of global optimality or performance on hidden cases.

## A. Primary outcome

All seven configurations achieve 25/25 PASS and 25/25 target met on each stage in both runs. Of 50 public cases, only Stage 2 `case_021` changes weighted area or delay under `r8_iterate`. Other 49 cases have unchanged area/delay.

| Configuration | Stage 1 area | Stage 2 area | Case 021 area / delay |
|---|---:|---:|---:|
| `r72` | 529,014 | 508,535 | 22,590 / 69 |
| `r8_off` | 529,014 | 508,535 | 22,590 / 69 |
| `r8_factor` | 529,014 | 508,535 | 22,590 / 69 |
| `r8_reuse` | 529,014 | 508,523 | 22,578 / 70 |
| `r8_strict` | 529,014 | 508,535 | 22,590 / 69 |
| `r8_all` | 529,014 | 508,523 | 22,578 / 70 |
| `r8_iterate` | 529,014 | 508,480 | 22,535 / 70 |

The overall **area sum** decreases from 1,037,549 to 1,037,494 (55 units, or approximately **0.00530%**). The improved instance decreases by 55/22,590 = **0.2435%**, while its delay **increases by one** and just meets its target of 70. Therefore the candidate is **not Pareto-dominant** over Round 7.2 in Area–Delay space. The course's exact grading formula has not been established.

## B. Mechanism: iterative, noncommutative search

The `local_results/diagnostics/stage2_case_021_r8_iterate.log` records the following accepted-pass trajectory:

| Accepted step | Selected candidate | Area | Delay | Marginal area gain |
|---|---|---:|---:|---:|
| Baseline | Round 7.2 | 22,590 | 69 | — |
| 1 | `reuse` | 22,578 | 70 | 12 |
| 2 | `reuse` (rather than an available factoring candidate at 22,555) | 22,543 | 70 | 35 |
| 3 | `factor` | 22,539 | 70 | 4 |
| 4 | `reuse` | 22,535 | 70 | 4 |
| 5 | no improving candidate | 22,535 | 70 | 0 |

**Substantive algorithmic insight:** An algebraic transform can change the availability and cost of subsequent transforms. In this specific experiment, factoring finds no improving candidate in the original baseline, yet a later factoring pass becomes useful after accepted reuse steps. These results support an *order/interaction hypothesis*; they do not demonstrate that the same synergy generalizes to other circuit families.

The log's `reused=165` or `factored=6` refers to local/rebuilt-node counts in *tentative candidates*, **not** to 165 or six independently accepted full-graph improvements. Candidate acceptance uses live-DAG full metrics. Do not mistake tentative rewrite counts for successful global optimizations.

## C. Netlist-level evidence

The archived full output netlists confirm the following:

| Gate type | `r72` | `r8_iterate` | Difference |
|---|---:|---:|---:|
| AND2 | 5,391 | 5,325 | −66 |
| OR2 | 6,401 | 6,544 | +143 |
| NOT | 16 | 16 | 0 |
| Total gates | 11,808 | 11,885 | +77 |

The case's weights are `AND2 = 3, OR2 = 1, NOT = 1`, giving:

\[
\Delta A = (-66)\cdot 3 + 143\cdot 1 + 0\cdot 1 = -55.
\]

**Important qualification:** The fact that total gate count increases while weighted area decreases is a simple arithmetic possibility, *even without DAG sharing*. The noteworthy result is an actual implementation that discovers an equivalent, feasible multi-output circuit using preexisting divisors and further interactions. Aggregate gate counts alone do not isolate how much of the 55-unit saving was specifically caused by inter-output sharing; that needs an additional counterfactual ablation (disable or restrict global divisor reuse while maintaining identical timing and rewrite budgets).

## D. Runtime: no robust overall improvement demonstrated

Official evaluator runtimes on the user's WSL machine:

| Stage | Variant | Run 1 median ms | Run 2 median ms | Runtime geometric ratio R8/R7.2 (run 1 / run 2) |
|---|---|---:|---:|---:|
| 1 | `r72` | 46.999 | 50.220 | 1 / 1 |
| 1 | `r8_iterate` | 51.403 | 51.529 | 0.9711 / 1.0289 |
| 2 | `r72` | 32.688 | 35.190 | 1 / 1 |
| 2 | `r8_iterate` | 32.131 | 32.703 | 1.0431 / 0.9453 |

`case_021` runtime: baseline **198.921 / 251.721 ms**; R8 Iterate **228.311 / 249.370 ms** (runs 1 / 2). Effects are inconsistent across runs and have very different magnitude from the tiny overall area gain. No reliable speed improvement can be claimed from these two paired runs. The target input for `case_021` allows 100,000 ms, so this prototype still has a large local resource margin, but small-budget hidden instances require separate stress testing.

`case_016` retains Area 1,781 / Delay 36 with `r8_iterate` runtimes **26.297 / 26.920 ms**, well under its 100 ms limit in these observations. The integrated R8 postprocessing is gated for short input limits, however; this does not prove the rewrite engine itself can run safely on arbitrary 100 ms cases.

## E. What is and is not proved

**Confirmed:** (i) official PASS and target met for all 50 cases under all configurations in two runs; (ii) R8 Iterate's one-case area gain and delay trade-off, independently supported by saved netlists; (iii) specific multi-pass alternation of reuse and factoring; (iv) the narrow coverage (1/50 public cases).

**Not established:** (i) general advantage over the R7.2 baseline; (ii) general superiority of reuse, factoring, or any ABC-inspired family; (iii) that additional gates *require* DAG sharing to save area; (iv) that no additional improvements exist on the other 49 functions; (v) robustness on hidden cases; (vi) official grade improvement under unknown grading formula.

**Structural limitations observed in `r8_structural.hpp`:** The optimizer matches direct two-level identities and a narrow divisor pattern keyed to existing interned nodes. It does not enumerate arbitrary k-feasible cuts, does not perform complete SAT resubstitution, does not globally optimize multiple polarities jointly, and accepts only completed lexicographically better full-circuit solutions under the chosen area-first ranking. These conditions lead to a small *search neighborhood*, not necessarily to absence of profitable alternatives.

## F. Next-round research hypotheses and recommended tests

1. **Candidate availability vs optimization utility:** For each netlist record (a) candidate cuts/windows seen, (b) valid Boolean alternatives, (c) timing-feasible alternatives, (d) globally area-improving alternatives, and (e) cost to reach each stage. This separates search-space coverage from acceptance policy. For the 49 unchanged cases, don't infer optimality from zero accepted candidates.
2. **Technology-aware 3/4-input resynthesis:** Enumerate exact local truth tables at feasible cuts; obtain a *portfolio* of NAND/AND/OR/NOT-polarity realizations, mapped to current per-case gate costs, input arrival times, and sharing. Use a library or enumerator rather than only syntactic pattern recognition. Validate every replacement by local exact equivalence and final full-DAG metrics.
3. **DAG-wide divisor opportunities:** Build candidate divisors from multiple output cones, and test windows where factoring is not syntactically adjacent. Distinguish inter-output reuse from within-output sharing using counterfactuals. Any bit-parallel signature is a filter, not by itself a proof of functional equivalence on larger input spaces.
4. **Bounded structural choice:** Compare beam widths 1, 3, and 5 using equal **total** CPU budgets, not merely equal pass counts; retain several non-dominated area/delay implementations and structural diversity. Keep the frozen R7.2 incumbent for safe fallback. Avoid a false comparison in which one method receives far more time.
5. **Method interaction design:** Compare factor-only, reuse-only, factor→reuse, reuse→factor, and alternating passes on both public and frozen generated holdouts. Report not just success cases, but time spent per candidate and failure modes; freeze thresholds before seeing held-out outcomes.
6. **Score uncertainty:** Keep the 22,590/69 and 22,535/70 variants on a Pareto frontier until the course grading formula can justify choosing between them.

**Milestone decision:** Round 8.0 is a **valid research prototype** with a reproducible narrow optimization and a demonstrated interaction effect. Do **not** label it a generally better or final synthesizer. The next algorithm milestone should focus on broadening the equivalent-circuit candidate space and measuring why previously tested cases have no accepted improvement, rather than tuning the five-pass count on the sole successful public case.

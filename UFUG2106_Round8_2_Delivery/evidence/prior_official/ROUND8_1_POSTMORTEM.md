# Round 8.1 — 2026-11-21 Official Feedback Postmortem

**Evidence source:** `Round8.1_Feedback_20261121_161108_240427.zip`; SHA-256 `62e4ad259f293ce4f36ce57908f8591ff2410aaa053d2bb3a03ff6ae6a4a28ef`.  
**Observation unit:** 2 runs × 2 stages × 25 cases × 8 variants = **800 evaluator results**. All are PASS and all are Target Met.  
**Scope:** public benchmarks and same-host WSL2 evaluator, not hidden-case quality or official course grading formula.  
**Method:** inspect raw source CSVs, align by `(run,stage,case)`, compare each candidate to **the paired Round 7.2 run**; never infer area savings from failed-case omissions.

## 1. Executive decision

**Round 8.1 is validated as a structural synthesis research milestone, not as a confirmed score-optimal submission.**

- **Area exploration has materially improved:** `r81_reverse` saves 14,355 (run 1) / 14,263 (run 2) of 1,037,549 weighted-area units, with 30/50 improved cases and no per-case area regressions.
- **Delay and runtime remain real costs:** six area-improving cases have higher delay; all six produce worse *area×delay products*. Overall reverse geometric mean runtime factor is 2.514× / 2.455×. Area×delay geometric mean ratios are 1.01771 / 1.01759 (>1 means worse under this **hypothetical** proxy).
- **Strict policy is a small improvement at high runtime cost:** 303 / 305 total area savings, no delay regressions, runtime 2.53× / 2.39× baseline in pairwise geometric mean.
- **`r81_shannon` is a practical speed/quality contender:** 13,056 / 12,944 saved with runtime 1.57× / 1.51×, capturing over 90% of reverse's area savings in these runs but without claiming dominance in any actual grading formula.
- **Candidate choice is nontrivial:** `r81_all` is worse in total area than SOP, Shannon, and independent branch. This is consistent with structural path dependence under greedy mapping, not evidence that SOP and Shannon are mathematically incompatible.

## 2. Complete 50-case aggregate metrics

Baseline area total in each run: **1,037,549**. R8.0 iterative total: **1,037,494**.

| Variant | Run1 Area | Run2 Area | Mean saving | Cases improving (each run) | Delay regressions | Runtime geom. factor (Run1/Run2) |
|---|---:|---:|---:|---:|---:|---:|
| `r72` | 1,037,549 | 1,037,549 | 0.0 | 0/0 | 0/0 | 1.000× / 1.000× |
| `r80_iterate` | 1,037,494 | 1,037,494 | 55.0 | 1/1 | 1/1 | 1.020× / 0.998× |
| `r81_sop` | 1,025,327 | 1,025,346 | 12,212.5 | 27/27 | 5/5 | 1.640× / 1.642× |
| `r81_shannon` | 1,024,493 | 1,024,605 | 13,000.0 | 25/25 | 6/6 | 1.573× / 1.507× |
| `r81_all` | 1,028,076 | 1,027,964 | 9,529.0 | 30/30 | 6/6 | 1.755× / 1.676× |
| `r81_branch` | 1,023,716 | 1,024,350 | 13,516.0 | 30/30 | 6/6 | 2.583× / 2.483× |
| `r81_strict` | 1,037,246 | 1,037,244 | 304.0 | 25/25 | 0/0 | 2.528× / 2.395× |
| `r81_reverse` | 1,023,194 | 1,023,286 | 14,309.0 | 30/30 | 6/6 | 2.514× / 2.455× |

**Note:** The 800 official evaluator results are not 800 independent cases: they reuse 50 public cases under eight policies and two repetitions. Two repetitions are insufficient to make strong confidence-interval claims about performance stability.

## 3. Area–delay tradeoff diagnostic (`r81_reverse`, Run 1)

| Case | Area | Delay | Area saved | Increase in delay | ADP ratio | Max delay-vs-area log-weight ratio for preferring new candidate |
|---|---|---|---:|---:|---:|---:|
| stage1/case_010.txt | 4,712→3,065 | 32→61 | 1,647 | +29 | 1.2400 | 0.667 |
| stage1/case_012.txt | 5,359→3,778 | 25→40 | 1,581 | +15 | 1.1280 | 0.744 |
| stage2/case_003.txt | 19,494→15,207 | 39→63 | 4,287 | +24 | 1.2601 | 0.518 |
| stage2/case_005.txt | 112,221→106,770 | 40→57 | 5,451 | +17 | 1.3558 | 0.141 |
| stage2/case_021.txt | 22,590→22,534 | 69→70 | 56 | +1 | 1.0120 | 0.172 |
| stage2/case_023.txt | 2,986→1,968 | 25→40 | 1,018 | +15 | 1.0545 | 0.887 |

For sensitivity only, consider the hypothetical weighted-log objective

\[
J(G)=\alpha\log A(G)+\beta\log D(G),\quad \alpha,\beta\ge0.
\]

For a candidate that lowers area but raises delay, this proxy prefers it over the baseline only when

\[
\frac{\beta}{\alpha} < \frac{-\log(A_{\rm new}/A_{\rm old})}{\log(D_{\rm new}/D_{\rm old})}.
\]

**These are break-even sensitivities, NOT the course's official scoring rule.** Even when a case satisfies its target, increasing delay may still harm its actual score. Runtime must also be included when the official formula becomes available.

Six reverse tradeoff cases produce worse Area×Delay products (both repetitions). The overall Area×Delay geometric mean also worsens, despite area reductions in 30 cases. This demonstrates objective-function mismatch, not a universal defeat of cut resynthesis.

## 4. Distribution of area gains

- Run 1: top five cases account for **13,984/14,355 = 97.42%** of all area savings. The other 25 improved cases contribute only **371** units.
- Run 2: top five cases account for **13,892/14,263 = 97.40%** of all area savings. The other 25 improved cases contribute only **371** units.

The top five Run 1 contributors are Stage2/005, Stage2/003, Stage1/010, Stage1/012, and Stage2/023. All five have delay regressions. Thus the bulk of area savings is tied to spending timing slack; the many smaller strict improvements are real but contribute little total area.

**Example area-only oracle over already measured variants:** choose, *after the fact*, the smallest area for each case across all eight configurations. This gives: 
- Run 1: oracle measured-variant area = **1,023,154**, vs `r81_reverse` **1,023,194**, an extra **40** area units.
- Run 2: oracle measured-variant area = **1,023,283**, vs `r81_reverse` **1,023,286**, an extra **3** area units.

This oracle is *not* an implementable single-run synthesis result: it assumes prior knowledge of all variant outputs and ignores the time spent to obtain them. It does suggest that simply evaluating more of the *same* branch portfolio may yield diminishing returns compared with reducing overhead and improving timing-aware local mapping.

## 5. Repeatability and search-budget sensitivity

- Frozen `r72` and `r80_iterate` produce exactly the same per-case Area/Delay in both WSL runs.
- `r81_reverse`: **2/50 cases differ in area** across runs, and one differs in delay. Stage1/012: 3,778 → 3,684 area; Stage2/005: 106,770/57 → 106,956/58.
- `r81_branch`: 2/50 cases differ in area; Stage2/005 varies by 651 units. `r81_shannon` varies in two cases; `r81_strict` in one.
- Diagnostic profiles for Stage2/005 record `budget_hit=1` on at least some cut branches and show hundreds of milliseconds of accumulated search (see `official_run/diagnostics/`). Together with wall-time cutoffs in source code this supports **timing-sensitive search truncation** as a plausible cause of run-to-run variation; it is not yet a controlled demonstration of the sole cause.

**Research intervention:** add work-unit determinism (root/cut/candidate counters) *alongside* absolute time caps. Measure fixed-work vs wall-time policies under paired WSL testing. A time-only scheduler may finish a different prefix of the candidate space depending on host scheduling.

## 6. Source-level algorithm reconstruction and limitations

Based on the delivered `source_snapshot/src/synth_round81.cpp` and `r81_cut.hpp`:

1. Once a valid Round7.2 / optional Round8.0 incumbent exists, for declared limit ≥1000 ms and elapsed time below 71% of the limit, attempt a bounded cut optimization stage. Sub-1000ms cases skip it.
2. Each local cut has at most four leaf variables; its exact truth function is computed as a 16-bit mask. Cut enumeration retains at most nine cut frontiers per node and samples at most 2500 candidate roots per branch.
3. Candidate families are greedy SOP/POS prime covers and several Shannon variable-order decompositions; “exact truth mask” does **not** mean globally exact minimum circuit synthesis.
4. Candidate admission accounts conservatively for private gate reclamation using fanout and rejects replacements exceeding propagated required-time bounds. It uses structural hashing while building candidate DAGs.
5. Whole-graph acceptance requires a valid netlist, lower actual weighted area (or equal area with lower delay), and delay at or below target. `branch_strict` additionally forbids delay regressions relative to its basegraph.
6. Branches are independent whole-graph trials (sop/shannon/all). The per-invocation cut stage has a 450 ms/16%-of-limit total cap, with per-branch 160 ms/6.5%-of-limit caps; these caps are heuristic and allow small overshoots. `reverse` additionally runs the Round8.0 structural rewrite after each cut branch.
7. Profiling on Stage2/003 shows SOP/Shannon/All yield distinct area/delay results. Stage2/021 logs tens of thousands of locally rejected timing candidates. These counters show active exploration and constraint filtering; they do not independently prove each rejected candidate was globally inferior.

**Correctness:** replacing a cut root by a functionally identical expression on its separating frontier preserves the entire output function by substitution. The official evaluator provides independent passing functional/timing tests for all 800 evaluations in this feedback; randomized local testing was also included in the previous delivery. This is *not* a formal proof of timing compliance on future hidden inputs.

**Efficiency caveats:** a larger cut-candidate menu can increase speculative allocations, local mapping overhead, and preprocessing cost even if the final accepted graph is small. Local private-reclaim cost is conservative and may miss opportunities that require several coupled rewrites. Bounds on cuts, roots and time imply incomplete search.

## 7. Recommendations for Round 8.2 — Timing-regularized, budget-aware resynthesis

Prioritize **better selection and better cost-efficiency**, not merely adding more transformations:

1. **Objective-aware Pareto archive:** preserve legal incumbents spanning (area, delay, observed time) where meaningful. Since output timing is computed exactly, use a delay cap relative to baseline (0, 1, a small amount, or full target slack) and compare across policies. Until scoring formula is known, retain an area-priority and a conservative delay-priority candidate.
2. **Work-metered cut scheduling:** deterministic cut/root budgets complemented by a hard wall-clock reserve. Instrument discovery counts, candidate rejection causes, true live-DAG gain, and candidate value per millisecond to identify costly low-yield search.
3. **Adaptive representation routing (not testcase-ID routing):** cut statistics and available required-time slack decide whether to attempt SOP, Shannon, or both. Preserve controls in ablation. Avoid deriving a general rule from the already repeatedly viewed 50 public cases.
4. **Reduce expensive branch duplication:** `r81_shannon` already retains around 90% of reverse's measured total area savings for roughly 1.5–1.6× instead of 2.45–2.51× runtime; incremental last-mile gain may not justify all parallel branch runs.
5. **Independent holdout:** freeze a fresh, deterministic suite *before* any tuning; include distinct function families, gate price skews, input/output counts, and timing limits. Record seeds, hashes, and all failed runs. Evaluate once after design decisions, clearly distinguishing this from 50 public development cases.
6. **Score sensitivity:** request the official syllabus grading formula. Absent a published formula, report the full Pareto frontier; do not invent weights or silently treat meeting the delay target as the only timing objective.

**Go/no-go for Round8.1:** GO as a verified research building block. NO to declaring `r81_reverse` universally best. Preserve R7.2 as fast safe fallback, `r81_shannon` as balanced exploratory control, and `r81_reverse` as area-oriented experimental control pending actual grading weights.

## 8. Threats to validity

- **Selection bias:** same 50 public cases have been reused repeatedly across prior rounds, so they are development data, not blind generalization evidence.
- **Temporal noise:** two paired passes do not establish reproducible runtime ordering with statistical confidence.
- **Infrastructure:** WSL2 + Windows-mounted project path differs from an Ubuntu 22.04 evaluator on native Linux; absolute timings are not portable.
- **Aggregation:** area sum and median runtime are descriptive, not necessarily the assignment's score function. Cases with different input/output counts and targets may be implicitly weighted differently.
- **Causality:** correlations between structure, timing budgets and gains do not identify a sole cause without controlled offline fixed-work experiments.
- **Optimality:** exact cut truth-table evaluation does not imply exact global optimality, even for fixed four-leaf boundaries (greedy gate realization).

## 9. Evidence map and reproduction

- `casewise_800_official_records.csv`: every observed case × variant × run, including area/delay/runtime, normalized runtime and proxy scores.
- `stage_run_variant_summary.csv`: per run, stage and variant aggregates.
- `six_delay_tradeoffs.csv`: detailed six-case area-delay sensitivity and log-weight break-even thresholds.
- `source_snapshot/*`: current Cut engine and baseline/rewriter implementation contained in the uploaded archive.
- `official_run/*.csv` + `*.log`: authoritative official evaluation raw data; `official_run/diagnostics/*.log` provide candidate-stage counters.

Every figure in this postmortem can be regenerated by the accompanying `build_audit.py` with the exact feedback ZIP at the recorded path. No background experiments or invented evaluator runs are included.

# Paper Development Notes — Cross-Stage Logic Synthesis

These notes preserve an audit trail for later formal report writing. They are **not** a claim of official grade improvement.

## Research questions

**RQ1:** Can exact acceleration of two-level cover computation improve actual synthesis throughput under hard per-case budgets? Round 7 established lower primitive work but exposed an adverse interaction with portfolio selection.

**RQ2:** Can candidate dispatch that accounts for a feasible incumbent improve end-to-end deadline reliability without sacrificing circuit quality? Round 7.1 is designed to test this using paired data and a scheduler-off ablation.

**RQ3:** How robust is a strategy developed with Stage 1 across a new Stage 2 dataset? The two-stage regression matrix is mandatory. Existing R5.1 passed Stage 1 25/25; it missed Stage 2 `case_016` intermittently.

**RQ4:** When should a synthesis algorithm increase representation diversity (ROBDD, SOP/POS factoring, AIG rewriting, cross-output resubstitution) rather than deeper search in one representation? No evidence from Round 7.1 alone can answer this; it motivates Round 8.

## Suggested report outline

1. **Problem formulation**: Boolean truth table \(F\), legal AND2/OR2/NOT DAG, area/delay recurrences, runtime constraint and unknown course score weighting.
2. **Stage 1 algorithm recap**: ROBDD-based synthesis, variable ordering, cached structural hashing, affine/polarity cases, SOP/POS cover, area recovery, candidate portfolio. Baseline source fingerprint.
3. **Failure analysis from new data**: Stage 2 outlier structure; why `case_016` stresses exhaustive two-level cover; actual official statuses and direct profiler evidence.
4. **Round 7 computational improvement**: Hash-neighbor cube merging \(O(kS_r)\) expected vs pair enumeration \(O(S_r^2)\); packed bitset greedy gain counts; A/B identity on 10,656 combinations.
5. **Counterintuitive interaction**: End-to-end runtime can regress when faster code triggers extra search attempts; demonstrate with candidate count and official PASS discrepancies. Avoid equating local speedups with total system gains.
6. **Round 7.1 scheduling method**: General short-budget guard \(L\le250\) ms, absolute dispatch cap \(0.72L\), feasible-incumbent skip predicate, deadline-aware secondary primary candidates, opt-out ablation.
7. **Experimental validation**: Paired repeated same-host official evaluator; per-case area/delay/runtime; Stage 1 regression and Stage 2 outlier; failure rate; independent netlist verification and source fingerprinting.
8. **Trade-off interpretation**: Improvements in PASS and runtime reserve versus potentially missed alternative logic structures. Pareto comparisons before considering an unknown grading formula.
9. **Limitations and next steps**: Heuristic budget thresholds, non-interruptible sections, hidden-case generalization, later multi-representation synthesis and structural optimization.

## Evidence ledger

| Claim | Evidence location | Verification state |
|---|---|---|
| Frozen Stage 1 area total 529,014 | `evidence/baseline/round51_stage1.csv` and Round 7 user CSVs | Observed |
| Stage 2 R5.1 intermittent case016 timeout | `evidence/round7_user_run/run1_stage2_round51.csv`, `run2_stage2_round51.csv` | Observed |
| R7 default missed case016 in both repeats | `evidence/round7_user_run/run*_stage2_default.csv` | Observed |
| Both one-kernel ablations recovered case016 in two repeats | Matching CSVs | Observed, not a reliability guarantee |
| R7 accelerations keep exact cover choices | `tests/test_exact_cover.py`, 10,656 C++ A/B comparisons | Tested for specified combinations; separate mathematical proof |
| 8 versus 6 completed synthesis candidates | `evidence/round7_user_run/case016_profile_comparison.csv` | Observed in direct profiling |
| Additional candidates cause official timeout | Logs plus source analysis | Strong hypothesis; exact attribution unproven |
| R7.1 resolves failure with margin | To be populated by user's R7.1 Feedback ZIP | NOT TESTED YET |
| R7.1 improves area/delay across stages | To be populated by user's R7.1 Feedback ZIP | NOT TESTED YET |
| Hidden-test or official-grade improvement | Requires external results / scoring information | UNKNOWN |

## Wording safeguards for the final paper

- Write **"reduced cover kernel work"** rather than **"reduced total running time"** until paired official measurements confirm.
- Write **"all shared PASS cases reported equal area and delay"**, not **"every netlist was identical"**, except for the specifically hashed diagnostic netlists.
- Treat `case_016` Area 1,781 as a successful circuit *only in runs that PASS*.
- Record on-target delay as a quality attribute; the evaluator treats deadline and correctness separately from the target delay penalty.
- Avoid treating 50 public cases as a blind, statistically independent test set after repeated public-driven tuning. Fresh holdouts should be precommitted and used only for generalization checks.

# Round 8.5 — Search Order, Budget Return and Unseen-Case Risk

## 1. Frozen comparison and controlled intervention

The new search strategies reuse the same exact four-leaf cut Boolean truth-table validator, graph materializer and full-graph metrics from Round 8.4. They modify only the **order** in which Shannon/SOP candidate branches are searched, the per-branch root cap, and an optional transfer of unused wall-time allowance. Thus Boolean semantics are unchanged *provided every candidate is correctly checked against the cut truth function*, and the original feasible incumbent is retained if no acceptable complete replacement exists.

For a candidate circuit `C`, existing acceptance compares complete-graph area, tests `delay(C) <= target_delay`, and keeps only legal candidates. The local exhaustive `verify_exhaustive.cpp` independently simulates all `2^n` assignments and computes the full circuit's structural metrics. A candidate that misses the target is not preferred by this branch, even though course rules may allow delay-penalized circuits to PASS.

## 2. Why SOP-first may differ from Shannon-first

Each branch starts from the **same** frozen incumbent (not from the partially rewritten result of the other branch). However, their bounded total runtime leaves the later branch only the remaining share. With wall-dependent cost, permutations in branch order change which exact subset of root cuts can finish before the deadline. Hence outputs may differ even when the total number of root candidates permitted is identical.

The 0.77·L global guard reserves at least 0.23·L for program tail *after* the recorded start; this is only heuristic (some nonpreemptible work may run past the check). The per-branch `work_roots` cap is deterministic, but `budget_hit` remains hardware/load-dependent. None of these rules constitute a hard real-time scheduling proof.

## 3. Independent full Stage 2 evaluation

See the exact `evidence/stage2_125_exact_local.csv` and summary. A standalone one-off local run generated 125 valid outputs, each checked against *every original input assignment* and with output Delay within target. The baseline R8.4 TopQ Dual produced 501,124 total weighted Area. SOP-first scored 499,340, a numerical gain of 1,784, while Shannon-first scored 502,308 (worse by 1,184); root-permutation results depend heavily on `case_005`. There is no guarantee of this ranking under different timing, nor a known exact official scoring formula. Runtime and peak RSS are measured only on this local host; report them separately from the official evaluator.

## 4. Why the naive budget-return variant is not a solution to team Issue #2

The experimental standalone Cut Search `budget_reclaim` expands the second branch's per-branch wall allowance and potential root cap when the first branch returns early. In one local full Stage 2 pass, Area sum=501,635, worse than SOP-first, with no decisive stability improvement. In the teammate's proposal, by contrast, an *ineligible optional Round 5.1 mapper* reserves budget that should be returned to the upstream **BDD search**. These are conceptually similar capacity-accounting policies but not equivalent optimizations. We cannot assume an observed negative result for one disproves a reported gain for the other.

## 5. Repeated-run stability limitation

The included `evidence/repeat_selected_local.csv` contains only the actually completed rows (a partial set, not a claimed complete experiment). Cases 003, 005 and 017 show variation where wall guards fire. Case 016 has tight 100-ms runtime budget and may also fluctuate **before Cut Search starts**, because primary BDD variants are time-dispatched. The current approach does not guarantee complete determinism; an upstream candidate variation can change the entire downstream optimization base.

## 6. Hidden-case validity and memory

18 additional synthetic cases are frozen from a separate Python specification and independent truth-table generator; they check broad Boolean functional patterns, not effectiveness on unseen instructor cases. The 24 existing structured holdouts are reused development data and not genuine blind holdouts. No optimization uses benchmark IDs. TA says the final 100 cases have no positive RAM limits. Memory remains an optimization research axis; observed R85 local peak RSS on a larger Stage 2 case reaches ~71 MiB, very far below the server's total 48 GiB, and must be evaluated with true per-process limits rather than confusing the total server RAM with a guarantee of private capacity.

## 7. Release decision criteria

Only promote R8.5 as the team's final Stage 2 code after: (a) both public banks score 50/50 PASS under **unmodified** evaluator inputs; (b) multiple paired evaluator runs show acceptable runtime, area and delay relative to R8.4; (c) fresh clean-build acceptance using the intended source layout; (d) code-owner review of integration and flag decisions. Do not close Issue #2 based on this standalone delivery.

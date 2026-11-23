# Round 8.6 — Controlled Allocation Ablation

## 1. Causal question

Round 8.5's `budget_reclaim` simultaneously: (i) increased second-branch SOP root quota by 300 and (ii) allowed the second branch to use more of the remaining common time budget. Hence a quality change cannot be attributed to budget refund without a factorial design.

This round holds constant the pre-existing BDD incumbent, Top-Q selection function, graph metric, correctness oracle, Shannon-first branch order, and global time guard, varying only the two above factors. The reverse allocation (300 more Shannon roots) is a negative control for an assumed SOP bias.

## 2. Budget equations and invariants

Let `L` be input runtime limit in milliseconds. Let `t` denote elapsed time from the solver start and `s` elapsed time from entering the R86 Cut stage. Define:

\[
T=\min(360,0.15L),\qquad B=\min(180,0.54T).
\]

At each branch's start, the available remaining budget is

\[
R=\min(T-s,\,0.77L-t).
\]

Branch 1 always receives \(\min(B,R)\). Branch 2 receives \(\min(B,R)\) for fixed-time policies and \(R\) for reclaimed-time policies. The outer limit cannot increase: **the same `T` and the same `0.77L` guard apply to all configurations**. If `R<5` ms, the next branch is not launched.

The default root cap is \(q=900\), with an inherited conservative reduction to \(q=600\) for \(L\le 2000\) and \(m\ge20\). The extra-root branch receives \(\min(1500,q+300)\). Root selection uses deterministic Top-Q ranking followed by original topological evaluation, but the *completion* of each selected search can still depend on its local wall deadline.

## 3. Local exhaustive experiment (not course evaluator)

All **150** generated circuit files from six policies and 25 actual public Stage2 inputs were independently verified against their complete truth tables (all assignments, not a random subset). Each met the case's target delay in the local metric checker.

| Policy | Verified | Total Area | Total Delay | Wall-hit events |
| --- | ---: | ---: | ---: | ---: |
| R86 baseline | 25/25 | 501,119 | 1,170 | 12 |
| R86 extra SOP roots | 25/25 | 500,279 | 1,170 | 15 |
| R86 time reclaim only | 25/25 | 501,590 | 1,170 | 10 |
| R86 both factors | 25/25 | 502,004 | 1,148 | 12 |
| R86 extra Shannon roots | 25/25 | 500,015 | 1,170 | 16 |
| Frozen R85 reclaim | 25/25 | 500,666 | 1,170 | 12 |

**These are one-pass, machine-dependent offline measurements and must NOT be advertised as grading results or the true effect of an isolated factor.** The factor comparisons are confounded by wall-clock cutoff variability even though all source-level non-budget settings were held constant.

Example Stage2 `case_003`: baseline 16,213; extra SOP 16,130 (wall hit), time-reclaim 16,213; combination 15,773 (no wall hit); frozen R85 reclaim 15,773. With a different run or machine load, cutoff and selected circuits can change.

Example `case_005`: baseline 109,084 / delay 68; extra SOP 108,340 / delay 68; time reclaim 109,555 / delay 68; combination 110,422 / delay 46; reverse allocation 108,083 / delay 68. Larger search can produce a worse Area and/or different Delay. It is not mathematically monotone because expanding Top-Q changes the candidate set and structural rewrite sequence; deadline truncation changes which candidates complete.

## 4. Key limits to claims

1. `budget_hit` counts branch-level wall timeouts, not total solver deadline failures; time spent before Cut and serialization still matters.
2. R86's baseline and R85's shannon-first are equivalent *by program intent* but produced in distinct binaries/processes; identical output is not guaranteed under time-sensitive search.
3. Independent exhaustive Boolean equivalence establishes correctness, but is not an official performance score.
4. The benefit of extra wall time is expected only when the fixed-time branch would otherwise stop due to the local time allowance, not because it exhausted its root quota.
5. The teammate's Issue #2 concerns **integrated BDD search** budget reallocation when Round5.1 is ineligible. R86 only studies the subsequent Cut optimization. It does not implement that separate integration change.

## 5. Frozen acceptance plan

Run two reversed-order paired official passes across both Stage1/Stage2 and seven configurations (the five R86 policies, plus both frozen R85 controls). Compare correctness (50/50 per config), target delay (50/50), Area (per-case, totals), Delay, median and geometric-mean runtime, and stability (same-case across two runs). Only after this test, choose a submission-quality candidate or retain R85 reclaim if the marginal improvement is not robust.

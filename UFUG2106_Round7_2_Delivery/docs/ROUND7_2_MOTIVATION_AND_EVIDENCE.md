# Research Evidence — Round 7.1 to Round 7.2

**Provenance:** User-supplied `Round7.1_Feedback_20261121_143631_942488.zip`; the previous independently reproduced `Round7_1_Postmortem_20261121.md`, also bundled in `evidence/`; two official paired evaluator runs on the user's WSL machine; Stage 1 `case_020` and Stage 2 `case_016` truth tables as found in the repository. Local Round7.2 observations dated 2026-11-21 were obtained in a *different* Linux container, not in the target WSL official evaluator environment.

## 1. Predecessor: what the earlier milestones actually established

| Round | Main change | Verified outcome | Remaining issue |
|---|---|---|---|
| Round 5.1 | Typed in-memory DAG postprocessing, plus existing ROBDD/Cover/polarity mapping | Stage 1 original archived 25/25 PASS, Area 529,014 | New Stage 2 short-budget case016 often at or above 100ms |
| Round 7 | Exact Cover acceleration: hash-neighbor implicant merge, bitset greedy cover | 10,656 Cover choice comparisons agreed; lower kernel runtime | Scheduler used freed time on more legacy candidates; default 24/25 Stage 2 in two official runs |
| Round 7.1 | Guarded short-budget portfolio, conservative stop of extra Legacy Search after feasible incumbent | Two complete paired official runs: 50/50 PASS; Stage 2 case016 ~25ms vs R5.1 ~98ms | Stage 1 case020 Area 766->777, Delay 30->32 |
| **Round 7.2** | Bounded cheap-first legacy quality recovery | Independent local smoke completed; *official target-host outcome pending* | Must confirm 50/50 PASS, QoR, and runtime reserve on WSL |

## 2. Round 7.1 genuine official evidence (not a hypothetical result)

| Dataset | R5.1 PASS / Target | R7.1 Guard PASS / Target | R5.1 complete Area | R7.1 complete Area |
|---|---|---|---:|---:|
| Stage 1 | 25/25 in both runs | 25/25 in both runs | 529,014 | 529,025 |
| Stage 2 | 25/25 in both runs | 25/25 in both runs | 508,535 | 508,535 |
| **Both** | **50/50** | **50/50** | **1,037,549** | **1,037,560** |

The +11 aggregate area change in R7.1 comes **entirely from Stage 1 case_020**. No other public case changed Area or Delay in those two runs. This unusually clean regression signature makes the subsequent quality recovery experiment interpretable.

### `case_016`: timeout was wasted candidate search

| Variant | WSL official run 1 (ms) | Run 2 (ms) | Functional result | Quality |
|---|---:|---:|---|---|
| Frozen R5.1 | 98.046 | 97.109 | PASS/PASS, ~2–3 ms reserve | 1781 / 36 |
| R7.1 Guard | 25.879 | 25.088 | PASS/PASS, ~74 ms reserve | 1781 / 36 |
| R7.1 Policy Off | timeout | timeout | FAIL/FAIL | No official valid output |
| R7.1 Legacy Merge | 41.036 | 40.016 | PASS/PASS | 1781 / 36 |
| R7.1 Legacy Cover | 42.140 | 44.117 | PASS/PASS | 1781 / 36 |

The unbounded direct profile (not official timing) showed the primary portfolio choosing candidate index 2. Three legacy candidates consumed approximately 43.840, 2.109, and 44.965 ms in one run; none improved the incumbent. Guard disabled all three, retaining the same netlist SHA across 15 R7.1 direct profiles. This is causal evidence for suppressing expensive *unproductive* work, not evidence that all legacy synthesis is useless.

### `case_020`: blanket skipping caused real optimization regret

| Variant | Area | Delay | WSL run1 (ms) | WSL run2 (ms) |
|---|---:|---:|---:|---:|
| R5.1 | **766** | **30** | 27.669 | 23.979 |
| R7.1 Guard | 777 | 32 | 11.320 | 9.684 |
| R7.1 Policy Off | **766** | **30** | 20.630 | 22.005 |

Its budget is 100 ms, target delay 35, with \(n=8\), \(m=8\). An independent local source reconstruction showed the second legacy candidate improving the pre-postprocessing intermediate Area from 796 to **776** in under 1 ms *in that container*; the same frozen postprocessor then reached final Area **766**, Delay **30**. Guard ended the same primary phase with intermediate Area 796 and final Area **777**, Delay **32**. Both final circuits exhaustively matched the truth table.

**Interpretation:** case016 argues against unbounded legacy work; case020 argues against blanket elimination of all legacy work. They directly motivate a *cost-class-based shortlist*.

## 3. What Round 7.2 actually changed

Only the short-budget, small-n branch is modified. Its one supplementary candidate uses the legacy complementary-normalization BDD representation with `cubemode=0` and a cooperative deadline, while the first and third higher-cost legacy candidates remain skipped. R7's exact Cover acceleration and R7.1's main-search portfolio are preserved.

- Admission: \(100\le L\le250\), \(n\le10\), a feasible on-target incumbent exists, and \(t<0.35L\).
- Cooperative deadline: \(0.60L\) relative to process entry; checks in legacy parsing/BDD construction/Boolean mapping.
- Postprocessing admission: skip the extra trial if \(t\ge0.65L\), reserving time for existing final transforms/output.
- Only valid strictly better candidates replace the incumbent according to the original lexicographic rank.
- Long-budget cases retain their existing R7.1 policy.

All thresholds are preregistered engineering heuristics, not mathematically certified worst-case bounds or invented scoring parameters.

## 4. Local R7.2 observed results (NOT official WSL scores)

We compiled the generated 53 KB C++ source with `g++ -O2 -std=c++17 -DNDEBUG` in the container and compared the same inputs against a previously frozen R7.1 source snapshot.

| Structural probe | R7.1 Guard Area / Delay | R7.2 Shortlist Area / Delay | Independent functional check |
|---|---|---|---|
| Stage 1 `case_020` | 777 / 32 | **766 / 30** | Exhaustive **256/256** assignments |
| Stage 2 `case_016` | 1781 / 36 | **1781 / 36** | Exhaustive **512/512** assignments |

The local candidate trace shows `case_020` accepting a 776/30 intermediate candidate from the shortlist, then producing a final 766/30 netlist. On `case_016`, the supplementary candidate is constructed but rejected as worse, and the final 1781/36 result is preserved.

We also ran the R7.2 executable on **all 25 Stage 2 public truth tables** and independently inspected the netlists:

- 25/25 solver processes returned success *without official evaluator resource enforcement*;
- 25/25 R7.2 netlists had the same Area and Delay as the independently run R7.1 guard netlists;
- 15/25 were exhaustively checked by an independent bit-parallel evaluator (\(n\le13\));
- 10/25 had deterministic seeded sampled functional checks (larger \(n\)); all matched;
- see `evidence/local_stage2_smoke.csv` and `evidence/local_stage2_independent_verification.csv` for **per-case** evidence.

Do not present the latter observations as teacher-evaluator PASS results, verified hard timeout compliance, or a universal correctness proof for large truth tables.

## 5. Candidate-quality accounting and what might be misleading

A score based only on **summed areas of cases marked PASS** is invalid for comparing a 24/25 version with a 25/25 version. For each jointly passed case \(i\), report its paired ratio

\[ r_i^A = A_i^{(7.2)}/A_i^{(7.1)}, \qquad r_i^T = T_i^{(7.2)}/T_i^{(7.1)}.\]

Across a stage, use

\[G_A=\exp\left(|S|^{-1}\sum_{i\in S}\ln r_i^A\right),\]

and similarly \(G_T\), together with the *complete-area sum only when all corresponding cases passed*. A more expensive but still valid circuit may be justified only by an explicitly documented scoring trade-off; the course's exact formula is not available here.

## 6. Testable hypotheses and falsification criteria

1. **H1 (quality recovery):** Stage 1 case020 regains Area 766 and Delay 30 while staying below its 100ms limit. Failure if improvement exists only outside the official timeout.
2. **H2 (stability):** Stage 2 case016 remains Area 1781, Delay 36, and retains substantial official time reserve. Failure if new shortlist regularly exceeds the runtime deadline.
3. **H3 (no widespread regressions):** across all Stage 1 and Stage 2 public cases, R7.2 maintains 50/50 PASS and all delay targets, without new casewise Area or Delay regressions compared with R7.1 Guard.
4. **H4 (causal attribution):** disabling R7.2 shortlist (`UFUG_R72_POLICY=guard`) reintroduces the case020 quality regression, while disabling only the cooperative deadline (`shortlist_nocancel`) does not change netlists on short, easy public cases. The latter might be inconclusive if no candidate ever reaches the deadline.

Any failed hypothesis should be reported and preserved, not silently removed from the archive.

## 7. Literature-facing positioning

This milestone is an implementation of **budget-aware candidate selection**, not yet a new logic representation. It sits between the project-specific typed-DAG synthesis baseline and the next planned methodological layer (AIG rewriting / library-based NPN resynthesis / multi-output resubstitution). The broader hypothesis is that controlling the *expected marginal utility per CPU budget* allows more search diversity while respecting per-instance resource constraints. R7.2 uses a **single algorithmic cost proxy** (`cubemode=0`), and it would be misleading to describe it as a learned value predictor or a globally optimal scheduler.

## 8. Limitations and next decision

The central unresolved issues remain: one additional candidate has no guaranteed payoff; cooperative cancellation is not hard preemption; area/critical-path trade-offs are evaluated using heuristic ranking rather than a published grade equation; exhaustive truth-table equivalence for the largest \(n\) is not feasible with the included quick verifier; and public-case performance alone cannot establish hidden-case generality.

**Next action:** Run `run_round72.sh` on the user's WSL CPU and upload its automatically generated `Round7.2_Feedback_*.zip`. Only then can R7.2 be accepted as a Stage 1+2 release candidate. See `EXPERIMENT_PROTOCOL.md` for exact collection instructions.

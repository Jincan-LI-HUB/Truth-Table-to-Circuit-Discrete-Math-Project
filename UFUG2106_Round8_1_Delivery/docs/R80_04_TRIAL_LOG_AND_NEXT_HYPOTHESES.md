# Round 8.0 — Trial log and failure analysis for paper writing

**Design goal:** preserve the distinction between an algorithmic hypothesis, implemented approximation, directly measured effect, and extrapolation. No trial should be deleted merely because it produced no gain.

## Trial T0. Inherited Round7.2 circuit, no structural change

Evidence: user's WSL Round7.2 feedback dated 2026-11-21, Stage1 529,014, Stage2 508,535, 50/50 public PASS and target-met twice. In this new prototype the frozen executable and `r8_off` are paired controls. Current local Stage2 saved netlists match these values. They are a useful starting point but not a proof of minimality.

## Trial T1. Basic absorption, double-negation cleanup

Method: bottom-up structural rewriting; optional identity collapses. One-pass Stage2 results: **0 improving cases**. The compacted baseline already appears to remove many such trivial redundant patterns. A non-improvement here does not refute simplification theory; it indicates it adds little on top of the current Round7.2 source output.

## Trial T2. Common-factor extraction

Method: rewrite `(x&y)|(x&z)` to `x&(y|z)` and the dual when syntactically visible; compare two fanout admission policies. One-pass Stage2 results: **7 candidate factoring matches** across 25 nets in either mode, **no accepted area improvement**. Plausible explanations: (a) many factors already extracted upstream; (b) other structural encodings hide common factors; (c) sharing of the original terms offsets local gains; (d) timing restrictions eliminate otherwise plausible choices. This prototype does not yet include NPN equivalence classes or cut/window matching, which might expose additional factors. Do not diagnose the general algorithm as ineffective from seven superficial matches.

## Trial T3. Polarity / De Morgan

Method: introduce opposite-polarity implementation only when declared gate costs suggest a possible local advantage; validate required time and global live costs. One-pass results: **16 attempted phase candidates**, no net improvement. Stage1/Stage2 have prior polarity-aware mapping, so much of this action has already been considered upstream. Additional work should consider joint phase assignment and multi-output complement sharing, not just replacing a single gate.

## Trial T4. DAG-aware inverse distribution, one pass

Method: if a precomputed divisor is present, try `x&(y|z)` -> `(x&y)|(x&z)` or dual, and evaluate exact global area after garbage collection. Stage2 generated **2,707 symbolic attempts**, but only `case_021` had a strict accepted net improvement: 22,590/69 -> 22,578/70. A meaningful result even though the local gate count could increase. This is a concrete example of interaction between algebra and cross-cone sharing. The timing slack constraint matters; without accepting an extra delay unit, the candidate would be rejected despite meeting target 70.

## Trial T5. Iterative structural rewriting

Method: after an accepted global improvement, rebuild candidates on the newly accepted DAG. Bound five passes, stop upon no improvement. `case_021` trajectory is **22,590 -> 22,578 -> 22,543 -> 22,539 -> 22,535**, delays 69 ->70 ->70 ->70 ->70. All 65,536 truth rows match after the final pass. Gate count **increased** from 11,808 to 11,885, while AND2 count decreased by 66 and OR2 count increased by 143. The separately implemented `iterate_strict` control prevents delay regression and therefore keeps 22,590/69 in this case; this makes the 55-unit result an explicit Pareto trade-off rather than a dominated baseline. The weighted area advantage follows from AND2 cost=3 and OR2 cost=1: -66(3)+143(1)=-55. Other Stage2 public cases did not improve with this limited candidate family.

This establishes that a small first-pass gain can expose a larger second-pass gain *for this example*. It does not establish that unrestricted repeat-until-no-change is optimal: our stopping rule can trap a search that requires a temporary area increase, a change in representation, or a new window size.

## Trial T6. Integrated Round8 source from frozen R7.2

The prototype source is generated from the exact Round7.2 source SHA, adding a final-stage rewrite portfolio. It retains Round7.2 intact and only accepts a new graph when the whole live weighted area improves (or ties with a strictly smaller delay), the entire DAG remains valid and the maximum output delay is within target. It skips declared budgets below 1,000ms. Stage2 local direct-run preflight regenerated all 25 output netlists; all **25/25 exhaustively verified** with exact truth tables; the only Area/Delay difference is the `case_021` reduction above. Official WSL evaluation remains **pending**, so no claim of runtime superiority or 50/50 official PASS for Round8 is made.

## Implications for the next independent research cycle

**H1 — Cost-aware 3/4-cut NPN choices.** A direct two-level pattern matcher found only seven factorable cones, indicating insufficient neighborhood breadth. Evaluate 3/4-feasible cuts with a bounded implementation library containing polarity and arrival-time alternatives; evaluate exact *global* weighted cost after mapping. Existing Round6.1 is a reasonable comparator, not an implementation to copy unchanged.

**H2 — Multi-output divisors.** Case021 gained through existing divisors. Build windowed divisor lists using fanout and output-cone overlap; use bit-parallel signatures only as candidate filters and check exact local truth-table equality for accepted cut functions. Avoid exponential truth-table storage per internal gate.

**H3 — Structural choice frontier.** Current greedy incumbent cannot cross barriers requiring temporary area increases. Hold a small non-dominated set of legal full graphs or bounded per-cut alternatives. Track Pareto diversity in area, delay and structural hash before final mapping. Compare beam width 1, 3, 5 with a fixed total CPU budget.

**H4 — Algorithm order interaction.** Compare factoring->reuse, reuse->factoring, rewriting->resubstitution and their reverse orders on frozen holdouts. A negative single-pass result may be an order interaction, not a false literature insight.

**H5 — Scoring uncertainty.** Collect area, delay, runtime as separate metrics until official grading is known. Do not invent an objective function or declare a 0.0108% Stage2 aggregate area gain to be a score improvement of equal magnitude.

## Reusable paper framing

> A naïve local algebraic rewriting pass rarely improves the already optimized baseline. In contrast, a bounded DAG-aware divisor-reuse transformation can reduce global weighted area under timing slack, and repeated transformations may unlock further savings. On 25 public Stage 2 cases, the initial structural prototype improves one instance by 55 area units with one additional delay unit while preserving all tested Boolean functions under exhaustive verification. The result motivates a broader search over NPN-equivalent cut implementations and cross-output divisors; it does not justify claims of general performance superiority or global circuit optimality.

This paragraph is intentionally cautious and should be updated after the WSL official paired tests and independent holdouts. Keep the negative trial counts and complete raw CSVs in the appendix.

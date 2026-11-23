# Paper Research Notebook — Stage 2, Round 7.2

> This file records the decisions and source-supported evidence *at the time of design*. It is not a completed experimental conclusion or a claim about hidden-case quality. Update it **after** reading the next WSL feedback archive; preserve this original as a preregistered design record.

## 1. Candidate paper narrative

**Working title:** *Resource-Constrained Multi-Output Boolean Synthesis: Exact Cover Acceleration and Budget-Aware Candidate Search*.

### Research questions

- **RQ1:** Under tight per-instance runtime limits, can equivalent synthesis strategies with different structural costs be scheduled so that no completed valid incumbent is lost?
- **RQ2:** Does exact subroutine acceleration translate into better end-to-end performance without an adaptive portfolio, or can it paradoxically increase timeout risk by admitting extra work?
- **RQ3:** Can a conservatively scheduled non-Cover legacy BDD candidate recover circuit quality lost by premature search termination?
- **RQ4:** How does a resource-aware strategy affect quality on an earlier public stage and on a later, more varied stage, as opposed to overfitting one outlier?

### Recommended argument flow

1. **Task setup:** an unknown multi-output truth table, restricted AND2/OR2/NOT gate library with case-dependent area/delay, separate runtime cap, delay target with penalty, two-stages public set plus undisclosed hidden set.
2. **Stage 1 contribution:** shared complemented-edge ROBDD and cached two-level Cover with polarity-aware mapping; typed in-memory DAG area recovery; freeze Round5.1 for historical comparability.
3. **Round 7 algorithmic acceleration:** replace the expected \(O(S^2)\) prime implicant pair scan with hash-neighbor lookup and greedy Cover's element-by-element scan with bitset popcount. Exact kernel A/B identity over 10,656 checks. State this tests the computed covers, not a global optimality proof.
4. **Unexpected failure:** faster kernel caused more legacy portfolio launches, pushing short-budget cases into timeout. This is a *scheduler-level performance regression* despite a locally faster kernel.
5. **Round 7.1 intervention:** early-terminate legacy search after an on-target incumbent under short budgets; demonstrate case016 stabilized to roughly 25ms while preserving 1781/36.
6. **Quality regret:** the same blanket skip suppresses a cheap and useful alternative for case020; report 766/30 → 777/32. Explicitly mention the 11-unit total area regression even though it is only ~0.001% of aggregate.
7. **Round 7.2 hypothesis:** admit one cost-class-selected candidate with a cooperative deadline and a time reserve, preserving the incumbent and refraining from high-tail variants. Show 2-case exhaustive smoke, then full official paired experiment once available.
8. **Future structural optimization:** explore AIG/NPN resynthesis, multi-output sharing, and choice networks only *after* the scheduling layer meets feasibility and quality goals.

## 2. Pre-registered independent variables

- Independent variable A: scheduler, `R7.1 Guard` versus `R7.2 Shortlist`.
- Independent variable B: optional legacy candidate cancellation, `shortlist` versus `shortlist_nocancel`.
- Sanity/control: `R7.2 Guard` should reproduce R7.1 quality because no shortlist candidate is admitted.
- Historical reference: `R5.1` independent source.
- Dependent variables: PASS, target_met, Area, Delay, evaluator runtime, time-limit utilization, candidate-level utility and cost.

These definitions are fixed before the user runs the target evaluator, reducing the temptation to select after-the-fact metrics.

## 3. Reusable tables for a paper

**Table A — Milestone progression:**

| Version | Newly introduced mechanism | Stage 1 PASS | Stage 2 PASS | Stage 1 Area | Stage 2 Area |
|---|---|---:|---:|---:|---:|
| Frozen R5.1 (R7.1 paired run) | Prior BDD/Cover + typed DAG | 25/25 | 25/25 | 529014 | 508535 |
| R7 Default (its own prior paired run) | Exact Cover acceleration, old scheduler | 25/25 | 24/25 | 529014 | 506754* |
| R7.1 Guard | Budget-aware skip-all-legacy | 25/25 | 25/25 | 529025 | 508535 |
| **R7.2 Shortlist** | Bounded cheap legacy recovery | pending official | pending official | pending | pending |

`*` **Incomplete sum because a case failed**. These data come from different experiment sessions; only compare within paired measurements for timing.

**Table B — Two opposite outliers from the R7.1 feedback:**

| Case | Baseline | Guarded | Failure type | Candidate evidence |
|---|---|---|---|---|
| Stage2 case016 | R5.1 ~98ms, Area 1781/Delay36 | Guard ~25ms, same quality | Wasted high-tail computation | Legacy durations ~43.8 / 2.1 / 45.0ms; no gain |
| Stage1 case020 | R5.1 766/30 | Guard 777/32 | Premature stopping | Second legacy recovers intermediate 776 and final 766 |

**Table C — R7.2 local preflight (not instructor evaluator):**

| Case | R7.1 | R7.2 | Verification |
|---|---|---|---|
| Stage1 case020 | 777/32 | 766/30 | complete 256 assignments |
| Stage2 case016 | 1781/36 | 1781/36 | complete 512 assignments |
| Stage2 all 25 | all direct programs complete | same Area/Delay per case | 15 exhaustive, 10 sampled |

**Table D — To be populated by returned R7.2 feedback:**

| Stage | Version | PASS/target | Complete Area | Median runtime | Geometric runtime ratio vs R7.1 | New QoR regressions |
|---|---|---|---:|---:|---:|---|
| Stage1 | R7.1 Guard | TBD | TBD | TBD | 1.000 | — |
| Stage1 | R7.2 Shortlist | TBD | TBD | TBD | TBD | TBD |
| Stage2 | R7.1 Guard | TBD | TBD | TBD | 1.000 | — |
| Stage2 | R7.2 Shortlist | TBD | TBD | TBD | TBD | TBD |

## 4. Equations worth retaining

Gate area and path delay:

\[A(C)=a_\land N_\land+a_\lor N_\lor+a_\neg N_\neg,\qquad D(C)=\max_{o}T(o).\]

Candidate admission policy:

\[
E=\{100\le L\le250,\ n\le10,\ B\text{ feasible and on target}\};
\quad\operatorname{Admit}(j^*)=\mathbf1\{E\land t<0.35L\}.
\]

Cooperative cancellation boundary and nominal reserve:

\[
t_{\mathrm{cancel}}=0.60L;\qquad
R_{\mathrm{nominal}}=L-t_{\mathrm{cancel}}=0.40L.
\]

`R_nominal` is not a hard guarantee: downstream operations after a checkpoint can exceed the remaining 40% if nonpreemptible.

Paired geometric mean:

\[
G_T=\exp\left(\frac1{|S|}\sum_{i\in S}\ln\frac{T^{72}_i}{T^{71}_i}\right).
\]

Accept a candidate iff it strictly improves the inherited lexicographic objective \(\rho(C)\) on a complete valid netlist; a better *intermediate* rank does not formally guarantee superior final postprocessed quality.

## 5. What must NOT be claimed

- Do not state that R7.2 has officially achieved 50/50 PASS until target-host CSVs verify it.
- Do not interpret a direct profile or container `timeout` as official evaluator timing.
- Do not claim exhaustive verification for \(n>13\) where only deterministic sample was checked.
- Do not claim the search is globally optimal, that the shortlist is a learned probabilistic reward model, or that its 35%/60% time limits are proved worst-case bounds.
- Do not compare incomplete Area Sum for any 24/25 run with complete 25/25 Area Sum.
- Do not fabricate official scoring weights; teacher's exact equation has not been provided.
- Do not describe the previous legacy search as uniformly poor: the case020 counterexample refutes that simplistic framing.

## 6. Post-feedback tasks for next review

1. Check that both Stage 1 and Stage 2 achieve 25/25 PASS and target_met, repeated twice (or more around tight deadlines).
2. Locate every casewise QoR delta (especially case020 recovery, case016 stability); inspect any new regressions before changing thresholds.
3. Separate timeout/failure causes (candidate uncaught vs postprocessing vs input overhead) from valid-but-slow cases.
4. Compare area and runtime both by normalized geometric ratios and raw complete Area Sum, not just a total score.
5. Inspect actual shortlist utility distribution across the 50 public cases: how often accepted, rejected, cancelled, or admission denied?
6. Do not optimize case IDs. Consider whether structural features (BDD node count, support, cost asymmetry, slack) can predict marginal value under different time limits.
7. If R7.2 meets all gates, freeze it before launching Round 8 representation and sharing experiments.

# Round 8.0 — Why this prototype, and what the data actually show

Date: 2026-11-21. Status: research prototype, NOT the frozen final Round 8 submission. Scope: exact, structure-preserving Boolean rewrites on already synthesized AND2/OR2/NOT gate DAGs, with global weighted area and timing validation.

## A. Background, preserved results and provenance

1. Round 5.1 delivered 25/25 Stage 1 functional passes, 25/25 delay targets, area sum 529,014. On Stage 2, the 100ms outlier `case_016` could PASS at ~97-99ms but failed other runs.
2. Round 7 exact-cover acceleration made minterm cover computation cheaper, but under the original time policy it could launch additional fruitless legacy candidates. Results exposed how an apparently faster *kernel* can produce a slower *complete search*.
3. Round 7.1 controlled short-budget search; Stage 2 `case_016` dropped to ~25ms but Stage 1 `case_020` increased area 766->777 and delay 30->32. The guard prevented a valuable cheap candidate.
4. Round 7.2 restored one bounded legacy candidate. The user's **official WSL paired evaluator** reported 25/25 PASS and target-met in BOTH stages for two runs; Stage 1 area 529,014 and Stage 2 area 508,535; case020 766/30, case016 1781/36. Thus Round7.2 is our frozen quality and feasibility reference.
5. Prior Round 6.1 four-feasible-cut rewriting on Stage 1 decreased aggregate area by about 128–150 units relative to 529,014 in two paired Linux experiments, while median runtime increased by about 23–31%. Those results show limited *implementation benefit under that budget*, not the intrinsic impossibility of cut rewriting. The old cut module requires local `new_arrival <= old_arrival` and an immediate reclaimable-area gain, potentially excluding lower-area solutions within remaining global timing slack.

The official course grade formula remains unknown. Every reported aggregate area is **descriptive**, not a course grade. Failing-case area must never be treated as zero or counted as an improvement.

## B. Experimental question, and why its opposite is plausible

**H8.0:** A distributive expansion that is locally counterintuitive can reduce the *whole, shared, live network* when some of its terms are already computed elsewhere. An independent rewrite engine can find such gains without damaging the known-valid incumbent.

Competing explanation: the Round7.2 DAG is already heavily optimized; factorings / De Morgan rephasing / decompositions could simply add gates, consume timing slack and runtime, or offer no extra sharing. This should be measured rather than assumed.

We construct seven separately ablatable modes: `absorb`, `factor`, `factor_relaxed`, `phase`, `reuse`, `combined`, and `combined_relaxed`. The integrated solver offers `off`, `factor`, `phase`, `reuse`, `all` (one pass), and `iterate` (bounded to five passes). `iterate` is the experimental default and **not** yet released as an official-quality optimization.

## C. Pre-study: structural heterogeneity

Frozen local Round7.2 netlists from all 25 Stage 2 functions were profiled before the rewrite engine. For example:

| Case | Area | Gates | % gates in ≥2 output cones |
|---|---:|---:|---:|
| 013 | 115,734 | 56,871 | 10.3% |
| 014 | 62,535 | 31,502 | 5.9% |
| 021 | 22,590 | 11,808 | 69.6% |

These are measurements of **existing sharing**, not estimates of globally available optimization. The very heterogeneous output-cone structure argues against applying a uniform expensive rewrite without profiling its interaction with timing and per-case cost.

## D. Local offline Stage 2 evidence (new, 2026-11-21)

Method: Use 25 saved Round7.2 netlists. Parse the original case metadata and perform each structural pass on the same input DAG. Evaluate the resulting *full live gate graph* using each case's exact AND2/OR2/NOT area and delay. Original truth tables were separately used for **exhaustive independent equivalence verification of all 25 integrated Round8 output netlists**, including up to 2^20 assignments per case. The local program is Linux, **not** the user's WSL official evaluator.

One-pass ablation (see `evidence/stage2_onepass_ablation.csv`):

| Independent mode | Cases with strict area improvement | Total area saved across Stage 2 | Count of symbolic attempted rewrites |
|---|---:|---:|---:|
| absorb | 0 | 0 | 0 |
| factor | 0 | 0 | 7 |
| factor_relaxed | 0 | 0 | 7 |
| phase | 0 | 0 | 16 |
| reuse | **1** | **12** | 2,707 |
| combined | 0 | 0 | 23 |
| combined_relaxed | **1** | **12** | 2,731 |

The numerous attempted `reuse` matches are NOT themselves independent gains. Only changes accepted on the *whole* live DAG count. Existing Round7.2 outputs were often already factored or had expensive shared children: a low count of factorable patterns is expected to limit these basic algebraic methods.

### E. The nontrivial iterative result

We reapply an ablation portfolio to the *previously accepted* full graph and preserve the previous graph if no improvement is found. Stage2 `case_021` evolves:

| Accepted pass | Area | Delay | Change from previous |
|---|---:|---:|---:|
| Round7.2 reference | 22,590 | 69 | — |
| 1 | 22,578 | 70 | −12 |
| 2 | 22,543 | 70 | −35 |
| 3 | 22,539 | 70 | −4 |
| 4 | **22,535** | 70 | −4 |
| 5 | 22,535 | 70 | 0 |

The **Pareto-conservative** `iterate_strict` mode preserves Area 22,590 / Delay 69 for this case, because the 55-unit area saving costs one delay unit. Neither output Pareto-dominates the other; the unknown official grade does not permit a universal ranking.

The original case's target delay is **70**. This is an area reduction of **55 units** (about **0.243%** of the *case's* original area), consuming one unit of timing slack. Across all 25 Stage 2 cases, the combined area decreases **508,535 -> 508,480**, only **0.0108%**. The other 24 cases show no confirmed net area saving in this pre-study.

### Gate-count versus weighted-area reversal

In Stage2 `case_021`, the original live graph has **5,391 AND2, 6,401 OR2, 16 NOT = 11,808 total gates**; after iterative rewrite it has **5,325 AND2, 6,544 OR2, 16 NOT = 11,885 gates**. The gate count **increases by 77** while the weighted area **decreases by 55**, because this instance charges AND2=3, OR2=1, NOT=1:

\[
\Delta A=(-66)(3)+(143)(1)+(0)(1)=-55.
\]

This is a directly measured example of why naive minimization of *number of gates* is not the same objective as the evaluator's explicit per-case weighted area. A source-level AIG node count would be still another objective.

All 25 Stage 2 cases were rerun through integrated Round8 code and checked by an independently implemented C++ bit-parallel verifier on **all** truth-table rows (not just 256 random samples). Every output agreed. The changed `case_021` netlist was also verified exhaustively after each offline iteration. In addition, 140 deterministic random small multi-output networks × 7 modes = **980 independent exhaustive equivalence comparisons** passed; these random tests are *correctness tests*, NOT valid predictors of performance on real test distributions.

**Crucial result:** The one-pass result alone understates the attainable savings from the same identity. Rewriting can expose new already-existing divisors for a later pass. Conversely, more passes are not automatically better: extra work could exhaust a strict time limit, and a zero-improvement pass should stop the current branch.

## F. What's not proven

- No official WSL Round8 evaluation has yet been performed. The local direct-run times are explicitly not official evaluator times, and published Round7.2 area figures are reference outputs only.
- 25 public Stage 2 cases are development evidence. The algorithm has not been validated on independent frozen large holdouts.
- This is an elementary DAG-aware distributive/divisor reuse prototype, **not** full NPN rewriting, SAT exact synthesis, generalized cut rewriting, or full multi-output factoring. We should not rename it as such.
- Monotone strict-area acceptance preserves incumbent quality when the incumbent is feasible, but the engine is still greedily locally biased and does not guarantee the globally minimum circuit.
- Bounded wall-clock checks occur *between* rewrite passes; they do not prove a hard CPU time upper bound in the evaluator's process accounting.

## G. Research decision

Proceed to a **paired official WSL Round8 prototype experiment**, with Round7.2 frozen baseline, single-pass and iterative ablations, 50-case per-row Area/Delay/Runtime comparison, and an auto-generated feedback ZIP. Do not freeze a final Round8 release based on the 55-unit Stage2 public saving alone. The next theoretical hypothesis should study why basic factoring rarely fires and whether 3/4-feasible-cut NPN choices + exact share-aware global mapping materially enlarge the reachable search space.

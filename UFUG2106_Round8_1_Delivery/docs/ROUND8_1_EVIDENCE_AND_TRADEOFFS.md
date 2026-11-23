# Round 8.1 — Evidence, Negative Results, and Trade-offs

**Date:** 2026-11-21. **Status:** independent local Linux prototype results only. No user WSL official evaluator run has been performed for Round 8.1 as of this document.

## 1. Prior evidence and research question

Our frozen Round 7.2 established 50/50 published PASS and 50/50 target satisfaction on two user WSL paired runs. Stage 1 area was 529,014; Stage 2 area was 508,535. Round 8.0 was also 50/50 with Stage 2 area 508,480, owing to an improvement of 55 on `case_021` and no change elsewhere; delay on that case increased 69→70. Round 8.0 was thus an existence/feasibility demonstration rather than broad synthesis quality improvement.

**New hypothesis H1:** Structural rewrite failure on other cases is driven in part by *candidate discovery*: restricting substitutions to explicit algebraic patterns misses legal equivalent structures. Search over exact small-cut truth functions should expose additional opportunities.

**H2:** The *level* at which methods are combined matters. Node-level mixing of SOP and Shannon is not necessarily better than constructing independent whole-graph alternatives and selecting the best.

**H3:** The *order* of cut resynthesis and algebraic rewrite can change available reuse/divisor opportunities. Compare A→B, B→A, and separate branches rather than judging A and B independently.

## 2. Crucial negative result during implementation

Our very first implementation compared new local cone cost with the *entire* pre-rewrite cone, inadvertently counting nodes with external fanout as if they would be removed. This biased substitutions toward eliminating shared logic that remained live globally. Three recorded offline runs (same R7.2 starting netlists; unaccepted whole-graph alternatives) were:

| Stage 2 case | Frozen area | Invalid local-score candidate area | Decision |
|---|---:|---:|---|
| 021 | 22,590 | 23,691 | Reject globally |
| 014 | 62,535 | 63,917 | Reject globally |
| 002 | 58,697 | 58,945 | Reject globally |

These were real development candidate measurements, **not accepted netlists and not official scores**. The resulting correction uses `private_reclaim`: nodes with fanout > 1 terminate the reclaim computation unless they are the replacement root. All candidates continue to require whole-DAG Area/Delay evaluation.

**Lesson:** for DAG optimization, optimizing expression size or whole cone size without fanout accounting can destroy previously shared work. The cost model, not necessarily the Boolean identity, caused the initial failure.

## 3. Offline isolated Cut Resynthesis experiment

Dataset: the 25 Stage 2 published truth tables, with 25 corresponding saved Round 7.2 netlists; n ranges up to 20. Every resulting netlist was checked on **all** \(2^n\) assignments by an independent C++ bit-parallel verifier against its original supplied truth table. Original area sum: **508,535**.

| Offline configuration | Cases improved | Area saved vs frozen R7.2 | Total area implied |
|---|---:|---:|---:|
| SOP/POS prime-cover | 21/25 | 6,747 | 501,788 |
| Shannon rotations | 19/25 | 6,820 | 501,715 |
| Mix both at every node (`all`) | 22/25 | 5,542 | 502,993 |
| Locally allow zero-gain choices | 23/25 | 5,109 | 503,426 |
| Round8.0 local pass then Cut | 22/25 | 5,250 | 503,285 |

**Interpretation:** `all` has the broadest local candidate family (other than `choices`), but is *worse* than independently applying `sop` or `shannon` to a full graph. Adding candidates does not guarantee a better result under local greedy selection: early choices modify the shared graph and prevent other structural combinations. This is an actual experimentally measured order/interaction effect, not merely an algebraic observation.

The 25-case comparisons above are the sums of each accepted full-graph result, not the sums of unaccepted local heuristic deltas. They are not official evaluator scores.

### Representative results (isolated postprocessor)

- `case_003`: area 19,494 → 15,932 under Shannon (delay 61; target 65), 3,562 saved. SOP yields 16,572 and delay 65. Different candidate families occupy different Area–Delay points.
- `case_005`: area 112,221 → 109,638 under SOP (delay 54; target 69), and 110,027 under Shannon (delay 51). SOP saves more area; Shannon returns lower delay.
- `case_023`: area 2,986 → 1,897 with zero-gain choices (delay 40; target 40); single-path `all` yields 1,958, illustrating sensitivity to structure choices.
- `case_021`: standalone cut only saves 2 area while preserving delay 69; the old Round8.0 iterative pattern optimizer saves 55 area while increasing delay to 70. These techniques have different inductive biases.

## 4. Integrated Round8.1 complete synthesizer (local pre-official study)

New integrated system: frozen Round7.2 → frozen Round8.0 (configurable) → optional bounded, independent cut branches. It runs directly on the original truth-table inputs and emits real allowed-gate netlists. We ran all Stage 2 cases with `r81_branch` and `r81_strict`, then **independently verified every assignment** for every emitted netlist (50 complete-case comparisons: 25×2). All 50 valid; all 50 satisfy target delay. Separately, 180 deterministic random DAGs under four cut modes yielded 720/720 exhaustive equivalence checks.

| Version (local) | Stage 2 area sum | Saved vs R7.2 | Cases improved | Target met |
|---|---:|---:|---:|---:|
| Frozen R7.2 control | 508,535 | 0 | — | 25/25 |
| Frozen R8.0 iterate (historic) | 508,480 | 55 | 1 | 25/25 |
| **R8.1 independent branch, area-priority** | **500,696** | **7,839** | **17/25** | **25/25** |
| **R8.1 independent branch, strict delay** | **508,352** | **183** | **14/25** | **25/25** |

The area-priority local aggregate improvement is \(7839/508535\approx1.5415\%\), much larger than Round8.0's roughly 0.0108%. However this is a quality measurement under local Linux, **not** the official user's WSL score or a proof of hidden-case performance.

### Where most area is saved

| Case | R7.2 Area / Delay | R8.1 Branch Area / Delay | Area improvement | Target delay |
|---|---|---|---:|---:|
| 003 | 19,494 / 39 | **15,932 / 61** | −3,562 | 65 |
| 005 | 112,221 / 40 | **109,073 / 55** | −3,148 | 69 |
| 023 | 2,986 / 25 | **2,103 / 40** | −883 | 40 |
| 021 | 22,590 / 69 | **22,531 / 70** | −59 | 70 |
| 001 | 2,086 / 32 | **2,046 / 32** | −40 | 41 |
| 025 | 6,533 / 73 | **6,501 / 73** | −32 | 80 |

Cases 003/005/023 account for \(3562+3148+883=7593\) of the 7,839 saved area units (~96.9%). This is a concentrated gain, **not** uniform success. The first three cases also increase delay. Neither variant globally Pareto-dominates the baseline for all cases.

### Why strict mode matters

`r81_strict` preserves baseline delay in every Stage 2 case and still reduces area by 183 across 14 improved cases. Its smaller area saving is *not* evidence of incorrect optimization; it is a different multiobjective requirement. With an unknown grading formula, there is no defensible universal declaration that the area-priority point is superior.

## 5. Order reversal experiment

A separately compiled `reverse` mode runs Cut → Round8.0 pattern rewriting from the same legitimate Round7.2 input, rather than Round8.0 → Cut. In independent direct integrated case studies:

| Case | Round8.0→Cut branch | Cut→Round8.0 reverse | Interpretation |
|---|---:|---:|---|
| Stage2 005 | 109,073 / 55 | **108,960 / 55** | Reversal improves area by 113 |
| Stage2 021 | **22,531 / 70** | 22,534 / 70 | Forward branch is 3 better |
| Stage2 003 | 15,932 / 61 | 15,932 / 61 | Same result here |

All three reverse netlists passed complete truth-table equivalence checking. This supports hypothesis H3, but these are selected case observations; the delivered full official ablation evaluates every case.

## 6. Runtime and practical release risks

The integrated local `r81_branch` program had the highest observed Stage 2 direct-call wall time of ~1.85 seconds, for a case whose runtime limit is 100 seconds. The shortest-runtime 100 ms cases skip cut resynthesis entirely. On cases with 1,000 ms limits, local integrated direct-run times were below the limit. This does **not** prove compliance on the user's Windows-mounted WSL CPU or hidden tests; per-invocation scheduling, I/O and hardware differ. The default runner therefore executes full *official* evaluator passes twice, reversing the order of variants and reporting each case's runtime.

Cut resynthesis adds computation. On difficult large cases, the area gains must be weighed against the unknown runtime contribution to the official score. Precomputed per-case limits are used for generic budget control only; no solver policy is conditional on specific case IDs.

## 7. Limits of what has been proven

- Formal equivalence of each cut transformation follows from exhaustive cut truth tables and the substitution lemma. Whole-network empirical equivalence was additionally checked for every Stage2 input assignment, in both integrated variants.
- The local gate builder produces legal topological netlists; all tested nets met declared target delays.
- The current algorithm is **not** exact resynthesis or a proof of global best-area circuits, despite using exact cut truth masks. SOP cover is greedy; cut count, root count and mapping orders are bounded.
- Stage 1 complete 25-case files were **not** present in the current container. Stage1 `case_020` was checked (area 766/delay 30 with both integrated variants). Full cross-stage regression remains **unverified** until user WSL official evaluator feedback.
- The official grading formula is still unknown. No invented aggregate score is reported.

## 8. Next experiment and decision logic

A controlled full WSL paired test should compare R7.2, R8.0, each cut family alone, the independent branch, the delay-strict branch, and reversed order, on **both** stages, twice. Key tests:

1. 50/50 PASS, 50/50 target met, no new short-runtime failure.
2. Pairwise area/delay changes, not area sum alone; report Pareto-dominated vs tradeoff cases.
3. Actual runtime per case relative to per-case limit; do not conflate container wall time and evaluator time.
4. Confirm area gain on 003, 005, 023 and strict improvements on the other 14 cases; characterize any discrepancy.
5. Investigate whether order reversal is worth extra runtime once the original two-stage benchmark is complete.
6. Preserve every negative ablation result to support paper methodology, not just the winning aggregate.

**Research decision:** Round8.1 is a stronger pre-official research candidate than Round8.0 in terms of multi-case area improvement. Final submission suitability and preferred Pareto point depend on the user's official evaluator data.

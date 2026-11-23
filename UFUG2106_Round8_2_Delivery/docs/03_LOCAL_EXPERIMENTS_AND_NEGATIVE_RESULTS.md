# Round 8.2 — Local Controlled Experiments and Negative Results

All numbers below were measured in the assistant's **local Linux container** using the same Stage2 public truth tables, NOT the course's official WSL evaluator. The Stage1 dataset is unavailable in this container apart from `case_020`. Wall-clock timings are diagnostic and can vary with host scheduling. The six-configuration study ran three concurrent subprocess workers; its timings are not comparable to the official single-process evaluator values.

## 1. Stage2 public developmental set, 25 cases

| Configuration | Area Sum | Savings vs R7.2 (508,535) | Sum of final delays | Median local runtime (ms) | Internal budget-hit count |
|---|---:|---:|---:|---:|---:|
| Stride, one Shannon, Area | 502,387 | 6,148 | 1,156 | 108.918 | 4 |
| Priority, one Shannon, Area | 502,167 | 6,368 | 1,137 | 126.009 | 3 |
| Priority, one Shannon, ADP | 508,376 | 159 | 1,101 | 113.863 | 3 |
| Priority, one Shannon, Slack | 505,810 | 2,725 | 1,109 | 115.034 | 3 |
| Priority, two branches, Area | 499,963 | 8,572 | 1,169 | 141.489 | 15 |
| Priority, two branches, Strict | 508,278 | 257 | 1,101 | 145.879 | 12 |

**Correctness:** 25 final netlists for `priority_area` and 25 for `priority_dual_area` were each exhaustively verified against all original input assignments. This gives 50/50 independently verified completed circuits; the other 100 configurations were generated with the same proven construction but were not all separately exhaustively checked in this study. Raw casewise CSV includes all 150 outputs, netlist digests, and local timings.

### Root-priority ablation

Compared case-by-case with `stride_area`, `priority_area` improves the area in **9/25**, worsens area in **2/25**, and leaves area unchanged in 14/25. It improves overall area by **220** and aggregate output delay by **19**. It is therefore a positive *aggregate* result, **not** proof of pointwise dominance.

On `case_003`, priority yields \(16,642/52\) compared with stride \(16,669/63\). On `case_005` both metrics improve in some local runs; timing-driven cutoffs cause modest non-determinism in individual area measurements. Report exact run provenance rather than conflating different local repetitions.

### Two-branch interaction

`priority_dual_area` saves a further **2,204** area units relative to `priority_area`; in this batch, 6/25 cases improved, none worsened in area, and 2 accepted a larger delay. The additional search is not free; median local runtime increased and 15/25 candidate runs hit an internal branch cutoff. These cuts are not failures, but demonstrate a binding compute budget.

### Root-cap sweep (five preselected developmental cases)

| Case | K=750 (Area/Delay) | K=1500 | K=2500 |
|---|---|---|---|
| 003 | 17,104/48 | 16,642/52 | 15,984/61 |
| 005 | 110,673/46 | 109,475/46 | 107,588/46 |
| 013 | 115,710/66 | 115,710/66 | 115,700/66 |
| 021 | 22,590/69 | 22,590/69 | 22,590/69 |
| 023 | 2,273/39 | 2,103/40 | 2,103/40 |

All 15 resulting circuits were independently exhaustively checked. Three `case_003` solutions constitute distinct Area–Delay Pareto points under these K values. **A larger search cap can change which circuit is selected, not merely monotonically improve both objectives.** Default K=1500 remains unchanged; this sweep is research ablation only.

## 2. Synthetic holdout v1 — NEGATIVE benchmark design finding

Before evaluating the solver, 24 random AND/OR/NOT DAG-generated cases were frozen to SHA-256 manifest. Their resulting functions collapsed to very simple or constant-like output logic. The total R7.2 area was only **484** for all 24 cases; the two Round8.2 single-branch strategies had the same area, and the dual branch saved just **1**. All 96 executions were exhaustively verified, and all target delays were met.

The scientifically supported conclusion is **the test generator lacked discrimination for the structural optimizations**, not that the new method fails to generalize. The dataset is preserved to avoid selective reporting. It is not a meaningful stand-in for hidden-stage difficulty.

## 3. Synthetic structured holdout v2 — additional generalization evidence

A **second, distinctly labeled** generator constructs 24 balanced, nontrivial, multi-input-dependent functions using XOR, MUX, Majority and mixed compositions. The input cases and individual SHA-256 hashes were frozen in `holdout_structured_v2/FROZEN_MANIFEST.json` *before* testing. The manifest SHA-256 is:

`7cff82819661397134726dcf907cdc68ec351e599b822b7adee99605c79bd71c`

| Variant | Area Sum, 24 cases | Improvement cases | Target Met |
|---|---:|---:|---:|
| Frozen R7.2 | 14,193 | — | 24/24 |
| R8.2 Fast Area | 13,924 | 16/24 | 24/24 |
| R8.2 Fast ADP | 13,939 | 14/24 | 24/24 |
| R8.2 Dual Area | 13,897 | 20/24 | 24/24 |

All 96 emitted netlists were independently verified over the entire truth table. These are valid **synthetic generalization checks** but NOT independent class hidden cases. The structured generator itself was designed after observing that v1 was too trivial; therefore the *overall holdout-development process* was adaptive. Preserve both findings, and do not advertise the pair as a perfect blinded benchmark program.

## 4. Negative/limited results and their interpretation

- ADP selection frequently preserves the faster baseline on six known high-slack public trade-offs; this is its design, not a synthesis error. Relative to single-branch area mode it yields significantly less total area savings.
- `priority` outperforms stride in aggregate yet loses on 2/25 cases; priority weights are heuristic and cannot establish universal improvements.
- `dual_*` increases cost and has more budget hits. If the course heavily rewards runtime, the area gains may not compensate.
- Even without changing the cost rule, wall-clock cutoff boundaries make some results vary between runs. Root-cap determinism narrows *which roots are considered*, but does not remove timing-induced variation when the deadline triggers mid-search.
- Candidate Pareto records are measured among the generated branches only; they are not a guarantee of a global Pareto frontier.

The observed numbers are traceable to `../evidence/local_stage2/stage2_local_ablation.csv`, `../evidence/local_rootcap_ablation.csv`, and both synthetic holdout result CSVs. Research reports should not infer statistical significance from two official runs without a broader paired repetition design.

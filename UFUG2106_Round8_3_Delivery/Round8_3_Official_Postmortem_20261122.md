# Round 8.3 — Official Postmortem and Root-Quota Audit

**Date:** 2026-11-22. **Status:** Stage 1/Stage 2 public release gate PASS; positive RAM cap issue unresolved. This report analyzes the uploaded `Round8.3_Feedback_20261122_002510_628132225.zip`, not a new official run.

## 1. Experimental scope, integrity, and limitations

- 6 variants × 2 runs × 2 stages × 25 cases = **600 official case records**. All are PASS and `target_met=yes`.
- The two runs reverse the order of variants; all were tested by the same WSL evaluator binary. The official CSVs do **not** provide output netlist hashes or per-case R83 root quota traces.
- SHA-256 fingerprints from `summary.json`: R8.2.1 comparator `77cd1db9de418bad796062bba8403b4790665a0c7cc8eb4f4e48466aeaae377f`, R8.3 `faca42b4ee25516e90301873351ae6a5cf31d2348c31ec6a172bef0190e40156`, evaluator `142361d7ce18bc47dea6a07538db79a588b3afbf446526c1d1246f4968b3d0ca`.
- Scope excludes the positive RAM limit anomaly from teammate Issue #2. The `known_ram_evaluator_discrepancy_not_retested` flag in official summary is `true`.
- Current public cases have been used repeatedly in development. Do not call these blind holdouts or claim hidden-case reliability from two runs.

## 2. Two-run total area and runtime

| Version | Run 1 area | Run 2 area | Run 1 runtime geomean ratio vs R8.2.1 Dual | Run 2 ratio |
|---|---:|---:|---:|---:|
| `r821_dual_area` | 1,020,017 | 1,020,717 | 1.0000 | 1.0000 |
| `r821_fast_area` | 1,027,659 | 1,027,659 | 0.8191 | 0.8095 |
| `r83_fast_area` | 1,029,745 | 1,029,745 | 0.7262 | 0.7389 |
| `r83_stable_dual` | 1,027,414 | 1,027,414 | 0.8546 | 0.8711 |
| `r83_dense_dual` | 1,024,829 | 1,024,829 | 0.9376 | 0.9449 |
| `r83_stable_adp` | 1,037,200 | 1,037,200 | 0.8760 | 0.9059 |

**Cross-run stability:** All four R8.3 configurations have identical Area and Delay for all 50 individual cases across the two official runs (200 paired case/configuration observations). Parent R8.2.1 Dual differs only on Stage 2 `case_005`: 102,928 → 103,628 (delta +700); its Delay is 67 in both runs. Parent Fast Area is identical on all 50. No claim that identical Area/Delay implies byte-identical netlists.

## 3. The substantive trade-off

- R8.3 Stable Dual total area **1,027,414** versus parent Dual **1,020,017 / 1,020,717**. Area penalty: **+7,397 / +6,697**, respectively. In exchange, geometric-mean paired runtime ratio is **0.8546 / 0.8711** (around 13–15% faster) and per-case measured Area/Delay is reproducible across the two runs.
- Stage 2 R8.3 Stable Dual area is 500,072, versus parent 493,922 / 494,622; the Stage 2 losses of 6,150 / 5,450 dominate the total difference. The 5,808 area-unit gap from `case_005` (+3,843 in run 1) and `case_003` (+1,965) explains 78.5% of the Stage 2 loss in run 1. Their Delay is identical in both algorithms (67 and 65, respectively). Stage 1 main losses are `case_010` (+677 with 1 lower Delay) and `case_012` (+551 with 2 higher Delay).
- R8.3 Dense Dual retains the same per-case Area/Delay in both runs, improves area relative to Stable Dual by **2,585** (11 cases improved; zero cases worsened), and has +2 aggregate Delay. It is 8.5–9.7% slower than Stable Dual by per-case geometric mean, yet approximately 5–6% faster than the parent R8.2.1 Dual. Despite official two-run stability, local preflight previously observed a dense-budget watchdog interruption; no global repeatability guarantee applies.
- R8.3 Fast Area is ~26–27% faster than parent Dual but has +9,728 / +9,028 area; it lowers aggregate Delay by 52. R8.3 Stable ADP sacrifices +17,183 / +16,483 area but reduces aggregate Delay by 109; geometric-mean per-case Area×Delay decreases about 2.4% relative to the parent. **This is only a sensitivity analysis; no official scalar grading rule is asserted.**

## 4. A concrete structural weakness in the quota implementation

The uploaded `source/src/r83_cut.hpp` ranks all live roots by `potential` (gate costs, privately owned one-hop gates, bounded slack), selects the **top 1,500** roots as a Boolean mask, then iterates them in **ascending topological ID**. The `work_roots=900` quota stops after the first 900 selected roots. Consequently, the actual 900 visited roots are **not** necessarily the highest-ranked 900.

An independent local diagnostic replay used the identical frozen R8.3 binary with `UFUG_R83_POLICY=off`, `UFUG_R82_POLICY=off`, `UFUG_R8_POLICY=off`, `UFUG_R81_POLICY=off`, on the three real Stage 2 input tables. The resulting pre-cut DAGs were rescored with the exact C++ `potential` expression. This is a **diagnostic reconstruction**, not an official evaluator output.

| Input | Live eligible roots | Actual visited in highest-ranked 900 | Higher-ranked roots skipped | Actual selected score sum | True top-900 score sum |
|---|---:|---:|---:|---:|---:|
| `stage2/case_003` | 8,864 | 501/900 | 399 | 75,200 | 81,048 |
| `stage2/case_005` | 51,025 | 663/900 | 237 | 89,808 | 93,600 |
| `stage2/case_021` | 11,808 | 462/900 | 438 | 55,727 | 58,921 |

This is a **priority-ranking utilization issue**, not a Boolean correctness flaw. The ranking is only a heuristic, so selecting the highest ranked 900 does **not** prove a better circuit. However, it is a controlled, testable algorithm change that may recover quality under the **same root budget**, without increasing the quota.

**Correct candidate for next stage:** first determine the best `Q` roots by the same deterministic score (with ID tie-breaking), mark exactly these roots, then rewrite them in topological order. Once `Q` roots have been processed, copy the remainder of the graph without cut search. The root selection and topological processing orders must stay distinct. Compare against current `top1500 -> first900 topo` using the same initial graph, score, time watchdog, and global acceptance policy. Record score percentile, actual candidate materialization count, completed roots, wall guard events, circuit area, delay, and runtime.

## 5. More robust follow-up design

1. **Keep frozen R8.2.1 dual and R8.3 Stable/Dense as baselines**, not merely R7.2. Compare per-case and across two WSL runs.
2. **Ablate ranking** under matched root budgets: old top-1500/topological-first-900, true ranked top-900/topological processing, old 1,100 dense, and optional root scoring without slack term. Avoid case IDs or score tuning on individual examples.
3. **Budgeted branch allocation:** record SOP vs Shannon incremental improvement per root/materialization and spend the next deterministic work tranche on the branch with the strongest observed normalized yield. Preserve an incumbent and a watchdog; evaluate overfitting on a newly frozen holdout.
4. **Measure optimization versus time honestly:** report per-case Area, Delay, runtime, and Area×Delay as a separate exploratory metric; report non-PASS as failures, not zero-area gains. Log complete candidate counters and binary fingerprints.
5. **Resource compliance separate:** teammate GitHub Issue #2 and evaluator positive-RAM discrepancy remain unresolved; do not infer a pass from Stage 1/2 results that do not stress positive RAM caps.

## 6. Decision

**PASS as a research milestone. Do not promote R8.3 Stable Dual to the final quality default.** Its deterministic root budget improves observed repeatability and mean runtime but loses several thousand area units to the parent Dual. **R8.3 Dense Dual is a stronger area–runtime intermediate candidate**, whereas the parent R8.2.1 Dual still produces the smallest area among these six whole-program configurations in these two runs. Investigate true top-Q priority selection before simply increasing quota again. All claims remain confined to the tested public cases and diagnostic reconstructions.

# UFUG2106 — Round 7.1 Official Postmortem & Round 7.2 Design Motivation

**日期：**2026-11-21。**状态：**Round 7.1 two-run public release gate PASS；Round 7.2 为研究设计、尚未实现和验证。

## 1. Evidence provenance & limitations

- Source: user-supplied `Round7.1_Feedback_20261121_143631_942488.zip` and its source snapshot.
- Feedback ZIP SHA-256: `22dafecd8638d4013c7a33a9a6ee68f6dba5ae1db9ced5f6508bdbe62f1fe3f7`.
- 20 official evaluator CSVs: 2 runs × 2 stages × 5 variants; 15 direct-profile records: 3 runs × 5 variants; diagnostic netlists, logs and independent verifier outputs.
- Round 7.1 generated source SHA-256: `3b63dbb63a910bd66583d4fbf5a7e7995c1a1cbfc33842bb60484f52180b102b`. Frozen R5.1 source Git blob: `68ec9f54b27081641ac10358f81eef260acfcbdb`.
- **Reproducibility caveat:** direct profiling bypasses the official 100 ms limit; its wall times do **not** establish official PASS. CPU and tool overhead vary with platform; do not compare diagnostic CPU timings numerically with WSL evaluator timings.
- **Scoring caveat:** precise official grading equation is unavailable. Area Sum is descriptive; the sum for a FAIL run excludes the unsuccessful case and must not be compared as if it covered 25 cases.

## 2. Official paired runs: PASS, Area, Delay

| Dataset | R5.1 PASS (run 1/2) | R7.1 Guard PASS (run 1/2) | R5.1 Area Sum | R7.1 Area Sum | Target met |
|---|---:|---:|---:|---:|---:|
| Stage 1 | 25/25, 25/25 | **25/25, 25/25** | 529,014 | **529,025** | 25/25 in all runs |
| Stage 2 | 25/25, 25/25 | **25/25, 25/25** | 508,535 | **508,535** | 25/25 in all runs |
| Combined | 50/50, 50/50 | **50/50, 50/50** | 1,037,549 | **1,037,560** | 50/50 in all runs |

**Only quality regression:** Stage 1 `case_020`: Area **766→777** (+11, +1.436%), Delay **30→32** (+2, +6.667%); Target Delay **35**, so it still meets target. The other 49 public cases have identical Area and Delay across R5.1 and guarded R7.1 in both runs.

**Overall Area trade-off:** +11 / 1,037,549 = **+0.00106%**; however the isolated case-level degradation should not be dismissed merely because aggregate effect is small.

## 3. Runtime analysis under official evaluator

| Stage | Run | R5.1 median ms | Guard median ms | Runtime geometric mean ratio | Guard faster cases |
|---|---:|---:|---:|---:|---:|
| stage1 | 1 | 48.361 | 48.926 | 0.8046 | 21/25 |
| stage1 | 2 | 49.453 | 48.648 | 0.8383 | 20/25 |
| stage2 | 1 | 35.193 | 31.268 | 0.7805 | 17/25 |
| stage2 | 2 | 32.508 | 31.427 | 0.8243 | 18/25 |

The geometric mean runtime ratio is computed over **all 25 cases** in the same stage, all PASS for both compared variants:

\[ G_T(S)=\exp\left(\frac{1}{|S|}\sum_{i\in S}\ln\frac{T_i^{(\mathrm{Guard})}}{T_i^{(\mathrm{R5.1})}}\right). \]

For the 50-case union, the ratios are **0.7924** (run 1) and **0.8313** (run 2): relative geometric-mean reductions of approximately **20.8%** and **16.9%**. These are descriptive for two paired runs, not significance estimates.

## 4. Stage 2 case_016: resource waste rather than weak functional synthesis

| Variant | Official run 1 | Official run 2 | Outcome | Area, Delay |
|---|---:|---:|---|---|
| R5.1 | 98.046 ms | 97.109 ms | PASS / PASS, ~2–3 ms slack | 1781, 36 |
| R7.1 Guard | **25.879 ms** | **25.088 ms** | PASS / PASS, ~74 ms slack | 1781, 36 |
| R7.1 policy off | TIME_LIMIT | TIME_LIMIT | FAIL / FAIL | N/A |
| R7.1 legacy merge | 41.036 ms | 40.016 ms | PASS / PASS | 1781, 36 |
| R7.1 legacy cover | 42.140 ms | 44.117 ms | PASS / PASS | 1781, 36 |

Direct profile (3 runs each): Guard finishes **5 primary candidates**, chosen index 2; it skips the Legacy Search because a valid on-target incumbent exists. Policy-off finishes **8 candidates** including **3 Legacy candidates**. The complete final netlist SHA-256 is identical across all 15 diagnostic runs:

- `176cbd52f7caa636737717ba9b42b1fddd45a90a4bd359735a09c683dbae7f9a`

The extra Legacy candidates brought **no improvement** to Area or Delay for this case. The run1 policy-off direct log shows Legacy candidate durations **43.840 ms, 2.109 ms, 44.965 ms**, with final 113.177 ms (unbounded direct run). Guard direct log finishes in 23.350 ms. Use official evaluator times above for official timing comparisons.

**Supported causal explanation:** Exact Cover acceleration finishes main candidates earlier, which makes the old threshold scheduler dispatch additional long, non-interruptible Legacy tasks. Guarded early termination prevents this work once the incumbent meets the delay target. This is supported by the source and candidate-level trace, not inferred merely from aggregate runtime.

## 5. Stage 1 case_020: lost quality opportunity

The original public case was re-read from the repository: **n=8, m=8, runtime limit 100 ms, target delay 35; AND2 area/delay 2/2; OR2 2/3; NOT 1/1**.

| Variant | Official Area | Official Delay | Run1 ms | Run2 ms |
|---|---:|---:|---:|---:|
| R5.1 | **766** | **30** | 27.669 | 23.979 |
| R7.1 Guard | 777 | 32 | 11.320 | 9.684 |
| R7.1 policy off | **766** | **30** | 20.630 | 22.005 |

**Independent source reproduction for stage1 case020:** The uploaded R7.1 source snapshot was compiled locally (different CPU than the WSL evaluator). The *same truth table* was passed once with `UFUG_R71_POLICY=guard`, once with `off`, and both generated outputs were verified exhaustively against **all 256 truth-table rows**. This reproduction is evidence for the *candidate selection path*, not for WSL timing.

- Both modes complete 5 primary candidates. Primary index 2 becomes incumbent with intermediate Area 796 and Delay 30; final guarded postprocessing yields **Area 777 / Delay 32**.
- Guard detects a valid on-target incumbent and skips the entire Legacy portfolio.
- Policy-off enters Legacy search. The **second Legacy candidate** (`influence-desc`, `cubemode=0`) improves its intermediate Area from 796 to **776**. Original postprocessing then reaches **Area 766 / Delay 30**.
- Hence a cheap *supplementary* candidate can produce meaningful QoR improvement even though the incumbent already meets target. An unconditional skip rule is too coarse.

Observed netlists were **not** byte-identical in the two case020 modes; each was exhaustively verified in the separate reproduction. This establishes an actual structural difference, beyond mere scheduling noise.

## 6. Mathematical motivation for Round 7.2: value-aware scheduling

Let the current fully verified incumbent be \(B\), elapsed time \(t\), global limit \(L\), and a candidate family \(j\) have predicted cost \(\widehat{\tau}_j\) and predicted quality gain \(\widehat{\Delta Q}_j\). The Round 7.1 heuristic is essentially a binary rule:

\[\mathrm{skipLegacy}=\mathbf1\{L\le250\ \land\ B\text{ valid}\ \land\ D(B)\le D^*\}.\]

This reduces timeout risk, but can suppress promising inexpensive transformations. A future **research** scheduler could rank work by expected improvement per estimated unit time, subject to an independent safety reserve:

\[\text{consider }j\text{ only if }t+\widehat\tau_j+R\le L\quad\text{and}\quad\widehat{\Delta Q}_j>0,\]

with \(R\) reserved for serialization, evaluator/system overhead and timer uncertainty. This is only a **heuristic** unless the estimated cost is replaced by an enforceable upper bound.

### Why Stage1 case020 and Stage2 case016 are complementary probes

- `case_020`: second legacy candidate cheaply improves quality; blanket skipping introduces regret.
- `case_016`: first and third legacy candidates are expensive and do not improve quality; blanket execution introduces deadline failure.
- A quality-aware/priority-aware system should be able to consider the cheap useful candidate **without** reintroducing unbounded candidates. This is a hypothesis for the next implementation; it has not yet been officially evaluated.

### Research ablation matrix for proposed R7.2

| Candidate variant | Objective | Risk / required check |
|---|---|---|
| R7.1 Guard | Reference feasible incumbent | case020 QoR regression |
| R7.1 Policy Off | Full candidate coverage | case016 timeout |
| R7.2 Cheap-first shortlist | Try low-cost legacy mapping before expensive tasks | Need measured cost model, quality regression tests |
| R7.2 Cooperative Legacy Deadline | Interrupt expensive Legacy computation | Need actual checkpoint coverage and safe cancellation |
| R7.2 Hybrid | Combine shortlist with deadline and end-to-end incumbent reserve | Must show zero new FAILs and retained QoR |

**Acceptance gate:** preserve 50/50 PASS, 50/50 target met, recover Stage1 `case020` Area 766/Delay 30 if possible, maintain Stage2 `case016` a substantial time reserve (e.g. engineering target \(\le 50\) ms on the present WSL), improve or retain the remaining 49 cases, and check independent holdout behavior. The \(\le50\) ms target is an engineering objective, not a course rule or formal guarantee.

## 7. Unresolved risks and methodological boundaries

1. Two paired runs are insufficient to estimate hard worst-case deadline performance. Increase repetition near the timing threshold and use official evaluator status as primary evidence.
2. The initial primary candidate and some postprocessing components still lack hard preemption. The existing 72% dispatch cap is not a hard real-time guarantee.
3. Optimizing solely against `case016` and `case020` risks public-set overfitting. Dispatch should depend on general cost and circuit-state signals, and must be evaluated across both Stages plus independent holdouts.
4. Full Boolean equivalence is established by evaluator for the public files. Some independent verification for larger n is sampling, not an exhaustive proof; preserve semantics-preserving transformation arguments.
5. Do not claim current Area 1,037,560 is an overall official score; the grading formula is unknown.
6. All subsequent Round release scripts should produce a feedback ZIP even when the release gate fails; explicitly include candidate-level logs and reproducibility fingerprints.

## 8. Current decision

**Round 7.1: ACCEPT as the first robust public feasible release candidate, with a known minor quality regression. Round 7.2: pursue quality recovery with deadline-aware low-cost candidate admission. Do not discard the Cover acceleration or revert to the time-unsafe full legacy portfolio.**

Supplementary complete per-case raw observations: `Round7_1_Casewise_Audit.csv`. Original evaluator logs and netlists remain in the user-provided feedback ZIP. Source trace reconstruction is documented as independently reproduced on a different CPU.

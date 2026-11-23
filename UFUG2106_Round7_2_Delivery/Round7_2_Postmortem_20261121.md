# UFUG2106 Stage 2 — Round 7.2 Postmortem & Research Record

**Date:** 2026-11-21  
**Evidence:** `Round7.2_Feedback_20261121_150300_498854.zip` (user WSL official evaluator, two opposite-order paired runs; additional three-repeat direct profiles).  
**Milestone decision:** **GO — freeze Round 7.2 as the best current public-tested feasibility-and-quality baseline; proceed to Round 8 structural QoR research.**  
**Scope caveat:** 50 public cases and two runs are not statistical proof for 50 hidden cases; the official score function has not been provided.

## 1. Research question and prior evidence

R5.1 achieved excellent circuit area but exhibited unstable 100ms timeouts on Stage2 `case_016`. R7 accelerated Quine–McCluskey cube merging via hash-neighbor lookup and greedy cover via bitset popcount. With shorter candidate generation, the initial portfolio completed earlier and admitted expensive, unproductive legacy candidates; default R7 could still time out. R7.1 introduced guard-based short-budget stopping and achieved 50/50 public PASS but lost Stage1 `case_020` QoR (Area 766→777, Delay 30→32). Candidate-level evidence showed that the second legacy variant, with `cubemode=0`, cheaply recovered quality for `case_020`, whereas the expensive full legacy portfolio provided no benefit on `case_016`.

**R7.2 hypothesis:** reinstate exactly one bounded, cover-free legacy candidate only if a legal incumbent already exists and sufficient short-budget time remains, thereby recovering quality without losing runtime reliability.

## 2. Algorithmic formulation

Circuit area and critical-path delay are

\[
A(C)=a_{\land}N_{\land}(C)+a_{\lor}N_{\lor}(C)+a_{\neg}N_{\neg}(C),
\]

\[
D(C)=\max_{o\in O}\operatorname{arrival}(o),\quad
\operatorname{arrival}(v)=d_{\mathrm{op}(v)}+\max_{u\in\operatorname{fanin}(v)}\operatorname{arrival}(u).
\]

The R7.2 policy makes a supplementary search eligible if \(100\le L\le 250\) ms, \(n\le10\), and a valid delay-feasible incumbent \(B\) exists. Admission requires elapsed time \(t<0.35L\). The one candidate uses the separate legacy influence-desc mapper, `cubemode=0` (no exhaustive cube-cover enumeration). A cooperative synthesis deadline is set at \(0.60L\), and expensive postprocessing is disallowed when \(t\ge0.65L\). An incumbent is only replaced when a fully constructed candidate is strictly better under the inherited delay-excess/area/delay rank. Other legacy variants remain blocked in these short-budget feasible cases.

**Correctness rationale:** the accepted circuit must be a legal completed DAG encoding the same truth table; scheduling changes which proven Boolean-preserving candidates are explored, not the function specification. The incumbent remains as a fallback. **No strict worst-case runtime bound follows**: cancellation is cooperative and not every graph/postprocessing operation is cancellable.

## 3. Official paired evaluation

| Variant | Stage 1 PASS Run1/Run2 | Stage 2 PASS Run1/Run2 | Stage 1 Area | Stage 2 Area | Per-case delay targets |
|---|---:|---:|---:|---:|---|
| R5.1 frozen | 25/25; 25/25 | 25/25; 24/25 | 529,014 | 508,535* | All passing cases meet target |
| R7.1 Guard | 25/25; 25/25 | 25/25; 25/25 | 529,025 | 508,535 | 50/50 both |
| **R7.2 Shortlist** | **25/25; 25/25** | **25/25; 25/25** | **529,014** | **508,535** | **50/50 both** |
| R7.2 Guard ablation | 25/25; 25/25 | 25/25; 25/25 | 529,025 | 508,535 | 50/50 both |
| R7.2 No-cancel ablation | 25/25; 25/25 | 25/25; 25/25 | 529,014 | 508,535 | 50/50 both |

\*R5.1 Stage2 508,535 is from its complete Run1. Run2 omitted a failed `case_016`, so its 506,754 area sum is **not comparable** as a complete 25-case total.

**Full public QoR conclusion:** Across both paired runs, R7.2 Shortlist and R5.1 produce equal per-case area and delay on every jointly passing case. R7.2 strictly improves exactly one case relative to R7.1 Guard (Stage1 `case_020`) and preserves the other 49. The R7.2 gate is passed, but it **does not yet improve area/delay beyond the Stage1 R5.1 best-known outcome**.

## 4. Structural evidence: `case_020` and `case_016`

### 4.1 Stage 1 case_020 — recovered quality

| Metric | R7.1 Guard | R7.2 Shortlist | Change |
|---|---:|---:|---:|
| Area | 777 | 766 | −11 |
| Delay | 32 | 30 | −2 |
| Gate count | 401 | 388 | −13 |
| AND2 | 176 | 198 | +22 |
| OR2 | 200 | 180 | −20 |
| NOT | 25 | 10 | −15 |
| Official runtime, Run1 (ms) | 10.495 | 10.971 | +0.476 |
| Official runtime, Run2 (ms) | 11.619 | 10.375 | −1.244 |

The input costs are AND2=2, OR2=2, NOT=1 for area, so \(\Delta A=22\cdot 2-20\cdot 2-15\cdot1=-11\). This is an actual reconstructed netlist change; the archived netlist SHA-256 is different. On the first direct trace, the cover-free shortlist search took **0.908 ms**, improved the intermediate area from 796 to 776, and subsequent original postprocessing produced final Area 766 / Delay 30. Independent verification is exhaustive over all \(2^8=256\) assignments.

### 4.2 Stage 2 case_016 — retained safety

| Metric | R5.1 Run1 / Run2 | R7.1 Guard Run1 / Run2 | R7.2 Shortlist Run1 / Run2 |
|---|---|---|---|
| Official runtime (ms) | 95.964 / TIME_LIMIT | 24.199 / 25.650 | **26.486 / 24.726** |
| Area / Delay | 1781 / 36 when PASS | 1781 / 36 | **1781 / 36** |
| Gate count | not archived | 1,120 | 1,120 |

The R7.2 shortlist candidate was **actually run** but not accepted. On its first direct trace it took **1.449 ms** and yielded candidate Area 1866 / Delay 37, worse than the incumbent Area 1781 / Delay 36. The output netlist has the same SHA-256 as R7.1 Guard. Independent verification is exhaustive over all \(2^9=512\) assignments. R7.2's official runtime is only ~25% of the 100ms limit in this particular two-run evaluation, not a hard guarantee on hidden cases.

## 5. Runtime trade-offs

Define the paired runtime ratio \(r_i=T_i^{\mathrm{R7.2}}/T_i^{\mathrm{reference}}\) for cases where both PASS, and geometric mean \(G=\exp(\frac1N\sum_{i=1}^N\ln r_i)\). This avoids overweighting large absolute runtimes. **Values depend on the WSL environment and are descriptive, not significance tests.**

| Reference | Run1 (number comparable / geom. ratio / faster) | Run2 (number comparable / geom. ratio / faster) |
|---|---|---|
| R5.1 | **50 / 0.8328 / 34** | **49 / 0.8152 / 40** |
| R7.1 Guard | **50 / 1.0073 / 23** | **50 / 0.9774 / 32** |

Compared with R5.1, R7.2 is faster by roughly 16.7%–18.5% in the all-stage geometric mean on jointly passing cases. Compared with R7.1, speed differences are small and inconsistent; R7.2 is ~0.7% slower in Run1 and ~2.3% faster in Run2. Its proven contribution over R7.1 is QoR recovery, not a consistent overall speedup.

## 6. What the ablations do *not* demonstrate

The `r72_guard` ablation reproduces the R7.1-style 777/32 on case020; `r72_shortlist` gets 766/30. This supports attributing the quality recovery to the shortlist candidate. But **`r72_nocancel` and `r72_shortlist` have equal area/delay on every public case in both runs**; none of the archived critical direct profiles shows the cooperative deadline being activated. Therefore the experiment does **not** independently demonstrate that the deadline cancellation is necessary, improves performance under a pathological slow candidate, or provides any hard timeout guarantee. That needs a new controlled stress test, not overinterpretation of a null ablation.

Other threats to validity: only two official repetitions, five variants evaluated sequentially (mitigated but not eliminated by reversed order), WSL host scheduling noise, public-data tuning, lack of random held-out evidence in this specific feedback package, no verified hidden-case behavior, unknown course score aggregation. Larger cases are only independently checked through samples in the original local development and by the instructor evaluator here, not exhaustively enumerated in this feedback.

## 7. Milestone decision and next research question

**Accept/freeze Round 7.2 as a current public-feasible algorithm:** 50/50 PASS and target-met twice, no per-case Area/Delay regression versus R7.1, and full recovery of R5.1's known QoR. Preserve its fixed source SHA, original paired reports, and netlists. This is not evidence of globally optimal logic synthesis.

**Stop tuning short-budget thresholds on public cases without new evidence.** A new Round 8 should target *structural area/delay improvements*: e.g., bounded cost-aware cut refactoring, DAG-aware resubstitution / multi-output factoring, and limited alternative representations. Use R7.2 as frozen control, run both stages and independently generated held-out functions, and require meaningful gain relative to the 1,037,549 public full-area baseline with no correctness loss. Compare per-case (not merely total) quality and runtime; avoid investing heavy search in cases with 100ms limits. Use library-based and ABC-inspired work as offline reference, not a presumed drop-in scorer.

**Large-area diagnostic priority, not a scoring claim:** the largest four areas are Stage1 cases 024/025/007/001 = **345,155** (65.24% of Stage1 area) and Stage2 cases 013/005/014/002 = **349,187** (68.67% of Stage2 area). The actual official scoring weights remain unknown and could treat cases differently.

Potential mature-method references (algorithmic inspiration): Berkeley ABC starting page <https://people.eecs.berkeley.edu/~alanmi/abc/starting.htm>; mockturtle cut rewriting <https://mockturtle.readthedocs.io/en/latest/algorithms/cut_rewriting.html>; resubstitution <https://mockturtle.readthedocs.io/en/latest/algorithms/resubstitution.html>. Their native AIG/node metrics do not directly equal the assignment's AND2/OR2/NOT weighted area.

## 8. Evidence provenance

- Original archived official reports: `local_results/run[12]_stage[12]_*.csv`.
- All-variant 50-case paired audit: `Round7_2_Casewise_Audit_20261121.csv`.
- Candidate-level traces: `local_results/diagnostics/*case_020*` and `*case_016*`.
- Reproduction and parameters: `release_snapshot/src/synth_round72.cpp`, `release_snapshot/bootstrap_round72.py`, `release_snapshot/SOURCE_MANIFEST.json`.
- Original experiment `local_results/summary.json` and `local_results/EXPERIMENT_REPORT.md`.
- This document contains analysis performed *after* the 2026-11-21 WSL experiment. It is not an additional official benchmark run.

# UFUG2106 — Round 8.2 Official Benchmark Audit & GitHub Issue #2 Triage

**Date:** 2026-11-21. **Status:** Research gate passed, submission gate NOT asserted; RAM-limited correctness not established.

## 1. Scope and primary evidence

- User-provided `Round8.2_Feedback_20261121_191537_181833.zip`: 20 official CSV files (two stages, 10 variants, two repeats) and full source snapshot. 1,000/1,000 records have `status=PASS` and `target_met=yes`.
- Round 8.2 source SHA-256 `07ca91581854fe3802ae0165674a3352771f1745ea85beee6608ee720f9a1caa`, identical between upload feedback snapshot and delivered Round 8.2 source.
- Repository Issue #2, 2026-11-21, https://github.com/Jincan-LI-HUB/Truth-Table-to-Circuit-Discrete-Math-Project/issues/2, authored by teammate `zdu881`.
- `Final_Project.pdf`: required `n, m, truth table, gate costs, target`; optional line 8 runtime_limit (ms), optional line 9 ram_limit (KB = 1024 bytes). A positive runtime or memory limit is an enforceable validity requirement, not a soft score feature. `0` means no respective limit.

## 2. Controlled comparison, complete 50-case banks

R7.2 reference total Area = **1,037,549** (stage1 529,014, stage2 508,535). The table below sums only complete 50/50 PASS variants.

| Variant | Round 1 Area / Δ vs R7.2 | Round 2 Area / Δ vs R7.2 | Runtime geometric mean ratio (R1/R2) | R1 ADP geometric mean ratio |
|---|---:|---:|---:|---:|
| R7.2 | 1,037,549 / 0 | 1,037,549 / 0 | 1.000 / 1.000 | 1.0000 |
| R8.1 Reverse | 1,029,115 / −8,434 | 1,029,508 / −8,041 | 1.873 / 1.848 | 1.0211 |
| R8.1 Shannon | 1,029,477 / −8,072 | 1,029,874 / −7,675 | 1.354 / 1.369 | 1.0227 |
| R8.2 Fast Stride Area | 1,029,614 / −7,935 | 1,029,814 / −7,735 | 1.323 / 1.389 | 1.0215 |
| R8.2 Fast Priority Area | 1,029,870 / −7,679 | 1,029,724 / −7,825 | 1.462 / 1.425 | 1.0116 |
| R8.2 Dual Area | **1,027,741 / −9,808** | 1,029,168 / −8,381 | 1.575 / 1.576 | 1.0222 |
| R8.2 Fast Slack | 1,035,196 / −2,353 | 1,035,385 / −2,164 | 1.509 / 1.430 | 1.0027 |
| R8.2 Fast ADP | 1,036,029 / −1,520 | 1,036,031 / −1,518 | 1.401 / 1.416 | **0.9987** |
| R8.2 Dual ADP | 1,035,897 / −1,652 | 1,035,895 / −1,654 | 1.515 / 1.566 | **0.9980** |
| R8.2 Dual Strict | 1,037,150 / −399 | 1,037,157 / −392 | 1.548 / 1.545 | **0.9987** |

All variants passed 50/50 and met 50/50 target in both runs; **the official scoring formula is not established**. ADP and area aggregate are *diagnostic proxies only*. An ADP geometric mean of >1 signifies worse multiplicative Area×Delay compared to R7.2.

Interpretation:

1. Dual Area achieved the largest area reduction in run1 (9,808; ~0.945%), but this was not replicated in run2 (8,381; ~0.808%). Run2's stage2 Dual Area = 502,853, worse than stage2 R8.1 Reverse's 502,753. The dramatic drift is mainly stage2 `case_003` 16,642→17,314 (672) and `case_005` 109,218→109,844 (626). Hence area-only branch is not yet reproducible enough to freeze.
2. Root priority vs stride is inconclusive. Priority total area was worse by 256 in run1, better by 90 in run2, and had higher geometric-mean runtime in both (1.188x, 1.047x relative to stride). This does not establish a general improvement.
3. Delay-sensitive configurations produce much smaller area savings but better ADP proxies. Dual Strict has 21/50 strict Area–Delay Pareto improvements and **zero delay regressions** in run1. Dual Area has 26 area improvements but **5 area-vs-delay tradeoffs**.
4. `case_016` remains PASS: R8.2 variants measured 52–66ms in this run (100ms case limit), but that only establishes an observed margin, not hard deadline guarantees or memory safety.

## 3. Source-backed memory issue (#2)

Issue #2 is titled **“Round 5.1 integration: check row-buffer RAM before starting an optional candidate.”** Its *integrated executable* memory measurement was peak **13,952 KiB** for a 20-input, one-output wire circuit with RAM cap **9,000 KiB**.

The supplied standalone Round8.2 source still has:

- `int main` reads a single optional `long long limit` token (runtime limit), **does not parse the additional RAM limit token**.
- `run_synth` constructs a new BDD order with `vector<size_t> orig(N)` and `vector<int> cur(N),next`, where `N=2^n`.
- BDD node and hash-table reservations also scale with N. The *first* BDD candidate can exceed strict RAM caps; skipping optional candidates alone is insufficient.
- Main loop starts subsequent candidates even after `Area=0, Delay=0`, which is already globally optimal for positive-cost gates.

**Independent local reproduction (not the official evaluator):** The exact Round8.2 source compiled on local Linux processed a 20-input, one-output wire test with 0ms runtime limit and 9,000KiB RAM limit. It wrote the correct netlist `20`, reported `completed=4 chosen=0 area=0 delay=0`, and had **PEAK_RSS_KB=34132** under `/usr/bin/time`. This independently supports the concern, and shows peak memory risk can occur even when the output circuit is trivial. These results are not meant to be compared numerically to the teammate's different integrated executable.

The test file is deterministically regenerated using `generate_issue2_case.py`; do not use case-name conditionals in the solver. `repro_issue2.sh` only measures RSS and does **not** enforce the RAM cap; use official evaluator to establish PASS/FAIL.

## 4. Remediation order and research design

### Immediately next: Round 8.2.1 — Memory/Resource Compliance Hotfix

**Gate A: parser semantics.** Accept independent optional runtime and memory bounds. Omitted/zero limits are unlimited. Robustly handle out-of-range parsing. Report resource limits in profiling, not output netlists.

**Gate B: low-memory semantics-preserving preflight.** While streaming rows, recognize constants, primary-input literals, complemented literals, and direct shared outputs. These functions have exact small circuits; a `y=x19` can be emitted without BDD construction, using negligible scratch memory. Do not overfit to any testcase name or n=20 special case. If all outputs are realizable in such a low-memory network and it is feasible, stop immediately. A *zero area, zero delay* circuit is globally optimal for positive gate costs, so no optional candidate should be run afterward.

**Gate C: resource-aware candidate admission.** Before the first BDD as well as every optional alternative, conservatively account for *all* major allocations: truth tables, `orig`, both row buffers, BDD nodes, buckets/hash objects, caches, final graph. The current `orig` and `cur` alone require (8+4) MiB at n=20, already over 9,000 KiB, and the full builder can allocate more. A mere current-RSS check just before allocations is insufficient. Avoid large eager reserves or use an explicitly low-memory synthesis fallback. An estimator is only a guard; validate peak with actual evaluator and OS RSS measurements.

**Gate D: tests.** `n=20, m=1, y=x19, runtime=0, ram=9000`; identical input with both limits; constants/multiple wires; a nontrivial 20-input output under a realistic memory cap; tests with absent/0 RAM cap; real Stage1 and Stage2 50-case paired regression, area/delay/runtime and peak RAM. Include at least one case with neither limit and one with both.

**Exit criterion:** release only when RAM-limited reproducible tests pass under official evaluator, all 50 public cases PASS + target met, no unexpected area or delay regressions, and feedback ZIP always includes memory profiles. It is not enough merely to accept an input ninth field.

### Round 8.3 — Optimization Portfolio Efficiency

After correctness is safe, evaluate whether the integrated solver loses search budget under a numeric limit and whether valid fallback choices are unnecessarily suppressed. The teammate reports `99,068→93,786` area on Stage2 case005 with **modified target=10^9, runtime=1000ms**, representing a 5.33% improvement within their integrated setup. This is **not** an official result for the released Stage2 case005; do not assume it transfers to the standalone solver. A dedicated 2×2 ablation should isolate independent RAM guard changes and budget reallocation.

### Final build packaging / README

The issue's README request is real but lower urgency than RAM validity. Carry it forward as a reproducible fresh-checkout build + launch test, ideally before the final submission freeze.

## 5. Proposed evidence / paper narrative

The present experiment supports *feasibility of time-aware, area-aware search under normal released limits*, not compliance with the general resource-constrained task definition. A rigorous paper can discuss three separable contributions: (i) successful area-versus-delay search; (ii) runtime throughput and portfolio scheduling; (iii) validity safeguards for explicit memory constraints. Report the 9,000KiB counterexample and its eventual fix as a systems-correctness finding, not an achieved area improvement. Keep area-only branches and delay-aware branches in a Pareto archive until the true scoring function is established.

**Sources:** original feedback CSV and source snapshot; course PDF; teammate's GitHub Issue #2; local reproducibility test. No GitHub issue comments or repository changes were made during this audit.

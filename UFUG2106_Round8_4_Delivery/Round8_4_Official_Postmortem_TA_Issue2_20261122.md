# UFUG2106 Round 8.4: official postmortem, teammate Issue #2, and TA clarification

Date: 2026-11-22. Evidence: `Round8.4_Feedback_20261122_161803_496295372.zip`; direct inspection of the archived C++ sources, 40 official CSVs, and `summary.json`; teammate GitHub issue #2; TA email supplied in the conversation. The official report and feedback archive are not replacements for the final grading run.

## 1. Scope and basic validity

- 10 configurations × 2 runs × 2 stages × 25 cases = **1,000 official case records**.
- **1,000/1,000 PASS** and **1,000/1,000 Target Met** on publicly released cases.
- Runner platform: WSL2 Linux 6.6.87.2; official evaluator fingerprint `142361d7ce18bc47dea6a07538db79a588b3afbf446526c1d1246f4968b3d0ca`.
- Official results depend on machine load and wall-clock search budgets. All 50 public cases are development data given repeated adaptation. The hidden 50 are not represented by these results.

## 2. Comparison with frozen R8.2.1 Dual Area

Area sums cover all 50 published cases, not a competition score. Runtime ratio is paired per-case geometric mean vs R8.2.1 in the same run.

| Configuration | Run 1 area | Run 2 area | Mean area | R2/R1 identical-area cases | Approx. relative runtime |
|---|---:|---:|---:|---:|---:|
| R8.2.1 dual area | 1,029,055 | 1,029,462 | 1,029,258.5 | 45/50 | 1.000× |
| R8.3 stable dual | 1,028,979 | 1,030,184 | 1,029,581.5 | 47/50 | 1.007× |
| R8.3 dense dual | 1,029,291 | 1,029,805 | 1,029,548.0 | 47/50 | 1.056× |
| R8.4 topology dual | 1,028,477 | 1,030,391 | 1,029,434.0 | 47/50 | 1.006× |
| R8.4 mixed33 dual | 1,029,557 | 1,029,592 | 1,029,574.5 | 49/50 | 1.048× |
| R8.4 mixed66 dual | 1,028,780 | 1,028,775 | 1,028,777.5 | 49/50 | 1.065× |
| R8.4 topq dual | 1,027,395 | 1,027,216 | 1,027,305.5 | 47/50 | 1.041× |
| R8.4 topq dense | 1,026,512 | 1,027,572 | **1,027,042.0** | 47/50 | 1.085× |
| R8.4 adaptive dual | 1,029,081 | **1,025,968** | 1,027,524.5 | 45/50 | 1.042× |
| R8.4 topq ADP | 1,036,036 | 1,036,036 | 1,036,036.0 | **50/50** | 1.062× |

**Key qualifications:**

1. TopQ Dense has the lowest *two-run mean area*, but its two-run difference is 1,060 area units. It is not an unqualified winner.
2. TopQ Dual uses less time than TopQ Dense on average (roughly +4% vs baseline rather than +8.5%) and has a slightly worse mean area; neither dominates the other in computation/area trade-off.
3. Mixed66 is notably consistent (49/50 area-matched) but sacrifices most of the area improvement found by TopQ Dense/Dual. Exact delay is a separate axis.
4. Only TopQ ADP has 50/50 cross-run area/ delay agreement; it has lower total delay (2,278 vs R8.2.1 2,346) but much higher total area (1,036,036 vs about 1,029,259). ADP is not known to be the official scoring formula.
5. R8.3 Stable Dual was 50/50 area-stable in its previous paired experiment but was only 47/50 in this more demanding evaluation. A deterministic root *quota* does not ensure deterministic final output when upstream candidate selection or wall-time guards remain.
6. The previous local Round8.4 TopQ and Mixed66 improvements do **not** reliably reproduce at the same absolute size under the official evaluator. Preflight critical cases include multiple `wall_hit=True` events, consistent with budget sensitivity; it is not a unique proof of the cause.
7. All recorded delay values are identical between Run 1 and Run 2 *within each configuration*. This does not imply they equal another configuration's delay values.

## 3. TA announcement: authoritative revision of grading assumptions

The TA email furnished by the user confirms:

- Reported benchmark results are *required for method/improvement discussion*, but **do not directly contribute to the performance score**; performances from different groups' development machines cannot be compared directly.
- Final performance is measured by running **Stage 2 source code** on the grading server against 50 public and 50 hidden cases.
- There is **no per-case `ram_limit`** in Stage 1, Stage 2, or hidden cases. They recommend omitting it from self-created development tests to match grading conditions.
- The grading server has **48 GiB of total RAM**, not an express exclusive per-process guarantee.

This resolves the grading *relevance* of the synthetic 9,000-KiB repro; it does not prove the `MEMORY_LIMIT` accounting issue was fixed or specify which metric the local evaluator uses.

## 4. GitHub issue #2 disposition, checked against archived Round8.4 source

GitHub issue: https://github.com/Jincan-LI-HUB/Truth-Table-to-Circuit-Discrete-Math-Project/issues/2 — currently Open with zero comments at review time. The teammate's issue contains three distinct suggestions.

**A. RAM scratch / 0-gate early stop (partial in modern standalone; NOT backported to frozen R5.1):**

- `src/synth_round84.cpp` reads `limit, ram_kb` near line 954 and calls the `r821::compact_probe` fallback when a positive RAM cap precludes a large BDD allocation.
- After at least one candidate it returns immediately if a feasible incumbent has area=0 and delay=0 (around line 1089).
- The original row-buffer allocations are **still present** in full BDD paths (`vector<size_t> orig(N)` and `vector<int> cur(N)` near lines 286/292 and 754/755 in the archived Round8.4 derived source).
- The frozen historical `UFUG2106_Round5.1_Delivery/src/synth_round51.cpp` was not modified. Neither its historical issue nor the integrated team's program can be declared fixed merely because later standalone descendants contain safeguards.
- The positive-RAM official evaluator reported `MEMORY_LIMIT` even for a tiny C program; this is an unresolved accounting discrepancy, not proof that all possible memory paths pass.

**B. Integrated BDD full-budget decision under exclusion of R5.1 (not verified / not implemented as the issue requests):**

- This is an integration/scheduler change for the teammate's Stage 2 solver. The standalone research descendants still implement their own dispatch/time caps; their public benchmarks do not establish that the team's BDD program receives full budget under the quoted numeric conditions.
- The teammate's area improvement (99,068 -> 93,786) was measured on a *modified target delay* of 1,000,000,000 and a 1,000-ms runtime cap; it is useful development evidence but should not be reported as an official-case improvement.

**C. README reproducible from a fresh checkout (partial only):**

- The archived Round8.4 README states that its experiment expects the frozen Round8.3 and Round8.2.1 folders plus an authentic `evaluator` and two public data banks. A freshly cloned repository without the expected artifacts has not been shown to run without extra preparation.
- Current exported Round8.4 source is available for inspection, but a *final self-contained Stage 2 delivery plus clean-checkout test* remains to be demonstrated.

**Conclusion:** do **not** close Issue #2 as fully resolved. It is reasonable to respond that some memory-safety mechanisms were implemented in later standalone descendants, and request verification/patch integration in the team's actual solver; both the BDD budget and reproducible clean-checkout criteria remain open.

## 5. Development roadmap revised in light of grading clarification

**P0: Final Stage 2 deliverable assurance (near-term).** Confirm exact source/dependency bundle, clean build on an Ubuntu 22.04-like environment, `./program input_path output_path`, no dependence on the project's frozen-history folders, and 100% public PASS/Target Met. Detect/avoid inadvertent environment variables that turn on optional ablation behavior.

**P1: Hidden-case generalization and wall-budget reliability.** Work on reproducible candidate selection and backup outputs. Keep Round8.2.1 and TopQ Dual/Dense as separate frozen comparators. Do not tune to named public cases. Use newly locked holdout functions with varied sizes, output counts, target delays, and gate costs. Test multiple repeated runs and response to busy-host conditions. Record search wall-hit frequencies, root-work counts and end-to-end time headroom.

**P2: Memory profiling as an efficiency optimization, not a grading-cap workaround.** Measure peak RSS on representative large-input and high-output synthetic cases in an uncontaminated process; separate mandatory truth-table storage, row permutation arrays, BDD nodes/unique tables, speculative graph clones and cache residency. Compare allocation pooling, buffer reuse, packed storage, and bounded cache strategies. Prefer changes that keep Area/Delay/netlist equal before considering memory-capped search that trades away candidate quality. Maintain the low-memory path for spec compliance even though official grading will not exercise a positive `ram_limit` per the latest TA email.

**P3: Exact score-based choice.** Request/verify how the grading server weights area vs delay among target-feasible circuits; do not optimize an assumed Area*Delay formula as if it were official. Produce Pareto comparisons for observed candidates and report limitations candidly.

## 6. Source provenance

- Exact uploaded feedback ZIP: `Round8.4_Feedback_20261122_161803_496295372.zip`.
- Extracted source: `source/src/synth_round84.cpp`, `source/src/r821_resource.hpp`, `source/README.md`, `experiment/official/summary.json`.
- Comparative CSV outputs generated from 40 official CSVs: `Round8_4_Casewise_Official_1000.csv`, `Round8_4_Official_Comparative_Summary.csv`.
- Team issue #2 read live via connected GitHub, not inferred from only the prompt.


# UFUG2106 Round 10.1 — Official paired performance audit

**Audit date:** 2026-11-22  
**Uploaded evidence:** `Round10.1_Feedback_20261122_124252_511091.zip`  
**Scope:** Genuine course evaluator on all 25 Stage 1 and 25 Stage 2 public cases, two reversed-order runs, seven configurations; **700/700 PASS and 700/700 target met**. Hidden cases were not tested.

## 1. Decision

**NO-GO for R10.1 budget reductions.** Retain the exact frozen R10.0 Repeat SOP (160 roots, nominal 90ms cap, with existing guard conditions) as the primary low-area Stage 2 candidate. Retain R9.0 (Repeat SOP off) as the lower-runtime fallback. Do **not** promote the trial `synth_round101.cpp` / `trial_submission` solely because it ties the baseline: it adds an unused environment-controlled experimental budget setting and has no demonstrated robust benefit.

## 2. Exact official aggregated results

All values below are **for one run**; both runs produced identical Area and Delay totals in every policy. Runtime geometric means are evaluated on 100 paired observations (50 cases × two runs) relative to the *same Stage, same case, same run* of frozen R10.0. Ratios below 1 favor the candidate. Note: unweighted area sums are a diagnostic, **not the course's score**.

| Config | Stage 1 Area | Stage 2 Area | Combined Area | Combined Delay | Area lost vs R10.0 | Paired runtime ratio | Case-wise Area regressions / 50 |
|---|---:|---:|---:|---:|---:|---:|---:|
| Frozen R10.0 | 525,582 | 493,965 | **1,019,547** | 2,382 | 0 | 1.000000 | 0 |
| R10.1 default | 525,582 | 493,965 | **1,019,547** | 2,382 | 0 | 0.999096 | 0 |
| R10.1 80 roots | 525,794 | 494,355 | 1,020,149 | 2,382 | **602** | 0.991734 | 6 |
| R10.1 40 roots | 525,934 | 494,621 | 1,020,555 | 2,382 | **1,008** | 0.997390 | 6 |
| R10.1 45ms budget | 525,582 | 494,206 | 1,019,788 | 2,382 | **241** | 1.007051 | 1 |
| R10.1 off (R9.0-style) | 526,135 | 494,999 | 1,021,134 | 2,382 | **1,587** | **0.954324** | 8 |
| Trial submission | 525,582 | 493,965 | **1,019,547** | 2,382 | 0 | 1.015062 | 0 |

All policies passed every official public case, with 25/25 Target Met per Stage in both runs. Source-only cold builds and 42/42 exhaustive local preflight tests also passed.

## 3. Source integrity

Frozen R10.0 source (`bundle/src/synth_round100_frozen.cpp`) SHA-256: `8c863f1a1c9555ae571948a0424c25642c29c9a9f98f1f3e5f193c6b20f5b15d`.

R10.1 trial source (`bundle/src/synth_round101.cpp`) SHA-256: `ad5e1becdab1952a77a0e445dd17fa4bc45301d021d3dfc01154410844d8a568`.

R10.1 trial submission (`bundle/trial_submission/synth.cpp`) is byte-identical to the R10.1 trial source. **The R10.0 freeze is the prior source snapshot, not the new trial source.** Preserve its accompanying 12 headers in submission packaging.

## 4. Mechanism checks and individual regressions

### 80-root cap loses area on six public cases (each repeated twice)

| Stage | Case | Area at frozen R10.0 | Area at 80-root cap | Additional Area |
|---|---|---:|---:|---:|
| Stage 1 | 010 | 3,037 | 3,161 | +124 |
| Stage 1 | 012 | 3,763 | 3,851 | +88 |
| Stage 2 | 003 | 15,623 | 15,706 | +83 |
| Stage 2 | 005 | 102,889 | 103,142 | +253 |
| Stage 2 | 012 | 4,143 | 4,145 | +2 |
| Stage 2 | 023 | 1,904 | 1,956 | +52 |

These cases account exactly for 602 additional Area per run. Notably, Stage 2 case 005 contributes 253/602 (~42.0%) of the degradation.

- **40 roots:** six cases likewise regress, combined +1,008 Area per run; barely changes geometric runtime (0.997390).
- **45ms nominal cap:** only Stage 2 case 005 changes (+241 Area per run). Geometric runtime **worsens** to 1.007051, so reducing a nominal search allowance does not establish a wall-clock saving.
- **Off:** reverses all eight public-case benefits of Repeat SOP, sacrificing 1,587 Area per run, but cuts paired geometric runtime by ~4.57%.

In all cases, observed circuit Delay is unchanged. The area losses are *between separate program invocations*, and do not mean a rewrite is incorrectly accepting a locally area-worsening candidate.

## 5. How strong is the 80-root runtime gain?

For each of the **50 public (Stage, Case)** units, average the log runtime ratio across the two runs, then independently resample those 50 case units with replacement for a **descriptive** nonparametric bootstrap (25,000 draws, fixed seed 20261122).

| Policy | Geometric runtime ratio | Descriptive resampling 95% interval |
|---|---:|---:|
| 80 roots | 0.991734 | [0.9737, 1.0111] |
| 40 roots | 0.997390 | [0.9790, 1.0173] |
| 45ms budget | 1.007051 | [0.9876, 1.0252] |
| Off | 0.954324 | [0.9387, 0.9714] |

These are **not statistical confidence intervals for hidden tests**: public cases were not randomly sampled from the unknown grading distribution, and the WSL scheduling effects are uncontrolled. They illustrate that the 80-root ~0.83% advantage is smaller than case-to-case and run-to-run timing variability; there is no robust evidence for promotion.

Additional warning: Stage 1 case 024 took 2451.048ms in R10.1 default run 2, while the frozen control measured 1688.449ms; both passed. The 100-case timing profile is noisy even with identical Area/Delay.

## 6. Submission and remaining risks

- **Freeze:** R10.0 source + exactly matching 12 headers, no environment flags required, default Repeat SOP.
- **Fallback:** R9.0 source with the Repeat SOP disabled; retain versioned, testable snapshot.
- **Avoid:** promoting R10.1 trial code and any cap/budget tuning to the final default.
- **Open risks:** Unknown area/delay/runtime weighting in the final grading formula; 50 hidden cases not observed; potential wall-clock sensitivity on other systems; one separate teammate Issue #2 BDD budget proposal has not been merged/verified; check final submission interface and packaging against course instructions.
- **Recommended final action:** complete a one-time source-only build + official 50 public cases + existing 100ms stress fixtures + one untouched independent test bank; write final Stage 2 README and report; stop parameter tuning unless a reproducible correctness or hard-timeout regression appears.

## 7. Evidence

- User-uploaded 141-entry feedback ZIP, with 28 official raw CSVs (seven policies × two stages × two runs), each holding 25 rows.
- `bundle/results/20261122_123551_337516131/official/paired_policy_summary.csv`.
- `bundle/results/20261122_123551_337516131/official/paired_runtime_area_delay.csv`.
- `bundle/results/20261122_123551_337516131/official/summary.json`.
- `/mnt/data/R101_casewise_reconstructed_700.csv` is an exact normalized extraction of official raw CSVs for independent re-analysis.

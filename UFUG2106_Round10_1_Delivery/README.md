# UFUG2106 — Round 10.1: Area–Delay–Runtime Performance Audit

**Status:** experimental performance audit; **R10.0 remains the default Stage 2 frozen candidate**. No hidden-case performance claim.

## Purpose

Isolate the incremental value and runtime risk of the optional Repeat SOP pass from Round 10.0. The original successful solver and its 12 headers are preserved unchanged as `src/synth_round100_frozen.cpp` and `frozen_submission/`. A minimally modified trial solver only adds an **opt-in** time-budget cap, while the existing `UFUG_R91_ROOT_CAP` controls work quota. The trial default is still 160 roots and 90ms nominal budget; no new Boolean rewrites or case-specific selectors are introduced.

## Commands for WSL

Unzip `UFUG2106_Round10_1_Delivery.zip` beside `evaluator`, `data/stage1`, and `data/stage2` in the original `Final Project` root.

```bash
BASE="/mnt/e/canfiles/Common courses study/大学通识/26-27 Fall/UFUG 2106 Discrete Math/assignment/Final Project"
cd "$BASE" || exit 1
bash UFUG2106_Round10_1_Delivery/run_round101.sh
```

Runs **7 configurations × 2 stages × 2 runs × 25 cases = 700 official public evaluations**, with reversed policy order in run 2. `--quick` runs 4 configurations × 2 stages × 1 run = 200 evaluations, preceded by a compact correctness preflight. `--local-only` runs the preflight without invoking the evaluator.

Automatically packages `feedback/Round10.1_Feedback_<UTC stamp>.zip` on both success and failure; **upload only this feedback ZIP** for the decision review.

## Comparison design

| Policy | Source | Repeat SOP root quota | Nominal extra-pass budget | Role |
|---|---|---:|---:|---|
| `r100_frozen` | exact R10.0 | 160 | min(90 ms, 6% total limit, remaining) | Historical default |
| `r101_default` | trial R10.1 | 160 | identical | Source-patch isolation |
| `r101_cap80` | trial R10.1 | 80 | identical | Less search work |
| `r101_cap40` | trial R10.1 | 40 | identical | More aggressive reduction |
| `r101_budget45` | trial R10.1 | 160 | min(45 ms, 6% total limit, remaining) | Shorter nominal time allowance |
| `r101_off` | trial R10.1 | none | none | True fallback |
| `trial_submission` | independent trial source-only | 160 | identical | Cold-build and deployment parity |

The **budget is cooperative**, not a hard wall-clock cutoff; an individual expensive candidate may overshoot. The program's `runtime_limit` remains unchanged, and only the real course evaluator can confirm its official handling. Positive RAM limits are not set in the official public or hidden grading cases per TA clarification.

## What has been established locally (NOT official)

- The original official Round10.0 feedback contains 600/600 PASS and Target Met. On each public-bank run, Repeat SOP improves 8/50 cases, saves 1,587 total weighted Area, and leaves Delay Sum unchanged. Runtime has a measurable cost, but the source program's earlier time-sensitive search creates substantial timing noise.
- One new local Stage2 sweep (25 real public cases × four quotas) achieved **100/100 exhaustive Boolean-equivalence checks**. At quota 160, 17/25 cases executed the extra pass, 7 accepted an improved graph, 10 executed with no final area reduction, and 8 never entered the pass. The 25-case Area sums vary by quota but are **not a ranking supported by official grader hardware**.
- The default Stage 2 freeze **does not change** in R10.1. To promote a reduced-budget variant, demand paired official results, acceptable timeout tail, no hidden-style holdout regression, and a meaningful runtime gain over R10.0. Otherwise R10.0 stands.

## Deliverable contents

- `src/synth_round100_frozen.cpp`: exact R10.0 source.
- `src/synth_round101.cpp`: trial source with opt-in nominal time cap (default unchanged).
- `frozen_submission/`: independent R10.0 default source + local headers.
- `trial_submission/`: trial source + local headers, independent compilation.
- `evidence/official_r100_vs_r90_casewise_100.csv`: 100 paired official public observations from prior feedback.
- `evidence/local_stage2_cap_ablation_100.csv`: actual new local full-truth-table evidence.
- `docs/01_CAUSAL_AUDIT.md`: motivation, mathematics, confounders and negative results.
- `docs/02_RELEASE_DECISION.md`: precise stop/go decision and handover for final submission.
- `SOURCE_MANIFEST.json`: SHA-256 of frozen and trial sources and other files.

## Runtime is still part of performance

For a valid submitted circuit, the course grades weighted area, delay, and runtime. The PDF does **not** publish an explicit combined formula. No single metric alone selects the best grading strategy. In particular, one smaller Area Sum on 50 public cases **does not certify a better final score**.

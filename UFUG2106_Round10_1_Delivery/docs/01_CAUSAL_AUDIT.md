# R10.1 — Causal audit of Repeat SOP search budget

## 1. Research question and estimand

Let \(B\) be the valid best circuit before the optional Repeat SOP pass and \(P_q(B)\) the candidate from a repeat pass with work quota \(q\). The solver commits the candidate only if it is valid and

\[
A(P_q(B)) < A(B),\qquad D(P_q(B))\le D_{\mathrm{target}}.
\]

This property protects area relative to the **incumbent produced by that same program invocation**, but not necessarily across different invocations: the time-limited earlier search may have returned different \(B\)'s. Therefore the comparison `Area(cap40) > Area(off)` on one busy host does **not** prove the post-pass accepted an area-increasing rewrite.

Search-time economics requires measuring both accepted global area reduction and actual extra search time. A useful diagnostic is the count of executed-but-not-accepted passes and their accumulated `R91_POST ms`, not merely the difference between total process times of two independent executions.

## 2. Parent code, exact safeguards

Source `src/synth_round100_frozen.cpp` is SHA-pinned. Default Repeat SOP is only considered if `runtime_limit >= 1000`, a valid target-meeting incumbent exists, and the estimated available time is sufficient (at least 8ms). Its nominal per-pass allowance is

\[
\min\bigl(90\text{ ms},\; 0.06 T_{\mathrm{limit}},\;0.82T_{\mathrm{limit}}-T_{\mathrm{used}}\bigr).
\]

The original library pass is not enabled. Original root cap is 160. The trial modifies only the optional 90ms term under the environment variable `UFUG_R101_BUDGET_CAP_MS`; with no environment variable it remains 90ms. The original `UFUG_R91_ROOT_CAP` sets work quota, clamped to [20,400].

## 3. Official parent evidence

Source: genuine course evaluator CSVs inside `Round10.0_Feedback_20261122_121200_917768.zip` (100 paired comparisons, 2 runs × 50 cases). Each run: 50/50 PASS for frozen R9.0 and R10.0; area savings **1,587** across **8/50** cases; Delay Sum unchanged. Paired runtime ratio geometric mean is about **1.0166** for R10.0 default vs R9.0 in that batch. This is a difference in observed total runtime, **not** an isolated measurement of optional SOP pass duration. Only the grader knows the combined score formula.

## 4. Local controlled sweep: actual Stage2 public cases

25 actual Stage2 inputs × 4 configurations (off/40/80/160), a single host, one execution each, reverse quota order on alternating case IDs. Each of **100/100 output netlists** was exhaustively verified over all \(2^n\) assignments and met the target delay.

| Quota | Local Stage2 Area Sum | Delay Sum | Entered Repeat SOP | Accepted improvement | `budget_hit` |
|---|---:|---:|---:|---:|---:|
| Off | 501,744 | 1,170 | 0 | 0 | 0 |
| 40 | 501,349 | 1,170 | 17 | 6 | 0 |
| 80 | 500,672 | 1,170 | 17 | 6 | 1 |
| 160 | 500,652 | 1,170 | 17 | 7 | 2 |

At quota 160, the 17 executed post-passes cumulatively consumed about **925ms**, 10/17 did not result in an accepted Area reduction, and 8/25 cases did not enter the pass. A few cases show area variation from the **prior** time-based synthesis phase; a single local sweep is not strong evidence for choosing quota 80 over 160.

Important negative example: Stage2 case005 under quota40 produces greater final Area than that case's separate invocation with postprocessing off. The post code only accepts strictly smaller global Area than its own invocation's incumbent. Thus **the baseline incumbent differed**, demonstrating why independent wall-clock comparisons can be confounded.

## 5. Research trade-off and rejection rules

- `cap40` or `cap80` may save candidate work, but could miss late beneficial Cuts. Since case003 and case023 benefit from late candidates locally, lower cap can lose Area.
- `budget45` limits only nominal allowance: the rewrite routine polls time cooperatively, and a single expensive root may overshoot. It is not a hard execution cutoff and cannot guarantee a stricter `runtime_limit`.
- Do not use public case IDs as a classifier; such a predictor would overfit and violate the generality goal.
- Never report all cases with unchanged Area as "wasted search" without checking whether the post-pass actually ran.
- Never use the sum of area alone as the course's final grading function.

## 6. Final decision gate

The actual WSL official evaluator comparison must meet: all stages 25/25 PASS and Target Met; no new short-runtime failure; stable paired Area/Delay (two reverse-order runs); meaningful paired Runtime reduction; and acceptable overall Area loss measured on original banks and separate unseen stress functions. If no robust Pareto improvement, keep R10.0 unchanged. The trial source is **not** promoted by this package.

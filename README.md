# Truth Table to Circuit

**UFUG2106 Discrete Mathematics · HKUST (Guangzhou)**  
**Stage 1–Stage 2 Boolean synthesis: source, experiments, and research reports**

**Contributors:** Jincan LI and Zeyun DU (Group 2)  
**Core implementation:** C++17 · **Evaluation/research tools:** Python 3, shell scripts, LaTeX

[**Quick Start**](QUICK_START.md) · [**Final Project Report (PDF)**](Stage%202%20Formal%20Report/main.pdf) · [**Unified Research Trial Log (PDF)**](Stage%202%20Formal%20Report/Research_Trial_Log/UFUG2106_Stage2_Research_Trial_Log_v3.pdf) · [**Integrated Final**](Final_Submission_by_Zeyun_DU/) · [**Course specification**](Final_Project.pdf)

## Attribution and Publication Notice

This repository documents the collaborative research and implementation of the UFUG2106 Discrete Mathematics Group 2 project.

The integrated Stage 2 solver and associated team-authored research materials are archived on GitHub with the permission of the team members. Original authorship, algorithmic contributions, upstream references, and source provenance are explicitly preserved.

The corresponding team repository is maintained by [Zeyun Du](https://github.com/zdu881/UFUG2106-Project), with the archived integration pinned to commit [`59e3350`](https://github.com/zdu881/UFUG2106-Project/commit/59e33505616d127fc06a63580ca3ae3c34d1da72).

Instructor-provided specifications, evaluation tools, and benchmark datasets are included for academic documentation and experimental reproducibility. All applicable intellectual property rights remain with their respective rights holders. No ownership or general redistribution license over third-party materials is claimed. 

## Overview

The project synthesizes a **functionally equivalent, acyclic multi-output combinational circuit** from a complete Boolean truth table. The generated netlist uses only `AND2`, `OR2`, and `NOT` gates, and must respect per-instance gate costs and synthesis resource limits. The principal circuit-quality measures are:

- **Area:** sum of the given area costs of the emitted gates;
- **Circuit delay:** longest output-path delay under the given gate-delay costs;
- **Synthesis runtime / memory:** resources used by the synthesis *program*, not by the circuit.

Functional validity (`PASS`) and satisfaction of the target delay are distinct evaluator outcomes. The project does not assume an undisclosed grading formula or claim globally minimum circuit area.

## Integrated Final

Zeyun Du's integrated Stage 2 solver is the final team version planned for submission. The archive pins the source to `59e3350` and preserves its provenance, build instructions, and public test records. The integration adapts J51 mapping and R10.0 cut rewriting and adds its own variable-order scheduling, shared-output selection, and timing recovery. The course submission status is unverified. [Zeyun Du’s original repository](https://github.com/zdu881/UFUG2106-Project) · [Pinned integration commit](https://github.com/zdu881/UFUG2106-Project/commit/59e33505616d127fc06a63580ca3ae3c34d1da72) · [Source and build](Final_Submission_by_Zeyun_DU/) · [Integration audit and matched evaluation](Final_Submission_by_Zeyun_DU/integration/AUDIT.md)

The executable first completes a natural-order BDD mapping, then schedules BDD order screening and the imported J51 portfolio. It ranks complete shared DAGs against a one-unit internal delay reserve. When admitted, it mixes output cones, polishes cuts with the inherited SOP mapper, explores shared factors and repairs late paths. An output still late to the stated target can trigger exact cofactor reconstruction. [Integrated source](Final_Submission_by_Zeyun_DU/src/synth_stage2.cpp) · [Formal Report](Stage%202%20Formal%20Report/main.pdf)

In both matched repeats, **all four solvers passed all 50 released cases and met every delay target**. Integrated Final had at least one delay unit of slack on each public case. It reduced aggregate area by **22.6% versus Z1** and **14.4% versus R10.0**, using **2.14–2.20× R10.0's summed synthesis time**. Independent replay checked all 100 integrated netlists. The comparison measures the architecture and its search budget together. [Matched results](Final_Submission_by_Zeyun_DU/integration/data/public_summary.csv) · [Paired results](Final_Submission_by_Zeyun_DU/integration/data/matched_pairs.csv)

![Matched repeat 1 whole-system area and time, alongside timing-slack distributions](Stage%202%20Formal%20Report/figures/phase_c_systems.png)

Each of J51, R10.0 and Integrated Final used less total time and weighted area than Z1 in both matched repeats. Integrated Final used the least area, and J51 the least total time. These two metrics omit per-case margin and limit exposure. The matched case data also show that 43 of 50 cases improve in area relative to R10.0, while the three largest gains supply 60.75% of repeat 1's gross savings. In each repeat, nine cases improve both weighted area and circuit delay, twelve reduce area at equal delay, and twenty-two reduce area with higher delay. The 22 slower circuits still meet their individual delay targets.

![Absolute, cumulative and bank-level weighted-area contributions relative to R10.0](Stage%202%20Formal%20Report/figures/phase_c_contributions.png)

The upstream ZIP acceptance runs separately passed all 50 public cases and targets in each of three repeats, with total areas of 884,234, 876,694, and 876,694. The upstream freeze record lists 168/168 targets on the development banks, 55/56 on four designated validation banks, and 28/28 on two banks generated after the final ZIP freeze. The four validation banks were prospective in one snapshot and labeled development in the later extended-window snapshot. The freeze grouping preserves their upstream designation. Across the six banks, 83/84 targets were met in 72 generated networks and twelve observations of two repeated exact-delay controls. One generated case remains late at delay 28 against target 27. [Upstream public results](Final_Submission_by_Zeyun_DU/reports/stage2-timing-20261124/public-runs.csv) · [Generated case and witness](Final_Submission_by_Zeyun_DU/reports/stage2-timing-20261124/residual.csv)

## Independent Stage 2 research freeze — R10.0

R10.0 is the selected solver from Jincan Li's independent Stage 2 research. Its bounded cut mapper and repeat-SOP settings carry into Integrated Final. The original controller and controlled experiments remain documented in the independent delivery and the unified trial log. [Frozen R10.0 source](UFUG2106_Round10_0_Delivery/submission/) · [Full delivery](UFUG2106_Round10_0_Delivery/)

### Main approach

1. **Exact construction and representation diversity:** build candidate circuits through Shannon/BDD-based plans and other available Boolean forms; detect simple structures where the time/resource budget warrants a specialized path.
2. **Cost-aware mapped network:** map to permitted gates, share reusable signals with structural hashing, and recover circuit timing/area on the output-reachable DAG.
3. **Bounded four-leaf rewriting:** represent cut functions by complete truth signatures; explore SOP- and Shannon-oriented alternatives subject to pruning and resource checks.
4. **Global selection and guarded refinement:** compare completed networks rather than accepting a purely local gate-count estimate. The ordinary default employs the R8.6 `extra_sop` selection and an optional R10.0 `repeat_sop` pass, accepted only for strict whole-network area reduction while meeting the target.
5. **Final serialization:** prune unused gates and produce a topologically ordered netlist. Short-limit and RAM-guarded cases may take different source-defined paths.

For formal definitions, pseudocode, correctness assumptions, implementation details and experimental results, see [`Stage 2 Formal Report/main.pdf`](Stage%202%20Formal%20Report/main.pdf) and its [LaTeX source](Stage%202%20Formal%20Report/main.tex).

### Stage 2 development: area and delay

![Stage 2 historical area savings and delay changes across feasible research milestones](Stage%202%20Formal%20Report/Research_Trial_Log/figures/14_stage2_area_delay_trajectory.png)

*Stage 2 milestone trajectory.* The upper panel tracks weighted area saved against R7.2 on the **25 released Stage 2 cases**; the lower panel tracks the corresponding change in the sum of circuit delays. Only checkpoints with **25/25 functional PASS and delay targets met** are included (R7's incomplete 24/25 result is omitted). These archived milestone snapshots show the path of development, **not** the isolated causal effect of each feature. [Source data](Stage%202%20Formal%20Report/Research_Trial_Log/data/stage2_full_milestone_trace.csv) · [Chart-generation script](Stage%202%20Formal%20Report/Research_Trial_Log/scripts/plot_high_resolution_comparisons.py).

### Historical public-case comparison

The **first historical matched repeat** compares submitted Stage 1 (Z1) with R10.0 on the same 50 released truth tables (25 from each stage):

| Metric | Submitted Stage 1 (Z1) | Independent Stage 2 (R10.0) |
|---|---:|---:|
| Functional PASS | 50/50 | **50/50** |
| Delay target met | 50/50 | **50/50** |
| Sum of weighted gate area | 1,144,244 | **1,019,547** |
| Net area change | — | **−124,697 (−10.90%)** |

R10.0 has smaller area on 18 cases and larger area on 32; the aggregate improvement is concentrated in a subset of cases. A second paired repeat confirmed the same direction of the per-case differences, while exact runtime and area values can vary with time-bounded search. The result is a **whole-solver comparison**, not a claim that the final SOP pass alone produced the aggregate gain.

The historical casewise CSV retains both repeats. The current Formal Report appendix covers the later four-method matched experiment. [Historical casewise data](Stage%202%20Formal%20Report/data/matched_case_metrics.csv) · [Numerical checks](Stage%202%20Formal%20Report/verify.py)

![Signed area changes on all 50 released cases, comparing the submitted Stage 1 solver Z1 with Stage 2 R10.0](Stage%202%20Formal%20Report/Research_Trial_Log/figures/07_matched_area_rank_reversal.png)

*Why the aggregate result needs a casewise view.* In the **first matched repeat**, the 18 improved cases contribute **160,696 weighted area units saved**, while 32 regressions offset **35,999 units**, for a net reduction of **124,697 units**. The result is driven by the magnitude of improvements, not by winning on most cases; the plot compares **the entire submitted Z1 and R10.0 solvers**, not one isolated optimization pass. [Full matched data](Stage%202%20Formal%20Report/data/matched_case_metrics.csv) · [Related cumulative view](Stage%202%20Formal%20Report/Research_Trial_Log/figures/08_matched_cumulative_contribution.png).

## Stage 1: an essential part of the project

Stage 1 includes two distinct contributions that the repository and reports keep separate:

- **Formally submitted Stage 1 solution (Z1):** developed by Zeyun Du and used as the actual submitted-method comparator in the final report. The original source is archived with the Stage 1 audit evidence listed in the repository guide.
- **Independent Stage 1 research path (J51):** developed by Jincan Li across Rounds 1–6.1. The selected Round 5.1 research freeze achieved **25/25 PASS**, **25/25 delay targets met**, and **529,014 total area** on the released Stage 1 bank. Its typed-DAG and early cut-rewriting investigations contributed important design foundations for Stage 2.

See the [Stage 1 Technical Report](UFUG2106_Stage1_Writing_v1_0/technical_report/main.pdf), [Stage 1 Trial Log](UFUG2106_Stage1_Writing_v1_0/trial_log_record/main.pdf), and [Round 5.1 frozen evidence](Stage1_Freeze_Round5.1_Verified/).

### Stage 1 area and runtime trajectory

These figures are **selected historical WSL observations**, not a nine-way paired timing experiment. R5.1 is the preferred *research efficiency baseline*, not the formally submitted Z1 implementation.

| Research Round | PASS | Delay targets | Total area | Median synthesis time |
|---|---:|---:|---:|---:|
| R1 | 25/25 | 12/25 | 1,103,455 | 5.455 ms |
| R2 | 25/25 | 25/25 | 790,243 | 36.427 ms |
| R3 | 25/25 | 25/25 | 533,705 | 68.486 ms |
| R4 | 25/25 | 25/25 | 528,910 | 127.568 ms |
| R4.1 Balanced | 25/25 | 25/25 | 529,014 | 102.615 ms |
| R5 | 25/25 | 25/25 | 529,014 | 68.861 ms |
| **R5.1** | **25/25** | **25/25** | **529,014** | **55.488 ms** |
| R6.0 | 25/25 | 25/25 | 528,738 | 114.610 ms |
| R6.1 | 25/25 | 25/25 | 528,854 | 80.731 ms |

![Archived Stage 1 area trajectory](UFUG2106_Stage1_Writing_v1_0/shared/figures/area_evolution.png)

R5.1's typed in-memory DAG improved the R5 paired median by **23.13%** and **9.45%** in the two recorded reverse-order runs while retaining the same aggregate area and per-case delay. Its subsequent cut-rewriting experiments gained a small amount of area at additional search cost. See [paired evidence](UFUG2106_Stage1_Writing_v1_0/shared/data/paired_benchmarks.csv) and [archived round history](UFUG2106_Stage1_Writing_v1_0/shared/data/round_history.csv).


## Research evolution and evidence

The history is preserved as reproducible source, mathematical reasoning and controlled/archived evaluation evidence—not as a claim that each round was run simultaneously:

| Research interval | Main problem addressed |
|---|---|
| **R1–R3** | From an exact baseline to diversified, timing-aware mapped circuits |
| **R4–R5.1** | Better physical mapping and less synthesis overhead through typed-DAG operations |
| **R6.0–R6.1** | Initial bounded cut rewriting, with a real area–runtime trade-off |
| **[R7–R7.2](UFUG2106_Round7_2_Delivery/)** | Reduce short-budget failure risk and recover useful low-cost candidates |
| **[R8 prototype](UFUG2106_Round8_Prototype/) – [R8.7](UFUG2106_Round8_7_Delivery/)** | Four-leaf cut resynthesis, structural sharing, candidate order, guarded search, controlled SOP quotas |
| **[R9.0](UFUG2106_Round9_0_Delivery/) – [R9.1](UFUG2106_Round9_1_Delivery/)** | Short-limit screening, optional library versus Repeat SOP, source-only deployment controls |
| **[R10.0](UFUG2106_Round10_0_Delivery/) – [R10.1](UFUG2106_Round10_1_Delivery/)** | Freeze selected default; test reduced root caps and nominal budgets, retain R10.0 |

The [**unified Trial Log**](Stage%202%20Formal%20Report/Research_Trial_Log/UFUG2106_Stage2_Research_Trial_Log_v3.pdf) is the comprehensive research record: motivations, mathematical derivations, source changes, negative results, per-round decisions and cross-version visualizations. The [**Final Report**](Stage%202%20Formal%20Report/main.pdf) focuses on the *solution*, retaining only the historical comparisons needed to explain major design decisions.

### Why R10.0 remained the final research candidate

![R10.1 controlled policy ablations: extra weighted circuit area and paired synthesis-runtime ratios versus frozen R10.0](Stage%202%20Formal%20Report/Research_Trial_Log/figures/12_r101_native_pareto.png)

*Late-stage area–runtime trade-off.* The R10.1 controlled comparison uses **100 matched public-case observations per policy** (two runs over 50 cases); the left panel expresses the area penalty **per 50 cases** relative to frozen R10.0, and the right panel shows the median paired synthesis-runtime ratio. Disabling Repeat SOP costs **1,587** area units and reduces median runtime to **0.942×**; lowering the root quota to 40 or 80 gives smaller runtime reductions with **1,008** or **602** extra area units. The 45 ms nominal budget costs **241** area units and does not improve median runtime in this comparison. Since the course's combined score is not disclosed and search-time checks are cooperative, the reduced-budget trials were **not promoted** over R10.0. [Policy CSV](Stage%202%20Formal%20Report/data/final_policy_tradeoff.csv) · [Release decision](UFUG2106_Round10_1_Delivery/docs/02_RELEASE_DECISION.md).

## Repository guide

| Location | Role |
|---|---|
| [`Final_Project.pdf`](Final_Project.pdf) | Official project specification |
| [`data/stage1/`](data/stage1/), [`data/stage2/`](data/stage2/) | Released truth-table inputs (25 per bank) |
| [`Final_Submission_by_Zeyun_DU/`](Final_Submission_by_Zeyun_DU/) | Pinned team integration, provenance, official and independent verification |
| [`UFUG2106_Round10_0_Delivery/`](UFUG2106_Round10_0_Delivery/) | **Selected research-frozen R10.0 implementation**, exact checking, experiments and evidence |
| [`UFUG2106_Round10_1_Delivery/`](UFUG2106_Round10_1_Delivery/) | Post-freeze budget-ablation experiment; **not** the selected final solver |
| [`UFUG2106_Round7_2_Delivery/`](UFUG2106_Round7_2_Delivery/), [`UFUG2106_Round8_6_Delivery/`](UFUG2106_Round8_6_Delivery/), [`UFUG2106_Round9_1_Delivery/`](UFUG2106_Round9_1_Delivery/) | Representative early, core and late Stage 2 iterations; all other named Round folders remain at root |
| [`Stage 2 Formal Report/`](Stage%202%20Formal%20Report/) | Canonical `main.tex`, `main.pdf`, data, figures, reproducibility scripts |
| [`Stage 2 Formal Report/Research_Trial_Log/`](Stage%202%20Formal%20Report/Research_Trial_Log/) | Complete integrated Stage 1–Stage 2 research log |
| [`UFUG2106_Stage1_Writing_v1_0/`](UFUG2106_Stage1_Writing_v1_0/) | Archived Stage 1 papers, figures, data and scripts |
| [`Stage1_Freeze_Round5.1_Verified/`](Stage1_Freeze_Round5.1_Verified/) | Stage 1 frozen research baseline and supporting evidence |
| [`Stage 2 Formal Report/UFUG2106_Final_Algorithm_Audit_v1/stage1_zeyun/`](Stage%202%20Formal%20Report/UFUG2106_Final_Algorithm_Audit_v1/stage1_zeyun/) | Archived Z1 submitted Stage 1 implementation and corresponding audit evidence |
| [`baseline/`](baseline/) | Early synthesis baseline |

Large duplicated reconstruction workspaces, old manuscript drafts, machine-generated build outputs and local backup archives are excluded from new Git commits by [`.gitignore`](.gitignore). Original per-round source, explanatory documents, and selected CSV/JSON evidence are retained. Local ZIP/RAR feedback bundles are ignored by default; normalized evidence tables are included. The archive documents released cases and separately identified generated-case experiments.

## Build, test and reproduce

The quick start builds the integrated team solver and links to the independent R10.0 and Stage 1 reproduction commands. Use the solver archive for the matched integration scripts and the Formal Report directory for rebuilding the paper. [Quick Start](QUICK_START.md) · [Integration reproduction](Final_Submission_by_Zeyun_DU/integration/AUDIT.md) · [Stage 1 delivery guide](UFUG2106_Round5.1_Delivery/README.md)

The merged Trial Log is available as a complete PDF, and its CSV/plots explain iteration decisions. Its **editable LaTeX reconstruction** additionally requires the Stage 1/Stage 2 body sources, palette, figure set and merge scripts; see that log's own [README](Stage%202%20Formal%20Report/Research_Trial_Log/README.md).

## Research integrity and attribution

Jincan Li developed the independent Stage 1 research line and the Stage 2 research solver frozen as R10.0. Zeyun Du authored the submitted Stage 1 solver and coordinated the Stage 2 team integration and release validation. The integrated code credits the J51 and R10.0 modules it adapts. The upstream report credits Codex for timing-rescue implementation and verification assistance. [Source attribution](Final_Submission_by_Zeyun_DU/src/round51/ORIGIN.md) · [Upstream release report](Final_Submission_by_Zeyun_DU/reports/stage2-timing-20261124/UFUG2106_Group2_Stage2_Report.pdf)

The public release is a **research and coursework archive**, not a formally verified synthesis engine or a promise of success on unreleased cases.

## Repository integrity and evidence scope

The Phase D review record documents the release decision, reproduction commands, exact PDF hashes and the scope of the scientific claims. [Final acceptance audit](FINAL_ACCEPTANCE_AUDIT.md) · [Claim evidence matrix](CLAIM_EVIDENCE_MATRIX.md)

All named R7/R8/R9/R10 research-delivery directories and both public banks have been checked on GitHub `main`. The documentation and scientific values are based on archived results; source-defined time budgets are cooperative, not universal hard runtime bounds. Full reconstruction of the merged Trial Log requires its archived `tex/` bodies, `shared/palette.tex`, full referenced figure set, and merge/plot scripts in addition to the precompiled PDF.

# Round 8.0 — Controlled experiment and reporting protocol

**Mandatory principle:** a positive transformation in an independent local postprocessor is not an official Stage 2 PASS. The instructor's evaluator on the user's WSL environment decides the public-case status, run limit and netlist costs.

## 1. Frozen controls and variables

- Parent baseline: `UFUG2106_Round7_2_Delivery/build/synth_round72`, itself verified to match the frozen Round7.2 source SHA-256 `d7c0dac7ddb173d8cd76f8ae0ebae9160856a1e0ab443e162584bdd2c15bff9e`.
- Candidate: `UFUG2106_Round8_Prototype/build/synth_round8`; compile flags `-O2 -std=c++17 -pipe -DNDEBUG`, one process/case and no network dependency.
- Input sets: all 25 old Stage 1 truth tables and all 25 new Stage 2 truth tables, plus future independent holdouts. Retain Stage1 separately for detecting regressions.
- Official comparator always runs on the same machine, with alternated variant order on consecutive runs. Default is two runs, not one.
- Preserve complete evaluator stdout and original CSVs, not just a summary. An absent area due to FAIL is not zero and is never averaged as a successful candidate.

## 2. Planned ablations (no testcase-ID special cases)

| Label | Candidate engine | Research question |
|---|---|---|
| `r72` | frozen Round7.2 | Full realistic control |
| `r8_off` | Round8 solver, rewriting disabled | Does integration itself perturb results? |
| `r8_factor` | single factoring modes | Do local distributive factors help the weighted netlist? |
| `r8_reuse` | single divisor-reuse pass | Does sharing-aware inverse distribution have standalone value? |
| `r8_all` | seven independent candidates, one pass | Does portfolio variety improve coverage? |
| `r8_iterate` | bounded repeated full-graph selection, maximum five passes | Can rewrites enable new matches in subsequent passes? |
| `r8_strict` | iterative but delay never exceeds inherited R7.2 baseline | Is there a true Pareto-dominating improvement, rather than area-delay exchange? |

The default interactive run is a **controlled paired design** and archives results under `results/<timestamp>/`. For each run, Stage 1/Stage 2, and variant, the system writes the raw CSV and full evaluator log. Candidate profile logs for Stage1 `case_020` and Stage2 `case_016`, `case_021` are saved separately, with explicit labels saying direct run != official timed evaluator.

## 3. Metrics

For dataset \(S\), first evaluate the counts:

\[
 N_{\mathrm{PASS}}(S)=\sum_{i\in S}\mathbf 1[\mathrm{PASS}_i],\quad
 N_{\mathrm{target}}(S)=\sum_{i\in S}\mathbf 1[\mathrm{PASS}_i\land D_i\le D_i^{\mathrm{target}}].
\]

Area sum \(\sum_{i\in S}A_i\) is complete **only if** every case in that dataset PASSES. For pairwise regressions, compare Area/Delay only where both versions PASS. Report per-case \(\Delta A_i=A_i^{8.0}-A_i^{7.2}\), \(\Delta D_i=D_i^{8.0}-D_i^{7.2}\) and timing ratio \(r_i=T_i^{8.0}/T_i^{7.2}\). Geometric mean of positive runtime ratios is \(\exp(|S|^{-1}\sum_i\log r_i)\), calculated over jointly passing pairs. Preserve the number of excluded failures.

**Release gate (research preference, not grading formula):** both stages achieve 25/25 functional PASS and 25/25 target met in *every* paired run, with no jointly passing case showing a positive area delta relative to its paired frozen control. For `r8_iterate`, a delay increase within target is explicitly permitted; the `r8_strict` ablation forbids regression against the inherited delay. A delay increase within target is explicitly permitted by our area-first research ranking, but must be disclosed as a trade-off. No automated gate proves good hidden-case generalization.

## 4. Correctness checks

1. Source manifest checks the frozen parent and generated file hashes. The original Round7.2 folder remains untouched.
2. Independently verify Boolean semantics using the standalone `tests/verify_exhaustive.cpp`, which simulates 64 assignments at a time. The checker compares *all rows* for n<=20; this is a second implementation independent of the netlist builder and candidate choice rule.
3. Baseline local preflight: 25 Stage 2 netlists were regenerated in Linux and **25/25 exhaustively verified**, including the cases with n=20. The checker also computes exact area and arrival-based delay.
4. Stress random 140 low-input DAGs across 7 rewrite modes, **980 exhaustive comparisons**, all matched. The synthetic suite tests *soundness* of identities, not expected benchmark QoR.
5. On the user's WSL run, Stage1/Stage2 official evaluator is the authoritative source for PASS, area, delay and runtime. No CPU timing from the developer's Linux container may be substituted.

## 5. Execution from existing project root (WSL)

```bash
BASE="/mnt/e/canfiles/Common courses study/大学通识/26-27 Fall/UFUG 2106 Discrete Math/assignment/Final Project"
cd "$BASE" || exit 1
bash UFUG2106_Round8_Prototype/run_round8.sh
```

If time is short, preliminary quick mode:

```bash
bash UFUG2106_Round8_Prototype/run_round8.sh --quick --runs 1
```

Quick mode is for testing the executable path, **not** a reliable final result. Default runs all variants twice. The wrapper always writes a single `feedback/Round8_Prototype_Feedback_<timestamp>.zip` even when build, testing, or evaluator fails, and reports the nonzero exit status on failure.

Feedback includes full official evaluator CSVs and logs, per-case comparison, summary, source snapshot and design documents. The original input truth tables, `evaluator` binary, and compiled platform-specific binaries are intentionally not included.

## 6. Negative results and next decision

At this point, local direct-run Stage 2 research shows only one improved case, saving 55 total area after iterations. In particular, do NOT claim generalized multi-output resubstitution or choice-network improvement. If official runtime grows noticeably without larger area improvement, keep the standalone research as a valuable mechanism demonstration and do not replace frozen R7.2 as the default. Conversely, if integration is safe, investigate cut-function exact rewriting, a limited Pareto frontier and multi-output divisor mining before declaring that all structural methods have failed.

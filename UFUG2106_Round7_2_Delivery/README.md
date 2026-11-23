# UFUG2106 — Round 7.2 Delivery

**Milestone:** `Round 7.2 — Budget-Constrained Quality Recovery`  
**Status:** Research candidate. Independent local compile/smoke verified; **official evaluator on the user's WSL machine is pending**.  
**Primary comparator:** frozen Round 7.1 `r71_guard` (a known two-run public 50/50 feasible research release candidate).  
**Secondary comparator:** frozen Round 5.1.

## 1. Why this round exists

The verified Round 7.1 feedback exposes two complementary search behaviors:

- **Stage 2 case_016:** guarded R7.1 preserved Area 1781 / Delay 36 while reducing official runtime from about 98 ms to 25 ms, by skipping expensive, low-value legacy work.
- **Stage 1 case_020:** guarded R7.1 increased Area 766 -> 777 and Delay 30 -> 32, because it skipped a *cheap, valuable* second legacy candidate (`influence-desc`, `cubemode=0`).

Therefore, R7.2 **does not revert to unbounded full search**. It adds one constrained supplementary candidate in the short-budget branch and preserves the original R7.1 incumbent and postprocessing pipeline.

## 2. One-command WSL execution

**Unzip this folder beside** `UFUG2106_Round5.1_Delivery`, `UFUG2106_Round7_1_Delivery`, `data/stage1/`, `data/stage2/`, and the teacher-provided `evaluator`.

```bash
BASE="/mnt/e/canfiles/Common courses study/大学通识/26-27 Fall/UFUG 2106 Discrete Math/assignment/Final Project"
cd "$BASE" || exit 1
bash UFUG2106_Round7_2_Delivery/run_round72.sh
```

The script:

1. Generates `src/synth_round72.cpp` deterministically from the *frozen Git blob* of Round 5.1 via the stored Round 7 and Round 7.1 patch chains, then compiles it as C++17 with `-O2`.
2. Ensures the Round 7.1 comparator is built; checks the generated source SHA; runs **10,656 independent Cover-kernel A/B comparisons**.
3. Runs **two exhaustive functional checks** on Stage 1 `case_020` and Stage 2 `case_016` using an independent bit-parallel verifier.
4. Runs **two reversed-order paired official evaluator passes** over both Stage 1 and Stage 2, with multiple ablations.
5. Profiles both structural probes outside the official timeout, retaining their netlists and candidate-level logs.
6. **Always writes a feedback ZIP even if one of the steps fails.**

The script prints:

```text
FEEDBACK ZIP CREATED: .../UFUG2106_Round7_2_Delivery/feedback/Round7.2_Feedback_<timestamp>.zip
```

Upload **only that ZIP** for the next analysis. It contains all official CSVs, complete logs, the reproduced source and SHA manifest, experimental comparisons, and diagnostic results. It does **not** contain input truth tables, the evaluator binary, or platform-specific executables.

### Fast path

```bash
bash UFUG2106_Round7_2_Delivery/run_round72.sh --quick --runs 1 --diagnostic-runs 1
```

Use the default command for research evidence; this fast path tests fewer variants and has a weaker reliability basis.

## 3. Core change and ablations

The default `UFUG_R72_POLICY=shortlist` is active only when there is a **feasible incumbent** and the input declares a short time budget in the specified range. It admits one complementary-normalization legacy candidate that does not invoke Cover Enumeration (`cubemode=0`) and avoids the expensive first and third legacy candidates.

| Setting / version | Purpose |
|---|---|
| Round 5.1 `r51` | Frozen original synthesis baseline |
| Round 7.1 `r71_guard` | Previous short-budget guard, no supplementary legacy |
| **Round 7.2 `r72_shortlist`** | One complementary legacy candidate + deadline + R7.1 guard |
| `UFUG_R72_POLICY=guard` | Ablation: new binary with supplementary search disabled |
| `UFUG_R72_POLICY=shortlist_nocancel` | Ablation: same shortlist, no internal legacy deadline |

The last ablation **can exceed runtime limits** and is an experiment, not a recommended production configuration.

This is a principled **cheap-first shortlist**, **not** a trained probabilistic candidate-value predictor. The current code admits the candidate based on its *algorithmic work profile* (`cubemode=0`), an elapsed-time admission gate, and a cooperative deadline. Expected improvement per unit time remains a research question.

## 4. Data sources and integrity

- `evidence/Round7_1_Postmortem_20261121.md`: frozen analysis from the user's real R7.1 official results; provenance and limits included.
- `evidence/Round7_1_Casewise_Audit.csv`: full previous paired per-case comparison.
- `evidence/round51_stage1.csv`, `evidence/round51_stage2.csv`: early frozen baseline snapshots; do not mistake different dates/host loads for controlled comparisons.
- `evidence/local_stage2_smoke.csv`: current container-based **direct execution** comparison, 25 cases (R7.1 vs R7.2); no official evaluator limits applied.
- `evidence/local_stage2_independent_verification.csv`: 15 cases exhaustive, 10 cases fixed-seed sample, all matched for the R7.2 netlists.
- `evidence/local_critical_diagnostics.csv`: direct subprocess tracing and independent netlist checks for the two structural probes (not official timed evaluator data).
- `SOURCE_MANIFEST.json`: reproducible source hashes and frozen R5.1 Git blob.

**Important:** historical R7.1 and local smoke timings use different machines/measurement conditions; only same-run paired official evaluator data is valid for timing comparison.

## 5. Release gates

`run_benchmarks.py` records two separate gates:

1. **Feasibility/target gate**: both stages 25/25 PASS and 25/25 target-met in *every* Round 7.2 default run.
2. **No QoR regression gate**: no jointly passing case has a worse Area **or** Delay versus Round 7.1 Guard. This is intentionally stricter than simple Pareto dominance and is a development gate, **not** the official course grading rule.

If either fails, the script returns a nonzero code but still creates the feedback ZIP. The code **never treats failed cases as zero-Area improvements**.

## 6. Contents

| Path | Role |
|---|---|
| `bootstrap_round72.py`, `bootstrap_round71.py`, `bootstrap_round7.py` | Fully auditable generation chain from frozen R5.1 |
| `src/` | Full generated solver and headers, source hash fixed by manifest |
| `Makefile` | C++17 compilation |
| `tests/` | Cover A/B, patch integrity, small-case exhaustiveness, independent verifier |
| `tools/run_benchmarks.py` | Official paired evaluation, full CSVs, quality regression analysis |
| `tools/profile_critical.py` | Candidate traces, netlist SHA, structure probes for cases 016/020 |
| `tools/export_feedback.py` | Auto-generated feedback ZIP even on failure |
| `docs/ROUND7_2_MATHEMATICAL_DESIGN.md` | Formal algorithm, correctness conditions, runtime/QoR trade-offs |
| `docs/ROUND7_2_MOTIVATION_AND_EVIDENCE.md` | Numerical evidence and causal interpretation from prior rounds |
| `docs/EXPERIMENT_PROTOCOL.md` | Metric definitions, ablation matrix, scope of verification |
| `docs/PAPER_RESEARCH_NOTES.md` | LaTeX-ready manuscript ideas, tables, limitations, next questions |
| `docs/CHANGELOG.md` | Precise scope of code changes and risks |

## 7. Engineering limitations

- The deadline is *cooperative*, not a hard upper bound: not every downstream graph rewrite and output write is cancellable.
- A 100 ms CPU runtime limit measured by a separate evaluator is not identical to a source-level steady-clock deadline. Reserve is therefore necessary.
- This milestone is **quality recovery and search scheduling**; it is not yet the planned Round 8 research on AIG/NPN choice networks and multi-output resubstitution.
- All public results can be overfit. Measure both stages and independent held-out functions before claiming generality.
- Official scoring weights remain unknown; do not substitute ad hoc area/delay/runtime weights.

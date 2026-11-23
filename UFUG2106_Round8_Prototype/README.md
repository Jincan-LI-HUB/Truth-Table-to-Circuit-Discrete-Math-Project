# UFUG2106 Round 8.0 — Structural Synthesis Research Prototype

**Status:** THEORY-FIRST PROTOTYPE — not yet a frozen Round8 final release. Derived from verified Round7.2 source. Single-threaded C++17; no external synthesis package or external network at runtime.

## Scope of changes

- Exact local Boolean identities, including absorption, factoring and dual forms, and De Morgan alternatives.
- Limited **DAG-aware divisor reuse** using reverse distributivity: a subexpression already computed elsewhere can make an otherwise larger distributed form cheaper globally.
- Required-time filter allows an area improvement to use permitted delay slack.
- A **bounded multi-choice portfolio** evaluates up to seven alternatives on the same incumbent, and the iterative policy may repeat up to five passes. The baseline incumbent is never replaced without checking actual full live-graph Area/Delay and valid netlist structure.
- Resource guard: attempts rewriting only for declared limits ≥1000ms, with bounded time allocation. Short 100ms cases, including previously unstable Stage2 `case_016`, are left on the frozen Round7.2 pipeline.

**This is not a port of Berkeley ABC/mocking SAT solvers or a proof of global optimality.** See `docs/02_MATHEMATICAL_DESIGN.md` for the precise implemented subset.

## One-command official WSL test

Extract `UFUG2106_Round8_Prototype/` beside `UFUG2106_Round7_2_Delivery/`, `data/stage1/`, `data/stage2/` and the instructor `evaluator` in your `Final Project` root:

```bash
BASE="/mnt/e/canfiles/Common courses study/大学通识/26-27 Fall/UFUG 2106 Discrete Math/assignment/Final Project"
cd "$BASE" || exit 1
bash UFUG2106_Round8_Prototype/run_round8.sh
```

This compiles frozen-source-derived R8, checks three critical cases exhaustively, and runs **two paired official evaluator passes** on BOTH Stage1 and Stage2 for R7.2 control and R8 modes `off`, `factor`, `reuse`, `all` (single pass), `iterate` (up to five passes), `iterate_strict` (iterative with no delay regression vs inherited incumbent). It saves full evaluator logs and CSVs, per-case differences, and direct-run diagnostics.

**Automatic feedback:** regardless of PASS/FAIL, the wrapper archives results into:

```
UFUG2106_Round8_Prototype/feedback/Round8_Prototype_Feedback_<timestamp>.zip
```

Upload only this ZIP. If the evaluator is missing or build fails, an error-feedback ZIP with source and logs will still be generated. Quick smoke:

```bash
bash UFUG2106_Round8_Prototype/run_round8.sh --quick --runs 1
```

The quick run is weaker evidence than the default two-run ablation.

## Verified evidence to date

| Test | What was actually checked | Result |
|---|---|---|
| Compiler | C++17 -O2 generated integrated solver, postprocessor, exact checker | PASS |
| Full Stage2 local preflight | New output netlists against EVERY truth-table row on 25 provided Stage2 cases, n up to20 | **25/25 exhaustive** |
| Random small DAG checks | 140 frozen-seed functions × 7 modes | **980/980 exhaustive matches** |
| Standalone Stage2 one-pass ablation | Seven modes on saved R7.2 netlists | `reuse` saves 12; `factor`/`phase` net zero |
| Iterative Stage2 direct-run | Bounded full-graph accepted improvements | `case_021` saves **55** area, delay 69->70 (target70) |
| Existing R7.2 official baseline | User's paired WSL results from 2026-11-21 | 50/50 PASS, 50/50 target, area 529014+508535 |
| **New R8 official WSL results** | Teacher's evaluator on user's computer | **PENDING** |

**Multiobjective caveat:** `case_021` reduces weighted area by 55 but raises delay from 69 to 70. This is a *Pareto trade-off*, not Pareto dominance. `iterate_strict` retains the original 22,590 / 69 result on this case when a delay increase is unacceptable. The true official grading formula is still unknown.

Savings 55 correspond to just **0.0108%** of the 508,535 Stage2 area sum, on a single case. This is a useful causal demonstration, not yet a broadly strong optimization.

## Files and source provenance

- `bootstrap_round8.py`: checks SHA256 of original Round7.2 source `d7c0dac7...` and injects independent rewrites; never modifies previous rounds.
- `src/synth_round8.cpp`: generated integrated synthesizer, `src/r8_structural.hpp`: standalone symbolic optimizer; `src/optimize_netlist.cpp`: offline candidate/ablation CLI.
- `tests/verify_exhaustive.cpp`: independent full-truth-table bit-parallel checker; `tests/test_boolean_rewrite.py`: 980 randomized soundness checks.
- `tools/run_benchmarks.py`: official paired 50-case comparisons and detailed casewise CSV; `tools/export_feedback.py`: produces single feedback ZIP on failure or success.
- `evidence/stage2_onepass_ablation.csv`, `results/offline_iteration/iterations.csv`, `results/local_preflight/stage2_direct_compare.csv`: all actual local experiments; `evidence/round72_*_official_run1.csv`: *historical* original reports preserved without alteration.
- `docs/`: mathematical design, evidence analysis, negative trial log, evaluation protocol. `SOURCE_MANIFEST.json`: frozen-source and generated-source hashes.

Read `docs/01_MOTIVATION_AND_EVIDENCE.md` and `docs/04_TRIAL_LOG_AND_NEXT_HYPOTHESES.md` before attempting additional technique integration. They explain why superficial single-pass results are not sufficient to reject a method.

## Important constraints and caveats

- The integrated optimizer accepts strictly better global live-DAG candidates; it is not general NPN cut resynthesis, general resubstitution, or SAT.
- The inside-pass rewrite is not interruptible, so time budgets are approximate. Monitor the **official** evaluator runtime, not container microseconds.
- Public cases have been used for development; independent heldout functions remain a next-step requirement. Results do not transfer automatically to the hidden 50 cases.
- Course grading formula remains unconfirmed. Area-first within target is a research proxy, not necessarily the maximizer of course score.

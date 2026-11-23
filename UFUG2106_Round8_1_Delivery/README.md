# UFUG2106 — Round 8.1 Research Delivery

**Topic:** Cost-aware small-cut resynthesis with bounded structural-branch selection.

**Status:** Independent Linux prototype compiled and locally verified. **Not yet an official WSL/evaluator score.** Round 7.2 remains the frozen admissible baseline and is never overwritten.

## Objective

Round 8.0's simple algebraic patterns improved only one of 50 published cases (Stage 2 `case_021`: 22,590 → 22,535, with delay 69 → 70). Round 8.1 asks whether recognizing the **Boolean function** of a bounded logic cone, rather than requiring a particular syntactic pattern, creates improvements across a broader range of functions. The optimization may increase delay *up to the published target*; an independent `strict` mode disallows any delay regression, so a course-specific score can later be applied without conflating these objectives.

## Implemented method

* Enumerate at most nine distinct structural cuts with **up to four leaf signals** per node, using bounded fan-in cut unions; examine a deterministically sampled subset of at most 2,500 roots per sweep.
* Evaluate an exact cut truth table on the independent formal leaf variables.
* Resynthesize that Boolean function using prime-cube SOP/POS and multiple Shannon decomposition orders. Use real AND2/OR2/NOT costs and arrivals, and a conservative estimate of independently reclaimable original gate area.
* Offer individual `sop`, `shannon`, `all`, `choices` and independent full-graph `branch` searches; `branch_strict` enforces a delay-non-regression comparator. `reverse` tests cut-before-pattern sequencing.
* **Acceptance is only at the complete live-DAG level** after rebuilding with structural hashing and garbage collection. A fully valid incumbent from Round 7.2/8.0 remains available. No testcase names are inspected by solver decision rules.
* Search is time-budgeted and skipped below 1000 ms declared runtime; cooperative checks are not a strict worst-case real-time proof.

**Important terminology:** This is a *bounded multi-start structural choice* prototype. It is **not** a full choice-network/equality-saturation implementation, and it is **not** an exact optimum for four-variable functions.

## Files

- `src/r81_cut.hpp`: Boolean cut enumeration, local truth masks, SOP/POS, Shannon, reclaimable-area screening, candidate statistics.
- `src/synth_round81.cpp`: generated complete synthesizer, equivalent baseline preserved.
- `src/optimize_cut.cpp`: independent offline postprocessor for controlled tests.
- `bootstrap_round81.py`: hash-checked frozen Round8.0 → Round8.1 source materialization; does not edit older versions.
- `tests/test_cut_random.py`: reproducible randomized exhaustive equivalence checks on 180 synthetic DAGs × 4 modes = 720 tests.
- `tests/verify_exhaustive.cpp`: independent original-truth-table verification for n ≤ 20.
- `tools/run_benchmarks.py`: two reversed-order official same-host paired evaluations of Stage 1 and Stage 2, with 8 ablation configurations.
- `tools/export_feedback.py`: unconditional feedback archive (including failure logs).
- `docs/`: theory, experimental motivation, evidence, trade-offs, paper notes, source references and protocol.
- `evidence/`: **local, non-official** complete-truth-table results and candidate matrices.

## Run in your WSL Ubuntu

Unzip this folder **alongside** `UFUG2106_Round7_2_Delivery` and `UFUG2106_Round8_Prototype` inside the existing `Final Project` directory. Retain `./evaluator`, `./data/stage1`, `./data/stage2`.

```bash
BASE="/mnt/e/canfiles/Common courses study/大学通识/26-27 Fall/UFUG 2106 Discrete Math/assignment/Final Project"
cd "$BASE" || exit 1
bash UFUG2106_Round8_1_Delivery/run_round81.sh
```

**No matter whether official testing passes or fails**, this produces:

```
UFUG2106_Round8_1_Delivery/feedback/Round8.1_Feedback_<timestamp>.zip
```

Upload **that single feedback ZIP** for Stage 1/2 casewise, timing, ablation and score-sensitivity analysis. The script runs exhaustive preflight checks and both stages' official evaluator; it does not require a nonstandard Python library.

Optional quick paired comparison (still archives feedback):

```bash
bash UFUG2106_Round8_1_Delivery/run_round81.sh --quick
```

Full modes: `r72`, `r80_iterate`, `r81_sop`, `r81_shannon`, `r81_all`, `r81_branch`, `r81_strict`, `r81_reverse`. Reverse evaluation order in run 2 reduces machine-order confounding. Direct profiling is distinguished from evaluator runtime.

## Pre-official local results

Local system: Linux container, same input truth tables. 25 Stage 2 files were tested by exhaustive bit-parallel verification over **every** `2^n` input assignment. These are *not* the user WSL evaluator results.

| Configuration | Stage 2 area sum | Area savings vs R7.2 | Cases improved | Target met |
|---|---:|---:|---:|---:|
| Frozen Round 7.2 | 508,535 | — | — | 25/25 |
| R8.0 iterate | 508,480 | 55 | 1 | 25/25 |
| R8.1 branch (area-priority) | **500,696** | **7,839** | **17** | **25/25** |
| R8.1 branch strict (no delay regression) | **508,352** | **183** | **14** | **25/25** |

The area-priority improvement on Stage 2 is ≈1.54%, **but some improvements consume timing slack**. For example `case_003`: 19,494 / 39 → 15,932 / 61 (target 65); `case_005`: 112,221 / 40 → 109,073 / 55 (target 69); and `case_023`: 2,986 / 25 → 2,103 / 40 (target 40). These outputs passed complete truth-table checking, but official scoring may prefer the faster baseline. The strict configuration addresses this trade-off.

Local integrated runtime is not proof of compliance on the grading hardware. **The complete Stage 1 dataset is not available in this container** (only `case_020` was independently checked, yielding area 766 / delay 30 in both modes); full 50-case acceptance awaits the user's official evaluator.

## Research decision rule

1. Correctness (100% public PASS) and runtime/RAM compliance are prerequisites, not rewards to trade for area.
2. Report actual latency, target violations, area, Pareto domination and time-headroom per case; never report incomplete sums without marking missing cases.
3. Preserve both strict and area-priority versions unless an official scoring formula justifies a unique choice.
4. Compare against both R7.2 and R8.0; retain all ablations and negative evidence.
5. New Round 8.1 is *research prototype* until the WSL feedback validates the complete workflow.

Read `docs/ROUND8_1_MATHEMATICAL_DESIGN.md` and `docs/ROUND8_1_EVIDENCE_AND_TRADEOFFS.md` for proofs and data.

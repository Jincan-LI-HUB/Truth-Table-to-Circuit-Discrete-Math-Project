# Round 7 — Baseline and Preliminary Experimental Report

**Status:** Preliminary kernel evidence; local official evaluator validation pending.

## Frozen Round 5.1 baseline (user-provided fresh WSL CSVs)

| Metric | Stage 1 | Stage 2 |
|---|---:|---:|
| Input cases | 25 | 25 |
| Official PASS | 25 | 24 |
| Target met among accepted | 25 | 24 |
| Area of accepted netlists | 529,014 | 506,754 |
| Median runtime among accepted | 54.177 ms | 39.020 ms |
| Failures | none | `case_016` TIME_LIMIT |

The Stage 2 accepted-only Area number **cannot be treated as the aggregate Area for all 25 cases**. The baseline Stage 1 Area exactly matches the historical frozen figure, 529,014. The fresh Stage 1 median of 54.177 ms is near the older archive's 55.488 ms, as expected for wall-clock measurements.

## Direct Round 5.1 case_016 profile (user-provided)

| Stage | Time |
|---|---:|
| BDD | 0.398 ms |
| Mapping | 92.523 ms |
| First completed candidate | 105.674 ms |

Generated netlist: Area 2,677, Delay 21 vs target 42; independent exhaustive verification matched 512/512 assignments. Official 100 ms limit is violated, so this is not scored as PASS.

## Round 7 isolated symbolic-cover kernel tests (assistant container)

| Test | Result |
|---|---|
| C++ compiler | g++ with `-O2 -std=c++17` |
| Random A/B cover decisions | 10,656/10,656 identical |
| `case_016` legacy symbolic cover | 62.3666 ms, mean of 10 |
| `case_016` Round 7 symbolic cover | 21.1053 ms, mean of 10 |
| Selected cubes for `case_016` | Identical across legacy and optimized kernels |

Relative improvement in this isolated benchmark: approximately **66.2% less time**. This is **NOT** the whole-solver improvement, and should not be extrapolated to official runtime, area, or delay without a paired evaluator run.

The benchmark uses an already extracted copy of the user's Stage 2 `case_016.txt` on the assistant's CPU, *not* the user's WSL system.

## Required official Round 7 experiments

Run `python3 UFUG2106_Round7_Delivery/tools/run_benchmarks.py --paired --runs 2` from the repository root after `make -C UFUG2106_Round7_Delivery`. Keep the generated timestamped evidence under `results/round7/`.

Official questions to answer:

1. Does Stage 2 `case_016` become a reproducible PASS under 100 ms?
2. Are Stage 1 25/25 PASS and Area 529,014 retained or improved?
3. Are Stage 2's other 24 cases retained or improved in Area, Delay and runtime?
4. Does the new runtime permit additional portfolio candidates, changing the selected circuit?
5. If not, should a distinct Round 7-B budget-aware candidate scheduling experiment be introduced?

No numerical outcomes are predicted or fabricated.

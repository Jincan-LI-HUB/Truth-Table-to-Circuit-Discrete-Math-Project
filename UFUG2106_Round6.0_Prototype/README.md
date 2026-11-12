# UFUG2106 — Round 6.0 Prototype

**Topic:** Bounded 4-feasible Cut Rewriting after Round 5.1 synthesis, under exact global AND2/OR2/NOT Area and timing constraints.

**Status:** Research prototype; **not recommended as the final default submission** without a better Area/Runtime trade-off.

## Summary

Stage 1 Linux reference: **25/25 PASS, 25/25 target, Area 529,014 → 528,825 (−189, −0.0357%)**, with median synthesis runtime **78.726 → 138.390 ms**.

New pre-frozen 40-function holdout: **40/40 PASS, 40/40 target, Area 9,709 → 9,496 (−213)**, with median time **6.897 → 14.013 ms**.

Previously frozen 80+16 regressions: **96/96 PASS, 96/96 target**, 656 total Area saved across them, again with substantial synthesis-time overhead. All 161 new netlists independently verified (127 exhaustive, 34 sampled; see evidence for actual split). No case-specific rules were introduced.

**Technical changes**: at most ten propagated cuts per node, \(k\leq4\) formal input leaves, SOP/POS prime implicant covers, distributive factoring, Shannon cofactor candidates, conservative local private-cone area, and exact global area/delay acceptance. The frozen Round 5.1 source remains untouched.

## Compile and run (Linux/WSL)

```bash
make -j1
./build/synth_reference  input.txt reference_netlist.txt
./build/synth_round60    input.txt candidate_netlist.txt
# To isolate the postprocessor and inspect individual cut statistics:
./build/cut_postprocess input.txt reference_netlist.txt postprocessed.txt 4000 120
```

Direct evaluator contract is unchanged: the official evaluator invokes either synthesizer using an input file and output netlist path.

## Full paired local experiment

Put this directory beside previous Round folders inside your `Final Project`, then in WSL run:

```bash
BASE="/mnt/e/canfiles/Common courses study/大学通识/26-27 Fall/UFUG 2106 Discrete Math/assignment/Final Project"
CASES="$BASE/data/stage1"
cp "$BASE/evaluator" /tmp/ufug2106_evaluator
chmod +x /tmp/ufug2106_evaluator
cd "$BASE/UFUG2106_Round6.0_Prototype"
bash run_round6_0_local.sh /tmp/ufug2106_evaluator "$CASES"
```

The script performs **two alternated official pairs** (Round 5.1 vs Round 6.0), three holdout comparisons, independent verification, and ZIP archiving through Python. It does **not** require network access, Linux `zip`, or `sudo`.

The local output follows the previously agreed structure:

```text
local_runs/
├── YYYYMMDD_HHMMSS_Round6.0/
│   ├── benchmark/
│   ├── holdout/
│   ├── source_snapshot/
│   ├── official_per_case.csv
│   ├── summary.json
│   ├── environment.txt
│   └── report_ready/
│       ├── mathematical_design.md
│       ├── reference_experiment.md
│       ├── local_reproduction_report.md
│       └── README.md
└── YYYYMMDD_HHMMSS_Round6.0_local_results.zip
```

## Important limitation

Only the final full-circuit Area/Delay test is exact. A heuristic local proposal can miss profitable globally shared replacements. The method does not exhaust the 4-input truth-function space or optimize the complete DAG globally. The 120 ms post-search cap is a worst-case budget for the cut engine itself, **not** a guarantee of zero end-to-end overhead.

Read `docs/ROUND6_0_MATHEMATICAL_DESIGN.md` and `docs/ROUND6_0_REFERENCE_EXPERIMENT.md` before treating the prototype as a submission candidate.

### Paired reference follow-up

Two alternating full-container runs (same source, no threshold retuning) reproduced 25/25 functional PASS and target met: Area **528,822 / 528,805** for Round 6.0 versus **529,014 / 529,014** for Round 5.1; median runtime **134.384 / 135.084 ms** versus **77.822 / 74.006 ms**. The solver is time-budget-dependent, so minor Area variation across runs is expected.

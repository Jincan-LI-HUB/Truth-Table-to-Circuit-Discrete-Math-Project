# UFUG2106 — Round 5.1 Delivery

**Objective:** Test whether typed, in-memory gate DAG postprocessing speeds up Round 5 without changing the underlying Boolean synthesis heuristics or degrading Area/Delay.

**Comparator:** The frozen Round 5 executable, compiled from `src/synth_round5.cpp` (not Round 4.1).

## Algorithm differences

- Parse the upstream BDD-mapped Netlist once into a typed `Graph` with integer `(op, fanin_a, fanin_b)` nodes.
- Feed that immutable graph directly into `rebalance(Graph)` and then, if feasible, `area_recover(Graph)`. Do not convert through intermediate strings.
- Maintain exact incremental Arrival Times as each gate is inserted, and hash-cons repeated gates.
- Prune dead nodes and compute exact global Area/Delay before accepting each candidate; serialize only candidates that improve the incumbent.
- The phase/algebraic final alternatives still work with text: this version does not claim end-to-end graph-only synthesis or a fully incremental global Area solver.

See `docs/ROUND5_1_MATHEMATICAL_DESIGN.md` for correctness and limitations.

## Reference results

- Two container paired runs: **25/25 functional PASS, 25/25 target met, Area 529,014**, in both reference and Round 5.1.
- Round 5 vs Round 5.1 paired median runtime: **90.006 → 69.389 ms** and **94.047 → 76.986 ms**.
- 96 precommitted held-out tests: **96/96 PASS**, exact per-case Area and Delay equality to Round 5; mixed easy cases show almost no speedup, while larger structured tests improve by approximately 21.8% in median.
- Independent verification: all 25 official plus all 96 held-out Round 5.1 Netlists passed, with exhaustive verification where `n<=13`, deterministic sampling otherwise.

**These container timings are not the user's WSL timings, and hidden Stage 2 performance is unknown.**

## Build and run (Linux / WSL2)

```bash
make clean && make
./build/synth_round51 input.txt output.txt
./build/synth_reference input.txt reference.txt
```

## WSL complete paired reproduction

Extract alongside the Round 5 folder in the original `Final Project` directory. Then:

```bash
BASE="/mnt/e/canfiles/Common courses study/大学通识/26-27 Fall/UFUG 2106 Discrete Math/assignment/Final Project"
CASES="$BASE/data/stage1"
cp "$BASE/evaluator" /tmp/ufug2106_evaluator
chmod +x /tmp/ufug2106_evaluator
cd "$BASE/UFUG2106_Round5.1_Delivery"
bash run_round5_1_local.sh /tmp/ufug2106_evaluator "$CASES"
```

This script compiles both source versions with the same flags, runs **two paired official passes in opposite orders**, independently verifies each new official Netlist, tests the old generated cases and both held-out corpora, and creates:

```text
local_runs/
├── YYYYMMDD_HHMMSS_Round5.1/
│   ├── benchmark/
│   ├── holdout/
│   ├── source_snapshot/
│   ├── per_case_comparison.csv
│   ├── summary.json
│   ├── environment.txt
│   └── report_ready/
│       ├── mathematical_design.md
│       ├── reference_experiment.md
│       ├── local_reproduction_report.md
│       └── README.md
└── YYYYMMDD_HHMMSS_Round5.1_local_results.zip
```

No network, `sudo`, or Linux `zip` package needed. Upload the generated `*_Round5.1_local_results.zip` for formal local-CPU conclusions. Older Rounds and Reports are untouched.

## Experiment integrity

- Test generator seed and function specification were set *before* inspecting held-out results. The generated test input **format** needed one correction to comply with the evaluator's three paired gate cost lines; the function definitions were not altered.
- The public 25 functions were used for debugging syntax and runtime stability; no new case-specific optimization choices or thresholds were fitted to them.
- Source/case SHA-256 hashes, results, original baseline, and independent checker are included.
- Synthetic holdouts cannot guarantee behavior on Stage 2.

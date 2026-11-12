# UFUG2106 — Round 6.1 Delivery

**Purpose:** optimize Round 6.0's cut-rewriting cost without changing the maximum cut size, operators, or core Round 5.1 mapping.

**Status:** Conditional research GO; Round 5.1 remains the default efficiency baseline. Reported 6.1 Stage 1 area **528,864 / 528,886** across two container runs, against **529,014** for Round 5.1. Both 25/25 PASS and 25/25 target delay met. Paired median runtime approximately **99.74–100.98 ms** vs **77.32–80.64 ms**. No Stage 2 claims.

## Source layout

- `src/synth_round51.cpp` — frozen Round 5.1 reference.
- `src/synth_round60.cpp` / `src/cut_rewriter.hpp` — frozen Round 6.0 reference for optional ablation.
- `src/synth_round61.cpp` / `src/cut_rewriter61.hpp` — new Round 6.1 with symbolic Boolean cover cache, structural cut priority, 25 ms postprocessing cap.
- `src/cut_postprocess61.cpp` — standalone analysis of the cut engine, accepting case / incumbent netlist / output / root cap / runtime cap.
- `docs/` — full mathematical correctness, complexity and experimental limitations.
- `tests/holdout_round61_fresh_v1/` — fresh 40-case independent suite, deterministically generated and SHA-256 manifested.
- `tests/holdout_round61_large_v1/` — new 8-case large suite, similarly manifested.
- `results/` — first/second official runs, development ablations, holdout CSVs, selected output Netlists and independent verification evidence.

## WSL reproduction

Place this delivery folder alongside the existing Round 5.1 and Round 6.0 folders in your `Final Project` root, then execute:

```bash
BASE="/mnt/e/canfiles/Common courses study/大学通识/26-27 Fall/UFUG 2106 Discrete Math/assignment/Final Project"
CASES="$BASE/data/stage1"
cp "$BASE/evaluator" /tmp/ufug2106_evaluator
chmod +x /tmp/ufug2106_evaluator
cd "$BASE/UFUG2106_Round6.1_Delivery"
bash run_round6_1_local.sh /tmp/ufug2106_evaluator "$CASES"
```

The script rebuilds Round 5.1 and Round 6.1 with the same `-O2 -std=c++17` flags, performs **two alternated paired official runs**, checks the two new test sets, independently verifies 73 Round 6.1 outputs, and archives everything inside:

```text
local_runs/
├── YYYYMMDD_HHMMSS_Round6.1/
│   ├── benchmark/
│   ├── holdout/
│   ├── source_snapshot/
│   ├── official_per_case.csv
│   ├── environment.txt
│   ├── summary.json
│   └── report_ready/
│       ├── mathematical_design.md
│       ├── reference_experiment.md
│       ├── local_reproduction_report.md
│       └── README.md
└── YYYYMMDD_HHMMSS_Round6.1_local_results.zip
```

No network, sudo or system `zip` command is required. Keep the original Round 5.1 and 6.0 folders and results unchanged. If an evaluator process stalls due to the host environment, do not silently omit that case or claim a full run; retain the raw log and rerun as appropriate.

## Constraints and reproducibility

The postprocessor cap applies only to the cut optimizer. Existing portfolio search also stops by wall-clock deadlines; bytewise identical Netlists across separate runs are not guaranteed. An official PASS does not by itself guarantee `target_met=yes`; the report checks both. Independent simulation is exhaustive for `n<=13`, deterministic sampled for larger inputs.

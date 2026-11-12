# UFUG2106 — Round 5 Delivery

**Stage:** Round 5 — Synthesis Efficiency and Reuse.  
**Frozen comparator:** Round 4.1 Balanced, not Round 4.1 Strict or Fast.

## What changed?

Four engineering changes were implemented without changing the underlying Boolean synthesis rules:

1. Cache a completed immutable complemented-edge ROBDD and its affine subfunction masks for repeated `influence-desc` mappings, bounded by variable count and node count.
2. Cache deterministic selected SOP/POS symbolic Implicant Covers for each output/polarity (small support only). Gate mapping and structural sharing remain candidate-specific.
3. Skip an exactly redundant candidate when \(n>13\): candidates 0 and 2 differ only in a cube option that does not run at that size.
4. Replace high-allocation repeated Netlist metric parsing with an exact linear-scan `stats()` function.

Mathematical motivation and correctness obligations: `docs/ROUND5_MATHEMATICAL_DESIGN.md`. The frozen experimental evidence and negative results: `docs/ROUND5_REFERENCE_EXPERIMENT.md`.

## Build (Linux / WSL2)

```bash
make clean && make
./build/synth_round5 input.txt output.txt
./build/synth_reference input.txt reference-output.txt
```

GCC or Clang supporting C++17 is required. No external synthesis libraries or internet are used. Both binaries are single-process, single-threaded C++17. The reference implementation is the unmodified Round 4.1 Balanced source. Runtime logs go to stderr; the Netlist is written to the named output file.

## Local reproduction on Windows + WSL2

Copy or extract `UFUG2106_Round5_Delivery` alongside the earlier Round folders, then run in a **WSL Ubuntu terminal**:

```bash
BASE="/mnt/e/canfiles/Common courses study/大学通识/26-27 Fall/UFUG 2106 Discrete Math/assignment/Final Project"
CASES="$BASE/data/stage1"
cp "$BASE/evaluator" /tmp/ufug2106_evaluator
chmod +x /tmp/ufug2106_evaluator
cd "$BASE/UFUG2106_Round5_Delivery"
bash run_round5_local.sh /tmp/ufug2106_evaluator "$CASES"
```

The runner:

- Compiles **both** the frozen Round 4.1 reference and the new Round 5 program with the same C++17 flags.
- Runs the official Evaluator on all 25 cases for both programs and saves all Netlists.
- Performs independent full-table (\(n\le13\)) or deterministic sampled (larger \(n\)) verification of each Round 5 Netlist.
- Checks and reports whether all 25 candidate Netlists are byte-for-byte identical; differences can occur because time-bounded search completes a different candidate set. Generates per-case Area/Delay/Runtime comparisons.
- Profiles representative cases (001, 005, 024) and saves source, compiler, evaluator and input digests.
- Creates a `report_ready/` directory with methodology, historical evidence and actual local results.
- Compresses the evidence using Python's standard `zipfile` module (**no `sudo`, system `zip` package or network needed**).

Result location:

```
UFUG2106_Round5_Delivery/
└── local_runs/
    ├── YYYYMMDD_HHMMSS_Round5/
    │   ├── reference/{official.csv,evaluator.log,outputs/}
    │   ├── round5/{official.csv,evaluator.log,outputs/,independent_verification.log}
    │   ├── profiles/
    │   ├── source_snapshot/
    │   ├── per_case_comparison.csv
    │   ├── summary.json
    │   ├── environment.txt
    │   └── report_ready/{mathematical_design.md,reference_experiment.md,local_reproduction_report.md,README.md}
    └── YYYYMMDD_HHMMSS_Round5_local_results.zip
```

**Upload the final `*_Round5_local_results.zip`** to create the formal local Round 5 stage report. Do not overwrite Round 4.1 local logs or reports.

## Reference results

The container-side measurements on 25 official cases are 25/25 `PASS`, 25/25 `target_met`, Area sum **529,014**, with two new-run medians of 90.935 ms and 95.662 ms. A paired frozen Round 4.1 run had median 126.438 ms. The user's WSL timings must be measured independently; CPU and OS differences matter.

Generated tests: 110/110 official `PASS` (96 meet their synthetic delay targets). Two larger stress tests also `PASS`. In one evaluation all 25 official output Netlists were byte-identical to the previously uploaded WSL Round 4.1 Balanced outputs. In an additional paired rerun, one `case_022` output differed because of time-bounded search; both were valid and Round 5 was slightly better. The local script reports, rather than suppresses, these changes.

## Next-step options

- Profiling instrumentation: set `UFUG_ROUND5_PROFILE=1` when invoking the Round 5 binary. It prints stage timings to stderr, never the Netlist file.
- Further reduce parse/serialize cycles in `rebalance`, `area_recover` and phase mapping by introducing a typed in-memory graph rather than strings.
- Add incremental Area and Arrival updates with fanout tracking; verify unchanged outputs on a frozen candidate set.
- Once execution is sufficiently efficient, try cut-based rewriting as a **new** algorithmic round with explicit area/delay/runtime ablations.

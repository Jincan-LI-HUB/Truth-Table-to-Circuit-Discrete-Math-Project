# UFUG2106 — Round 4 Logic Synthesis

This archive contains the **Round 4 experimental C++17 synthesizer**, its frozen Round 3 comparator, derivations/proofs, verified Stage 1 results, and a WSL-local reproduction runner. This is a research iteration, **not** a claim of a course submission or globally minimum netlist.

## Published Stage 1 benchmark (Linux container, November 11, 2026)

- 25/25 official PASS; **25/25 Target Delay Met**.
- Sum of per-case Areas: **528,910**, versus **533,705** for frozen Round 3.
- Median runtime: **188.677 ms** in this measurement (platform-dependent).
- Independent checker: 25/25 area/delay match; exhaustive for 13 cases and deterministic sampling for 12 larger cases.
- Extra validation: 110/110 generated cases PASS (96/110 synthetic delay targets met); 2/2 large stress cases PASS.

## Source files

- `src/synth.cpp`: final unified Round 4 synthesizer (C++17, single process).
- `src/synth_round3_frozen.cpp`: original unmodified Round 3 synthesizer, retained as an ablation baseline; this source alone doesn't include the Round 4 mapping headers.
- `src/synth_round4_basic.cpp`: first successful Round 4 post-mapping integration without extra order diversity.
- `src/polarity_mapper.hpp`: phase-bit cost model and polarity-aware technology mapping.
- `src/algebraic_mapper.hpp`: absorption/factorization rewrite rules.
- `docs/ROUND4_MATHEMATICAL_DESIGN.md`: mathematical definitions, identities, and correctness proof.
- `docs/ROUND4_EXPERIMENT_LOG.md`: actual results, limitations and method history.
- `results/reference_round3.csv`, `results/reference_round4.csv`: retained historical evaluator outputs.
- `tools/verify_netlist.py`, `tools/audit_verification.py`: independent function and metric verification.

## Compiling on Linux / WSL Ubuntu

```bash
make clean && make
./synth /path/to/stage1/case_001.txt /tmp/test.output.txt
```

Run instructor evaluator on all Stage 1 cases:

```bash
./evaluator ./synth /path/to/stage1 --report /tmp/round4.csv
```

For a complete evidence archive with independent checking, run:

```bash
bash run_round4_local.sh /tmp/ufug2106_evaluator '/path/to/data/stage1'
```

This runner needs `g++`, `make`, `python3`, and `sha256sum`. It creates a ZIP using the Python standard library; **`apt`, `sudo` and a system `zip` binary are not required**.

### User's established WSL paths

```bash
BASE="/mnt/e/canfiles/Common courses study/大学通识/26-27 Fall/UFUG 2106 Discrete Math/assignment/Final Project"
CASES="$BASE/data/stage1"
cp "$BASE/evaluator" /tmp/ufug2106_evaluator
chmod +x /tmp/ufug2106_evaluator
cd "$BASE/UFUG2106_Round4_Delivery"
bash run_round4_local.sh /tmp/ufug2106_evaluator "$CASES"
```

The local runner places all evidence in:

```text
local_runs/YYYYMMDD_HHMMSS_Round4/
    official.csv
    evaluator.log
    outputs/
    source_snapshot/
    independent_verification.log
    independent_crosscheck.csv
    per_case_comparison.csv
    environment.txt
    summary.txt
    report_ready/
        mathematical_design.md
        round4_reference_experiment.md
        local_metrics.md
        README.md
```

And produces `local_runs/YYYYMMDD_HHMMSS_Round4_local_results.zip` to share for independent review. Preserve all earlier rounds, and put the finalized Round 4 stage Report in that run's `report_ready/` folder.

## Design outline

Round 4 keeps Round 3's complemented-edge ROBDD, affine recognition, variable-order portfolio and timing-slack area recovery. Then it tries deterministic polarity labelings, exact algebraic rewrites and alternative representation orders. New circuit candidates are compared **only after producing a valid final netlist**. The original Round 3 result remains the fallback.

See the mathematical design document before making substantive algorithm changes; incorrect handling of node polarity or multi-output sharing can silently corrupt circuits.

## Known limitations

A larger random-order pool may have severe BDD node growth. Extra order candidates now have cooperative time checks and a node cap; the original Round 3 synthesizer still lacks a universal hard realtime bound. Stage 1 area sums are descriptive, not the instructor's undisclosed score. Generated tests do not replace full evaluation on future Stage 2 or hidden cases.

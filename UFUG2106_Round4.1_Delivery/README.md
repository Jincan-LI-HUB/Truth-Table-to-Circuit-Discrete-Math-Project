# UFUG2106 Round 4.1 — Runtime Optimization (Experimental Revision)

This **does not replace** the frozen Round 4 baseline. It tests three generic single-process C++17 variants against the instructor's 25 Stage 1 cases.

## Algorithms

- **Strict (`src/synth_strict.cpp`)**: shared immutable Truth Table/variable-influence cache; fewer phase-mapping passes, chosen to retain identical per-case area and delay against the original Round 4 benchmark.
- **Balanced (`src/synth_balanced.cpp`)**: shared cache + two base phase passes, no phase-after-algebra; nearly identical Area with shorter runtime.
- **Fast (`src/synth_fast.cpp`)**: prunes several duplicated synthesis candidates plus fewer phase passes; permits a small Area increase. This original fast source re-parses input each candidate: it is a controlled candidate-pruning ablation, not a caching claim.

All three sources retain the same truth-preserving Shannon/BDD construction and legal AND2/OR2/NOT mapping. Trimming candidate sets can affect optimization quality, **not** the semantics of the retained completed candidates. The observed PASS and Target Met counts are empirical, not worst-case guarantees.

## Measured reference (same container environment, sequential but not interleaved runs)

| Variant | PASS | Target Met | Area sum | Median Runtime (ms) | Maximum Runtime (ms) |
|---|---:|---:|---:|---:|---:|
| Frozen Round 4 | 25/25 | 25/25 | 528,910 | 225.201 | 5,840.173 |
| Strict | 25/25 | 25/25 | 528,910 | 161.757 | 4,848.9 |
| Balanced | 25/25 | 25/25 | 529,014 | 131.907 | 3,521.7 |
| Fast | 25/25 | 25/25 | 530,822 | 82.910 | 3,152.3 |

Area totals describe the 25 public cases, not the instructor's unpublished grade. Hardware, system load, disk performance and runtime budget may affect measured speed or chosen outputs. No candidate is guaranteed optimal.

Additional tests: each variant passed all 110 independent generated small truth tables (96/110 arbitrary synthetic delay targets) and both separately evaluated structural/high-entropy stress cases. Teacher Evaluator results are retained in `results/`.

## Local WSL reproduction

Extract this folder next to your existing `UFUG2106_Round4_Delivery` directory, then in WSL:

```bash
BASE="/mnt/e/canfiles/Common courses study/大学通识/26-27 Fall/UFUG 2106 Discrete Math/assignment/Final Project"
CASES="$BASE/data/stage1"
cp "$BASE/evaluator" /tmp/ufug2106_evaluator
chmod +x /tmp/ufug2106_evaluator
cd "$BASE/UFUG2106_Round4.1_Delivery"
bash run_round4_1_local.sh /tmp/ufug2106_evaluator "$CASES"
```

No `sudo`, `apt` or system `zip` command needed. Each experiment's output ZIP is placed in `local_runs/`, and report draft materials are placed at `local_runs/YYYYMMDD_HHMMSS_Round4.1/report_ready/`.

Send back the `*_Round4.1_local_results.zip`. The frozen 2026-11-11 local Round 4 CSV is stored under `results/round4_user_wsl_reference.csv`, so you will get a matched **same-machine** comparison.

### Notes on scope

- Immutable input caching and reusing variable influence leaves the Boolean function unchanged. It reduces redundant I/O/statistics computation.
- Candidate pruning preserves validity because the synthesizer still emits one complete correct candidate and only compares completed netlists. It can lose opportunities to minimize area.
- Faster synthesized circuits are not claimed; Runtime here means **time spent by the synthesizer**, independent of gate critical-path delay.
- Search on arbitrary unknown cases is not hard-real-time: some legacy synthesis candidates still have no inner interrupt. Treat hidden-case resource compliance as a testing objective.

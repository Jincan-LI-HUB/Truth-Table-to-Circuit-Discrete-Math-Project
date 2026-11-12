# UFUG2106 Round2 — 多策略 BDD / Two-level Shannon / Implicant Portfolio

This package reproduces a specific **historical** algorithm version from this conversation. It does not include instructor-supplied test cases or the evaluator; use your separate course copies.

## Version identity

- `src/synth.cpp`: original archived algorithm source renamed for a common build interface; **algorithm unchanged**.
- `SOURCE_PROVENANCE.txt`: source SHA-256 fingerprint.
- `results/reference.csv`: previously measured official Evaluator result; **not** a result measured on your machine.
- Historical result: 25/25 PASS, 25/25 Target Delay Met, Area sum 790,243.
- Historical median runtime 55.460 ms; another environment may differ.
- The 21/25 intermediate portfolio is an earlier iteration, archived under `results/intermediate_21target.csv`, not the final Round 2 release.

## Build (WSL Ubuntu)

```bash
make clean && make
./synth /absolute/path/to/stage1/case_001.txt /tmp/sample.output.txt
```

## Run full Stage 1 evaluation and retain evidence

```bash
bash run_round_local.sh /tmp/ufug2106_evaluator "/mnt/e/.../Final Project/data/stage1"
```

The script compiles from source, evaluates all 25 cases, performs independent exhaustive checks for n<=13 and sampled checks otherwise, summarizes differences against the historical reference, records environment and SHA-256, and archives **all 25 generated netlists** and logs under `local_runs/`.

The independent checker is additional evidence only: official Evaluator PASS remains the primary full-case verification.

To share results, upload `local_runs/*_Round2_local_results.zip`. Do not delete the logs when a run fails.

## Read before adding to the final report

- `docs/ALGORITHM_AND_MATH.md`: definitions, equations, mathematical correctness, algorithm decomposition and limitations.
- `docs/REPORT_EVIDENCE_TEMPLATE.md`: how to write the results chapter without inventing student contributions.
- `results/reference.csv`: historical per-case measurements; distinguish from `local_runs/.../official.csv`.

**Important:** The project handout does not define a numerical grade function. PASS, target_met, Area, Delay and Runtime must be reported separately. Area sums are descriptive, not official scores. Both implementations use only AND2/OR2/NOT and C++17, and are single-threaded. Compiler runtime and RAM behavior can vary between platforms.

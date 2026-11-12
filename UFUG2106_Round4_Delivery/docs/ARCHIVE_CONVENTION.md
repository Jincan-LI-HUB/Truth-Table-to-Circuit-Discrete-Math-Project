# Project report and evidence archive convention

The user stores every **stage/round report** under the corresponding local reproducibility run:

`local_runs/YYYYMMDD_HHMMSS_Round*/report_ready/`

Conventions:

- Do not overwrite previous rounds, even when a newer algorithm is better.
- Place finalized local stage reports and editable source in `report_ready/`.
- Keep `official.csv`, `evaluator.log`, environment info, SHA-256 manifests, and generated netlists one directory above under the run folder.
- Clearly distinguish local WSL measurements from assistant-container references, and `PASS` from `target_met`.
- The `*_RoundN_local_results.zip` file should contain the run folder including `report_ready/`, but need not include the instructor-supplied input truth tables or evaluator binary.
- Preserve algorithm rationale, correctness proofs, negative experiments, experimental conditions, per-case data, and runtime tradeoffs for the final report.

Round 4's `run_round4_local.sh` implements this convention automatically.

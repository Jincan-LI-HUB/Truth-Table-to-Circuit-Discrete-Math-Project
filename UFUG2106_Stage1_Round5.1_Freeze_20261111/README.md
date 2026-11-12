# Stage 1 — Round 5.1 Research Source Freeze

This archive is assembled from the WSL result ZIP originally supplied by the user.

- Canonical source: `source_snapshot/src/synth_round51.cpp` and the headers in the same folder.
- Source SHA-256: `cf90d0b110e6f45d1d508db351c95f10e7d704824fc34e17e6a5f5b783e20759`.
- Matched original official evaluator run: `benchmark/run1_round51.csv`; 25/25 PASS; 25/25 target delay met; Area sum 529,014.
- Extra evidence: 2 paired benchmark runs, independent verification log, 25 Round 5.1 output netlists, holdout CSVs, case input fingerprints and environment report.

## Claim boundary

This is a **research source freeze**, not a verified record of an actual course submission. Preserve the final submitted ZIP and its SHA-256 separately after submission.

## Build

On Linux with a C++17 compiler:

```bash
cd source_snapshot
make build/synth_round51
```

## Distribution

The ZIP contains course evaluation summaries and measured netlist outputs. Review course data-sharing rules before publishing evidence or logs on public GitHub. The private evaluator and full official input cases are intentionally excluded.

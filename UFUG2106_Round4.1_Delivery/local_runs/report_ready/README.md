# Round 4.1 — Dual-run local reproduction archive

Validated inputs:

- `20261111_121043_Round4.1_local_results.zip`
- `20261111_121216_Round4.1_local_results.zip`
- Historical same-machine comparator: `20261111_112447_Round4_local_results.zip`

This folder contains a synthesized, archival research report and a merged 25-case comparison. It does **not** replace either raw measurement ZIP, their circuit netlists, source snapshots, or independent verification logs.

## Install into your WSL project archive

Copy all files in this `report_ready/` folder to one of the existing Round 4.1 local run directories, for example:

`UFUG2106_Round4.1_Delivery/local_runs/20261111_121216_Round4.1/report_ready/`

You may also keep it in a separately named analysis directory; preserve the two raw trial directories unchanged.

## Results

- Strict: 25/25 PASS & target met, area sum 528,910, median runtimes 111.149 and 117.527 ms.
- Balanced: 25/25 PASS & target met, area sum 529,014, median runtimes 96.048 and 102.615 ms.
- Fast: 25/25 PASS & target met, area sum 530,822, median runtimes 67.605 and 63.035 ms.
- All 75 paired netlists are byte-identical between the two repetitions. Strict also reproduces original Round 4 output netlists byte-for-byte on all 25 cases.
- Official evaluator: 150/150 PASS. Independent checking: 13 exhaustive + 12 deterministic sample cases per variant per run.

The PDF is for reading; Markdown is editable for the final project report. Full SHA-256 values are in JSON.

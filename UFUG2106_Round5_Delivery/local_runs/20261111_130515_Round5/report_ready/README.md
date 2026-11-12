# Round 5 — report_ready archive

**Local run:** `20261111_130515_Round5` (WSL2, 2026-11-11).

Copy the contents of this `report_ready/` directory into:

`UFUG2106_Round5_Delivery/local_runs/20261111_130515_Round5/report_ready/`

The original experiment folder must be retained unchanged, particularly `reference/`, `round5/`, `source_snapshot/`, `profiles/`, `environment.txt`, `case_sha256.txt`, and `summary.json`. The report supplements these raw records and does not replace them.

- `Round5_Local_Reproduction_Report_20261111.pdf` — 4-page Chinese technical report.
- `Round5_Local_Reproduction_Report_20261111.md` — editable Markdown source, equations and case tables.
- `Round5_Local_PerCase_Comparison.csv` — augmented 25-case metrics including timing slack.
- `Round5_Validated_Local_Summary.json` — derived and checked summary fields.
- `Round5_Original_Mathematical_Design.md` — original mathematical design document provided in the local result bundle.
- `Round5_Original_Reference_Experiment.md` — original reference experiment document.

**Verified local results:** 25/25 official PASS, 25/25 target met, 25/25 byte-identical Netlists; total area 529014 in both versions; median runtime 87.041 -> 68.861 ms. The reported runtime reduction is a single-run estimate.

# Draft v0.3 — P1/P2 Technical Revision

This is a **review draft**, not a final submission. P0 authorship/AI declaration was explicitly deferred by the student.

## Contents
- `technical_report/main.tex` / `main.pdf`: IEEEtran manuscript (updated candidate control-flow algorithm, internal ranking, required-time proof, fixed-boundary caveat, RAM-limit scope, and worked example).
- `trial_log_record/main.tex` / `main.pdf`: tutorial-oriented research log (full 8-row truth table, netlist with actual node IDs, cost & timing calculation, worked absorption, proof caveats).
- `shared/scripts/verify_worked_example.py`: no-dependency exhaustive simulation of the example; writes `shared/data/worked_example_truth_table.csv`.
- `shared/data/`: carried-over original experiment CSVs; unchanged by the P1/P2 revision except for the added worked-example table.
- `shared/figures/`: carried-over charts. The new original sharing diagram is TikZ embedded in `technical_report/main.tex` and needs no external image.
- `REVIEW_RESOLUTION_P1_P2.md`: itemized audit log.

## Reproduce

```bash
python3 shared/scripts/verify_worked_example.py
(cd technical_report && pdflatex main.tex && bibtex main && pdflatex main.tex && pdflatex main.tex)
(cd trial_log_record && pdflatex main.tex && bibtex main && pdflatex main.tex && pdflatex main.tex)
```

## Source integrity
The frozen Round 5.1 research source is NOT modified here. Its SHA-256 is:
`cf90d0b110e6f45d1d508db351c95f10e7d704824fc34e17e6a5f5b783e20759`.

## Evaluator interpretation
The uploaded Linux x86 evaluator's `--help` describes `--timeout-ms`, `--ram-kb`, `--report` and `--save-outputs`, but does **not** publish a numerical scoring rule. The course PDF describes only qualitative preferences. The manuscript's lexicographic tuple is the synthesizer's **internal** heuristic.

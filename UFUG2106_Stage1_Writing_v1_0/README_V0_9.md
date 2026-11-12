# UFUG2106 Stage 1 Writing Draft v0.9

This is an editable **Draft**, not the final Canvas submission. All P0 contribution/AI acknowledgments remain pending verified author facts. The first-page temporary `\thanks` has been removed.

## Included artifacts
- `technical_report/main.tex`, `main.pdf`, `main.bbl`, plus editable TikZ overview figure in `technical_report/figures/`.
- `trial_log_record/main.tex`, `main.pdf`, `main.bbl`.
- `shared/bibliography/references.bib`: actually used by **both** papers, with IEEEtran numbered bibliography.
- `shared/data/*.csv`, especially `round_history.csv`; `shared/scripts/make_milestone_table.py` generates Table I with real median synthesis runtimes.
- `shared/scripts/make_figures.py`, seven empirical figures in PDF/PNG; user-defined 8-color `palette.json`/`palette.tex`.
- `shared/test_generation/`: unchanged deterministic supplemental test-generation scripts and case-hash manifests, **without** republishing original course truth-table inputs.
- `shared/evidence/TEST_SUITE_PROTOCOL.md`, `REFERENCE_AUDIT_v0_9.md`, `TEST_CASE_MANIFEST_AUDIT_v0_9.json`, and figure/data provenance manifest.
- `REVIEW_ROUND7_REFERENCES_AND_VISUALS.md`: request-by-request changes and scope.

## Rebuild
With LaTeX + IEEEtran BibTeX installed, run `bash build_papers.sh` at package root. It runs `pdflatex`, `bibtex`, `pdflatex`, `pdflatex`. On systems where the `bibtex` command is absent but `/usr/bin/bibtex.original` is installed, the build script uses that executable.

Rebuild empirical figures from the included CSVs with `python3 shared/scripts/make_figures.py`; these outputs may have non-identical binary hashes due to PDF metadata while reproducing the same data.

## Evidence boundaries
Stage 1 historical runtimes in Table I are from **separate** WSL run archives, not one paired experiment; Fig. 7 and the corresponding CSV report controlled within-run comparisons. Synthetic tests check selected function families, not unreleased Stage 2. Source freeze and course-supplied test inputs/evaluator are stored in separate private archives, not inside this public-facing writing bundle.

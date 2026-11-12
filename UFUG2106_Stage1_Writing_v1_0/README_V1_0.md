# UFUG2106 Stage 1 — Manuscripts v1.0

Two papers are included: `technical_report/main.tex` (IEEEtran, course-facing) and `trial_log_record/main.tex` (long-form research notebook for study / possible GitHub publication).

## What changed from v0.9
- Resolved the previously deferred author contribution / AI-use disclosure in **both manuscripts**.
- Named the actual collaboration model without fabricating individual module ownership.
- Disclosed extensive generative-AI involvement in C++ programming, experimental automation/data aggregation, research assistance and writing, rather than describing it as editing only.
- Kept the Round 5.1 frozen research source and historical benchmark data unchanged; clarified that this is not necessarily the final course-portal submission.
- Removed outdated manuscript-facing "pending contribution/AI disclosure" statements and updated the Trial Log title-page version.

## Build
From this directory run `bash build_papers.sh`. The script uses pdflatex and BibTeX (`IEEEtran` style) and produces both PDFs.

To regenerate figures: `python3 shared/scripts/make_figures.py`.
To verify bundled provenance: `python3 shared/scripts/verify_provenance.py --help` (see `README_V0_7.md` for modes).

## Boundaries
The writing package includes figures, data, `.bib`, TikZ, generator scripts, test manifests and checks; course-supplied input truth tables and evaluator are not republished. AI usage is reported transparently. The paper claims empirical performance only for archived runs.

## Documentation
`V1_0_RELEASE_AUDIT.md` lists edits, bibliographic and TeX checks, and remaining actual-submission checks. Prior review records remain for research provenance.

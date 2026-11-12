# UFUG2106 Stage 1 Manuscripts — Draft v0.6

Two manuscripts, both **Stage 1 only**:

- `technical_report/main.tex` → `technical_report/main.pdf` (IEEEtran, 11 pages)
- `trial_log_record/main.tex` → `trial_log_record/main.pdf` (student's homework template adapted as an instructional research notebook, 20 pages)

## Review focus

The purpose of v0.6 is mathematical and pedagogical depth rather than adding a new synthesis algorithm. See `REVIEW_ROUND4_EXPLANATION_DEPTH.md` and `V0_6_CHANGELOG.md` for a section-by-section audit.

The adopted **research freeze** remains Round 5.1; no claim is made that the actual Canvas submission has already been identified. Unconfirmed contribution and AI-use details remain to be filled at submission time.

## Reproducible evidence

```bash
python3 shared/scripts/verify_deep_exposition.py
python3 shared/scripts/verify_worked_example.py
python3 shared/scripts/make_figures.py
```

The source of each empirical plot remains in `shared/data`, its producing script is under `shared/scripts`, and its exported PDF/PNG pair is under `shared/figures`. A fixed set of evidence-file SHA-256 hashes is listed in `editorial/V0_6_EVIDENCE_INTEGRITY.json`.

Compile separately:

```bash
cd technical_report && latexmk -pdf -interaction=nonstopmode main.tex
cd ../trial_log_record && latexmk -pdf -interaction=nonstopmode main.tex
```

Dependencies are LaTeX packages named in the documents and the existing standard-library plotting dependencies (`requirements-figures.txt`). Generated build auxiliary files are not needed in the deliverable archive.

**P0 remains deferred.** Both PDFs are review drafts, not a declaration of complete authorship/AI compliance or final submission.

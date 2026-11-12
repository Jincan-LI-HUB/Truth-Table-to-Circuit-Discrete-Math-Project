# UFUG2106 · Stage 1 Writing Package — Draft v0.8

Two **editable, compiled** documents based on the Stage 1 research archive:

| Document | Audience | Files | Status |
|---|---|---|---|
| Stage 1 Technical Report | Instructor / TA | `technical_report/main.tex`, `main.pdf` | IEEEtran, 11 pages, editorial review completed |
| Trial Log & Research Development Record | Future self / GitHub readers | `trial_log_record/main.tex`, `main.pdf` | Homework-derived single-column, 20 pages, editorial review completed |

This is **not** marked as a final submitted version. The requested P0 (actual contributions, course-compliant AI-use statement, and actual Canvas source ZIP) is left pending. The main research candidate is frozen Round 5.1; this writing archive does not bundle the course's private test inputs/evaluator or the large original result ZIPs.

## Build the two documents

On Linux with a working TeXLive installation:

```bash
(cd technical_report && latexmk -pdf -interaction=nonstopmode -halt-on-error main.tex)
(cd trial_log_record && latexmk -pdf -interaction=nonstopmode -halt-on-error main.tex)
```

The Technical Report uses IEEEtran; the Trial Log uses the user's homework-derived template with `newtxtext/newtxmath`. Both pull figures and color definitions from the common `shared/` directory.

## Regenerate mathematical examples and figures

```bash
python3 shared/scripts/verify_provenance.py --report editorial/audit_bundled.json
python3 shared/scripts/verify_deep_exposition.py
python3 shared/scripts/verify_worked_example.py
python3 shared/scripts/make_figures.py --out-dir /tmp/ufug2106_figures
bash shared/tests/run.sh
```

Regenerating a PDF chart need not yield exactly the same binary bytes due to exporter metadata, but the source data and values are unchanged.

## What's inside

- `shared/data/`: evaluator-derived normalized CSVs and archived ablation data; does not include raw course truth tables.
- `shared/scripts/`: data extraction, provenance auditing, figure generation and worked-example verification.
- `shared/figures/`: PDF/PNG charts made with the user's low-saturation color palette.
- `shared/evidence/`: claim–evidence ledger, citation verification, figure-data manifest and data-source notes.
- `shared/bibliography/references.bib`: editable bibliography; both drafts also retain their locally compiled references.
- `editorial/`: revision patches, audit outputs, build logs and artifact summary.
- `REVIEW_ROUND6_FINAL_EDITORIAL.md`: exact editorial findings and remaining submission gates.

## Provenance boundaries

The writing package permits **figure reproduction** from bundled CSVs. Re-extracting historical official runs requires the separately archived nine experiment ZIPs. A fresh official evaluator rerun requires the frozen C++ sources, instructor inputs/evaluator and Linux x86. Runtime can change due to elapsed-time-based candidate eligibility; output byte identity is not guaranteed across executions. Data in the writing package should not be mistaken for fresh Stage 2 testing.

Original research notes and prior review records remain archived. **Do not upload the private evidence ZIPs or instructor files to a public GitHub repository without permission.**

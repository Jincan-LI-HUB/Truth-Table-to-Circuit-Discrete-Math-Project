# UFUG2106 — Stage 2 Formal Report

This is the **canonical editable report directory**, not a version archive. It is intended to be copied into, and overwrite matching files under:

```text
E:\canfiles\Common courses study\大学通识\26-27 Fall\UFUG 2106 Discrete Math\assignment\Final Project\Stage 2 Formal Report
```

## Scope

The report summarizes the whole Truth Table to Circuit project, **principally explaining the final R10.0 synthesis solution**: how a correct initial circuit is built, why the mapped shared DAG is the optimization object, how bounded cut rewriting produces alternatives, how the program ranks and accepts completed candidates, and what matched tests establish. The main controller is presented as Algorithm 1 near the execution architecture; Algorithm 2 formalizes the bounded four-leaf cut-resynthesis subroutine. These complement the architecture figure, rather than replacing the source-aligned mathematical explanation. The separate unified Stage 1–Stage 2 Research Trial Log preserves all individual development rounds and their decision evidence; the report selects only the milestones needed to explain the final method.

The baseline comparisons have distinct meanings: **Z1** is Zeyun Du's actually submitted Stage 1 implementation, **J51** is the independent Stage 1 R5.1 research baseline, and **R10** is the final Stage 2 solver. The mandatory first-versus-final comparison is Z1 against R10.

## Files

- `main.tex`, `main.pdf` — editable IEEE LaTeX and compiled report.
- `references.bib`, `main.bbl` — references (the `.bbl` also allows pdfLaTeX compilation without BibTeX).
- `casewise.tex`, `build_casewise.py` — 50-case Z1/R10 first-repeat table and its deterministic CSV-based generator.
- `figures/*.pdf`, `figures.py` — vector diagrams and reproducible charts.
- `data/*.csv`, `verify.py` — matched results and numeric checks.
- `palette.json` — fixed muted colors, dark labeling and grayscale-accessible markers.

Source archives, restricted course inputs, and the evaluator are kept in their existing research directories, not duplicated here.

## Rebuild and verify

From this directory:

```bash
python3 build_casewise.py
python3 verify.py
python3 figures.py
pdflatex -interaction=nonstopmode -halt-on-error main.tex
pdflatex -interaction=nonstopmode -halt-on-error main.tex
```

Run `bibtex main` **before** the two final pdfLaTeX calls only if a BibTeX executable is installed and you have changed `references.bib`. Otherwise the maintained `main.bbl` provides the bibliography.

The casewise table and figures use `data/matched_case_metrics.csv` (three methods, two repeats, 50 cases), `data/official_r90_r100_casewise.csv`, and the controlled R8.6/R10.1 datasets. Runtime observations from separate experimental families are not pooled into a single causal comparison.

## Interpretation and evidence boundaries

The complete-system 50-case Z1/R10 comparison and the narrowly controlled R9.0/R10.0 final-pass comparison answer **different questions**. A cut truth signature proves functional equivalence under the specified boundary conditions; the full output-reachable DAG determines physical area and timing. Search quotas and periodic checks reduce resource exposure but do not establish universal hard limits. The report identifies these distinctions at the corresponding method and evaluation claims.

The editorial and integrity audit checks official specification coverage, claim scope, references, credited contributions and source-derived experimental totals. It fixes the 50-case appendix status/header alignment and regenerates that table from the matched CSV, and corrects single-column figure scaling for legibility. The limited root/time checks are not represented as worst-case real-time bounds. **No benchmark was rerun and no experimental number was changed during this editorial revision.** Use `verify.py` for the archived aggregate checks.

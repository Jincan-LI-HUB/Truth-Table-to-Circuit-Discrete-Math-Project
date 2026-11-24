# UFUG2106 — Stage 2 Formal Report

This directory contains the canonical editable report and compiled PDF.

## Scope

The report summarizes the whole Truth Table to Circuit project, **principally explaining the final R10.0 synthesis solution**: how a correct initial circuit is built, why the mapped shared DAG is the optimization object, how bounded cut rewriting produces alternatives, how the program ranks and accepts completed candidates, and what matched tests establish. The main controller is presented as Algorithm 1 near the execution architecture; Algorithm 2 formalizes the bounded four-leaf cut-resynthesis subroutine. These complement the architecture figure, rather than replacing the source-aligned mathematical explanation. The separate unified Stage 1–Stage 2 Research Trial Log preserves all individual development rounds and their decision evidence; the report selects only the milestones needed to explain the final method.

The mathematical sections explain **R10.0**, Jincan Li's frozen Stage 2 research solver. The historical comparison uses **Z1**, Zeyun Du's submitted Stage 1 implementation, and **J51**, Jincan's independent Stage 1 research baseline. The new integration section adds **Integrated Final**, the planned team delivery, and uses a fresh four-method matched batch. [Integration audit](../Final_Submission_by_Zeyun_DU/integration/AUDIT.md)

## Files

- `main.tex`, `main.pdf` — editable IEEE LaTeX and compiled report.
- `references.bib` — bibliography source. BibTeX generates `main.bbl` locally.
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
python3 ../Final_Submission_by_Zeyun_DU/integration/verify_evidence.py
pdflatex -interaction=nonstopmode -halt-on-error main.tex
bibtex main
pdflatex -interaction=nonstopmode -halt-on-error main.tex
pdflatex -interaction=nonstopmode -halt-on-error main.tex
```

The integration table reads a generated TeX fragment from the archive. Regenerate it with the archive verifier's `--write` flag when reproducing the derived tables.

The casewise table and figures use `data/matched_case_metrics.csv` (three methods, two repeats, 50 cases), `data/official_r90_r100_casewise.csv`, and the controlled R8.6/R10.1 datasets. Runtime observations from separate experimental families are not pooled into a single causal comparison.

## Interpretation and evidence boundaries

The complete-system 50-case Z1/R10 comparison and the narrowly controlled R9.0/R10.0 final-pass comparison answer **different questions**. A cut truth signature proves functional equivalence under the specified boundary conditions; the full output-reachable DAG determines physical area and timing. Search quotas and periodic checks reduce resource exposure but do not establish universal hard limits. The report identifies these distinctions at the corresponding method and evaluation claims.

The earlier editorial audit checks specification coverage, claim scope, references, attributed contributions and the historical figures. The final integration adds a new benchmark, and the existing R10.0 casewise appendix and its source data retain their original values. Use `verify.py` for the archived aggregate checks.

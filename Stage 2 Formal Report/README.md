# UFUG2106 — Stage 2 Formal Report

The canonical IEEE manuscript explains **Integrated Final**, the planned team solver pinned to upstream commit `59e3350`. It follows the executable from the complete BDD fallback through scheduled mapping, J51 candidates, shared-output selection, the inherited SOP cut pass and conditional timing rescue. The independent R10.0 investigation supplies algorithmic components and controlled historical evidence. Its standalone controller is documented in the unified Research Trial Log.

## Files

- [`main.tex`](main.tex), [`main.pdf`](main.pdf), [`references.bib`](references.bib) — editable manuscript, compiled PDF and references.
- [`casewise.tex`](casewise.tex), [`build_casewise.py`](build_casewise.py) — deterministic four-method overview and both 50-case matched repeats.
- [`build_phase_c_figures.py`](build_phase_c_figures.py), [`phase_c_data.py`](phase_c_data.py), [`palette.json`](palette.json) — figures and archive readers. `figures/phase_c_*` contains the PDF, SVG and PNG exports.
- [`verify.py`](verify.py), [`PHASE_C_REVISION.md`](PHASE_C_REVISION.md) — numerical checks and claim traceability.
- [`Research_Trial_Log/`](Research_Trial_Log/) — R1–R10.1 archive and expanded team integration record.

## Rebuild and verify

From this directory, with Python 3, pandas, NumPy, Matplotlib, pdfLaTeX and BibTeX:

```bash
python3 build_casewise.py
python3 build_casewise.py --check
python3 verify.py
python3 ../Final_Submission_by_Zeyun_DU/integration/verify_evidence.py
python3 build_phase_c_figures.py
latexmk -pdf -interaction=nonstopmode -halt-on-error main.tex
```

Without `latexmk`, run `pdflatex main.tex`, `bibtex main`, and `pdflatex main.tex` twice. These commands use the archived CSVs without rerunning any solver. To export repeat 2 for comparison, run `python3 build_phase_c_figures.py --repeat 2 --out /path/to/repeat-2-figures`. The tracked figures and figure captions use repeat 1 for matched plots; the resource figure's separate direct-process RSS series has no repeat number.

The Phase C figures use canonical manuscript colors and IEEE single- or double-column widths. The current paper includes 12 figures, with mathematical examples and source schematics separated from observations. The matched plots read the integration archive. The combined ablation figure reads the archived R8.6, R9.1 and R10.1 experiment files. The earlier percentage casewise and aggregate resource charts are available as companions. See the [figure record](FIGURE_REVISION_PLAN.md) for the scientific questions, data and widths.

## Evidence

The [integration audit](../Final_Submission_by_Zeyun_DU/integration/AUDIT.md) indexes the matched evaluator outputs, independent replay and direct RSS. Both repeats have 50/50 passes and targets for each method. Integrated Final reduces summed area by about 22.6% against Z1 and 14.4% against R10.0, with higher synthesis runtime than R10.0. The earlier controlled experiments describe the passes on their original incumbents. The matched batch contains no iso-budget control that separates changes in architecture from changes in search allowance.

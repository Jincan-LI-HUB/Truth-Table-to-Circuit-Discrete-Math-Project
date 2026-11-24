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

The Phase C figures adapt the UFUG2106 Figure Reuse Kit's architecture boxes and arrows, shared-cone contours and directly labeled zero-baseline area bars. They use canonical manuscript fills and keep dark teal for selected results and rust for timing violations or recovery. The eight figures are sized for IEEE single- or double-column placement. Architecture and budget figures are source schematics; the cone, cofactor and critical-cut figures are constructed examples. The three empirical figures read the integration archive. The historical `figures.py` and its datasets are retained for reproduction of earlier plots.

## Evidence

The [integration audit](../Final_Submission_by_Zeyun_DU/integration/AUDIT.md) indexes the matched evaluator outputs, independent replay and direct RSS. Both repeats have 50/50 passes and targets for each method. Integrated Final reduces summed area by about 22.6% against Z1 and 14.4% against R10.0, with higher synthesis runtime than R10.0. The earlier controlled experiments describe the passes on their original incumbents. The matched batch contains no iso-budget control that separates changes in architecture from changes in search allowance.

# UFUG2106 Truth Table to Circuit — Complete Research Trial Log

This unified research archive preserves the finalized Stage 1 R1–R6.1 mathematics and the Stage 2 R7–R10.1 reasoning and decisions. The evidence cutoff is 24 November 2026. Part III tracks team integration through upstream paired pass studies, headroom and cap trials, sequential timing recovery, matched evaluation and the residual failure at freeze. [Integration audit](../../Final_Submission_by_Zeyun_DU/integration/AUDIT.md)

## Files

- `UFUG2106_Stage2_Research_Trial_Log_v3.pdf` — combined compiled research record (title inside: *Complete Research Trial Log*).
- `tex/main.tex`, `tex/cover.tex` — master and shared title page, with continuous contents and unified references.
- `tex/stage1_body.tex`, `tex/stage2_body.tex`, `tex/decision_atlas.tex` — preserved substantive bodies and the revised high-information variant analysis.
- `tex/final_integration.tex` — integration decision and evidence record.
- `RESEARCH_TRIAL_LOG_v3.md` — merged searchable Markdown companion; the TeX/PDF determine the final page layout.
- `source_stage1_main.tex`, `tex/source_stage2_full.tex` — unmodified evidence input texts for reassembly.
- `figures/13_...` through `figures/17_...` — new multiscale comparisons and archived variant-dispersion analyses; the originals and detailed casewise figures remain in `figures/`.
- `data/*.csv` — complete casewise and round/variant evidence, including the 111-name configuration index (105 with at least one full-pass record).
- `scripts/merge_full_trial.py`, `scripts/plot_high_resolution_comparisons.py`, `scripts/verify_evidence.py` — reproduction, figure generation, and audit.

## Key visualization decisions

- Stage 1: early dramatic area reduction is plotted alongside a **late-stage zoom** around R5.1, where the differences are only 104–276 area units.
- Stage 2: complete 25-case checkpoints are shown as **relative area and delay** rather than conflating circuit delay with synthesis time; R7's incomplete 24/25 result is excluded from the 25-case area trajectory.
- Late convergence: a **narrow-scale** chart makes the 1,034-unit Stage 2-bank improvement between R9.0 and R10 visible.
- All 111 variants: the CSV remains the full index; the main PDF replaces eight near-identical scatter plates with a **within-Round complete-case area-spread plot** (qualified/total configurations labeled; symlog scale declared explicitly).
- Controlled R8.6, R9.1 and R10.1 comparisons retain their paired original evidence and meaningful precision.

**Important:** Cross-round charts summarize archived development snapshots, not one-factor causal effects. Historical total-area plots cannot be interpreted as the course's undisclosed numerical score.

## Rebuild (from this directory)

```bash
python3 scripts/verify_evidence.py
python3 ../build_phase_c_figures.py --only architecture systems resources pass_evidence policy_evidence recovery_evidence
cd tex
pdflatex -interaction=nonstopmode -halt-on-error main.tex
pdflatex -interaction=nonstopmode -halt-on-error main.tex
cp main.pdf ../UFUG2106_Stage2_Research_Trial_Log_v3.pdf
```

The tracked historical figures are used directly in this build. For reconstruction of the historical figures and TeX bodies, use `scripts/plot_high_resolution_comparisons.py` and `scripts/merge_full_trial.py` from this directory.

Dependencies: Python `pandas`, `numpy`, `matplotlib`, `pymupdf`; pdfLaTeX with the same Stage 1 package set. The original Stage 1 PDF and assignment PDF are held under `references/` for exact-source checking.

The existing `scripts/build_document.py` now delegates to `merge_full_trial.py` as a backwards-compatible entry point, so it **cannot accidentally restore an obsolete Stage-2-only paper**.

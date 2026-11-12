# Stage 1 Manuscript Draft v0.2 — Evidence Update (pre-review)

## Added source evidence
1. Round 3 sequential ablation CSV (including a distinct implication branch); no invented isolated feature effects.
2. Round 4 postprocessor per-case CSV (25 rows) and its direct strategy-wise aggregate.
3. Round 6.1 40- and 16-function development budget JSON files; these are not independent holdouts.
4. Round 5.1 student-confirmed frozen-source SHA-256 manifest; research freeze != Canvas submission.
5. Single standalone case_024 GNU time observation, transcribed from user's terminal output; not evaluator timing.

## Added reproducible figures
- `shared/figures/round3_ablation_path.{pdf,png}`.
- `shared/figures/round4_postprocess_ablation.{pdf,png}`.
- `shared/figures/round61_budget_tradeoff.{pdf,png}`.

All figures derive from `shared/data/*.csv` and the original inputs in `shared/data/raw_evidence/`; regenerate with `python3 shared/scripts/make_figures.py`.

## Research integrity and deferred review
- Never call the R3 stages randomized, independent effects.
- Never conflate R4 postprocessor-only area 532,070 with full R4 area 528,910.
- Never call R6.1 budget development data a blind test, or local postprocessor wall time the official full synthesizer runtime.
- Do not combine `case_024` single-run 1.66 seconds with official paired benchmark medians.
- Confirm named contributions and precise AI tool-use record before final course submission.
- Stage 2 outside scope. Actual submitted source version not yet asserted.

**Next step:** Detailed manuscript review of mathematical assumptions, provenance, method-source correspondence, and presentation.

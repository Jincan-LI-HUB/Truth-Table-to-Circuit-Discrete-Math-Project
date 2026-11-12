# Draft v0.7 — Research Reproducibility and Final Academic Audit

This revision follows Draft v0.6 and **does not** change frozen synthesis sources, original benchmark data, or the deferred P0 contribution/AI declaration. The new work concerns evidence provenance and manuscript clarity.

## New materials

- `shared/scripts/verify_provenance.py`: standard-library, read-only multi-level audit. With original ZIPs it verifies original archive SHA-256 and exact regenerated CSVs; without ZIPs it verifies bundled evidence schema/hashes. Optional frozen source hash check.
- `shared/evidence/CLAIM_EVIDENCE_LEDGER.csv`: one source and inference scope per high-value quantitative claim.
- `shared/evidence/BIBLIOGRAPHY_VERIFICATION.md`: verified classic-source DOIs and conceptual attribution boundaries.
- `REVIEW_ROUND5_ACADEMIC_AUDIT.md`: review findings and open limits.
- Technical Report: new dedicated section describing data-lineage and four levels of reproducibility.
- Trial Log: a stepwise replication exercise distinguishing figures from full algorithm reruns.

## Reproduce the manuscript (from the writing archive only)

```bash
python3 shared/scripts/verify_provenance.py --report editorial/audit_bundled.json
python3 shared/scripts/verify_deep_exposition.py
python3 shared/scripts/verify_worked_example.py
python3 shared/scripts/make_figures.py
(cd technical_report && latexmk -pdf -interaction=nonstopmode -halt-on-error main.tex)
(cd trial_log_record && latexmk -pdf -interaction=nonstopmode -halt-on-error main.tex)
```

## Audit against original experiments (requires separate source ZIPs)

```bash
python3 shared/scripts/verify_provenance.py \
  --source-dir '/path/to/archived/local_results_zip_files' \
  --freeze-dir '/path/to/UFUG2106_Stage1_Round5.1_Freeze_20261111' \
  --report editorial/audit_full.json
```

The writing package includes **neither the original local-run ZIPs nor the private instructor truth tables/evaluator**. A separate, controlled official rerun would require those inputs and a suitable Linux environment. The frozen research source hash is not a claim of a Canvas submission.

P0 remains deferred at the author's direction. Stage 2 not included.

**Figure byte reproducibility:** Matplotlib may write nondeterministic PDF export metadata. See `editorial/V0_7_ARTIFACT_INTEGRITY.json` for current PDF hashes and unchanged CSV source digests.

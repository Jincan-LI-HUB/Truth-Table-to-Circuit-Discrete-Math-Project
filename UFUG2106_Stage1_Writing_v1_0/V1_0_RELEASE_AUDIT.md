# Stage 1 Manuscripts v1.0 — Author Contribution & AI Disclosure Release Audit

## Scope
This is the first full v1.0 **writing release**, produced from the reviewed v0.9 source. It does not represent a new synthesis algorithm round, a new benchmark, or an assertion that a particular ZIP has been submitted to the course portal.

## Changes verified
1. Technical Report: added a concise, fact-based `Collaborative Development and AI Assistance` section. It names both students and describes independent initial exploration followed by method comparison and integration, without inventing per-module ownership.
2. Technical Report: transparently discloses extensive generative-AI roles: substantial C++ coding and revision, benchmarking/data-collection/packaging automation, algorithm discussion, mathematical reasoning support, and report writing. Student direction and independent WSL evidence checks are distinguished from AI outputs.
3. Trial Log: added a detailed `Collaboration, AI-Assisted Development, and Responsibility` section with collaborative process, AI roles, human critical review, safeguards and limits. Changed title-page status to `Stage 1 research record v1.0`.
4. Removed the manuscript statements that the contribution and AI disclosure remained pending; kept accurate caveat about *actual* source ZIP to be uploaded to the course portal.
5. Corrected a pre-existing `\texttt` typography typo in Technical Report reproducibility notes.
6. Both manuscripts retain active BibTeX references (`shared/bibliography/references.bib`, IEEEtran style) and the user's palette/TikZ and evidence scripts.

## Frozen engineering facts (unchanged)
- Round 5.1 research source (verified `synth_round51.cpp`) SHA-256: `cf90d0b110e6f45d1d508db351c95f10e7d704824fc34e17e6a5f5b783e20759`.
- Main public Stage 1 official results: 25/25 PASS; 25/25 target met; aggregate gate area 529,014.
- Source snapshot and official test inputs remain in separate archived bundles; the writing package is NOT an all-in-one official evaluator rerun.
- All `shared/` data, plots, scripts, and citations are byte-identical to v0.9 (confirmed through SHA-256 comparison). No performance observation, chart value or research result was modified in v1.0.

## Verification performed
- `bash build_papers.sh`: both LaTeX + BibTeX pipelines built successfully.
- Bundle-only provenance audit: **18/18 PASS**.
- Worked-example and detailed derivation checks: **PASS**.
- Frozen typed DAG regression: **2,000 networks / 8,000 transform checks PASS**.
- PDF inspection: both PDFs generated; no unresolved citations or LaTeX overfull box warnings after layout revision. First-page authorship footnote remains removed.

## Remaining actual-submission checks
- Both students should review the exact final PDF and disclosure wording.
- Verify actual submitted C++ source ZIP matches the paper's chosen research implementation (or update the report to match).
- Follow the course's exact upload and AI-use requirements; do not imply an archived research freeze has been submitted already.
- For GitHub publication: omit student IDs if not needed, and do not publish private instructor truth tables or evaluator binaries without permission.

## Bibliography and generated figures
The `.bib` file is actually used by both papers. Existing empirical figures are backed by CSV/JSON; TikZ diagrams are editable. `shared/scripts/make_figures.py`, original data, color definitions, generated PDFs/PNGs and test-generation scripts remain included. PDF metadata may change on regeneration without changing plot contents.

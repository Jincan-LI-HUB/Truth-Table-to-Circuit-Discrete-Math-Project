# Phase D final acceptance audit

**Technical acceptance passed. Team authorization confirmed.** The repository owner confirmed that the team members authorized public GitHub archiving of their contributions. Approval of the full release scope, including retained third-party materials, is pending.

## Acceptance checklist

| Check | Result and evidence |
|---|---|
| Candidate and lineage | PASS. The isolated Git clones started at `34d6bf24e1c0a6c41cee792d567688ee74c353fe`. The pre-integration research baseline is `4838e50d52408087639c3d3816b10761f18f6ccb` and the integration archive checkpoint is `293258a6d9ba9af9e07899d84e22923a46e11779`. Git tree and blob comparisons covered frozen solvers, headers, evaluator and original experimental data. |
| Team archive | PASS. Checked all 74 imported Git blobs and upstream SHA-256 values against a separate upstream clone at `59e33505616d127fc06a63580ca3ae3c34d1da72`. All 74 local hashes match the manifest, including eight intentionally redacted report files (four PDF/HTML pairs). All 50 course inputs and the evaluator match their upstream blobs. [Manifest](Final_Submission_by_Zeyun_DU/PROVENANCE.json) |
| Mathematics | PASS within stated scope. Reviewed the stated invariants and candidate-selection paths against the pinned source. Independent enumeration covered 65,812 Boolean functions of 1–4 leaves, 65,536 four-by-four Boolean slices and grouped cofactor tables, 16 two-by-two slices, 6,400 reference/rollback trials, and the 32 assignments and four union areas of the joint-switch example. Required-arrival and lexicographic feasibility arguments were checked against their boundary and positive-target assumptions. [Claim evidence matrix](CLAIM_EVIDENCE_MATRIX.md) |
| Experimental claims | PASS. Recomputed the aggregates, joint outcomes, ratios, Pareto ordering, per-case slack and exposure, direct RSS and historical controls from archived rows. Matched evaluator files had all 400 expected case keys with unique observations and no failures. Checked all 100 independent replay records against their matched evaluator rows. The separate interrupted J51 record and older 49/50 results remain in scope. |
| Figures and documents | PASS. 18 figures in PDF/SVG/PNG for each matched repeat in separate output directories. Rendered every final PDF page, reviewed at page scale and inspected affected figures separately. Both document builds reached stable cross-references. |
| Documentation | PASS for root README, Quick Start, report guides, and current archive entry points. Verified local Markdown links and TeX figure inputs. The archived upstream course notice still points to the original upstream file layout. Use the root course files and the [team solver guide](Final_Submission_by_Zeyun_DU/README.md) for this checkout. |
| Research integrity | Authorship, contribution statements and AI disclosures were checked against the pinned archive and reports. Newly added text contains the necessary source identities and relative repository paths. The existing upstream material permissions remain unresolved. |

## Exact identities

Git tree IDs pin the complete path contents including headers and archived case data. The SHA-256 values below identify individual files. The [matched environment record](Final_Submission_by_Zeyun_DU/integration/data/matched/environment.json) lists every compiled source member and all 50 input SHA-256 values.

| Object | Git object ID | SHA-256 for file |
|---|---|---|
| Z1 entry point, archived Stage 1 `src/synth.cpp` | `9f43431a521d8520a77feb1aa1ccf268e01ef44f` | `cd31f7d2a0540c85dc32277ad97fda0e221e769d323ea4adfec8b69916584550` |
| J51 `synth_round51.cpp` | `68ec9f54b27081641ac10358f81eef260acfcbdb` | `cf90d0b110e6f45d1d508db351c95f10e7d704824fc34e17e6a5f5b783e20759` |
| R10.0 `submission/synth.cpp` | `f60275ba5902599b1f8182b8226c43d963099b6a` | `8c863f1a1c9555ae571948a0424c25642c29c9a9f98f1f3e5f193c6b20f5b15d` |
| Integrated Final `src/synth_stage2.cpp` | `217282c40caeb3ca914faf2bd783db70d753bd16` | `dacee2c609da53ccdf8a29457a9b3a982d7fb1e5df99a5d041ec65be83762a3d` |
| J51 verified `source_snapshot/` | `480d723518fd79971dc391328a22ec6211925874` | |
| R10.0 `submission/` | `fefcedd079aaa9c2fd9d4abfd8bd0ba5f0c2a0ac` | |
| Integrated Final `src/` | `d5c37a7bb894454b23602a39664dfd26e7d8a2b8` | |
| `data/stage1/` | `5892f9a1d9e91af52d3a424eb5b440c5cf128363` | |
| `data/stage2/` | `7a1fd505e8383e52de3014131cbdbf34be733259` | |
| `evaluator` | `0a034561a54372e58b5598b6a94d31b91abe9570` | `142361d7ce18bc47dea6a07538db79a588b3afbf446526c1d1246f4968b3d0ca` |
| Team upstream `reports/` | `3dea5efbc30468dc460925cbb6f0a584b9ee23e9` | |
| Team `integration/data/matched/` | `e8a8beb795a5e025bd7d9489f5e9816848478488` | |
| Formal Report `data/` | `e25f272e82cc747e1e5ec1c13bb4a442aa24ceaa` | |
| Trial Log `data/` | `391c2174df6785a894644b89b947c683558e4218` | |

## Clean-room commands and results

Build and smoke tests used Ubuntu WSL2, GCC 13.3.0, Make 4.3, Python 3.12.3 and NumPy 1.26.4. Document and data checks used Python 3.13.5, NumPy 2.1.3, pandas 2.2.3, Matplotlib 3.10.0, PyMuPDF 2.1, pypdf 6.6.2, Poppler 26.11.0, TeX Live 2025 pdfTeX 1.40.28 and BibTeX 0.99d. Relative commands use the working directories shown in [Quick Start](QUICK_START.md).

| Command or entry point | Exit and result |
|---|---|
| `make -C Final_Submission_by_Zeyun_DU -j2 stage2 stage2-source` | 0. Cold native build and source ZIP. GCC reports the known `terms[4]` inlined sort warning. Source review bounds the populated range to four iterations. |
| `python3 -m zipfile -e ZIP OUT` and `g++ -O2 -std=c++17 OUT/synth_stage2.cpp -o SYNTH` | 0 each. Independent cold source-package build, including the shared-output example. |
| `python3 -m unittest discover -s tests -p 'test_*.py'` from the team archive | 0, 22/22 tests, including constant, memory, cut and cone fixtures. |
| J51 and R10.0 Make targets and checkers in Quick Start | 0. J51 exercised its sampled checker on Stage 1/001. R10.0 exercised all 131,072 assignments on Stage 2/001. |
| R10.0 `tools/verify_package.py` and `tests/test_cold_build.py` | 0 each. 52-file manifest and frozen parent/source checks. Cold standalone passed all 2,048 and 1,048,576 assignments on two fixtures. |
| `check_circuit.py`, `build/verify_exhaustive`, `evaluator` and `verify_all.py` | 0 on the focused runs below. Tested the documented evaluator flags and exact replay with a one-case bank. Read archived CSVs for both full banks. |
| `build_casewise.py --check`, Formal Report `verify.py`, integration `verify_evidence.py`, Trial Log `scripts/verify_evidence.py` | 0 each. Appendix byte check, report totals, 400 matched rows/100 netlist replays/200 RSS observations, and historical index and ablations. A checkout with automatic CRLF conversion failed raw input hashes. The Linux clone passed byte checks, and Quick Start now disables conversion at clone time. |
| `build_phase_c_figures.py --repeat N --out DIR` for `N=1,2` | 0 each, 54 outputs per repeat. Fifteen unaffected PDFs per repeat matched the baseline regeneration in text and rendered pixels. The three edited figures retain the same data. |
| `latexmk -pdf -interaction=nonstopmode -halt-on-error -outdir=DIR main.tex` in each document | 0 each from clean output directories. Formal Report exercised pdfLaTeX and BibTeX. Trial Log exercised three pdfLaTeX passes using its embedded bibliography. |
| Historical `scripts/build_document.py` and `latexmk` on an isolated tracked export | 0 each. Its 60 reassembled pages matched the canonical build in extracted text and rendered pixels. |

**Fresh smoke results only.** The native build passed the shared-output example (8 assignments, area 10, delay/target 5/5), Stage 1/001 (32,768, area 53,955, 73/77) and Stage 2/001 (131,072, area 1,768, 39/41) in both exhaustive checkers. The ZIP executable reproduced the shared-output result. The one-case evaluator run reproduced Stage 2/001 area and delay at 479.475 ms, with valid independent replay. The full benchmark suite was outside this audit. Historical measurements retain their original values.

## Independent data reconciliation

| Quantity | Repeat 1 | Repeat 2 |
|---|---:|---:|
| Integrated Final weighted area | 872,813 | 872,919 |
| R10.0 gross savings less penalty | 147,385 − 651 | 147,279 − 651 |
| R10.0 net savings | 146,734 | 146,628 |
| R10.0 area reduction, aggregate / median casewise | 14.392% / 13.187% | 14.382% / 13.187% |
| Integrated Final to R10.0 runtime, ratio of sums / median of pairs | 2.195 / 2.316 | 2.143 / 2.262 |
| Lower area and lower / equal / higher delay against R10.0 | 9 / 12 / 22 | 9 / 12 / 22 |

All four solvers reached 50/50 functional passes and timing targets in each matched repeat. J51, R10.0 and Integrated Final comprise the two-metric area/synthesis-time frontier in both repeats. The 22 joint area wins with higher delay still meet their individual targets. Direct memory was measured separately using GNU `time %M`. The six freeze-group banks combine 72 generated networks and twelve repeated control observations. The four validation banks yield 55/56 and the two post-freeze banks 28/28. The former four are labeled development in the later extended-window snapshot.

## Publication and change record

| Exact inspected PDF | Pages | SHA-256 |
|---|---:|---|
| [Formal Report](Stage%202%20Formal%20Report/main.pdf) | 14 | `d4033bb7ebf9f1a168247534b49aa26fcf2c464abe59ad9c65252acb361bf8b2` |
| [Unified Trial Log](Stage%202%20Formal%20Report/Research_Trial_Log/UFUG2106_Stage2_Research_Trial_Log_v3.pdf) | 60 | `0a6d67ae719c90f1763b9b494001752b8c267ff066411f3ddfca7f2fd0874b3f` |

The Formal Report contains 13 figures, 4 algorithms and 5 tables including the four bank/repeat appendix tables. The Trial Log contains 23 figures, its contents, two historical research appendices and seven bibliography entries. Every page was reviewed for readable labels and formulas, visible clipping or overlap, table alignment, contents, cross-references, pagination, column balance and appendix completeness.

- **P1, scientific clarity.** Corrected validation history and denominators, added joint area–delay outcomes, and aligned cut substitution and timing-repair pseudocode with their assumptions and source state. The new numerical assertions were checked independently against the original records.
- **P1, figure annotations.** Clarified the direction of change and case labels in the area–delay figure, removed the extra-Shannon marker from the extra-SOP factorial axis while retaining its result in the caption and text, and clarified the recovery heatmap's denominator and role encoding.
- **P1, publication.** Removed double numbering from five Trial Log headings and consolidated four duplicate bibliography entries. Six Stage 1 crops exposed 255–519 words to pypdf despite showing 29–52 chart words in Poppler. Reassembly removes surrounding source operators before embedding the vector crop. Both extractors now agree to within a word boundary. Four crops were pixel-equivalent at 125 dpi and two had at most 0.103% changed color-channel samples, with identical visible chart content. Trial Log float/longtable warnings and 0.116 pt alignment excess were reviewed without visible overflow. The Formal Report has no overfull box.
- **P1, reproduction.** Completed the Integrated Final workflow and corrected the Trial Log's stale two-pass instructions. Both banks use the same documented evaluator interface. The archived upstream notice keeps four original layout links for the handout, evaluator, ZIP and cases. The current workflow resolves the corresponding tracked handout, evaluator and case directory from the research root.

## Limits and release decision

Seed 711413/003 remains functionally valid at delay 28 against 27. Its archived witness reaches 27 and all six alternate searches remain at 28. Historical J51 timeouts and the upstream evaluator memory-control discrepancy remain part of the evidence. The two matched repeats describe the released inputs and chosen operating points, without iso-budget controls or a population-level inference. Cooperative time and memory checks do not establish hard limits. Official scores, hidden cases and actual Stage 2 submission status are unverified.

No unresolved scientific or build P0 was demonstrated. Team authorization covers public GitHub archiving of team contributions. The pinned upstream tree has no identified general redistribution license, and third-party rights for instructor assets, including the course handout, evaluator and released cases, remain unconfirmed. The main-branch release and tag await the repository owner's approval of the publication scope. [Pinned upstream commit](https://github.com/zdu881/UFUG2106-Project/commit/59e33505616d127fc06a63580ca3ae3c34d1da72) · [Course-material notice](Final_Submission_by_Zeyun_DU/official/README.md)

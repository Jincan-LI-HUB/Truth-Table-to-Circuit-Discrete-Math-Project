# Manuscript Review — Round 6: Final Editorial and Submission-Readiness Review

**Baseline:** Draft v0.7 (provenance-audited).  **Revised draft:** v0.8.  **Date:** 12 November 2026.

## Scope of review

This is a presentation and readability pass, **not** a new synthesis experiment. The original 25-case metrics, paired measurements, cut-budget studies, frozen Round 5.1 source, mathematical proofs, figures and raw evidence remain unchanged. P0 (individual contributions, final AI-use disclosure and the actual submitted Canvas source) is intentionally deferred by the authors' instruction.

## Findings resolved

| ID | Finding in v0.7 | Revision and why it matters | Status |
|---|---|---|---|
| E1 | Two paragraphs explaining Typed DAG's actual coverage and the decision to freeze Round 5.1 appeared beneath the **Round 6 exploration** section. | Moved both to **A More Efficient Synthesis Engine**, immediately after the implemented Round 5.1 overview. This restores the argument's order: method, scope, selection, next experiment. | Resolved |
| E2 | The Abstract summarized the same research progression as the Introduction and did not immediately foreground the measured paired comparison. | Rewrote a concise result-led Abstract, retaining exact figures and limitations. | Resolved |
| E3 | Cut-rewriting section opened twice with nearly the same question. | Removed duplicated framing; retained the cut definition, exact truth-mask construction, sharing caveat and ablation evidence intact. | Resolved |
| E4 | Pseudocode's candidate-update condition lacked visible logical grouping. | Added parentheses around incumbent absence OR strict rank improvement. The intended predicate is unchanged. | Resolved |
| E5 | Final discussion repeated the complete R4.1/R5.1 comparison and caveats already covered in the methods. | Condensed the decision summary, retaining the **104 area units**, non-paired R4.1 comparison caveat, runtime-criterion violation and unknown official score. | Resolved |
| E6 | The last double-column page had uneven column heights just before the one-column appendix. | Used the standard LaTeX `balance` mechanism for the final discussion page. The full 25-case table remains readable in the one-column appendix. | Resolved |
| E7 | The Trial Log contents extended to a mostly empty second TOC page and did not give a fast route for first-time readers. | One-page major-section TOC plus two reading paths (conceptual vs. engineering). All subsection headings still appear in the text and PDF search. | Resolved |
| E8 | Notation needed for the Trial Log was scattered across sections. | Added a compact symbol table distinguishing Boolean function, gate DAG, area, circuit delay, synthesis runtime, node timing, and heuristic rank. | Resolved |
| E9 | The Trial Log closing reflection repeated some of the introductory development narrative. | Tightened it around the conceptual change of objects: function, BDD, gate DAG, timed DAG, and synthesis program. | Resolved |
| E10 | Hyperlinks inherited a saturated default blue from the homework template. | Used a darker readable link color derived from the supplied `#92B3CD` palette. No palette asset itself was changed. | Resolved |

## Independent checks performed

- LaTeX: IEEEtran and the homework-derived Trial Log both compiled successfully (`latexmk -pdf -halt-on-error`), with references and citations resolved in the **final** logs.
- Pages: **11** for Technical Report, **20** for Trial Log. Both PDFs were rendered and checked at page level, including the last two-column report page, the long official-results table and the new Trial Log TOC.
- Frozen shared assets: **52 files** under `shared/data`, `shared/scripts`, `shared/figures`, `shared/evidence`, and `shared/bibliography` were byte-identical to v0.7.
- Bundled provenance audit: **18/18** checks passed. No full official evaluator rerun was performed.
- Independent worked-example and deep-exposition checks: passed (including all eight truth rows, SOP/POS, influences, `0xCE` cut mask, timing calculations).
- Typed DAG randomized regression: **2,000 DAGs, 8,000 transforms**, all passed; these tests are not formal proofs or official evaluator reruns.
- Figure recreation: the Python script regenerated figures from the included CSVs into a separate working directory. Exported PDF bytes may differ because of renderer metadata; underlying shared input data was unchanged.

## Remaining submission gates (not silently resolved)

1. **P0 remains open:** verify individual contribution attribution and precise AI-assisted work disclosure against the actual course policy.
2. **Submission version:** Stage 1 Round 5.1 is the frozen research candidate, not automatically the code uploaded to Canvas. The authors must identify and freeze the actual submitted ZIP.
3. **Course restrictions:** verify permission before publishing instructor-provided truth tables/evaluator; they are not bundled here.
4. **No published numerical grade formula:** the manuscript compares area, timing, and runtime separately; no official score or hidden-case guarantee is claimed.
5. **Stage 2 is separate:** do not retrofit future results into this Stage 1 history.

## Editorial decision

**Proceed to author review, not automatic final submission.** The manuscript has reached a stable structure, with the main technical argument and source-provenance audit unchanged; the remaining tasks concern author-confirmed provenance, policy, and final submission details rather than further algorithm parameter tuning.

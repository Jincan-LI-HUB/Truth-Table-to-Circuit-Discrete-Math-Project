# Phase 0–2 Completion Audit — 23 November 2026

**Status: usable technical baseline, with an explicit candidate/integration gate still open.** This work does not assert that the final team source has been submitted or that all source branches have been formally verified.

| Gate | Assessment | Evidence |
|---|---|---|
| Assignment contract captured | Verified | `REQUIREMENTS_MATRIX.md`, specification source PDF |
| Exact actually submitted Stage 1 code identified | Verified | Zeyun submitted original RAR extraction; code SHA and independent build |
| Exact R10.0 research candidate identified | Verified | R10 source, 12 headers, source SHA, feedback ZIP embedded matching source |
| Exact team-integrated final Stage 2 source | **Open** | Frozen R10 README explicitly disclaims integration status |
| Primary evidence archive data integrity | Verified | 26/26 SHA-256 checks from original `MANIFEST.json` |
| R10 original official feedback re-aggregation | Verified | Stage1/Stage2 25×2 cases and totals, `R100_FEEDBACK_RECOUNT.csv` |
| Historical 50-case three-method comparison available | Verified as existing batch, not newly rerun | 300-row `matched_case_metrics.csv`, distinct WSL environment |
| Independent local functional smoke | Verified on its finite fixtures | 20/20 complete-table local checks; 18-input affine full 262,144-row simulator check |
| Actual default source-path reverse engineering | Completed with exact line references | `FINAL_SOLVER_SPEC.md` |
| Core mathematical reasoning | Proved subject to stated invariants | `MATHEMATICAL_VERIFICATION.md` |
| Formal implementation correctness over every input | Not established | Requires code review/verification beyond current examples |
| Hard runtime/RAM guarantee | Not established and not claimed | Source intentionally uses heuristic admission and conservative RAM estimates |

## Key fact reconciliations

- **R8.6 extra-SOP** is the upstream default; **R9.1 repeat-SOP** is the additional R10.0 default pass. Other R8 branches are mostly historical/ablation-selectable options, not successive unconditional stages.
- **Strict full-network area decrease** is the admission rule for R10.0's additional pass; R8.6's area policy can also accept same-area, smaller-delay candidates.
- Candidate `Graph::metric()` counts the entire stored node table; the graph builder prunes unused gates. The actual submission file charges all listed gates as per the assignment.
- One complete truth table checked at cut frontier proves local functional equivalence, not timing, acyclicity, area, correctness of all C++ paths or optimality.
- Team-submitted Zeyun Stage 1 and Jincan independent Stage 1 R5.1 are separate comparators with different study roles.
- This work creates no LaTeX paper draft or figure; the unchanged `palette.json` is retained for later scientific visualization.

## Research next gate (after validating this technical dossier)

Perform a source-to-source method-improvement comparison anchored in the **submitted Zeyun Stage 1** and **current frozen R10 candidate**, while retaining the independent R5.1/R6 line as material historical contribution. Then move to exact 50-case paired comparisons, targeted ablation/negative evidence, figure/storyboard specification, and only then the manuscript. All report contents must answer `Final_Project.pdf` with the final solution as the focus.

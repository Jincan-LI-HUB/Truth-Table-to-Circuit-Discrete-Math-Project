# Manuscript Review Resolution — Draft v0.3 (P1/P2)

## P0 explicitly deferred
Author contributions and AI disclosure remain placeholders; do not treat this draft as ready for submission.

## P1
- P1-1: Replaced a misleading per-candidate postprocessing pseudocode with a version matching source `synth_round51.cpp` (portfolio, legacy fallback, final algebra/phase alternatives). This is a manuscript-control-flow defect; it does not establish that running phase optimization per candidate is better or worse.
- P1-2: The provided evaluator is a Linux x86 command-line binary. Its `--help` exposes runtime and RAM caps, but not a numerical grade formula; the project brief describes only directional preferences. Formalized the *internal* lexicographic rank, explicitly not an official score.
- P1-3: Restated the required-time proposition with fixed external cone boundaries, unchanged dependencies, arrival bounds at replacement roots, and a topological proof. Distinguishes sufficient timing condition from whole-network validation.
- P1-4: Stated the optional ninth-line RAM limit is not explicitly parsed by the frozen main; no source modification.

## P2
1. Documented R5.1 vs R4.1 Strict selection as an efficiency/reproducibility choice, not a minimum-area or score-optimality theorem.
2. Limited typed-DAG claims to per-candidate balancing/recovery.
3. Added a fully enumerated 3-input/2-output example with concrete topological gate IDs, cost, timing, and absorption alternative.
4. Added an original TikZ cofactor-sharing diagram in the Technical Report.
5. Clarified exponential truth-table input bound and heuristic worst-case limitations.
6. Preserved archived run labels and empirical dataset distinctions.
7. Retained IEEE double-column and rich single-column document styles; neither draft is a final submission.

## Evaluation binary caveat
`evaluator --help` only documents options and output paths; no scoring equation was exposed. We do not claim to have audited its internal compiled algorithm.

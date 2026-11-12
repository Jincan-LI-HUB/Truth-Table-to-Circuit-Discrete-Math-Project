# Draft v0.5 → v0.6

**Nature:** A substantial explanatory/academic revision, not a new synthesis experiment.

## Technical Report
- Explained how Shannon nodes lower to the legal gate library, distinguishing canonical ROBDDs from minimum-area mapped circuits.
- Added functional-versus-syntactic sharing and a counterexample to treating influence as an optimal-order predictor.
- Added a pointwise correctness argument for SOP/POS covering.
- Formalized the output-reachable gate set and exact global area difference.
- Strengthened the Round 6 cut argument with an explicit k-feasible boundary, 3-input `0xCE` mask, correlation caveat and non-cyclicity requirement.
- Added a conditional Typed DAG preservation proposition with a topological induction proof.
- Preserved Round 5.1's frozen ranking, full benchmark table and all existing empirical evidence.

## Trial Log
- Added a four-level conceptual map: truth table → BDD → charged gate DAG → executing synthesizer.
- Extended the running example across more rounds, with actual cofactor tables, influence fractions, SOP/POS, XOR cofactor algebra, changing Required Time and Cut masks.
- Added the precise assumptions underlying the Boolean cache, hash-consed typed builder and Pareto comparisons.
- Preserved unsuccessful trials and timing variability rather than smoothing them away.

## Quality assurance
- The new example's 8-row truth table and derived values are checked by `shared/scripts/verify_deep_exposition.py`.
- All 34 archived input datasets and empirical PDF figures match v0.5 SHA-256 exactly.
- Both PDFs compiled using the supplied LaTeX sources; no Overfull hbox or undefined-reference errors observed.
- P0 deliberately untouched as requested.

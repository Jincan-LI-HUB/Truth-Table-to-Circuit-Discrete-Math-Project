# Round 8.7 Release Notes

1. **Purpose:** independent generalization/robustness validation, not parameter tuning.
2. **Frozen code:** embedded exact R8.6 and R8.5 source snapshots. No algorithm changes.
3. **Frozen bank:** 36 new independently generated circuit-function cases, 216 local paired checks in two runs; 216/216 exhaustively correct and target-met locally. Cross-run 108/108 identical netlist SHA-256 pairs.
4. **Strong caveat:** all three policies gave identical Area/Delay on this bank; it does not discriminate their optimization quality. Need harder untouched Stage 9 validation and official public pairings.
5. **Adversarial runtime:** independent 100-ms stress bank, with two n20 cases locally above 100 ms; genuine evaluator results pending WSL. It is NOT included in the main success rate.
6. **Invalid preliminary stress:** a discarded earlier stress generator accidentally overwrote Target Delay instead of Runtime Limit. It is excluded; provenance noted in `evidence/invalid_stress_v1/`. Only corrected, manifest-verified `stress_v2/` is used.
7. **Official status:** Round 8.7 course evaluator not present in the creation environment. Original Stage 1/2 grading verification must be run in your WSL.
8. **Exit discipline:** feedback ZIP on success or failure, no claim of hidden grader performance.

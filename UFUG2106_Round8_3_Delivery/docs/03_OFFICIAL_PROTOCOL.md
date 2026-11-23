# Round 8.3 — WSL Official Acceptance Protocol

## Gates

1. Verify full frozen source SHA-256 manifest and compiler build (`g++ -O2 -std=c++17 -DNDEBUG`). Do not override the shipped parent snapshot. Keep both original and R83 executables.
2. Strategy isolation: conflicting R8/R81/R82 environment settings must not change R83 output.
3. Real course truth-table preflight (up to 5 Stage2 cases, bit-parallel **exhaustive**, including `case_016`, `case_017`); all must match and meet Target Delay.
4. Official evaluator 2 runs on Stage1 and Stage2; reverse the variant order in the second run. Each configuration must pass **all 50 public cases** with target met.
5. Store every official CSV, evaluator stdout/stderr log, program SHA256, per-case area/delay and runtime, and pairwise comparison against the frozen R8.2.1 Dual reference.
6. Compare repeated-run digest variation and root cutoff counts before choosing a final default. A cut watchdog hit is not automatically an invalid circuit, but may indicate limited stability.

## Variants

- R8.2.1 Fast Area (frozen).
- R8.2.1 Dual Area (frozen).
- R8.3 Fast Area (Shannon only).
- R8.3 Stable Dual Area (default 900/600 roots).
- R8.3 Stable Dual ADP (same deterministic quota, ADP acceptance).
- R8.3 Dense Dual Area (1100-root, *potential* timeout variability).

Because the exact grading formula is not verified here, final comparisons report 4 axes: boolean correctness, Area, Delay, Runtime, plus raw timeout and target statuses; one aggregate alone is not sufficient.

## Expected output of `run_round83.sh`

Success or failure produces a single `feedback/Round8.3_Feedback_<timestamp>.zip` automatically, containing all run logs, official output, frozen source, audit docs and evidence. Missing real evaluator terminates with a **nonzero exit status** and no fabricated PASS. A `--quick` option runs 1 paired round with 3 variants.

## Scope of Issue #2

The low-RAM code from R8.2.1 is inherited, but the evaluator's `MEMORY_LIMIT` classification for a minimal C and a patched C++ program with very low current RSS has not been reconciled with official teaching staff. Round8.3 does not claim to fix that unresolved evaluator incompatibility. Do not close the teammate's GitHub Issue #2 based only on public Stage1/2 passes.

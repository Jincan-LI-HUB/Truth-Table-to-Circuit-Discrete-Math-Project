# Change Log

## Round 7 — Exact Cover Acceleration (initial milestone package)

- Preserved immutable Round 5.1 original source via hash-checked offline bootstrap.
- Replaced quadratic prime implicant pair scan with exact hash-neighbor enumeration.
- Replaced greedy-cover repeated minterm scans with exact packed-bitset `popcount` gains.
- Added independent legacy switches for causal ablation and cover-stage profiling.
- Included unchanged Stage 1 and Stage 2 Round 5.1 CSV baselines.
- Added 10,656-comparison kernel A/B test, focused `case_016` kernel benchmark, and paired 50-case evaluator runner.
- Deferred portfolio time-budget policy changes to a separately measured experiment; no case-specific thresholds.
- Official 50-case full-solver regression is **pending user's WSL execution**.

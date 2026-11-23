# Round 7.2 Changelog & Audit Trail

## 2026-11-21 — Round 7.2 initial research delivery

**Immutable upstream basis:** frozen R5.1 Git blob `68ec9f54b27081641ac10358f81eef260acfcbdb`. Generation chain: `bootstrap_round7.patch` (Cover kernel) → `bootstrap_round71.patch71` (short-budget guard) → `bootstrap_round72.patch72` (quality-recovery shortlist). The Makefile and shell script do not modify Round 5.1 or Round 7.1 files.

### Source modifications (relative to generated R7.1)

1. Extend `legacy::run_synth` with **optional** cooperative `steady_clock` deadline. Existing callers without a deadline retain unlimited mode; checks inserted in legacy input parsing, variable-order permutation, BDD construction, gate creation and ROBDD recursion.
2. Add `UFUG_R72_POLICY` values `shortlist` (default), `guard`, and `shortlist_nocancel` (research ablation).
3. Add a *single* pre-registered cheap-first candidate (`influence-desc`, `cubemode=0`) before the R7.1 short-budget skip-all-legacy guard, admitted under `n<=10`, `100<=limit<=250`, valid on-target incumbent, and elapsed `<35%` of budget.
4. Cancel the supplementary candidate near `60%` of budget cooperatively; do not begin its DAG recovery if elapsed >=`65%`.
5. Preserve original R5.1/R7.1 candidate metric, rank and final algebraic/phase postprocessor. Only accept a fully parsed valid candidate if strictly better.
6. Add `R72_TRACE` (via `UFUG_R71_TRACE=1`) for per-trial choice, candidate utility and cancellation reason.

### New experimental infrastructure

- Full two-stage, same-host paired evaluator with reversed order and all 5 baseline/ablation configurations, default two runs.
- Source/Git-blob hashing and compiled executable fingerprints.
- Independent critical case verifier (all 256/512 truth-table assignments), R7 exact Cover A/B tests (10,656 comparisons).
- Independent high-n sampled regression checker; exported local smoke CSV and verification CSV.
- `profile_critical.py` prints and saves candidate-level logs, independent verification results and circuit SHA-256 for two structural probes; direct timing explicitly separated from official evaluator results.
- `export_feedback.py` always packages official CSVs, logs, generated source, research docs, and fingerprints. The bash exit trap also operates when the release gate fails or compilation stops.
- Paired analysis avoids incomplete Area Sum misinterpretation, separates feasibility and QoR gates, reports casewise changes.

### Observed preflight results

- R7.2 C++ source compiles with `g++ -O2 -std=c++17 -DNDEBUG` on container Linux.
- Stage1 case020: Guard 777/32 → R7.2 Shortlist 766/30, 256/256 exhaustive.
- Stage2 case016: Guard 1781/36 → R7.2 Shortlist 1781/36, 512/512 exhaustive.
- 25/25 Stage2 local direct cases produced valid netlists, all same weighted area/delay as local guarded R7.1; 15 exhaustive and 10 sampled independent functional checks.
- **No R7.2 official target-host results yet.** No claim of hard runtime guarantees.

### Known limitations

Cooperative checkpoints cannot preempt arbitrary library calls or all downstream processing; one cheap candidate is not a trained utility model; additional search time can still worsen a borderline case; public 50-case tests cannot establish hidden-case generalization. The original course scoring formula is not provided.

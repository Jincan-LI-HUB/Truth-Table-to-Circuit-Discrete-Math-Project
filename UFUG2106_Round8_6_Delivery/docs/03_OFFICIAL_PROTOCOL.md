# Round 8.4 — Official Paired Evaluation Protocol

## Experimental controls

Freeze source parent from `SOURCE_MANIFEST.json` and compile C++17 with `-O2 -DNDEBUG` on WSL. Use **unmodified** provided `data/stage1`, `data/stage2`, and the genuine `./evaluator`. Do not claim that local exhaustive checks demonstrate official time or RAM compliance.

`run_round84.sh` runs source-manifest verification, independent critical-case truth-table verification, strategy isolation, and the genuine evaluator with **two runs**, reversing configuration order in Run 2.

The variants are the frozen Round 8.2.1 Dual Area, frozen Round 8.3 Stable/Dense, R8.4 Topology, Top-Q, Top-Q Dense, Mixed33, Mixed66, Adaptive, and Top-Q ADP. Each stage contains 25 cases. The total normally includes 10 configurations × 2 runs × 2 banks × 25 = 1,000 official case evaluations. The runner checks 25/25 PASS and 25/25 Target Met before advancing. Positive-RAM official tests remain **separate and unresolved**.

To reduce cost, `--quick` performs one run and four configurations; this cannot establish full two-run stability. All logs/reports/inputs used by local preflights, source and SHA hashes are bundled in the feedback ZIP even if a stage or evaluator call fails.

## Decision criteria

(1) Correctness, output validity, Target Delay, and all stated time limits must hold. (2) Compare Area by paired cases, not only aggregate sum. (3) Compare Delay and Area×Delay as sensitivity metrics; the precise official scoring scalar must not be invented. (4) Compare runtime geometric means and per-case failure tails. (5) Check whether output reproducibility holds across two runs. (6) Preserve negative results of Top-Q instead of silently changing defaults.

## Timing caveats

The quota only bounds selected roots; a single cut/BDD operation may take varying time and the emergency wall guard remains. The Stage 1 public data have not been compiled/tested in the current container. Do not merge or recommend an experimental policy as final submission based only on Stage 2.

## Error handling

The official evaluation script rejects any missing or non-25-row CSV; rejects any non-PASS, non-Target case; and writes partial `summary.json`. Bash EXIT trap always invokes `tools/export_feedback.py`, preserving partial results. On fake/missing evaluator, do **not** claim official PASS. No data or evaluator is bundled in this ZIP.

## Specific replication question after local results

The correct Top-Q vs mixed66 experiments are deliberately separate. In particular, Mixed66's original Stage 2 total of 499,035 was not stable for case_005 across repeated trials: repeat Area 106,806 / 109,218 / 106,771 (all equivalent and timing-feasible). Compare each official run's case_005 explicitly and report wall-hit signatures; a good aggregate on one run cannot stand in for a reproducibility guarantee.

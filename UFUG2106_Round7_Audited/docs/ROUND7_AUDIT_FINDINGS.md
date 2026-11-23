# Round 7 — Independent Postmortem (2026-11-21)

## Primary evidence

- User-provided `20261121_135745.rar`, containing official evaluator CSV and logs, with `summary.json` binary / evaluator hashes.
- First Round 7 package's `bootstrap_round7.py`, `run_round7.sh`, `tools/run_benchmarks.py`, and unit tests.
- Frozen Round 5.1 main loop and `shared_covers` source from GitHub.

## Findings

1. **Different binaries, same observed quality.** Stage 1 Area=529014 for both programs in both paired runs. Stage 2 all 24 jointly accepted cases have exactly equal area and delay. This is consistent with Round 7 only changing exact computational kernels, not the synthesis objective. Netlist identity has *not* been established.
2. **Release gate fails.** Stage 2 `case_016` fails in both Round 7 runs. The first Round 5.1 paired run passed that case, while its second run failed. Its passing time was 98.409ms, only 1.591ms of slack below the official runtime limit.
3. **No official ablation was actually run.** `--ablate` was optional in the original one-shot script; only two Round 7 configurations are represented in the user's original summary: `default` and the Round 5.1 control. The core A/B unit tests did not emit CSV files.
4. **The original runner used exit status 0 for release failure** since the evaluator driver only printed a failure notice. The audited runner sets status 2, preserving all reports.
5. **Source-level budget weakness.** The outer trial scheduler checks a 75%-of-limit threshold only *before* starting a candidate, and initial `run_synth` calls use no per-candidate deadline. This can make an isolated kernel acceleration fail to reduce overall wall time. Actual causal attribution for `case_016` needs direct candidate tracing/ablation results.
6. **Instrumentation overhead confounder.** Original Round 7 increments counters and executes small clock measurements even with profiling disabled. Before making quality claims from timing, production profiling should be gated and repeated trials conducted under same conditions.

## Proposed controlled next steps

A. Run all four Round 7 configurations alongside the frozen Round 5.1 in both stages. Record per-case PASS, area, delay and runtime in independent CSVs, in alternating order.

B. Independently profile `case_016`: BDD time, cover generation `merge_ms`, `greedy_ms`, mapping, and `trial_total index` / selected candidate. The direct run is diagnostic, not official.

C. Depending on trace, implement a **separate**, instrumented budget-aware candidate scheduler, with candidate-level ceilings and an incumbent-return path. Treat it as a third Round 7 ablation rather than silently combining it with the exact-cover changes.

D. Only after 50/50 pass in repeated official evaluation should larger representation and rewrites be evaluated (Round 8).

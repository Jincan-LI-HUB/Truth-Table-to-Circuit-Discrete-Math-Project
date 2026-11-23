# Changelog

## Round 7.1 — 2026-11-21

**Base:** Frozen Round 5.1 source; deterministic reapplication of Round 7 exact Cover optimization.

### Added / changed

- Short-budget \(L\le250\) ms incumbent-aware legacy dispatch guard.
- Short-budget \(0.72L\) primary/postprocessor dispatch reserve, beginning time measurement before the first input parse.
- Cooperative absolute deadline on *secondary* primary candidates in tight budgets where supported by old `run_synth`.
- Detailed optional R71_TRACE on each primary/legacy candidate, skip reasons, and final wall elapsed.
- `UFUG_R71_POLICY=off` switch to restore the old R7 dispatch for causal ablation.
- Full automatic paired Stage 1/2 × variant × repetition evaluator results.
- Direct case_016 profiling with verification + source fingerprints.
- Automatic feedback ZIP upon success, release-gate failure, compile failure, or exception.
- Source-derived experimental motivation, mathematical design, and paper notes.

### Deliberate nonchanges

- No change to Boolean function semantics, cover tie-breaking, mapping formulas, netlist output grammar, or candidate rank.
- Long-budget candidate ordering and dispatch thresholds mostly retained to limit Stage 1 regressions.
- No case-number-specific `if (case_016)` logic.
- No claim that Round 7.1 is already 50/50 PASS or strictly deadline-safe.

### Risks requiring official measurement

- Skipped legacy candidates may worsen area/delay on short-budget cases.
- A first candidate or a non-interruptible postprocessor can still overrun the evaluator deadline.
- The `policy=off` ablation still starts the clock earlier (before parse); this tiny timing-origin difference precludes bit-identical scheduling under every host condition.

# Round 8.7 — Experimental Protocol

## Hypothesis and source integrity

Hold the base logic-synthesis implementation constant, comparing only the frozen R8.6 `baseline`, R8.6 `extra_sop`, and R8.5 `budget_reclaim`. Hypothesis: the additional SOP root quota improves the public cases without creating correctness or tail-risk regressions on newly generated, untouched Boolean functions.

Frozen source hashes (from R8.6 prior to the R8.7 experiment):
- `src/synth_round86.cpp`: `6d21a7d3cf80a8662f4f42a965e84c50d6cffcef7766a4d2dccf282c204078d8`.
- `src/synth_round85_frozen.cpp`: `fa0421e3fbb9d1058a3b389e00ba57c85e9ca0cf44e7f5cd2e4428545bb7d969`.

The new synthetic bank uses seed `2026112287`, with per-case seed `2026112287*1000 + case_index`. The generator makes its *own* bit-vector truth tables with independent Boolean operations (`AND`, `OR`, `XOR`, `NOT`, `MUX`, majority-like networks, sparse DNF, and shared DAGs). The circuit generating the truth table is not given to the synthesizer. All file hashes are recorded before running the comparators. No case was dropped after seeing algorithm results.

## Verifier and metrics

For every output netlist, `tests/verify_exhaustive.cpp` checks every `2^n` truth-table row via bit-parallel simulation; its independent graph parser also checks gate references, valid structure and costs. Extract from independent verifier: Area, Delay, Target Met. Record synthesis exit code, process elapsed wall time, `/usr/bin/time` maximum RSS where installed, optional Cut Search wall-hit logs, and netlist SHA-256. The `run_holdouts.py` script deliberately records failures (not only PASS).

Two runs reverse policy order on each case. Compare:
- `Area`, `Delay`, and `Target Met`;
- `median` and `p95` of process wall time, ratio to the input runtime limit;
- Peak RSS and its scaling with `n`, `m`;
- exact repeats by Area/Delay and by output netlist SHA-256;
- worst-case FAIL and timeouts, not only averages.

**Decision rule:** no unverified correctness regression; no consistent new performance advantage can be claimed unless demonstrated on a separate untouched test distribution. Keep candidate fallback for Round 9 and final integration.

## Sampling limitations

The synthetic families focus on interpretable Boolean functions and broad input/output sizes. They are not probability samples from the course hidden distribution. The 36 cases are quite easy for the pre-cut synthesizer, which explains why all policies generated the same Area/Delay. This is a *non-discriminative negative result* for the Area-gain hypothesis, and the honest next step is to test new algorithms against an additional untouched challenging bank, **not** to tune on this frozen one.

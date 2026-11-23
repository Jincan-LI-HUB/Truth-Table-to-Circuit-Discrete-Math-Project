# Round 8.7 — Local Outcomes (as of 2026-11-22)

Independent local host, NOT the course evaluator and NOT the grader. The complete CSV and machine-readable summary are in `evidence/`.

| Policy | Exact | Target met | Runtime within generated limit | Run1/2 Area&Delay | Run1/2 Netlist SHA | Peak RSS (KiB) |
|---|---:|---:|---:|---:|---:|---:|
| R8.6 baseline | 72/72 | 72/72 | 72/72 | 36/36 | 36/36 | 36,292 |
| R8.6 extra_sop | 72/72 | 72/72 | 72/72 | 36/36 | 36/36 | 36,288 |
| R8.5 budget_reclaim | 72/72 | 72/72 | 72/72 | 36/36 | 36/36 | 36,332 |

**All 36 cases have equal Area and Delay across all three policies.** This supports a no-regression observation, but does not support a hidden-case quality advantage. There were zero logged Cut Search wall-hit events in this bank. Thus most cases appear not to exercise the complex late Cut Rewrite search responsible for public-case optimization gains.

The three strategies' local `median` synthesis wall time across both runs was approximately 35.7 ms, 34.6 ms, and 31.3 ms, respectively. These times include the supervisor's process-start overhead, so small ratio differences are not reliable optimization gains.

Adversarial input bank (`stress_v2`) retains original Boolean function and target delay 170, changing only `runtime_limit=100`. In the local environment, `n=20` direct/wire costs ~125–129 ms and `n=20` parity ~120–124 ms; an `n=18` sparse input was ~41–42 ms. All six circuits are functionally correct; the first four trials **exceed 100 ms locally**. Their official status is unknown until a separate run of the genuine course evaluator.

A preliminary stress input generator mistakenly changed the target rather than the runtime limit. Those measurements were invalidated, excluded from all comparisons, and the generator was corrected to assert both fields and SHA-256. Metadata from the invalid trial is archived under `evidence/invalid_stress_v1/` for research integrity.

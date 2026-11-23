# R9.0: Risk register and official acceptance

| Item | Gate | State before WSL |
|---|---|---|
| No-env Extra SOP | No flags, fingerprint and correctness on synthetic cases | Locally testable |
| Spec-conforming input | 39 normalized original-vs-canonical pairs preserve every token | Locally testable |
| Source-only build | `submission` folder compiled in new isolated directory | Locally testable |
| Short-limit large `n` | Genuine official evaluator on 3 adversarial `100 ms` cases | **Unknown**; do not claim PASS |
| Public functional regression | Genuine evaluator on all 50 cases, four variants, two runs | **Unknown** pending WSL |
| Hidden grading tests | 50 hidden cases as specified by TA | **Unavailable** |
| Integrated BDD budget | Team's separate Stage2 integration | **Open** |
| RAM positive limits | TA says no final test uses them | Non-scoring research only |

**Key nuance:** Even a correctly constructed output is invalid if a positive runtime limit is exceeded. The new short-limit bypass reduces redundant work but the input file must still be read in full, so it cannot promise a 100-ms pass on the grader.

Reported metrics: each case's correctness, area, delay, runtime, exit code, memory where available, emitted-netlist hash, and evaluator original logs. Compare no-env candidate against explicit Extra SOP (same source) and against frozen R8.6 Extra SOP; runtime-sensitive cases can differ by execution jitter. Compare at fixed budget and preserve negative results.

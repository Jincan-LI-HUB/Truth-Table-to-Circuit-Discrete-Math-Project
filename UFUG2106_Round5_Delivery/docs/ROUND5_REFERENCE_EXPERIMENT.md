# Round 5 — Reference Experiment (Container, 11 November 2026)

> These numbers come from the current container, **not** from the user's Windows 11 / WSL2 machine. The local reproduction script will create new, paired evidence. This is a performance-engineering round, not a new Boolean representation or proof of optimal hardware Area.

## 1. Frozen comparison

- Baseline: `src/synth_balanced.cpp`, Round 4.1 Balanced, compiled with `g++ -O2 -std=c++17`.
- New program: `src/synth_round5.cpp`, same flags plus `-DROUND5_CACHE=1`.
- Gate set: AND2 / OR2 / NOT; test set: the same 25 teacher-provided Stage 1 files; instrument: teacher-provided Linux evaluator.
- Historic Round 4.1 user WSL runs had median runtimes 96.048 ms and 102.615 ms. They are not directly paired with the container numbers below.

## 2. Stage-by-stage ablation (separate measurements)

| Variant | Area sum | PASS | Target met | Median runtime (ms) |
|---|---:|---:|---:|---:|
| Round 4.1 Balanced reference CSV | 529,014 | 25/25 | 25/25 | 131.907 |
| BDD graph + affine mask cache | 529,014 | 25/25 | 25/25 | 136.080 |
| Plus duplicate candidate elimination | 529,014 | 25/25 | 25/25 | 137.820 |
| Plus symbolic implicant cover caching | 529,014 | 25/25 | 25/25 | 125.590 |
| Plus fast Area/Delay Netlist parser | **529,014** | **25/25** | **25/25** | **95.662** |

The cache-only runs do **not** demonstrate a speed gain in isolation. Mapping and candidate post-processing dominate; measurements also vary with CPU load. All recorded reference values are included under `results/`.

## 3. Same-environment interleaved comparisons

Another run in the same container gave:

| Program | Area sum | Target met | Median (ms) | Sum of case runtime (ms) |
|---|---:|---:|---:|---:|
| Frozen Round 4.1 (`benchmark_ref_a.csv`) | 529,014 | 25/25 | 126.438 | 12,831.27 |
| Round 5 (`benchmark_new_retry.csv`) | 529,014 | 25/25 | **90.935** | **9,107.58** |

The observed median runtime reduction for these two runs was about **28.1%**. A separate complete Round 5 run measured 95.662 ms (about 24.3% below the 126.438 ms reference). Timing is empirical, not deterministic. A planned multi-run interleaving was interrupted; no results from the incomplete run are used as a full 25-case comparison.

Illustrative paired samples:

| Case | Frozen Round 4.1 (ms) | Round 5 (ms) | Reduction |
|---|---:|---:|---:|
| 001 | 1,277.09 | 816.28 | 36.1% |
| 007 | 1,503.93 | 1,062.59 | 29.3% |
| 015 | 850.32 | 612.24 | 28.0% |
| 024 | 3,855.00 | 2,853.77 | 26.0% |
| 025 | 1,752.20 | 1,197.79 | 31.6% |

## 4. Correctness checks

- 25/25 official `PASS`, 25/25 targets met; Area sum **529,014**.
- In one run, **25/25 emitted Netlists byte-identical** to the user's second WSL Round 4.1 Balanced run (`20261111_121216_Round4.1_local_results.zip`), not just metric-equivalent.
- Independent verifier: 25/25 files valid; 13 small cases exhaustive, 12 larger cases deterministic sampled; independent Area and Delay checked against official results.
- Additional generated Truth Tables: **110/110 official PASS**, **96/110 target met** (the target values were synthetic and are not official Stage 1 targets).
- Two structured stress cases: 2/2 `PASS`, both targets met; including an \(n=20,m=8\) case.

## 5. Limitations

1. Performance numbers are collected from a single Linux container and are not an official grade.
2. The 25 official cases were already used to guide previous algorithm development; the 110 generated cases provide additional correctness evidence but do not establish hidden-case optimality.
3. Current BDD caching uses bounded retention (at most 80,000 nodes, \(n\le18\)), not a universal multi-order memoization system.
4. `Fast stats` is only used on internally generated Netlists; the teacher's independent evaluator is still authoritative for submitted output.
5. Strict per-case runtime and memory limits on arbitrary hidden inputs remain difficult; the local WSL run should be performed before freezing a final version.

**Additional end-to-end workflow observation:** a separate container run using the exact local reproduction script produced a different but valid result for `case_022` (frozen Round 4.1: Area 1,334, Delay 32; Round 5: Area 1,320, Delay 31). Both achieved 25/25 PASS and 25/25 Target Delay. The difference reflects wall-clock search truncation and is retained as evidence, not discarded.

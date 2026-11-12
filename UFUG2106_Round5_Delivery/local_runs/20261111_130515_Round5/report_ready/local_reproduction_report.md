# Round 5 — Local Reproduction Results

> Local results, not historical/container results. Both executables were compiled in this run.

| Metric | Frozen Round 4.1 Balanced | Round 5 |
|---|---:|---:|
| Official PASS | 25 | 25 |
| Target Delay Met | 25 | 25 |
| Area sum | 529014 | 529014 |
| Median runtime (ms) | 87.041 | 68.861 |
| Maximum runtime (ms) | 2477.652 | 1787.182 |
| Total runtime over cases (ms) | 8695.436 | 6030.508 |

- **Identical Netlists:** 25/25 files (byte-for-byte).
- **Area / Delay Changed Cases:** none.
- **Median Runtime Reduction:** 20.89%.
- Runtime numbers are separate wall-clock measurements performed by the official evaluator; CPU and filesystem conditions can influence them.
- **Search-time caveat:** faster synthesis can complete a different number of candidates before a time-based cutoff. Byte identity is an empirical check, not a guaranteed invariant of the whole executable.
- The netlist checker is exhaustive only for small input counts (n≤13), otherwise deterministically sampled; the official evaluator separately checks all published cases.

## Per-case timing

| Case | Round 4.1 (ms) | Round 5 (ms) | Reduction |
|---|---:|---:|---:|
| case_001.txt | 847.895 | 557.764 | 34.22% |
| case_002.txt | 299.460 | 203.947 | 31.90% |
| case_003.txt | 334.859 | 227.636 | 32.02% |
| case_004.txt | 32.896 | 23.466 | 28.67% |
| case_005.txt | 43.081 | 26.091 | 39.44% |
| case_006.txt | 41.987 | 28.630 | 31.81% |
| case_007.txt | 1030.063 | 762.796 | 25.95% |
| case_008.txt | 53.351 | 38.939 | 27.01% |
| case_009.txt | 87.041 | 68.861 | 20.89% |
| case_010.txt | 142.901 | 121.846 | 14.73% |
| case_011.txt | 51.879 | 29.868 | 42.43% |
| case_012.txt | 41.385 | 31.236 | 24.52% |
| case_013.txt | 141.519 | 101.089 | 28.57% |
| case_014.txt | 376.718 | 242.159 | 35.72% |
| case_015.txt | 565.101 | 366.987 | 35.06% |
| case_016.txt | 21.324 | 16.432 | 22.94% |
| case_017.txt | 9.887 | 6.781 | 31.41% |
| case_018.txt | 18.215 | 12.252 | 32.74% |
| case_019.txt | 166.373 | 101.077 | 39.25% |
| case_020.txt | 42.161 | 25.068 | 40.54% |
| case_021.txt | 567.564 | 420.715 | 25.87% |
| case_022.txt | 54.687 | 31.379 | 42.62% |
| case_023.txt | 13.012 | 8.250 | 36.60% |
| case_024.txt | 2477.652 | 1787.182 | 27.87% |
| case_025.txt | 1234.425 | 790.057 | 36.00% |

## Evidence

- `../reference/` and `../round5/`: official CSVs, evaluator logs, saved Netlists.
- `../round5/independent_verification.log`: independent verifier output.
- `../source_snapshot/`: compiled C++ and headers, Makefile, and scripts.
- `../profiles/`: optional stage timings on representative cases.
- `../environment.txt` and `../case_sha256.txt`: environment, sources, inputs, evaluator provenance.
- `../per_case_comparison.csv`, `../summary.json`: machine-readable local comparison.
- `mathematical_design.md`: the formal invariance argument and cache conditions.

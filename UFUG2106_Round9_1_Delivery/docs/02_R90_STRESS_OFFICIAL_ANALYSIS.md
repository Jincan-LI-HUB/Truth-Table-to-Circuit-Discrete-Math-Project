# Original Round 9.0 Stress Feedback — Genuine Evaluator Audit

User-provided feedback: `Round9.0_Feedback_20261122_192303_311650892.zip`. The CSV in `evidence/r90_official_stress_9.csv` preserves the raw distinct local and evaluator Runtime measurements.

## Correct interpretation

All **9/9 genuine course evaluator calls passed**; `exit_code=0` and `target_met=yes`, with `runtime_ms<100` in all nine official reports. The same nine outputs passed independent exact equivalence checks.

| Case | Frozen R8.6 (ms) | R9.0 default (ms) | Standalone default (ms) |
|---|---:|---:|---:|
| 20-input direct | 93.927 | 31.581 | 29.413 |
| 20-input affine | 77.023 | 21.321 | 26.222 |
| 18-input nonaffine | 28.469 | 27.985 | 30.337 |

**Local wall** is measured around Python's separate subprocess and may exceed 100ms while the evaluator's own time report is lower. This difference is an instrument-boundary difference, not proof of a memory or timer malfunction.

The frozen direct candidate's 93.927ms indicates a small observed 6.073ms slack; the R9.0 direct candidate's 31.581ms has larger observed slack. Three stress inputs are not a statistical guarantee for 50 private hidden tests. These cases set a positive runtime limit but no positive RAM limit, in line with TA guidance.

The literal `~` typed before the Bash commands invoked the home directory as a command and produced an irrelevant `Is a directory` shell error; the subsequent test script executed normally.

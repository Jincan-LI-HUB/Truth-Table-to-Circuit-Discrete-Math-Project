# Round 8.4 — Ablation, Negative Results and Evidence Provenance

## Dataset and measurement

The local experimental bank comprises the **actual previously provided 25 Stage 2 course cases**. All 6 search policies were run on all 25 inputs. Each generated circuit was checked against the full original truth table, *not sampled*. This produced **150/150 exact correctness passes**, all with delay <= each target. Input case numbering is used only for reporting, not in algorithm decisions. Source policy flags were cleared before each run. These experiments are **not the course evaluator**.

| Mode | Number of cases | Total area | Total output delay | Wall-guard occurrences |
|---|---:|---:|---:|---:|
| topology_dual | 25 | 500,072 | 1,169 | 0 |
| topq_dual | 25 | 503,764 | 1,155 | 0 |
| topq_dense | 25 | 502,649 | 1,155 | 2 |
| adaptive_dual | 25 | 502,618 | 1,157 | 0 |
| mixed33_dual | 25 | 499,684 | 1,169 | 3 |
| mixed66_dual | 25 | 499,035 | 1,169 | 2 |

Results: `evidence/stage2_full_150_exhaustive.csv`, `evidence/stage2_policy_summary.csv`.

## Interpretations

- **Negative result:** selecting strictly the top-ranked 900 decreases aggregate area quality even though it visits roots with better *proxy scores*. Of 25 cases versus topology, Top-Q reduces area in 3, worsens in 10 and ties in 12.
- **Area–delay trade-off:** Stage 2 `case_005`, old topology 106,771/67; new Top-Q 110,045/53 under target 69. The higher-area circuit has considerably lower delay; neither dominates the other.
- **Density trade-off:** Top-Q 1,100 recovers some Area (502,649) but triggered wall-clock protection twice in 25 local cases. It does not eliminate stability risk.
- **Positive mixed strategy:** selecting 600 of 900 roots by score and filling 300 from the earliest remaining topological roots (`mixed66_dual`) reduces total Area by **1,037** relative to topology while keeping every case's final Delay exactly the same; 8 cases improve in Area, 1 worsens by 4, the rest tie. The 1/3 variant saves 388. However `mixed66` triggered two wall-clock checkpoints (both branches of case_013), so repeated-run stability remains to be verified.
- **Crucial corrected-ablation note:** an earlier pre-release implementation accidentally applied the 1,500-root selection limit to the mixing modes, then truncated to 900 topologically. It misleadingly reproduced topology's scores. This invalid test was **discarded and rerun** after ensuring that exactly 900 selected roots are populated before topological processing. The displayed 499,684 and 499,035 numbers are from the corrected implementation, not the discarded data.
- **Pilot/focus:** 220-root Shannon/SOP pilots plus 1,100-root winner produced 502,618 area and no wall-guard hits in this particular local run. The method repeats the winner's first 220 roots and is a hypothesis rather than a proven improvement.

## Original scheduling diagnostic

In the frozen R8.3 code, top-ranked-900 overlap among the first 900 topologically visited eligible roots:

| Stage 2 input | Top-900 rank overlap | Missed high-score roots |
|---|---:|---:|
| case_003 | 501 | 399 |
| case_005 | 663 | 237 |
| case_021 | 462 | 438 |

These figures establish that priority selection and processing quota were not aligned. They **do not** establish that high-score skipped roots would yield more useful cuts. The Stage 2 area ablation directly refutes that naive inference.

## Frozen-source and implementation integrity

For `case_003`, `case_005`, `case_016` and `case_021`, Topology Dual in Round 8.4 generated **byte-identical netlists** to the frozen Round 8.3 Stable Dual when compiled on the same local host. This is a stronger control than matching only area sums.

## Runtime and evidence limitations

`local_ms` is process launch + synthesis + file-write wall time measured locally, *not* the official evaluator timing. The new mode's root selection can change memory allocation, and the time guard can still be triggered by machine load. The first random synthetic Holdout used in earlier rounds was overly trivial; the 24-case structured set in this package is reused developmental data, not a fresh blind test. No claims about the hidden bank are made.

## Memory trial evidence

`evidence/memory_direct_profiles.csv` measures direct Peak RSS from `/usr/bin/time` for Stage 2 cases 003,005,016,021 on the current Linux host. Per-instance RSS varies substantially (e.g. old 8.2.1 case_003 ~44,728 KiB, case_005 ~48,584 KiB), demonstrating **remaining practical memory-management work** for complex cases. These measurements cannot resolve the independent official positive-RAM evaluator anomaly. In particular, kernel RSS, `ru_maxrss` inherited across `execve`, and evaluator accounting must be differentiated.

## Structured holdout (reused development set)

The 24 previously frozen XOR/MUX/Majority structured cases were **reused**, rather than held blind. Both `topology_dual` and corrected `mixed66_dual` produced 24 legal, exhaustively verified circuits and identical total weighted area **13,897** and delay sum **613**. This neither refutes the development-set local gain nor establishes cross-distribution generalization. See `evidence/structured_holdout_r84_48.csv`.

## Repeated runs (local stability, 12 experiments)

Mixed66 was re-run three times each on Stage 2 cases 003, 005, 013, 023; all twelve outputs passed exhaustive verification. Areas for 003 were **16,517, 16,517, 16,517**, for 023 **2,140, 2,140, 2,140**, and for 013 **115,710** on all three. On **case_005** however, observed areas were **106,806, 109,218, 106,771** with respective wall-hit counts **1, 1, 0**. These different results are significant relative to the aggregate improvement (1,037) in the single prior full-bank run. Consequently, **Mixed66 must not be labeled fully deterministic**. See `evidence/repeat_mixed66_12.csv`.

This is why the default R8.4 mode remains the frozen-equivalent `topology_dual`, while all new modes are available for same-host official evaluation. The next experimental hypothesis is a *budget-safe completion policy* that avoids admitting incomplete branch results or uses more predictable work costs, without discarding valuable topological enabling rewrites.

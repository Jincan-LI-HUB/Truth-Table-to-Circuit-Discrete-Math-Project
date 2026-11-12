# Round 5.1 Local Reproduction Report

Local measurements (both executables recompiled on this machine).

| Paired run | Round 5 median (ms) | Round 5.1 median (ms) | Round 5 area | Round 5.1 area |
|---|---:|---:|---:|---:|
| 1 | 72.188 | 55.488 | 529,014 | 529,014 |
| 2 | 60.827 | 55.077 | 529,014 | 529,014 |

Mean-of-medians reduction: **16.88%**.
Run 1 netlist byte-identical: **25/25**.

This figure is descriptive, not a statistical confidence interval. Time-based candidate cutoffs may sometimes change netlists despite correct fixed-candidate transformations.

## Generalization check
- generated_110: 110/110 functional PASS; 96/110 target met; area_equal=True; delay_equal=True.
- holdout_v1: 80/80 functional PASS; 80/80 target met; area_equal=True; delay_equal=True.
- holdout_large_v1: 16/16 functional PASS; 16/16 target met; area_equal=True; delay_equal=True.
- stress: 2/2 functional PASS; 2/2 target met; area_equal=True; delay_equal=True.

## Archival notes

Evaluator logs, official CSVs, saved circuits, compiler and source hashes, independent verification and source snapshot are retained outside `report_ready/`, alongside this report.

Stage 2 remains unobserved. This test set does not establish zero overfitting or universal performance improvement.

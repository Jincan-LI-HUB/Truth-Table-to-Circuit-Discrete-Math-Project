# Round 8.1 — Official evaluator paired study

Raw evaluator CSV and log files are authoritative. No course scoring formula was assumed.

| Stage | Variant | Runs PASS | Passed-case Area (asterisk=incomplete) |
|---|---|---|---|
|stage1|r72|25/25, 25/25|529014, 529014|
|stage1|r80_iterate|25/25, 25/25|529014, 529014|
|stage1|r81_sop|25/25, 25/25|526378, 526397|
|stage1|r81_shannon|25/25, 25/25|525925, 525869|
|stage1|r81_all|25/25, 25/25|526793, 526778|
|stage1|r81_branch|25/25, 25/25|525699, 525682|
|stage1|r81_strict|25/25, 25/25|528920, 528918|
|stage1|r81_reverse|25/25, 25/25|525685, 525591|
|stage2|r72|25/25, 25/25|508535, 508535|
|stage2|r80_iterate|25/25, 25/25|508480, 508480|
|stage2|r81_sop|25/25, 25/25|498949, 498949|
|stage2|r81_shannon|25/25, 25/25|498568, 498736|
|stage2|r81_all|25/25, 25/25|501283, 501186|
|stage2|r81_branch|25/25, 25/25|498017, 498668|
|stage2|r81_strict|25/25, 25/25|508326, 508326|
|stage2|r81_reverse|25/25, 25/25|497509, 497695|

**Release gates:** {"r81_branch": {"50_case_pass_target_each_run": true, "no_area_regression_on_paired_pass": true, "no_delay_regression_on_paired_pass": false, "release_candidate": true}, "r81_strict": {"50_case_pass_target_each_run": true, "no_area_regression_on_paired_pass": true, "no_delay_regression_on_paired_pass": true, "release_candidate": true}}

See `casewise_comparison.csv`, `summary.json`, direct diagnostics, and official evaluator logs.
Area decreases with delay regressions are *not* Pareto improvements.

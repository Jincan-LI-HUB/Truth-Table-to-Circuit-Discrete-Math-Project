# Round 8.2 — Official evaluator paired study

Raw evaluator CSV and log files are authoritative. No course scoring formula was assumed.

| Stage | Variant | Runs PASS | Passed-case Area (asterisk=incomplete) |
|---|---|---|---|
|stage1|r72|25/25, 25/25|529014, 529014|
|stage1|r81_shannon|25/25, 25/25|526710, 526653|
|stage1|r81_reverse|25/25, 25/25|526531, 526755|
|stage1|r82_fast_area_stride|25/25, 25/25|526341, 526341|
|stage1|r82_fast_area|25/25, 25/25|526557, 526355|
|stage1|r82_fast_slack|25/25, 25/25|528900, 528900|
|stage1|r82_fast_adp|25/25, 25/25|527649, 527649|
|stage1|r82_dual_area|25/25, 25/25|526194, 526315|
|stage1|r82_dual_adp|25/25, 25/25|527608, 527608|
|stage1|r82_dual_strict|25/25, 25/25|528859, 528859|
|stage2|r72|25/25, 25/25|508535, 508535|
|stage2|r81_shannon|25/25, 25/25|502767, 503221|
|stage2|r81_reverse|25/25, 25/25|502584, 502753|
|stage2|r82_fast_area_stride|25/25, 25/25|503273, 503473|
|stage2|r82_fast_area|25/25, 25/25|503313, 503369|
|stage2|r82_fast_slack|25/25, 25/25|506296, 506485|
|stage2|r82_fast_adp|25/25, 25/25|508380, 508382|
|stage2|r82_dual_area|25/25, 25/25|501547, 502853|
|stage2|r82_dual_adp|25/25, 25/25|508289, 508287|
|stage2|r82_dual_strict|25/25, 25/25|508291, 508298|

**Release gates:** {"r82_fast_area": {"50_case_pass_target_each_run": true, "no_area_regression_on_paired_pass": true, "research_gate": true}, "r82_fast_adp": {"50_case_pass_target_each_run": true, "no_area_regression_on_paired_pass": true, "research_gate": true}, "r82_dual_area": {"50_case_pass_target_each_run": true, "no_area_regression_on_paired_pass": true, "research_gate": true}}

See `casewise_comparison.csv`, `summary.json`, direct diagnostics, and official evaluator logs.
Area decreases with delay regressions are *not* Pareto improvements.

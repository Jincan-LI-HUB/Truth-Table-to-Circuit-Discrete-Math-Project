# Round 10.0 — Local acceptance, provenance and negative evidence

## Verified acceptance

- Frozen Round9.0 SHA: `f846b2c055bfd5ad8d252dd1dcaa6770040b290bff6dc2bddc0ab27ff77e4010`.
- Frozen Round9.1 SHA: `345982dc0c27bd9862e03bf4b8e14a4741eeaba756212e2ccda114f040f4fb9f`.
- New Round10.0 solver and independent `submission/synth.cpp` have identical SHA, including complete header set.
- All five C++17 compilation targets built with `-O2 -DNDEBUG`.
- 10 fixed independent tests × six controls = 60/60 exhaustive equivalence checks, all meeting Target Delay. `evidence/local_exact_60.csv` includes true netlist SHA and individual runtime.
- Standalone `submission/` rebuilt in an empty temporary directory, without historical deliveries or custom environment variables; two independent tests (including a 20-input 100ms stress function) passed exhaustive equivalence.
- Two genuinely public Stage2 test cases (`case_003`, `case_005`), evaluated in this Linux container with all six controls: 12/12 exhaustive correctness checks. These are local executions, **not** official evaluator results. Public case data are not redistributed in this ZIP.
- Feedback exporter fail-closed test: missing evaluator generated a feedback ZIP with exit code 17, never a false official PASS.

## Negative: wall-clock trajectory affects final quality

`case_003` and `case_005` local results are recorded verbatim in `evidence/critical_public_local_12.csv`. Even equal sources or explicitly equivalent policy choices can return different *valid* netlists on high-complexity cases because an earlier time-budget decision is sensitive to elapsed wall time. This is not a Boolean correctness failure. We must evaluate paired comparisons using identical WSL evaluator, frozen inputs and reverse ordering, and must not require bitwise netlist equality on all wall-sensitive cases.

Do not report previously measured Area 1,019,547 as a new Round10.0 official result: it belongs to an earlier user-provided Round9.1 official feedback. WSL official release testing remains pending.

## Final grading assumptions

TA email of Nov 22 states 50 public + 50 hidden tests, no `ram_limit` on either; grading server has 48 GiB in total. No hidden tests were executed; no score weighting can be inferred from total Area alone. The Repeat SOP postpass may increase Runtime (prior user-provided public estimate geometric mean +3.4%), and its nominal 90ms search allowance is not a hard preemptive limit.

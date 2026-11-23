# Round 9.1 release notes

- Exact frozen Round9.0 parent SHA-256 retained (not modified).
- Source default remains frozen R9.0 `extra_sop`; Round9.1 experimental module `off` by default.
- New library enumerates 13,956 bounded 2/3/4-cut expression recipes and verifies each instantiated graph independently.
- Matched extra SOP and Shannon controls receive the same 160-root, nominal 90ms/6%-of-runtime opportunity (possible overrun due to non-preemptive root processing).
- `R91_ERROR` short-limit dispatch defect found and fixed before release; short-limit cases now correctly skip R9.1 without an error.
- 40/40 WSL-independent preflight cases PASS full equivalence; four lockbox cases opened once after the algorithm was frozen and show no library quality improvement.
- R9.0 user stress evidence 9/9 official PASS, not a grading-server generalization claim.
- Local Stage 2 totals are NOT official Round9.1 evaluator results; time sensitivity and input order effects remain.
- Genuine 500-record paired public gate must run in the user's WSL before any performance promotion.

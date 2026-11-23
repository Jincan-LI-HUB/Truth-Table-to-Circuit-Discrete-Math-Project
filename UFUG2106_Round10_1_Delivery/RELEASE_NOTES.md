# Round 10.1 release notes — Performance Audit, not a new final solver

1. Preserved R10.0 independent candidate source exactly (verified by SHA-256). **Official reference stays R10.0.**
2. Modified an experimental duplicate only: add `UFUG_R101_BUDGET_CAP_MS` to cap Repeat SOP's nominal 90ms allowance when explicitly set. No new rewrites, no logic-library changes, no changes to the grading CLI, no case-ID exceptions.
3. Inherited `UFUG_R91_ROOT_CAP` permits 40-vs-80-vs-160-root comparisons under otherwise identical code.
4. Introduced two-run, reverse-order paired evaluator protocol including the exact frozen baseline, reduced-quota experiments, explicit off and source-only cold-build trial.
5. Retained negative result: reduced root quotas cannot be assumed to preserve area, and wall-clock timing can alter the earlier synthesis incumbent. The 45ms cap is only a nominal allowance and not a hard-timeout guarantee.
6. No claimed improvement in hidden-case grade; all tests still need official WSL replay.

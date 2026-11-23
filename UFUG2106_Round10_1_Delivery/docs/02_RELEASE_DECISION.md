# Round 10.1 decision register

| Workstream | Status | Required before closing |
|---|---|---|
| R10.0 default Repeat SOP source | **Frozen** | Keep SHA constant; do not change default based on local score |
| R10.1 40/80 root quota | Experimental | Official paired 2-stage run, runtime/area sensitivity, short limits |
| R10.1 45ms nominal budget | Experimental | Official paired verification; hard wall-clock is *not* guaranteed |
| Source-only release | Prepared | Cold-build from isolated `frozen_submission/` in actual team project |
| Teammate Issue #2 integrated BDD budget | **Unresolved / separate** | Need actual integrated implementation; no patch was invented |
| Hidden tests | Unknown | Cannot claim pass or measured score |

**Stop condition:** if reduced quotas fail to improve the Area–Delay–Runtime trade-off reliably, stop experiments and ship the proven R10.0 + 12 headers. Changes in one local sweep never override a frozen official baseline. If the teammate's implementation is not available, do not pretend integration has been performed.

**Next action after WSL feedback:** compare each pair on Stage, run, case; evaluate per-case Area/Delay and paired runtime ratios with stage-level and global weighted metrics. Inspect any `TIME_LIMIT` or `target_met=no` first, then decide whether a smaller cap deserves validation on *new* cases. Do not select from Stage1/Stage2 area sums alone.

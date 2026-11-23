# Round 7 — Official Result Audit

- Result folder: `20261121_135745`
- Complete 4-mode official ablation: **False**
- Default Round 7 meets 50/50 PASS and all targets in each available run: **False**

## Official per-stage comparisons

| Run | Stage | Variant | PASS | Area Sum of PASS | Common PASS | Area improved/equal/regressed | Runtime G-mean ratio |
|---:|---|---|---:|---:|---:|---|---:|
| 1 | stage1 | default | 25/25 | 529014 | 25 | 0/25/0 | 0.980541 |
| 1 | stage2 | default | 24/25 | 506754 (partial) | 24 | 0/24/0 | 0.945277 |
| 2 | stage1 | default | 25/25 | 529014 | 25 | 0/25/0 | 1.041156 |
| 2 | stage2 | default | 24/25 | 506754 (partial) | 24 | 0/24/0 | 0.913382 |

## Notes

- Missing runtime or area for a FAIL is kept missing, **not zero**.
- Runtime is measured by the official evaluator. Ratios use only cases PASS in both programs.
- Two repeats are insufficient to establish statistical stability near a 100ms deadline.
- Equal area and delay do not prove identical gate-by-gate netlists.

**Official ablations are incomplete. Rerun `bash UFUG2106_Round7_Delivery/run_round7.sh` with this audited package, or explicitly use `--ablate`.**

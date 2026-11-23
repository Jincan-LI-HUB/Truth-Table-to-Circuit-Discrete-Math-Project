# Round 7 — Official Result Audit

- Result folder: `20261121_140841`
- Complete 4-mode official ablation: **True**
- Default Round 7 meets 50/50 PASS and all targets in each available run: **False**

## Official per-stage comparisons

| Run | Stage | Variant | PASS | Area Sum of PASS | Common PASS | Area improved/equal/regressed | Runtime G-mean ratio |
|---:|---|---|---:|---:|---:|---|---:|
| 1 | stage1 | default | 25/25 | 529014 | 25 | 0/25/0 | 0.987352 |
| 1 | stage1 | legacy_both | 25/25 | 529014 | 25 | 0/25/0 | 1.005098 |
| 1 | stage1 | legacy_cover | 25/25 | 529014 | 25 | 0/25/0 | 0.959663 |
| 1 | stage1 | legacy_merge | 25/25 | 529014 | 25 | 0/25/0 | 0.941732 |
| 1 | stage2 | default | 24/25 | 506754 (partial) | 24 | 0/24/0 | 0.917345 |
| 1 | stage2 | legacy_both | 25/25 | 508535 | 24 | 0/24/0 | 0.958086 |
| 1 | stage2 | legacy_cover | 25/25 | 508535 | 24 | 0/24/0 | 0.959889 |
| 1 | stage2 | legacy_merge | 25/25 | 508535 | 24 | 0/24/0 | 0.977733 |
| 2 | stage1 | default | 25/25 | 529014 | 25 | 0/25/0 | 0.984911 |
| 2 | stage1 | legacy_both | 25/25 | 529014 | 25 | 0/25/0 | 1.029378 |
| 2 | stage1 | legacy_cover | 25/25 | 529014 | 25 | 0/25/0 | 1.005101 |
| 2 | stage1 | legacy_merge | 25/25 | 529014 | 25 | 0/25/0 | 0.998517 |
| 2 | stage2 | default | 24/25 | 506754 (partial) | 24 | 0/24/0 | 0.929614 |
| 2 | stage2 | legacy_both | 25/25 | 508535 | 25 | 0/25/0 | 1.039612 |
| 2 | stage2 | legacy_cover | 25/25 | 508535 | 25 | 0/25/0 | 0.952317 |
| 2 | stage2 | legacy_merge | 25/25 | 508535 | 25 | 0/25/0 | 0.955834 |

## Notes

- Missing runtime or area for a FAIL is kept missing, **not zero**.
- Runtime is measured by the official evaluator. Ratios use only cases PASS in both programs.
- Two repeats are insufficient to establish statistical stability near a 100ms deadline.
- Equal area and delay do not prove identical gate-by-gate netlists.


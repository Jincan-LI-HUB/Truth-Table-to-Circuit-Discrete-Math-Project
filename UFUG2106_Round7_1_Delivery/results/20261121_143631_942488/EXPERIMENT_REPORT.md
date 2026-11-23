# Round 7.1 — Local Paired Experiment

- Official-evaluator release gate: **PASS**
- Runs: 2; variants: r51, r71_guard, r71_policy_off, r71_legacy_merge, r71_legacy_cover

| Stage | Version | PASS counts | Area sums of passed |
|---|---|---|---|
| stage1 | r51 | 25/25, 25/25 | 529014, 529014 |
| stage1 | r71_guard | 25/25, 25/25 | 529025, 529025 |
| stage1 | r71_policy_off | 25/25, 25/25 | 529014, 529014 |
| stage1 | r71_legacy_merge | 25/25, 25/25 | 529025, 529025 |
| stage1 | r71_legacy_cover | 25/25, 25/25 | 529025, 529025 |
| stage2 | r51 | 25/25, 25/25 | 508535, 508535 |
| stage2 | r71_guard | 25/25, 25/25 | 508535, 508535 |
| stage2 | r71_policy_off | 24/25, 24/25 | 506754*, 506754* |
| stage2 | r71_legacy_merge | 25/25, 25/25 | 508535, 508535 |
| stage2 | r71_legacy_cover | 25/25, 25/25 | 508535, 508535 |

*Asterisk: area sum excludes a failed case; never compare it as a complete 25-case score.*

The official grading formula is unknown. Failed cases cannot be assigned area zero.
The bundled diagnostic runs are not official time-limited measurements.

# Round 7.2 — WSL Official Paired Evaluation

**Correctness/target gate:** PASS
**No per-case area/delay regression relative to R7.1 Guard:** PASS

| Stage | Variant | PASS per run | Sum of area on passed cases per run |
|---|---|---|---|
| stage1 | r51 | 25/25, 25/25 | 529014, 529014 |
| stage1 | r71_guard | 25/25, 25/25 | 529025, 529025 |
| stage1 | r72_shortlist | 25/25, 25/25 | 529014, 529014 |
| stage1 | r72_guard | 25/25, 25/25 | 529025, 529025 |
| stage1 | r72_nocancel | 25/25, 25/25 | 529014, 529014 |
| stage2 | r51 | 25/25, 24/25 | 508535, 506754* |
| stage2 | r71_guard | 25/25, 25/25 | 508535, 508535 |
| stage2 | r72_shortlist | 25/25, 25/25 | 508535, 508535 |
| stage2 | r72_guard | 25/25, 25/25 | 508535, 508535 |
| stage2 | r72_nocancel | 25/25, 25/25 | 508535, 508535 |

*An asterisk denotes incomplete area because at least one case failed.*
No official grading formula is implied. Direct profiles are NOT official timing.
Quality regression report compares every jointly passing case to R7.1 Guard.

## Pre-registered hypotheses
- H1: R7.2 shortlist recovers Stage1 case020 QoR without worsening Stage2 case016 QoR.
- H2: R7.2 shortlist remains within the official 100ms constraint for both cases.
- H3: Most larger-budget cases remain byte-for-byte quality-equivalent to R7.1.
See casewise_comparison.csv and all per-run original evaluator logs for evidence.

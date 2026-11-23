# Round 10.0 — Official Feedback Audit (2026-11-22)

**Evidence:** uploaded feedback ZIP `Round10.0_Feedback_20261122_121200_917768.zip`. No hidden-case performance claim.

## Gate

- 600/600 official public evaluations PASS and 600/600 target met.
- All 6 configurations produce identical Area/Delay per case across the two runs (50/50 each).
- R10 default, R10 explicit Repeat SOP, independent submission, and frozen R9.1 explicit Repeat SOP: **300/300 paired case comparisons** are identical in Area and Delay (3 new configurations × 2 runs × 50 public cases).
- R10 `off` matches frozen R9.0 per-case Area/Delay.

## One-run area and delay totals (repeated identically in run 2)

| Policy | Stage1 Area | Stage2 Area | Total Area | Total Delay |
|---|---:|---:|---:|---:|
| `r90_frozen` | 526,135 | 494,999 | 1,021,134 | 2,382 |
| `r91_sop_explicit` | 525,582 | 493,965 | 1,019,547 | 2,382 |
| `r100_default` | 525,582 | 493,965 | 1,019,547 | 2,382 |
| `r100_sop_explicit` | 525,582 | 493,965 | 1,019,547 | 2,382 |
| `r100_off` | 526,135 | 494,999 | 1,021,134 | 2,382 |
| `submission_default` | 525,582 | 493,965 | 1,019,547 | 2,382 |

## Run1 improvements of R10 default vs frozen R9.0

| Stage | Case | Area R9.0 | Area R10.0 | Savings | Delay Δ |
|---|---|---:|---:|---:|---:|
| stage1 | `case_010.txt` | 3,335 | 3,037 | 298 | +0 |
| stage1 | `case_012.txt` | 4,013 | 3,763 | 250 | +0 |
| stage1 | `case_016.txt` | 2,145 | 2,140 | 5 | +0 |
| stage2 | `case_003.txt` | 15,773 | 15,623 | 150 | +0 |
| stage2 | `case_005.txt` | 103,641 | 102,889 | 752 | +0 |
| stage2 | `case_012.txt` | 4,145 | 4,143 | 2 | +0 |
| stage2 | `case_023.txt` | 2,029 | 1,904 | 125 | +0 |
| stage2 | `case_024.txt` | 6,878 | 6,873 | 5 | +0 |

Total savings = **1,587**. Improved 8/50 cases; no Area/Delay deterioration observed.

## Paired runtime (R10 default vs frozen R9.0)

- `r91_sop_explicit`: paired runtime geometric mean ratio **1.0477×**; median official Runtime **157.12 ms**; max **1710.07 ms**.
- `r100_default`: paired runtime geometric mean ratio **1.0166×**; median official Runtime **151.43 ms**; max **1755.54 ms**.
- `r100_sop_explicit`: paired runtime geometric mean ratio **1.0349×**; median official Runtime **154.93 ms**; max **1727.93 ms**.
- `r100_off`: paired runtime geometric mean ratio **0.9889×**; median official Runtime **142.25 ms**; max **1785.94 ms**.
- `submission_default`: paired runtime geometric mean ratio **1.0216×**; median official Runtime **149.67 ms**; max **1861.73 ms**.

These runtime figures are observations from one WSL evaluation batch, not guarantees about runtime on the final grader. Comparison is paired by stage, case and run.

## Source provenance

- R10 research / submission source SHA-256: `8c863f1a1c9555ae571948a0424c25642c29c9a9f98f1f3e5f193c6b20f5b15d` (byte-identical).
- Source is multi-file C++17: `submission/synth.cpp` includes twelve local `.hpp` dependencies. Final source release must include **all** these files and a compile README; the course PDF specifies source code and compilation instructions but does not require a single-file submission.
- R9.0 and R9.1 frozen sources have been retained. R10 uses `repeat_sop` only as the missing-environment fallback, and `off` is an explicit test backstop.
- The official test harness clears `UFUG_*`, `R90_*`, and `R10_*` environment variables before unconfigured tests.

## Decisions and integration gate

1. **Freeze independent candidate** (not yet the team-integrated Stage2 submission): source integrity, public Area/Delay and fallback passed.
2. **No more broad algorithm exploration:** extra SOP improves public Area by 0.1554%, with runtime increase around 1.7% in the direct R10-vs-R9.0 paired experiment. Since score weightings are unspecified, do not claim best grading score.
3. **Round10.1 integrate only with actual team source**: first freeze team baseline; run team-only and R10-only in identical conditions; integrate modules individually with default environment cleared; verify full exactness and 50 public cases plus adversarial short-budget cases; explicitly test Issue #2 BDD budget transfer only against its true integration stage; never blindly overwrite frozen versions.
4. **Issue #2 remains open.** GitHub main and documentation branch do not expose a Stage2 integrated implementation at audit time; request a concrete branch/commit/archive for reproducible merge.
5. **Round10.2**: construct final submission archive with all headers, test `g++ -O2 -std=c++17 -DNDEBUG submission/synth.cpp -o synth` from a fresh directory, test CLI path handling and successful output, run official 50+stress, preserve frozen manifest, complete method comparison and teammate contribution report.


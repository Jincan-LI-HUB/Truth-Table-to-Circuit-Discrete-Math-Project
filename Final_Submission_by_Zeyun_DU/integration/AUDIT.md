# Final integration audit

The planned team delivery is Zeyun Du's integrated Stage 2 solver at upstream commit `59e33505616d127fc06a63580ca3ae3c34d1da72`. On 24 November 2026, the upstream default branch pointed to that commit, and the local research `main` and its upstream pointed to `4838e50d52408087639c3d3816b10761f18f6ccb`. The research working tree was clean before this archive. The verified results below concern the released inputs. Course submission status and hidden-test results are unverified. [Pinned team source](https://github.com/zdu881/UFUG2106-Project/commit/59e33505616d127fc06a63580ca3ae3c34d1da72) · [Research checkpoint](https://github.com/Jincan-LI-HUB/Truth-Table-to-Circuit-Discrete-Math-Project/commit/4838e50d52408087639c3d3816b10761f18f6ccb)

## Source and cold build

The manifest lists 74 files from the pinned Git tree. It records the Git blob and SHA-256 for every source, header, tool and archived evidence file. Four report pairs have their student numbers removed in local copies, with both original and local hashes recorded. The upstream and research Git blobs match for the course evaluator and all 50 public truth tables. The archive reuses the research repository's copies and preserves the upstream course-material attribution. [Provenance manifest](../PROVENANCE.json) · [Original source attribution](../src/round51/ORIGIN.md) · [Course materials notice](../official/README.md)

The native build ran from a fresh WSL filesystem directory with the archived source, headers and Makefile. It used no upstream home directory or historical research source paths. A second build used the source ZIP extracted into a separate directory. The ZIP contains `synth_stage2.cpp` at its root. Both executables passed independent exhaustive replay of the shared-output example. GCC 13.3 issued an array-bounds warning while inlining a sort involving `terms[4]` in the imported Round 5.1 header. The build completed and the warning is preserved for review. [Cold build log](data/matched/logs/cold-build.txt) · [Native smoke check](data/matched/logs/synth_stage2-smoke-verified.txt) · [ZIP smoke check](data/matched/logs/synth-smoke-verified.txt)

All 22 upstream tests passed on the archived source. [Test log](data/matched/logs/archive-tests.txt)

## Reconciled upstream results

The four supplied rows reproduce exactly from `stage2-cuts-20261124/casewise.csv` after rounding summed evaluator milliseconds to two decimal places in seconds. The upstream row labels `local` and `merged` identify the previous and then-current integrated cuts snapshots. The CSV supplies the measurements but does not identify exact executable hashes for those snapshots. [Earlier casewise CSV](../reports/stage2-cuts-20261124/casewise.csv)

| Earlier cuts run | Evaluator PASS | Delay target met | Weighted area | Synthesis sum |
|---|---:|---:|---:|---:|
| Submitted Stage 1 (Z1) | 50/50 | 50/50 | 1,205,667 | 39.89 s |
| Jincan R10.0 | 50/50 | 50/50 | 1,023,713 | 26.07 s |
| Previous Integrated Stage 2 (`local`) | 50/50 | 50/50 | 872,639 | 32.90 s |
| Integrated cuts snapshot (`merged`) | 50/50 | 50/50 | 869,773 | 33.68 s |

The pinned release's own three public repeats were built from the extracted source ZIP, according to the upstream release report. All runs report 50 evaluator passes and 50 delay targets met, minimum slack of one delay unit, and exhaustive replay. Across these repeats the maximum measured runtime was 49.7% of the relevant input limit. The separate upstream direct-process RSS series peaks at 45,976 KiB (44.9 MiB) on Stage 1 case 024. [Release acceptance CSV](../reports/stage2-timing-20261124/public-runs.csv) · [Upstream verification description](../reports/stage2-timing-20261124/README.md) · [Upstream direct RSS](../reports/stage2-timing-20261124/public-rss.csv)

| Pinned release repeat | Evaluator PASS | Delay target met | Weighted area | Synthesis sum |
|---|---:|---:|---:|---:|
| 1 | 50/50 | 50/50 | 884,234 | 49.73 s |
| 2 | 50/50 | 50/50 | 876,694 | 46.15 s |
| 3 | 50/50 | 50/50 | 876,694 | 46.01 s |

The earlier cuts snapshot, the pinned acceptance tests and the historical Jincan research batch have their own version/run provenance. Whole-solver runtime and area comparisons with Integrated Final use only the fresh matched batch below. [Historical Z1/J51/R10.0 data](../../Stage%202%20Formal%20Report/data/matched_case_metrics.csv)

## Fresh matched benchmark

The four entry points are Z1 from the original Stage 1 submission audit, J51 from the verified Round 5.1 freeze, R10.0 from its frozen independent delivery, and Integrated Final from this pinned archive. A single WSL2 Ubuntu host compiled all four with GCC 13.3 and `-O2 -std=c++17 -pipe -DNDEBUG`. The official evaluator ran both 25-case banks sequentially with default input limits and saved netlists. Repeat 2 reversed bank order and solver order. Each absolute benchmark input is identified by its bank and basename. Source snapshots, options, compiler and Python versions, input and evaluator hashes, and run order are in the environment record. [Environment and source identities](data/matched/environment.json)

The evaluator's PASS count and target-met count measure different conditions. The independent checker evaluates every assignment and recomputes weighted area, critical-path delay, and target status on the saved Integrated Final netlists. Runtime sums include only reported durations, with their denominators retained. Delay medians, maxima and minimum slack describe the observed passing circuits. The maximum time-budget share is the largest reported runtime divided by that input's positive limit. Per-case runtime ratios pair equal bank, case, and repeat on jointly passing observations. A median of those ratios and the ratio of runtime sums answer different questions.

| Repeat | Solver | Evaluator PASS | Delay target met | Weighted area | Synthesis sum | Median time | Max time / limit |
|---:|---|---:|---:|---:|---:|---:|---:|
| 1 | Z1 | 50/50 | 50/50 | 1,127,450 | 37.151 s | 602.59 ms | 63.04% |
| 1 | J51 | 50/50 | 50/50 | 1,037,549 | 8.663 s | 29.60 ms | 97.92% |
| 1 | R10.0 | 50/50 | 50/50 | 1,019,547 | 14.736 s | 145.37 ms | 21.95% |
| 1 | Integrated Final | 50/50 | 50/50 | 872,813 | 32.350 s | 218.87 ms | 51.94% |
| 2 | Z1 | 50/50 | 50/50 | 1,127,196 | 36.954 s | 602.94 ms | 67.52% |
| 2 | J51 | 50/50 | 50/50 | 1,037,549 | 9.419 s | 34.78 ms | 96.93% |
| 2 | R10.0 | 50/50 | 50/50 | 1,019,547 | 15.047 s | 148.66 ms | 23.62% |
| 2 | Integrated Final | 50/50 | 50/50 | 872,919 | 32.243 s | 223.61 ms | 51.95% |

Integrated Final saved **22.6%** aggregate weighted area versus Z1 and **14.4%** versus R10.0 in both repeats. It improved area on 36 and 35 cases versus Z1 and 43 cases in each repeat versus R10.0. Relative to Z1, its median per-case runtime ratios were **0.532× / 0.529×** and its ratios of summed runtime were **0.871× / 0.873×**. Relative to R10.0, those were **2.316× / 2.262×** and **2.195× / 2.143×**, respectively. The paired table also includes J51 and the delay win/tie/loss counts. [Within-repeat pairs](data/matched_pairs.csv)

J51's Stage 2 case 016 consumed 97.92% and 96.93% of its input time limit in the two completed repeats. It hit the time limit during an earlier invocation that stopped the benchmark driver. The driver was corrected to keep a complete evaluator CSV when the exit status indicates a case failure, then both repeats were rerun from a clean build. The earlier 24/25 Stage 2 bank remains a diagnostic outside the matched results, as does the failure in the historical research batch. [Interrupted run evaluator log](data/diagnostic/interrupted-J51-stage2.txt) · [Historical research batch](../../Stage%202%20Formal%20Report/data/matched_case_metrics.csv)

The delay statistics were identical across the two completed repeats. Integrated Final had a median delay of 50 and a maximum of 85, with at least one unit of slack on every public input. Compared with R10.0, its delay was lower on 12 cases, equal on 16, and higher on 22 in each repeat. In each repeat, nine cases improve both weighted area and circuit delay, twelve reduce area at equal delay, and twenty-two reduce area with higher delay. The 22 slower circuits still meet their individual delay targets. All 100 of its saved netlists matched every source truth-table assignment in the independent replay. [Independent replay records](data/matched/independent/) · [Case-level delay](data/matched_case_metrics.csv)

| Solver | Median circuit delay | Max circuit delay | Min delay slack | Median direct RSS | Max direct RSS |
|---|---:|---:|---:|---:|---:|
| Z1 | 44.0 | 85 | 0 | 6,880 KiB | 56,024 KiB |
| J51 | 46.0 | 73 | 0 | 6,772 KiB | 72,496 KiB |
| R10.0 | 48.5 | 73 | 0 | 12,124 KiB | 75,564 KiB |
| Integrated Final | 50.0 | 85 | 1 | 7,742 KiB | 58,912 KiB |

The direct RSS experiment ran each executable once more per case outside the evaluator, with GNU `time %M`. The RSS table describes these separate processes. The two public banks omit the RAM limit, so there is no public RAM-budget percentage for this comparison. The upstream generated memory controls retain the official verdict and direct-process measurements side by side. [Matched case metrics](data/matched_case_metrics.csv) · [Per-bank and aggregate summaries](data/public_summary.csv) · [Within-repeat paired metrics](data/matched_pairs.csv) · [RSS summary](data/direct_memory_summary.csv) · [Upstream generated memory controls](../reports/stage2-timing-20261124/memory.csv)

## Attribution and scope

- Zeyun Du authored Z1 and coordinated integration, public acceptance objectives and validation. Jincan Li developed the independent J51 and R10.0 research line. The integration reuses Round 5.1 candidate construction and mapping and the R10.0 four-leaf cut mapper. The upstream report credits Codex for timing-rescue implementation and release verification assistance. [Origin note](../src/round51/ORIGIN.md) · [Upstream contribution section](../reports/stage2-timing-20261124/UFUG2106_Group2_Stage2_Report.pdf)
- Earlier same-incumbent instrumentation reports 3,165 weighted area units saved by SOP cut polishing across 17 of 50 public cases. The shared-factor instrumentation reports 5 area units saved across two public cases, with separate results on diagnostic and holdout cases. These instrumented passes ran on earlier integration snapshots. Their effects cannot be added to explain the whole-version delta. [Cut instrumentation and measurements](../reports/stage2-cuts-20261124/paired.csv) · [Factor instrumentation and measurements](../reports/stage2-factors-20261124/paired.csv)
- The integrated source includes variable-order scheduling, a compact alternative and output selection, one-unit delay reserve, critical-cut repair, and exact late-output rescue. The nominal main search budget is `min(3300 ms, 0.45 × limit)` for positive limits, or 1800 ms otherwise. The upstream old-cap trial with 910,462 area ran under competing CPU load. This observation motivated the 3.3 s cap, but the archive has no controlled comparison quantifying the cap's independent contribution to the integrated area's advantage. [Source](../src/synth_stage2.cpp) · [Earlier cap measurements](../reports/stage2-timing-20261124/earlier-budget.csv)
- The upstream freeze record lists 168/168 targets on the development banks, 55/56 on four designated validation banks, and 28/28 on two banks generated after the final ZIP freeze. The four validation banks were prospective in one snapshot and labeled development in the later extended-window snapshot. The freeze grouping preserves their upstream designation. Across the six banks, 83/84 targets were met in 72 generated networks and twelve observations of two repeated exact-delay controls. The remaining generated miss is seed 711413, case 003, with achieved delay 28 and target 27. It remains a recorded test limit. [Pinned timing evidence](../reports/stage2-timing-20261124/README.md) · [Remaining case](../reports/stage2-timing-20261124/residual.csv)

## Reproduce the local evidence

Run from the research repository root under Linux or WSL:

```bash
archive=Final_Submission_by_Zeyun_DU/integration
python3 "$archive/verify_evidence.py"
work=$(mktemp -d)
python3 "$archive/run_benchmark.py" "$work/matched"
```

The verifier checks the imported bytes and original Git blob identities where applicable, the matched source/evaluator/input hashes, each bank's case coverage, the independent results and the derived tables. Use `--write` to regenerate those tables from the recorded CSVs. The benchmark runner preserves each new run in its own output directory. The existing R1–R10.1 sources and original CSVs retain their historical values.

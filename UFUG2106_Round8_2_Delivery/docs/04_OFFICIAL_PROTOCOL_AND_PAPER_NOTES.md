# Round 8.2 — Official Experimental Protocol, Quality Gates, and Publication Notes

## Exact comparison plan

The supplied `run_round82.sh` builds the new C++ source from a SHA-256-locked Round8.1 file and then runs the course evaluator on **Stage1 (25) and Stage2 (25), each twice**, reversing variant execution order in the second repetition. All raw CSVs and evaluator logs are retained. The experiment is not a synthetic equivalent of the official evaluator: no PASS is claimed until this runs on the user's machine.

| Variant | Purpose | Main cost |
|---|---|---|
| `r72` | Frozen reference incumbent | Baseline |
| `r81_shannon` | Frozen single-mode comparator | Old sampling/selection |
| `r81_reverse` | Frozen expensive best-area comparator | Prior area benchmark |
| `r82_fast_area_stride` | Isolate sampling | Strided, same R82 work cap |
| `r82_fast_area` | New priority with area selection | One Shannon branch |
| `r82_fast_slack` | Isolate bounded slack selection | Same candidates as fast area |
| `r82_fast_adp` | Isolate ADP selection | Same candidates as fast area |
| `r82_dual_area` | Isolate second SOP branch | More runtime |
| `r82_dual_adp` | Same branch space, different selection | More runtime |
| `r82_dual_strict` | Delay-non-regression comparator | Strong quality constraint |

The `--quick` command runs the frozen R7.2 and R8.1 Shannon comparators plus the three principal R8.2 variants; the full command is preferred for publication evidence. Optional `UFUG_R82_ROOT_CAP=750/1500/2500` can be used for additional *separately logged* stress studies, but it must not silently change the default dataset.

## Evaluation variables

For each complete PASS candidate record: \((A_i,D_i,T_i)\), relative area \(A_i/A_i^{(0)}\), relative delay \(D_i/D_i^{(0)}\), relative runtime \(T_i/T_i^{(0)}\), and normalized delay penalty \(D_i/D_{\mathrm{target},i}\). Record minimum runtime headroom \(1-T_i/T_{\mathrm{limit},i}\) when the limit is available from the input. Missing or TIME_LIMIT cases must be excluded from ratio denominators *and* reported separately; missing areas must not improve total-area sums.

Report geometric mean of paired ratios, median, 95th percentile, worst case, target-met count, Pareto-dominance count, and aggregate area ONLY for full common-pass sets. The exact class scoring formula remains unknown; do not optimize arbitrary guessed weights.

## Gate criteria

1. All 50 public cases produce structurally valid, truth-table-equivalent outputs within evaluator runtime/RAM constraints.
2. All 50 meet target delay (desired engineering gate, although public PASS may not require this).
3. Preserve a complete valid incumbent; require no paired-case area regressions for principal candidate modes unless a new trade-off is explicitly documented.
4. Direct diagnostic runs are separated from official evaluator runtime, and all instrumentation overhead is disclosed.
5. Compare the expensive prior Reverse, the simpler old Shannon, and the new R8.2 variants on the same machine and same input datasets.
6. Never turn a single benchmark into case-ID-specific solver logic.

## What the study can say

- A priori root selection changes feasible cut-search trajectories, measurable by the stride/priority ablation.
- Exact full-DAG cost decisions preserve a valid incumbent for every completed branch; locally equivalent cuts preserve Boolean function.
- Bounded slack and ADP surrogates expose the policy sensitivity that an area-only result hides.
- The structured synthetic holdout suggests broader *synthetic* effectiveness beyond the 50 public development cases.

## What the study must not say

- "Globally optimal circuit" (not proven).
- "Official grade improves" (the syllabus scoring equation is unavailable).
- "Hidden cases will pass" (untested distribution, different resource regime).
- "Root Priority always dominates Stride" (two Stage2 public regressions exist in a 25-case batch).
- "Time budget is guaranteed" (the current cutoff is cooperative, not a hard real-time scheduler).
- "Pareto choice graph" (only a tiny measured-metric archive is implemented).

## Subsequent research questions (Round 8.3 only after official feedback)

- Does root priority retain its aggregate advantage in Stage1, which was not available for full local verification?
- Can a learned-but-still-simple cost predictor outperform the hand-chosen potential function without overfitting public data?
- Is a root-cap portfolio (750, 1500, 2500) worth maintaining as separate Pareto branches rather than picking K from public case scores?
- Can critical-cone-aware multi-output resubstitution recover large area without consuming 100% of timing slack?
- How does the actual syllabus objective change the preferred policy relative to ADP, strict, and area?

## Reproducible paper material

Preserve the parent SHA, new source SHA, all code configuration environment variables, raw official evaluator CSVs/logs, boolean equivalence reports, negative holdout-v1 results, structured-v2 frozen SHA manifest, paired casewise tables, and a statement that this research involved adaptive iterations on public cases.

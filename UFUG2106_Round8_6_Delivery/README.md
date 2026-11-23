# UFUG2106 — Round 8.6 (Controlled Root Allocation and Time Reclaim)

**Research candidate, not a final frozen submission.** This package is self-contained: the R8.6 C++17 source and the exact frozen R8.5 comparator source are embedded; no earlier Round directory is necessary. No modifications are made to the genuine evaluator or public cases.

## Motivation and experimental contract

R8.5 `budget_reclaim` increased the second SOP branch's root quota from 900 to 1200 **and** raised its allowable wall time. Its gains therefore did not identify which factor caused the improvements. Round 8.6 tests those two factors independently, with the same pre-cut incumbent, graph, scoring, Top-Q ordering, correctness checker, and global time guard.

| Policy (`UFUG_R86_POLICY`) | Shannon roots | SOP roots | SOP time allowance |
| --- | ---: | ---: | --- |
| `baseline` | 900 | 900 | original nominal |
| `extra_sop` | 900 | 1200 | original nominal |
| `time_reclaim` | 900 | 900 | may use unused shared budget |
| `combined` | 900 | 1200 | may use unused shared budget |
| `reverse_allocation` | 1200 | 900 | original nominal |

**Scope rule:** for runtime budget `limit<=2000 ms` and `m>=20` the common root baseline is 600 and the extra-quota branch gets 900. This rule is inherited from R8.5. The matrix describes the usual 900-root settings; the program logs the actual values.

The two frozen comparator controls are `r85_dual` (`dual_shannon_first`) and `r85_reclaim` (`budget_reclaim`). SOP/Shannon order is **Shannon then SOP** throughout this Round's five factor ablations, with the R8.5 comparator using the same order.

## Run in WSL

Place this folder alongside the course's original `evaluator` binary and `data/stage1`, `data/stage2`. Then:

```bash
BASE="/mnt/e/canfiles/Common courses study/大学通识/26-27 Fall/UFUG 2106 Discrete Math/assignment/Final Project"
cd "$BASE" || exit 1
bash UFUG2106_Round8_6_Delivery/run_round86.sh
```

- `bash UFUG2106_Round8_6_Delivery/run_round86.sh --quick`: short preflight plus 3 official configurations × 2 stages × 25 cases × 1 run = 150 official results.
- `bash UFUG2106_Round8_6_Delivery/run_round86.sh --local-only`: C++ build, policy isolation, 5 critical cases × 5 configurations, 18 fresh synthetic cases, cold-source build; no official claims.
- Full run: 7 configurations × 2 stages × 25 cases × 2 runs = **700 official case records** with reverse configuration order on run 2.

Whether passing or failing, the script saves logs and creates:

```text
UFUG2106_Round8_6_Delivery/feedback/Round8.6_Feedback_<timestamp>.zip
```

The tool never fabricates official scores when the genuine evaluator is absent. The independent local verification uses `tests/verify_exhaustive.cpp` on each generated netlist.

## Experimental metrics and caveats

Inspect `official/summary.json` and 28 official CSVs. For causal interpretation, compare Area, Delay, per-case runtime, time allocation, `R86_STAGE` logged root visits, and wall-cutoff counts. Wall-clock deadlines and upstream BDD exploration remain load-sensitive; repeated equality on one host is not a proof of deterministic output across machines.

The local 25 × 6 Stage2 controlled ablation passed 150 exhaustive truth-table checks; the **offline** results are in `evidence/local_stage2_150_casewise.csv`. Offline outcomes can change with host load and cannot substitute for the course evaluator.

## Source tree

- `src/synth_round86.cpp`: proposed controlled experiment source; `UFUG_R86_POLICY` selects its five modes.
- `src/synth_round85_frozen.cpp`: exactly the parent Round8.5 source (SHA in manifest) for paired comparison.
- `src/*.hpp`: all embedded headers; no historical directories needed.
- `tools/run_official.py`: original evaluator, original public banks, paired reverse order.
- `tests/verify_exhaustive.cpp`: complete truth-table verification.
- `tests/test_clean_build.py`: isolated compilation without previous deliveries.
- `docs/07_R86_CONTROLLED_ABLATION.md`: hypotheses, implementation mathematics, local results and limitations.
- `docs/08_POST_R86_RESEARCH_ROADMAP.md`: proposed R8.7–8.9 roadmap and stop criteria.

**Team Issue #2:** The teammate's integrated Stage2 BDD budget refund remains separate; this package only studies post-BDD SOP/Shannon Cut Search. Positive `ram_limit` is not a grading condition according to the latest TA announcement. Memory monitoring continues as an engineering concern.

# UFUG2106 · Round 8.5 Research Delivery

**Grading-Aligned Robustness, SOP/Shannon Branch Scheduling, and Clean Build**

Status: **self-contained source / 125 independent exhaustive Stage 2 validations PASS locally / official course evaluator pending on the recipient's WSL machine.**

## What changed

- Complete current Stage 2 synthesizer and a SHA-frozen Round 8.4 comparator are included **inside this ZIP**. No prior `UFUG2106_RoundX` folder is needed for compilation or evaluation. This closes the *research package* reproducibility dependency, not yet the teammate's separate *integrated Stage 2 repository* README issue.
- Add explicit R85 search policies using the existing proven 4-cut Boolean equivalence rewriter: Shannon→SOP, SOP→Shannon, dense SOP-first, SOP-only, and an experimental remaining-time-reclaim policy. Gate operators, correctness verifier, incumbent fallback, and 23% wall-clock reserve are unchanged.
- Preserve the Round 8.2.1 positive-memory fallback; do **not** claim the official 9,000-KiB evaluator discrepancy is fixed. TA clarified the final 100 cases carry no positive RAM Limit.
- Add a *reference* integration budget ledger with a unit test for the teammate's Issue #2 item 4. It is not a patch to their integrated source, which is not present in the public main branch inspected for this project.
- Add frozen new synthetic Boolean correctness fixtures to complement the 24 reused structured holdouts.

## Extract and run on WSL

Place `UFUG2106_Round8_5_Delivery/` alongside the genuine evaluator and public banks:

```bash
BASE="/mnt/e/canfiles/Common courses study/大学通识/26-27 Fall/UFUG 2106 Discrete Math/assignment/Final Project"
cd "$BASE" || exit 1
bash UFUG2106_Round8_5_Delivery/run_round85.sh
```

Full run: two reversed-order runs, both Stage 1 and Stage 2, seven policies (700 evaluator records); **does not require any other Round folder**. Failures also save a feedback ZIP. Reduced official pilot:

```bash
bash UFUG2106_Round8_5_Delivery/run_round85.sh --quick
```

Local-only correctness, policy isolation, clean build, and unit tests (does **not** claim genuine official evaluator success):

```bash
bash UFUG2106_Round8_5_Delivery/run_round85.sh --local-only
```

Result: `UFUG2106_Round8_5_Delivery/feedback/Round8.5_Feedback_<timestamp>.zip`.

### Research ablations

Environment variable `UFUG_R85_POLICY` controls Round 8.5; it is **`dual_sop_first` by default** for research, *not a selected final grading submission*. All options are generic, never keyed to case IDs.

| Policy | Explanation |
|---|---|
| `dual_shannon_first` | Top-Q 900 roots in Shannon then SOP order |
| `dual_sop_first` | Top-Q 900 roots in SOP then Shannon order (**provisional research default**) |
| `dense_shannon_first` | Top-Q 1,100 roots, Shannon first |
| `dense_sop_first` | Top-Q 1,100 roots, SOP first |
| `sop_only` | Single SOP branch, cap 900 |
| `budget_reclaim` | Return unused first-branch wall-time allowance to second branch, up to 1,200 roots (experimental) |
| `off` | Revert to explicit `UFUG_R84_POLICY` controls for frozen ablation |

Use `UFUG_R85_PROFILE=1` for per-branch work and guard diagnostics; `UFUG_R85_ROOT_CAP=100..1500` is optional for research. **Do not set unmeasured benchmark-dependent policy variables in final submission.**

## Local research findings (not official)

All 125 independently evaluated solutions (25 original Stage 2 cases × 5 policies) passed all truth assignments and met their target delays. The totals below come from one local run on this machine; they are not directly comparable to WSL official timing and can fluctuate when the wall guard fires.

| Policy | Stage 2 Area Sum | Delay Sum | Wall-hit events |
|---|---:|---:|---:|
| Frozen R8.4 Top-Q Dual | 501,124 | 1,170 | 13 |
| R8.5 Shannon-first | 502,308 | 1,170 | 11 |
| **R8.5 SOP-first** | **499,340** | 1,170 | 16 |
| R8.5 Dense SOP-first | 500,097 | 1,170 | 18 |
| R8.5 Budget reclaim | 501,635 | 1,170 | 15 |

Important caveat: SOP-first's area gain is primarily case 005, which is wall-sensitive. Repeated-run experiments showed meaningful casewise fluctuations; **no strategy is declared stable or best based on one sum**. The remaining-time-reclaim variant is a negative result in this standalone Cut Search; it is not the same as the teammate's BDD budget-return proposal.

Evidence: `evidence/stage2_125_exact_local.csv`, `evidence/stage2_125_summary.csv`, `evidence/repeat_selected_local.csv` (partial 38-run repeat set), `evidence/fresh_synthetic_v1/`.

## Final grading context and source handoff

The TA's November 2026 clarification says final grading reruns the submitted Stage 2 source on 50 public + 50 hidden cases, with **no positive `ram_limit` on any of those 100**. Area, Delay and Runtime all matter, and the score formula is not specified in the project PDF. Small improvements on a repeatedly explored public bank are not evidence of hidden-score superiority.

This delivery contains C++17 source plus headers; see `STAGE2_SUBMISSION_README.md`. Compile with `g++ -O2 -std=c++17 -pipe -DNDEBUG src/synth_round85.cpp -o synth`; this command does **not** need former Round folders. Keep the source, build command, selected policy and report method consistent at actual Stage 2 submission.

## Where Issue #2 stands

Reply to your teammate **now**, marking its item 4 as OPEN. The integration-specific budget refund should be tested on their actual Stage 2 solver and original course cases. The standalone `integration/budget_ledger.hpp` and `tests/test_budget_ledger.cpp` show only a tested accounting contract, not the integration fix. Keep the GitHub Issue open until integrated testing and clean-checkout README are verified.

See `docs/05_R85_METHOD_AND_ABLATION.md`, `integration/ISSUE2_BUDGET_REFUND_CONTRACT.md`, `docs/06_TEAM_ISSUE2_REPLY.md`.

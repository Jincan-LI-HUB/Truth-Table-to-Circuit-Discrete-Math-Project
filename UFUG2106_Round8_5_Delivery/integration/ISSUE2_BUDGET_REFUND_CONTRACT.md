# Issue #2, item 4: Budget Reclamation in the Team's Integrated Stage 2 Solver

**Current status: OPEN / implementation not inspected.** The public GitHub main branch reviewed on 2026-11-22 did not expose the teammate's integrated Stage 2 solver, so this package cannot honestly state that the teammate's budget-handling bug is fixed. This is a testable proposal, not a patch to their source.

## Reproducer and claimed improvement

The teammate reports that, for modified Stage 2 case 005 with target delay `1,000,000,000` and runtime limit `1000 ms`, returning time previously earmarked for the Round 5.1 optional phase to the BDD phase improved area from `99,068` to `93,786`. Both the modified input and the integrated executable must be frozen to verify that observation; it is not the original benchmark score.

## Explicit accounting invariant

Let `L` be the positive program time limit, `R` be the output/exit reserve, and `Q` the amount set aside for Round 5.1 **if and only if Round 5.1 is eligible**. The BDD search deadline, as measured since program start, is

\[
D_{\mathrm{BDD}}=\max\{0,L-R-Q\,\mathbf 1_{\{\mathrm{R5.1\ admissible}\}}\}.
\]

When numeric limits mean Round 5.1 is *not* admissible, its reservation is `0`, not `Q`. Example `L=1000`, `R=80`, `Q=150` gives BDD deadline 770 ms when Round 5.1 is admitted and 920 ms when it is excluded. For `L=0`, no numeric deadline exists; this is represented by the sentinel `0` and must not accidentally mean zero time.

Test reference: `integration/budget_ledger.hpp`, `tests/test_budget_ledger.cpp`.

## Integration acceptance test

1. Freeze the integrated source and executable SHA-256, including the input and all policy variables.
2. Log eligibility for Round 5.1, actual spent time, reserved vs reclaimed budget, BDD start/deadline, completed candidate counts, and final area/delay.
3. Test both admissible and inadmissible R5.1 cases under *unchanged* course inputs first; evaluate the teammate's modified-target example in a separately labeled controlled ablation.
4. Preserve a feasible incumbent and a tail reserve, do not overrun a positive `runtime_limit`, and check against the evaluator.
5. Compare Area, Delay, Runtime and PASS under both Stage 1 and Stage 2. A candidate with better area but timeout is not an improvement.

Do not close GitHub Issue #2 or claim the integrated budget fix based solely on a successful unit test of the reference ledger.

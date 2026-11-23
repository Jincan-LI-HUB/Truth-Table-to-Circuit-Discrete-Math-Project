# Round 8.7 — Decision Gate, Limitations, Round 9 / 10

## Gate assessment

**PASS (local functional robustness):** 216/216 correct, 216/216 target met, 108/108 exact netlist-hash repeat pairs, frozen independent functions and compiler source.

**UNDETERMINED (quality generalization):** 0 Area/Delay differences on new synthetic cases, so the existing 36-function bank cannot tell whether extra SOP has an unseen-case area advantage.

**OPEN (time tail):** Short runtime inputs at `n=20` can exceed a synthetic 100-ms limit in the local environment even for simple functions, apparently due in part to reading a million-row truth table. This is not confirmed against the course grading server. Use `bash .../run_round87.sh --stress-only` to check with the provided genuine evaluator locally.

**PENDING (official baseline regression):** Course evaluator is not included in this environment. WSL full run must confirm Stage 1 and Stage 2 public outcomes for all three frozen strategies.

## Research priorities and stop conditions

1. **Round 9A — Library-Based Rewriting prototype.** Small cuts of 3–4 input variables, Pareto libraries by weighted Area/Delay and truth-table equivalence; carefully account for shared DAG/MFFC removability, no zero-cost deletion assumption. Prototype only if a control case shows a meaningful cut opportunity.
2. **Round 9B — Resubstitution with existing signals.** Candidate reuse of externally available nodes with topological safety, exact Boolean equivalence and full DAG re-evaluation. Optimize shared reuse only when it preserves Target Delay and reduces objective.
3. **Round 9 independent gate.** Must test new source on a **new, untouched, harder** externalized bank; avoid tuning the algorithm on Round 8.7's 36 cases. Require complete functional correctness, no public PASS loss, and acceptable runtime/peak RSS.
4. **Round 10 — Integrated submission** with teammate's Stage 2 solver, explicit BDD budget reallocation test for Issue #2, clean-checkout build, final report and rollback to frozen R8.6 Extra SOP if Round 9 offers no reliable improvement.

The TA says official public and hidden cases have no positive `ram_limit`, but still capture memory to identify scaling failures. Never treat total 48 GiB RAM as a per-process promise.

**Stop working on routine Root Cap tuning** absent a clear causal anomaly. Stop introducing rewriting changes before final submission if they cannot pass independent correctness, risk and public grade gates. One new well-tested transformation is better than multiple under-tested modes.

# Suggested GitHub Issue #2 Reply (Draft — not posted)

Thanks for the detailed reproducer and the integration findings. I agree that these are useful issues to track, and I checked the later standalone implementation against your list.

**Memory allocation and early exit:** The original Round 5.1 source remains frozen rather than being silently rewritten. Round 8.2.1 and subsequent standalone versions added early exit on a zero-area/zero-delay valid incumbent, plus positive-RAM admission checks and compact / bounded fallback paths. This reduces actual peak RSS in the 20-input direct-wire reproduction, but does not mean every large allocation in the general BDD path was eliminated or the team-integrated version already has the fix.

**Round 5.1 source and integration:** We plan to port the validated changes to the integrated Stage 2 code, preserve source hashes for historical experiments, and rerun the resource-focused tests. The TA's later announcement clarifies that none of the final 100 grading cases will set a positive RAM limit. We are still preserving resource safety as an engineering requirement rather than closing the issue based on that announcement.

**BDD budget restitution (still open):** Your finding that disabling the Round 5.1 stage should release reserved time back to BDD Search is sensible and worth a controlled integration ablation. Your 99,068 → 93,786 area result was obtained with modified target-delay / runtime settings, so we should also verify the change under the original public cases and both Stage banks. Our standalone Round 8.5 test of *Cut-stage* budget return was not consistently beneficial, but it is a different phase and does not invalidate your BDD proposal. We have written a simple budget-accounting contract and test for the team to adapt; the integrated source still needs independent validation.

**Reproducibility:** Round 8.5 now compiles from a fresh isolated directory with its own headers and an embedded frozen comparator, without relying on previous delivery folders. We should separately verify the team's eventual Git checkout and README with the exact submitted Stage 2 source.

I suggest we keep this issue open until the integrated BDD budgeting, low-memory path, and final checkout/build are all checked in the actual integration branch. Thanks again for the concrete test case and measurements.

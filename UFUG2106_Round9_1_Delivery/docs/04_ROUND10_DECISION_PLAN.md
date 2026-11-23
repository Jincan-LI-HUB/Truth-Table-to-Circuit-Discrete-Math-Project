# From Round 9.1 to Round 10: Decision plan

**Now:** Run the exact official paired experiment from `run_round91.sh` on the course WSL installation. Do not use local minima from the wall-clock-sensitive source to select the winner.

**Gate A (correctness):** 500/500 official public PASS and Target Met for five modes and two reversed runs. No assumption about hidden tests. If any mode fails, reject its promotion and diagnose using bundled logs.

**Gate B (performance):** Compare *casewise*, within the same stage/run: Area, Delay, runtime_ms (not only total Area), exact solved case count, and near-hard-limit Runtime. The new Library must outperform not just R9.0 but also the `repeat_sop` matched-resource control; a marginal-only public gain with no lockbox gain is not enough by itself.

**Gate C (production):** Do not enable `UFUG_R91_POLICY=library` in final submission unless Gate A and B clearly justify it. Currently `submission/synth.cpp` is a self-contained source-only implementation with the experimental module OFF by default. Historical frozen source and matched controls are testing code, not grading deliverables.

**If no robust library win:** Conclude R9.1 experimentally (negative result accepted) and skip conditional R9.2 unless a new, non-redundant resubstitution hypothesis is developed and its code can be independently verified within the remaining schedule. Prioritize Round 10:

1. Obtain and verify the team's *actual* integrated Stage 2 solver, not the standalone code.
2. Address Issue #2's BDD budget reallocation in the integrated source with paired tests and full runtime safeguards; the independent Round 8.x Cut Search experiments do not settle this BDD integration issue.
3. Merge only validated modules, remove research-only flag dependence from production, test cold build in a fresh Ubuntu environment, run both 25-case public banks and representative short-limit/large input fixtures.
4. Write the final mathematical rationale, ablations (including negative results), correctness, tradeoffs, experimental environment, and reproducibility artifacts.

Memory remains an engineering resource to profile, but no positive RAM limit is used in official public/hidden grading per TA announcement. Avoid sacrificing practical Area/Delay/Runtime solely to solve the unrelated 9000KiB evaluator anomaly.

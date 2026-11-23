# Open Issues and Scope Boundaries — Phase 0–2

## Must resolve before team submission / final manuscript freeze

1. **Candidate versus integrated source (P0):** R10.0's own `primary/03_frozen_candidate/README.md` explicitly states *"Independent solver candidate only. Not the teammate-integrated final Stage 2 release."* That status must not silently become "submitted team implementation." The team must confirm actual final integrated source, hash and supported README; re-run checks if files differ.
2. **Official all-50 baseline comparison (P0):** Recovered 300 matched observations from a prior WSL reproducibility batch and 100 default-R10 observations from R10 official feedback. The course truth-table files and evaluator are not present in this container, so this work cannot independently rerun the official 50-case evaluator here. Preserve run metadata and the existing matched CSV and validate comparability before writing final numbers.
3. **Runtime and RAM guarantees (P0):** The code is *budget-aware*, not a formally proven hard real-time or hard peak-RSS bounded algorithm. `r90` streaming bypass only proves an early output when its detection succeeds and delay is feasible. `r821` BDD admission is expressly conservative; early failure (exit 14) is possible when the fallback fails. Report guarantees narrowly and honestly.
4. **Research R5.1 local source (P1):** Stage 1 final trial log and GitHub record identify frozen `synth_round51.cpp` SHA-256 `cf90d0b110e6f45d1d508db351c95f10e7d704824fc34e17e6a5f5b783e20759`. Its code is available in the Stage 1 repository, but is not a separate mounted local source file in this audit package. Cite the reference source in the project study, do not relabel Zeyun's source as R5.1.
5. **Memory/CPU portability (P1):** Linux WSL GCC build/smokes are not a cold run on the instructor's Ubuntu 22.04.3 / AMD EPYC 7542. Rebuild in requested environment when available.

## Mathematical assertions requiring narrow wording

6. **Correct-by-construction versus verified software:** Shannon identity, formal cut-leaf exhaustive masks and legal gate identities are mathematical facts *conditional on implementation invariants*. These do not prove the entire C++ program error-free.
7. **Full gate accounting nuance:** `r51::Graph::metric()` sums every node stored in the graph; it does not perform reachability pruning. `Builder::finish()` and `run_synth` prune before candidate comparison. Hence write "mapped, pruned candidates are globally remeasured", not "metric automatically knows which nodes are live".
8. **Old required times after rewriting:** `r84cut` computes `needed` from the old graph to screen local candidates, but graph sharing/fanouts may change. Final accepted graphs undergo global delay checks; old required times alone are not a universal timing proof.
9. **Area improvement is not uniform:** Independent 20 fixture smoke evaluations include R10 results with larger area than Zeyun for several tiny functions. It is invalid to say R10 dominates every case. Source README warns about clock-dependent exploration.
10. **No improvement from larger time alone:** R8.6 factorial data are published-case observations under fixed configs, not a general theorem that time never helps. Preserve the exact scope.
11. **R10 final pass default:** Explicitly distinguish defaults: R8.6 `extra_sop` is the upstream policy, R9.1 `repeat_sop` is an *additional* default follow-up. Historical R8.3/R8.4/R8.5, R8.1/R8.2 etc. are source-retained opt-in experimental alternatives, not an unconditional sequence.
12. **If no declared time limit:** `limit=0` means no limit by the task contract, but several optional optimization branches use `limit>=1000` and consequently do not run. This is a source behavior, not a validity violation. Do not describe those optimizers as always running on every input.

## Not done by this phase

- No full report drafting, layout, statistical figure design or Stage 2 Q&A handout in this phase.
- No hidden-case validation; no exhaustive test for all 20-input functions.
- No attempt to optimize frozen C++ source or change its empirically chosen budgets.

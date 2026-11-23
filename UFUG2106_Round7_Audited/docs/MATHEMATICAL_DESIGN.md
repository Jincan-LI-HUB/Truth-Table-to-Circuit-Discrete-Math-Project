# Round 7 — Mathematical Design and Correctness

## 1. Upstream behavior and scope

Frozen Round 5.1 transforms a truth table into a ROBDD, Shannon-maps the graph, and optionally constructs Quine–McCluskey prime implicants plus greedy covers for each output with essential support at most nine. Several mapping candidates reuse the same cached cover plans. The final netlist is evaluated and may be balanced or area-recovered.

Round 7 changes **only two symbolic-cover kernels** and adds their profiling/ablation switches. It preserves supported functions, mapping candidate list and order, timing slack logic, gate costs and output formatting. An exact cover result can lead to a different *whole-program final choice* if additional candidates now fit within the wall-clock budget; that is a meaningful portfolio effect, not a change to the cover's mathematics.

## 2. Prime implicant merging

Represent cube `c=(mask,val)` with invariant `val & ~mask == 0`. Valid pairs at one Q–M level have identical mask and exactly one nonzero difference bit in their specified values:

`mask_a == mask_b` and `popcount((val_a XOR val_b) & mask_a) == 1`.

Because normalized values contain no bits outside the mask, the second condition is equivalent to the existence of a specified single bit `bit=2^j` such that `val_b = val_a XOR bit`.

**Original kernel:** compare all unordered pairs among `S_r` cubes per level, `O(S_r^2)` comparisons.

**Round 7:** hash `((uint64_t)mask << 32) | val` to cube index, then for each cube query the single-bit neighbors for every set mask bit. This requires at most `k*S_r` hash queries per level and expected `O(k*S_r)` work (under expected constant-time hashing).

Each original merge appears among the hash-neighbor probes; each matching hash neighbor meets the original merge criterion. `used`, the merged cube `(mask ^ bit, val & (mask ^ bit))`, and de-duplication remain unchanged. Final prime implicants are explicitly sorted and uniqued as before, independent of traversal order.

## 3. Greedy cover selection

Let `U` be the uncovered ON/OFF minterms and `P_t` the minterms covered by prime cube `t`. Round 5.1 computes:

`gain_t = |U intersect P_t|`

and scores a cube by:

`score_t = gain_t / (0.4 + max(1, popcount(mask_t)))`.

Round 7 stores `U` and each `P_t` in bit-vectors and computes the **same integer gain** by:

`gain_t = sum_w popcount(U_w & P_{t,w})`.

After selecting the best cube, uncovered minterms are updated via `U_w &= ~P_{t,w}`. The candidate iteration order, floating-point score expression, tie-breaking (`>` rather than `>=`), and selected-cube append order are unchanged. Therefore, by induction over greedy iterations, the chosen cube sequence is the same for any fixed prime set.

The `P_t` masks are constructed once (`O(P*Q)` in the current implementation), rather than comparing all prime/minterm combinations again at each greedy step; gain computation is `O(P*ceil(Q/64))` per iteration. `Q<=512` for supported `k<=9`.

## 4. Performance and correctness test protocol

1. `tests/test_exact_cover.py` generates an actual C++ compiler harness using the exact Round 7 snippets from `bootstrap_round7.py`. It randomly explores different input sizes, densities, all-constant functions, ON/OFF covers, and all four combinations of legacy/current kernels.
2. `tests/bench_cover_kernel.py CASE_FILE` times exactly these symbolic-cover kernels and verifies cube sequence identity for the input case.
3. Full synthesizer must be rebuilt from the frozen Round 5.1 source in the user's repository. `SOURCE_MANIFEST.json` tracks SHA-256 hashes and the upstream Git blob SHA.
4. The official course evaluator must run on **both Stage 1 and Stage 2** on identical WSL hardware; `tools/run_benchmarks.py` saves repeat outputs with alternating version order. Independent gate-netlist verification should supplement (not replace) official PASS.

Randomized tests provide empirical confidence; the arguments in §§2–3 establish the mathematical equivalence of the two kernel substitutions under the stated cube normalization invariant. They are not proofs that the entire solver meets a particular wall-clock deadline.

## 5. Intentional non-goals

- No new input-specific case-ID branches.
- No invented course grading formula or empirically unsupported score weights.
- No heuristics that remove available cover candidates.
- No Round 6.1 cut rewriting, yet: archived Stage 1 results suggest small Area gains with material runtime cost. That direction remains a separate future milestone subject to controlled experiments.
- No claim that output Area/Delay can **never** change: wall-time-limited portfolio search can complete different numbers of candidates after acceleration.

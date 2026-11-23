# Round 8.2.1 Mathematical and Systems Design

## 1. Input contract and why Round 8.2 fails

The course requires the seven base fields, with independent optional `runtime_limit` (milliseconds) and `ram_limit` (KiB). An absent or zero limit is unrestricted; to specify only RAM, the runtime token must be zero. R8.2 read only the runtime token and then entered `run_synth`, which uses an eager `orig(N)` permutation of `size_t`, `cur(N)` of `int`, an additional `next`, `nodes.reserve(N)`, `cache.reserve(min(2N,5e6))`, truth-table caches and graph buffers, with \(N=2^n\). For \(n=20\), `orig` alone consumes \(8\) MiB on x86-64, before other allocations. An optional-candidate admission check by itself is insufficient because the *first* BDD can already exceed a small cap.

## 2. A streaming constant/literal recognizer

For every output \(j\), maintain exactly the \(2+2n\) candidate functions

\[0,\quad 1,\quad x_0,\neg x_0,\ldots,x_{n-1},\neg x_{n-1}.\]

Stream the truth table once. Each observed assignment removes incompatible candidates. At end, any surviving candidate equals the specified output on *every* truth-table row, by exhaustive elimination. Build the outputs with direct signal references, constant zero or shared NOT gates, then perform a full DAG metric check before emission. Memory is \(O(mn)\), independent of \(2^n\), apart from the input text buffer. A zero-Area, zero-Delay network is globally optimal when all gate-area costs are positive.

## 3. Packed semantic truth table and affine detection

If the literal recognizer cannot realize all outputs and the RAM cap is tight, store each output as a packed bitvector of \(\lceil2^n/64\rceil\) 64-bit words, provided the packed storage uses at most one-sixth of the declared memory cap and at most 8 MiB. Compare this with the eager `orig`/`cur`/BDD allocation chain.

An affine function over \(\mathrm{GF}(2)\) must satisfy

\[f(x)=c\oplus\bigoplus_{v=0}^{n-1} a_vx_v,\quad c=f(0),\quad a_v=f(e_v)\oplus f(0).\]

These coefficients are *uniquely determined*. Verify this identity against **all** \(2^n\) rows; only then synthesize the XOR tree using permitted AND2/OR2/NOT gates. The balanced priority-queue reduction lowers delay relative to a serial chain. This catches high-support parity/affine functions that a ten-variable support restriction cannot capture.

## 4. Exact support-restricted Shannon fallback

An input \(x_v\) is irrelevant to output \(f\) iff for every assignment of all other inputs, toggling \(x_v\) leaves \(f\) unchanged. Check this condition against all pairs of truth-table rows. Do so **per output**: different outputs may have disjoint supports even when their union exceeds ten.

For a supported output with at most ten semantic support variables, evaluate the reduced truth table and apply Shannon expansion recursively:

\[f=(\neg x_v\land f_{x_v=0})\lor(x_v\land f_{x_v=1}).\]

Use constant propagation and structural hashing, followed by associative rebalancing. A cut variable omitted from the support can be fixed arbitrarily without changing the function, so reduced-table lifting is exact. The final network is measured under the *actual input costs* and accepted only if its global delay does not exceed `target_delay`.

## 5. Memory-bounded packed ROBDD fallback

For functions depending on more than ten variables and not recognized as affine, process the packed original truth table bottom-up. At the last variable, map every pair of truth bits to a Boolean terminal or canonical BDD node; at each preceding variable merge adjacent references. Hash a node by \((v,lo,hi)\), reusing identical children and eliminating `lo=hi`. This constructs the same reduced ordered BDD semantics by induction on the eliminated suffix, but unlike the old builder:

- it does **not** allocate a length-\(2^n\) `size_t` row permutation;
- it never reserves \(2^n\) BDD nodes or \(2^{n+1}\) hash buckets ahead of time;
- the peak row buffers cost approximately \(3\cdot2^n\) bytes across the two integer vectors;
- a deterministic node cap is derived from the declared RAM limit (allowing conservative fixed overhead and estimated bytes per retained node).

After building the reduced DAG, recursively implement nodes by exact Shannon identities with constant simplifications. Rebalance associative cones to improve delay, then measure the complete network and validate its declared target. Exact equivalence follows by induction from bit terminals through BDD nodes and through the gate mapper.

**Important:** the `240 bytes/node` guard and fixed-memory reserve are engineering admission estimates, not a verified allocator upper bound for every C++ standard-library implementation. A failed node cap returns a diagnostic rather than launching an unbounded alternative. This is not complete synthesis under all positive RAM constraints.

## 6. Eager-BDD admission and portfolio stop

A conservative memory estimate is

\[\widehat M=3\mathrm{MiB}+2^n(m+104)\ \mathrm{bytes}.\]

This is deliberately pessimistic for several inputs, because the frozen eager BDD maintains simultaneous row buffers, nodes, hash buckets, affine cache and truth-table storage. The estimate is used to decide whether the *unmodified* full search path should be attempted. When the RAM limit is positive and below \(\widehat M\), the compact low-memory paths are tried. If none can return a legal circuit, the solver exits with code 14 and a machine-readable diagnostic. When the cap is positive and less than \(2\widehat M\), optional follow-up BDD candidates are skipped after a feasible incumbent has been obtained.

No claim is made that \(\widehat M\) upper-bounds actual peak RSS. Both the evaluator's positive memory limit and direct OS peak measurements must be checked. No gate-count, area, delay or runtime score can be computed from a failed case as if it had passed.

## 7. Correctness obligations and proof limitations

1. **Streaming preflight:** every output candidate was verified on all rows, so its Boolean mapping is exact.
2. **Affine:** coefficients are uniquely fixed, and the candidate is checked on the entire original truth table before being emitted.
3. **Reduced support:** exhaustive pair checks prove independence, and Shannon decomposition is an identity.
4. **Packed ROBDD:** terminal truth bits, node hash-consing and Shannon mapping preserve the original output by structural induction.
5. **DAG:** only earlier node IDs are referenced, and `Builder.finish` drops dead nodes while remapping IDs in topological order.
6. **Timing:** candidate is emitted only after complete graph metric check; all tests also use an independent exhaustive verifier.
7. **Resource limitation:** static admission estimates are a precaution, not an absolute in-process memory enforcement primitive. Resource success must be determined from the official evaluator and empirical per-process RSS checks. The algorithm may decline some feasible inputs; true memory-complete synthesis is not achieved.

## 8. Experiment design

Keep all existing Round 8.2 variants unchanged. Compare frozen and patched binaries using identical environment policies and two reversed-order runs on both released stages. Separately test RAM-only, combined/nonzero limits, pure literals, low-support nontrivial functions, full-support affine functions, and full-support nonaffine functions. The official evaluator's output takes precedence over direct RSS or test-verifier results.

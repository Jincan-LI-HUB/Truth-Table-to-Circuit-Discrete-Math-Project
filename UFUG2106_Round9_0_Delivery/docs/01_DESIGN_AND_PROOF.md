# R9.0: Algorithmic design and correctness proof

## Non-invasive default change

The original R8.6 standalone source is preserved byte for byte. The new solver changes the default for the policy-selection expression from `baseline` to `extra_sop`. Explicit research overrides remain possible. No ranking or rewriting rules are changed.

## Streaming signatures

Truth-table row `r` represents assignment `x_0...x_{n-1}`, most significant first. On the *first and complete* sequential input pass, maintain a constant/literal candidate bitset for each output, and maintain an affine coefficient vector `c_j` for each output:

\[
 f_j(r)=a_j\oplus\bigoplus_{k=0}^{n-1}c_{jk}x_k(r).
\]

`a_j=f_j(0)`. At every power-of-two index `2^b`, the previously unobserved basis coefficient is fixed to `c_{jb}=f_j(2^b) xor a_j`. For every other row `r`, all its set-bit coefficients have already been observed, because every power-of-two component of `r` is strictly smaller than `r`. Thus comparing the predicted affine value against each observed truth-table output proves or disproves global affine equivalence with *no stored truth table*. The literal bitset tests the independent constant/`x_k`/`NOT x_k` candidates at **every** row. No sampling is involved.

The accepted affine implementation builds each XOR using only the permitted gates:

\[
 u\oplus v=(u\lor v)\land\neg(u\land v).
\]

The builder structurally hashes gates, builds an acyclic DAG and emits only live nodes. Its metric computes exactly the per-gate weighted area and maximum arrival time. The bypass is accepted only when the constructed graph is valid and meets the supplied Target Delay. Otherwise control returns to the frozen synthesis process.

The bypass applies only when `n>=18` and a **positive** `runtime_limit` is no more than 250 ms. For all other cases it only adds a small amount of `StreamProbe` initialization; normal synthesis remains available. No change to any input's limits is made.

## Complexity and trade-offs

The streamed affine signature uses O(nm) bits plus O(m) metadata. The candidate graph occupies O(nm) nodes in an unconstrained multi-output affine case, before structural sharing. Computing literal match masks costs O(n) for rows while some candidate remains; otherwise the arithmetic affine check costs O(m) per row. The *mandatory* input scan remains O(m*2^n) characters, so 100 ms cannot be promised on slower filesystems or machines.

The streaming affine implementation is a fast safe representation, not a claim of minimum area. On a positive short deadline, it may return a larger circuit than the long-budget BDD search. This is an explicit Runtime–Quality trade-off, not a correctness trade-off.

## Independent verification

The embedded `verify_exhaustive.cpp` independently parses all emitted gates, checks acyclicity and signal references, and evaluates every one of the `2^n` assignments. The verification runs on the canonical case file, not on a sampled subset.

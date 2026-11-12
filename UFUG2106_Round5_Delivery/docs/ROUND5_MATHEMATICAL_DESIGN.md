# UFUG2106 — Round 5: Reuse of Boolean Structures and Efficient Candidate Evaluation

**Status:** Engineering optimization of Round 4.1 Balanced.  
**Scope:** Same input Truth Table, same AND2/OR2/NOT target library and same search objectives.  
**Correctness claim:** The transformations introduced in this round do not change a Boolean function or the intended candidate-ranking rule. Validity is additionally checked by the official evaluator and an independent simulator.

## 1. Motivation: repeated work inside one synthesis invocation

Our Round 4.1 Balanced synthesizer constructs several candidate circuits for the same input case. In the first five options, the variable ordering is predominantly `influence-desc`; multiple mapping options then use this **same ordered ROBDD**. In addition, for small functions the Prime Implicant enumeration and Greedy Cover are repeated for each candidate, even though they depend only on the underlying truth table. Finally, each candidate's textual Netlist is repeatedly parsed for Area/Delay assessment. These are three different kinds of duplication.

The objective is not to change the circuit optimization problem, but to lower the cost of solving it:

\[
\min_{C\equiv f}\ A(C)
\quad\text{s.t.}\quad
D(C)\leq D_{\mathrm{target}},\quad
T_{\mathrm{synthesis}}\leq T_{\mathrm{limit}}.
\]

The official output-check validity (`PASS`), meeting the delay target (`target_met`), and the runtime limit are distinct measurements. Aggregate Area over 25 cases is descriptive, not an unpublished instructor score.

## 2. Immutable ROBDD cache

### 2.1 Mathematical representation

Let \(\pi\) be a fixed permutation of the input variables and let \(f_j\) denote output \(j\). Shannon's identity states

\[
f_j=\neg x_{\pi(k)}\land (f_j)_{x_{\pi(k)}=0}\;\lor\;
 x_{\pi(k)}\land (f_j)_{x_{\pi(k)}=1}.
\]

A reduced ordered Binary Decision Diagram (ROBDD) shares nodes with identical `(level, low child, high child)` and eliminates a decision when the two cofactors agree. This implementation also normalizes complemented edges (one bit of the returned reference) so that complementary functions share one graph node. Fixed input, variable order, canonical node normalization and interning procedure determine the same ordered graph **independently of the later mapping policy**.

Let

\[
G(f,\pi)=(V,E,\text{root}_0,\ldots,\text{root}_{m-1})
\]

be the BDD DAG and its output roots. Given a mapping parameter \(\theta\), the actual circuit is computed as

\[
C_{\pi,\theta}=\operatorname{Map}(G(f,\pi),\theta).
\]

For a collection \(\theta_1,\ldots,\theta_k\), it is unnecessary to recompute \(G(f,\pi)\) each time.

### 2.2 Correctness by referential transparency

BDD Construction is a deterministic function of `(truth table, variable order)`. We cache the completed BDD only; each Gate Mapper receives an immutable view of the node table, permutation, root references and precomputed affine masks. The Mapper still allocates its **own** gates, Structural Hash Table, Arrival Times, complemented literals and output Netlist.

Therefore, under identical input and ordering:

\[
\operatorname{Map}(\operatorname{BuildBDD}(f,\pi),\theta)
=\operatorname{Map}(\operatorname{CachedBDD}(f,\pi),\theta).
\]

This is an equality of the complete intermediate graph, not merely a claim that the two representations compute the same Boolean function. It follows that no candidate change is required, provided caching does not cross input files or incompatible variable orders. The code caches only the repeated `influence-desc` ordering and retains it when \(n\le18\) and the BDD has at most 80,000 nodes; otherwise it reconstructs normally. The cache is per process; the program is invoked once per case.

The affine mark for a node represents either a sentinel for non-affine subfunctions or a bit mask for a function of the form

\[
 c\oplus\bigoplus_{i\in S}x_i,
\]

and depends only on the graph and original input variable indices. Therefore it is safe to cache together with the graph.

### 2.3 Complexity and memory tradeoff

If one BDD build costs \(T_B\), one mapping costs \(T_M(\theta)\), and we test \(k\) mapping options for the same \(\pi\), then the relevant contribution changes from

\[
kT_B+\sum_{i=1}^kT_M(\theta_i)
\quad\longrightarrow\quad
T_B+\sum_{i=1}^kT_M(\theta_i).
\]

This ignores small cache lookup overhead. **It does not imply a proportional reduction of total runtime** when Gate Mapping and post-processing dominate. The resident BDD consumes \(O(|V|)\) additional memory; capping the cached node count avoids unbounded duplication while another variable order is built. Other orderings are not interchangeable.

## 3. Symbolic Implicant Cover cache

### 3.1 Essential support and a Boolean cube

For output \(f_j\), a variable \(x_i\) is essential iff

\[
(f_j)_{x_i=0}\not\equiv(f_j)_{x_i=1}.
\]

Let \(S_j\) be the essential support and \(k_j=|S_j|\). An implicant (cube) specifies a subset of the support literals; it may use either polarity for each specified input and omit the others.

The existing small-support algorithm applies a Quine–McCluskey-style merging step and selects a greedy cover for \(f_j=1\) (SOP) and for \(f_j=0\) (which can be complemented to obtain a POS-like realization). The greedy cover is **not guaranteed minimum**, but every selected cube is an implicant of the specified ON-set, and the union covers every ON-set minterm. Therefore the resulting SOP equals the target Boolean function.

### 3.2 Why the cover can be reused

The selected symbolic cubes depend only on

\[
(f_j, S_j, \text{deterministic greedy tie-breaking}),
\]

not on how AND2, OR2, and NOT gates are priced or mapped. The Round 5 cache stores for each output and target polarity: `(support, selected val/mask cubes, constant/unsupported flag)`. Candidate-specific gate creation still uses the original algorithm, current Structural Hashing, Arrival Times, and complementary signal handling.

Thus, the symbolic `Cover(f_j, goal)` is computed once, while `GateMap(Cover, candidate)` is carried out independently for each candidate. For a function exceeding the previous threshold \(k_j>9\), the cover remains unsupported; for \(n>13\) the entire Implicant method is disabled as before. The exact generation, sorted-prime ordering and greedy scoring rule were preserved.

### 3.3 Important limitations

The Quine–McCluskey prime enumeration may have exponential worst-case complexity; this is one reason the existing algorithm restricts \(k_j\le9\). Caching removes repeated enumeration but does not improve that worst-case bound. The stored cover is a set of candidate terms, not a certificate of globally minimum hardware Area or Delay.

## 4. Remove a provably duplicated candidate

In Round 4.1, candidates `i=0` and `i=2` have exactly the same variable order, `fast`, `rewrite`, `expand`, `margin`, and `affine` settings. Their only difference is `cubemode=1` versus `cubemode=0`. However, the source performs Implicant Cover only if

\[
\texttt{cubemode}\ne0\quad\land\quad n\le13.
\]

For \(n>13\), this condition is false in both candidates, so their BDD construction, Gate Mapping and final Netlists are identical. The second execution is skipped. No potentially different candidate is removed for \(n\le13\).

**Caveat:** The total elapsed time changes, so a wall-clock-based search cutoff may allow additional candidates on a machine near its budget. Such timing-driven search behavior is not a mathematical invariant even though the removed candidate itself was duplicate. The actual 25-case output comparison verifies the observed effect.

## 5. Fast Netlist evaluator

For a gate \(g\), define the arrival time recursively:

\[
T(g)=\begin{cases}
T(a)+d_{\mathrm{NOT}}, & g=\neg a,\\
\max\{T(a),T(b)\}+d_{\mathrm{AND}}, & g=a\land b,\\
\max\{T(a),T(b)\}+d_{\mathrm{OR}}, & g=a\lor b.
\end{cases}
\]

Inputs and constant zero have arrival time zero. The circuit delay is \(D(C)=\max_j T(\mathrm{out}_j)\) and its Area is the sum of the emitted gate areas, one contribution per gate.

The older implementation used an `istringstream`, many short `string` allocations and `stoi` to parse *every gate line* whenever a candidate was scored. Round 5 replaces this with a one-pass pointer-based parser of our own generated Netlist grammar, while retaining consecutive-ID, fan-in, output-count, and gate-type checks. It computes exactly the same recurrence and aggregate Area.

Both evaluators take \(O(L+G)\) time for input text length \(L\) and \(G\) gates, but have different constants and allocation behavior. The faster implementation is not a new Boolean simplification; it is a lower-overhead exact metric evaluator.

## 6. Proof obligation and independent evidence

1. A fixed variable ordering produces the same BDD whether a previously computed immutable graph is reused or rebuilt.
2. The greedy symbolic covers are independent of candidate mapping policy; their selected literal sets and order are preserved.
3. The eliminated candidate is an exact duplicate only in the guarded region \(n>13\).
4. Both score parsers use the same Area and Arrival recurrence on the same emitted gates.
5. Each synthesized Netlist must still be accepted by the authoritative evaluator; for small \(n\), independent exhaustive simulation checks all input assignments, and for larger \(n\) deterministic sampling checks additional assignments.

**Observed on one completed set of the 25 released cases:** all 25 Netlist files were byte-for-byte identical to the user's frozen Round 4.1 Balanced local outputs; all official cases passed and met Target Delay. In a separate rerun, a time-cutoff-sensitive case (`case_022`) selected a different, valid circuit (Round 4.1: Area 1334 / Delay 32; Round 5: Area 1320 / Delay 31). This does not contradict the fixed-candidate graph equivalence argument: the number of candidates finished before a wall-clock cutoff can change. The independent verifier separately validated 25/25 output files. This supports—but does not mathematically guarantee—general hidden-case performance or strict runtime limits.

## 7. Runtime constraints and future work

The existing search budget checks before expensive candidates and inside some ROBDD work. It is **not a formal hard-real-time bound** on a single noninterruptible Gate Mapping or post-processing step. The node cap limits only cached BDD retention, not the full worst-case synthesis memory footprint. These remain active research problems.

For the next stage, promising work includes (a) reusing partial Gate Mapping across mapping modes without mixing mutable node IDs; (b) replacing parse-serialize-parse passes in Rebalance / Area Recovery with a typed in-memory Netlist; (c) incremental timing and Area updates; and (d) using any verified runtime savings for richer cut-based rewrites while preserving a safe fallback.

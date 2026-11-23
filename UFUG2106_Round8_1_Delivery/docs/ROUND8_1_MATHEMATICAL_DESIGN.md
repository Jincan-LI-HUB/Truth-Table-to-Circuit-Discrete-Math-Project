# Round 8.1 — Mathematical Design and Limitations

## 1. Research problem and objective

Let a case supply a multi-output Boolean map \(F:\{0,1\}^n\to\{0,1\}^m\), gate library \(\mathcal L=\{\mathrm{AND2},\mathrm{OR2},\mathrm{NOT}\}\), gate-area costs \((a_\land,a_\lor,a_\neg)\), gate delays \((d_\land,d_\lor,d_\neg)\), and target \(D^\star\). A legal gate DAG \(G\) has live-node area and maximum output arrival

\[
A(G)=\sum_{v\in\mathrm{Live}(G)}a_{\operatorname{op}(v)},\qquad
D(G)=\max_{o\in\mathrm{Outputs}}t(o),
\]

with primary inputs and the constant 0 at arrival 0, and

\[
t(v)=d_{\operatorname{op}(v)}+\max_{u\in\mathrm{Fanin}(v)}t(u).
\]

The optimization is multi-objective: minimize \((A,D,T)\) subject to equivalence, resource limits and legality. **We do not know the official exact scoring function.** Consequently, we expose an area-priority branch (respecting \(D\le D^\star\)) and a strict branch (respecting \(D_{new}\le D_{base}\)), rather than falsely claiming one always scores higher.

## 2. Why Round 8.0 was incomplete

Round 8.0's algebraic rewrite recognizes explicit patterns such as \(x\wedge(y\vee z)\). Two logically equivalent cones can have very different syntax, even after structural hashing and complemented-polarity rewrites. An algebraic pattern search can therefore fail despite the existence of a better small-function realization. In the frozen public experiment Round 8.0 improved only Stage 2 `case_021` by 55 area units, increasing delay from 69 to 70, and no other public case. This **does not** refute cut-based rewriting; it only bounds the old *candidate generator*.

## 3. A cut is a formal Boolean interface

For node \(v\), a **feasible cut** \(C=\{\ell_0,\ldots,\ell_{k-1}\}\) intercepts every backward path from \(v\) to a primary input/constant. Here \(2\le k\le4\) for resynthesis. Each leaf is treated as an *independent formal Boolean variable*, even if the actual leaf signals correlate in the original circuit. The cut truth function is

\[
f_{v,C}(s)=\operatorname{Eval}\left(v;\ell_i\mapsto s_i\right),
\quad s\in\{0,1\}^k.
\]

Its truth mask \(M_{v,C}=\sum_{s=0}^{2^k-1} f_{v,C}(s)2^s\) fits in 16 bits at \(k=4\). The code evaluates it by memoized recursion over the old DAG; if any primary input is encountered without a blocking leaf, the cut is rejected. This is an exact function evaluation, not random sampling.

**Lemma (local substitution).** If an expression \(h(\ell_0,\ldots,\ell_{k-1})\) agrees with \(f_{v,C}\) for all \(2^k\) formal assignments, replacing \(v\) by \(h\) preserves its output under *every* actual primary-input assignment.

*Proof:* For every primary-input assignment, the actual leaf values define one assignment of formal cut variables. The two expressions agree there. Structural induction along every downstream path preserves all circuit outputs. ∎

## 4. Candidate generation: two complementary families

**4.1 SOP/POS prime cubes.** A cube is represented by fixed-bit mask \(q_m\) and value \(q_v\). Cube coverage is \(S(q)=\{s:(s\wedge q_m)=q_v\}\). An implicant of truth mask \(M\) satisfies \(S(q)\subseteq\mathrm{On}(M)\). It is *prime* when dropping any fixed literal would include an off-set assignment. The implementation enumerates up to \(3^4=81\) cube shapes, tests primeness exhaustively, then greedily chooses cubes to cover all on-set assignments. Two deterministic policies vary the literal-cost heuristic. The POS dual runs an SOP on \(\neg f\), followed by a NOT.

Every generated cover is sound (no off-set assignment is covered) and complete (the uncovered on-set is reduced to the empty set). Hence the emitted circuit computes exactly \(f\), whether or not the greedy cover is minimum.

**4.2 Shannon family.** Given formal cut variable \(x_j\),

\[
f=(\neg x_j\wedge f|_{x_j=0})\vee(x_j\wedge f|_{x_j=1}).
\]

The implementation recursively evaluates cofactors using several cyclic variable orders, then maps MUX-like structures into permitted gates with structural hashing and constant propagation. Each cofactor is exact by construction. Different variable orders produce distinct structures and different arrival times/costs. A fully exhaustive search over every variable ordering is **not** claimed.

The two families do not commute with DAG context: an SOP cone might reuse a shared AND term, while a Shannon cone might reveal a simpler timing path. Simple node-wise mixing can be worse than applying each family to an independent whole-graph branch.

## 5. Timing constraints and local cost approximation

For every original output \(o\), set the required time \(r(o)=D^\star\). For an original DAG predecessor \(u\),

\[
r(u)=\min_{v:\,u\in\mathrm{Fanin}(v)}\left(r(v)-d_{\operatorname{op}(v)}\right).
\]

An alternative is locally admissible only if its constructed arrival \(t_{alt}(v)\le r(v)\). This uses the *original* graph's required times; it is a conservative filter for many local replacements, not a substitute for checking the rebuilt global timing graph.

Old gates with multiple external fanouts cannot be assumed to disappear just because one root is rewritten. Define a conservative reclaimable area \(R(v,C)\) as the weighted area of the private old cone bounded by cut leaves, stopping at nodes with \(\mathrm{fanout}>1\), except at root \(v\). For candidate \(h\), estimate its cone cost \(K(h,C)\) relative to the mapped leaves. A default local replacement is considered when

\[
K(h,C)-R(v,C)<0.
\]

An exploratory `choices` mode also permits equal-cost local substitutions. This local inequality is merely a screening heuristic: new gates may be shared with other outputs, and old cones may have additional consumers. **True acceptance always uses the full live-DAG metric after pruning dead gates.**

The implementation's conservative `private_reclaim` check was added after an initial development experiment naively counted shared gates as free to reclaim, causing some whole-graph area regressions. Both positive and negative measurements are retained in the evidence.

## 6. Bounded structural choices, not full choice-network synthesis

Each structural branch starts from the same frozen incumbent, and constructs its own fully mapped candidate graph:

- `SOP`: two greedy cover policies and the complement dual.
- `Shannon`: up to four variable-order rotations.
- `All`: the union of both families *within one node-wise greedy pass*.
- `Choices`: local equal-cost choices are also permitted.

At the end we compare only **complete, semantically correct DAGs** using declared gate-area weights and delay. The `branch` policy evaluates independent `SOP`, `Shannon`, and `All` output graphs; the final chosen output is the best legal complete result, not necessarily the result of greedy mixing. This is a bounded *multi-start* form of structural choice; no e-graph, global Boolean choice network, or equality saturation is implemented.

**Why alternatives may be complementary:** Once graph rewriter A modifies the sharing structure, a rewriter B may discover a new opportunity. Sequential application and independent-branch selection are distinct control experiments; neither is guaranteed to dominate the other.

## 7. Formal correctness and acceptance theorem

**Theorem.** Suppose the old incumbent is a legal DAG implementing \(F\). If (i) every local cut alternative has exactly the enumerated truth mask, (ii) the new builder produces a valid topologically ordered AND2/OR2/NOT graph, (iii) the final graph has been garbage-collected and recomputed, and (iv) a new graph is accepted only if its complete computed area/delay satisfy the chosen gate, then the returned circuit remains functionally equivalent to \(F\) and satisfies that gate.

*Proof sketch:* By the cut-substitution lemma, induction through the DAG shows Boolean equivalence. The `Builder` emits existing permitted operations in topological order and rewires outputs through its mapping; `Builder::finish` traverses live gates and renumbers them. The exact metric checks area and delay of the resulting live DAG; rejecting any invalid or non-improving alternative leaves the previous incumbent unchanged. Therefore a return value is a legal semantically equivalent incumbent. ∎

This is not a proof of globally minimum area or delay. The conservative cut subset and local value estimate exclude many possible improvements.

## 8. Resource bounds and failure scenarios

Cut size is bounded \(k\le4\), retained cuts \(\le9\) per gate, and examined roots \(\le2,500\) per pass (deterministic stride over topological nodes). For k=4, each full truth table contains 16 assignments and the raw cube enumeration contains at most 81 cubes. Local computation is finite, but cut-set propagation is performed over the whole DAG, so the optimization can still be expensive on large circuits.

The implementation budgets each branch by at most \(\min(160\mathrm{ms},0.065 L)\) and the combined cut phase by at most \(\min(450\mathrm{ms},0.16L)\), where \(L\) is the declared runtime limit in ms. It starts only when \(L\ge1000\) and elapsed synthesis time is less than 71% of \(L\). Cooperative checks at regular root intervals are pragmatic, not formal hard real-time deadlines; the rest of synthesis and process startup remain additional work. Official evaluator measurements are essential.

**Limitations:** bounded root sampling, cut ranking bias, no exact multi-output factoring, no SAT exact synthesis, incomplete use of divisor reuse, approximate local reclaim, full-network rebuild cost, no memory formal bound, no universal improvement guarantee. A candidate can be equivalent but inferior in weighted cost; it is then rejected.

## 9. Pareto and grading ambiguity

For area-priority, accept \(A_{new}<A_{best}\) with \(D_{new}\le D^\star\). In strict mode additionally require \(D_{new}\le D_{parent}\). Both configurations are retained because the scoring formula is not provided in the project PDF; Delay increases within the target may still reduce the official grade.

For empirical reporting, distinguish functional PASS, target met, pairwise weighted-area improvement, delay-regression cases, runtime headroom, and valid Pareto improvements. A drop in total passed-case area caused by a FAIL is **not** counted as improvement.

## 10. Research anchors (not exact code transfers)

- Berkeley ABC public project: https://github.com/berkeley-abc/abc
- Mockturtle cut enumeration: https://mockturtle.readthedocs.io/en/latest/algorithms/cut_enumeration.html
- Mockturtle rewriting: https://mockturtle.readthedocs.io/en/latest/algorithms/rewrite.html
- Mockturtle resubstitution: https://mockturtle.readthedocs.io/en/latest/algorithms/resubstitution.html
- Mishchenko et al., DAG-aware rewriting and balancing (DAC 2006): https://people.eecs.berkeley.edu/~alanmi/courses/2007_290N/papers/synthesis_berkeley_dac06.pdf
- Davis et al., *Standardizing Boolean Transforms* (2024): https://people.eecs.berkeley.edu/~alanmi/publications/2024/tech24_resub.pdf

These are methodological references; the actual code and claims are grounded in this implementation and our own tests. No claim of matching ABC or mockturtle benchmarking performance is made.

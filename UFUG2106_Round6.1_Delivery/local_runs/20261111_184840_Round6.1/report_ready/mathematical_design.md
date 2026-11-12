# Round 6.1 — Budgeted, Cached Cut-based Boolean Rewriting

**Research status:** controlled follow-up to the Round 6.0 prototype. The Round 5.1 and Round 6.0 sources are included as frozen comparisons. Round 6.1 uses the same permitted `AND2`, `OR2`, `NOT` library and the same full-truth-table input/evaluator contract.

## 1. Motivation and scope

Round 6.0 demonstrated that rewriting a small local Boolean subfunction can lower the complete DAG area; however, it spent excessive computation repeatedly enumerating the same symbolic prime-implicant covers and creating candidate gates. Round 6.1 **does not enlarge the cut size or add new Boolean operators**. The key constraints fixed before the final holdout run are:

- Cut size \(k\leq4\), at most ten retained cuts per node, at most 4,000 examined live roots.
- A separate **25 ms wall-clock budget** for the cut postprocessor, additionally restricted by 6% of the input's stated synthesis limit (at least 5 ms). This does *not* bound the whole synthesizer to 25 ms.
- Conservative local estimates and **exact global** area/timing measurement; the Round 5.1 incumbent remains valid even when a cut search is stopped.
- Generic structural prioritization and cache keys based on local truth functions, with no names or positions of Stage 1 cases in any decision rule.

## 2. Formal four-feasible cut

Let \(G\) be an acyclic gate network and \(v\) an internal gate. A set of upstream nodes \(C\) is a cut for \(v\) when every backward path from \(v\) to a primary input crosses \(C\). We retain \(|C|=k\leq4\) and interpret the values of the leaves \(x_0,\ldots,x_{k-1}\) as independent *formal Boolean variables*. This does not assume their real circuit signals are statistically or logically independent.

For any assignment \(s\in\{0,1\}^k\), evaluate the original cone using its AND/OR/NOT operators to obtain \(f_{v,C}(s)\). The complete mask

\[
M_{v,C}=\sum_{s=0}^{2^k-1} f_{v,C}(s)2^s
\]

specifies the cut function exactly and takes at most 16 bits.

## 3. Symbolic implementation cache

The old engine repeatedly computed an implicant cover for the same function under many different cut roots. In the new engine, the symbolic cover is memoized under

\[
K=(k,\;M,\;p),\quad p\in\{0,1\},
\]

where \(p\) selects one of two deterministic greedy implicant-cover policies. A *cube* stores only a fixed-variable mask, a value mask, its covered-minterm mask and its literal count.

**Key correctness condition:** the cache stores no Gate IDs, arrival times, fanout values or node indices. The same formal \(k\)-variable truth mask and policy always produce the same ordered symbolic cubes; a new emitter maps formal literal \(x_i\) to the actual \(i\)-th cut leaf for each root. Consequently, cached cube reuse changes computation cost but not the Boolean function or allowed-gate realization of any fixed candidate.

A reversed-logic POS candidate uses the mask of \(\neg f\) and a final NOT, so it is cached separately from an SOP of \(f\). Input permutation is *not* silently identified: the order of cut leaf IDs defines the formal variable positions and is reflected by the truth mask.

The code's packing of the cache key uses disjoint bit fields for \(k\), \(p\) and \(M\), where \(M<2^{16}\). This guarantees no key collision within the specified domain.

## 4. Generic structural priority

The old traversal sorted feasible cuts by number/IDs of boundary leaves; Round 6.1 instead evaluates a conservative reclaimable-area score

\[
R(v,C)=\sum_{u\in P(v,C)} a(u),
\]

where \(P(v,C)\) consists of \(v\) and recursively private predecessors up to the cut boundary, stopping whenever a predecessor has an external fanout. The area weights \(a(u)\) are the declared gate costs. Cuts with \(R\leq0\) are ignored; remaining alternatives for a single root are tried in nonincreasing \(R\) order.

This priority is not a proof of improvement: a candidate may need more gates than can be reclaimed. It only decides search order when a strict per-instance time budget might expire. We leave the original root traversal topological so substitutions always reference already processed predecessor signals.

## 5. Local candidate generation and acceptance

For each tested cut, candidate representations are unchanged from Round 6.0:

1. Greedy prime-implicant SOP under two fixed policies.
2. Complemented SOP / POS duals.
3. Factoring one common literal out of a group of SOP or POS terms.
4. Two fixed Shannon decomposition orders.

Each candidate is constructed with structural hashing. A conservative estimate compares the actual gate cost in its local cone against \(R(v,C)\) and accepts only an improvement satisfying

\[
\Delta A_{\mathrm{local}}<0,
\qquad T_{\mathrm{new}}(v)\leq T_{\mathrm{old}}(v).
\]

**Important limitation:** global gate sharing may prevent a local estimate from being exact. Speculative gates from rejected rewrites are not considered free in the candidate cone-cost computation.

Finally the entire output graph is garbage-collected and ranked with the declared costs. It replaces the previous incumbent only if

\[
A(G_{6.1})<A(G_{\mathrm{incumbent}})
\quad\text{and}\quad
D(G_{6.1})\leq D_{\mathrm{target}}.
\]

The source returns the Round 5.1-based candidate unchanged otherwise. This is an *intra-run* safety property; outputs of separate timed runs can differ because earlier portfolio candidates can also depend on wall-clock cutoffs.

## 6. Correctness argument

**Lemma 1.** Evaluating the gate cone bit-parallel on the cut variables produces the same local Boolean function as the original circuit, for all possible cut-leaf assignments. Proof: structural induction over the AND/OR/NOT DAG.

**Lemma 2.** All candidate SOPs, complemented SOPs, factored forms and Shannon forms compute that same function. Proof: prime-implicant covers exhaust the on-set and contain no off-set minterms; complementation, Boolean distributivity and Shannon expansion are identities.

**Lemma 3.** A symbolic cube fetched from the cache is identical to the cube generated by the deterministic uncached algorithm on the same \((k,M,p)\). Proof: the cover search reads only those three values, with fixed enumeration order and tie-breaking.

**Theorem.** Replacing any node by a verified equivalent expression in its cut leaves preserves every downstream output. Since the replacement DAG is topologically valid and the full-circuit metric is checked before accepting it, the emitted circuit preserves Boolean function and respects the verified full Area/Delay constraints.

## 7. Runtime complexity and limitations

For an invocation visiting \(V\) nodes, retaining at most \(q\leq10\) cuts per node and considering at most \(k=4\) cut variables, the number of *distinct symbolic cover computations* is bounded by the number of keys encountered rather than the number of gate-mapping attempts. A cache lookup has expected \(O(1)\) time; building one cover is finite (at most 81 raw 4-variable cubes), but gate emission and DAG traversal remain substantial costs.

Even with a 25 ms cut-search budget, the final graph completion/serialization and the rest of Round 5.1 synthesis take additional time. The search is **heuristic and incomplete**, especially because we cap cuts and roots and constrain the postprocessing budget.

## 8. Overfitting guardrails

The 25 ms budget was chosen using the already observed public Stage 1 and the prior Round 6.0 developmental tests (including its existing holdouts); those sources are therefore **development evidence**, not new blind tests. The independent `holdout_round61_fresh_v1` (40 cases, seed `661061`) and `holdout_round61_large_v1` (8 cases, seed `0x615A7E11`) were generated, hashed and frozen **after the algorithm and 25 ms default were set**, then used once without subsequent retuning.

Synthetic holdouts protect against some testcase-specific optimization, but they cannot establish the distribution or performance of hidden Stage 2 cases. Retain the locked Round 5.1 efficiency baseline and the negative or mixed results in all later comparisons.

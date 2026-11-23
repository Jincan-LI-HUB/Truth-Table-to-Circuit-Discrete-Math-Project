# Round 8.4 — Mathematical Design and Correctness

## 1. Problem statement

Let a legal circuit be a directed acyclic graph of `AND2`, `OR2`, `NOT` gates, with output graph \(G\). For each input instance the six nonnegative costs specify area and gate delay. Denote total live area by \(A(G)\), maximum output arrival by \(D(G)\), and specified delay target by \(D_*\). The practical objective is to find a correct circuit with \(D(G)\le D_*\) and low area under a limited search/runtime budget; the **course's exact scoring formula is not inferred from the development records**.

Round 8.3 orders its preselected root candidates in topological order: a priority score \(s(v)\) selects set \(P_{1500}\), but only the first 900 members of \(P_{1500}\) encountered in increasing gate ID are actually considered. This is not the global top 900 by \(s\).

## 2. Two candidate-selection operators

Define a deterministic total order \(\prec_s\) on roots by (negative priority score, gate ID). Define \(\prec_t\) by increasing original topological gate ID. For root work quota \(q\):

\[
T_q=\operatorname{First}_q^{\prec_s}(V),\qquad
L_q=\operatorname{First}_q^{\prec_t}(T_{1500}).
\]

`topq_dual` examines \(T_{900}\) in **topological** order. `topology_dual` examines \(L_{900}\). The topology traversal is crucial because upstream node substitutions must be mapped before later nodes reference them. Selecting roots using a different ranking does not change this invariant.

We also define mixture sets. Select first \(r\) globally ranked roots, then fill remaining \(q-r\) slots using earliest topological gate IDs in \(T_{1500}\) not already selected. Tests use \(r=\lfloor q/3\rfloor\) and \(r=\lfloor 2q/3\rfloor\). This is a **hypothesis about enabling earlier rewrites**, not a proven optimum.

## 3. Bound on the root loop

All root choices are deterministic functions of the frozen graph, actual instance-specific costs, arrival and required-time values, and declared work quota. The cut traversal uses an upper bound of four cut leaves; a root is visited only after its transitive fanins have already been mapped. The selected-root quota bounds the number of **root optimization opportunities**, not total operation count: cut enumeration and graph construction can still be expensive. A separate wall guard is retained for timeout safety.

## 4. Adaptive pilot–focus alternative

Run two independent 220-root pilots, one for Shannon and one for SOP, on the same incumbent. If a pilot returns valid area \(A_i\) using \(w_i\) completed roots, define

\[
\gamma_i=\frac{\max(0,A_0-A_i)}{\max(1,w_i)}.
\]

The larger \(\gamma_i\) receives a 1,100-root follow-up search, again from the **same original full graph**. Equal scores prefer Shannon. This controls pilot selection without using wall-clock measurements, but the global total search time and the final full-graph selection remain relevant. Because the winning pilot is restarted, the scheme repeats work and is not inherently faster. Complete graph comparison retains the best feasible incumbent.

## 5. Cut truth-table equivalence

For a root \(v\), a feasible cut is a frontier \(C=\{c_1,\ldots,c_k\}\), \(k\le4\), intersecting every path from \(v\) to primary inputs. Treat cut leaves as independent formal Boolean variables. Evaluate the original DAG cone under all \(2^k\) assignments; this gives an exact mask \(f_{v,C}\). SOP/POS and Shannon candidates are equivalent to this mask by Boolean identities.

**Correctness lemma:** If a node is replaced with an equivalent function over a valid cut frontier whose mapped dependencies precede it topologically, every output remains unchanged. Proof: structural induction over topological order; all later gates compute the same function of their inputs.

`Builder` performs hash-consing, and final `finish()` retains only live output-reachable gates. The full circuit is measured again; only functionally equivalent, structurally legal, target-feasible full graphs are eligible to replace the incumbent. Thus no local heuristic is trusted as a substitute for exact final metrics.

## 6. Why Top-Q need not improve Area

The priority score is only an estimate of local recoverability: it cannot predict exact downstream DAG sharing or path-dependent future candidate availability. In an iterated graph rewrite, two valid root sets with the same cardinality are **not exchangeable**; optimizing an earlier root changes which mapped cut leaves and hash-consed nodes are available later. Therefore selecting the highest individual scores may destroy a chain of smaller enabling transformations. In particular, neither \(A(T_q)\le A(L_q)\) nor the reverse holds in general.

## 7. Time, memory and validity boundary

Search-limited output is conditional on the incumbent and actual completed computation. A hard wall deadline may truncate a large run before its deterministic work cap, so the algorithm is *work-capped*, not universally deterministic. Its memory includes BDD construction, truth-table caches, DAG nodes, hash tables and temporary rewrite graphs; the root quota alone is not a sufficient memory bound. The Round 8.2.1 RAM low-memory fallback is preserved and the evaluator ambiguity remains unresolved.

# Round 6.0 — Bounded Four-feasible-cut Boolean Rewriting

**Research status:** exploratory prototype. **Frozen control:** Round 5.1 (`src/synth_round51.cpp`), compiled with the same `-O2 -std=c++17 -DNDEBUG` flags. The project permits only `AND2`, `OR2`, `NOT`, input wires, and the constant-zero node.

## Motivation and design constraints

Round 5.1 primarily maps BDD/Shannon structures to gates, then performs generic balancing, De Morgan, polarity selection and short algebraic identities. It does **not** enumerate arbitrary 4-input cuts and synthesize local truth tables independently of the original gate shape.

The Round 6.0 hypothesis was that some redundant structure remains in the final DAG, but that any improvement must be **globally** costed under shared fanout and a timing constraint. The experiment deliberately restricts the cut size and search budget.

## Definition: a feasible cut

Let \(G=(V,E)\) be the existing acyclic netlist and \(v\in V\) an internal gate. A cut \(C_v\subset V\) is feasible if every path from \(v\) back to a primary input (or zero) meets an element of \(C_v\). The cut is \(k\)-feasible if \(|C_v|\leq k\); this prototype fixes \(k\leq4\).

A cut defines an induced Boolean function

\[
f_{v,C_v}:\{0,1\}^{|C_v|}\to\{0,1\},\]

where the cut boundary signals are treated as independent formal inputs. **Independence here is only a truth-table enumeration device**, not a statistical claim about actual signals. If two leaf signals are logically correlated, a replacement correct for *all* boundary assignments remains correct on the correlated subset.

Each gate propagates up to ten cuts (including the trivial cut consisting of the gate itself), formed by union of child cuts and filtered at size four. The cap controls combinatorial explosion; it does **not** exhaust all 4-feasible cuts. The root implementation only visits up to 4,000 live roots, and the postprocessor is additionally time-bounded.

## Four-input truth-table computation

For a cut of size \(k\leq4\), enumerate the \(2^k\leq16\) assignments to its leaves. Use bit-parallel masks to simulate `AND2`, `OR2`, and `NOT` through the cut's internal gates. The resulting integer mask uniquely specifies the cut function.

A cut replacement is considered only when its Boolean mask is realized by one of the following algebraically exact constructions:

1. **SOP:** cover the on-set by prime implicant cubes (two fixed, input-independent greedy policies), then OR the corresponding conjunctions.
2. **Complemented SOP / POS:** build an SOP for \(\neg f\), then negate it. This represents a dual product-of-sums form by De Morgan's law.
3. **One-literal factoring:** extract a common literal from two or more terms of a selected cover; for example \(ab\lor ac=a(b\lor c)\).
4. **Shannon decomposition:** split on the first or last available cut variable and recursively synthesize its two cofactors:

\[
f=\neg x\land f_{x=0}\;\lor\;x\land f_{x=1}.\]

The generated structure has only the allowed gate types, preserves topological ordering, and reuses identical gates via structural hashing. This is **not** an exact minimum-area implementation library and does not explore every NPN-equivalent circuit.

## Local cost is not global cost

If a cut replacement alters the signal at \(v\), old internal gates can be eliminated only if they are no longer referenced by any other output or fanout. The local cost estimate therefore counts as removable only \(v\) plus recursively private internal nodes whose old reference count is one and which are not cut leaves.

Candidate gate cost is computed by walking the candidate's actual local cone to the cut leaves. **Speculative gates created by rejected candidates are not treated as free**, even if they remain in the temporary hash table. This avoids a known flaw in naive hash-table-based incremental costing.

The local test is deliberately conservative:

\[
A_{\mathrm{new,local}}-A_{\mathrm{removable,old}}<0,
\qquad
T_{\mathrm{new}}(v)\leq T_{\mathrm{original}}(v).
\]

The second inequality ensures that later gate arrival times cannot increase *because of this replacement*, assuming the mapping of input cut leaves is already fixed. The method may miss global opportunities because it rejects some rewrites that require a temporary area or delay increase.

**Crucially, the final acceptance test does not trust this estimate:** the complete DAG is garbage-collected and its actual Area and critical path are recomputed from scratch. The new final output replaces the Round 5.1 incumbent only if

\[
A(G_{6.0})<A(G_{5.1})
\quad\text{and}\quad
D(G_{6.0})\leq D_{\mathrm{target}}.
\]

The existing Round 5.1 netlist remains the fallback.

## Correctness argument

**Lemma 1 (Cut preservation).** By induction on the internal cut gate DAG, bitwise gate simulation computes exactly \(f_{v,C_v}\) for every assignment of the cut leaves.

**Lemma 2 (Candidate equivalence).** Every SOP candidate covers only true minterms and exhausts the on-set. Complemented SOP follows from Boolean complementation, factoring from distributivity, and Shannon candidates from the Shannon identity. Therefore each emitted candidate computes \(f_{v,C_v}\) for every leaf assignment.

**Lemma 3 (Global substitution).** Replacing \(v\) with an equivalent function of its existing cut leaves does not affect any predecessor; by induction on downstream gates, all primary outputs remain unchanged. Structural hashing and deletion of dead gates do not alter the realized functions.

**Theorem.** Every successful Round 6.0 substitution preserves the output truth tables of the original netlist. The total-area / timing acceptance rule then ensures the emitted candidate respects the checked Stage 1 area-decrease and target-delay constraints (subject to the correctness of the parser and gate-cost model, separately cross-checked with the official evaluator and independent simulation).

## Complexity and experiment limitations

The unbounded number of distinct cuts can grow combinatorially; this implementation fixes \(k=4\), at most ten retained cuts per node, 4,000 searched live roots, and a **120 ms maximum cut-search budget** (further limited to 6% of the testcase synthesis limit, with a 5 ms floor). The entire full-synthesis executable may still pay an additional traversal and allocation cost to initialize the rewrite machinery. The `cut_postprocess` executable permits the same local algorithm to be profiled independently.

The final selection is strict-area-improvement only. A local candidate can be valid and faster but still be rejected because its total Area is larger; similarly, a locally promising rewrite can be suppressed by shared-fanout constraints.

**Overfitting caveat:** The code was debugged using public Stage 1 cases. The 40-case new holdout was frozen after the algorithmic rules and thresholds were fixed, then its input *format* was corrected to satisfy the official evaluator without changing any Boolean truth values. We also reuse the previously frozen 80+16 Round 5.1 regression corpora. None of these synthetic distributions is guaranteed to represent hidden Stage 2.

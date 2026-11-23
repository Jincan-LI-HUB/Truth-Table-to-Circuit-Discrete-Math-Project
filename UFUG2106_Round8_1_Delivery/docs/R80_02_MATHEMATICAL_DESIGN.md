# Round 8.0 — Mathematical design and safety argument

**Intent:** a deliberately narrow structural synthesis experiment that diagnoses interaction among algebraic form, global DAG sharing, required time, and bounded iterative search. No global optimality claim.

## 1. Formal model

Input: a complete Boolean function \(f:\{0,1\}^n\to\{0,1\}^m\) supplied as a truth table. The existing Round7.2 engine emits a topologically ordered directed acyclic graph \(G=(V,E)\) with primary input nodes, the literal constant-0 node, and internal operations \(\mathrm{AND2},\mathrm{OR2},\mathrm{NOT}\).

For each gate \(v\), \(a(v)\) is the declared gate area, \(d(v)\) is its delay. Let \(L(G)\) be all internal gates reachable from at least one of the \(m\) outputs. The *true* weighted area and timing are

\[
 A(G)=\sum_{v\in L(G)} a(v),\qquad
 t(v)=d(v)+\max_{u\in \mathrm{fanin}(v)}t(u),\qquad
 D(G)=\max_{o\in\mathrm{outputs}(G)}t(o).
\]

An error is to use \(\sum_{v\in\mathrm{modified\ local\ cone}}a(v)\) as the accepted area difference. The local cone may have external fanout, and gate hashing might reuse nodes previously computed for another output. Every accepted replacement uses *full live-DAG recomputation* after garbage collection.

## 2. Inherited feasible incumbent and guards

Let \(G_0\) denote the Round7.2 output. Round8 preserves its exact serialized form until an improved network is validated. In the integrated solver structural rewriting is attempted only if the reported budget is \(\ge1000\) ms and current elapsed time is below 67% of that budget; tighter 100ms cases are left unchanged. This is a resource-aware *heuristic guard*, not a formal deadline guarantee.

For every structural candidate \(G'\), the acceptance condition is

\[
 \operatorname{Valid}(G')\land D(G')\le D_{\mathrm{target}}
 \land\bigl(A(G')<A(G_*)\ \lor\ [A(G')=A(G_*)\land D(G')<D(G_*)]\bigr).
\]

The `iterate_strict` ablation additionally enforces \(D(G')\le D(G_0)\), where \(G_0\) is the inherited Round7.2 incumbent, to keep delay from regressing. This is important because \(A=22{,}535,D=70\) and \(A=22{,}590,D=69\) are **mutually non-dominating** candidates, not a proof that one is universally better under unknown grading weights.

Thus the candidate's measured full area strictly decreases, or ties with strictly improved delay. A candidate with smaller area may spend timing slack, but may **never** cross the target. This favors area after feasibility, not a fabricated official scalar scoring rule.

## 3. Exact algebraic candidate generation

All expressions below denote Boolean functions of arbitrary *signals*, which can themselves be complex shared subgraphs. They are identities for every valuation of those signals and need no probabilistic assumption about independence.

### 3.1 Canonical local identities

\[
 x\land x=x,\quad x\lor x=x,\quad
 x\land0=0,\quad x\lor0=x,\quad
 x\land\neg x=0,\quad x\lor\neg x=1.
\]

Absorption and double negation:

\[
 x\land(x\lor y)=x,\quad x\lor(x\land y)=x,\quad \neg\neg x=x.
\]

All internal nodes are constructed with structural hashing: a hash table interns the canonical operation and fanin IDs, avoiding redundant construction in the current tentative DAG.

### 3.2 Factoring (and its dual)

\[
 (x\land y)\lor(x\land z)\equiv x\land(y\lor z),
\]
\[
 (x\lor y)\land(x\lor z)\equiv x\lor(y\land z).
\]

The conservative mode permits the factored candidate only when both original children have one original fanout and the alternative root fits the backward propagated required time. The relaxed mode tries factoring even when the children have external users; the final **global** cost test will reject unprofitable replacements.

A negative result for one factoring mode does not imply that factoring has no utility. It can mean the old graph is already factored, the pattern does not appear in a direct two-level cone, the children are shared, or the timing constraint excludes the variant.

### 3.3 Phase alternatives and per-case cost

\[
 x\lor y=\neg(\neg x\land\neg y),\qquad
 x\land y=\neg(\neg x\lor\neg y).
\]

The direct and dual expressions have different weighted areas and propagation delays in the course's case-specific gate library. The prototype considers a De Morgan candidate when the direct gate's declared area exceeds the opposite-polarity gate plus three NOT costs, and the candidate respects the required time. Structural hashing may reduce actual incremental cost when complement signals already exist. **Whole-circuit evaluation** decides whether the alternative is actually an improvement.

### 3.4 DAG-aware divisor reuse (the only presently fruitful new mechanism)

For a node with \(w=x\land(y\lor z)\), suppose the existing DAG already includes \(u=x\land y\), or \(v=x\land z\), constructed for a different output or predecessor. The alternative is

\[
 w\equiv u\lor v=(x\land y)\lor(x\land z).
\]

If both \(u\) and \(v\) already exist, the alternative may need only an OR2 gate; the old cone needed an OR2 and AND2 gate. This can save area even though a purely local syntax tree comparison would say distribution **expands** one AND/OR pair into three gates. If only one divisor exists, the alternative is more speculative: whole-DAG area can improve or worsen and is measured exactly before acceptance.

The dual identity for OR of an AND cone is also supported. To avoid exploring an unbounded number of bad expansions, the prototype attempts the distributed form only when at least one child product is already present in the **current builder's structural hash table**. It checks timing feasibility against propagated required times before choosing the rewritten node. It later invokes garbage collection and measures area and delay for **all outputs**.

This mechanism is *limited resubstitution* in a concrete, inspectable sense: it seeks already computed divisors that match distributive products. It is NOT the general Boolean resubstitution search available in mockturtle or ABC.

## 4. Required time and slack

For each output \(o\), initialize \(r(o)=D_{\mathrm{target}}\). Process the original DAG in reverse topological order:

\[
 r(u)\gets \min\bigl(r(u),r(v)-d(v)\bigr),\quad u\in\mathrm{fanin}(v).
\]

A candidate rebuilding original node \(v\) is tentatively allowed when its current arrival time does not exceed \(r(v)\). This may admit a slower local cone if the original network had unused timing slack. Because the rewrite can change other shared fanouts and reconvergent paths, this check is a **filter, not a correctness certificate**. The final acceptance additionally requires the exact new global delay \(D(G')\le D_{\mathrm{target}}\).

In Stage2 `case_021`, the original delay 69 and target 70 leave one unit of timing slack; the accepted rewrite consumes that slack and lowers area.

## 5. Structural choices, repeated passes, and noncommutativity

A pass generates multiple valid candidate graphs \(G'_1,\dots,G'_q\) from the same incumbent \(G_*\). Every alternative is evaluated using the exact gate library and global live-DAG cost. We accept the best improving candidate and can begin a second pass *on the accepted result*.

Generally, \(F_A(F_B(G))\ne F_B(F_A(G))\) because rewriting can create or remove syntactic matches and can alter structural hashing opportunities. A first pass that yields only a modest improvement can therefore expose new divisor candidates in a second pass. This is **not** a proof of global convergence: we only test up to five passes and stop when a full pass fails to improve the incumbent.

**Monotonicity theorem (for accepted completed candidates).** If every accepted candidate satisfies the criterion in Section 2, the sequence of weighted areas is nonincreasing and strict decreases occur whenever the area is changed. If the area ties, the delay strictly decreases. Since these metrics are nonnegative integers and the search is bounded, every completed pass returns a feasible incumbent without degrading either the feasibility requirement or the ranking used to select it.

*Proof:* By construction, every update is guarded by global validity, target timing, and lexicographic improvement in \((A,D)\). Induction over accepted updates preserves feasibility and the monotone ordering. This does **not** prove an arbitrary intermediate speculative graph is valid or that the algorithm terminates without runtime controls; its bounded loops guarantee termination under finite per-pass computation.

## 6. Complexity and limits

Each DAG traversal and full-metric computation is \(O(|V|+|E|)\) expected under amortized-constant hash operations. Each candidate pass uses a fixed collection of simple local identities and a bounded number of graph rebuilds. More generally with \(p\) passes and \(q\) rewrite modes, the expected transformation work is \(O(pq(|V|+|E|))\) plus hashing and serialization. This is an *average expected-work model*; it does not bound OS scheduling delays or worst-case unordered-map behavior.

The integrated search uses \(p\le5\), a postprocessing budget of \(\min(250\,\mathrm{ms},0.10T_{\mathrm{limit}})\), and a global pre-pass stop if total elapsed time reaches 82% of the declared budget. **A single in-progress rewrite is not interruptible**: CPU resource safety therefore remains empirical, and the official 50-case evaluator is mandatory.

Memory is \(O(|V|+|E|)\) per candidate graph plus the source, hash tables, and transient graphs. No external ABC executable, SAT solver or background tasks are required. The synthesized netlist contains only permitted operations and valid topological gate IDs.

## 7. Why this cannot claim optimality

1. The rewrite neighborhood consists of specific two-level identities, not all NPN classes or arbitrary cut functions.
2. Current search accepts only immediate complete-DAG improvements. A sequence requiring temporary global area degradation may remain inaccessible.
3. Choosing a single incumbent at each pass loses non-dominated structural choices. A bounded Pareto frontier is the next hypothesis.
4. Explicit truth-table synthesis and minimum-area multi-output DAGs with per-case gate costs are combinatorially complex; a short-budget heuristic cannot certify global optimum.
5. Unknown official scoring formula means the proxy \((\text{feasibility},A,D)\) is a research ranking, not the official scoring objective.

## 8. Prior-work links and non-equivalence of objectives

- Berkeley ABC: https://github.com/berkeley-abc/abc . Multi-level AIG rewriting and logic network methods; raw AIG node count does not equal explicit NOT-weighted area.
- mockturtle: https://mockturtle.readthedocs.io/en/latest/ . Cut resynthesis, rewriting, resubstitution and technology mapping; our implementation is a small identity-based prototype, not a port.
- Choice-network research (2025): https://arxiv.org/abs/2508.14068 . Motivates retaining multiple structural alternatives but does not prove a particular parameter setting for this benchmark.
- eSLIM SAT-based local improvement: https://drops.dagstuhl.de/entities/document/10.4230/LIPIcs.SAT.2024.23 . A candidate for future cut-local exact synthesis, beyond this milestone.

See `01_MOTIVATION_AND_EVIDENCE.md` for the measured outcomes, and `03_EXPERIMENT_PROTOCOL.md` for controlled on-machine validation.

# UFUG2106 — Round 5.1: Typed In-memory DAG & Incremental Arrival Propagation

## 1. Goal and scope

Round 5.1 is an **engineering optimization**, not a new Boolean synthesis heuristic. Round 5 is the frozen reference; the candidate list, Boolean identities, cost constants, phase search and deadlines are unchanged. The exact code modifications are isolated in `src/typed_netgraph.hpp` and the integration in `src/synth_round51.cpp`. The original `src/synth_round5.cpp` is included verbatim as the comparator.

This distinction matters because repeated selection on the public Stage 1 cases risks benchmark overfitting. Round 5.1 was designed to preserve fixed-candidate semantics and is tested against separately generated held-out functions.

## 2. Typed Netlist representation

For inputs \(x_1,\ldots,x_n\) and outputs \(y_1,\ldots,y_m\), represent a combinational DAG as

\[
G=(V,E,\operatorname{op},\operatorname{fanin},\operatorname{outputs}),
\]

where node 0 is the constant zero, nodes \(1,\ldots,n\) are the inputs, and each gate node \(v>n\) has \(\operatorname{op}(v)\in\{\mathrm{AND2},\mathrm{OR2},\mathrm{NOT}\}\), with fanin IDs strictly less than \(v\). In memory, each gate is a compact tuple `(op,a,b)`, not a line of text. A single explicit parser converts the output of the upstream BDD mapper to this representation.

**Topological invariant.** For every gate \(v\), all its fanins precede it. The construction and final live-node compaction preserve this property, so the graph serializes directly to the official format.

## 3. Why reusing an in-memory graph is correct

For each node define \(f_v:\{0,1\}^n\to\{0,1\}\) recursively. The legal transformations used here are exactly those in Round 5:

- Associative regrouping of AND/OR chains, plus idempotence \(a\land a=a\) and \(a\lor a=a\) in `rebalance`.
- Timing-aware De Morgan alternatives in `area_recover`, relying on

\[
\neg(\neg a\lor\neg b)=a\land b,\qquad
\neg(\neg a\land\neg b)=a\lor b.
\]

- Structural hash-consing of `(op, min(a,b), max(a,b))` for commutative gates, and `NOT(a)` for negation.
- Dead-gate elimination by backward reachability from each output.

The typed implementation preserves the traversal order, priority-queue ordering, hashing-based reuse semantics, and the old acceptance comparison. A structural induction on gate IDs establishes \(f_v\) remains unchanged for every mapped node. Pruning deletes only nodes not reachable from any output, so the output functions are unchanged.

**Qualification:** hashing and mapping affect gate IDs, and wall-clock-dependent search deadlines can affect which candidate finishes. Therefore we separately compare the final Area, Delay, and Netlist bytes. A guarantee of byte identity across all possible executions is not claimed.

## 4. Incremental Arrival Time

Let the cost model supply delays \(d_\wedge,d_\vee,d_{\neg}\). Initialize all primary input and constant node arrivals to zero. When a new node \(v\) is inserted into the typed builder, compute immediately:

\[
 t(v)=\begin{cases}
 t(a)+d_{\neg},&\operatorname{op}(v)=\mathrm{NOT},\\
 \max(t(a),t(b))+d_{\wedge},&\operatorname{op}(v)=\mathrm{AND2},\\
 \max(t(a),t(b))+d_{\vee},&\operatorname{op}(v)=\mathrm{OR2}.
 \end{cases}
\]

Because the graph is topologically ordered and structurally shared gates are immutable, each stored \(t(v)\) is exact by induction. Both rebalance's heap scheduling and area recovery's timing feasibility use these in-memory arrival values. This removes repeated text parsing and intermediate serialization in the two principal postprocessors.

The *total* graph Area is still recomputed from the **pruned live DAG** before ranking:

\[
 A(G)=\sum_{v\text{ live gate}}a_{\operatorname{op}(v)},\qquad
 D(G)=\max_{y\in\operatorname{outputs}}t(y).
\]

This is deliberate: a local gate rewrite may change shared fanout and liveness. Merely subtracting the replaced gate's area is incorrect when ancestors are shared. Full graph-wide incremental fanout-based Area updates are **not** implemented in Round 5.1; adding them without a correctness proof would increase risk.

## 5. Correctness and performance controls

1. Compile both frozen Round 5 and Round 5.1 using the same compiler flags.
2. Interleave two complete official evaluations in opposite orders; compare each case's Area, Delay and runtime.
3. Independently verify 13 small official cases exhaustively and 12 larger cases by deterministic sampling, in addition to the official Evaluator's functional check.
4. Use a pre-committed test generator seed to produce **80 distinct function cases**, containing affine, sparse, threshold, MUX, arithmetic, shared and dense functions.
5. Use a separately committed **16-case large/structural** benchmark to check whether any gains survive beyond the public cases.
6. Re-run the older 110 generated tests and two structured stress tests.
7. Never adjust new heuristics based on holdout Area; the Round 5.1 source and holdout generator were frozen before valid holdout results were inspected. A formatting correction in the generated case files was necessary to satisfy the official input schema, and did not alter the generated functions.

## 6. Limitations and scope for future work

- Round 5.1 does **not** keep a single typed graph all the way through the final `round4_algebra` and `round4_phase` implementations; those stages still accept strings. The optimization is concentrated in BDD postprocessing, rebalancing and recovery.
- A large corpus with predominantly small easy circuits may show no meaningful runtime gain because input/evaluator overhead dominates. Aggregate speedups must be stratified by problem size.
- Stage 2 has not been observed and could have a different distribution of Boolean functions, costs, input sizes or runtime limits.
- Wall-clock heuristic cutoffs can change chosen candidates; final output still needs official validation.
- Byte-for-byte equality on the public 25 is empirical evidence, not a mathematical proof of all future executions.

## 7. References to reproducible material

- `src/synth_round5.cpp` — frozen reference.
- `src/synth_round51.cpp` — candidate with shared typed postprocessing.
- `src/typed_netgraph.hpp` — typed parser, builder, live-node pruning, metric and transforms.
- `tests/holdout_manifest.json` and `tests/holdout_large_manifest.json` — deterministic held-out populations.
- `results/` — official CSVs, paired benchmark logs, independent verification evidence.

# Round 8.2 — Mathematical and Algorithmic Design

## 1. Problem and precise optimization targets

For a shared directed acyclic Boolean gate graph \(G=(V,E)\), each internal node \(v\) uses \(\land,\lor,\neg\), with example-specific area \(a(v)\) and intrinsic delay \(d(v)\). Its weighted area is

\[
 A(G)=\sum_{v\in V_{\mathrm{live}}\setminus V_{\mathrm{PI}}}a(v).
\]

The arrival time at any internal gate is

\[
 t(v)=d(v)+\max_{u\in\operatorname{fanin}(v)}t(u),
 \qquad D(G)=\max_{o\in O}t(o).
\]

We require exact truth-table equivalence, valid output representation, a total process runtime within the case-specific evaluator limit, and prefer \(D(G)\le D_{\mathrm{target}}\). Public PASS may not require target met, but both are essential release gates here.

Two objective families are deliberately *not* conflated:

1. **Area priority:** minimize \(A(G)\) under \(D(G)\le D_{\mathrm{target}}\).
2. **Timing-regularized quality:** admit a lower-area candidate only if it satisfies an additional delay cap or improves an explicit surrogate such as \(A(G)D(G)\). This is not a known course grading formula.

## 2. Exact cut-function equivalence

Let \(C=\{u_1,\dots,u_k\}\), \(k\le4\), be a feasible cut of the root \(v\): every path from any primary input to \(v\) intersects \(C\). Treat the cut leaves as formal independent Boolean inputs, and calculate the exact local truth mask

\[
 M_{v,C}=\sum_{s=0}^{2^k-1} f_{v,C}(s)\,2^s.
\]

The cut may be re-expressed through prime-implicant SOP/POS or Shannon decomposition in multiple variable orders. Each expression is checked through exact local Boolean function construction, not inferred from syntax or approximate simulation.

The source retains the Round8.1 generator with the same maximum four leaves, small retained cut sets and structural hash emission. The new contribution is **where and how long we search**, and **how we select among complete mapped candidates**.

## 3. Required arrival times and slack

For every output \(o\), initialize \(r(o)=D_{\mathrm{target}}\). Backpropagate required times along fanins:

\[
 r(u)=\min_{v:u\in\operatorname{fanin}(v)}[r(v)-d(v)].
\]

The current arrival time \(t(u)\) is computed by forward topological dynamic programming. The available local slack is \(s(u)=r(u)-t(u)\). The algorithm uses slack for **ranking only**; actual complete-circuit timing is independently measured before accepting any candidate.

## 4. Reclaim-aware deterministic root priority

Let \(c(v)\) denote the example-specific area cost of a gate. Let \(F(u)\) be the original network fanout count. For each live root, the fixed heuristic is

\[
 P(v)=16c(v)
 +8\sum_{u\in\operatorname{fanin}(v)}c(u)\,\mathbf1_{\{u\text{ internal},\ F(u)=1\}}
 +\min(8,\max(0,s(v))).
\]

For NOT, the unused second fanin is omitted. Coefficients \(16,8,8\) are **heuristic priorities**, not optimality constants or a proven approximation ratio. They were chosen before evaluating the frozen structured holdout and are fully documented so future experiments can vary them without silent drift.

The priority branch selects at most \(K=1500\) live roots with maximum \(P(v)\), breaking ties deterministically by node ID. Selected roots are then visited in **original topological order**; changing exploration priority does not create invalid forward references. The control `stride` selects approximately every \(\lceil |V_{\mathrm{internal}}|/K\rceil\)-th node and retains the earlier Round8.1 sampling approach.

Work caps \(K=750,1500,2500\) are tested independently for critical developmental cases; do not silently promote a public-case-optimal cap to default. Topological DAG construction still visits all nodes; the cap restricts expensive rewriting, not graph traversal.

## 5. Exact whole-graph candidate selection

For the already valid baseline graph \(G_0\), let

\[
 A_0=A(G_0),\qquad D_0=D(G_0),\qquad S_0=D_{\mathrm{target}}-D_0.
\]

Each proposed branch \(G_j\) is fully materialized and measured after structural hashing / dead-node elimination. No local optimistic cost proxy decides final acceptance. A complete incumbent is maintained throughout, and candidates must be valid, equivalent by the local rewriting construction, and respect the specified delay restriction.

**`area`** admits \(A_j<A_0\) or equal area with smaller delay, provided \(D_j\le D_{\mathrm{target}}\). Choose minimum area, break ties by delay.

**`strict`** adds \(D_j\le D_0\); candidate area never increases.

**`slack`** admits only \(D_j\le D_0+\lfloor S_0/3\rfloor\), capped by target. Thus it permits using up to one-third of the *existing* whole-circuit slack, not an arbitrary fixed delay increment.

**`adp`** admits only candidates satisfying

\[
 A_j\le A_0,\qquad A_jD_j<A_0D_0,\qquad D_j\le D_{\mathrm{target}}.
\]

Then select the candidate with the smallest product; tie-break on area and delay. Multiplication uses 128-bit intermediate integers so overflow does not silently corrupt comparisons. This objective is a sensitivity experiment, **not an assertion that the course score equals area × delay**.

A small metric-only Pareto archive contains \((A,D,\text{source branch})\) for the incumbent and the completed SOP/Shannon branches. If a point is dominated by another measured point, it is excluded from profiling output. **This is not a full structural choice DAG or persistent bank of all netlists:** only the selected best netlist is emitted.

## 6. Runtime and branch selection

`fast_*` examines an independently generated Shannon branch; `dual_*` examines Shannon then SOP, both from the SAME frozen starting graph rather than node-level interleaving. The default per-call root cap is 1500.

R8.2 starts only for declared runtime limits of at least 1000 ms and only when the incumbent already meets target. A synthesis call is admitted if existing elapsed time is below 70% of the declared limit. Aggregate R8.2 search allocation is at most

\[
 B=\min(300\mathrm{ms},0.10\,T_{\mathrm{limit}}),
\]

with at most 140 ms per branch and additional whole-process checks at 80–82% of the declared limit. The underlying cut generator checks its clock after batches of selected roots and completes the remaining DAG after early termination.

These are *cooperative time budgets*, **not hard real-time deadlines**: rebuilding, memory allocation, graph serialization and evaluator overhead consume additional time. The official same-host evaluator remains the only authoritative runtime gate. For n ≤ 20 local Stage2 cases, independent exhaustive verification confirms the emitted functions; full official equivalence still has to be checked on both stages.

## 7. Trade-offs and what the math does NOT prove

- A higher priority score is not a proof that the root contains a useful cut; it merely changes which candidate roots are examined under a finite budget.
- Adding a second branch can improve area but has a nonzero runtime and memory cost, and may choose a slower circuit.
- A lower area-delay product does not necessarily improve the unknown class score; compare Pareto feasibility and course weights once available.
- Exact cut equivalence plus valid topological substitution guarantees Boolean equivalence, but **does not guarantee globally optimal mapping, complete search, or robust wall-clock behavior**.
- `stride` and `priority` may each win on individual cases; aggregate public improvement is not a domination guarantee.

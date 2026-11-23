# Round 8.3 — Search Work Budget and Mathematics

## 1. Why Stage2 dual search varied

Round 8.2 independently runs Shannon and SOP cut rewriters, but uses a shared wall-clock budget and branch deadlines. In `r82_cut.hpp`, the chosen roots are deterministic given a fixed input DAG, yet the loop breaks every 32 selected roots when `Clock::now() > deadline`. As a result, time jitter changes the number of roots considered, with potentially different entire-DAG outputs. The instability can also begin in upstream BDD/legacy choices; controlling only the cut stage will not eliminate all nondeterminism.

## 2. Root-work quota

Let `G` be an AND2/OR2/NOT DAG with actual area weights `a_AND`, `a_OR`, `a_NOT` and propagation delays `d_AND`, `d_OR`, `d_NOT`. Determine a deterministic priority order over live eligible roots (reclaimable cost, a bounded slack score and topological ID tie-break). Select a subset of at most 1,500 roots. Visit selected roots in topological order, and bound the *completed* rewrites by an integer quota `Q`. The stop event is checked **between full roots**, so a root's set of cut alternatives is not partially inspected for a work-count reason.

For the default dual policy, `Q=900`, except when `runtime_limit<=2000` and `m>=20`, when `Q=600`. The dense ablation explicitly requests 1,100. `Q` is a deterministic search-count heuristic, **not a bound on CPU instructions**. A separate emergency wall guard stops the cut loop when needed; timeouts can still produce different results. Retain the original incumbent and finish mapping all remaining gates in topological order after either stop reason.

## 3. Formal equivalence

For a feasible cut `C={u_1,...,u_k}`, `k<=4`, at root `v`, evaluate every `s in {0,1}^k` as *formal* independent assignments. Each constructed SOP/POS or Shannon circuit `h_C` satisfies:

\[
\forall s\in\{0,1\}^k,\qquad h_C(s)=f_{v,C}(s).
\]

Replacing the root by its equivalent function of cut leaves leaves the full network function unchanged by structural induction. When the quota or guard stops, the rest of the nodes are copied without rewriting, preserving equivalence. The independent verifier checks all `2^n` original truth-table rows for tested `n<=20` cases.

## 4. Real costs and timing

The true globally live area is

\[
A(G)=\sum_{v\in\mathrm{Live}(G)}a(\mathrm{op}(v)),
\]

and delay is the maximum arrival time among outputs, with each node arrival determined by its gate delay plus the maximum predecessor arrival. Local rewriter uses conservative private-cone cost and per-node required time to reject unpromising candidates. **Only the resulting full DAG metric is used for final acceptance.**

For candidate `H` and incumbent `G0`, every active policy requires actual validity and `D(H)<=D_target`. Area-policy eligibility uses `A(H)<A(G0)`; ADP and Strict follow the frozen `r82_archive.hpp` exactly. Modes are run on **the same frozen `G0`**, not chained on one another, so comparisons are meaningful. The final archive retains both candidate `A`, `D` for traceability.

## 5. Complexity and limitations

With at most `Q` visited roots, at most 9 retained cuts per root and max 4 formal cut variables, the *resynthesis work* per branch is bounded by a fixed number of local candidate analyses under the chosen heuristics. Construction and copying of the full DAG remains at least linear in the graph size, and individual cut evaluation is not constant-time in arbitrary upstream cone size without bounded traversal. Therefore neither `Q` nor a watchdog implies an absolute total runtime guarantee. Resource limits and initial BDD search must continue to be tested independently.

## 6. No universal dominance

Stability and minimum area have different objectives. For fixed target delay, a deterministic search may end before discovering a low-area cut the time-based search occasionally reaches. A candidate is preferable under one scalar score only if the grading formula and weights justify it. Report separate area, delay, runtime and wall-hit counts, and retain negative examples.

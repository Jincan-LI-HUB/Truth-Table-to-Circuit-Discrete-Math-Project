# Round 9.1 Mathematical and Algorithmic Design

## Aim

R8.4/R8.6 used local SOP and Shannon constructions. Round 9.1 constructs a distinct finite library of bounded Boolean expressions indexed by complete 2–4-input truth functions, and compares it **against a time/root-matched second run** of those earlier algorithms.

## Exact function signatures

Let `C = {u_0,...,u_{k-1}}`, k<=4, be a frontier separating root `r` from all primary inputs. Then `r = F_C(u_0,...,u_{k-1})`. Define the complete truth signature

\[
T(F_C)=\sum_{a=0}^{2^k-1} F_C(a)2^a.
\]

A library recipe `E` is admitted only if `T(E)==T(F_C)`. The key is complete for local functions of the cut leaves; it is not a heuristic collision-prone hash. Because the frontier separates all paths from root to primary inputs, replacing `r` by `E(C)` preserves the global Boolean function (provided no cycles are introduced, which is guaranteed by reusing only already mapped predecessors).

The library enumerates parenthesized AND/OR chains, two-pair factorizations, MUX, 2-/3-input XOR, Majority, and literal polarities; each recipe is truth-indexed and individually instantiated into a fresh graph in `tests/test_library.cpp`. **13,956/13,956** recipe instances were validated for every one of their possible input assignments. This is not an assertion that the library contains minimum-area implementations for all 65,536 four-input Boolean functions.

## Weighted DAG cost

For any candidate graph G, compute actual weighted area:

\[
A(G)=a_A N_{AND2}(G)+a_O N_{OR2}(G)+a_N N_{NOT}(G).
\]

The public project uses case-specific gate weights, so unweighted minimum gate count is not sufficient. Arrival times use the specified gate delays and topological order, and outputs determine `D(G)`.

A local candidate is shortlisted using the fanout-aware estimate

\[
\widehat{\Delta A}=A_{candidate\ cone}-A_{privately\ reclaimable\ cone}.
\]

It is **not** sufficient for final acceptance: graph rebuilding can alter sharing and fanout. The only accepted final candidate satisfies

\[
A(G_{new}) < A(G_{old}),\qquad D(G_{new})\le D_{target}.
\]

The selected candidate is regenerated with consistent gate IDs and dead-node removal. If no qualifying candidate is found, the original graph is returned.

## Runtime boundary

The new postprocessor only runs when case runtime limit `L>=1000` ms, a valid base solution exists, and wall elapsed time is below `0.82L`. Its allowance is

\[
\tau=\min(90\ \mathrm{ms},\,0.06L,\,0.82L-t_{spent}).
\]

If `tau<8ms`, skip it; root selection takes up to 160 of the highest ranked eligible nodes. The deadline is checked periodically rather than preempting a partially processed root, so the **nominal** optional-pass allowance can itself be exceeded (e.g. the matched Shannon control took 158ms on one local case despite a nominal 90ms limit). Parsing, fixed setup, and graph cleanup also add work. This experimental branch must not be promoted without official time-limit regression evidence.

## Proof boundary

The library verifies local truth signatures and enforces a global area/delay gate; this provides a deterministic logical equivalence argument for the transformation **if the cut frontier is valid**. Independently, every emitted test netlist in the local runs is checked against all assignments of the original truth table. Do not extrapolate those tests to grading-hidden cases.

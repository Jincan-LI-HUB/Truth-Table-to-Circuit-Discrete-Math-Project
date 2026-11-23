# Mathematical Verification and Scope Ledger (Phase 2)

**Subject:** R10.0 independent frozen candidate (source hash in `FINAL_SOLVER_SPEC.md`).  
**Purpose:** specify the mathematical claims we can justify from definitions/code, distinguish them from implementation evidence, and identify where additional validation remains necessary before the Final Report.

## A. Formal objects and the optimization contract

Let \(F=(f_0,\ldots,f_{m-1})\) be completely specified by \(m2^n\) bits. A legal gate netlist \(G\) has zero/input signals and AND2, OR2, NOT nodes with topologically earlier fanins. Write \(\llbracket G\rrbracket\) for the \(m\)-output function computed by its output signals. The semantic obligation is

\[
\forall x\in\{0,1\}^n:\quad \llbracket G\rrbracket(x)=F(x).
\]

The official assignment counts the area of **all listed gates** and measures longest-path delay. The official PASS predicate additionally checks valid file format, full truth table and positive resource caps; \(D(G)>D_{\rm target}\) causes a score penalty but is not by itself FAIL. The source's internal preference for target-feasible candidates is an engineering decision, not a separate logical correctness obligation.

## B. Verified logical constructions (mathematical claims)

### B1. Shannon exactness and ROBDD reductions

Fix variable \(x_i\), with cofactors \(f_0\) and \(f_1\). Then

\[
f=(\neg x_i\land f_0)\lor(x_i\land f_1).
\]

*Proof.* Evaluate at \(x_i=0\) and \(x_i=1\). These two substitutions yield \(f_0\) and \(f_1\), respectively. By induction on the number of remaining variables, the recursive decomposition is exact. A node with equal children computes that common child; interning identical (variable, low, high) triples merges equal expressions without changing their semantics. Complement-edge normalization follows from \(\neg(\neg f)=f\). **This does not prove minimum mapped gate area.**

**Code anchors:** `synth.cpp:299–311` for reduced complemented BDD creation; `synth.cpp:395–435` for physical Shannon lowering.

### B2. Exact affine synthesis

For Boolean inputs, \(a\oplus b=(a\lor b)\land\neg(a\land b)\). The right-hand side can be proved by four-row truth table. By associativity and commutativity of XOR, a balanced pairing of leaves constructs any \(c\oplus\bigoplus_{i\in S}x_i\). Every internal XOR must be realized using AND2/OR2/NOT. A balanced *pairing* may reduce critical-path depth for equal-delay subexpressions, but the code's ready-time priority queue is a heuristic for unequal arrivals; it is not a global delay-optimality theorem.

**Code anchors:** `synth.cpp:317–334,380–405`; `r90_stream.hpp:85–115`.

### B3. Output-preserving local gate identities

Examples used by the actual builder include

\[
\begin{gathered}
a\land 0=0,\quad a\lor 0=a,\quad a\land a=a,\\
a\lor\neg a=1,\quad \neg\neg a=a,\\
a\land(b\lor c)=(a\land b)\lor(a\land c),\\
\neg(a\land b)=\neg a\lor\neg b.
\end{gathered}
\]

All identities are pointwise exact. A structural hash merges only *syntactically identical* typed gates after canonicalizing commutative fanin order; it is not a complete semantic equivalence oracle.

**Code anchors:** `typed_netgraph.hpp:114–145`, `r8_structural.hpp:20–137`, `r84_cut.hpp:35–130`.

## C. Gates, sharing, cost and time (conditional lemmas)

### C1. Live gate cost versus local expression size

Let \(L(G)\) be the union of gate ancestors reachable from *all* primary outputs. Suppose both \(G\) and \(G'\) have been pruned so their stored gates coincide with their respective reachable sets, and all gate-type prices are unchanged. Then

\[
\begin{split}
A(G')-A(G)=
&\sum_{v\in L(G')\setminus L(G)}a(v)\\
-&\sum_{v\in L(G)\setminus L(G')}a(v).
\end{split}
\]

This is an exact identity when vertices in unchanged shared portions are identified consistently. Merely deleting one fanin use does not remove a gate that remains reachable through another output; replacing a root can also prune an entire private cone. Thus neither number of syntactic operators in a rewritten expression nor the local cut estimate generally equals the full graph cost change.

**Implementation nuance:** `r51::Builder::finish()` performs the reachability traversal and gate renumbering (`typed_netgraph.hpp:124–144`). `Graph::metric()` then charges all stored gates (`:26–44`); it does **not** itself delete unused gates. The actual official output file would charge unused listed gates as well. Do not conflate a mathematical definition of *live* area with the official definition of all *listed* gates unless pruning has been performed.

### C2. Exact arrival propagation under topological insertion

Assume a finite directed acyclic gate graph with every fanin inserted before its consumer. Primary input and constant arrival are zero. Assign each new node by the recurrence

\[
T(v)=d(v)+\max_{u\in\mathrm{fanin}(v)}T(u).
\]

Induction on gate insertion order proves the stored arrival is the critical-path delay from a source to that gate; maximizing over all outputs gives the network delay. No probability/statistical assumption is involved.

**Code anchors:** `typed_netgraph.hpp:26–44` and `:114–145`.

### C3. When an old required-time bound is sufficient

Take a feasible original DAG \(G\), set output required times to \(\Delta\), and propagate backward by \(R(u)\le R(v)-d(v)\) along every original dependency. Suppose a subgraph is replaced with an equivalent acyclic subgraph **without altering the unchanged graph's interfaces, gate types or downstream dependencies**. If every replacement boundary root that drives unchanged nodes has new arrival at most its original required time, then the entire resulting DAG meets the target.

*Proof.* Topologically induct through the unchanged nodes. Every source/boundary arrival is bounded by its original required time; for an unchanged node \(v\),
\[
T'(v)\le\max_{u\in\mathrm{fanin}(v)}R(u)+d(v)\le R(v).
\]
Every output consequently arrives by its assigned deadline.

**Where this lemma does *not* apply:** if a rewrite changes graph fanout/dependency relationships, changes boundary membership, or if an earlier rewrite has made old `needed[]` values stale. The source's local filter in `r84_cut.hpp:179–348` uses old required times as an admissibility *heuristic*. The external full-graph delay check before acceptance is the defensible end-to-end safeguard. Do not write "required time proves every accepted rewrite globally target-safe" without these conditions.

## D. Four-feasible cut resynthesis: semantic proof and cost distinction

### D1. Formal cut semantics

A cut \(C=\{\ell_0,\ldots,\ell_{k-1}\}\) is an upstream separating frontier for root \(r\). By recursively evaluating only operations between \(C\) and \(r\), the engine defines a Boolean function \(h_{r,C}(z_0,\ldots,z_{k-1})\), where \(z_i\) are **formal** independent leaf values. For \(k\le4\), enumerating all \(2^k\) assignments yields a signature that fits within 16 bits. If another gate expression \(\widetilde h\) has the same 16-bit signature, then

\[
\forall z\in\{0,1\}^k:\ h_{r,C}(z)=\widetilde h(z).
\]

Substituting the *actual* signals \(z_i=\ell_i(x)\) preserves equality for every primary-input assignment \(x\), whether or not the cut leaves are mutually independent in any stochastic or realizability sense.

*Proof.* The actual vector of cut-leaf values for each input assignment belongs to \(\{0,1\}^k\), on which the two expressions have already been checked equal. Therefore the outputs agree on the actual image of the leaf-signal map.

### D2. Why signature equality is not enough

The signature only certifies the *function between a valid cut and a root*. A valid program replacement additionally requires: the cut must truly intercept every path, the replacement must use allowed gates, no cycles may be introduced, all multi-output dependencies retained, and the actual entire output netlist remeasured under physical costs. These are separately enforced or tested by gate construction, `Builder::finish()` and outer validity/delay/area checks. An exhaustive signature check is not a proof of the entire implementation's correctness if the cut enumeration or graph wiring contains a bug.

### D3. Cut/greedy cover algorithm is incomplete by design

The method limits the cut cardinality to four and retains a bounded number of cuts per node, so it is **not an exhaustive circuit optimization algorithm**. SOP cover choices greedily maximize uncovered truth-table coverage divided by a price proxy and are not necessarily minimum gate-cost covers. The Shannon alternatives sample a limited list of variable orders. Priority root selection uses a heuristic area/slack proxy, not a lower bound on potential gain.

These limitations matter because they explain why additional search passes can yield new improvements *without* contradicting the fact that earlier alternatives were exact Boolean functions. Exact **semantics** and incomplete **optimization search** are perfectly consistent.

## E. Candidate acceptance gives narrow, useful monotonicity

Let \(G_0\) be the incumbent immediately before the final R10.0 `repeat_sop` pass. If the pass is skipped or rejected, the output stays \(G_0\). If accepted, the code checks

\[
\mathrm{valid}(G_1)\ \land\ D(G_1)\le\Delta\ \land\ A(G_1)<A(G_0).
\]

Therefore, **conditional on correct implementation of graph serialization/metrics and completion of that execution**, R10.0's *last pass alone* cannot increase its current incumbent's reported area, and it does not select a target-violating candidate. This property does **not** imply that R10.0 always beats the R9.0 executable, because they may run different clock-bounded candidate paths before the final pass, and it does not imply an upper bound on total runtime or RAM.

**Code anchors:** `synth.cpp:1843–1899`.

The earlier R8.6 `"area"` eligibility has a slightly broader policy: `p.area<base.area` **or** `p.area==base.area && p.delay<base.delay`. Thus do not misstate the entire final algorithm as accepting only strict area decreases at every stage.

## F. Runtime and memory limits: what is and is not mathematically shown

Any program that consumes an arbitrary complete truth table must read \(\Omega(m2^n)\) bits. A ROBDD can be exponentially large in \(n\) in the worst case. Limiting cut cardinality to four bounds *individual local truth signatures*, not the number of candidate graph roots or the total runtime of the complete engine without additional policies.

The code uses time-based checkpoints, branch admission thresholds (for example 65%, 77%, 82%), root-work quotas and small fixed search budgets. But the initial candidate and some legacy operations are not all preempted by a hard supervisor; the system cannot guarantee completion before an arbitrary positive runtime limit. RAM admission estimates are intentionally conservative and do not constitute a peak-RSS theorem. A positive RAM cap may force an explicit failure if compact synthesis cannot solve the case.

**Important distinction:** a runtime-limit policy is a *heuristic designed to improve empirical validity under a watchdog*, not a proof that time usage is less than the limit. The official evaluator records the observed validity separately.

## G. Experimental audit, classified by evidential strength

| Evidence | What it verifies | What it does not verify |
|---|---|---|
| Frozen C++ source hashed; `SOURCE_REGISTRY.csv` | Exact inspected implementation bytes | That this is identical to future team-integrated submission |
| 26/26 `MANIFEST.json` SHA matches | Primary evidence archive integrity | Independent rerun of all historical benchmarks |
| Zeyun and R10 C++17 cold compile | Buildability in this Linux environment | Instructor's final build/runtime environment |
| 20/20 local exhaustive input/output checks | Correctness on five constructed functions × two runtime settings × two solvers | Full correctness on every 20-input function or hidden cases |
| 18-input affine synthetic streaming test; **all \(2^{18}\)** rows independently simulated | The specific R90 shortcut emits an equivalent legal-gate network | Arbitrary 18-input short-budget workloads |
| R10 original official-feedback CSV, two repeats, 25+25 each | Observed 50-case R10 PASS/area/delay/runtime under the archived WSL evaluator run | Hidden cases or unchanged performance after team integration |
| Three-method matched local case table, 300 rows | Paired public-case comparison for Zeyun/Z1, Jincan/J51 and R10/S100, in that run environment | Official scoring function or runtime causal generalization |

## H. Unresolved correctness/security/performance obligations

1. Recheck final integrated code and documentation before submitting it as the team solution.
2. Re-run official 50-case evaluation if integrated source, compiler flags, environment or evaluator changes.
3. Perform targeted RAM-limit tests with valid positive low/mid caps (the compact fallback can fail), and short runtime stress cases beyond easy affine/literal forms.
4. Inspect typical large-n mapped-graph behavior and output memory usage; small smoke tests do not stress worst-case BDD reserve behavior.
5. Keep case-level regressions and failed R5.1 Stage 2/016 in comparative analysis; never drop failing rows and sum only surviving areas as if all methods were feasible.
6. Do not present local cut improvement as global optimality or claim to establish an unpublished grader formula.

**Verdict:** The mathematical core provides strong conditional semantic guarantees for Shannon/BDD construction, exact cut truth signatures, legal gate identities and topological timing. The frozen engineering realization adds explicit global candidate validation. However, absolute software correctness, hard runtime/RAM compliance and globally optimal area remain empirical/unsolved obligations. This distinction must be preserved in the eventual Method and Limitations discussions.

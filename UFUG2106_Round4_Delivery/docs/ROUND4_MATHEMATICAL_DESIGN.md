# UFUG2106 — Round 4 Mathematical and Algorithmic Design

**Scope:** an optimization *extension* of the frozen Round 3 C++17 truth-table-to-circuit synthesizer. It is not a claim of a globally optimal Boolean circuit or of a novel logic-synthesis theorem.

**Source correspondence:** `src/synth.cpp` orchestrates Round 3 candidates and Round 4 postprocessing; `src/polarity_mapper.hpp` implements phase optimization and mapping; `src/algebraic_mapper.hpp` implements structure-preserving algebraic rewrites. `src/synth_round3_frozen.cpp` is retained unchanged for provenance and comparisons.

## 1. Motivation and constrained optimization problem

The project accepts only `AND2`, `OR2`, `NOT` gates, with case-specific areas \(a_{\land},a_{\lor},a_{\neg}\), delays \(d_{\land},d_{\lor},d_{\neg}\), and output arrival limit \(D_{\mathrm{target}}\). The semantic constraint is \(C(x)=F(x)\) for every input row. The time constraint is

\[
D(C)=\max_{j\in[m]}T(y_j)\le D_{\mathrm{target}},\qquad
T(g)=\max_{u\in\mathrm{fanin}(g)}T(u)+d_g.
\]

With gate sharing, area is \(A(C)=\sum_{g\in \mathrm{reachable}(C)}a_g\): each emitted and reachable gate is charged once. The project has not supplied a closed numerical score formula, so Round 4 uses **delay feasibility first, then area** as a candidate-ranking rule. Neither this ranking nor the sum of 25 case areas is necessarily the official grade.

Round 3's timing-aware De Morgan rewrite can recover considerable area, but its decisions are mostly made while traversing gates under a specific intermediate representation. Two related opportunities remain: globally choosing signal polarity and simplifying Boolean expressions spanning multiple gate levels.

## 2. Phase/polarity as a representational decision

For each normalized internal DAG node \(v\), define its logical Boolean function \(f_v\). Introduce a **phase bit** \(p_v\in\{0,1\}\) and represent the output of this node by

\[
q_v=\neg^{p_v}f_v,
\]

where \(\neg^0 f=f\) and \(\neg^1f=\neg f\). Signal phase does not change the logical function at the final outputs; it changes which polarity is *stored* as a gate output and where a physical NOT must be inserted.

Normalize an old netlist by treating old `NOT` gates as inversion bits on references. Let an input reference to node \(u\) carry inversion bit \(e\); it denotes \(\neg^e f_u\).

For an AND node with two child references \((a,e_a)\), \((b,e_b)\):

\[
 f_v=(\neg^{e_a}f_a)\land(\neg^{e_b}f_b).
\]

Two equivalent physical realizations are:

\[
\begin{aligned}
p_v=0:&\quad q_v=(\neg^{e_a}f_a)\land(\neg^{e_b}f_b),\\
p_v=1:&\quad q_v=(\neg^{1\oplus e_a}f_a)\lor(\neg^{1\oplus e_b}f_b).
\end{aligned}
\]

The second identity is simply De Morgan's law. OR nodes are dual: an OR becomes AND under output inversion. Given the stored child signal \(q_u=\neg^{p_u}f_u\), a parent requiring \(\neg^{p_v\oplus e}f_u\) can obtain it by either using \(q_u\) directly (when \(p_u=p_v\oplus e\)) or emitting a shared `NOT` (when unequal).

In C++ we implement:

```cpp
required_child_phase = parent_phase ^ edge_inversion;
physical_op = logical_op ^ parent_phase; // AND2=0, OR2=1
if (required_child_phase != child_phase) use_shared_NOT(child_output);
```

Inputs and constant-zero start in positive phase. Any requested negative phase of constant-zero produces a legal constant-one signal `NOT 0`.

### 2.1 Structural correctness proof

Induct over a topological order of the normalized DAG.

**Base:** each primary input and constant-zero node represents its specified function. A physical NOT gives precisely the opposite phase.

**Inductive step:** suppose every already mapped predecessor \(u\) correctly computes \(q_u=\neg^{p_u}f_u\). Before synthesizing a parent gate, insert a NOT on a child edge exactly when its required and available phases differ. Thus each parent receives the precisely required logical child signal. If \(p_v=0\), use the original AND/OR operation. If \(p_v=1\), use the dual AND/OR operation on inverted inputs; De Morgan's laws give \(q_v=\neg f_v\). Therefore the invariant holds for \(v\).

At each final output the required phase is the original output-reference inversion bit, and a physical NOT is used if necessary. The emitted final output thus equals the original netlist's output for every input assignment. Structural hashing, constant folding, and reachability pruning preserve these equalities. \(\square\)

## 3. Global polarity cost surrogate and search

A naïve local De Morgan decision overlooks sharing: if multiple consumers require a node's opposite polarity, one physical NOT can serve all of them.

Round 4 proposes a phase assignment \(p\) using a surrogate area objective:

\[
\widehat A(p)
=\sum_{v\in V_{\mathrm{binary}}}a_{\operatorname{op}_v\oplus p_v}
+a_{\neg}\sum_{u\in V\cup X\cup\{0\}}
\mathbf{1}\{\text{some consumer or output requests the opposite of }p_u\}.
\]

The first term counts one AND/OR gate per logical binary node, using the gate type selected by its phase. The second term estimates one shared inversion per source whenever at least one of its consumers needs the opposite phase. In particular, it **does not multiply a NOT cost by the number of fanouts**.

This objective is *not* the exact realized area: it does not capture structural hashing collisions, constant folding, dead gates, or all timing effects. Accordingly, it is used **only to propose candidate phase assignments**.

The implementation tests several deterministic initializations (positive, negative, gate-cost-driven) and uses coordinate descent: flip one internal node's phase only when the surrogate decreases. For each tentative flip, only the unary gate cost, its own outgoing polarity demands, and the polarity demands on its two incoming sources need re-evaluation. The search terminates at a one-bit local optimum or a preset number of sweeps. No global optimality is implied.

Each completed phase candidate is reconstructed into actual `AND2/OR2/NOT` gates and its reachable-gate **actual area** and **actual output delay** are computed. Candidate acceptance uses the *realized* netlist metrics, not \(\widehat A\).

## 4. Algebraic rewrites spanning two levels

The independent algebraic pass rebuilds the DAG with global gate hashing and applies functionally exact identities, including:

**Idempotence and absorption:**

\[
A\land(A\lor B)=A,\qquad A\lor(A\land B)=A.
\]

**Complement absorption:**

\[
A\land(\neg A\lor B)=A\land B,\qquad
A\lor(\neg A\land B)=A\lor B.
\]

**Distributivity / factoring:**

\[
(A\land B)\lor(A\land C)=A\land(B\lor C),
\]
\[
(A\lor B)\land(A\lor C)=A\lor(B\land C).
\]

The implementation matches actual DAG structures (not sampled truth-table signatures), so each transformation is an identity. It also collapses double negation and recognizes constants and complementary operands. A specific rewrite may increase area when previous subexpressions were shared by other outputs; therefore the **full final circuit** is always remeasured, and a worse candidate is rejected.

The algebraic and phase passes are composed in both orders, because the result of one pass can expose patterns for the other. This is deterministic heuristic exploration, not complete equivalence-class enumeration or SAT-based exact synthesis.

## 5. Variable ordering and bounded candidate construction

Different BDD orders can yield radically different numbers of distinct cofactors. Besides the Round 3 natural/influence-descending/reverse strategies, Round 4 tests rotated and influence-ascending orders on eligible cases (dimension and declared runtime permitting). This uses the original truth table and does not branch on case filenames.

An unconstrained experiment showed that certain extra permutations can take far too long, even though they are logically valid. Hence the Round 4 implementation adds a **cooperative per-extra-candidate timeout** with periodic checks during truth-table traversal, BDD construction, and gate mapping, plus a BDD node cap for these extra candidates. On timeout the partial candidate is discarded, preserving the already completed solution.

There remain limits: the **original Round 3** candidate generation, and noninterruptible postprocessors, do not have a universal hard real-time guarantee. The 25 published-case PASS status and two generated stress cases are empirical evidence, not a proof that arbitrary input limits are always satisfied.

## 6. Global selection and proof of non-regression under the selected ranking

Let \(C_3\) be the completed Round 3 candidate and \(\mathcal S\) the set of completed Round 4 candidate circuits. The implemented selector compares

\[
\rho(C)=\bigl(\max(0,D(C)-D_{\mathrm{target}}),\ 
 A(C)\text{ if }D(C)\le D_{\mathrm{target}}\text{ else }0,\ D(C),\ A(C)\bigr)
\]

lexicographically, retaining the smallest. If \(C_3\) satisfies its target, no accepted new candidate can violate that target, and no accepted new candidate can have strictly larger area. This property is conditional on correct circuit statistics and successful completion; it does **not** imply that synthesis will always finish under arbitrary runtime or memory limits.

Every transformation from original network to proposed candidate has a Boolean identity or a structural-induction argument. Candidate comparison then concerns area/timing, not semantic validity. For empirical assurance, the released test circuits are independently verified with a bit-parallel simulator and the instructor's evaluator.

## 7. Complexity, assumptions and research limitations

- Truth-table input already has \(\Theta(m2^n)\) bits. Worst-case BDD size is exponential in \(n\), and gate mapping can be costly for poor orders.
- A single phase-map construction is \(O(|V|+|E|)\) expected time given amortized hash operations. Each coordinate-descent sweep visits vertices and their fanouts and has approximately \(O(|V|+|E|)\) work for typical bounded-fanin DAGs; multiple candidates multiply this cost.
- Algebraic rewriting is linear in the size of the netlist under hash-table assumptions for bounded-depth patterns, excluding hash reallocation and parser costs.
- Gate cost and delay are the *per-case* parameters. There is no fixed universal gate-library preference.
- Global area recovery may have a nonconvex landscape; one-bit polarity descent can stick at a local optimum, and neither phase search nor distributive rewriting guarantees global minimum area or minimum delay.
- Multioutput sharing means that locally fewer gates can globally **increase** area. This is why the program evaluates complete reachable Netlists before acceptance.
- Report both resource cost and circuit quality. The extra search is not free.

## 8. Suggested later investigations (not yet implemented)

1. Replace one-bit coordinate descent with timing-aware phase optimization or a stronger binary-label optimization model; preserve exact output delay bounds.
2. Enumerate small cuts and perform library-based technology mapping rather than only two-level algebraic patterns.
3. Implement a unified interruptible `synthesize_candidate` API with memory accounting, so every optional candidate respects a strict runtime budget.
4. Evaluate on fresh Stage 2/hidden-case-like data before interpreting area improvements as generalization.

**Academic provenance:** These are established Boolean identities and standard synthesis ideas. The Round 4 implementation is an original modification of our frozen Round 3 code, motivated in part by reviewing public optimization techniques, including the peer repository `https://github.com/zdu881/UFUG2106-Project`. Do not describe these textbook identities as new theorems or use another group's source without attribution and license review.

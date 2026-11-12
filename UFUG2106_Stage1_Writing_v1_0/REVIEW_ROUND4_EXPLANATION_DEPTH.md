# Manuscript Review — Round 4: Explanation Depth and Academic Quality

**Base:** Draft v0.5 (narrative revision)  
**Output:** Draft v0.6 (deep-exposition revision)  
**Review standard:** A reader with undergraduate discrete mathematics, but no prior logic-synthesis experience, must be able to follow every introduced object, verify every displayed elementary identity, and understand why the engineering choice followed the measurement. The Technical Report should remain a research argument, not a tutorial chapter.  
**P0:** Deferred per student instruction. Neither claimed individual contributions nor the AI-policy statement was finalized in this pass.

## I. Diagnosis: four recurring explanation gaps

| Gap | Why it matters | Revision |
|---|---|---|
| Functions, ROBDDs, and hardware gates were adjacent without a sharp boundary | A canonical BDD can be misread as a minimum-area circuit; a complemented BDD edge can be misread as a free inverter | Explained semantic vs structural sharing, explicitly priced the MUX lowering, and restated the four distinct research objects |
| Heuristic ordering and SOP/POS covers were introduced faster than their mathematical motivation | “Influence” can sound like an optimality measure; greedy cover can sound like approximate correctness | Derived the exact influence of *both* outputs in a running example; gave the two-implication proof that a selected implicant cover is logically exact |
| Shared fanout was discussed without showing which physical gates actually survive | A local reduction need not reduce total live-gate area; required time changes when consumers change | Introduced the output-reachable live-node set and explicit area accounting; recomputed a primary output's required time after its downstream consumer is removed |
| Cut masks and Typed DAG semantics were stated but not made checkable | A four-input cut can sound like a black box, and typed-graph optimization can sound equivalent to a proof about implementation | Worked out the three-input mask 0xCE, explained formal-boundary equivalence and acyclicity, and supplied a conditional typed-graph preservation proposition |

## II. Core mathematical checks

### A. The multi-output example, reused across several stages

Let `f1 = (a AND b) OR (NOT a AND c)`, `f2 = f1 OR b`. After absorption, `f2 = b OR (NOT a AND c)`.

For a fixed selector `a`, the Shannon cofactors are:

| Output | a = 0 | a = 1 |
|---|---|---|
| f1 | c | b |
| f2 | b OR c | b |

Both BDD roots may point to the **same residual function** `b`; it is not a BDD terminal constant. The earlier wording “terminal subproblem” was corrected.

The example's physical netlist uses gate IDs 4 through 8 with outputs (7, 8), AND2 area/delay 2/2, OR2 area/delay 3/2, NOT area/delay 1/1. The original circuit has area 11 and delay 7. Replacing only the second output's OR2 arguments with `(b, NOT a AND c)` leaves the first output and every emitted gate alive; area remains 11 but delay falls to 5. With a target of 8, the old required time for gate 7 is `min(8,8-2)=6` because gate 7 is both a primary output and gate 8's fanin. After the rewrite, gate 7 has no downstream consumer other than its own primary-output role, so its **new** required time is 8. This calculation illustrates why old required times cannot be reused after changing fanout.

### B. Influence is not an optimal ordering oracle

For each variable, compute its Boolean influence as the fraction of other-variable assignments for which toggling that variable changes the output:

| Function | I_a | I_b | I_c |
|---|---:|---:|---:|
| f1 | 1/2 | 1/2 | 1/2 |
| f2 | 1/4 | 3/4 | 1/4 |

Although `a` is the selector for `f1` and `b,c` are its data inputs, all three influences tie. Therefore influence carries information about sensitivity, **not** a guarantee on the BDD size or weighted mapped-gate cost. Multi-output aggregation is an additional heuristic choice.

### C. Why a prime-implicant cover is functionally exact even when greedy

Let selected cubes `c_j` satisfy `c_j => f` for every cube and `f => OR_j c_j` for every assignment in the on-set. The two implications give `f = OR_j c_j` for all assignments. The optimization heuristic is choosing **which valid cubes** to use, not making the function approximate. For the example, `b` and `NOT a AND c` are sufficient cubes; distributivity also gives the exact POS `(b OR NOT a) AND (b OR c)`. The best **mapped** cost still depends on area/delay prices and sharing.

### D. When a cut truth-mask substitution is justified

With leaves `(a,b,c)` indexed as `s=4a+2b+c`, `f2` is 1 on rows `1,2,3,6,7`. Its 8-bit truth mask is `206 = 0xCE`. The equality of two candidate masks on every **formal** leaf assignment is a sufficient functional replacement condition even if, in the real network, those leaves have correlated values. However, this alone does not check acyclicity, legal gate types, output connections, or actual area. The complete output-reachable DAG must be rescored.

### E. Why the typed-DAG claim is conditional

The new proposition explicitly assumes: topological construction, exact Boolean identities, hash-consing on identical operator/operand keys, and reachability from **all** primary outputs. Under these conditions, induction shows that the emitted graph preserves output functions, and its gate-count area/arrival recurrences match the prescribed library. These conditions are **not** a formal verification of every C++ branch. The source freeze, official evaluator, property-based tests, and independent checker provide separate implementation evidence.

## III. Technical Report: appropriate depth and limits

New material focuses on the mathematical claims directly needed to evaluate the **frozen Round 5.1** design and to interpret the **Round 6** research branch. It does not expand all nine rounds into full tutorials, and it does not claim new theory for Shannon expansion, ROBDDs, or DAG rewriting.

The added exact live-gate accounting is especially important:

`A(G) = sum_{v in L(G)} a(op(v))`, where `L(G)` is the **union** of gates reachable from every primary output. A gate deleted from one consumer's expression may remain live because another consumer still references it. It is incorrect to infer true `Delta A` from the rewritten cone's local gate count alone.

The frozen code's selected candidate and the **official evaluator's numerical grade** are not conflated. The internal ranking and runtime cutoff remain heuristic and clock-dependent; no numeric official scoring formula has been claimed.

## IV. Trial Log: on-ramp for an unfamiliar reader

The single three-input, two-output example is no longer just a standalone worked problem. It now reappears to illustrate cofactor sharing (R1), influence and SOP/POS (R2), timing and fanout requirements (R3), live-gate area (R4/R6), and the concrete local cut truth mask (R6). This makes the mathematical development traceable without requiring the reader to already know logic synthesis.

We retained the negative outcomes: typed graphs are not universally faster on every tiny function; cut rewriting produces modest gains at extra runtime; Stage 2 generalization and globally optimal mapping are unproved.

## V. Independent calculation and evidential boundaries

Run `python3 shared/scripts/verify_deep_exposition.py` from the archive root. It verifies the complete eight-row truth table, SOP/POS identity, two output-influence vectors, XOR/cofactor identity, cut mask 0xCE, area 11, delay 7 -> 5, and required time of shared output 6 -> 8. Output is archived at `shared/tests/v0_6_exposition_check.txt`.

This **new test is for the constructed pedagogical example only**. It is not a new official evaluator run, and does not replace existing Stage 1 verification. No source code, benchmark CSV/JSON, or measured plotting data was changed in this revision. The integrity manifest `editorial/V0_6_EVIDENCE_INTEGRITY.json` lists 34 unchanged evidence files/figures checked by SHA-256.

## VI. Remaining academic limitations

1. No universal minimum-area/minimum-delay proof and no hidden Stage 2 inference.
2. The actual Canvas submission snapshot still needs a final independent check against the research freeze.
3. Individual student contributions and AI-assistance disclosure are still pending fact verification (P0 deferred).
4. All empirical speed claims are scoped to the archived machine/run, and the single Peak RSS observation is not generalized to other cases.
5. A proof of the **specified** transformation does not establish that arbitrary implementation paths satisfy its preconditions. Retain the independent checker and regression tests alongside the manuscript.

**Review decision:** Draft v0.6 is ready for a focused author read-through. Do not treat it as submission-final before verifying authorship, the course policy, and the actual submitted code archive.

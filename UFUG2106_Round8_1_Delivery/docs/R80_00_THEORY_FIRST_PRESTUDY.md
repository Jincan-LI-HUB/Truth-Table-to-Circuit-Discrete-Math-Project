# UFUG2106 — Round 8 Theory-First Research Design (v0)

**Status (2026-11-21):** research design and independent baseline structural profiling; **not** a Round 8 synthesis implementation, official evaluation or proof of global optimum. Frozen quality baseline: Round 7.2. Preserve frozen binaries, manifests, CSVs, and the official evaluator.

## 0. Research questions and evidence boundary

Our goal is a *best-known feasible circuit under the course's allowed gate library, finite runtime and memory*, not an unqualified claim of globally optimal circuit size. The exact official score formula has not yet been confirmed; consequently the research uses a feasibility-first Pareto comparison of area, delay and runtime rather than a fabricated weighted scalar objective.

Let \(G\) be the live, multi-output gate DAG; each gate \(v\) has operation \(\mathrm{op}(v)\in\{\mathrm{AND2,OR2,NOT}\}\), cost \(a_{\mathrm{op}(v)}\), and delay \(d_{\mathrm{op}(v)}\). Define

\[
 A(G)=\sum_{v\in \operatorname{live}(G)}a_{\mathrm{op}(v)},\qquad
 t(v)=d_{\mathrm{op}(v)}+\max_{u\in \operatorname{fanin}(v)}t(u),\qquad
 D(G)=\max_{o\in\operatorname{outputs}(G)}t(o).
\]

The search outputs a correct complete DAG; a new candidate is accepted only when the required feasibility checks hold. A local optimality certificate does not certify global optimality because choices can alter cross-output sharing.

**Existing results:** Round 7.2 has 50/50 public PASS and target-met in two paired WSL runs; Stage 1 area 529,014; Stage 2 area 508,535. Previous Round 6.1 cut rewriting gave Stage 1 aggregate area about 528,864 vs Round 5.1 529,014 in one matched experiment, while increasing median runtime from 80.635 to 99.740 ms. This demonstrates that the inherited small-cut flow can improve area, but does **not** demonstrate that the technique is intrinsically ineffective. Its constraints (cuts \(k\le4\), at most 10 retained cuts per node, 4,000 examined roots, 25 ms extra cut time, no local arrival-time increase) substantially constrain the search space.

## 1. New preliminary 25-case Stage 2 structure audit

Method: Re-run the locally compiled Round 7.2 synthesizer on the 25 supplied Stage 2 cases, parse each generated AND2/OR2/NOT netlist, compute exact live-gate area, delay, and reverse output-cone reachability. A gate is **cross-output shared** iff reachable in the cones of at least two output terminals. These local direct-run timings are **not comparable** to official WSL runtimes; area and delay were checked against the user's official Round 7.2 Stage 2 CSV (25/25 exact matches).

| Case | Area | Live gates | Gates in 2+ output cones | Share rate | Notes |
|---|---:|---:|---:|---:|---|
| stage2/013 | 115734 | 56871 | 5867 | 10.3% | Large multi-output network, low observed cone overlap |
| stage2/005 | 112221 | 51025 | 14787 | 29.0% | Large, notable overlap |
| stage2/014 | 62535 | 31502 | 1867 | 5.9% | Large, very low observed cone overlap |
| stage2/002 | 58697 | 36889 | 3125 | 8.5% | Large, low observed overlap |
| stage2/021 | 22590 | 11808 | 8215 | 69.6% | Strong existing multi-output sharing |
| stage2/016 | 1781 | 1120 | 204 | 18.2% | Short-budget scheduling probe, not representative of large cones |

Top four Stage 2 areas sum to 349,187 / 508,535 = about 68.7%. Median cross-output shared-gate fraction across the 25 cases is 15.9%. **These facts show heterogeneous generated structures, not that an optimal network must have more sharing.** More shared gates may increase depth or block local refactoring. The profiler's `shared_pct` has an operational definition: output-cone overlap, not a proof of redundant computation.

Interpretation: one global rewrite algorithm and one fixed resource budget are questionable. Evaluate improvements conditional on structure, cost regime, output sharing, and timing slack; use these as exploratory features but do not tune thresholds by case ID.

## 2. Literature-derived hypotheses rather than tool name transplantation

### H1. Quality depends on the final weighted gate mapping, not merely on AIG node count

ABC's AIG rewriting minimizes AIG nodes/levels, where complement edges are essentially free. Our evaluator charges a positive cost for NOT and may charge a dramatically different area/delay for OR2 versus AND2. For example, with \((a_\land,a_\lor,a_\neg)=(2,8,1)\), direct \(x\lor y\) has area 8, while \(\neg(\neg x\land\neg y)\) costs 5 if all three NOTs are new; timing can worsen. If inverted phases are already shared, actual incremental area changes again. Thus we should maintain **several equivalent implementations** and evaluate with per-case gate costs and actual arrival times, rather than select one AIG-node-minimal solution before mapping.

### H2. Share-aware global cost matters more than a purely local node gain

For a replacement \(G\mapsto G'\), the valid area delta is

\[
\Delta A=\sum_{v\in\operatorname{live}(G')}a(v)-\sum_{v\in\operatorname{live}(G)}a(v).
\]

Local MFFC reclaimable area is useful as a cheap filter, but it cannot certify global multi-output gain. Use an estimated area-flow ranking followed by exact live-DAG cleanup/cost evaluation and equivalence verification. Require an acceptance rule that measures *all output paths*, not merely the rewritten root's arrival time.

### H3. Timing slack should be available to the optimizer

Set \(r(o)=D_{\rm target}\) at each output. Propagate required times backward through each gate by \(r(u)\gets\min(r(u), r(v)-d(v))\). A candidate with a slower local root can still be legal when it fits the relevant backward required time. The old Round 6.1 local condition \(t_{\rm new}(v)\le t_{\rm old}(v)\) is conservative; replacing it with required-time feasibility may admit lower-area implementations. The actual global delay must be checked after rewriting because DAG reconvergence and gate sharing can modify timing.

### H4. Structural choices, not a single greedy incumbent, can unlock future savings

ABC's zero-cost rewriting and the 2025 CRISTAL choice-network work show why retaining a bounded set of equivalent structural alternatives can reduce structural bias. Store a small cost-aware Pareto set of candidate *implementations* per cut or cone, with per-case timing and phase information, and defer committing to a unique graph until the global mapping/cleanup step. Bound the number of variants and track memory and runtime.

### H5. Resubstitution / multi-output factoring is a different hypothesis from cut rebuilding

A local cut rebuilt from its leaves can miss a nearby already-computed divisor from a *different* output cone. Explore DAG-aware divisors and multi-output sharing using bounded windows, fanout/reference counts, simulation signatures, and exact Boolean equivalence tests. Do not treat syntactically similar expressions as equivalent without verification. Early structural evidence shows case-dependent sharing rates but does not yet establish feasible savings.

### H6. Espresso order effects cannot be inferred from published generic results

The 2024 structural-bias study documents substantial harm from standard multi-output two-level preprocessing for **heavily incompletely specified** functions. Our input truth tables are completely specified, so this is **not direct evidence** that multi-output minimization is harmful here. It is strong reason to compare the *order* of two-level factoring, multi-level rewriting, and mapping instead of assuming that a locally minimized PLA is the best intermediate representation.

## 3. Proposed multi-stage experimental design

### Stage A — Feasibility of structural improvement (offline, with generous research budget)

Freeze Round 7.2 outputs for comparison. Build a BLIF/Verilog export of the existing netlists; use ABC scripts (e.g. `strash`, `balance`, `rewrite`, `refactor`, `resyn2`, `choice`) as **offline structural comparators**. Remap every result to the three allowed gates using the per-case cost/arrival data, and independently check the truth table. **ABC's native AIG node count and ABC's own timings are not the course score.** The external comparator must not silently become a forbidden runtime dependency.

Establish at least two alternative structural initializations per case: (1) the existing ROBDD/Shannon solution; (2) AIG-canonicalized output; optionally (3) two-level/factored output for support-small or structurally promising cases. Keep complete generated netlists and per-stage metrics to diagnose where savings are lost.

### Stage B — Cost-aware synthesis/mapping, keeping representations separate

Implement a local \(k\le 4\) truth-table candidate library for direct AND2/OR2/NOT implementations and their complemented-polarity variants; use NPN canonicalization as an index, **not** as a blanket guarantee that all phases have the same cost. Generate several non-dominated (incremental area, arrival time, polarity, sharing) alternatives. For isolated small cuts one can use bounded exhaustive/SAT synthesis to obtain local optimality certificates; these do not prove global network optimality.

Run cut enumeration with alternative priority policies: high MFFC reclaimable area, high critical slack, and high sharing prospect. Measure candidate-eligible count, candidate-generation time, fractional usable time, accepted substitutions, and area gain per millisecond. Expose rollback on invalid or non-improving full networks.

### Stage C — Resubstitution and choice-network integration

Generate a bounded divisor set from fanins, sibling cones and other outputs, and use bit-parallel simulation to prefilter candidates. Apply SAT/complete truth tables where feasible, or prove equivalence algebraically for restricted patterns. Record the maximum reachable live-DAG gain and use MFFC/refcount-aware prioritization. For a finite set of structural alternatives, test both rewrite→resub and resub→rewrite: they are not assumed to commute.

### Stage D — Real-runtime scheduling and final selection

Retain the frozen R7.2 circuit as a *correct fallback*. Heavy experiments may inform the best algorithms, but the submitted single-thread executable must obey the actual per-instance Runtime/RAM limits and output format. Admit structural search only when the remaining budget supports it; commit an alternative only after functional validation and global metrics. Keep the short-budget R7.2 path intact unless a rigorously measured improvement is established.

## 4. Factorial testing: distinguish method failure from integration failure

Use at least the following controlled configurations, with same input, same machine, frozen seeds, and paired reversed order:

- baseline R7.2;
- weighted mapping only;
- structural rewrite only (then conventional remap);
- rewrite + weighted mapping;
- resub only;
- resub + weighted mapping;
- rewrite → resub → mapping;
- resub → rewrite → mapping;
- bounded structural choice + mapping.

Measure (a) synthesis representation cost, (b) post-mapping live-DAG area, (c) worst output delay and slack, (d) official pass/target metrics, (e) total and per-stage runtime and memory, (f) candidate acceptance and failure reasons. Interactions can be quantified by the difference-in-differences for an objective such as area:

\[
I_{AB}=A_{AB}-A_A-A_B+A_0.
\]

A negative value means combined area improvement exceeds the additive prediction for the same fixed inputs, but *only if each named configuration is functionally valid and comparable*. Repeat for delay and evaluate feasibility separately. Do not call a single extreme good case a global improvement.

## 5. Anti-premature-rejection decision ladder

If an algorithm fails, classify before abandoning it:

1. **Logical validity failure:** mathematical assumption, cut boundary, don't-care or DAG replacement bug. Reject the implementation, not the technique.
2. **Local improvement but no global area gain:** mapping mismatch, fanout sharing, timing violation or structural context. Test cost-aware mapping / context-aware resub / alternative order.
3. **Excellent quality but runtime limit failure:** scheduling/engineering problem; run offline quality exploration, then budgeted version or selective windows.
4. **No candidate improvement even offline:** representation/candidate-library deficiency; compare with ABC/exact small-cut reference. If the alternatives also fail under matched conditions, deprioritize with documented evidence.
5. **Only public gains, holdout declines:** apparent overfit; retain experiment as research, do not promote to release.

A method should go through at least the relevant algorithm-only, mapping-aligned, and integrated/adequately-budgeted tests before a final NO-GO recommendation. Conversely, reserve explicit caps on development time and memory to prevent endless unproductive search.

## 6. Promotion gate and statistical discipline

**Feasibility:** 50/50 public cases pass and satisfy target delays in repeated paired runs; inspect timeout-sensitive cases and max runtime/limit utilization. Generate independent structured holdouts using preregistered seeds; include random, arithmetic/structured, high-sharing, low-sharing, skewed output density, and asymmetric gate-cost classes.

**Quality:** per-case exact area/delay and runtime against the same-run R7.2 control, 50-case area sum, paired geometric mean ratios, count improved/equal/regressed, relevant quantiles, and objective sensitivity to unknown grading weights. Track one-sided wins and losses; maintain a Pareto frontier. Avoid the invalid calculation that treats a FAIL case as area zero.

**Reproducibility:** save source SHA, compiler flags, machine info, official CSV, candidate-level trace, netlist SHA, independent verifier results, and automated feedback ZIP even on failure. This allows later paper sections to distinguish hypotheses, method, ablations, empirical facts, and limitations.

## 7. Source reading list (directly relevant statements)

1. Berkeley ABC documentation, DAG rewriting and zero-cost replacements, AIG balancing and common factoring: https://people.eecs.berkeley.edu/~alanmi/abc_old/ . The native AIG objective is **not** the per-case weighted gate library objective.
2. mockturtle v0.4 extended technology mapping and exact-library graph mapping: https://mockturtle.readthedocs.io/en/latest/algorithms/mapper.html . It explicitly distinguishes cut priority by delay and area-flow and supports technology libraries.
3. mockturtle v0.4 cost-generic resubstitution: https://mockturtle.readthedocs.io/en/latest/algorithms/cost_generic_resub.html . A starting point for a custom weighted cost evaluator, not a ready-made drop-in proof of optimal mapping.
4. Chen, Yin & Yu, *Revisit Choice Network for Synthesis and Technology Mapping*, 2025: https://arxiv.org/abs/2508.14068 . Evidence for prioritizing **high-quality choices** rather than blindly accumulating many equivalent networks.
5. *New Stories on the Structural Bias in Logic Synthesis* (IWLS 2024): https://users.fit.cvut.cz/~fiserp/papers/iwls24.pdf . Its negative multiple-output preprocessing result specifically concerns **heavily incompletely specified** functions.
6. Reichl, Slivovsky & Szeider, *eSLIM: Circuit Minimization with SAT Based Local Improvement*, SAT 2024: https://drops.dagstuhl.de/entities/document/10.4230/LIPIcs.SAT.2024.23 . Supports bounded local exact synthesis, not global optimality under course runtime constraints.

## 8. Decision at this point

**GO for Round 8 theory-first prototyping; NO claim of an optimized Round 8 delivery yet.** The initial high-value combination to test is **weighted/polarity-aware candidate mapping + DAG-global cost and required-time checks**, with bounded structural choices and resubstitution as separate, ablatable extensions. A negative result in one standalone rewrite pass is not sufficient to discard the literature technique; neither is a positive AIG-level result sufficient for release.

## 9. Replication script (WSL/Linux)

The attached `profile_structure.py` is an **offline structural audit**, not a replacement for the official evaluator. After compiling Round 7.2, run from the Project Root:

```bash
python3 profile_structure.py --cases data/stage2 --program UFUG2106_Round7_2_Delivery/build/synth_round72 --output Round8_PreStudy/structure --official-csv UFUG2106_Round7_2_Delivery/results/<TIMESTAMP>/run1_stage2_r72_shortlist.csv
```

Replace `<TIMESTAMP>` with the real folder. The script stores generated netlists in the chosen output folder and verifies area/delay against the optional official CSV. Its direct-run milliseconds are environment-specific and **must not** substitute for official evaluator timings.

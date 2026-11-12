# UFUG2106 Stage 1 — Round 3 Optimization Research Report

**Date:** 2026-11-11  
**Basis:** the published 25 Stage 1 cases, their dynamic gate-cost parameters, the course's Linux Evaluator, the earlier in-conversation Portfolio synthesizer, and the publicly described peer reference implementation.  
**Result:** 25/25 PASS, 25/25 Target Delay Met; aggregate Area 533,705 on the final completed run (core-only version: 543,209).

## 1. What changed, and why

Previous research established that Shannon decomposition, BDD sharing, two-level expansion and SOP/POS implicant cover could generate correct circuits and achieve 25/25 target delays. Yet Area remained 790,243 (the earlier Portfolio). This round focuses on **area recovery under timing constraints**, complemented-subfunction sharing, affine detection, DAG balancing, and bounded variable-ordering search. We did **not** try to identify a unique hidden original circuit; many different circuits implement the same truth table.

We treat every test case's AND2, OR2, and NOT Area/Delay as dynamic inputs. No fixed default gate costs are assumed. The score formula has not been published, so our candidate rank is an engineering heuristic: prefer a valid circuit meeting the target, then smaller total Area, with Delay as a tie-breaker. Case-area aggregation is a diagnostic, not the teacher's numerical score.

## 2. Mathematical foundations and correctness

### 2.1 Complemented-edge ROBDD

The truth table defines a function \(f:\{0,1\}^n\rightarrow\{0,1\}^m\). For each output, use Shannon's identity

\[
f=\neg x\land f_0\;\lor\; x\land f_1,
\qquad f_b=f\vert_{x=b}.
\]

Our BDD stores terminal False as literal 0 and True as literal 1. A nonterminal literal is represented as \(L=2p+\sigma\), with the low-order bit \(\sigma\in\{0,1\}\) indicating whether the function represented by regular node \(p\) is complemented. When creating a node with children \((\ell,h)\), choose \(\sigma=h\bmod 2\), complement both child literals if \(\sigma=1\), intern the normalized key \((x,\ell\oplus\sigma,h\oplus\sigma)\), and return the node literal with the same complement bit \(\sigma\).

Why is it correct? Simultaneously complementing both cofactors complements the entire Shannon function. Restoring the complement bit therefore recovers the original function. The unique table shares identical normalized nodes, while the DAG structure remains acyclic because variables are processed in a fixed order. Complemented edges do not directly become free physical NOT gates; the subsequent Gate Mapping still accounts for all emitted NOT gates.

### 2.2 Affine-function recognition

An affine Boolean function has form

\[
f(x)=c\oplus\bigoplus_{i\in S}x_i,
\qquad c\in\{0,1\}.
\]

If a BDD node's children satisfy \(f_1=\neg f_0\) and \(f_0\) is affine, Shannon's identity implies

\[
f=f_0\oplus x.
\]

This is an **exact functional identity**, not a heuristic approximation. Our mapper recognizes such nodes bottom-up and builds balanced XORs from the **only three legal gates**, using

\[
a\oplus b=(a\lor b)\land\neg(a\land b).
\]

XOR detection helps some functions; its absence is not a correctness problem because ordinary Shannon mapping is always available.

### 2.3 Two-level Shannon expansion and DAG balancing

The earlier work already introduced expanding two decision levels. For branch-specific second variables \(u,v\), the exact identity is

\[
\begin{aligned}
f={}&(\neg x\land\neg u\land f_{00})\lor(\neg x\land u\land f_{01})\\
   &\lor(x\land\neg v\land f_{10})\lor(x\land v\land f_{11}).
\end{aligned}
\]

Terms can be formed in parallel and their OR tree balanced, often reducing the longest path. Our next pass can also flatten AND/OR cones when an internal node has a single fanout. Associativity and idempotence justify the re-parenthesizing and duplicate-leaf elimination; shared subgraphs with multiple fanouts are deliberately not destructively flattened. The final Netlist is always re-pruned and re-numbered.

### 2.4 Main contribution: required-time-driven Area Recovery

Let the starting Netlist already have \(D(C)\le D_{\mathrm{target}}\). Let \(T(v)\) be the arrival time at signal \(v\). Set a **required arrival time** for each output \(y\) by

\[
R(y)=D_{\mathrm{target}}.
\]

Process the old Netlist in reverse topological order. For every gate \(v\) of intrinsic delay \(d(v)\), propagate to each input signal \(u\):

\[
\boxed{R(u)\gets\min\big\{R(u),R(v)-d(v)\big\}.}
\]

If a signal reaches multiple downstream gates, the minimum over all consumers enforces the strictest downstream requirement. We then construct a functionally identical Netlist in forward topological order. For each gate, first construct the direct implementation from its already-mapped inputs. When a De Morgan alternative is cheaper under this case's cost parameters, we may replace an OR2 by AND2 plus inversions, or vice versa:

\[
a\lor b=\neg(\neg a\land\neg b), \qquad
 a\land b=\neg(\neg a\lor\neg b).
\]

The alternative is accepted locally **only when its actual mapped output arrival satisfies** \(T'(v)\le R(v)\). Negations already available in the new network may be reused. For this ablation we use the simple sufficient standalone cost test

\[
a_{\mathrm{OR}}>a_{\mathrm{AND}}+3a_{\mathrm{NOT}}
\]

or its AND/OR dual before attempting a replacement. This is sufficient to make the isolated construction cheaper, not an exact global marginal-Area test; sharing can change the true benefit.

**Timing correctness argument.** For input signals, \(T'=0\). Assume by induction that every mapped predecessor \(u\) satisfies \(T'(u)\le R(u)\). If gate \(v\) keeps its original type, its output obeys

\[
T'(v)=\max_{u\in\mathrm{fanin}(v)}T'(u)+d(v)
\le\max_u R(u)+d(v)\le R(v).
\]

If a De Morgan implementation is selected, our code explicitly checks its actual output arrival against \(R(v)\). Thus the invariant holds for all nodes, and every final output satisfies \(T'(y)\le D_{\mathrm{target}}\). This argument applies to a **valid starting Netlist** with unchanged fanin dependencies; it does not assert that all inputs with arbitrary targets admit a feasible circuit. The final circuit is also independently scored; a candidate is retained only if it improves the complete Netlist ranking, never solely on a local gate estimate.

**Why it improves Area:** the previous fast mapping often rejected cheap De Morgan implementations if they added even one unit of local delay. Here, only delay increases that consume unavailable *end-to-end* slack are forbidden. In cases with an expensive OR2 or AND2, this can recover substantial Area while keeping the required output timing intact.

### 2.5 Bounded variable-order portfolio

The strategy pool includes natural input order and influence-based BDD orderings. For cases whose declared runtime allowance is at least 5,000 ms and \(n\le18\), the final version also tries reverse order once. These conditions depend on the **public input dimensions and resource budget**, not on test-case names or the hidden circuit. Every completed candidate is scored by its reachable, pruned Netlist; only one candidate is emitted. All candidate construction remains single-threaded and sequential.

Variable order can greatly change ROBDD node count, shared subfunctions and eventual Gate Area. A faster-to-build or smaller BDD is not always a smaller mapped circuit. Additional orders therefore require cost-aware screening rather than unlimited random search.

## 3. Full published-case ablation

All figures below are from retained official Evaluator CSVs. Every method passed 25/25 functional tests and met 25/25 target delays. Running conditions are from one local environment, not guaranteed portable runtime measurements.

| Method | PASS | Targets | Area sum | Median Runtime (ms) |
|---|---:|---:|---:|---:|
| Previous portfolio | 25/25 | 25/25 | 790,243 | 55.460 |
| Complemented BDD | 25/25 | 25/25 | 777,324 | 51.728 |
| Affine detection | 25/25 | 25/25 | 770,195 | 49.583 |
| Balanced cones | 25/25 | 25/25 | 762,164 | 75.844 |
| Slack-aware area recovery | 25/25 | 25/25 | 586,218 | 103.259 |
| Area recovery + reverse order | 25/25 | 25/25 | 543,209 | 106.124 |
| Legacy representation as a fallback | 25/25 | 25/25 | 533,705 | 102.302 |

The changes are sequential **ablation configurations**, not a guarantee that each feature improves every case. The Area improvement from the original 790,243 to 533,705 is about **32.46%**. The last candidate-selection expansion improves Area mainly on cases 002 and 024, with a non-negligible increase in runtime. The Stage 2 prototype described in the peer public repository reports Area sum 617,943 on the same published Stage 1 cases; our final 533,705 is lower by about **13.6%** (core-only 543,209 is lower by about 12.1%). Their numbers are source-reported and not independently rerun here; runtime values across environments are not directly comparable.

### 3.1 Per-case results

The original portfolio's results are shown alongside the round-3 final measured results. Negative Area change means an improvement. Per-case output retains both Area and Delay, since neither metric may safely be inferred from the other.

| Case | Old Area | New Area | Δ Area | Old Delay | New Delay | New Runtime (ms) |
|---|---:|---:|---:|---:|---:|---:|
| case_001 | 119,318 | 61,952 | -57,366 | 71 | 62 | 877.104 |
| case_002 | 18,918 | 18,918 | +0 | 60 | 60 | 351.245 |
| case_003 | 27,445 | 24,463 | -2,982 | 54 | 55 | 352.860 |
| case_004 | 7,940 | 4,550 | -3,390 | 55 | 47 | 44.337 |
| case_005 | 1,241 | 700 | -541 | 30 | 31 | 49.548 |
| case_006 | 11,002 | 5,962 | -5,040 | 41 | 46 | 49.600 |
| case_007 | 139,536 | 78,042 | -61,494 | 65 | 71 | 1805.307 |
| case_008 | 15,586 | 8,637 | -6,949 | 56 | 50 | 61.314 |
| case_009 | 23,648 | 14,584 | -9,064 | 41 | 46 | 102.302 |
| case_010 | 4,771 | 4,712 | -59 | 34 | 32 | 366.236 |
| case_011 | 484 | 474 | -10 | 35 | 33 | 61.980 |
| case_012 | 5,760 | 5,359 | -401 | 25 | 25 | 48.253 |
| case_013 | 12,106 | 12,014 | -92 | 55 | 60 | 163.383 |
| case_014 | 11,648 | 11,760 | +112 | 61 | 61 | 734.056 |
| case_015 | 36,345 | 36,345 | +0 | 62 | 62 | 682.201 |
| case_016 | 4,206 | 2,149 | -2,057 | 46 | 40 | 25.675 |
| case_017 | 455 | 440 | -15 | 22 | 22 | 13.510 |
| case_018 | 1,384 | 1,350 | -34 | 29 | 29 | 32.034 |
| case_019 | 9,349 | 5,319 | -4,030 | 51 | 57 | 250.943 |
| case_020 | 776 | 776 | +0 | 30 | 30 | 59.983 |
| case_021 | 28,134 | 28,134 | +0 | 60 | 60 | 752.937 |
| case_022 | 1,336 | 1,334 | -2 | 31 | 32 | 80.688 |
| case_023 | 236 | 215 | -21 | 21 | 21 | 10.130 |
| case_024 | 162,143 | 124,830 | -37,313 | 67 | 72 | 2455.640 |
| case_025 | 146,476 | 80,686 | -65,790 | 53 | 60 | 1280.706 |

### 3.2 Why we retained an earlier synthesizer representation

A single new representation should **not** automatically replace every earlier candidate. Although complemented-edge normalization reduced aggregate Area, it regressed several individual test cases. The final portfolio therefore retains a separately mapped **non-complemented BDD** family in low-risk, moderate-sized cases with sufficient runtime budget. This is not a case-ID lookup: the fallback is triggered solely by \(n\) and the declared Runtime Limit, and it competes against the newer mapper using the same full-Netlist ranking.

On the published cases, this non-regression safeguard recovered Area on cases 002 (27,483 to 18,918), 015 (36,938 to 36,345), 020 (796 to 776), and 021 (28,460 to 28,134), yielding **533,705** in the final single executable. It can trade away timing slack (for example case 002, Delay 36 to 60, target 61) in exchange for a smaller Area while preserving the target. An additional \(n=20,m=8\) case still has a tiny regression of 112 Area units relative to the earlier Portfolio; searching that case further would incur more runtime and is not enabled by default.

The lighter version without this fallback is retained as `src/synth_core.cpp`, and the Area-oriented version with fallback is `src/synth.cpp`. The latter increases code size and does not always make each individual case faster. The benchmark should be interpreted as a **Pareto-aware portfolio** rather than a single universally superior representation.

## 4. Negative results and failure-mode analysis

- **Cofactor implication rewriting** was implemented and verified but the corresponding pre-balancing Area sum rose from 770,195 to 776,953. A valid mathematical rewrite does not imply a good mapping heuristic. The implication code is retained for comparison, but it is **not enabled** in the final method.
- **Local delta-cost rewriting** was attempted: create both sides of De Morgan and compare newly allocated gates. In representative tests it made some Area results slightly worse (for example case 001, 61,952 → 62,206). It did not reliably capture *global* reuse, so it is not retained.
- **Repeating Area Recovery** on selected cases 001, 005, 007, 019 and 025 yielded no further improvement with the current greedy rule: the mapping had reached a fixed point of this specific rewrite procedure, **not** a globally optimal circuit.
- **Aggressively trying many variable orders** can make intermediate BDD construction much slower or memory-hungry, particularly for high-dimensional functions. The best observed Area improvement from an additional reverse order was on case 024: 159,633 → 124,830 (Delay 69 → 72; Target 83). Not all orders helped.
- **Target Delay is not a proof of optimality.** The teacher's scoring function is unspecified; Area sum is a useful ablation statistic, but the official grade could also weight Delay and Runtime differently.

## 5. Robustness and verification

- **Official 25 Stage 1 cases:** 25/25 `PASS` and 25/25 `target_met=yes`, including a subsequent fresh run built from the final source (`results/final_release.csv`).
- **Independent bit-parallel Netlist verification:** final Netlists: 25/25 checked (`results/final_independent_verification.csv`); 13 smaller cases were exhaustively checked over all assignments, and 12 larger cases were checked on deterministic samples. The checker independently recomputed Area and Delay and found exact agreement. The official Evaluator supplies the exhaustive check for the full published case set.
- **Extra generated Boolean functions:** 110/110 `PASS` in the official Evaluator, including constants, variable projections, Parity/XOR, multiplexer and multi-output functions. Exactly 96/110 met their synthetic target delays; these targets were not engineered to be necessarily attainable or representative of Stage 1.
- **Structured stress test:** \(n=20,m=8\), input declares a 128 MiB RAM limit; official Evaluator returned PASS with Area 751, Delay 78 and Runtime around 703 ms.
- **Random-function stress test:** \(n=16,m=4\), deterministic high-entropy truth table, the same RAM limit; official Evaluator returned PASS (Area 108,917, Delay 63, Runtime 1,584 ms). These stress tests do not prove safe operation on all random \(n=20\) functions.

## 6. Research directions worth pursuing next

1. **True polarity-aware mapping on the shared DAG.** Complemented BDD edges make it possible to track both phases of each signal. Instead of introducing a pair of NOTs whenever a Gate is rewritten, build a global dynamic program that keeps selected positive/negative implementations and shared fanout costs. This can beat greedy De Morgan replacement but requires careful cross-output accounting.
2. **Small-cut rewriting with an exact local truth signature.** Enumerate limited input cuts of 4–5 leaves, compute their Boolean functions, and compare legal gate networks with a Pareto set of Area/Arrival Time candidates. For complex cuts, avoid exact enumeration that scales exponentially. Verify all replacements by truth signatures or a separate checker.
3. **BDD order screening / sifting with a hard budget.** Generate candidate orders cheaply, estimate BDD node count/edge sharing, map only promising orders. Share parsed truth table and intermediate caches to avoid re-reading millions of tokens on each trial. A per-candidate time/memory cancellation mechanism is essential for untrusted or much larger hidden cases.
4. **Output-aware timing slack and Area recovery.** Propagate required times from each output and compute critical cones and exact fanout counts. Reorder cone optimization by estimated recoverable Area per unit of consumed slack; compare several passes without claiming that a greedy choice is globally optimal.
5. **Technology-independent AIG / XOR-AND Graph and decomposition.** Detect disjoint-support, affine/XOR-heavy and multiplexer-heavy functions, then use technology mapping to assign actual AND2/OR2/NOT structures. Compare on generated adversarial functions, not just the 25 public cases.
6. **Engineering hardening.** The current code checks the case runtime budget only between candidates; individual synthesis attempts are not safely interruptible. Introduce cooperative deadlines into BDD and cube construction, preserve a valid fallback candidate, honor strict memory budgets, and retain independent full-table checks when feasible.

**Experimental design principle:** freeze a baseline, change one algorithmic component per ablation, measure Area/Delay/Runtime on all cases, record failures, and retest on held-out synthetic functions. A 25/25 target-met count should be treated as a feasibility milestone, not an optimization stopping rule.

## 7. Reproduction and citation of reference work

Compile the packaged source (the default `make` also builds the smaller `synth_core` ablation):

```bash
make
./evaluator ./synth /path/to/stage1 --report stage1_round3.csv
```

To verify a saved output (from the included fresh run), supply the corresponding instructor case:

```bash
python3 tools/verify_netlist.py /path/to/stage1/case_017.txt verification_outputs/case_017.output.txt
```

Public technical reference: [zdu881/UFUG2106-Project](https://github.com/zdu881/UFUG2106-Project), especially its `docs/METHOD.md`, `src/synth.cpp` and `docs/STAGE2_PROGRESS_20261110.md`. The reference's reported Stage 2 prototype numbers come from that repository, not from a local reproduction. Both projects describe AI-assisted development; published results should be presented with correct provenance and student review.

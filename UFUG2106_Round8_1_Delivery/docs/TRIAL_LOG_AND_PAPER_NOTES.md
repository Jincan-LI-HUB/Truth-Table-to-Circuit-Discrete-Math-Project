# Round 8.1 — Trial Log, Causal Story, Paper Evidence Index

## Research diary (chronological)

**2026-11-21 / hypothesis:** Round8.0 improves only case021; inspect whether syntactic algebraic matches are the bottleneck instead of true absence of alternatives. Study ABC and mockturtle cut/resubstitution architecture conceptually, without assuming their AIG-standard cost metrics match our custom gate library.

**Prototype 0 / unsuccessful:** Three local candidate netlists became worse (case021 +1,101; case014 +1,382; case002 +248) because screening counted multi-fanout cones as reclaimable. All alternatives rejected globally. Corrected the private-cone valuation and retained negative evidence in `ROUND8_1_EVIDENCE_AND_TRADEOFFS.md`. This is a **reasoned implementation correction**, not simply tuning a numeric threshold.

**Prototype 1 / isolated method:** Compile 4-feasible-cut recognizer, truth-mask evaluator, prime-cube greedy SOP/POS and multiple Shannon orders. Exhaustively validate the emitted circuits. See `evidence/offline_ablation.csv`. SOP and Shannon both often work, but naive node-wise mixing performs worse in aggregate; this motivated independent full-DAG branches.

**Prototype 2 / integrated Round8.1:** Derive from exact frozen Round8.0 SHA; after its accepted incumbent run bounded cut resynthesis independently by template family. Reject any final graph which fails valid weighted-area improvement or timing check. Stage2 25 cases × 2 policies = 50 complete-truth-table equivalence checks; 25/25 target met in each policy. Area-priority: 508,535→500,696 (17 cases), strict delay: 508,535→508,352 (14 cases). See `evidence/integrated_local_full_truth.csv`.

**Prototype 3 / order reversal:** Distinct `reverse` ablation cut→pattern changes case005 to 108,960/55 vs forward 109,073/55, while forward is slightly better on case021; all examples exhaustively verified. No universal best ordering found. Do *not* silently force `reverse` into the default policy without its full WSL runtime evaluation.

**Randomized robustness:** 180 independent random small DAGs × 4 cut methods = 720/720 exhaustive checks. This tests correctness of novel transformations on circuits not present in the public 50-case benchmark; it does not show scoring improvements on hidden tests.

## What the final paper may legitimately claim

1. A single algebraic-pattern rewrite may have weak coverage even when local exact-cut substitutions exist.
2. Multi-fanout sharing invalidates naive local area estimates; conservative reclaimability plus whole-graph verification prevents systematic acceptance of those regressions.
3. Independent family-wise cut searches can outperform local candidate-family mixing under the same Boolean constraints.
4. Case-specific gate weights and arrival/required times are necessary for meaningful ranking.
5. The *empirical* advantage in local Stage2: 17 improved cases and 7,839 weighted-area units saved, with some deadline-safe delay regressions. The Pareto-conservative version saves 183 area across 14 cases without delay regression.
6. Any summary of full 50-case official scores or stable runtime improvement **must await the user's WSL evaluator ZIP**.

## What the final paper must NOT claim

- 'Exact global optimum', 'ABC state of the art replicated', or 'optimal 4-variable implementation library'. This implementation is bounded, greedy, and searches at most four cut variables.
- 'All cases get better'. On current Stage2, area-priority improves 17/25, strict improves 14/25; several are unchanged.
- 'The official grade increased' without an explicit syllabus grade formula.
- 'We proved strict runtime compliance' from ordinary wall-clock measurements.
- 'Multi-output factoring was fully solved'; the current method uses shared DAG graph hashing but does not implement a global multi-output decomposition theorem.

## Hypotheses for Round 8.2 and ablation ideas

- **Exact 3-input implementation library / NPN classes:** replace greedy local expressions for k≤3 by enumerated Pareto candidates under custom costs. Compare library coverage and run time against SOP/Shannon; do not conflate exact local Boolean enumeration with exact mapped circuit synthesis.
- **True resubstitution:** collect divisor signals from a bounded window, evaluate their care-set functional compatibility, and compare cost with cut-only rewriting.
- **Fanout-aware choice evaluation:** iterative rounds after private-cone rewriting to exploit newly available shared gates. Test objective improvement vs extra runtime and possible drift in Stage1.
- **Budget adaptive routing:** use cut-count and reclaimed-area histograms, not case IDs, to allocate time to hard / easy cuts.
- **Score sensitivity:** if syllabus provides grading formula, re-rank Area/Delay/Runtime Pareto candidates; otherwise keep strict and area-priority results separately.

## Suggested final report sections

1. Problem and evaluator: multi-output truth table to 2-input gate DAG; gate costs and independent limits.
2. Stage 1 method: ROBDD, variable ordering, Shannon mapping and cover selection; why Round7 was needed.
3. Runtime engineering: Round7.0→7.1→7.2 with 50-case regression and timeout case016.
4. Structural optimization: Round8.0 pattern-based tests and limits; Round8.1 cut truth masks and why they improve generality.
5. Formal correctness: cut substitution theorem and global topological DAG checker.
6. Experiments: isolated and integrated ablations, strict vs area-priority, order effects, original/negative outcomes.
7. Threats to validity, limitations, unknown official score, hidden-case generality.

All paper tables should link back to exact `source sha256`, official CSV, evaluator log, random seed, and run environment. Keep conjecture, local measurements and official results explicitly distinct.

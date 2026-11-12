# Manuscript Review Round 2: Mathematical Consistency and Gate Notation

Version: v0.4 (derived from v0.3 P1/P2, original v0.3 preserved).
Status: second-round audit + targeted corrections; NOT a final submission.
P0 is explicitly deferred and unchanged.

## Findings and resolutions

### M1 — Incorrect equality at an output also used internally (corrected)

**v0.3 issue:** the sufficient timing theorem asserted `R_G(y_j)=D_target`. If a primary output signal is also the fanin of another gate, reverse required-time propagation takes the minimum of its output obligation and its consumer obligations. In general `R_G(y_j) <= D_target` and the inequality can be strict.

**Correction:** for any original output `y_j`, `T'(y_j) <= R_G(y_j) <= D_target`. This preserves the correct theorem conclusion. In the documented two-output worked example, `R(7)=min(8,8-2)=6`, since node 7 is both output y1 and a fanin of node 8.

**Scope of theorem:** applies to DAG replacements respecting old exposed boundaries, gate types/delays on unchanged gates, and no new external dependencies. It does NOT prove timing preservation for arbitrary rewrites. The full graph is re-evaluated before acceptance in the actual synthesizer.

### M2 — Typed DAG semantics and multi-output sharing (expanded)

**Frozen source:** `typed_netgraph.hpp`, `Builder::add`, `Builder::finish`, `rebalance`, `area_recover`.

- Builder canonicalizes operand order for AND2/OR2; identical typed gates share one ID via intern/hash lookup. That is structural equivalence, not arbitrary functional equivalence.
- Rebalance associates and de-duplicates same-op inputs, flattening only a single-use interior cone (the root itself may be flattened). Fanout counts include every output reference, so shared output nodes are not mistaken for private intermediate nodes.
- All output roots are traced for live reachability. Dead nodes are removed and live nodes renumbered in topological sequence; the output list retains its positional order.
- The De Morgan rewrite for a gate is functionally exact; replacement acceptance uses postconstruction netlist-wide metrics. The area metric is exact for live/pruned candidate graphs, not a general constant-time incremental shared-cost model.
- The internal parser is not a fully general untrusted-netlist validator; only synth-produced nets are passed through it. Official evaluator and independent checker provide separate validation.

**Independent regression:** 2,000 deterministic-seed pseudorandom DAGs (2–6 inputs, 1–3 outputs) with 8,000 transformation checks, each tested over all `2^n` input assignments. All passed; see `shared/tests/test_results.txt`. This is additional evidence, **not** a formal correctness proof or exhaustive test over arbitrary graph sizes.

Frozen header SHA-256: `55030bc9a51ff435e15285c0e9cb36db4032625a45b42993d4f1434290e04950` (the header snapshot is bundled solely for repeatable testing). Frozen main C++ source remains unchanged and is identified separately by SHA-256 in the project freeze manifest.

### M3 — Cutoff and candidate ranking (clarified)

**Frozen source:** `synth_round51.cpp`, modern loop approx. lines 849–915; legacy fallback lines 919–949; final algebra/phase lines 951–1005.

A timing-based outer eligibility check skips late modern candidates after ~75% of declared limit, legacy candidates after ~72%, and final postprocessing branches after ~79–88%. Some additional variable orderings have internal periodic deadline checks with exception fallback. These do not enforce an unconditional hard total runtime deadline (initial candidates and other stages may run beyond a target).

The internal ranking is lexicographic `(max(0,delay-target), feasible?area:0, delay, area)`. A candidate is compared only after a completed, parsed, locally scored DAG is available. Once a feasible incumbent exists, a newly infeasible candidate cannot replace it. Across runs, however, changing elapsed-time eligibility may change which valid netlist is selected; byte-identical output is an empirical result for specified runs, not a theorem.

### T1 — AND/OR/NOT typeface (standardized)

The `technical_report/main.tex` macros for `AND2`, `OR2`, `NOT` used `\mathsf` (sans serif), while the Trial Log used `\mathrm`. Both can be valid notation, but the difference was unexplained and visually inconsistent. Both manuscripts now use upright roman serif `\mathrm` in math for gate types; logical operations remain `\land`, `\lor`, `\neg` and exact file-format tokens are monospace. No semantic or source-code changes.

## No-new-data policy and limitations

- No new Stage 1 evaluator performance result or synthesized area is claimed.
- Do not infer worst-case runtime, exact global area minimality, hard RAM/runtime-limit enforcement, or hidden Stage 2 performance.
- P0 (policy/authorship/submission details) remains deferred at the user's request.
- This is a manuscript review of frozen implementation, **not** an approved program patch.

## Files changed relative to v0.3

- `technical_report/main.tex`: gate-type typography, timing proof output inequality, shared-output example, typed DAG invariant derivation, internal parser validation scope, runtime cutoff scope.
- `trial_log_record/main.tex`: same timing fix and shared-output example, multi-output sharing proof motivation, runtime-cutoff treatment, typography convention.
- Added `shared/tests/frozen_src/typed_netgraph.hpp` (identical snapshot), `shared/tests/test_typed_dag_invariants.cpp`, `shared/tests/run.sh`, `shared/tests/test_results.txt`.

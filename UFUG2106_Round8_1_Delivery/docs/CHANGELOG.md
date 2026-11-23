# Changes — Round 8.1

- Frozen ancestor: Round 7.2 synthesis & budget-aware shortlist.
- Frozen direct parent: Round 8.0 `synth_round8.cpp`, SHA-256 `9ec7dc97161d3dc906dfad7960e0fc232b8e2cf0399908c6c4e99b756d8bacd8`.
- New: `r81_cut.hpp` for k≤4 bounded cut enumeration, exact local truth masks, SOP/POS prime-cube covers, cyclic Shannon decompositions and timing-filtered cost-aware replacement.
- Fixed after negative test: multi-fanout nodes cannot be optimistically counted as removed; use conservative `private_reclaim` and whole-live-DAG acceptance.
- New: independent full-graph family branches, strict delay mode and optional order-reversal mode.
- New: 720 deterministic random exhaustive cut checks and independent full Stage2 truth-table verification results.
- New: paired same-machine two-stage official evaluator and eight method ablations.
- New: feedback ZIP on successful and failed local runs, including code snapshot and original official logs.
- No changes to original Round7.2 or Round8.0 sources. No hardcoded case-ID algorithm behavior.
- Not implemented: SAT exact local resynthesis, full choice networks, complete e-graph equality saturation, complete window divisor resubstitution.

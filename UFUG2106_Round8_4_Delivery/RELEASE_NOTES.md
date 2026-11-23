# Round 8.4 Release Notes

## Changes

1. Added a separate `r84_cut.hpp` with **priority-consistent Top-Q** root selection. The old Top-1500/topological-first-900 behavior remains available as `topology_dual`.
2. Added deterministic 1/3 and 2/3 priority mixtures. They retain the original topological propagation order after selected roots are fixed.
3. Added experimental pilot–focus branch allocation using completed-root area gains, rather than elapsed time, to choose a larger follow-up budget.
4. Added independent source SHA manifest, strategy-isolation and exhaustive truth-table tests, stage-paired official evaluator runner, and failure-safe ZIP feedback.
5. Preserved the low-memory fallback from Round 8.2.1 without changes.

## Evidence-based decision

150/150 local Stage 2 exhaustive verifications PASS. Strict Top-Q often **loses Area**, and its delay is sometimes lower. Rank mixtures did improve area locally: mixed66 499,035 versus legacy 500,072 (1,037 smaller), with unchanged per-case delays; however two branch wall-guard triggers warn that repeatability is not established. **Default is kept topology_dual** rather than making an unproven policy the submission default. The standalone source has not been evaluated by the genuine official evaluator in this container.

## Known limitations

The cost-based root score is only a proxy for future net Area gain. Topological position can matter because early rewrites change later candidates' mapped DAG frontiers. Adaptive pilot–focus re-evaluates its winning branch and thus duplicates some work. Scheduling parameters are developmental and do not constitute hidden-set optimization guarantees. Positive-RAM official evaluation anomaly remains separately unresolved.

- **Repetition warning:** mixed66 case_005 varies materially under different wall-guard outcomes; repeated-run stability has not been shown.
- **Generalization warning:** reused structured 24-case set shows no difference between mixed66 and topology, so the local development-bank gain is not demonstrated on independent blind data.

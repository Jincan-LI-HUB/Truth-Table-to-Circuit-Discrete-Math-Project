# Phase C revision and evidence map

Phase C follows the accepted local archive at `293258a6d9ba9af9e07899d84e22923a46e11779`. The revised manuscript is centered on Integrated Final, with the independent trials condensed into their contribution to that design. The implementation source for the planned submission is pinned to upstream `59e33505616d127fc06a63580ca3ae3c34d1da72`.

| Revised material | Source and evidence |
| --- | --- |
| Complete fallback, BDD screening, typed-portfolio guards, working-target rank, CompactChoice and cooperative deadlines | [`synth_stage2.cpp`](../Final_Submission_by_Zeyun_DU/src/synth_stage2.cpp), especially `main`, `BDD`, `Mapper`, `SearchMemory`, `CompactChoice` and `search_round51`. Figures 1–2 cover the integrated entry point and the nominal clock policy. |
| Imported J51 library versus standalone J51/R10.0 control | [`ORIGIN.md`](../Final_Submission_by_Zeyun_DU/src/round51/ORIGIN.md), [`synthesis.hpp`](../Final_Submission_by_Zeyun_DU/src/round51/synthesis.hpp) and the [R10.0 freeze](../UFUG2106_Round10_0_Delivery/submission/). The integrated controller uses the J51 library and one inherited SOP invocation. |
| Exact marginal area and delay accounting under output switches | `mix_outputs` in [`synth_stage2.cpp`](../Final_Submission_by_Zeyun_DU/src/synth_stage2.cpp) and the intern/prune procedures in [`typed_netgraph.hpp`](../Final_Submission_by_Zeyun_DU/src/round51/typed_netgraph.hpp). Figure 3 is a constructed gate example. |
| Cut signatures, SOP replacement, required arrival and late-output rescue | [`r84_cut.hpp`](../Final_Submission_by_Zeyun_DU/src/round51/r84_cut.hpp), [`critical_cuts.hpp`](../Final_Submission_by_Zeyun_DU/src/round51/critical_cuts.hpp), [`shared_factors.hpp`](../Final_Submission_by_Zeyun_DU/src/round51/shared_factors.hpp), [`cofactor_timing.hpp`](../Final_Submission_by_Zeyun_DU/src/round51/cofactor_timing.hpp). Figures 4–5 illustrate exact cofactor reconstruction and a faster equivalent cut. |
| Four-solver area, paired runtime, stage differences, delay and resource use | [Integration audit](../Final_Submission_by_Zeyun_DU/integration/AUDIT.md), [matched case metrics](../Final_Submission_by_Zeyun_DU/integration/data/matched_case_metrics.csv), [paired summary](../Final_Submission_by_Zeyun_DU/integration/data/matched_pairs.csv), [direct RSS](../Final_Submission_by_Zeyun_DU/integration/data/matched/direct_memory.csv). Figures 6–8 are archive-derived; the casewise appendix includes all 400 observations. |
| J51 near-limit case and remaining Integrated Final timing miss | [Interrupted J51 diagnostic](../Final_Submission_by_Zeyun_DU/integration/data/diagnostic/interrupted-J51-stage2.csv), [release timing record](../Final_Submission_by_Zeyun_DU/reports/stage2-timing-20261124/README.md), [generated-case witness](../Final_Submission_by_Zeyun_DU/reports/stage2-timing-20261124/residual.csv). |
| Historical controller selection and causal boundaries | [R8.6 quota factorial](data/quota_factorial.csv), [R9.1 feedback](Research_Trial_Log/data/raw_feedback_verified.csv), [R10.1 paired policy](data/final_policy_tradeoff.csv), and [unified log](Research_Trial_Log/UFUG2106_Stage2_Research_Trial_Log_v3.pdf). These experiments retain their original incumbents and comparison boundaries. |

The casewise report and figure generator consume the local Phase A/B archive. The independent source and archived datasets remain intact. The figure kit informed composition and implementation; its bundled CSV excerpt is excluded from the build. PDF, editable SVG and PNG exports share the same plotting source. The article distinguishes measurements from the three mathematical examples and the two source schematics.

## Revision 1 after human review

The revision starts from draft `e3d8e80` and recovers relevant mathematics from `293258a`. It organizes the paper around finite-resource exploration of functionally equivalent shared networks.

| Section | Revision |
| --- | --- |
| I. Problem formulation and research motivation | Restates the area objective on the feasible set and distinguishes Boolean validity, physical cost and the resources required to search. |
| II. Mathematical foundations | Restores Shannon reduction, complemented references and exact influence. Adds the equal-size AND/XOR decision example and two unequal-cost realizations of one function. |
| III. Resource-aware architecture | Condenses the call-by-call narrative. Defines the nested feasible sets and explains the reserve, compact candidate and screening budget through their effects on candidate choice. |
| IV. Shared-DAG structural optimization | Formulates binary output selection, exact marginal area and the reference invariant. Adds a joint-switch counterexample, restores the cut substitution proof and maximal cube construction, and works through a shared SOP cut with explicit prices and arrivals. |
| V. Timing-constrained decomposition | Restores the fixed-boundary arrival proof and the critical cut example. Derives grouped reconstruction and AND/OR/XOR split conditions, connecting the local screen to the complete reconstruction check. |
| VI. Experimental evaluation and ablations | Preserves the matched and stress results. Restores R8.6 factorial contrasts, R9.1 frequency versus magnitude, and the paired R10.1 time/area table. Explains what transferred to integration and the lack of an equal-budget comparison. |
| VII. Limitations, contributions and conclusion | Consolidates proof limits, public and generated-case coverage, and project attribution. |

The current draft reuses the eight existing figures. [Figure revision plan](FIGURE_REVISION_PLAN.md)

`verify.py` checks the constructed examples and recomputes the reported historical contrasts, improvement counts and time ratios. The Phase A/B archive verifier checks the matched case-level evidence independently.

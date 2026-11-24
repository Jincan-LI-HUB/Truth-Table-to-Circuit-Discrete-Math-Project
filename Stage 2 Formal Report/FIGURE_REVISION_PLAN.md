# Phase C Revision 3 figure inventory

All widths are the IEEE single column (about 3.46 in), full text width (about 7.15 in), or the Trial Log text width. Each empirical plot reads the archived data named below. Constructed examples and source schematics are identified in their captions.

| Formal Report | Scientific question | Basis | Width |
| --- | --- | --- | --- |
| 1. Framework | How do equivalence, structural search, global evaluation and finite resources interact? | Conceptual model. | Column |
| 2. Architecture | How do generation, global evaluation and guarded feedback interact while execution remains sequential? | Pinned Integrated Final entry point and guarded promotion. | Full |
| 3. Budget | Which cutoffs are absolute and which allowances depend on elapsed entry time? | Pinned scheduler, schematic only. | Full |
| 4. Cone selection | Which gates stay live and when does a better joint move require worse individual moves? | Constructed reference-count and joint-switch examples. | Full |
| 5. Shared-term SOP | Why can a local estimate of −1 differ from a whole-DAG gain of 3? | Three constructed DAGs with shared area 2, removed area 8 and constructed area 5 for the SOP transition. | Full |
| 6. Critical cut | How can reassociation preserve area and improve root slack? | Constructed four-leaf AND tree. | Column |
| 7. Cofactor reconstruction | How do equal cofactor rows determine the binary selector? | Constructed matrix with residuals `c` and `c∨d`. | Column |
| 8. Bidecomposition | How do rectangle and parity conditions extend beyond a single two-by-two slice? | Verified four-by-four AND, OR and XOR examples built from the same block factors. | Column |
| 9. Operating points and slack | Which solvers are nondominated in summed area and time, and how does delay margin differ? | [Matched case metrics](../Final_Submission_by_Zeyun_DU/integration/data/matched_case_metrics.csv) for 50 cases per solver. | Full |
| 10. Absolute contributions | How concentrated are the savings across inputs and banks? | Matched casewise R10.0-relative area, repeat 1. | Full |
| 11. Resource exposure | What paired runtime, observed RSS and per-case time-limit use accompany the area result? | Matched time and [separate direct RSS](../Final_Submission_by_Zeyun_DU/integration/data/matched/direct_memory.csv). | Full |
| 12. Full area–delay scatter | Which inputs exchange area for delay, and how does area normalization change the comparison? | All 50 matched inputs, repeat 1, with four labeled cases. | Full |
| 13. Independent decisions | What identifies quota effects, improvement magnitude and last-pass trade-offs? | [R8.6 factorial](data/quota_factorial.csv), [R9.1 controlled pairs](Research_Trial_Log/data/raw_controlled_pairs_verified.csv) and [R10.1 policy summary](data/final_policy_tradeoff.csv). | Full |

Trial Log Part III reuses the architecture, operating-point and resource figures and adds three dedicated statistical panels.

| Part III figure file | Scientific question | Basis |
| --- | --- | --- |
| `phase_c_integration_passes` | Are fixed-incumbent gains frequent or concentrated, and do factor gains transfer across families? | [Paired cuts](../Final_Submission_by_Zeyun_DU/reports/stage2-cuts-20261124/paired.csv) and [paired factors](../Final_Submission_by_Zeyun_DU/reports/stage2-factors-20261124/paired.csv). |
| `phase_c_integration_policy` | Which recorded operating points met both public area and reserve, and how variable are the cap batches? | [Headroom trials](../Final_Submission_by_Zeyun_DU/reports/stage2-headroom-20261124/development.csv), [old-cap records](../Final_Submission_by_Zeyun_DU/reports/stage2-timing-20261124/earlier-budget.csv) and [frozen ZIP runs](../Final_Submission_by_Zeyun_DU/reports/stage2-timing-20261124/public-runs.csv). |
| `phase_c_integration_recovery` | Which bank failures remained at each cumulative snapshot? | [Development matrix](../Final_Submission_by_Zeyun_DU/reports/stage2-timing-20261124/development.csv), with the archived role at each snapshot. |

The archived Phase C area-only and percentage-by-case plots remain available as companions. `build_phase_c_figures.py` generates vector PDF, editable SVG and PNG. Use `--only` for a named subset and `--repeat 2 --out <directory>` for the alternative matched repeat. Upstream and independent controlled studies retain their original denominators.

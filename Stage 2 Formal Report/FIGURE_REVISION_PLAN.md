# Figure revision plan

Revision 1 uses the existing eight figure files. The actions below apply to the subsequent visualization session. Widths refer to IEEE column or full text width, approximately 3.46 or 7.15 inches.

| Figure or proposed panel | Scientific question | Action | Basis | Width |
| --- | --- | --- | --- | --- |
| `phase_c_architecture` | How do complete candidates become available for global comparison, and where does timing recovery enter? | Revise to emphasize the fallback, primary and compact choices, and the two feasibility thresholds. | Pinned integrated entry point and guarded candidate promotion. | Full |
| `phase_c_budgets` | How does a finite allowance divide among screening, measured mapping and recovery? | Retain. Keep the main window and later admission windows visually distinct. | Source-defined main, BDD, J51 and later clocks. Schematic, with no measured durations. | Full |
| `phase_c_cones` | Which gates are paid for on a root switch, and when can greedy moves miss a cheaper union? | Revise to add the four binary choices of the joint-switch example alongside the live-reference diagram. | Constructed unit-price networks. Standalone cones cost 4 and 3, and union areas are 5, 7, 7 and 4 at delay 3. | Full |
| Worked SOP cut | Why can a local cone estimate differ from the true whole-network gain? | Add a compact before/after depiction if it replaces or augments the numeric table. | Constructed cut with shared `ab`, mask `0xA8`, and area 10 to 7 at unchanged arrival. | Column |
| `phase_c_critical` | How can a different cut expression improve slack at the same area? | Retain. | Constructed four-leaf AND cut, equal gate count and root slack changing from −1 to +1. | Column |
| `phase_c_cofactors` | How do cofactor classes reconstruct an output exactly? | Retain. | Constructed selector `h=ab` with quotient rows `c` and `c∨d`. | Column |
| `phase_c_area_comparison` | How do the four released solvers compare in weighted area? | Retain. | Matched repeat 1, 50 cases per solver in [public summary](../Final_Submission_by_Zeyun_DU/integration/data/public_summary.csv). | Column |
| `phase_c_casewise` | Are area changes widespread and similar across banks? | Retain. | Matched repeat 1, same-case area differences against Z1 and R10.0 in [case metrics](../Final_Submission_by_Zeyun_DU/integration/data/matched_case_metrics.csv). | Full |
| `phase_c_resources` | What runtime, memory and limit exposures accompany the area result? | Retain. | [Matched case metrics](../Final_Submission_by_Zeyun_DU/integration/data/matched_case_metrics.csv) for synthesis time, [separate process measurements](../Final_Submission_by_Zeyun_DU/integration/data/matched/direct_memory.csv) for RSS. | Full |
| R8.6 factorial | Does exposing roots affect area differently from reclaiming nominal time? | Restore the historical panel if used in place of a redundant numeric display. | [Existing figure](figures/r86_factorial_design.pdf) and [quota factorial CSV](data/quota_factorial.csv), first repeat. | Column |
| R9.1 frequency and magnitude | Does a method that improves more cases also save more area in aggregate? | Restore the historical design if needed to compare all three policies in a common panel. | [Existing figure](Research_Trial_Log/figures/05_r91_frequency_vs_magnitude.pdf) and [controlled pairs](Research_Trial_Log/data/raw_controlled_pairs_verified.csv), first repeat. | Column |
| R10.1 policy trade-off | What area penalty accompanies a smaller last-pass allowance? | Restore only as a replacement for the policy table if a paired visual is preferred. | [Existing figure](figures/final_policy_tradeoff.pdf) and [paired policy summary](data/final_policy_tradeoff.csv), 100 pairs per policy. | Full |

Keep units, baselines and experimental families attached to each panel. A constructed circuit or source schematic should be identified as such in its caption.

# Phase C Revision 2 figure record

The publication set uses the established palette. All source diagrams and constructed networks are labeled separately from observations. Width is the IEEE single column (about 3.46 in) or full text width (about 7.15 in).

| Figure | Change | Scientific question and basis | Width |
| --- | --- | --- | --- |
| Framework | Added | How do equivalence, structural search, global evaluation and finite resources interact? Conceptual model. | Column |
| Architecture | Replaced | Which candidate and state relationships matter, and what actually runs in sequence? Pinned Integrated Final entry point. | Full |
| Budget | Replaced | Which windows are absolute deadlines and which allowances depend on elapsed entry time? Pinned scheduler, with no measured durations. | Full |
| Cone selection | Extended | Why does charging live gates make a single switch exact but leave a joint-move barrier? Two constructed examples, including the four states at delay 3. | Full |
| Shared-term SOP | Added | How does live reuse turn a local −1 into global −3? Three explicit gate DAGs, mask 0xA8 and two fixed output arrivals. | Full |
| Critical cut | Replaced | How can a gate-level reassociation keep area fixed and improve root slack? Constructed late-leaf AND tree. | Column |
| Cofactor reconstruction | Replaced | Where do row classes and the binary selector come from? Complete constructed four-by-four truth matrix. | Column |
| Bidecomposition | Added | What do the operator-specific partition screens look like? Verified two-by-two AND, OR and XOR slices. | Column |
| Area totals | Retained | How large are whole-solver area differences? Archived matched public summary, repeat 1. | Column |
| Absolute contributions | Added to article in place of the percent-by-case panel | How much of the net improvement comes from a few inputs and from Stage 2? Archived matched case metrics, repeat 1. The existing percent figure remains available as a companion. | Full |
| Runtime and RSS | Retained as a companion; aggregate measurements remain in the text | What resources accompany the area outcome? Archived matched runtime and separate direct-process RSS. | Full |
| Representative trade-offs | Added | Which outputs gain area, delay, or both, and at what synthesis-time ratio? Four paired cases from the matched CSV, repeat 1. | Column |
| Historical ablations | Restored as one compact panel set | What can quota/reclaim, choice frequency, and final-pass cost identify under their own controls? R8.6 factorial CSV, R9.1 controlled pairs and R10.1 paired policy CSV. | Full |

`build_phase_c_figures.py` exports PDF, SVG and PNG. Use `--only` with selected figure names to update a subset. Figures read existing archives, whose benchmark and experiment provenance is unchanged. The same plotting command can use repeat 2 for the fresh matched figures.

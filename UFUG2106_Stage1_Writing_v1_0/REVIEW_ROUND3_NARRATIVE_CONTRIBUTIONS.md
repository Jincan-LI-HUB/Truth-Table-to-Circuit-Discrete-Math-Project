# Manuscript Review, Round 3 — Research Narrative and Contribution Boundaries

**Input:** `UFUG2106_Stage1_Writing_Draft_v0_4_Consistency.zip` and its preserved mathematical consistency review.  
**Output:** Draft v0.5 (narrative revision).  
**Status:** Editorial revision of two manuscripts, *not* a new synthesis experiment. P0 remains deferred by student request.

## The diagnosis

The v0.4 manuscripts already contain the required Boolean and timing derivations, candidate-selection semantics, frozen source provenance, official measurements, and several methodological caveats. The remaining problem is that a list of algorithms does not automatically explain why one method motivated the next or why the final engineering configuration was chosen.

- **Technical Report:** the research questions, contributions, and boundaries of evidence were implicit, dispersed across sections. The final choice of R5.1 required a clearer distinction between *area-minimizing* and *cost-effective* candidates. The course rubric values understanding, not only a leaderboard.
- **Trial Log:** individual rounds had motivations and decision boxes, but there was no single roadmap that made successive research hypotheses and abandoned alternatives visible to a new reader.

## Decisions and editorial actions

| Priority | Observation in v0.4 | Action in v0.5 | Evidence that constrains the rewrite |
|---|---|---|---|
| High | Intro mixed methods and observations without clear questions | Explicit RQ1 representation/feasibility, RQ2 global area/timing, RQ3 synthesis efficiency and stopping | R1 12/25 targets; R2 25/25; R3 global recovery; paired R5.1; R6.1 No-Go |
| High | “Our contribution” could appear to claim novelty for classic Boolean techniques | State precisely: reproducible implementation/integration, measured engineering refactoring, transparent negative-result decision | Bryant 1986; Shannon 1949; Mishchenko 2006; bundled sources |
| High | R1 → R2 → R3 appeared as a technical feature list | Add problem-to-method transitions: correctness → representation → global shared gate costs | WSL area/target archives; Round 3 sequential ablation |
| High | R4.1–R5.1 story could read as merely “we optimized runtime” | Explain the change in *object of optimization* from circuit to synthesis program | Paired WSL runtimes; code-level caching/typed DAG |
| High | R6.1 was mostly a footnote to area performance | Explain the distinct “does a new Boolean search pay for itself?” hypothesis; make the negative result explicit | 25-case paired WSL and 48 newly generated tests; budget-development data |
| Medium | Evidence scope was spread across text | Add a concise table of what proofs, evaluator, paired benchmarks, and synthetic holdouts can establish | Evidence matrix and frozen checker reports |
| Medium | Trial Log could be hard to navigate by hypothesis | Add a seven-transition decision map and explicit falsification/stop discussion | Trial sequence and recorded Go/No-Go decisions |
| Medium | “Trial Log” risked reading as an expanded final report | Add counterfactual decisions and retained failures rather than merely enlarging numerical tables | R4 search cost; R5.1 small-case overhead; R6 cut cost |

## Resulting research narrative

1. **Exactness first:** Shannon + ROBDD give a correct constructor, but miss 13 out of 25 delay targets.
2. **Representation matters:** alternative orders and mapping forms satisfy all 25 targets while reducing aggregate area.
3. **The target is a shared, priced DAG:** complements, algebra, and required-time recover area beyond abstract BDD shape.
4. **The optimizer has a cost:** candidate proliferation and repeated intermediate work make runtime an explicit resource.
5. **Engineering can preserve quality:** caching and typed DAG reduce measured synthesis time without changing recorded circuit area/delay in the paired comparison.
6. **A valid improvement need not be worth adopting:** cut rewriting finds additional area savings on tested families but breaches the predeclared runtime tolerance in WSL.

## Statements deliberately *not* made

- No claim of global minimum area, minimum delay, or numerical official grade optimization.
- No assertion that Round 3's sequential ablation is an isolated causal effect.
- No direct cross-machine comparison of historical runtime medians.
- No claim that synthetic holdouts statistically represent the unreleased Stage 2 distribution.
- No invented individual roles, falsely exclusive authorship, or undocumented AI-use scope.
- No claim that this research freeze has already been submitted to Canvas.

## Source/data changes

No synthesis code, evaluator results, CSV, JSON, or empirical figure was changed. The bundled plotting script and underlying original evidence remain intact. Only LaTeX prose, a new interpretive table, the Trial Log's decision map, and editorial documents were added. The Trial Log's figures are anchored in place to avoid float-only pages.

## Remaining reviews

- **P0:** deferred. Resume only when the authors are ready to finalize submission-specific contribution and disclosure content.
- Check the intended level of detail for the professor's Stage 1 report and the readable GitHub log. Reviewer and author preferences may lead to further shortening of the IEEE paper and expansion of tutorial examples in the Trial Log.
- Reconcile the final real Canvas submission source with the frozen Round 5.1 *research* snapshot when the actual submission is decided.

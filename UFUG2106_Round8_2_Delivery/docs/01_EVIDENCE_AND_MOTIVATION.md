# Round 8.1 → Round 8.2: Evidence-Based Motivation

**Research decision date:** 2026-11-21. **Status:** prior WSL evaluator evidence plus new, clearly separated, non-official Linux experiments. All 50 public cases have been used repeatedly for algorithm development; they are NOT blind holdout data.

## 1. What the frozen Round 8.1 evaluator results actually establish

The original feedback `Round8.1_Feedback_20261121_161108_240427.zip` contained 28 official CSVs (eight variants × two stages × two runs = 800 case records); all 800 records reported PASS and all target delays were met.

- Frozen Round7.2 reference: Stage1 area 529,014; Stage2 area 508,535; total 1,037,549.
- Round8.1 Reverse: total area 1,023,194 (run1), 1,023,286 (run2). 30/50 cases improve in area in both runs; six large improvements increase delay.
- Reverse runtime geometric means compared with R7.2: approximately 2.51 and 2.46. Stage1/Stage2 behavior is heterogeneous.
- Stage1 case_010: 4,712/32 → 3,065/61. Stage2 case_003: 19,494/39 → 15,207/63. Stage2 case_005: 112,221/40 → 106,770/57. Area reduction need not improve the area-delay product.
- Shannon single-mode produced about 91% of Reverse's aggregate area savings for a substantially smaller observed runtime ratio (roughly 1.5× versus 2.5× Round7.2).
- An offline, per-case oracle among the existing eight complete variants saved only 40 (run1) and 3 (run2) further area beyond Reverse. **This bound applies only to the eight generated versions, not to the globally attainable minimum.**

The official numbers are re-indexed in `../evidence/prior_official/`. The actual official scoring equation remains unknown; a surrogate such as area-delay product is a diagnostic sensitivity measure, not the course grade.

## 2. Why a new experiment is justified

The 8.1 algorithms were able to find new structures, but the default selector rewarded area while allowing output delay to reach the published target. The runtime-based cut deadline can also select different final cuts under small host scheduling variations. Moreover, a deterministic interval-based sample of root IDs does not prioritize nodes according to reclaimable area or local timing slack.

Three independent hypotheses are examined:

- H1 (root selection): selecting high-potential roots improves the set of local alternatives explored with a fixed root count.
- H2 (timing regularization): a delay-constrained or area-delay objective avoids weak area-for-delay trades at a measurable area opportunity cost.
- H3 (branch budgeting): one branch covers much of the area benefit more cheaply than two branches; a second branch may still find structurally distinct improvements.

These hypotheses deliberately concern different causal mechanisms. A negative result for one is not a refutation of the other two.

## 3. Experimental controls

All Round8.2 configurations reuse the same frozen R7.2-derived incumbent (Round8.0 preprocessing disabled in the official paired protocol). No case ID or case-specific lookup is used in solver decisions. The parent Round8.1 executable is left unmodified. Root caps and mode order are explicit, ablated, logged and preserved in the feedback archive.

Test sets:

- **Public Stage 2 development set:** 25 cases; not independent generalization evidence.
- **Synthetic holdout v1:** 24 random AND/OR/NOT networks, frozen before evaluation. Many outputs simplify to trivial functions; failure of benchmark *design*, not of algorithm correctness. Preserve this negative result.
- **Synthetic structured holdout v2:** 24 previously unobserved functions constructed using XOR/MUX/Majority mixtures, balanced and multi-input dependent by construction; frozen before execution with SHA-256 manifest. This is an additional generalization probe but is *not* representative of unpublished course cases by assumption.
- **Random DAG correctness tests:** 180 generated DAGs × four Boolean synthesis modes = 720 exhaustive comparisons. These test semantics, not scoring superiority.

## 4. Conclusions and limits before WSL

The development measurements show promising reductions in weighted area, including cases with better delay and cases with large area-delay trade-offs. They do not prove stable evaluator runtime compliance on WSL or across hidden distribution shifts. The official Round8.2 double-stage gate must be checked before proposing a release candidate.

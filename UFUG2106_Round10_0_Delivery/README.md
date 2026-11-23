# UFUG2106 — Round 10.0 Candidate Freeze

**Independent solver candidate only. Not the teammate-integrated final Stage 2 release. Hidden grader cases remain untested.**

## Purpose

Fix the Round 9.1 deployment discrepancy: successful `UFUG_R91_POLICY=repeat_sop` ablation required a research-specific environment variable, while the standalone `submission/synth.cpp` otherwise defaulted to no postprocessing. Round10.0 changes ONLY the fallback to `repeat_sop` when `UFUG_R91_POLICY` is absent. All old synthesis code, Cut library (default disabled), root caps and safeguards remain unchanged.

Frozen references:

- Round9.0 `src/synth_round90_frozen.cpp`: baseline without extra postprocessing.
- Round9.1 `src/synth_round91_frozen.cpp`: exact historical research build. Run with `UFUG_R91_POLICY=repeat_sop`.
- Round10.0 `src/synth_round100.cpp`: fallback `UFUG_R91_POLICY=repeat_sop`.
- Independently buildable `submission/synth.cpp`: byte-for-byte identical to Round10.0 source, with required headers in the same directory.

An **explicit** `UFUG_R91_POLICY=off` disables postprocessing. The extra pass only activates under the original Round9.1 safeguards (`runtime_limit >= 1000`, valid candidate, sufficient remaining time, global strict Area reduction and Target Delay). For 100ms stress cases, it remains disabled. The official scorer is never assumed to configure custom environment variables.

## WSL commands

Extract this folder directly into the user's **Final Project** directory beside genuine `evaluator` and `data/stage1`, `data/stage2`.

```bash
BASE="/mnt/e/canfiles/Common courses study/大学通识/26-27 Fall/UFUG 2106 Discrete Math/assignment/Final Project"
cd "$BASE" || exit 1
bash UFUG2106_Round10_0_Delivery/run_round100.sh
```

Default full test: **6 configs × 2 runs × 2 stages × 25 public cases = 600 official evaluations**, reversing config order on run 2. A feedback ZIP is produced on success and failure. Upload this ZIP for release decision.

For preliminary tests:

```bash
bash UFUG2106_Round10_0_Delivery/run_round100.sh --quick
bash UFUG2106_Round10_0_Delivery/run_round100.sh --local-only
```

`--quick`: four configs, one run, two public stages (200 evals). `--local-only`: full cold build plus equivalence tests, no official score claim.

## Comparison design

| ID | Source | `UFUG_R91_POLICY` | Hypothesis |
|---|---|---|---|
| r90_frozen | exact Round9.0 | unset | Area ~1,021,134 in prior WSL test |
| r91_sop_explicit | exact Round9.1 | repeat_sop | Area ~1,019,547 in prior WSL test |
| r100_default | new Round10.0 | unset | Should match explicit Round9.1, within search timing variation |
| r100_sop_explicit | new Round10.0 | repeat_sop | Same behavior as new default |
| r100_off | new Round10.0 | off | No extra postprocessing; should match Round9.0 |
| submission_default | independent submission/synth.cpp | unset | Should match new default |

Previous values are **expectations based on an earlier official feedback**, not newly measured official results. Paired official evaluation, not the local container, decides whether they generalize. Per-case Area/Delay differences are logged, not automatically interpreted as correctness errors; wall-clock trajectory may legitimately differ.

## Final submission warning

This ZIP is an **independent candidate**. The teammate-integrated code is not included and Issue #2 (BDD search budget) is **open**. Before final submission: integrate deliberately, cold-build from actual team repo, test unchanged Stage1+Stage2 banks and short-limit stress, verify default with environment cleared, and obtain a frozen SHA. No official hidden or positive-RAM-limit claim.

## Local acceptance and timing caveat

The package was independently compiled, passed **60/60** local exhaustive verification checks on 10 fixture cases, and passed an additional **12/12** exhaustive checks on actual Stage2 `case_003`/`case_005` (inputs not bundled). The standalone submission built from scratch and passed two more independent checks.

**Caveat:** some large public cases produce different valid Area results under repeated same-source, same-mode calls because the inherited synthesis uses real elapsed-time stop rules. Consequently, the official gate records paired casewise Area/Delay/Runtime and does not falsely require bit-identical netlists across wall-sensitive cases. See `docs/02_LOCAL_ABLATION_AND_LIMITS.md`.

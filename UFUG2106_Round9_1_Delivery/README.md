# UFUG2106 — Round 9.1 Experimental Library Rewriting

**Status: independent R9.1 experimental delivery; NOT integrated Stage 2 submission; not verified with the course evaluator in this environment.**

## What this round adds

- A *new* function-indexed cut-expression library (`src/r91_library.hpp`) with 13,956 tested 2–4-input recipes (AND/OR chains, factored two-pair forms, MUX, XOR2/3, and Majority). Each instantiated recipe is independently tested over all 2^k cut assignments.
- A conservatively guarded `UFUG_R91_POLICY=library` **postprocessor** after the frozen Round 9.0 synthesis. Default is `off`: no algorithm replacement is allowed until the official comparative evidence supports it.
- Same search cap (160 selected roots, nominal 90ms / 6% of case Runtime Limit (periodic deadline checks may overshoot)) for `library`, `repeat_sop`, and `repeat_shannon`, with per-run exact netlist verification. The emergency deadline and source graph can still create runtime variation.
- A frozen Round 9.0 comparator whose source SHA is `f846b2c055bfd5ad8d252dd1dcaa6770040b290bff6dc2bddc0ab27ff77e4010`.
- Evidence of a **negative outcome**: on one complete local Stage 2 pass, the library did not improve on matched old-algorithm pass, and on the four one-time lockbox cases it yielded no Area improvements. Do not claim library superiority.

## WSL: genuine evaluator

Extract this folder into your original course `Final Project` folder, beside the supplied `evaluator` and `data/stage1`, `data/stage2`:

```bash
BASE="/mnt/e/canfiles/Common courses study/大学通识/26-27 Fall/UFUG 2106 Discrete Math/assignment/Final Project"
cd "$BASE" || exit 1
bash UFUG2106_Round9_1_Delivery/run_round91.sh
```

The default gate runs **five configurations × two public stages × two runs × 25 cases = 500 official case evaluations**, with reverse execution order in run 2. A feedback ZIP is generated on success and on failure. Upload it for casewise comparison.

Other modes:

```bash
bash UFUG2106_Round9_1_Delivery/run_round91.sh --local-only
bash UFUG2106_Round9_1_Delivery/run_round91.sh --quick
```

`--local-only` verifies exact Boolean correctness and source-only build without claiming course results. `--quick` performs a shorter gate and **only one official run**; it is not enough to demonstrate stability.

## Candidate flags (research ONLY)

`UFUG_R91_POLICY` choices:

- `off` (default): frozen Round9.0 synthesis with no additional optimization
- `library`: the new local function-indexed expression library
- `repeat_sop`: same extra root/time allowance using original SOP construction
- `repeat_shannon`: same extra root/time allowance using original Shannon construction

Optional `UFUG_R91_ROOT_CAP=160` (range 20–400); `UFUG_R91_PROFILE=1` emits counters. The script controls all flags explicitly, clearing inherited UFUG environment variables. **Do not assume the official grading server sets custom environment variables**.

## Frozen data and source

- `hard_bank/dev`: four development cases.
- `hard_bank/lockbox`: four cases that were opened *once only* after freezing the R9.1 algorithm SHA (`345982dc...`), and must not be reused for tuning.
- `holdouts` and `stress_v2`: exact normalized independent tests from R9.0.
- `evidence/local_4way_summary.csv`: explicit negative/positive local comparisons.
- `evidence/r90_official_stress_9.csv`: official R9.0 stress summary, extracted from user-provided feedback.
- `submission`: cold-buildable source tree with library OFF by default, not a final merged submission.

The package contains NO course evaluator or proprietary public-bank data. Local Stage 2 ablation was performed against unmodified public cases available during development, with exact equivalence checks; those inputs are intentionally excluded from the ZIP.

## Next decision

If `library` does not outperform `repeat_sop` or the frozen baseline on **official paired evaluation**, retain R9.0 as the default and do not merge Library merely for novelty. Round 10 focuses on the teammate-integrated final solver, the remaining Issue #2 BDD budget reallocation, cold-build isolation, and final report. R9.2 resubstitution remains optional and only justified by new independent evidence.

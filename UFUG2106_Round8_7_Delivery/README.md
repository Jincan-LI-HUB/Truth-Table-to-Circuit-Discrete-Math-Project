# UFUG2106 — Round 8.7: Robustness & Generalization Gate

**Frozen-comparator research package; NOT a new synthesis algorithm and NOT a hidden-case score.**

This package holds the exact C++17 source snapshots from R8.6 (`extra_sop` / `baseline`) and R8.5 (`budget_reclaim`). No previous delivery folder is needed for build or local verification. Source SHA-256 and test-bank SHA-256 are checked before execution. The independent Boolean-function generator was frozen before evaluating the new bank, and the truth-table inputs are included for reproduction.

## What is new

- `holdouts/`: 36 fixed-seed **new synthetic** cases across seven Boolean circuit families, 6–20 inputs, 3–20 outputs, and runtime limits of 100/1000/3000 ms. These are **not course hidden tests** and are not a statistical representation of the unseen grader distribution.
- `tools/run_holdouts.py`: 36 × 3 synthesis strategies × 2 reversed-order repetitions = **216** checks, each using a separate exhaustive verifier (all `2^n` input assignments), measured wall time, approximate peak RSS, output SHA, and per-case performance.
- `stress_v2/`: three *separate adversarial* cases that tighten the time limit to 100 ms without changing the original Boolean function or Target Delay. These are reported independently and do not count toward the ordinary holdout gate.
- `tests/test_cold_build.py`: source-only cold build and exact check without any historical Round directories.
- `tools/run_public.py`: optional genuine course evaluator on original public Stage 1 and Stage 2 banks; no fabricated official result.

## WSL commands

Unzip this directory alongside the **unmodified course** `evaluator`, `data/stage1` and `data/stage2`:

```bash
BASE="/mnt/e/canfiles/Common courses study/大学通识/26-27 Fall/UFUG 2106 Discrete Math/assignment/Final Project"
cd "$BASE" || exit 1
bash UFUG2106_Round8_7_Delivery/run_round87.sh
```

Modes:

- `--quick`: 12 holdout cases × 3 variants × 1 run, isolated build, original public banks (3 variants × both stages × 1 run).
- `--local-only`: full 216 synthetic checks, source-only build, **without course evaluator**.
- `--stress-only`: deliberately difficult n=20 / 100 ms scenarios, local measurement and **actual course evaluator when available**. Sensitivity study only. It does **not** assert a release pass.
- No flag: 216 synthetic checks, isolated build, and 300 genuine public evaluation records (3 policies × 50 cases × 2 runs), with reversed order in the second run.

Always creates a `feedback/Round8.7_Feedback_<timestamp>.zip`, including the experiment data and original source. A missing course evaluator is an explicit error for `--quick`/full; use `--local-only` if you only want independent checks.

## Local results (nonofficial)

The test bank was fixed *before* these results were obtained. On the current Linux host, 216/216 synthesized netlists were functionally correct, target-met and below their test-input wall-time limits. 108/108 run1/run2 netlist SHA pairs were identical. All three variants had identical Area and Delay on all 36 cases. The maximum `/usr/bin/time` peak RSS across policies was ~36.3 MiB. These are evidence of correctness and limited stability, **not evidence that Extra SOP generalizes a score advantage**.

Stress-only inputs have target delay 170 and runtime_limit 100. Two large n=20 stress functions exceeded 100 ms **locally**, despite correct netlists, while an n=18 sparse function did not. **This is not a claim about the grading server**. Use `--stress-only` for genuine evaluator verification on your WSL machine. See `docs/03_BOUNDARIES_AND_NEXT_STEPS.md`.

## Scope and limitations

- The final grader has 50 unseen hidden cases. These tests do not expose or predict their distribution.
- Official public PASS is not claimed until the WSL run succeeds with the course binary.
- The latest TA email states the grader does not impose a positive RAM limit. Still report RSS to catch scaling errors.
- The peak RSS from `/usr/bin/time` is diagnostic and can differ from the evaluator's accounting.
- Wall time includes process-launch overhead; it is a **conservative comparison** rather than an exact reproduction of the evaluator's timer.
- No new logic rewriting rules were added in R8.7. Novel library rewriting/resubstitution is deferred to Round 9.

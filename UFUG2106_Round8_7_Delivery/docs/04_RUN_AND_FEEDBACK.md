# How to verify in WSL

```
BASE="/mnt/e/canfiles/Common courses study/大学通识/26-27 Fall/UFUG 2106 Discrete Math/assignment/Final Project"
cd "$BASE" || exit 1
bash UFUG2106_Round8_7_Delivery/run_round87.sh
```

- Default: full 216 local synthetic comparisons, isolated cold build, 300 public case evaluations by **original unmodified** course evaluator (three policies, both stages, two reversed-order runs).
- `--quick`: 12-case local quick pass and one public run.
- `--local-only`: full holdouts and cold build, no course binary required.
- `--stress-only`: three adversarial short-runtime inputs and two policies; if course evaluator binary is present, runs that binary on each input and preserves raw CSV/log. No unconditional PASS claim is made here.

A `Round8.7_Feedback_<timestamp>.zip` is always emitted on success/failure. Please upload that one ZIP. Review specifically `experiment/holdout/summary.json`, `experiment/official/summary.json`, `experiment/adversarial_stress/summary.csv` when present, and original `*.log` files.

The current setup has no actual course evaluator executable, so a local test of the default full official path must fail explicitly, rather than fabricating a score.

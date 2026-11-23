# Round 8.7 deeper audit — preliminary submission safety / Round 9 planning kit

**This is a diagnostic/research package, NOT a replacement for Round 8.7, NOT a new Round 9 algorithm and NOT the final submitted Stage 2 source.**

- `ROUND87_DEEP_AUDIT_AND_ROUND9_DECISION.md`: read first; includes full evidence, invalid inference boundaries and go/no-go protocol.
- `comparison_summary.csv`, `official_300_records.csv`, `holdout_216_records.csv`: direct audit of user-supplied feedback, no hidden case access.
- `prepare_r87_next_gate.py`: creates PDF-spec formatted *copies* of frozen holdout/stress cases; optionally creates a *copy* of R8.6 source with the no-environment default set to `extra_sop`, checking parent SHA-256.

## Use on your WSL machine

Unzip this audit kit next to `UFUG2106_Round8_7_Delivery`, `evaluator`, and `data` in the `Final Project` folder:

```bash
BASE="/mnt/e/canfiles/Common courses study/大学通识/26-27 Fall/UFUG 2106 Discrete Math/assignment/Final Project"
cd "$BASE" || exit 1
python3 Round8_7_Deep_Audit/prepare_r87_next_gate.py \
  --delivery UFUG2106_Round8_7_Delivery \
  --output Round8_7_Deep_Audit/preflight \
  --stress-only --make-default-extra-sop-copy
cd Round8_7_Deep_Audit/preflight/standalone_extra_sop
# Note: compile only this copied source tree, not any historical delivery in-place
g++ -O2 -std=c++17 -pipe -DNDEBUG src/synth_round86.cpp -o synth_submission_candidate
```

Then, from `BASE` (return with `cd "$BASE"`), run genuine evaluator **only as a sensitivity diagnostic**, not a release gate:

```bash
P="$BASE/Round8_7_Deep_Audit/preflight"
mkdir -p "$P/evaluator_reports"
for f in "$P"/canonical/stress_v2/stress_*.txt; do
  name="$(basename "$f" .txt)"
  # A nonzero result is relevant diagnostic evidence, not a script error to hide
  "$BASE/evaluator" "$P/standalone_extra_sop/synth_submission_candidate" "$f" \
    --report "$P/evaluator_reports/$name.csv" \
    >"$P/evaluator_reports/$name.log" 2>&1 || true
  cat "$P/evaluator_reports/$name.log"
done
```

To canonicalize all 36 holdouts as well, omit `--stress-only` and choose a new output directory. The generated files strictly follow line 1 = n, line 2 = m, line 3 = one space-separated truth-table line, unlike the prior synthetic bank. Verify equivalence and runtime on these copies before relying on the results.

The changed default is **NOT** proof that hidden cases pass. Submit only the team-integrated, fully regression-tested final code.

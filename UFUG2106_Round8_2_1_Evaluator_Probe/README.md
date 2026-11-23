# Round 8.2.1 Official Evaluator Probe — diagnostic runner patch

**Scope:** Repairs and instruments the Round 8.2.1 *test harness*, not the C++ synthesizer. The uploaded WSL log showed that all 10 direct resource tests pass, but `run_resources.py` stopped when the actual official evaluator first ran. The prior script supplied a mixed-content directory (case `.txt` plus logs and `.netlist`) as the evaluator's benchmark folder, and discarded evaluator details from the console.

**Diagnosis status:** The mixed-content directory is a concrete harness flaw; whether it was the *actual* failure cause remains unconfirmed until `official_folder.log` from the original failed run is examined. The probe calls the actual course evaluator on an isolated directory containing only `case_001.txt`. On failure, it also tries the documented single-file mode, preserving both attempts, stdout/stderr, exit codes, CSV reports, and an explicit diagnostic summary. No mock evaluator is used by `run_retry.sh`.

## Use in WSL

Extract this ZIP alongside the existing `UFUG2106_Round8_2_1_Delivery` under `Final Project`. The original source code and `SOURCE_MANIFEST.json` are **not modified**.

First diagnose the official resource evaluator without running the full 50-case benchmark:

```bash
BASE="/mnt/e/canfiles/Common courses study/大学通识/26-27 Fall/UFUG 2106 Discrete Math/assignment/Final Project"
cd "$BASE" || exit 1
bash UFUG2106_Round8_2_1_Evaluator_Probe/run_retry.sh --resources-only
```

If the 4 official resource cases succeed, run the complete frozen-code paired benchmark:

```bash
bash UFUG2106_Round8_2_1_Evaluator_Probe/run_retry.sh
```

For a short probe: `bash UFUG2106_Round8_2_1_Evaluator_Probe/run_retry.sh --resources-only --quick`.

An optional `--single-file-only` tests the evaluator's documented single-case input mode, without the folder attempt.

All runs save evidence in `UFUG2106_Round8_2_1_Delivery/results/<timestamp>_official_probe/` and automatically export `UFUG2106_Round8_2_1_Delivery/feedback/Round8.2.1_Feedback_<timestamp>_official_probe.zip` on PASS **or FAIL**. Upload that single feedback ZIP (or the old failed ZIP) for analysis. The original `official.log` for the earlier failed run is available in the earlier ZIP at `experiment/resource_tests/wire/official.log`.

## What is and isn't established

- **Established:** The previous folder contained other artifacts besides case inputs; the official interface permits passing one case or a benchmark folder. Isolating input removes an avoidable ambiguity.
- **Not established:** That this ambiguity caused the observed nonzero evaluator status. We need the saved log to confirm. In particular, if evaluator fails despite a clean directory, report that failure rather than claiming solver RAM safety is resolved.
- A mock evaluator in `tests/` is used **only** to locally verify that the wrapper creates a clean directory and parses a CSV correctly. It is not proof of official correctness.
- No Stage 1 or Stage 2 official results are claimed until the user's WSL evaluator runs.

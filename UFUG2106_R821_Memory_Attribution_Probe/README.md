# Round 8.2.1 — Official MEMORY_LIMIT attribution probe

**Purpose:** Determine why the genuine course evaluator marks a zero-gate 20-input wire example as `MEMORY_LIMIT` despite the independent C++ process measurement reporting RSS below 9,000 KiB. This probe is **diagnostic only**. It does not modify the Round 8.2.1 synthesizer, submit substitute answers, or claim a release gate.

## Evidence leading to this probe

`Round8.2.1_Feedback_20261121_202416_182376486.zip` contains:

```
FAIL case_001.txt | n=20 m=1 reason=MEMORY_LIMIT exit_code=0 target_delay=10
```

The solver's independent peak runner reported `3840 KiB` and the output is `20` (zero gates). A mismatch in the evaluator's memory accounting, memory metric, process startup, or WSL-specific runtime remains possible. Prior guesses about polluted input directories are not sufficient to explain the explicit `MEMORY_LIMIT` result.

## Run in WSL

Extract alongside `UFUG2106_Round8_2_1_Delivery` and `./evaluator` under `Final Project`:

```bash
BASE="/mnt/e/canfiles/Common courses study/大学通识/26-27 Fall/UFUG 2106 Discrete Math/assignment/Final Project"
cd "$BASE" || exit 1
bash UFUG2106_R821_Memory_Attribution_Probe/run_probe.sh
```

Short version (`6` runs rather than `14`):

```bash
bash UFUG2106_R821_Memory_Attribution_Probe/run_probe.sh --quick
```

**Output:** `UFUG2106_R821_Memory_Attribution_Probe/feedback/R821_Memory_Attribution_Feedback_<timestamp>.zip` contains raw evaluator outputs, CSV reports, direct child memory measurements and a JSON matrix. Upload one feedback ZIP for diagnosis.

### What is tested?

All fixtures implement the *same* simple function `y=x_(n-1)` and have a target delay of 10, runtime limit of 0.

- Compare the real Round 8.2.1 C++ solver with a **diagnostic-only** minimal C fixture writer. The tiny C program is correct for these wire fixtures only; **never submit it**.
- Compare no RAM limit (`0`) with `9,000`, `16,000`, `32,768`, `65,536 KiB`.
- Compare 20-input versus 12-input truth tables under the same limit.
- Compare evaluator single-file and clean single-case-folder modes at `9,000 KiB`.

The runner is pure C and samples RSS and VmPeak from `/proc` in addition to collecting `wait4` ru_maxrss. This avoids the earlier Python fork/exec artifact.

### How to read the results

| Observation | Strongest interpretation | Limitations |
|---|---|---|
| Both tiny C and full C++ report `MEMORY_LIMIT` with cap=9000 | Evaluator monitoring/startup/input parsing becomes the first suspect | Not yet proof of evaluator bug |
| Tiny C PASS, full C++ FAIL under the same cap | Solver-specific memory characteristic, potentially VmPeak/loader or transient allocations | Inspect direct VmPeak/RSS and memory thresholds |
| Both PASS with cap=0, FAIL with cap=9000 | Failure tied to memory gate, not circuit correctness | May be either evaluator or solver usage |
| 12-input PASS, 20-input FAIL for tiny C | Failure scales with truth-table size or evaluator input handling | Input-dependent evaluator overhead is a hypothesis |
| File PASS, folder FAIL (or vice versa) | Invocation path influences evaluation | Compare exact raw logs and report rows |

**Do not treat a successful local direct RSS check as official RAM compliance.** Any evaluator FAIL keeps Issue #2 open. The course evaluator binary and its actual measurement implementation are not included in this package.

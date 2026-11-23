# Round 8.2.1 — MEMORY_LIMIT Attribution: Official Probe Audit

**Date:** 2026-11-21  
**Evidence:** User-provided `R821_Memory_Attribution_Feedback_20261121_204445(1).zip`.  
**Observed environment:** WSL2 Linux 6.6.87.2, actual course evaluator SHA-256 `142361d7ce18bc47dea6a07538db79a588b3afbf446526c1d1246f4968b3d0ca`.  
**Status:** Robust evidence for a *process-launch peak-memory accounting discrepancy*; exact evaluator implementation is not available for code-level confirmation.

## 1. What is proven by the user's logs

All 14 evaluator invocations returned internally consistent CSV/terminal results. The same valid wire-function input was solved with both (a) the full Round 8.2.1 C++ solver and (b) a minimal C program that emits the correct input-signal ID. Both programs PASS without RAM limit, FAIL with `MEMORY_LIMIT` at 9,000 and 16,000 KiB, and PASS at 32,768 and 65,536 KiB. For the 12-input input with RAM cap 9,000 KiB, both also FAIL, in single-file mode. For 20 inputs, both single-file and isolated-folder mode FAIL at 9,000 KiB. The exit code of the solver itself is zero in failing official tests. The netlist contains only the wire signal ID.

| Inputs | RAM cap (KiB) | Patched C++ | Minimal C | Notes |
|---:|---:|---|---|---|
| 20 | 0 | PASS | PASS | No memory cap |
| 20 | 9,000 | MEMORY_LIMIT | MEMORY_LIMIT | File and folder modes both fail |
| 12 | 9,000 | MEMORY_LIMIT | MEMORY_LIMIT | Smaller truth table also fails |
| 20 | 16,000 | MEMORY_LIMIT | MEMORY_LIMIT | File mode |
| 20 | 32,768 | PASS | PASS | File mode |
| 20 | 65,536 | PASS | PASS | File mode |

The minimal C diagnostic recorded its *own* resource usage **inside the officially launched process**:

| Inputs | RAM cap (KiB) | `getrusage(RUSAGE_SELF).ru_maxrss` (KiB) | `/proc/self/status` VmHWM (KiB) | VmPeak (KiB) | Official outcome |
|---:|---:|---:|---:|---:|---|
| 20 | 0 | 28,128 | 1,344 | 2,684 | PASS |
| 20 | 9,000 | 27,964 | 1,344 | 2,684 | MEMORY_LIMIT |
| 12 | 9,000 | 14,016 | 1,344 | 2,684 | MEMORY_LIMIT |
| 20 | 9,000 | 28,136 | 1,344 | 2,684 | MEMORY_LIMIT (folder) |
| 20 | 16,000 | 28,132 | 1,344 | 2,684 | MEMORY_LIMIT |
| 20 | 32,768 | 28,124 | 1,344 | 2,684 | PASS |
| 20 | 65,536 | 28,132 | 1,344 | 2,684 | PASS |

The `getrusage` values closely straddle the official PASS/FAIL thresholds, despite the minimal C executable's actual current-image peak RSS being only 1,344 KiB. A **separate low-footprint launcher** measured the minimal C program's process peak RSS at about 1,536 KiB. The corresponding direct measurement for the patched C++ solution with a positive RAM cap was about 3,840 KiB. Thus this is **not** explained by the patched algorithm using >9 MiB of current-image RSS.

## 2. Strongest causal explanation, and what remains unverified

Linux `getrusage(2)` explicitly documents that resource usage measurements survive `execve(2)`; `ru_maxrss` is the historical maximum resident set size. In a `fork` -> `exec` launch, a large evaluator process may be inherited by a child briefly before the new executable replaces its address space; thus `ru_maxrss` can include the *pre-exec evaluator footprint*, whereas the current executable's `/proc/self/status` VmHWM is small. This mechanism is also reproduced on an independent Linux host by `verify_exec_peak.py` (run it to reproduce locally; it is not a replay of the course evaluator).

The approximately 14 MiB `ru_maxrss` value on the 12-input input versus approximately 28 MiB on the 20-input input is consistent with the evaluator's parent process having loaded a larger truth table *before* starting the contestant process. This is strongly suggestive but not direct evidence of the exact evaluator code path.

**Not proven:** that the course evaluator necessarily reads `ru_maxrss`, how it launches the subprocess, or whether its resource metric is documented elsewhere. Only the course team's source or instrumented accounting can establish that precisely. The official evaluator's `MEMORY_LIMIT` result should still be reported accurately, not overwritten with our own PASS label.

References: Linux man-pages `getrusage(2)` https://man7.org/linux/man-pages/man2/getrusage.2.html (see NOTES on `execve`); https://jkz.wtf/random-linux-oddity-1-ru_maxrss (mechanism illustration).

## 3. Recommended course-staff action

Request that the course team check whether their memory monitor uses `getrusage`/`wait4` max RSS from a `fork`/`exec` child and, if so, whether it includes the evaluator's own pre-exec footprint. A per-program-image monitor or a launcher whose footprint is reset/isolated before starting the solution would avoid penalizing the solution for evaluator memory, but the exact fix should be implemented and verified by the course team. The published spec says `ram_limit` constrains the program's memory. The student cannot fix a baseline imposed upstream by the monitor simply by shrinking an already tiny C program.

Do not change user testcase RAM limits, fabricate evaluator PASS, or claim that the student solver is fully compliant on the official checker until confirmed. The original Round 5.1/8.2 memory-heavy path *was* a genuine risk; the standalone R8.2.1 hotfix independently reduced that peak. Both findings can coexist.

## 4. Suggested concise report to teaching staff

Subject: Possible evaluator RAM accounting discrepancy on minimal zero-gate circuit

We observed that both our standalone solver and a minimal C program generating a valid zero-gate wire circuit fail the provided evaluator with `reason=MEMORY_LIMIT` at `ram_limit=9000`, despite the minimal C process reporting VmHWM=1344 KiB and VmPeak=2684 KiB. Under the evaluator, the same C process reports `getrusage(RUSAGE_SELF).ru_maxrss` around 28,000 KiB for a 20-input fixture (about 14,000 KiB for 12 inputs). Both executables PASS with `ram_limit=32768` and FAIL at 16000, matching the historical `ru_maxrss` rather than the process-image VmHWM. Linux resource usage metrics can persist across `execve`, so one possible cause is the evaluator's pre-exec memory being included in the child peak. Could the evaluator's memory accounting and process-launch path be checked? We can provide a reproducible fixture, minimal C source, logs, and the evaluator SHA-256.

## 5. Safe continuation of main benchmarking

Until this is clarified, keep the positive-memory-cap release gate as FAIL/UNRESOLVED. It is nevertheless possible to run **development-only** official Stage 1/Stage 2 regression separately, without editing testcase limits or changing evaluator outcomes:

```bash
BASE="/mnt/e/canfiles/Common courses study/大学通识/26-27 Fall/UFUG 2106 Discrete Math/assignment/Final Project"
cd "$BASE" || exit 1
RUN="$BASE/UFUG2106_Round8_2_1_Delivery/results/stage_regression_$(date +%Y%m%d_%H%M%S)"
mkdir -p "$RUN"
python3 UFUG2106_Round8_2_1_Delivery/tools/run_official.py --results "$RUN" --runs 2
```

This *does not* constitute passing the full RAM release gate. It separately checks whether the code patch regresses existing public testcases.

## 6. Evidence files

- `comparison_14_cases.csv`: all 14 matched official conditions, direct measurements, child self-measurements and SHA-256s.
- `official_and_memory_logs/`: exact per-case official stdout, CSV, direct monitor, and minimal-C in-process measurements.
- `tiny_wire.c`: original diagnostic-only C source; valid for the supplied wire-function test, not a general synthesizer.
- `input_n12_ram9000.txt`, `input_n20_ram9000.txt`: exact original wire-function fixtures.
- `attribution_original.py`: original user-supplied diagnostic harness.
- `measure_exec_memory.c`, `verify_exec_peak.py`: independent Linux memory-statistic demonstration, not official evaluator emulation.

**Status:** Issue #2 remains OPEN. Escalate evaluator-accounting question to course team; protect Round 8.2.1 as the independent local memory fix. Continue Stage 1/2 paired benchmarking as a separate, labelled development activity.

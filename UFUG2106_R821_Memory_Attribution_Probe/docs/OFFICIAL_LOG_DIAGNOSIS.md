# Official evaluator memory-limit failure — diagnosis record

## Source of truth

User-supplied feedback: `Round8.2.1_Feedback_20261121_202416_182376486.zip`.

Within `experiment/resource_tests/wire/official.log`, the actual course evaluator printed:

```
FAIL case_001.txt | n=20 m=1 reason=MEMORY_LIMIT exit_code=0 target_delay=10
0/1 passed
```

`official.csv` exists and contains `FAIL`, blank area/delay/time and blank `target_met`. The original Python harness raised an exception because evaluator's status was nonzero. That exception is a secondary symptom, not the root diagnosis.

Within the same archive:

- `case_001.netlist` contains only `20` and a newline: a legal zero-gate wire.
- `verify.log`: `PASS exact_assignments=1048576 area=0 delay=0 target=10`.
- `peak_rss.log`: `R821_PEAK_RSS_KIB=3840 ... EXIT=0`.
- The final case lines are `1 1`, `1 1`, `1 1`, `10`, `0`, `9000`. Thus the `runtime_limit` is disabled and the RAM limit is 9,000 KiB.

The explicit `MEMORY_LIMIT` log rules out output incorrectness as the *reported* cause, and means directory contamination is not an evidenced explanation. The independent memory measurement and the evaluator are in conflict, but no specific monitor implementation is yet established.

## Plausible mechanisms (NOT findings)

- The evaluator may count peak virtual address space or a different memory measure rather than RSS.
- Its process-launch sequence may include pre-`exec` inherited pages in a measured peak. This is a known pitfall when using `ru_maxrss` in `wait4` after forking from a large supervising process, but is **not** proven about this evaluator.
- WSL runtime mappings differ from the local Linux reproduction.
- The course evaluator may measure a more comprehensive per-process or process-tree usage than the separate `peak_runner`.

Local independent execution on the analysis host measured peak RSS about 2.1 MiB and a sampled peak VmSize about 6.6 MiB, both below 9,000 KiB. This is *not* a substitute for WSL or official measurements.

## Decisive next test

The supplied `run_probe.sh` compares:

1. The same 20-input, million-row wire truth table with the frozen Round 8.2.1 solver vs a minimal *C-only fixture writer*. Both compute the identical correct wire output. If both fail at 9,000 KiB despite low independent memory, investigate evaluator accounting before modifying the synthesis algorithm.
2. A 12-input wire case with the same cap to assess dependence on input file size and evaluator parsing.
3. The identical 20-input case with RAM cap 0, 16,000, 32,768, and 65,536 KiB to bracket the pass threshold.
4. Single-case file vs isolated folder modes to eliminate incidental path effects.

A minimal C fixture writer is NOT a general solution or a valid Stage 2 submission. It exists solely to distinguish evaluator accounting from the real synthesizer's memory demand.

The authentic `evaluator` binary is unavailable in the analysis container. This test package has been syntax/compile checked and exercised with a clearly labeled, isolated mock evaluator to validate *harness mechanics only*. No mock outcomes appear in the deliverable.

## Acceptance and workflow

- Treat all actual `MEMORY_LIMIT` outputs as release-blocking until explained and fixed.
- Keep GitHub Issue #2 open.
- Do not change the production C++ solver or its source fingerprints based on an unverified theory about the evaluator.
- Once the matrix returns, distinguish candidate code changes from evaluator/workflow issues. Only thereafter rerun the official Stage 1 and Stage 2 comparisons.

# UFUG2106 — Round 8.2.1: Resource Compliance / Memory-Safe Synthesis

**Status:** self-contained C++17 source compiles; 10 direct low-RAM tests pass locally; frozen 24-case structured holdout produces byte-identical output to Round 8.2. **Official Stage 1/2 and positive `ram_limit` evaluator results are pending on the user's WSL host.** Do not call this a final submission or close GitHub Issue #2 yet.

## Scope

This is a deliberately limited **resource-correctness hotfix** to Round 8.2, not an additional cut-search optimization. It fixes parsing of the independent ninth-line `ram_limit` (KiB), gives limited-memory functions a low-allocation synthesis path, admits a legacy BDD only if a conservative size estimate fits, and avoids optional search after a valid zero-area circuit.

Primary references: [`Final_Project.pdf`](../Final_Project.pdf), [GitHub Issue #2](https://github.com/Jincan-LI-HUB/Truth-Table-to-Circuit-Discrete-Math-Project/issues/2), frozen `UFUG2106_Round8_2_Delivery/src/synth_round82.cpp` SHA-256 `07ca91581854fe3802ae0165674a3352771f1745ea85beee6608ee720f9a1caa`.

## Run on WSL

Unzip alongside `UFUG2106_Round8_2_Delivery` in the existing `Final Project` folder (also containing the actual course `./evaluator` and `data/stage1`, `data/stage2`).

```bash
BASE="/mnt/e/canfiles/Common courses study/大学通识/26-27 Fall/UFUG 2106 Discrete Math/assignment/Final Project"
cd "$BASE" || exit 1
bash UFUG2106_Round8_2_1_Delivery/run_round821.sh
```

For a shorter initial benchmark:

```bash
bash UFUG2106_Round8_2_1_Delivery/run_round821.sh --quick
```

The default protocol first compiles and checks hashes; runs direct OS RSS checks and exact truth-table verifications for 10 positive memory-limit cases; runs the real official evaluator on four RAM-limited cases; then runs **two reversed-order paired tests for both 25-case stages** with frozen R8.2 and R8.2.1 under matched `fast_adp`, `fast_area`, `dual_area` configurations.

The script always exports a **single feedback ZIP**, even if a compiler, resource test, or official evaluator fails:

```
UFUG2106_Round8_2_1_Delivery/feedback/Round8.2.1_Feedback_<timestamp>.zip
```

Upload that ZIP for detailed official-result review. Failure cases remain visible, and the script does **not** substitute mock official results.

## Standalone compile / direct resource test

```bash
make -C UFUG2106_Round8_2_1_Delivery -j1
python3 UFUG2106_Round8_2_1_Delivery/tools/run_resources.py \
  --results UFUG2106_Round8_2_1_Delivery/results/manual_resources
```

A bundled small C++ `peak_runner` uses `wait4` to capture child peak RSS without relying on an external `/usr/bin/time` package or Python fork memory. `tests/verify_exhaustive.cpp` independently checks all \(2^n\) assignments, not sampling. The official evaluator remains authoritative for `ram_limit` compliance.

## Implementation, safety guarantees and limitations

The standalone source and local headers are bundled and **do not require re-generating the patched source from a plugin**. `src/source_patch.diff` records the exact change against frozen R8.2; `SOURCE_MANIFEST.json` stores SHA-256 hashes.

There are four low-memory paths: streaming constants/direct inputs/complements; complete truth-table-verified affine detection; exact-support Shannon resynthesis (at most 10 support variables **per output**); and compact bit-packed bounded-node ROBDD construction with a structural-hash and later associative balancing. All are general function-based decisions, **not case-ID special cases**.

If a function is not solved by these paths and the estimated memory for the frozen eager BDD exceeds the declared RAM limit, the program exits with **code 14** and an `R821_RESOURCE` diagnostic rather than knowingly beginning a large allocation. This behavior prevents one failure mode but means **the patch does not guarantee a solution for every feasible RAM-limited input**. In particular, size estimates are conservative heuristics, *not a formal cap on all allocator overhead or OS RSS*. Unexpected resource-related failure should be reported and investigated, not called a PASS.

For unbounded / omitted RAM limits, the logic synthesis path is unchanged except the provably optimal zero-area/zero-delay early exit. For positive but sufficiently large RAM limits, the eager BDD path is admitted by the conservative estimator; otherwise the compact solver is used. Under a tight positive RAM cap, further optional search is not attempted once a feasible incumbent exists.

The legitimate output remains strictly `AND2/OR2/NOT` (plus constant-zero/input wires) in the original format.

## Evidence and outstanding issues

- Original unchanged Round 8.2 on the 20-input wire / 9,000 KiB counterexample: **34,104 KiB** peak RSS in this local Linux container (measurement, *not* official evaluator).
- New Round 8.2.1 on same counterexample: **approximately 2,120 KiB** peak RSS and Area 0 / Delay 0; complete 1,048,576-row truth-table check passes.
- Additional 20-input tests (`xor2`, `majority3`, `multi`, `four_var`, `parity_all`, `and_all`, `or_all`, constants and inversions): **10/10** direct per-process memory compliance under 9,000 KiB, verified exhaustively.
- The `and_all` and `or_all` full-support cases produce **Area 19 / Delay 5** and use about 5.1 MiB RSS in the local environment; they exercise the memory-bounded packed BDD path.
- **24/24** frozen `holdout_structured_v2` cases produce **byte-identical netlists** compared with Round 8.2 under unbounded RAM.
- The course official evaluator is unavailable in the current container. Official 50-case regression and official resource PASS are **not claimed**. Use the WSL script.

Read `docs/02_MATHEMATICAL_RESOURCE_DESIGN.md` for correctness arguments, `docs/03_TEST_EVIDENCE_AND_LIMITATIONS.md` for limits and negative evidence, and `docs/04_OFFICIAL_PROTOCOL.md` for the WSL acceptance gate.

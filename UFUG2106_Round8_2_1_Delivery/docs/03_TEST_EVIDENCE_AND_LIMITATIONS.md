# Round 8.2.1 Local Evidence and Negative Results

## Reproducer and measurements

Same Linux container, same source compiler flags `g++ -O2 -std=c++17 -pipe -DNDEBUG`, 20 inputs, one output equal to the least-significant input, line-8 runtime limit zero, line-9 RAM 9,000 KiB.

| Binary | Peak RSS (KiB) | Area | Delay | Direct exact verifier |
|---|---:|---:|---:|---|
| Frozen R8.2 | 34,104 | 0 | 0 | Original output is a wire; baseline is memory-ineligible under 9,000 KiB |
| R8.2.1 | about 2,120 | 0 | 0 | PASS, 1,048,576 assignments |

The original value was independently measured here, not copied from Issue #2's integrated measurement (13,952 KiB). Distinct executables can have distinct peak memory. The low-memory result was also measured in several separate runs; naturally RSS fluctuates slightly.

## Additional tests under 9,000 KiB

Eight other meaningful patterns plus the wire test were checked, along with constant/inversion and repeated multi-output functions. Local results in `evidence/round821_memory_experiments.log`; the actual WSL command regenerates each input under a unique results directory, stores peak RSS and exact verifier output, and evaluates selected cases under the **real course evaluator**.

Key exact results after simplification and rebalancing:

- 20-input XOR of the two lowest bits: **Area 4, Delay 3**; 1,048,576 assignments matched.
- 20-input AND of all inputs: **Area 19, Delay 5**, local peak approximately 5.1 MiB; 1,048,576 assignments matched.
- 20-input OR of all inputs: **Area 19, Delay 5**, local peak approximately 5.1 MiB; 1,048,576 assignments matched.
- 20-input full parity: **Area 76, Delay 15**, target 40; 1,048,576 assignments matched.
- 20-input three-output combination: full truth table matches under a positive 9,000-KiB RAM limit.

These are source-backed local **direct** evaluations, not official PASS claims. A RAM cap in the input is not enough to establish evaluator compliance without running the evaluator.

## Compatibility regression

R8.2 and R8.2.1 both compiled from frozen sources. On the 24 previously frozen `holdout_structured_v2` inputs without positive RAM caps, both binaries generated **byte-identical** netlists, and independent exhaustive verification passed for each. See `evidence/holdout_structured_regression.json`.

This is stronger than agreeing only on area/delay for those cases, but it still does **not** establish unchanged scores on both official public banks; conduct the two-stage paired official run on WSL.

## Negative results and open risks

- A function with many independent inputs, no detectable affine or narrow-support structure and a large packed ROBDD can exceed the bounded node budget. In that case the function is not synthesized, and the solver returns **14** instead of initiating the previously unsafe large BDD allocation. This is an explicit **remaining coverage limitation**, not a PASS.
- A purely static memory estimate cannot perfectly predict C++ allocator overhead, per-platform RSS, or shared maps. Therefore, after admission, a specific case may still exceed its RAM cap. Official verification and worst-case profiling remain mandatory.
- A highly restrictive runtime limit combined with a low RAM limit can make an additional truth-table preflight itself too slow. Preflight is activated only when the positive RAM limit is below the conservative eager-BDD estimate, reducing this regression risk for ordinary released cases.
- The compact BDD path optimizes feasibility, not minimal gate area. Better global resynthesis can be studied only after resource validity is established.
- Zero-area/zero-delay early exit is valid under the official strictly positive gate costs, but it changes search behavior by design.

## Follow-up research

If WSL official memory cases pass, inspect which cases remain close to both limits. For failures, distinguish a true memory overshoot from a failure to synthesize (exit 14), timeout due to second truth-table pass, and target violation due to conservative local mapping. Keep the Issue open for teammate integration verification until those checks pass.

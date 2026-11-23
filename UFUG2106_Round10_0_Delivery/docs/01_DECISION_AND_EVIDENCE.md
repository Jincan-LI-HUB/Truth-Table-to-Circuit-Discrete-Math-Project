# Round 10.0 Decision Record

## Motivation

Round9.1 WSL official paired experiment: 500/500 PASS, all targets met, and two-run casewise Area/Delay equality. `repeat_sop` total public Area 1,019,547 vs frozen R9.0 Area 1,021,134; total Delay 2,382 unchanged, and time geometric mean ~+3.4%. Library gave Area 1,020,471 with Delay sum +2 and time ~+8.2%. These are prior-round external measurements, not results from the current Round10.0 code.

## Hypothesis

Replacing the missing-policy fallback with `repeat_sop` reproduces explicit Round9.1 SOP follow-up under identical inputs, compiler, environment, runtime and case order. It must not change the underlying 100ms special handling because existing R9.1 branch guard requires `limit>=1000`.

## Invariants

1. All frozen source files have known SHA-256; the parent is never edited.
2. When `UFUG_R91_POLICY=off`, the additional postprocessor is skipped exactly.
3. The original graph metric is compared to the candidate's global graph metric; the pass is accepted only when candidate Area is strictly less and Delay meets the target.
4. No change to the Boolean synthesis construction or serialization path beyond the mode default.
5. Independent `submission/` contains its own transitive C++ headers.

## Limits

This is not a causal proof of hidden-case performance. R9.0 remains a deliberate fallback, and team integration requires a separate merger/validation pass. Library research was closed on return-on-investment grounds rather than correctness failure.

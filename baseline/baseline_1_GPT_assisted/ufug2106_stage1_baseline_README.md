# UFUG2106 Stage 1: BDD Baseline

This is an **experimental reference implementation**, not an optimized final submission.

## Algorithm

1. Read the multioutput truth table.
2. Build a reduced, ordered binary decision diagram (ROBDD), reusing identical cofactors across all outputs.
3. Lower each BDD node using Shannon expansion: `f = (!x & low) | (x & high)`.
4. Apply trivial constant folding and structural hashing to avoid duplicate gates.
5. Write a valid gate-level netlist in the specified format.

Gate costs are parsed, but this baseline **does not currently optimize for them**. The variable ordering is fixed to `x0, x1, ...`.

## Compile

```bash
g++ -O2 -std=c++17 -o synthesizer ufug2106_stage1_bdd_baseline.cpp
```

## Run evaluator (on Linux)

```bash
./evaluator ./synthesizer ./stage1 --report results.csv
```

## Observed result

The prototype passed 25/25 published Stage 1 cases in one evaluator run. 12/25 met target delay; 13/25 exceeded it but still passed. Results reflect the local runtime environment. The evaluator CSV does not contain a numerical grading score.

## Important caveats

- This prototype favors correctness and sharing, not minimum area or delay.
- BDD variable order can greatly affect circuit size.
- Current Stage 1 cases include `n=19` and `n=20` despite the tentative PDF stating `n <= 18`.
- The source is an instructional starting point; inspect and test it before using or extending it.

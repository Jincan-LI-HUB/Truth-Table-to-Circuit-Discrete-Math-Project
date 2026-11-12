# Round 5.1 — Reference experiment (2026-11-11)

**Study type:** Frozen-logic, engineering-only, matched-compiler comparison. **Comparator:** Round 5. This is **container evidence**, not the user's WSL benchmark. Source selection was not tuned on the 96 held-out tests.

## 1. Official Stage 1, two interleaved paired runs

| Metric | Round 5, run 1 | Round 5.1, run 1 | Round 5, run 2 | Round 5.1, run 2 |
|---|---:|---:|---:|---:|
| Official PASS | 25/25 | 25/25 | 25/25 | 25/25 |
| Target Delay Met | 25/25 | 25/25 | 25/25 | 25/25 |
| Sum Area | 529,014 | 529,014 | 529,014 | 529,014 |
| Median Runtime (ms) | 90.006 | 69.389 | 94.047 | 76.986 |
| Runtime sum (ms) | 8,671.618 | 7,438.191 | 8,971.524 | 7,496.963 |

The mean of the two paired-run medians falls from **92.027 ms** to **73.188 ms**, a **20.5% decrease**. Both runs produced identical Area and Delay for each of the 25 cases. In the first run, all 25 emitted Netlists were also byte-identical. An individual case may still regress in runtime because measurements are variable; the first run had 22/25 faster cases, and the second 24/25.

These are *descriptive*, not confidence-interval estimates. Evaluator wall-clock includes process overhead; two interleaved repetitions are an improvement over a single non-paired run, but not a sufficient basis for universal speedup guarantees.

## 2. Held-out correctness and distribution checks

The holdout function generator seed was committed **before Round 5.1 was implemented**. Each generated case is evaluated against the *same* frozen Round 5 reference without modifying the candidate based on test outcomes.

| Corpus | Cases | Round 5 PASS | Round 5.1 PASS | Area / Delay equivalence | Reference median | Round 5.1 median |
|---|---:|---:|---:|---|---:|---:|
| 80 mixed small/medium holdouts | 80 | 80 | 80 | 80/80 exact | 4.880 ms | 4.842 ms |
| 16 larger structured holdouts | 16 | 16 | 16 | 16/16 exact | 121.609 ms | 95.094 ms |
| Existing generated functions | 110 | 110 | 110 | See CSVs | — | — |

The first corpus has small/easy cases, so the runtime improvement is **negligible** there. The larger held-out functions show a **21.8% lower** median runtime, close to the official 25-case trend. The two corpora were **not designed to reproduce Stage 2's unknown distribution**.

All 96 held-out Round 5.1 Netlists passed the independent verifier: 74 were exhaustively evaluated (70+4), while the other 22 were sampled deterministically. The official 25-case Round 5.1 Netlists also passed independent verification (13 exhaustive + 12 sampled).

## 3. Overfitting concern and interpretation

**What this evidence supports:** A typed graph and incremental Arrival propagation reduce repeated parsing/serialization overhead in larger cases, while retaining the Boolean synthesis rules and observed netlist costs. The presence of improvement on the larger held-out set is evidence against an advantage limited solely to public Stage 1 cases.

**What it cannot establish:** That no algorithmic overfitting exists in the earlier Round 1–4.1 selection heuristics, or that any hidden Stage 2 benchmark will have similar properties. The 96 held-out cases are synthetic, correlated within structural families, and do not substitute for independent Stage 2 data. The performance measurement sample is limited, and there is no demonstrated statistical significance for tiny cases.

## 4. Engineering decision

Round 5.1 is **provisionally accepted as an efficiency experiment**. It is recommended for a WSL-local paired replication, but **not yet recommended as a final submission replacement** until the user's actual compile/evaluator environment confirms both 25/25 correctness and measurable speedup. Further code complexity (e.g. a graph-spanning incremental shared-fanout Area update) is **not justified** without a profiling result proving it is the remaining bottleneck. Optimizing Stage 1 median alone is not a sound Stage 2 research objective.

The next high-value direction, if the user chooses to continue, is to improve **Area under delay constraints** on fresh distributions, possibly through cut-based technology mapping, rather than endlessly micro-optimizing runtime once budget constraints are satisfied.

# UFUG2106 — Round 4 Experimental Record

Date of reference experiments: **2026-11-11**. This document records tests performed in the assistant's Linux container. It is NOT yet a reproduction record on the user's WSL machine. The latter is produced by `run_round4_local.sh` in `local_runs/YYYYMMDD_HHMMSS_Round4/report_ready/`.

## Frozen baselines and Round 4 results

| Design | Official Stage 1 PASS | Targets met | Sum of 25 areas | Median runtime in corresponding reference run |
|---|---:|---:|---:|---:|
| Round 3 frozen | 25/25 | 25/25 | 533,705 | 104.064 ms |
| Round 4: phase + algebra only | 25/25 | 25/25 | 532,070 | 188.466 ms |
| Round 4: phase + algebra + extra bounded order search | **25/25** | **25/25** | **528,910** | **188.677 ms** |

Net area improvement of final Round 4 versus Round 3: **4,795** area units, or **0.8985%**. These sums are descriptive, not official scores. The reference runs were not an identical paired controlled-speed experiment and runtime varies with load.

The final Round 4 official reference is `results/reference_round4.csv`; the frozen Round 3 reference is `results/reference_round3.csv`; `results/round3_round4_comparison.csv` stores case-level paired differences. The final Round 4 program is the single-process `src/synth.cpp` built with `-O2 -std=c++17`, not an offline selection assembled from precomputed case outputs.

### Largest area improvements

| Case | Round 3 Area | Round 4 Area | Area saved | Round 3 Delay → Round 4 Delay |
|---|---:|---:|---:|---:|
| case_015 | 36,345 | 33,371 | 2,974 | 62 → 64 |
| case_013 | 12,014 | 11,248 | 766 | 60 → 60 |
| case_024 | 124,830 | 124,466 | 364 | 72 → 72 |
| case_003 | 24,463 | 24,236 | 227 | 55 → 55 |
| case_014 | 11,760 | 11,634 | 126 | 61 → 61 |
| case_018 | 1,350 | 1,231 | 119 | 29 → 31 |
| case_023 | 215 | 123 | 92 | 21 → 22 |

Other cases have small improvements or no change. In particular, the final design does not improve the area of every single published case, and no claim is made that it finds an optimal circuit.

### Independent verification

The instructor evaluator reports `PASS` on all 25 released cases and that every candidate meets its target delay. An independent bit-parallel verifier performed exhaustive checking on 13 cases with \(n\le13\); the remaining 12 cases were checked on at least 500 deterministic input assignments each. The verifier additionally recomputed **exact gate area and critical-path delay from the entire netlist**, and these agreed with official CSV for all 25. The verifier is not a substitute for a full truth-table proof in the large cases; the instructor evaluator is a separate end-to-end check.

### Generated function tests

The final C++ synthesizer was evaluated on 110 independently generated small structured/random Boolean-function cases: **110/110 official PASS**, and **96/110** met their synthetic target delay. Missing a synthetic target is not a correctness failure, and does not establish mathematical unreachability.

Two large supplementary tests also passed:

- `case_901` (\(n=20,m=8\)): PASS, area 751, delay 78, runtime ~741 ms, target 100.
- `case_902` (\(n=16,m=4\), random high-entropy truth table): PASS, area 108,871, delay 63, runtime ~4,740 ms, target 200.

Their specific resource limits and data are retained in the experimental working directory, but **not bundled into this source-only handoff**, which expects user-provided official cases.

## A negative result: unconstrained order permutations

Adding arbitrary extra variable orders without per-candidate checks caused occasional excessive synthesis time. This was observed and rejected. The final Round 4 introduces periodic time checks and a BDD node cap for these **new** candidates, and falls back to an already completed correct candidate on a timeout. The core Round 3 portions are unchanged, so we do not claim hard real-time bounds for all possible inputs.

## What changed from Round 3 — algorithmic ablation

1. **Global phase choice:** normalize NOT as inverted references, then choose each internal AND/OR gate's output polarity by multiple initializations and coordinate descent on a sharing-aware NOT-area surrogate.
2. **Two-level algebraic identities:** apply exact absorption, complement absorption and factoring to the realized gate DAG.
3. **Composition:** try algebra→phase and phase→algebra as completed candidates, not assume the first order is universally superior.
4. **Bounded order diversity:** additionally screen rotated and influence-ascending variable orders on manageable cases; drop timed-out candidates rather than risking the reference.
5. **Global verification/ranking:** accept a new candidate only if its final full-DAG area/delay ranking improves, preserving the Round 3 result otherwise.

Round 4 remains a heuristic. A useful next step would be a real cut-based mapper with explicit arrival/departure slack and global shared-area accounting. That is **proposed research**, not a method already present in the Round 4 code.

## Limitations and report-writing warnings

- The official numerical scoring formula and hidden-case distribution are not known.
- Runtime figures come from a specific Linux container; do not claim they are measurements on the user's WSL until a local run is uploaded.
- A small improvement (~0.9% total Area) comes at higher search cost and does not prove generalization to unknown cases.
- Some new candidate-time guards are cooperative. Existing Round 3 candidate constructions and several postprocessors are not hard-bounded.
- Mathematical equivalence is proved by Boolean identities and structural induction; target feasibility and achieved Area are empirical.
- Keep the complete `official.csv`, independent checks, source snapshots, hashes and CPU/compiler metadata in the local archived run. Do not merge evidence from different machines without labels.

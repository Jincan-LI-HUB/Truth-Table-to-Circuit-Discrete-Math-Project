# UFUG2106 — Round 4.1 — Runtime Optimization Report

**Research iteration:** Round 4.1 performance tuning, 2026-11-11.  
**Reference:** user-uploaded WSL Round 4 evaluation `20261111_112447_Round4_local_results.zip`.  
**Status:** 25/25 official Stage 1 cases pass all variants; 25/25 satisfy the delay targets.

## 1. Diagnosis based on the local WSL evidence

The uploaded local run measures Area sum **528,910**, median synthesis runtime **127.568 ms**, and maximum runtime **3,535.952 ms**. The largest runtime contributors include cases 024 (3,535.952 ms), 007 (1,553.239 ms), 025 (1,408.648 ms) and 001 (1,013.339 ms).

The unchanged original Round 4 program repeatedly constructs BDD candidates, re-parses the same Truth Table and recomputes variable influence, and also tries many phase-mapping initializations. A targeted profile of `case_024` on the assistant's container allocated about 3.7 seconds to its first eight synthesis candidates and about 2.4 seconds to algebra/phase remapping. The latter comparison is **not** a measurement on the user's WSL machine.

## 2. Algorithmic optimizations

### 2.1 Immutable function-data caching

For every output function \(f_j\), define variable influence:

\[
I_i=\sum_{x\in\{0,1\}^n:\,x_i=0}\sum_{j=1}^{m}
\mathbf 1\!\left[f_j(x)\ne f_j(x\oplus e_i)\right],
\]

where \(e_i\) is the bit vector containing a 1 at position \(i\) and zeros elsewhere.

Influence depends only on the Truth Table, *not* on the gate mapping or choice of initial BDD mapping heuristics. In the strict and balanced variants, Truth Table decoding and influence computation are performed once per executable invocation, and a read-only cached representation is used by subsequent synthesis candidates.

With \(k\) candidates, the former influence-calculation component has complexity \(O(k n m 2^n)\); caching reduces that component to \(O(n m 2^n+k n)\). This does not change the worst-case complexity of constructing the candidate BDDs themselves. The decoded Truth Table still takes \(O(m2^n)\) memory.

### 2.2 Reduced phase-search restarts

The Round 4 polarity mapper chooses phases \(p_v\in\{0,1\}\) and maps a node to a positive or negative representation using legal AND2/OR2/NOT gates. Multiple phase initializations are heuristic alternatives. Reducing the number of restarts does not invalidate Boolean equivalence, but may forego a smaller implementation.

The **strict** variant retains the same complete-Circuit Area and Delay for every released Stage 1 case while substantially reducing the restart count. The **balanced** variant reduces them further, with only a small measured Area increase.

### 2.3 Candidate-space pruning

The **fast** variant skips some redundant or less productive synthesis configurations. A correct baseline candidate is still constructed, and completed candidates are still ranked by target feasibility and Area. This design keeps correctness independent of search breadth, but naturally sacrifices some Area optimality on the benchmark.

## 3. Measured Area–Runtime trade-offs

The four C++ programs were evaluated sequentially on the same analysis container (same test set, evaluator, C++17 \(-O2\)). Figures below are from a *single run per variant*, so they are not statistically robust latency estimates.

| Configuration | Official PASS | Target delay met | Area sum | Median Runtime | Maximum Runtime |
|---|---:|---:|---:|---:|---:|
| Frozen Round 4 | 25/25 | 25/25 | **528,910** | 225.201 ms | 5,840.173 ms |
| Strict-area | 25/25 | 25/25 | **528,910** | 161.757 ms | 4,848.9 ms |
| Balanced | 25/25 | 25/25 | 529,014 | **131.907 ms** | 3,521.7 ms |
| Throughput-first | 25/25 | 25/25 | 530,822 | **82.910 ms** | 3,152.3 ms |

The strict variant preserves the per-case Area and Delay (not just aggregate values) for all 25 benchmark cases. The balanced variant increases aggregate Area by **104 units (0.0197%)**, for an observed median runtime reduction of about **41.4%** in the container. The throughput-first variant increases Area by **1,912 units (0.3615%)**, for an observed median runtime reduction of about **63.2%** in the container.

These are **descriptive candidate-design trade-offs**, not confirmed changes in instructor scores or guaranteed WSL speedups.

## 4. Extra verification

Each accelerated variant passed all **110/110** additional independent small random/structured Truth Tables, and **96/110** of their arbitrary generated delay targets. Each passed both stress benchmarks, including an \(n=20,m=8\) case with a 128 MiB cap and an \(n=16,m=4\) high-entropy Truth Table case. The instructor evaluator passed every published case for each variant.

The release script also runs the project-independent bit-parallel checker on each of the 25 saved output Netlists, exhaustively on \(n\le13\) and with deterministic samples on larger cases. The latter is additional evidence rather than an exhaustive proof of large-function equivalence.

## 5. Recommendations

**Default experiment:** Balanced. It sacrifices only 104 aggregate Area units on the published cases and nearly halves the median measured synthesis time in this container. If minimizing Area is prioritized, choose strict-area; if synthesis CPU time dominates grading, compare the throughput-first variant.

Before adopting a release, evaluate each variant on the user's WSL machine using the included `run_round4_1_local.sh` script and compare directly with the original Round 4 local CSV. Store the resulting stage notes under the usual `local_runs/YYYYMMDD_HHMMSS_Round4.1/report_ready/` directory.

## 6. Remaining bottlenecks and next research

- Share the **constructed BDD DAG by variable order**, rather than just the input and influence arrays. The same ordering is reconstructed several times under different gate-mapping heuristics.
- Replace whole-Netlist string parsing and repeated full-graph scoring with incremental gate and arrival-cost updates.
- Use a marginal-value stopping criterion for phase search, or a Pareto queue of candidates, rather than a fixed pass count.
- Add explicit interruption in every legacy candidate, not just the outer candidate loop, to strengthen hidden-case runtime guarantees.
- Repeat tests with controlled CPU load, alternate generated random functions, and more stringent RAM/runtime limits.

The frozen original Round 4 sources remain unchanged. This is a performance-research candidate, not a claim of final submission or global optimality.

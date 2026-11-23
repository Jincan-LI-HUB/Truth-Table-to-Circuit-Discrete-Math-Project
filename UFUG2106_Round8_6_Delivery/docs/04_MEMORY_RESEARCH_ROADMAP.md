# Memory Optimization: Separating Genuine Headroom from Evaluator Accounting

## 1. Two different questions

The positive RAM-limit discrepancy reproduced in Round 8.2.1 occurred even for a tiny C program with current-image VmHWM near 1.3 MiB; some official evaluator runs classified it as MEMORY_LIMIT at 9,000 KiB. The upstream reported `ru_maxrss` could reflect history from a parent process before `execve`. This is a **hypothesis** supported by controlled measurements, not source-level proof of evaluator behavior. A custom checker may assist research but cannot replace the course's evaluator.

Separately, the actual synthesizer has significant allocation costs on complex truth tables and candidate DAGs. The Round 8.2.1 streaming/low-memory fallback already reduced direct input cases substantially, yet larger Stage 2 cases still use many MiB. These are real opportunities for algorithm engineering.

## 2. Genuine low-risk optimization opportunities

- Replace per-candidate duplicated immutable truth-table vectors with shared read-only representations or bit-packed arrays; distinguish row-major and output-major access patterns.
- Profile the BDD `orig(N)/cur(N)` scratch buffers: allocate only when the candidate is admitted, reuse across mutually exclusive candidate orders, and release after consumption.
- Use compact node IDs and packed op descriptors when value ranges allow. Audit `std::unordered_map` bucket overhead vs open-addressed alternatives, including allocator fragmentation.
- Build cut caches lazily, with explicit high-water marks; limit the *number of simultaneously resident* alternative graphs, not only total candidates explored.
- For completely independent candidate branches, destroy the previous branch state as soon as exact global metrics and a serialized incumbent have been recorded.

These can lower RSS with no intended change in final circuit semantics, but may affect runtime due to packing, rehashing, and cache behavior.

## 3. Quality-sensitive memory policies

- Cap BDD and cut node counts under RAM budgets, then try compressed-support/affine/factored fallback. Lower RAM can limit search diversity and enlarge final Area or Delay.
- Maintain a bounded Pareto archive rather than all candidate DAGs, considering Area, Delay, runtime and estimated allocation cost. Frontier pruning must preserve a valid incumbent.
- Use memory-admission preflight and actual RSS instrumentation. Static bytes estimates can be conservative but cannot guarantee exact platform RSS.

## 4. Proposed experiments for a dedicated memory round

Separate benchmark axes: peak **current-image** RSS, maximum transient allocation, wall-clock runtime, final Area, final Delay, verified equivalence, and official evaluator result. For frozen inputs and seeds, compare unchanged full-memory baseline against cache sharing, buffer reuse, bit-packing, and node-pool variants. Repeat each test under multiple RAM caps; do not modify official test limits in benchmark reporting. Use the same bounded root-work budget for fair comparisons. Distinguish `ru_maxrss`, `VmHWM`, `VmRSS` and any cgroup memory counter. Public test cases are developmental; freeze a fresh workload set before scoring.

## 5. Round ordering

Round 8.4 is a *search-scheduling* research experiment. After its official WSL feedback, conduct a separate **Memory Profiling/Allocation** round rather than mixing memory architectural changes into the root-ranking ablation. Keep the parent low-memory fallback intact and leave Issue #2 open until the team/instructor clarifies the positive-limit evaluator behavior.

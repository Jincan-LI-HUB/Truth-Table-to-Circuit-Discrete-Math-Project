# Round 4.1 Runtime Analysis — Mathematical and Experimental Record

## 1. Objective and constraints

Each output netlist `C` is functionally equivalent to the submitted truth table. Gate implementation must satisfy the official netlist grammar. We measure (A(C),D(C),T_alg), where A is gate area, D critical-path gate delay, and T_alg synthesis runtime.

The resource-quality problem is a constrained tri-objective problem: minimize area subject to correctness, delay-target feasibility (when achievable), and time/memory budgets. More search does not always yield sufficient incremental benefit.

## 2. Immutable Truth Table and influence cache

For output functions f_j, the influence measure used to rank variables is

I_i = sum_{x: x_i=0} sum_j [f_j(x) != f_j(x with the i-th bit flipped)].

For a fixed input file this is determined entirely by the truth table, independently of BDD mapping configuration or Boolean gate costs. Recomputing I_i on every candidate is redundant. Likewise, the same table need not be lexically decoded multiple times. The optimization stores its decoded bits and I_i once, then provides read-only references to subsequent candidate synthesizers. This is a **semantic-preserving memoization**: if data and variable order are unchanged, BDD construction receives identical inputs.

An input with n binary variables and m output bits has 2^n rows. Naively recomputing influence over k candidate runs costs O(k n m 2^n) Boolean comparisons. Caching reduces this component to O(n m 2^n) plus O(k n) for reading precomputed influence. This bound describes influence calculation only, not all of synthesis. The table memory is O(m 2^n).

## 3. Phase-mapping search budget

The original Round 4 applies several alternative initial node phases to a shared DAG, performs coordinate-descent phase improvement, reconstructs legal gates, evaluates candidate area/delay, and retains the better completed circuit. Multiple initial phases can lead to similar or identical solutions. Reducing the number of initializations lowers computational work; the transformations are still Boolean-equivalent, but skipping variants may forego a smaller implementation.

The strict variant retains enough phase alternatives to reproduce the same area and delay for every published case. The balanced variant reduces phase alternatives further, losing only 104 units of area on the 25 published cases.

## 4. Optional candidate pruning

The fast variant skips some distinct synthesis configurations, always retaining a valid baseline candidate. The optimization ranking remains based on complete circuits, so no invalid mathematical inference is introduced. The Area loss is measurable: +1,912 units on the published cases. This should be interpreted as an empirical area/time Pareto point, not a guarantee for other truth tables.

## 5. Correctness rationale

Each candidate derives from Boolean identities: Shannon expansion, De Morgan, absorption, distributivity, and structurally correct DAG sharing. Candidate set reduction does not change their equivalence; it changes which valid netlist is selected. Cached influence and Truth Table arrays are immutable after loading. All candidates are finally serialized with predecessor-only gate IDs, followed by independent and official validation.

## 6. Key profiling evidence

For case_024 in the original measured container run, eight BDD candidates cost approximately 3.7s combined, while repeated algebra/phase remapping added roughly 2.4s. Multiple BDD orders were substantially worse in Area than an existing candidate. This motivates more selective candidate search and fewer phase starts; times are instrumented **measurements on the analysis container**, not the user's WSL.

## 7. Quantified tradeoffs

See `results/*_container.csv` for the full 25-row measurements, `results/*_generated_110.csv` for held-out small tests, and `results/*_stress_*.csv` for high-dimensional resource checks.

The user-uploaded Round 4 baseline yielded median runtime 127.568 ms on their WSL, substantially different from the container median 225.201 ms. **Do not convert container speedup percentages into guaranteed WSL speedups.** Run all variants on the same WSL machine and compare the new outputs to the frozen local Round 4 measurements.

## 8. Further work

- Structural memoization of variable-order-specific BDDs (separate BDD construction from mapping).
- Incremental arrival and area accounting to avoid reparsing the whole netlist for every candidate.
- Early termination of phase search using marginal benefit rather than a fixed variant count.
- Tight timeout guards *inside* every candidate synthesis; current checks are incomplete for legacy calls.
- Larger out-of-sample stress tests, resource caps and two-seed timing repetitions.

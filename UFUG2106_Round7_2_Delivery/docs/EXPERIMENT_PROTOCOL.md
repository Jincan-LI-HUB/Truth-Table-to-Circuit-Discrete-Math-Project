# Round 7.2 — Reproducible Experiment Protocol

## 1. Two-stage comparison is mandatory

Each official experiment uses both `data/stage1/` (25 cases) and `data/stage2/` (25 cases), under **the same evaluator version and host machine**. Runs alternate comparator order to reduce systematic biases from warm-up, OS scheduling, and temporary CPU load. Only paired results with the same case are compared as runtime ratios.

**Default:** 2 repetitions; `r51`, `r71_guard`, `r72_shortlist`, `r72_guard`, `r72_nocancel` (five versions/conditions, twice on each stage; 20 official CSVs). On *each* run and stage, every variant is evaluated by the teacher-provided `evaluator PROGRAM BENCHMARK_FOLDER --report CSV` interface. The evaluator is copied to a Linux temporary directory to avoid WSL Windows-mount execution permission issues.

| Label | Binary | Environment | Hypothesis |
|---|---|---|---|
| `r51` | frozen Round 5.1 | no override | earlier 50-case reference |
| `r71_guard` | frozen Round 7.1 | default | controlled previous-release comparator |
| `r72_shortlist` | Round 7.2 | `UFUG_R72_POLICY=shortlist` | main quality recovery and time safety |
| `r72_guard` | Round 7.2 | `UFUG_R72_POLICY=guard` | source instrumentation without added candidate |
| `r72_nocancel` | Round 7.2 | `UFUG_R72_POLICY=shortlist_nocancel` | test value of deadline cooperation |

The `r72_nocancel` research ablation might fail due to timeout; that is not by itself a failure of the *default* release. If the ablation never reaches its deadline, an identical output is a **null/inconclusive** result, not proof of timeout mechanism efficacy.

## 2. Official evaluator metrics

For every case and run save: status, area, delay, runtime_ms, target_met, evaluator logs and source/program/evaluator SHA-256. Additional input header fields — gate costs, target delay, runtime limit — define a case's feasibility and relevant quality interpretation. Although failure due to time or RAM is not always equivalent to incorrect Boolean semantics, every such result counts as `FAIL` for the feasibility gate.

The report includes:

- PASS count, number of target-met PASS cases, complete Area Sum *only if 25/25 PASS*;
- per-case Area and Delay deltas (only on jointly passing cases);
- geometric mean of Area and runtime ratios (only on jointly passing cases);
- explicit lists of new failures and recovered failures;
- median and approximate P95 runtime of PASS cases;
- full execution logs and direct-case profiles, with clearly separated scopes.

**No zero-area imputation for FAIL cases. No claim that the Area Sum is the official score.**

### Two independent gates

- `release_gate_public_50_pass_target`: Round 7.2 default gets 25/25 functional PASS and target met on **both stages in every measured repetition**.
- `quality_gate_vs_round71`: no jointly passed case has **any Area or Delay increase** versus Round 7.1 Guard in any repetition. This is a conservative experiment gate, not a theorem and not the course grading formula.

The script reports both gates separately. If either fails, it exits nonzero **after preserving the CSVs** and the shell exit trap creates a ZIP.

## 3. Low-level verification

Before the official evaluator runs:

1. Verify the frozen R5.1 Git blob (`68ec9f54b27081641ac10358f81eef260acfcbdb`) and deterministically regenerate the R7.2 C++ source.
2. Compile in C++17 `-O2 -DNDEBUG` and compare the source SHA with `SOURCE_MANIFEST.json`.
3. Verify the Round 7 Cover kernels against all 4 A/B settings over 10,656 independent comparisons.
4. Generate and exhaustively verify the two *structural probe* netlists (`stage1/case_020`, `stage2/case_016`). This preflight is deliberately small and should **not** substitute for the official full evaluator.

The independent verifier is bit-parallel. It exhaustively checks cases of \(n\le13\), samples higher-n cases with a fixed seed, and recalculates weighted area/delay independently from the netlist.

## 4. Direct profiling is NOT official timing

After paired official evaluation, the script runs 3 repetitions of each structural probe and variant outside the 100ms evaluator limit. It records:

- actual netlist source and SHA-256;
- full `R71_TRACE` / `R72_TRACE` candidate records;
- elapsed wall-clock for the process and independent functional verification status;
- whether the shortlisted legacy candidate improved the incumbent;
- whether the candidate was rejected, cancelled or not admitted.

Logging changes execution time. Do not compare these direct wall-clock numbers with the evaluator's wall-clock measurements as if interchangeable.

## 5. Regressions and trade-off presentation

For each public case, let \(C_{71,i}\) be the frozen R7.1 guarded result and \(C_{72,i}\) be the R7.2 shortlisted result. On jointly passing cases calculate

\[ \Delta A_i=A(C_{72,i})-A(C_{71,i}),\quad \Delta D_i=D(C_{72,i})-D(C_{71,i}).\]

Then compute the geometric mean of runtime ratios, and present a casewise table for all regressions/improvements. Record *how many* cases improved, were unchanged, regressed or failed. A case can be incomparable (e.g. area lower but delay higher); in that situation report both measurements and do not describe it simply as 'better'.

Since Stage 2 limits vary from 100ms to 100,000ms, runtime slack should be normalized to declared limit, not judged by raw milliseconds alone. Different cases also use different gate area/delay weights; therefore comparing their absolute area without normalization can be misleading.

## 6. Proof obligations and research honesty

- **Functional correctness:** retain semantics-preserving components and verify every public case with instructor evaluator; independent checker adds redundancy.
- **Nondegradation:** additional candidate acceptance is strictly better according to a preexisting local rank, but final global postprocessing is nonlinear; only paired regression results justify final quality claims.
- **Runtime safety:** cooperative checkpoints, conservative admission and 40% nominal reserve reduce risk. They **do not prove** worst-case deadline adherence.
- **Generality:** 50 public cases remain a development set. Supplement with seeded holdouts or hidden evaluation when available. Do not add if/else case-ID conditions.
- **Reproducibility:** source checksum, evaluator checksum, compiler flags and case-by-case CSVs are preserved. Historical R7.1 evidence remains separate.

## 7. Feedback handling

Run from WSL:

```bash
bash UFUG2106_Round7_2_Delivery/run_round72.sh
```

The program **always** emits `feedback/Round7.2_Feedback_<timestamp>.zip`, including on failed tests or evaluator errors. Upload that single archive. The ZIP includes `feedback_metadata.json`, code snapshot and source manifest, full official run logs, `summary.json`, casewise CSV, diagnostic nets/traces and research documentation; it excludes raw truth tables, evaluator executable and compiled binaries.

If feedback was generated but no official run took place (e.g. compilation failed), the metadata's `results_available` is false; don't assume an absent CSV means PASS.

# Proposed Stage 2 Roadmap after Round 8.6 (22 Nov 2026)

**Current fixed facts:** TA reports final performance based on running submitted Stage2 source on 50 public plus 50 hidden inputs; neither set imposes `ram_limit`. Server has 48 GiB *total* memory. Report experiments explain the method but do not directly count toward performance. The unknown hidden distribution makes 50 repeatedly optimized public inputs insufficient validation.

## Round 8.6 — Causal ablation (current)

Separate root work quota vs remaining wall time; reverse SOP/Shannon allocation; test against R85 frozen candidate in the exact same evaluator session. Do not commit a policy purely because of a single aggregate Area minimum. Examine casewise gain/loss, delay effects, run-to-run variations, and outlier risk.

**Decision gate:** Freeze a promising candidate only if it passes official Stage1/2, improves across meaningful case strata or provides a clear and safe trade-off, and its gains survive reversed-order reruns. Otherwise record the negative result and keep R85 as baseline.

## Round 8.7 — Robustness and out-of-sample evaluation

- Create *fresh, seeded and provenance-controlled* test families not tuned against during candidate design: random structured DAGs; high-fanout shared subcircuits; sparse and dense outputs; parity/affine; mux-like functions; n=20 streaming stress; varied area and delay weights; very short runtime limits.
- Introduce resource diagnostics for time (wall, p95/p99, deadlines), graph size, and peak RSS; use only as an engineering metric, not a positive-RAM target.
- Evaluate stable parent and a **small preregistered candidate set** on the same fresh cases; avoid selecting hundreds of tuning configurations based on one fixed holdout.
- Record failure rate, delay misses, score proxies, worst-case regression and cross-run reproducibility, not only mean Area.

**Decision gate:** Choose a robust frontier candidate rather than a maximum-public-score overfit.

## Round 8.8 — Team integration and submission freeze

- Integrate with teammate's actual Stage2 source. Implement or explicitly reject Issue#2's *integrated BDD budget refund* on the actual merged solver; independently replay original unmodified Stage2 cases.
- Stop editing historical source snapshots. Make the final submission self-contained and exact: source + headers, single known entrypoint, no local absolute paths, clean Ubuntu/WSL compile.
- Run all public cases twice with the genuine evaluator, plus the fresh holdouts, with source and binary SHA-256 manifests. Verify no accidental old environment flags and that every netlist is formally valid.
- Freeze a single default objective and operating policy. Write reproducible report with mathematical motivation, negative results, and measured trade-offs.

**Stop criterion:** Avoid new risky Boolean rewrites once extra quality gain is small relative to hidden-case correctness and runtime risk.

## Optional Round 8.9 — Only if evidence supports it

Target one demonstrable gap (e.g. predictable time-budget abort for short cases, or an avoidable memory allocation that increases elapsed runtime), using a focused, reversible patch. Do not keep expanding broad ablations indefinitely.

## Memory priority

Maintain independent RSS tracking and remove proven redundant buffers if it improves memory without hurting correctness/Area/Delay. A 9,000-KiB positive-limit issue is not a grading blocker under the latest TA announcement. Avoid expensive memory-specific trade-offs unless actual timeouts, allocations, or resource failures emerge.

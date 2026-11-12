# UFUG2106 — Logic Synthesis, Round 3 Research Prototype

**Status (2026-11-11):** 25/25 PASS and 25/25 Target Delay Met on the published Stage 1 cases, with aggregate reported Area **533,705**. This is a reproducible experimental result, **not** a proof of optimality or a claimed official grade.

## Files

- `src/synth.cpp` — latest single-threaded C++17 synthesizer, retaining earlier non-complemented BDD candidates for non-regression (best measured Area).
- `src/synth_core.cpp` — smaller core-only implementation (Area sum 543,209), without the legacy fallback.
- `src/synth_complement.cpp` — complemented-edge BDD ablation.
- `src/synth_affine.cpp` — affine-function / XOR recognition ablation.
- `src/synth_balance.cpp` — associative AND/OR cone balancing ablation.
- `src/synth_area_recover.cpp` — timing-slack-aware De Morgan area recovery ablation.
- `src/synth_implication.cpp` — cofactor-implication experiment; **not retained** because its aggregate Area regressed.
- `results/` — retained official Evaluator CSVs, a clean rebuilt run, per-case comparison, and an independent verification record.
- `tools/verify_netlist.py` — independently parses/simulates a Netlist, checks Boolean outputs, syntax, Area and Delay. Exhaustive for `n<=13`, deterministic sampling for larger n.
- `docs/RESEARCH_REPORT.md` — method, proofs, experiments, limitations and future experiments.
- `verification_outputs/` — actual Netlists emitted during the clean-build run; can be checked with the source case files.

**Not included:** the instructor's 25 original input files or the evaluator executable. Use your authorized course copies.

## Build

```bash
make
./synth path/to/case_001.txt /tmp/case_001.output.txt
```

## Evaluate

```bash
./evaluator ./synth ./stage1 --report stage1_round3.csv
```

The Evaluator's `status=PASS` means correctness/format/resource constraints passed; `target_met=yes` is a distinct timing indicator. The score weights are not available in the provided materials.

## Independent check

```bash
python3 tools/verify_netlist.py path/to/case_017.txt /tmp/case_017.output.txt
```

For `n>13`, independent simulation is a deterministic **sample**, not an exhaustive proof. The official Evaluator checks the published cases independently. All 25 Netlists from the retained clean-build run were checked; 13 cases were exhaustively checked by this separate checker and 12 sampled.

## Results summary

See `results/ablation_summary.csv`. The core-only run is `results/fresh_build.csv`; the immediately preceding run is `results/search_all.csv`. Both report all 25 PASS and all 25 target delays met. Per-case outputs may vary if resource-dependent candidate search terminates at different points on different machines.

## Academic provenance

This is an **AI-assisted research prototype** developed using prior explorations of Shannon expansion, ROBDDs, implicant cover, and the ideas learned from [zdu881/UFUG2106-Project](https://github.com/zdu881/UFUG2106-Project). In particular, two-level Shannon expansion and BDD improvements were among the public technical reference points. The timing-slack-aware rewriting and experiments in this round are independently assembled here. Student ownership, proper attribution, actual team contributions and live Q&A preparation are separate responsibilities; please review and understand the code before considering submission.

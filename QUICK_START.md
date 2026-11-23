# Quick Start — Truth Table to Circuit

This guide reproduces the **final Stage 2 R10.0 synthesizer** using the existing repository layout. The historical Round 5.1 Stage 1 research implementation remains available and is covered below.

## Requirements

- Linux or WSL2 (recommended); `g++` with C++17 support; GNU `make`; Python 3.
- For the official released-benchmark evaluation: the **course-provided** `evaluator` at repository root and the `data/stage1/`, `data/stage2/` folders.
- For numerical checks/figure reproduction: Python packages `pandas`, `matplotlib` (install in a virtual environment if needed).
- For report compilation: `pdflatex`, `bibtex`, IEEEtran and the packages used by `main.tex`. The compiled `.bbl` is **not committed** because `.gitignore` excludes build intermediates.

All paths below are relative to the **repository root** unless otherwise stated. Commands are intended to be copied into a Bash shell (including WSL Ubuntu).

## 1. Clone and build the final synthesizer

```bash
git clone https://github.com/Jincan-LI-HUB/Truth-Table-to-Circuit-Discrete-Math-Project.git
cd Truth-Table-to-Circuit-Discrete-Math-Project

# Build only the exact standalone Stage 2 submission source and its headers.
make -C UFUG2106_Round10_0_Delivery build/submission_synth -j2
```

This compiles `UFUG2106_Round10_0_Delivery/submission/synth.cpp`, with headers placed alongside it, into `UFUG2106_Round10_0_Delivery/build/submission_synth`.

**Note:** the original `UFUG2106_Round10_0_Delivery/README.md` calls this an independent candidate freeze, reflecting the historical state when that README was written. The project's Formal Report identifies R10.0 as the selected **independent research-final Stage 2 candidate**; this is not evidence of a teammate-integrated final submission or hidden-test result.

## 2. Synthesize and verify one input

```bash
SOLVER="$(realpath UFUG2106_Round10_0_Delivery/build/submission_synth)"
CASE="$(realpath data/stage2/case_001.txt)"
NET="/tmp/ufug2106_case001.net"

"$SOLVER" "$CASE" "$NET"

# Independent all-assignments netlist check against the truth table.
make -C UFUG2106_Round10_0_Delivery build/verify_exhaustive -j2
UFUG2106_Round10_0_Delivery/build/verify_exhaustive "$CASE" "$NET"
```

Expected verifier behavior: a `PASS exact_assignments=... area=... delay=... target=...` summary. The verifier checks Boolean equivalence for every truth-table assignment; passing that check **alone** does not certify the external evaluator's runtime/memory requirements.

The output is a gate netlist, **not** a rendered circuit image. The R10.0 default Repeat SOP pass is conditional and may not run on a short-budget case.

## 3. Run the official released-case evaluator

The course evaluator is a platform-dependent executable. On Windows-mounted WSL file systems, it may lack executable permissions; copy it to the Linux temporary directory to avoid altering the tracked original:

```bash
cp evaluator /tmp/ufug2106_evaluator
chmod +x /tmp/ufug2106_evaluator

EVAL=/tmp/ufug2106_evaluator
SOLVER="$(realpath UFUG2106_Round10_0_Delivery/build/submission_synth)"

"$EVAL" "$SOLVER" "$(realpath data/stage1)" \
  --report /tmp/r100_stage1.csv
"$EVAL" "$SOLVER" "$(realpath data/stage2)" \
  --report /tmp/r100_stage2.csv
```

The documented basic interface is `evaluator PROGRAM BENCHMARK_FOLDER`. The archived evaluator accepts the optional `--report FILE` argument; omit it if you have a different version lacking that option.

Each released bank contains 25 cases. The CSV output reports case-specific PASS, target attainment, area, delay and synthesis runtime. For the archived matched three-solver comparison and source provenance, refer to [`Stage 2 Formal Report/data/matched_case_metrics.csv`](Stage%202%20Formal%20Report/data/matched_case_metrics.csv) and the report's evaluation section.

### Full R10.0 historical evaluation and ablations

The original delivery provides a full verification-and-comparison runner:

```bash
# Local compilation, cold-build checks, independent fixtures (no official scores):
bash UFUG2106_Round10_0_Delivery/run_round100.sh --local-only

# Quicker public case comparison (four configurations, one repeat):
bash UFUG2106_Round10_0_Delivery/run_round100.sh --quick

# Full historical experiment (six configurations, two repeats, both banks):
bash UFUG2106_Round10_0_Delivery/run_round100.sh
```

The full experiment runs **600 policy-case evaluations**, takes substantially more work than a single solver check, and generates local `results/` and `feedback/` files. The `.gitignore` omits generated binaries, LaTeX intermediates, and ZIP/RAR feedback archives; it does **not** blanket-ignore tracked/archived CSVs and research source.

## 4. Build the earlier Stage 1 research freeze

The independent **Round 5.1** line is retained for historical comparison and study:

```bash
make -C UFUG2106_Round5.1_Delivery -j1

./UFUG2106_Round5.1_Delivery/build/synth_round51 \
  data/stage1/case_001.txt /tmp/round51_case001.net

python3 UFUG2106_Round5.1_Delivery/tools/verify_netlist.py \
  data/stage1/case_001.txt /tmp/round51_case001.net
```

Round 5.1 was an **independent research baseline**, not the Stage 1 code formally submitted by Zeyun Du. For source lineage, archived evaluations and all intermediate experiments, consult the Stage 1 Technical Report and the unified Research Trial Log.

## 5. Rebuild and verify the Formal Report

```bash
cd "Stage 2 Formal Report"

# Recompute the casewise appendix and verify the already archived CSV metrics.
python3 build_casewise.py
python3 verify.py

# Rebuild vector statistical and algorithm figures (requires matplotlib/pandas).
python3 figures.py

# Regenerate the bibliography and PDF from tracked TeX/BibTeX sources.
pdflatex -interaction=nonstopmode -halt-on-error main.tex
bibtex main
pdflatex -interaction=nonstopmode -halt-on-error main.tex
pdflatex -interaction=nonstopmode -halt-on-error main.tex
```

Because the repository does not track `.bbl`, a clean clone should run `bibtex main` after the first `pdflatex` pass. This does not alter the experimental data.

PDFs available without recompiling:

- [**Formal Report**](Stage%202%20Formal%20Report/main.pdf): final R10.0 algorithm and Stage 1/Stage 2 comparison.
- [**Unified Research Trial Log**](Stage%202%20Formal%20Report/Research_Trial_Log/UFUG2106_Stage2_Research_Trial_Log_v3.pdf): detailed Stage 1–Stage 2 decisions, mathematics, controls, and cross-version data.
- [**Stage 1 Technical Report**](UFUG2106_Stage1_Writing_v1_0/technical_report/main.pdf): earlier rigorous treatment of representation, mapping and optimization.

## 6. Interpreting results responsibly

- `PASS` means the evaluator accepted the generated solution; meeting a preferred delay target is a separate field.
- Circuit delay and synthesis runtime are different quantities.
- Area totals are **weighted gate counts**, not operation counts or universally comparable hardware costs across differently priced cases.
- Published values in the project documents refer to the cited public-case runs. They may differ slightly from a fresh run because some search decisions depend on elapsed time.
- The final 50-case public evaluation compares **Z1 (submitted Stage 1)** against **R10.0 (research-frozen Stage 2)**; J51 is a distinct Stage 1 research baseline, not a substitute for Z1.

For navigation, return to the [repository README](README.md).


## 7. Access the full research history

- [Stage 1 independent R1–R6.1 technical report](UFUG2106_Stage1_Writing_v1_0/technical_report/main.pdf) and [original trial log](UFUG2106_Stage1_Writing_v1_0/trial_log_record/main.pdf).
- [Complete Stage 1 + Stage 2 Trial Log](Stage%202%20Formal%20Report/Research_Trial_Log/UFUG2106_Stage2_Research_Trial_Log_v3.pdf) and [casewise/variant CSV index](Stage%202%20Formal%20Report/Research_Trial_Log/data/stage2_all_variant_index.csv).
- [R8.6 controlled root/time-quota experiment](UFUG2106_Round8_6_Delivery/README.md) and [R10.1 final parameter-ablation decision](UFUG2106_Round10_1_Delivery/docs/02_RELEASE_DECISION.md).

The merged Trial Log PDF is available immediately. To regenerate its LaTeX from source, the full `Research_Trial_Log` editable bundle must contain `shared/palette.tex`, `tex/stage1_body.tex`, `tex/stage2_body.tex`, referenced figure PDFs, and the merge/plot scripts. Those source files may need to be restored from the complete research-log archive if absent in an older clone; do not mistake an existing PDF for proof of source-level reproducibility.

## 8. Troubleshooting

| Symptom | Action |
|---|---|
| `g++` or `make` not found | Install a C++17-capable build toolchain in Linux/WSL |
| Course evaluator reports `Permission denied` | Copy the tracked binary into `/tmp` and run `chmod +x` on the copy |
| Evaluator command does not recognize `--report` | Omit the optional flag if using a different evaluator version |
| Output passes the exhaustive verifier but fails the external evaluator | Inspect output validity, case-specific delay, resource limits and evaluator diagnostics separately |
| Fresh report build reports `IEEEtran.bst` missing | Install the TeX IEEE/BibTeX style packages and rerun the documented sequence |
| Repeated metrics differ slightly | Respect wall-clock sensitivity of bounded search; use same-run paired comparisons for causal claims |

Return to the [main README](README.md) for research background and the full repository map.

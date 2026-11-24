# Quick Start — Truth Table to Circuit

**Integrated Final** is the Stage 2 team solver planned for submission. Use Linux or WSL2 with Git, a C++17 GCC toolchain, GNU Make, Python 3 and NumPy. The course evaluator is a Linux x86-64 executable. Clone on the Linux filesystem when using WSL.

## 1. Clone, build and verify Integrated Final

```bash
git clone --branch main --config core.autocrlf=false \
  https://github.com/Jincan-LI-HUB/Truth-Table-to-Circuit-Discrete-Math-Project.git
cd Truth-Table-to-Circuit-Discrete-Math-Project

team="$PWD/Final_Submission_by_Zeyun_DU"
out=$(mktemp -d)
make -C "$team" stage2
"$team/build/synth_stage2" data/stage2/case_001.txt "$out/case_001.net"
python3 "$team/tools/check_circuit.py" data/stage2/case_001.txt "$out/case_001.net"
```

The checker reports exact truth-table equivalence, area, circuit delay and target attainment. Expect `"valid": true` and `"target_met": true` for this input. The clone option preserves the byte identities used by the evidence verifier.

## 2. Evaluate both released banks with the course evaluator

Continue from the repository root in the same shell.

```bash
install -m755 evaluator "$out/evaluator"
for bank in stage1 stage2; do
  "$out/evaluator" "$team/build/synth_stage2" "$PWD/data/$bank" \
    --report "$out/$bank.csv" --save-outputs "$out/$bank-netlists"
  python3 "$team/tools/verify_all.py" "$PWD/data/$bank" "$out/$bank-netlists" \
    "$out/$bank.csv" "$out/$bank-independent.json"
done
printf 'Reports and netlists are in %s\n' "$out"
```

Each bank contains 25 inputs. The evaluator CSV records functional status, whether the delay target was met, weighted area, circuit delay and synthesis runtime. The independent replay checks the emitted netlists against every assignment and reconciles the circuit metrics. Run the two commands for each bank together, since the replay needs that bank's CSV and saved netlists. Use the evaluator bundled with the repository for the flags above. The archive records the source ZIP build and the four-method matched experiment. [Solver guide](Final_Submission_by_Zeyun_DU/README.md) · [Integration audit](Final_Submission_by_Zeyun_DU/integration/AUDIT.md)

## Historical solver workflows

### R10.0 independent Stage 2 freeze

```bash
make -C UFUG2106_Round10_0_Delivery -j2 build/submission_synth build/verify_exhaustive
history=$(mktemp -d)
UFUG2106_Round10_0_Delivery/build/submission_synth \
  data/stage2/case_001.txt "$history/r100_case_001.net"
UFUG2106_Round10_0_Delivery/build/verify_exhaustive \
  data/stage2/case_001.txt "$history/r100_case_001.net"
```

To run the course evaluator against this freeze, use the absolute path to `UFUG2106_Round10_0_Delivery/build/submission_synth` as its program argument. Keep the output directory separate from the Integrated Final run. The historical [R10.0 runner](UFUG2106_Round10_0_Delivery/run_round100.sh) supports `--local-only`, `--quick` and the full controlled experiment. The full default runs 600 policy-case evaluations.

### J51 independent Stage 1 freeze

```bash
make -C UFUG2106_Round5.1_Delivery -j1
history=$(mktemp -d)
UFUG2106_Round5.1_Delivery/build/synth_round51 \
  data/stage1/case_001.txt "$history/j51_case_001.net"
python3 UFUG2106_Round5.1_Delivery/tools/verify_netlist.py \
  data/stage1/case_001.txt "$history/j51_case_001.net"
```

The J51 verifier reports whether it checked every assignment or selected a sample. The matched research evidence uses the [verified J51 freeze](Stage1_Freeze_Round5.1_Verified/) and identifies Z1 as Zeyun Du's submitted Stage 1 comparator. [J51 delivery guide](UFUG2106_Round5.1_Delivery/README.md)

## Rebuild the reports and check the archives

Install Python packages `numpy`, `pandas` and `matplotlib` for the plots and numerical checks. Use pdfLaTeX, BibTeX, IEEEtran and the LaTeX packages in the two masters. The optional historical reassembly uses PyMuPDF 1.26.4 or later.

```bash
cd "Stage 2 Formal Report"
python3 build_casewise.py
python3 verify.py
python3 ../Final_Submission_by_Zeyun_DU/integration/verify_evidence.py
python3 build_phase_c_figures.py
pdflatex -interaction=nonstopmode -halt-on-error main.tex
bibtex main
pdflatex -interaction=nonstopmode -halt-on-error main.tex
pdflatex -interaction=nonstopmode -halt-on-error main.tex

cd Research_Trial_Log
python3 scripts/verify_evidence.py
cd tex
latexmk -pdf -interaction=nonstopmode -halt-on-error main.tex
cp main.pdf ../UFUG2106_Stage2_Research_Trial_Log_v3.pdf
```

Without `latexmk`, run pdfLaTeX in the Trial Log's `tex/` directory until the contents and labels stabilize. The Trial Log uses a bibliography embedded in its master. The Formal Report builds its bibliography from `references.bib`. For repeat 2 figures, pass `--repeat 2 --out DIR` to `build_phase_c_figures.py`.

- [Formal Report PDF](Stage%202%20Formal%20Report/main.pdf) and [build guide](Stage%202%20Formal%20Report/README.md)
- [Unified Research Trial Log PDF](Stage%202%20Formal%20Report/Research_Trial_Log/UFUG2106_Stage2_Research_Trial_Log_v3.pdf) and [historical reassembly guide](Stage%202%20Formal%20Report/Research_Trial_Log/README.md)
- [Stage 1 Technical Report](UFUG2106_Stage1_Writing_v1_0/technical_report/main.pdf) and [original Trial Log](UFUG2106_Stage1_Writing_v1_0/trial_log_record/main.pdf)

Published results come from the archived runs. Search depends on elapsed time, so a fresh run can produce a different circuit. Course submission status, official scores and hidden-case performance remain unverified.

[Repository overview](README.md)

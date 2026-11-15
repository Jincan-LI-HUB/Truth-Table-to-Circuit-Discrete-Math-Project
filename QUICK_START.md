# Quick Start — Truth Table to Circuit

This guide uses the **existing repository and its original implementations**. No separate release repository or code rewrite is required.

**Recommended Stage 1 implementation: Round 5.1** (`UFUG2106_Round5.1_Delivery`). Round 5 is its direct comparison baseline; Rounds 1–4.1 and 6.0–6.1 document the wider development history. For methodology and all archived metrics, see the [main README](README.md) and the [Technical Report](UFUG2106_Stage1_Writing_v1_0/technical_report/main.pdf).

## 1. Run the recommended version (Round 5.1)

**Requirements:** Linux / WSL2, a C++17 compiler (`g++`), `make`, and Python 3 for optional independent verification. All commands below start at the **repository root**.

```bash
# Build the frozen research implementation.
make -C UFUG2106_Round5.1_Delivery -j1

# Run one truth table and write a gate netlist.
./UFUG2106_Round5.1_Delivery/build/synth_round51 \
  data/stage1/case_001.txt /tmp/round51_case001.output.txt

# Optional second check (full enumeration for n <= 13,
# deterministic sampling for larger n).
python3 UFUG2106_Round5.1_Delivery/tools/verify_netlist.py \
  data/stage1/case_001.txt /tmp/round51_case001.output.txt
```

The output is an **AND2/OR2/NOT gate netlist**, not a rendered circuit image.

### Run the instructor-provided evaluator on all 25 Stage 1 cases

The repository currently contains the `evaluator` binary and `data/stage1/`. If the checked-out binary lacks executable permissions (common on Windows-mounted WSL folders), copy it to a Linux temporary directory:

```bash
cp evaluator /tmp/ufug2106_evaluator
chmod +x /tmp/ufug2106_evaluator

EVAL=/tmp/ufug2106_evaluator
CASES="$(realpath data/stage1)"
ROUND51="$(realpath UFUG2106_Round5.1_Delivery/build/synth_round51)"

"$EVAL" "$ROUND51" "$CASES" --report /tmp/round51_stage1.csv
```

The documented two-argument evaluator interface is `evaluator PROGRAM BENCHMARK_FOLDER`; `--report` is supported by the evaluator version used in the archived experiments. If using another evaluator version that does not support it, omit that optional flag.

## 2. Compare Round 5 and Round 5.1

Round 5.1 retains the principal synthesis strategy from Round 5 while improving the efficiency of postprocessing with typed in-memory DAG operations. **This is the most directly interpretable paired comparison** in the archive.

After completing Section 1:

```bash
make -C UFUG2106_Round5_Delivery -j1

ROUND5="$(realpath UFUG2106_Round5_Delivery/build/synth_round5)"
"$EVAL" "$ROUND5" "$CASES" --report /tmp/round5_stage1.csv
```

The two CSV files contain per-case results to compare: functional `PASS`, `target_met`, `area`, `delay`, and `runtime_ms`.

For the **full original WSL paired protocol** (two reversed-order evaluations, independent checks, generated/holdout regression tests, and source/environment fingerprints), use:

```bash
bash UFUG2106_Round5.1_Delivery/run_round5_1_local.sh "$EVAL" "$CASES"
```

This extended runner saves **new** experimental evidence under `UFUG2106_Round5.1_Delivery/local_runs/`. It is not necessary for a quick demonstration; the prior successful runs are already archived below.

## 3. Run any other research round

Every main synthesizer accepts the same interface: `PROGRAM INPUT_FILE OUTPUT_FILE`. Build the selected version, then supply its executable to the evaluator as in Sections 1–2.

| Version | Build from repository root | Main executable (relative to repository root) |
|---|---|---|
| Round 1 (ROBDD baseline) | `make -C UFUG2106_Round1_Delivery` | `UFUG2106_Round1_Delivery/synth` |
| Round 2 | `make -C UFUG2106_Round2_Delivery` | `UFUG2106_Round2_Delivery/synth` |
| Round 3 | `make -C UFUG2106_Round3_Delivery` | `UFUG2106_Round3_Delivery/synth` |
| Round 4 | `make -C UFUG2106_Round4_Delivery` | `UFUG2106_Round4_Delivery/synth` |
| Round 4.1 (Balanced) | `make -C UFUG2106_Round4.1_Delivery` | `UFUG2106_Round4.1_Delivery/build/synth_balanced` |
| Round 5 | `make -C UFUG2106_Round5_Delivery` | `UFUG2106_Round5_Delivery/build/synth_round5` |
| **Round 5.1 (recommended)** | `make -C UFUG2106_Round5.1_Delivery` | **`UFUG2106_Round5.1_Delivery/build/synth_round51`** |
| Round 6.0 (experimental) | `make -C UFUG2106_Round6.0_Prototype` | `UFUG2106_Round6.0_Prototype/build/synth_round60` |
| Round 6.1 (experimental) | `make -C UFUG2106_Round6.1_Delivery` | `UFUG2106_Round6.1_Delivery/build/synth_round61` |

For example, compare the earliest correctness baseline with Round 5.1:

```bash
make -C UFUG2106_Round1_Delivery
ROUND1="$(realpath UFUG2106_Round1_Delivery/synth)"
"$EVAL" "$ROUND1" "$CASES" --report /tmp/round1_stage1.csv
```

Or test the later cut-rewriting experiment:

```bash
make -C UFUG2106_Round6.1_Delivery
ROUND61="$(realpath UFUG2106_Round6.1_Delivery/build/synth_round61)"
"$EVAL" "$ROUND61" "$CASES" --report /tmp/round61_stage1.csv
```

Round 4.1 also provides `synth_strict` and `synth_fast` variants. Rounds 6.0/6.1 include separate cut-postprocessor tools. Their own round READMEs explain these additional *ablations*, rather than treating them as the main executable.

**Important comparison note:** historical runtimes were not all measured together on identical machines. Rerunning versions on the same machine is preferable to interpreting archived median runtimes as a fully controlled ranking. The later Round 6 experiments reduced area slightly but incurred additional synthesis time; **Round 5.1 remains the recommended efficiency baseline**.

## 4. Where are our actual local results?

These are **recorded results from completed experiments**, not hypothetical outputs of the commands above.

| Evidence | Repository location |
|---|---|
| **Round 5.1 WSL reproduction report** | [Local reproduction report (2026-11-11)](Stage1_Freeze_Round5.1_Verified/evidence/report_ready/Round5.1_Local_Reproduction_Report_20261111.md) |
| **Paired Run 1: Round 5 vs 5.1** | [Round 5 CSV](UFUG2106_Round5.1_Delivery/results/paired/run1_reference.csv) · [Round 5.1 CSV](UFUG2106_Round5.1_Delivery/results/paired/run1_round51.csv) |
| **Paired Run 2: reversed order** | [Round 5 CSV](UFUG2106_Round5.1_Delivery/results/paired/run2_reference.csv) · [Round 5.1 CSV](UFUG2106_Round5.1_Delivery/results/paired/run2_round51.csv) |
| **Saved 25 Round 5.1 netlists** | [Frozen benchmark outputs](UFUG2106_Stage1_Round5.1_Freeze_20261111/benchmark/run1_round51_outputs/) |
| **Independent verification** | [Netlist verification log](UFUG2106_Stage1_Round5.1_Freeze_20261111/benchmark/independent_verification.log) |
| **Reproduction environment and source checksums** | [Environment](UFUG2106_Stage1_Round5.1_Freeze_20261111/environment.txt) · [Freeze manifest](UFUG2106_Stage1_Round5.1_Freeze_20261111/FREEZE_MANIFEST.json) |
| **Other rounds' evaluator CSVs** | The `results/` folders within each [Round 1](UFUG2106_Round1_Delivery/results/), [Round 3](UFUG2106_Round3_Delivery/results/), [Round 4](UFUG2106_Round4_Delivery/results/), [Round 5](UFUG2106_Round5_Delivery/results/), [Round 6.0](UFUG2106_Round6.0_Prototype/results/), and [Round 6.1](UFUG2106_Round6.1_Delivery/results/) directories |

In the archived paired WSL experiments, Round 5.1 achieved **25/25 PASS**, **25/25 delay targets met**, and **529,014 aggregate area** in both runs; the recorded median synthesis runtimes were **55.488 ms** and **55.077 ms**.

The [root README](README.md#4-research-development-rounds) summarizes the other rounds' recorded results. For mathematical derivations, detailed ablations, and failed or deferred ideas, see the [Technical Report](UFUG2106_Stage1_Writing_v1_0/technical_report/main.pdf) and [Trial Log](UFUG2106_Stage1_Writing_v1_0/trial_log_record/main.pdf).

*The official evaluator's PASS status and delay-target satisfaction are different conditions; the reported area sum is descriptive, not a published course grade. Stage 2 performance is not claimed here.*

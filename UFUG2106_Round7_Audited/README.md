# UFUG2106 — Round 7 Audited Experimental Package

**Status:** investigation / **NOT a qualified release**. This is the same Round 7 synthesis kernel as the earlier zip, with corrected experiments, diagnostics and reporting. No claim is made that the old `case_016` time-limit problem is solved.

## What we audited

The user's official paired results (2026-11-21 13:57 CST):

- Both implementations: 25/25 PASS on Stage 1, area 529,014 each; identical reported areas/delays for all jointly passed cases.
- Stage 2: Round 5.1 PASS counts 25/25 (run 1) and 24/25 (run 2). The first round's `case_016` passed with 98.409 ms, area 1,781, delay 36; the second run timed out. Round 7: 24/25 in both runs, failure on `case_016`.
- All 24 jointly passing Stage 2 cases had equal area and delay. Stage 2 speedups on common PASS/PASS cases were not sufficient to avoid a 100ms failure.
- The old one-click runner did not pass `--ablate` and thus produced no official ablation CSV. The independent 10,656-cover unit test did not write an ablation report. The old runner also exited successfully after printing a failed release gate.

**Critical suspected mechanism:** The first five search candidates in the original Round 5.1 main loop are not subject to a strict per-candidate deadline. The 75% guard is checked *only before* candidate initiation. A faster first candidate can permit a second candidate to start, thereby overshooting a 100ms total budget. This is a source-supported hypothesis, **not yet demonstrated by the archived profiled trace**.

## Place the folder

Unzip `UFUG2106_Round7_Audited` **beside** your existing `UFUG2106_Round5.1_Delivery`, `data` and `evaluator` directories in the `Final Project` root. It does not overwrite the existing `UFUG2106_Round7_Delivery` directory.

The compile step generates a source snapshot from the verified Round 5.1 code. It does not modify the Stage 1 implementation. `build/synth_round7` uses the same exact-cover optimization as the first Round 7 release; the synthesis algorithm itself is **not yet repaired**.

## 1. Run full official ablations (default)

From WSL:

```bash
BASE="/mnt/e/canfiles/Common courses study/大学通识/26-27 Fall/UFUG 2106 Discrete Math/assignment/Final Project"
cd "$BASE" || exit 1
bash UFUG2106_Round7_Audited/run_round7.sh
```

This runs Round 5.1, Round 7, and **three ablation modes** (`legacy_merge`, `legacy_cover`, `legacy_both`) on BOTH Stages and alternates test ordering across 2 repeats. The 4 Round 7 variants are configured by existing, unchanged environment toggles. The script *also writes* `results/ablation/cover_unit_test.log`.

A timestamped directory under `results/round7/` contains:

- `run{1,2}_stage{1,2}_round51.csv`
- `run{1,2}_stage{1,2}_default.csv`
- `run{1,2}_stage{1,2}_legacy_merge.csv`
- `run{1,2}_stage{1,2}_legacy_cover.csv`
- `run{1,2}_stage{1,2}_legacy_both.csv`
- Matching `.log` files for every evaluator call
- `summary.json`, `ablation_summary.csv`, `casewise_comparison.csv`, `AUDIT_REPORT.md`

**Exit status:** `2` if the default Round 7 misses a public PASS or delay target. The CSV files are still written and audited; a nonzero exit is intentional.

To reduce repeats (research quick-check only):

```bash
bash UFUG2106_Round7_Audited/run_round7.sh --runs 1
```

## 2. Diagnose case_016 search behavior (direct runs)

```bash
python3 UFUG2106_Round7_Audited/tools/profile_case016.py --runs 3
```

Writes `results/diagnostics/YYYYMMDD_HHMMSS/` with per-run stderr stage traces, explicit exit codes, individual netlists, independent exhaustive verifier outputs when possible, and `case016_profile_comparison.csv`.

**Important:** direct profiled execution has **no 100 ms official evaluation limit** (only a five-second diagnostic safety timeout) and includes instrumentation overhead. Only use it to locate the expensive stage / candidate and see which alternatives were attempted. Use the official evaluator CSVs to judge PASS.

## 3. The prior experiment and audit

The archive includes the user's first eight CSV reports and `summary.json` under `results/reference_20261121_135745/`, plus an independently generated `AUDIT_REPORT.md`, `ablation_summary.csv` and `casewise_comparison.csv`. Those are actual user-run official results, **not** results from this container.

## Interpretation rules

1. A PASS from one run and FAIL from another means a run-time **stability problem**, not deterministic success.
2. If a case fails, its area is missing; never treat it as zero or include partial sums as 25-case totals.
3. Equal area and delay are compatible with multiple different netlists. `case016_profile_comparison.csv` retains actual generated netlists for closer study.
4. A faster isolated cover kernel does not imply end-to-end benefit: earlier completion can trigger another search candidate.
5. The official PDF lacks a detailed numeric scoring function; comparisons in the audit use Pareto-oriented metrics, not an invented weighted score.
6. No source-level budget-control modification is included yet. The diagnostics should establish its actual effect before designing a robust scheduler rather than hard-coding `case_016`.

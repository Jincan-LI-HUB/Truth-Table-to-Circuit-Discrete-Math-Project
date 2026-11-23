# UFUG2106 Truth Table to Circuit — Round 7

**Milestone:** Round 7 (Exact Cover Acceleration)  
**Upstream:** frozen Round 5.1, GitHub blob `68ec9f54b27081641ac10358f81eef260acfcbdb`  
**Status:** Exact cover kernels tested; **official Stage 1 + Stage 2 evaluator runs still required on the user's WSL machine**.

## Why Round 7?

Round 5.1's fresh WSL baselines are:

| Data | Official PASS | Target met | Area sum | Median accepted runtime |
|---|---:|---:|---:|---:|
| Stage 1 (25 cases) | 25/25 | 25/25 | 529,014 | 54.177 ms |
| Stage 2 (25 cases) | 24/25 | 24/24 accepted | 506,754 (accepted only) | 39.020 ms (accepted only) |

`stage2/case_016.txt` fails with `TIME_LIMIT=100ms`. A standalone Round 5.1 direct run generated a correct netlist of area `2677`, delay `21`; the first trial required `105.674ms` (`BDD 0.398ms`, `mapping 92.523ms`). It is *not* an official PASS.

## Algorithm changes

- **R7-A:** Replace quadratic Quine–McCluskey cube-pair merging with **hash-neighbor merging**. The set of merged cubes and prime implicants is unchanged.
- **R7-B:** Replace repetitive greedy-cover minterm scans with **packed bit-vector intersections and population counts**. The gains, scores, tie-breaking, and chosen cover are unchanged.
- **R7-C:** Add cover-specific profiling and **independent ablation switches** for each optimization. **No deadline/portfolio policy changes in Round 7.** These are deliberately reserved for a later, controlled ablation if needed.

This is a strict algorithmic-efficiency iteration, not a claim of a new optimal synthesis strategy. Source-level reasoning appears in `docs/MATHEMATICAL_DESIGN.md`.

## Installation (WSL / Linux)

Place this unzipped folder **beside** your already existing `UFUG2106_Round5.1_Delivery` folder in the `Final Project` root:

```text
Final Project/
├── evaluator
├── data/{stage1,stage2}/
├── UFUG2106_Round5.1_Delivery/
└── UFUG2106_Round7_Delivery/
```

**Important:** This delivery is a **source-derived reproducible package**. It contains an offline bootstrapper rather than another unaudited duplicate of the original 43 KB C++ source. `make` automatically copies the exact local frozen source and its three headers to this milestone folder, applies the reviewed modifications, generates `SOURCE_MANIFEST.json`, then builds a standalone `build/synth_round7` binary. The original Round 5.1 directory is untouched. No Internet access required.

```bash
BASE="/mnt/e/canfiles/Common courses study/大学通识/26-27 Fall/UFUG 2106 Discrete Math/assignment/Final Project"
cd "$BASE" || exit 1

make -C UFUG2106_Round7_Delivery -j1
python3 UFUG2106_Round7_Delivery/tests/test_bootstrap.py
python3 UFUG2106_Round7_Delivery/tests/test_exact_cover.py
```

Or perform build, two independent tests and **both paired Stage 1 / Stage 2 evaluations** with one command:

```bash
bash UFUG2106_Round7_Delivery/run_round7.sh
```

If the upstream Git blob differs, bootstrap stops safely. Review local changes before explicitly opting into `python3 UFUG2106_Round7_Delivery/bootstrap_round7.py --allow-source-drift`.

## Official paired evaluations, both stages

```bash
python3 UFUG2106_Round7_Delivery/tools/run_benchmarks.py --paired --runs 2
```

Runs Round 5.1 and Round 7 on **both** `data/stage1` and `data/stage2`, alternating the pair order in the second repetition. Official outputs and logs are saved in a timestamped `results/round7/` directory; `summary.json` includes full pass/target counts, area sums, per-stage paired area differences, a 50-case joint comparison computed only on common PASS/PASS cases, recovery/regression cases, timing metrics, source/binary/evaluator digests.

If the basic evaluation succeeds, run the **independent optimization ablations**:

```bash
python3 UFUG2106_Round7_Delivery/tools/run_benchmarks.py --paired --runs 2 --ablate
```

Ablation labels:

| Label | Merge algorithm | Greedy algorithm |
|---|---|---|
| `default` | hash-neighbor | packed bitset |
| `legacy_merge` | original pairs | packed bitset |
| `legacy_cover` | hash-neighbor | original scan |
| `legacy_both` | original pairs | original scan |

These use `UFUG_R7_LEGACY_MERGE=1` and `UFUG_R7_LEGACY_COVER=1` and do **not** change the original source. Compare both stages; do not select thresholds based only on one publicly revealed case.

## Focused profiling

```bash
R7="$(realpath UFUG2106_Round7_Delivery/build/synth_round7)"
UFUG_ROUND5_PROFILE=1 "$R7" data/stage2/case_016.txt /tmp/r7_case016.net 2>/tmp/r7_case016.profile
cat /tmp/r7_case016.profile
python3 UFUG2106_Round5.1_Delivery/tools/verify_netlist.py \
  data/stage2/case_016.txt /tmp/r7_case016.net
```

The new `R7_STAGE stage=covers` line reports prime merging time, greedy selection time, probe counts, and configured ablations. The full official evaluation is still necessary; the direct run has no enforced official time limit.

## Verification already performed

- Compiled **the exact two C++ replacement snippets** in isolation, with `-O2 -std=c++17`.
- **10,656 randomized A/B comparisons** across `k=1..9`, ON and OFF covers, both toggles independently and together: all produced identical chosen cubes.
- Isolated Stage 2 `case_016` symbolic cover benchmark on the current container (mean of ten repetitions): **legacy 62.37 ms vs optimized 21.11 ms**. Equivalent selected cubes verified in this benchmark.

**Not performed here:** Compiling the whole upstream synthesizer in the assistant container (full Stage 1 source is not locally mounted), running your official local evaluator, confirming `25/25 Stage 2 PASS`, and determining final performance impact. Those claims are intentionally withheld. See `docs/EXPERIMENT_REPORT.md`.

## Release gate

Round 7 is eligible for promotion to a *candidate* only after:

1. Stage 1 **25/25 PASS** and Stage 2 **25/25 PASS** on official evaluator, repeatedly;
2. functional equivalence and preferably **all 50 target delays met**;
3. no major Stage 1 Area regression and positive combined Stage 1/2 Quality-of-Results trade-off;
4. new holdout and stress tests before final submission.

The reference CSVs are copied **unchanged** into `results/baseline/` so no missing-case area is silently counted as zero in a total score.

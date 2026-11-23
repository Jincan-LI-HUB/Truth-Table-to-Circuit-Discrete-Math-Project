# UFUG2106 — Round 7.1 Delivery

**Milestone:** Round 7.1 — Budget-Aware Portfolio Scheduling  
**Version status:** **Research candidate, not yet validated as 50/50 official PASS**  
**Input evidence:** User's paired Round 7 experiment (`20261121_140841`) and 15-case diagnostic log (`20261121_140830`).

## What this actually changes

It starts from the verified frozen Round 5.1 source and reuses the independently tested Round 7 hash-neighbor / bitset-cover accelerations. It adds a budget-aware dispatch policy: when the declared per-case runtime limit is at most 250 ms and a valid incumbent already meets target delay, it avoids starting optional **legacy** synthesis candidates. It reserves 28% of the declared budget for postprocessing, final output and evaluator overhead; secondary main candidates receive a cooperative deadline where the existing code supports it. Primary candidate zero, Boolean transformations and selection ranking remain unchanged.

This is *not* a new Boolean minimization representation, does *not* claim optimal circuits, and does *not* guarantee a hard execution deadline for every subsystem. Stage 1 and Stage 2 official outcomes are unknown until you run the included workflow on WSL.

### Why? Previous user-run evidence

- Round 5.1 on Stage 2: 24/25 and 25/25 across paired repetitions (the borderline case `case_016` changes outcome across runs).
- Round 7 default: 24/25 Stage 2 in **both** repetitions.
- One-fast-kernel ablations of Round 7: 25/25 Stage 2 in both repetitions.
- The R7 default direct profile showed eight completed candidates; one-fast-kernel variants completed six, yet selected the **same** verified case016 netlist with Area **1,781**, Delay **36**.
- Optimized merging/greedy counting reduced probes drastically, but the older portfolio could spend the saved time on extra legacy candidates. This interaction is the motivation for R7.1; see `docs/ROUND7_TO_7_1_EVIDENCE.md`.

## Quick start (WSL Ubuntu)

Extract this directory next to `UFUG2106_Round5.1_Delivery`, `evaluator` and `data/` in the existing Project Root.

```bash
BASE="/mnt/e/canfiles/Common courses study/大学通识/26-27 Fall/UFUG 2106 Discrete Math/assignment/Final Project"
cd "$BASE" || exit 1
bash UFUG2106_Round7_1_Delivery/run_round71.sh
```

**A feedback ZIP is created automatically even when a test fails.** Upload only the final file printed after `FEEDBACK ZIP CREATED:`. Expected location:

```text
UFUG2106_Round7_1_Delivery/feedback/Round7.1_Feedback_<timestamp>.zip
```

A failed release gate causes the runner to return a nonzero exit status **after** writing the ZIP; do not ignore it.

## Output and ablations

The default run executes **R5.1 + R7.1 guarded + R7.1 scheduler-off + two one-kernel ablations**, across both Stages in two paired repetitions with reversed order on repetition 2. It also profiles case016 directly (without the official deadline) and saves independent verification logs.

For faster preliminary smoke testing:

```bash
bash UFUG2106_Round7_1_Delivery/run_round71.sh --quick --runs 1 --case-profile-runs 1
```

The release criterion requires all 50 public cases PASS **and** meet target delays in both official rounds. Passing the public release gate is not a formal guarantee on the 50 hidden cases.

## Technical references

| Document | Purpose |
|---|---|
| `docs/ROUND7_TO_7_1_EVIDENCE.md` | Actual user-run numerical evidence, diagnosis, and conclusions |
| `docs/ROUND7_1_MATHEMATICAL_DESIGN.md` | Mathematical formulation, algorithm, proof sketch, time/quality trade-offs |
| `docs/EXPERIMENT_PROTOCOL.md` | Full build, environment, repeat, and interpretation protocol |
| `docs/PAPER_RESEARCH_NOTES.md` | Traceable research ledger and recommended report structure |
| `docs/CHANGELOG.md` | Exact changes and deliberately unmodified components |

`evidence/round7_user_run/` bundles the **actual previously uploaded** CSVs and selected logs; it is not Round 7.1 evaluation evidence. `evidence/baseline/` bundles the earlier Round 5.1 baseline CSVs. New results are created under `results/<timestamp>/` and packaged together with generated source and research notes.

## Source reproducibility

The delivery intentionally does not include a duplicate unfrozen implementation. It runs `bootstrap_round71.py`, which verifies the frozen Round 5.1 git blob `68ec9f54b27081641ac10358f81eef260acfcbdb` and generates `src/synth_round71.cpp` by two auditable deterministic patches. This leaves the R5.1 delivery untouched. The generated SHA-256 and header checksums are recorded in `SOURCE_MANIFEST.json` and included in your feedback ZIP. If source verification fails, do not use `--allow-source-drift` or replace the expected hash to force a build.

**Developer validation boundary:** The ten source-change anchors were checked against the exact GitHub frozen file; the isolated cover kernel test contains 10,656 A/B checks. The full generated C++ and official evaluator cannot be compiled/run in this file-creation environment without the user's local frozen-source folder and evaluator; those results must come from your WSL execution and are not claimed here.

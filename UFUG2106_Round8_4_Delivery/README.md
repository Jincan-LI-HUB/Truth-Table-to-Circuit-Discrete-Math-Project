# UFUG2106 · Round 8.4 Research Delivery

**Priority-Consistent Root Selection & Adaptive Work Allocation**  
Status: **locally verified research prototype; official Stage 1/2 evaluator confirmation requires the recipient's WSL environment**.

## Purpose

Round 8.3 ranks up to 1,500 candidate roots, then traverses them in topological order, examining at most 900. This is deterministic, but generally **does not examine the top-ranked 900**. Round 8.4 explicitly tests whether strict Top-Q selection is better, with controls for topology-first, rank/topology mixtures, denser budgets, and an adaptive pilot–focus branch allocation. None is presumed superior.

## Run

Extract this directory **alongside** `UFUG2106_Round8_3_Delivery` and `UFUG2106_Round8_2_1_Delivery` within the `Final Project` root; do not overwrite frozen versions. The root should also contain the authentic `evaluator`, `data/stage1`, `data/stage2`.

```bash
BASE="/mnt/e/canfiles/Common courses study/大学通识/26-27 Fall/UFUG 2106 Discrete Math/assignment/Final Project"
cd "$BASE" || exit 1
bash UFUG2106_Round8_4_Delivery/run_round84.sh
```

Quick check (1 evaluator run and fewer configurations):

```bash
bash UFUG2106_Round8_4_Delivery/run_round84.sh --quick
```

The script checks frozen-source fingerprints, compiles, runs policy isolation and independent exhaustive preflights, checks for the real course evaluator, and invokes **two paired runs over both public banks**. **Even if it fails**, it creates `UFUG2106_Round8_4_Delivery/feedback/Round8.4_Feedback_<timestamp>.zip`. Upload that single feedback ZIP.

### Experimental policies

Environment variable `UFUG_R84_POLICY`:

| Mode | Search description |
|---|---|
| `topology_dual` (**default**) | Old priority pool Top-1500; first 900 in topological order; conservative regression control |
| `topq_dual` | True top-ranked 900, subsequently processed topologically |
| `topq_dense` | True top-ranked 1,100 (more work; wall safety retained) |
| `mixed33_dual` | 1/3 high-score root quota + remainder by earliest topological order within Top-1500 |
| `mixed66_dual` | 2/3 high-score quota + remaining topology-first |
| `adaptive_dual` | 220-root Shannon/SOP pilots, then a 1,100-root focus on the higher gain-per-work branch |
| `topq_fast` | Single Shannon Top-Q branch |
| `topq_adp` | True Top-Q with area–delay-product-aware selection |
| `topq_strict` | True Top-Q with no delay increase relative to incumbent |
| `off` | No Round 8.4 postprocessing (legacy modes may be explicitly activated) |

Optional `UFUG_R84_ROOT_CAP=100..1500`, `UFUG_R84_PILOT_ROOTS=80..450`, `UFUG_R84_FOCUS_ROOTS=pilot..1500`, `UFUG_R84_PROFILE=1` for independent tracing. Clear `UFUG_R*` variables before a normal submission. All decisions are generic, never keyed to testcase IDs.

## What the local experiments actually showed

With a complete enumeration verifier, **150/150 Stage 2 outputs from 25 cases × six policies** computed the exact truth tables and satisfied target delay. All 25 cases were evaluated for each policy; see `evidence/stage2_full_150_exhaustive.csv`.

| Policy | Stage 2 Area Sum | Delay Sum | Wall-guard triggers |
|---|---:|---:|---:|
| `topology_dual` | 500,072 | 1,169 | 0 |
| `topq_dual` | 503,764 | 1,155 | 0 |
| `topq_dense` | 502,649 | 1,155 | 2 |
| `adaptive_dual` | 502,618 | 1,157 | 0 |
| `mixed33_dual` | 499,684 | 1,169 | 3 |
| `mixed66_dual` | 499,035 | 1,169 | 2 |

**Top-Q alone is a negative result for aggregate Area.** On Stage 2 `case_005`, Top-Q 900 produces 110,045 / Delay 53 versus topology's 106,771 / Delay 67, both valid under target 69. Mixing rank with topological coverage yielded a **new local Area improvement**: mixed66 reduced Stage 2 area by 1,037 with all casewise delays unchanged; some long cases still hit the emergency wall guard. One-off local timings are not comparable to official evaluator timings.

The first four critical cases' topology-mode netlist SHA-256 matched the frozen Round 8.3 executable. Full Stage 1 official results remain unmeasured in this container; do not infer them from Stage 2.

## Correctness and safeguards

- Every local candidate must implement the **same formal k-cut Boolean truth table** (k<=4).
- Per-root timing checks use backward-required time; the complete live DAG is checked before acceptance.
- Original full graph is preserved as a fallback and only complete valid candidates may replace it.
- Emergency wall clock guard remains. Fixed root quotas **do not guarantee bit-identical results on every machine** if the guard triggers earlier.
- Round 8.2.1 low-memory fallback and positive-RAM evaluator discrepancy are carried forward unchanged; no new claim of official RAM compliance is made.

## Study documents

- `docs/01_THEORY_AND_CORRECTNESS.md`: formal selection model, proofs, performance trade-offs.
- `docs/02_ABLATION_AND_NEGATIVE_RESULTS.md`: 150 verified local cases, counterexamples, and measurement scope.
- `docs/03_OFFICIAL_PROTOCOL.md`: paired official evaluation, limits and release gates.
- `docs/04_MEMORY_RESEARCH_ROADMAP.md`: actionable Memory–Runtime–Area/Delay study plan, separated from the external evaluator ambiguity.

## Final submission

This is a **research delivery**, not a new final submission binary chosen by score. Compare official output and 2+ runs before selecting a candidate. The final submitted executable should use the exact documented `program input_path output_path` contract, without special-case benchmark IDs or modified benchmark limits.

### Additional local stability checks

In the reused structured holdout, 24/24 exhaustive checks for each of Topology and Mixed66 passed; **Area Sum was identical (13,897)**. Repeating Mixed66 three times for four real Stage 2 cases found one important instability: `case_005` areas 106,806, 109,218, and 106,771 under different wall-guard outcomes. Therefore **the 499,035 local bank sum is a single-run outcome, not a guaranteed stable result**. See `evidence/repeat_mixed66_12.csv`.

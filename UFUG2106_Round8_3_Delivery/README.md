# UFUG2106 Final Project — Round 8.3

**Focus:** Deterministic root-work budgets, branch isolation, stable search and explicit Area–Delay–Runtime trade-offs. This is a **research candidate**, not yet a frozen final submission.

## What changed

Round 8.2.1 is frozen and remains a comparator. Round 8.3 adds `src/r83_cut.hpp` and an isolated `R83` branch to the standalone C++17 synthesizer. The new rewriter chooses live roots using the existing deterministic priority, then normally stops at a **fixed selected-root quota**; a separate time watchdog remains a safety fallback. Each SOP/Shannon branch is synthesized from the same original incumbent, with complete DAG cost/required-time assessment and explicit Pareto objectives.

- Default `stable_dual_area`: 900 selected roots per SOP/Shannon branch. On short-budget (`limit <= 2000 ms`) instances with at least 20 outputs, cap defaults to 600. These are generic resource features, *not case names*.
- `stable_fast_area`: one Shannon branch and 1200-root quota by default.
- `stable_fast_adp`, `stable_dual_adp`, `stable_dual_strict`: alternate ranking objectives.
- `full_dual_area`: 1500-root search-oriented ablation (may hit wall safety). Set `UFUG_R83_ROOT_CAP=1100` to reproduce the 1100-root dense ablation on any R83 mode.
- `UFUG_R83_POLICY=off` returns control to explicit R8.2 selection (`UFUG_R82_POLICY`).
- When R8.3 is active, old R8.0, R8.1 and R8.2 branches are **forced off**. This fixes a strategy-isolation error caught during prototyping.

The work quota is deterministic *conditional on the same frozen incumbent, the same compiler/inputs, and no watchdog interruption*. The initial Round 5.1/7.x candidate portfolio still has wall-clock-dependent decisions. **Round 8.3 is not a proof of fully deterministic end-to-end output.**

## Run on WSL

Extract next to `UFUG2106_Round8_2_1_Delivery` and `data/` in the existing `Final Project` directory:

```bash
BASE="/mnt/e/canfiles/Common courses study/大学通识/26-27 Fall/UFUG 2106 Discrete Math/assignment/Final Project"
cd "$BASE" || exit 1
bash UFUG2106_Round8_3_Delivery/run_round83.sh
```

The script verifies source hashes, compiles the standalone executable, checks strategy isolation on a real Stage2 input, exhaustively checks 5 critical Stage2 truth tables, then runs the **real course evaluator** in 2 reversed-order paired runs on both Stage1 and Stage2. Six configurations: R8.2.1 Fast Area, R8.2.1 Dual Area, R8.3 Fast Area, R8.3 Stable Dual Area, R8.3 Stable Dual ADP and R8.3 Dense Dual Area (1100-root ablation).

For the shorter 1-run/3-config smoke test:

```bash
bash UFUG2106_Round8_3_Delivery/run_round83.sh --quick
```

The script always creates one ZIP on success or failure in `feedback/Round8.3_Feedback_<timestamp>.zip`. **Upload that ZIP** for full analysis. A missing evaluator fails explicitly and is never treated as official success. Use `make -C UFUG2106_Round8_3_Delivery -j1` for standalone compilation.

## Local evidence already produced

- **Real Stage2:** 25/25 full truth-table exhaustive checks, target met, total area **500,072**, delay sum 1,169 on the author's current Linux container. No R83 cut watchdog hits in that particular 25-case run. This is NOT course evaluator data, and public cases are development data.
- **Same-container independent R8.2.1 Dual reference:** 25/25 exhaustive; total area 499,793; same per-case delays; **R8.3 is 279 area units worse in this comparison**. Variability in the parent time-based portfolio and other runtime settings limits generalization.
- **Prior structured synthetic holdout reused (not fresh blind):** 24/24 exhaustively correct; both same-container implementations total area 13,897 and delay sum 613.
- **Repeats:** in 3 runs each of 4 Stage2 probes (12 runs of default stable policy) all 4 had identical output hashes with no cut watchdog; a 1100-root comparison produced a watchdog event and varying hashes on `case_017`. It is NOT a statistical stability guarantee.
- **Aborted / invalid experiment:** an early prototype inadvertently activated R8.0/R8.1 when R8.2 was disabled. Those results were discarded; strategy-isolation regression test added.

See `docs/01_METHOD_AND_MATHEMATICS.md`, `docs/02_EXPERIMENT_EVIDENCE_AND_LIMITS.md`, and `docs/03_OFFICIAL_PROTOCOL.md` for details.

## Outstanding Issue #2 and grading caveat

GitHub Issue #2 was filed by a teammate, *not the course instructors*. Round 8.2.1's low-RAM repair is preserved, but the official evaluator still disagrees with independent RSS measurement on positive RAM limits. This delivery does **not** claim that resource issue is closed. The course's exact final score formula is not established here. Preserve separate Area, Delay, Runtime, and constraint-PASS comparisons rather than asserting a universal winner.

# Round 9.0 — Engineering Hardening & Submission Safety

**Status: independent local delivery, not grading-server acceptance or the team-integrated final Stage 2 solver.** This milestone intentionally adds no new Cut-Rewriting strategy.

## Fixes implemented

1. `submission/synth.cpp` now defaults to `extra_sop`, even when launched with **no** `UFUG_*` environment variables. Frozen R8.6 remains unchanged in `src/synth_round86_frozen.cpp` for a fair control.
2. For `n >= 18` and `0 < runtime_limit <= 250 ms`, the first full read of all truth-table entries checks exact constants/literals and GF(2)-affine signatures. If a correct, target-meeting netlist is obtained, the expensive BDD and Cut portfolio is skipped. The usual synthesis path is unchanged for normal-budget cases and non-affine functions. **A short runtime is not guaranteed.**
3. The 36 earlier Holdouts and 3 adversarial stress inputs have been independently reserialized to the PDF's exact line layout, preserving **all input tokens**. Both original and canonical inputs are provided for auditing.
4. Four new high-complexity **development** cases activate large Cut Search. Four additional seeded functions are in `hard_bank/lockbox`: **do not use the lockbox for parameter tuning**; reserve it for future frozen-candidate evaluation.
5. A standalone source-only submission tree, source fingerprints, isolated cold-compilation test, and real course evaluator pairing are included. There is no requirement for historical Round delivery folders to compile.

## WSL

Place the extracted directory beside the course `evaluator`, `data/stage1`, `data/stage2`:

```bash
BASE="/mnt/e/canfiles/Common courses study/大学通识/26-27 Fall/UFUG 2106 Discrete Math/assignment/Final Project"
cd "$BASE" || exit 1
bash UFUG2106_Round9_0_Delivery/run_round90.sh
```

Alternative modes:

- `--local-only`: provenance, canonical inputs, cold compilation and exhaustive checks; no course evaluator required.
- `--quick`: shorter local smoke and one pass of official public bank; skips repeated isolated cold recompilation (full/default includes it).
- `--stress-only`: exhaustive smoke plus **genuine evaluator** on the three adversarial 100-ms inputs when present; official FAILs are recorded rather than hidden. **Not a release gate.**

Every run creates a `feedback/Round9.0_Feedback_<timestamp>.zip`, even if the genuine evaluator is missing or a regression fails. Upload this one ZIP for audit. The standard run includes **four configurations × two stages × two runs × 25 cases = 400 official public records**.

## Submission contract

Copy **the entire `submission/` directory** into your eventual submission, with `synth.cpp` plus its 11 required headers. The program's only mandatory arguments are `<input_path> <output_path>`:

```bash
g++ -O2 -std=c++17 -pipe -DNDEBUG submission/synth.cpp -o synth_stage2
./synth_stage2 input.txt output.txt
```

Use `g++` from Ubuntu 22.04.x for the final submission check. This source is **not** the teammate's merged Stage 2 solver. Do not imply the team's integrated BDD budget issue is resolved.

## Evidence boundary

- Input/output functional correctness uses independent full `2^n` enumeration.
- All public-area comparisons are from the genuine evaluator, not the local verifier.
- The stress cases are user-created and deliberately harsher than public examples. Their outcome is not a statistical hidden-test estimate.
- The TA clarified no positive `ram_limit` on public or hidden grading cases, but memory profiling still matters for reliability.
- The new preflight may trade small input-pass overhead for avoiding large portfolio allocations on trivially structured, short-limit inputs.
- Source default policy can still be overridden through research-only environment flags. Final team integration should remove any accidental production dependence on such flags.

See `docs/01_DESIGN_AND_PROOF.md`, `docs/02_RISKS_AND_GATES.md`, and `docs/03_ROUND91_HANDOFF.md`.

## Locally measured negative evidence

A paired 3× direct-process benchmark found local median times (frozen R8.6 → new R9.0): direct 250.97 → 55.65 ms; affine parity 157.75 → 58.10 ms; **non-affine sparse 42.42 → 84.47 ms**. Wall times vary and should not be interpreted as official hard-deadline PASS. See `docs/04_LOCAL_ABLATION_REPORT.md` and `evidence/stress_paired_local_3x.csv`.

# UFUG2106 Final Algorithm Audit — Phase 0–2 deliverable

## What this package is

This is a **source-based technical analysis package**, not the final Report. It addresses the first gates of `UFUG2106_Final_Report_Execution_Plan_v1.md`: freeze identifiable sources, reconstruct the true R10.0 default execution path, formulate mathematics with explicit assumptions, verify primary experimental totals, and document unresolved matters.

**Read in this order:**

1. `FINAL_SOLVER_SPEC.md` — complete algorithm, data structures, gates, default policy, fallback, derivations, code anchors and measurements.
2. `MATHEMATICAL_VERIFICATION.md` — conditional proofs and false/overbroad claims to avoid.
3. `REQUIREMENTS_MATRIX.md` — map to `Final_Project.pdf` contract.
4. `OPEN_ISSUES.md` — blockers and known implementation limits.
5. `SOURCE_REGISTRY.csv`, `EVIDENCE_REGISTER.csv`, `PROVENANCE_CHECK.json` — hashes and provenance.
6. `R100_FEEDBACK_RECOUNT.csv`, `SOURCE_SMOKE_RESULTS.csv` — independently recalculated official-feedback totals and **separate local** small-function tests.

## Included primary source and reproducibility

- `primary/03_frozen_candidate/submission/` — exact 13-file R10.0 independent candidate, with release README.
- `stage1_zeyun/UFUG2106_Stage1/` — the actual Stage 1 submitted source extracted from the original RAR.
- `primary/02_official_feedback/` — collected official-feedback ZIPs from R7.2 through R10.1; the exact contents are integrity checked against collector `MANIFEST.json`.
- `research/` — selected source/round matched comparisons and analysis extracts from the 23 Nov reconstruction package; the original complete archive is `UFUG2106_Stage2_Research_and_Reproduction.zip` (separate earlier upload).
- `run_source_smoke_checks.py` — makes small complete truth-table fixtures and independently simulates both solver netlists.
- `verify_stream_affine.py` — independent **\(2^{18}\)**-row vectorized check for the high-n streaming path.
- `build_registry.py` — rebuilds SHA-256 provenance checks and R10.0 official feedback recount.

### Local regeneration (Linux, Python 3, GCC 11+/C++17; NumPy only for streaming vector check)

```bash
D=/path/to/UFUG2106_Final_Algorithm_Audit_v1

g++ -O2 -std=c++17 -DNDEBUG "$D/primary/03_frozen_candidate/submission/synth.cpp" -o "$D/r100_synth"
g++ -O2 -std=c++17 -DNDEBUG "$D/stage1_zeyun/UFUG2106_Stage1/src/synth.cpp" -o "$D/zeyun_synth"
python3 "$D/build_registry.py"
python3 "$D/run_source_smoke_checks.py"
python3 "$D/verify_stream_affine.py"
```

The compiled binaries and local fixture outputs are excluded from the slim deliverable to avoid distributing platform-specific build byproducts; the script and input fixture can regenerate them.

## Scope/notes

- No full 50-case *new* evaluator run in this container; instructor cases/evaluator are not directly installed here. The package does contain the **archived real official-feedback CSVs** and the original matched local reproducibility data.
- Stage 1 R5.1 independent research remains an essential historical reference in its GitHub Stage 1 freeze, but is not confused with the actually submitted Zeyun code.
- The frozen candidate README explicitly says this R10.0 is not yet the teammate-integrated final source.
- No color or graphical design was undertaken. `palette.json` is reserved unchanged for the later visualization stage.

## Gate status

See `PHASE_0_2_STATUS.md` for what is verified and what **remains open**. In particular, candidate source provenance is established, but team integration has not yet been proven; do not call this a submitted final team implementation.

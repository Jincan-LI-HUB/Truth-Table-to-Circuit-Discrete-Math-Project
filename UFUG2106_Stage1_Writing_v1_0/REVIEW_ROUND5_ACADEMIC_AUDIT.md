# Manuscript Review — Round 5: Research Reproducibility & Final Academic Audit

**Base:** Draft v0.6. **Output:** Draft v0.7. **P0:** deferred, unchanged. **Stage 2:** outside scope.

## Findings and actions

1. **Main evidence extraction verified.** The selected original 9 official WSL archives are referenced by immutable archive SHA-256 in `source_manifest.csv`. Re-running the extraction script against mounted original ZIPs produced 14 normalized CSV files that were **byte-identical** to the files shipped in the v0.6 writing package. The new verifier checks this mechanically and refuses missing archives/hashes, case IDs and invalid statuses.
2. **Source identity verified, not final-submission identity.** Frozen `synth_round51.cpp` SHA-256 matches the student-confirmed research freeze: `cf90d0b110e6f45d1d508db351c95f10e7d704824fc34e17e6a5f5b783e20759`. The `FREEZE_MANIFEST.json` also identifies dependent source files. No claim about actual Canvas-submitted bytes is made.
3. **Different reproducibility levels were previously blurred.** Recreating figures from bundled processed CSVs is not the same as re-extracting history from nine separate original ZIPs, and neither equals executing the synthesizer with private instructor cases. Added tiered explanation in both manuscripts.
4. **Claim-to-evidence lookup was implicit.** Added `CLAIM_EVIDENCE_LEDGER.csv`, recording provenance, values and inference limits, including single-sample Peak RSS and Round 6.1 budget development sweeps.
5. **Bibliography provenance checked.** Bryant 1986 and Mishchenko et al. 2006 DOI/page metadata were verified from external bibliographic or publisher sources; inserted the DOI identifiers in both inline bibliographies. External AIG rewriting is prior work, not a claimed implemented algorithm.
6. **Non-deterministic clock cutoffs:** source hashes alone do not imply identical generated netlists, speed, memory or official score on a different machine; this limitation now appears explicitly in the reproducibility discussion.

## Remaining boundaries / checks before publication

- Original private truth-table cases and official evaluator are deliberately not included in the public writing package; full end-to-end evaluator reproduction requires separately held original inputs and an appropriate machine.
- Do not describe sampled independent checking as exhaustive proof for every large input.
- The numerical official course-score function is not documented by the provided specification or evaluator CLI; claim only measured area/delay/runtime and own internal rank heuristic.
- Per-case published metrics are descriptive of their specific official logs; performance on unreleased Stage 2 remains unobserved.
- Author/team contribution and AI-use details (P0) are left explicitly pending, according to user direction.

## Plot artifact hashes

Re-running Matplotlib changed the export-level SHA-256 of seven vector PDF figures without changing their bundled numeric source CSVs. The earlier `editorial/V0_6_EVIDENCE_INTEGRITY.json` is a **historical v0.6 manifest**, not the current v0.7 hash list. `editorial/V0_7_ARTIFACT_INTEGRITY.json` records both sets of hashes and marks regeneration separately. Numeric provenance is checked from the CSVs, not by assuming deterministic PDF metadata.

## Verification commands

```bash
python3 shared/scripts/verify_provenance.py --report editorial/audit_bundled.json
python3 shared/scripts/verify_provenance.py --source-dir /mnt/data \
  --freeze-dir /mnt/data/UFUG2106_Stage1_Round5.1_Freeze_20261111 \
  --report editorial/audit_full.json
python3 shared/scripts/verify_deep_exposition.py
python3 shared/scripts/verify_worked_example.py
python3 shared/scripts/make_figures.py
```

Both manuscripts must then be compiled and PDF pages visually inspected. Keep the original archive hashes unchanged.

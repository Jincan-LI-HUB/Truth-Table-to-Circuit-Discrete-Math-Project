# Round 9.0 — Official Feedback Audit (2026-11-22)

## Evidence and scope
- Input feedback: `Round9.0_Feedback_20261122_191349_795748229.zip`; `220` ZIP members; CRC check passed.
- Source: 16 genuine evaluator CSVs, 400 casewise records (4 programs × 2 stages × 2 runs × 25 cases), local exhaustive logs, source snapshot and metadata.
- Platform: `Linux-6.6.87.2-microsoft-standard-WSL2-x86_64-with-glibc2.39`, according to feedback metadata. It is not the grading server.
- Evaluator SHA-256: `142361d7ce18bc47dea6a07538db79a588b3afbf446526c1d1246f4968b3d0ca`.
- R9.0 and submission source SHA-256: `f846b2c055bfd5ad8d252dd1dcaa6770040b290bff6dc2bddc0ab27ff77e4010` (exact match).
- Frozen R8.6 source SHA-256: `6d21a7d3cf80a8662f4f42a965e84c50d6cffcef7766a4d2dccf282c204078d8`.

## Official public gate
- **400/400 PASS and 400/400 Target Met** (all status rows and JSON summary agree).
- Each of the four configurations across both runs: Stage 1 Area = 526,135, Delay Sum = 1,212; Stage 2 Area = 494,999, Delay Sum = 1,170; overall Area = 1,021,134, Delay Sum = 2,382.
- **Every single case** matches frozen explicit Extra SOP in both Area and Delay (each of the 3 new variants: 100/100 across 2 runs), i.e. 300/300 paired casewise identical Area/Delay.
- Each of the 4 variants has 50/50 Area/Delay agreement between Run 1 and Run 2; this is measured outcome consistency, not netlist byte equality or cross-machine determinism.

### Runtime paired against frozen R8.6 Extra SOP
| Candidate | Run 1 Geomean runtime ratio | Run 2 Geomean runtime ratio |
|---|---:|---:|
| `r90_no_flags` | 1.0038 | 1.0054 |
| `r90_explicit_extra` | 1.0035 | 0.9974 |
| `submission_no_flags` | 1.0061 | 0.9884 |

These differences are around the 1% level and cannot establish a significant runtime improvement or regression from only two passes. The benchmark runs sequentially under WSL and depends on machine scheduling.

## Stress-case evidence (NOT an official stress evaluation)
The ordinary official runner did **not** invoke `tools/run_stress.py` and its feedback contains no course-evaluator status for the three 100-ms stress inputs. Never interpret local exact verification as the official runtime gate.
| Case (runtime_limit = 100 ms) | Frozen R8.6 local ms | New no-flags local ms | New explicit local ms | Submission local ms |
|---|---:|---:|---:|---:|
| `stress_001.txt` | 155.675 | 75.595 | 102.564 | 82.749 |
| `stress_002.txt` | 168.114 | 61.235 | 59.128 | 60.335 |
| `stress_003.txt` | 49.528 | 60.047 | 52.253 | 64.848 |

- `stress_001` is direct/literal; `stress_002` is affine; these new paths are logged as `R90_SHORT_PATH` and pass exact truth enumeration. `stress_003` is non-affine and falls back to the normal portfolio.
- One new explicit run of `stress_001` took 102.564 ms in direct local process timing, beyond its deliberate 100-ms cap; timing variation is material.
- Both `src/synth_round90.cpp` and `submission/synth.cpp` are **not** the team-integrated Stage 2 solver; the latter also requires 11 local headers to compile.

## Risk ledger and next steps
1. **PASS / closed:** No-environment default selection produces the intended Extra SOP results on all 50 public cases; confirmed both by source diff and independent evaluator runs. The submission tree can be cold-built without historical research round folders (reported cold build pass).
2. **PASS / narrowly:** Input canonicalization: WSL logs verify 39/39 token-equivalent inputs, plus 64 local exhaustive checks, across known cases.
3. **OPEN / critical verification:** Run `bash UFUG2106_Round9_0_Delivery/run_round90.sh --stress-only` in the WSL course environment; review official reports for direct, affine, and non-affine under 100 ms. These deliberately adversarial cases are not a substitute for the grading hidden test distribution.
4. **OPEN / integration:** Team Stage 2 merged solver and Issue #2 BDD budget transfer remain independently unverified. Ensure final packaging supports the included headers, not just the `synth.cpp` basename.
5. **Round 9.1 go/no-go:** Begin a small, reversible bounded local rewriting prototype against frozen no-env R9.0; keep difficulty-triggering development bank separate from untouched 4-case lockbox, and use new circuits for actual quality-generalization verification.
6. **Score caveat:** Aggregate Area and Delay are not the published grade score; the scoring formula/weights are not established by this feedback. Use casewise Area/Delay/Runtime and failure risk.

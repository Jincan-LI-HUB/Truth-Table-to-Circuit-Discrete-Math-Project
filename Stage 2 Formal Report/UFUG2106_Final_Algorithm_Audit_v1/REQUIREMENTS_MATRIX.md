# Official Requirement-to-Evidence Matrix — Phase 0

Basis: `primary/00_specification/Final_Project.pdf`, pp. 1–4. This matrix describes evidence readiness, **not** completed manuscript sections.

| Official requirement | Authoritative evidence | Current audit status | Writing implication / remaining action |
|---|---|---|---|
| Exact truth-table semantics; 1 ≤ n ≤ 20, m ≥ 1 | Specification pp. 1–2; `synth.cpp:948–965`, `:36–66` | Spec inspected; input parser and stream reader identified | Define index ordering (x0 MSB) once; avoid a separate storyline about stage ranges |
| Gate set AND2/OR2/NOT; ordered IDs, zero/inputs | Specification p. 2; `typed_netgraph.hpp:26–61,114–145`; `synth.cpp:352–354` | Source-traced; local independent netlist checker run | Describe legal serialization and constant-1 realization via NOT(0) |
| Validity requires full truth-table equality + legal netlist + positive resource limits | Specification p. 3; local smoke tests; archived evaluator | New smoke test: 20/20 exhaustive passes; formal benchmark results retained | Do not equate exhaustive testing of a few fixtures with universal software proof |
| Area A = Σ Nt at (charge listed gates once) | Specification p. 3; `typed_netgraph.hpp:26–44` | Verified metric code | Do not describe `metric()` as internally pruning: `Builder::finish()` does pruning |
| Delay critical-path maximum; target miss may still PASS | Specification p. 3; source `metric()` | Verified | Distinguish functional validity, delay target and runtime |
| Runtime wall-clock, positive RAM/time caps | Specification p. 3; `synth.cpp:948–1027, 1050–1112`; `r821_resource.hpp`; `r90_stream.hpp` | Control flow traced; limited independent smoke | Budget heuristics and RAM admission are not hard upper-bound proofs |
| Sequential CPU executable takes exactly two paths | Specification p. 4; R10.0 `main()`; frozen README | Successfully compiled/ran locally with GCC C++17 | Preserve actual `main()` interface and compilation flags |
| Stage 2 method improvements relative to **actually submitted Stage 1** | Zeyun submitted `src/synth.cpp`, final R10.0 source, Stage 1 trial log | Both exact local sources re-opened and SHA frozen | Document distinction between *team-submitted* Z1 and independent R5.1 research |
| Stage 2 both programs on 50 cases, per-case PASS/FAIL, Area, Delay, Runtime | `research/01_normalized_data/matched_case_metrics.csv`, original R10 official feedback | Existing 300 matched rows found; R10 100-case feedback CSV recalculated; input truth tables not bundled | Later re-audit full comparator CSV and use 50×2 official table, not aggregated summary alone |
| Individual contributions and teamwork | User-confirmed division; Stage 1 submitted README and trial log | Historical sources found; final team integration requires confirmation | Accurate, shared contributions; disclose substantial AI work |
| Final source + README, Live Q&A | R10 delivery README (`independent candidate` disclaimer), actual submission directory | Source candidate built; integrated final team submission not established | Before final release, obtain team-integrated final source/hash, cold build, exhaustive official/short-cap testing; both members prepare Q&A |
| 50 hidden cases (unavailable) | Specification p.4 | Cannot test | No hidden-case performance claims |

**Ground truth hierarchy:** task contract → actual frozen source → raw evaluator/case CSV → research trial log → written interpretation. Keep `PASS` distinct from `target_met`; never present an unpublished grading formula as known.

# Supplementary Generated Test Suites: Construction and Evaluation

## Why extra suites were constructed
The published 25 Stage 1 cases supported main algorithm development, so repeated comparisons on them risk performance-selection bias. Distinct structural function families probe correctness and performance on other known distributions; they cannot establish performance on future Stage 2 tests.

## Confirmed generator provenance

| Suite | Cases | Seed | Structures | Evidence role |
|---|---:|---|---|---|
| R5.1 mixed v1 | 80 | `0x51A17C0DE` | affine, sparse, threshold, mux, arithmetic, shared, structured, dense | held-out generative regression (per manifest) |
| R5.1 large v1 | 16 | `0x515A7E11` | local lookups, shared ensemble, XOR lookups, cascaded mux | larger structural holdout |
| R5.1 older generated suite | 110 | not verified from bundled generation script | legacy generated functions | **regression**, not new holdout |
| R5.1 stress | 2 | not separately specified | stress inputs | engineering regression |
| R6.0 development | 40 | `602106` | affine, mux, threshold, SOP, random gate DAG | development, not an untouched final holdout |
| R6.1 fresh mixed | 40 | `661061` | affine, mux, threshold, SOP, random gate DAG | post-budget-selection generated holdout |
| R6.1 fresh large | 8 | `0x615A7E11` | lookup, ensemble, XOR lookup, mux | larger post-budget-selection holdout |
| R6.1 budget sweep | 40+16 development functions | recorded separately | structural | **development** budget selection |

## Exact steps
1. Fix the generator seed, formula families, output counts and cost ranges.
2. Evaluate each formula on every input assignment, write an exact complete truth table and gate-cost parameters.
3. Save a manifest containing seed, family, n, m and SHA-256 per case.
4. Evaluate the frozen comparator and candidate separately with the official evaluator using identical generated inputs; save status/target/area/delay/runtime.
5. Cross-check Boolean equivalence of emitted netlists and preserve regression failures.
6. Keep development-set and holdout conclusions separately; do not make unknown-distribution claims.

## Provenance limitations
The statements `designed_before_testing` / `generated_before_implementation` are metadata present in saved scripts/manifests, not a separately audited chronology. Deterministic seeds support repeatability, not statistical representativeness. No original course-provided Stage 1 inputs are redistributed in this writing bundle.

# R9.0 Local ablation, with negative evidence

**Measured on a non-grading Linux host; never equate these times with course evaluator timing.** Executables built with `g++ -O2 -std=c++17 -pipe -DNDEBUG`; case inputs were normalized to the PDF line format. Each original and revised solution was validated by independent exhaustive enumeration.

## Three repetitions, alternated execution order

| 100-ms synthetic stress case | Frozen R8.6 Extra SOP median | R9.0 no-flags median | Observation |
|---|---:|---:|---|
| stress_001, 20-input direct | 250.97 ms | 55.65 ms | Large reduction from full-stream literal recognition |
| stress_002, 20-input affine parity | 157.75 ms | 58.10 ms | Large reduction from full-stream affine recognition |
| stress_003, 18-input non-affine sparse | 42.42 ms | **84.47 ms** | **Negative result:** new signature probing can cost more than it saves |

Individual wall times varied substantially (for example R9.0 direct 54–136 ms across three runs), so **none of these medians proves a hard 100-ms PASS**. The positive test cases are algorithmically fast on this host, but wall-clock noise and file system differ from WSL and the course grading server. Stage 2 public scoring uses original course files and the genuine evaluator; no stress-case modification is smuggled into that bank.

**Exact test evidence:** all 64/64 tests in `evidence/local_64_casewise.csv` pass Boolean equivalence. They compare new no-env default, new explicit Extra SOP, frozen R8.6 explicit Extra SOP, and a completely isolated submission directory. The representative cases include three short stress inputs, nine canonical earlier Holdouts and four new development functions. Four separately frozen lockbox functions remain untested for future research.

## Development bank Cut Search activation

The new `hard_bank/dev` contains random truth functions and independently generated random DAGs (no hand-selected course cases). Profiling with `UFUG_R86_PROFILE=1` confirms genuine root-work activity:

- `hard_002`: Shannon 900 visited roots and SOP 1200 visited roots; SOP achieved a weighted-area improvement from 6381 to 6380.
- `hard_004`: Shannon 900 roots and SOP 1200 roots with no accepted improvement, providing valuable negative evidence.
- `hard_001`: Shannon 759, SOP 759; one branch improved area.
- `hard_003`: Shannon 606, SOP 606, two successful updates.

These samples exercise R8.6 work allocation more than the original 36 easy Holdouts, but are only an instrumentation/development bank, not an unbiased prediction of official hidden-case scores. Lockbox files are intentionally preserved without evaluating them.

## Remaining boundaries

- The real evaluator may time out on stress_001 or stress_002, particularly on a slow filesystem; only the WSL stress report can evaluate that.
- The revised solver can be slower for non-affine inputs in the same short-time class. Do not use this patch without assessing its overall Runtime–Area effect.
- Extra SOP is superior on measured public area but about 4.2% slower in the prior paired analysis. The course did not disclose the exact score weights, so this does not prove final-score superiority.
- Actual team-integrated solver, BDD search-budget handling, hidden grading tests and 48-GiB server results are outside this stand-alone patch.

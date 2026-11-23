# UFUG2106 Round 9.1 — Official Postmortem and Round 10 Decision

**Audit inputs:** `Round9.1_Feedback_20261122_114755_082118.zip`; 20 course-evaluator CSVs (2 stages × 2 runs × 5 policies), 500 case records, bundled source and experimental evidence.  This is a public-data result, not a hidden-data result.

## Integrity and scope

- All 500/500 official public evaluations are `PASS`, with `target_met=yes`; 50/50 public cases for every policy in each run.
- All 5 policies have 50/50 casewise Area and Delay equal between run 1 and run 2. This establishes metric stability **within this two-run experiment**, not cross-machine or all-input determinism.
- `r91_off` and frozen R9.0 have identical casewise Area and Delay across both runs, supporting strategy isolation.
- Frozen R9.0 source SHA-256: `f846b2c055bfd5ad8d252dd1dcaa6770040b290bff6dc2bddc0ab27ff77e4010`.
- R9.1 candidate source SHA-256: `345982dc0c27bd9862e03bf4b8e14a4741eeaba756212e2ccda114f040f4fb9f`.  Bundled R9.1 submission source SHA-256: `345982dc0c27bd9862e03bf4b8e14a4741eeaba756212e2ccda114f040f4fb9f` (**identical**).
- The final R9.1 source has **postprocessing OFF when `UFUG_R91_POLICY` is unset**; `repeat_sop` in the WSL experiment is NOT the unconfigured submission behavior.

## Official summary (per run)

| Policy | Stage1 Area | Stage2 Area | Total Area | Total Delay | Area wins vs Frozen | Delay higher | Runtime geometric ratio to Frozen |
|---|---:|---:|---:|---:|---:|---:|---:|
| `r90_frozen` | 526,135 | 494,999 | 1,021,134 | 2,382 | 0/50 | 0/50 | 1.000× |
| `r91_off` | 526,135 | 494,999 | 1,021,134 | 2,382 | 0/50 | 0/50 | 0.993× |
| `r91_library` | 525,832 | 494,639 | 1,020,471 | 2,384 | 15/50 | 2/50 | 1.082× |
| `r91_repeat_sop` | 525,582 | 493,965 | 1,019,547 | 2,382 | 8/50 | 0/50 | 1.034× |
| `r91_repeat_shannon` | 525,737 | 494,518 | 1,020,255 | 2,381 | 5/50 | 0/50 | 1.028× |


## Causal interpretation

- **Repeat SOP**: total Area 1,019,547 versus frozen 1,021,134, improvement **1,587 (0.1554%)**, Delay unchanged in every public case, 8/50 cases improved, 0 regressed in Area. Its paired runtime geometric mean is **1.0336×** frozen (~+3.36%). The nominal extra pass has root cap 160 and time allowance `min(90 ms, 6% of case limit, available time to 82%-of-limit)`, subject to wall-clock overshoot from in-progress work. It executes only for specified policies with `limit>=1000`, valid incumbent and sufficient allowance.
- **Library**: Area reduction 663 (0.0649%), 15/50 improved cases but two Delay +1 cases (Stage1 case_002: 60→61, target61; Stage2 case_021: 69→70, target70). Runtime geometric ratio 1.0823× frozen (~+8.23%). This is an experimental research result, not evidence to turn on the library in production.
- **Repeat Shannon**: Area reduction 879 (0.0861%), Delay sum decreases by 1, runtime geometric ratio 1.0283× frozen.
- An **a posteriori oracle** that selects the lower-Area result of frozen, Library or Repeat SOP on each of the **known public cases**, while disallowing any higher Delay than frozen, would achieve 1,019,521 Total Area: only **26 lower** than Repeat SOP. This is an *observed candidate-selection upper bound*, not an implementable policy or a bound on future algorithms.
- These algorithms have different intrinsic cost per root/cut; matching root caps and nominal deadlines controls important parameters but does not equalize the actual CPU work. Interpret "matched budget" with that limitation.
- Both runs are public cases seen repeatedly in previous stages. No hidden-score ranking is warranted. The course's exact performance aggregation is not identified in these artifacts.

## Notable casewise reductions for Repeat SOP

| Stage and case | Frozen Area | Repeat SOP Area | Saved | Delay |
|---|---:|---:|---:|---|
| stage2 / case_005.txt | 103,641 | 102,889 | 752 | unchanged |
| stage1 / case_010.txt | 3,335 | 3,037 | 298 | unchanged |
| stage1 / case_012.txt | 4,013 | 3,763 | 250 | unchanged |
| stage2 / case_003.txt | 15,773 | 15,623 | 150 | unchanged |
| stage2 / case_023.txt | 2,029 | 1,904 | 125 | unchanged |
| stage1 / case_016.txt | 2,145 | 2,140 | 5 | unchanged |
| stage2 / case_024.txt | 6,878 | 6,873 | 5 | unchanged |
| stage2 / case_012.txt | 4,145 | 4,143 | 2 | unchanged |


## Engineering and acceptance risks

1. **P0 before promoting Repeat SOP**: in `source/src/synth_round91.cpp`, postprocessing is enclosed in `if (const char* r91env=std::getenv("UFUG_R91_POLICY"))`. Unconfigured execution stays in OFF mode. A production candidate must explicitly select the tested policy *without* relying on WSL-only environment variables, then be rebuilt and compared against the frozen experimental source in the supplied course evaluator.
2. Keep **R9.0** as a frozen rollback, and R9.1 repeat-SOP as a **new provisional quality candidate**, not a final scoring winner. Public Area and Delay are excellent, but runtime is mildly higher and the 50 hidden cases have not been observed.
3. The Library template bank is a valid research artifact. However, its potential **incremental** gain beyond Repeat SOP is at most 26 Area in the observed public candidate set using hindsight; jointly running modes can take more wall time and is not justified here. Library OFF by default.
4. Do **not** infer a true production time limit from local process wall time; evaluate using the course evaluator. All included public evaluations passed the actual evaluator.
5. The team-integrated Stage 2 source and Issue #2's BDD time-budget return are **not in this audit package**; cannot mark integration complete.

## Round 10 recommendation

- Do not start a large Round 9.2 resubstitution implementation based solely on these data. Preserve it as an unpursued proposal unless a small isolated hypothesis and independent correctness test demonstrate nonredundant improvement.
- Round 10.0: create an exact, no-flag `repeat_sop` candidate and run controlled official paired tests against frozen R9.0 and current R9.1 experimental SOP, including short-limited inputs. No claim of success until the same-source-default check passes.
- Round 10.1: obtain the **actual team-integrated Stage 2** source; only there test Issue #2 BDD budget return and memory fixes, with a fresh-checkout build.
- Round 10.2: complete public Stage1/2 test banks, new-function correctness tests, hard-limit stress, source-only submission contract, report and reproducibility.
- Maintain a simple fallback if the integrated solver is unstable: independently proven R9.0 and the postpass candidate. Avoid mixing novel logic mechanisms into the frozen submission without a clear gain.

## Data files

- `official_500_casewise.csv` — every course evaluator result.
- `summary.csv` — paired summary and runtimes.
- `paired_casewise_vs_frozen.csv` — 50 public cases across the three new passes.
- `oracle_counterfactual.csv` — clearly labeled hypothetical best-of-candidates result.

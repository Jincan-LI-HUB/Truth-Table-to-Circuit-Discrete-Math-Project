# Round 8.7 — Deep Audit & Round 9 Decision Protocol

Date: 2026-11-22. **Scope:** user-uploaded Round8.7 feedback; genuine official *public* evaluator reports, separate self-generated holdouts, frozen C++ sources. No hidden-test access or final-grading score is implied.

## A. Reproducible provenance

- Frozen R8.6 source SHA-256: `6d21a7d3cf80a8662f4f42a965e84c50d6cffcef7766a4d2dccf282c204078d8`.
- Frozen R8.5 source SHA-256: `fa0421e3fbb9d1058a3b389e00ba57c85e9ca0cf44e7f5cd2e4428545bb7d969`.
- Official evaluator SHA-256: `142361d7ce18bc47dea6a07538db79a588b3afbf446526c1d1246f4968b3d0ca`.
- Round8.7 uses 36 self-generated cases, 3 candidate policies and two order-reversed runs; 216 independent exhaustive checks and 300 genuine public-evaluator records.

## B. Official public benchmark: success, with a score caveat

| Policy | 100 records (2×50) | Area sum per 50-case run | Delay sum | Median runtime in ms (100 observations) |
|---|---:|---:|---:|---:|
| R8.6 baseline | 100 PASS / target met | 1,023,978 | 2,382 | 120.145 |
| R8.6 extra_sop | 100 PASS / target met | 1,021,134 | 2,382 | 133.371 |
| R8.5 reclaim | 100 PASS / target met | 1,021,134 | 2,382 | 133.319 |

- Extra SOP improves aggregated Area by 2,844 (0.2777% of baseline) without changing any per-case Delay in this paired evaluation. The Area improvements are concentrated in ten cases, especially Stage2 case005 (−2,235) and case003 (−440).
- Its per-case paired runtime geometric mean ratio vs baseline is about **1.0419** (4.19% slower). Thus it is **not a strict Area–Delay–Runtime Pareto dominance** and is not provably a better final grade: the PDF does not specify the score weights.
- Extra SOP and Reclaim have identical per-case Area/Delay on all public cases across both runs, consistent with R8.6 ablation: the +300 SOP root quota explains observed quality benefits; the extra reclaimed wall-clock allowance did not show an independent gain.

## C. Self-generated Holdout bank: semantic correctness, not a quality-generalization proof

- 216/216 exact truth-table equivalence, target met, and within the *generated* runtime caps. Each of 36 cases has identical netlist SHA-256 across two runs and across all three policies. Reported max RSS was about 37,864 KiB in the user's WSL measurement.
- **Zero cut work-limit and wall-limit events** in the bank, and all strategies have *identical Area and Delay* across cases. The extra SOP quota is therefore not meaningfully exercised on these tests.
- The generated target delay is either 140 or 170. The smallest observed target-delay margin is **108** units. This bank does not exercise near-critical delay constraints comparable to important public cases where Delay nearly equals Target.
- Short 100-ms runtime input cases in this bank have `n <= 14`. The challenging `n=20` cases are assigned 1,000 or 3,000 ms. Thus the bank does not validate `n=20` within 100 ms.
- **Input format defect:** `source/tools/generate_holdouts.py` puts `n m` on one line and each truth-table group on its own line. The course PDF instead specifies `n` on line 1, `m` on line 2, and all `2^n` groups space-separated on line 3. The current C++ parser and independent verifier are whitespace-tolerant, so Boolean equivalence results remain valid, but input-format conformity and I/O runtime representativeness are not established by these data.
- `--stress-only` has **not** been run in the supplied Round8.7 feedback ZIP: there is no `experiment/adversarial_stress/` output. Prior local 100-ms stress results are not official evaluator judgments.

## D. P0: submitted executable currently selects the wrong default policy

The frozen R8.6 source includes:

```cpp
const char* r86env_early = std::getenv("UFUG_R86_POLICY");
const std::string r86policy = r86env_early ? r86env_early : "baseline";
```

Research scripts explicitly set `UFUG_R86_POLICY=extra_sop`, whereas the grading contract promises only `<executable> <input_path> <output_path>` and does not set custom environment variables. Direct submission of the frozen source would therefore default to **baseline**, not the studied Extra SOP policy.

Prepared a **non-destructive candidate copy**, changing only the default string to `"extra_sop"`; frozen parent remains untouched, its SHA is checked. Resulting candidate source SHA: `d2cf83acbbc772dcfc07b476ba6d78ba1cde2847b71950b738e65cfdd0f5a317`. Compiled with `g++ -O2 -std=c++17 -pipe -DNDEBUG` and passed an independent exhaustive check on `holdout_016`. On the more complex public Stage2 case005, logged `R86_FINAL policy=extra_sop` with no environment policy set and with it explicitly set, with both netlists exhaustive-verified. Different netlist/Area across those two runs is expected under wall-clock search jitter, **not evidence that the policy selection differs**. This copy is a *preliminary backup candidate*, not a team-integrated, hidden-tested final submission.

## E. P1: a specific additional test is worth doing before algorithm changes

Use `prepare_r87_next_gate.py` to generate spec-conforming whitespace for the **same** 36 truth-table functions and 3 stress cases: it preserves every output token, cost and limit, changes only line layout, and refuses to overwrite frozen data. All 39 normalized files were checked for three-line header/truth-table conformance and exact token counts. The normalizer itself does **not** assert official-evaluator pass or perform a full after-normalization synthesis evaluation.

Then run the course evaluator on the canonicalized 100-ms stress cases, with the frozen R8.6 baseline and candidate default-Extra SOP. Analyze both official PASS/FAIL and actual runtime. These stress cases are deliberately adversarial: public Stage2 `n=20` cases had much larger runtime limits (10,000 ms) in the locally available official bank, so a custom `n=20,100 ms` failure alone does not imply a likely hidden grading failure.

## F. Round 9: controlled, new candidate-space research

**Order of work matters:**

1. **R9.0 / P0 Submission Safety Gate (do immediately).** No policy-specific shell environment assumed by the grading server. Prove a clean source-only build, default-policy identity, official public PASS, and identical mathematical constraints using the canonical input format. Keep Stage2 team's actual integrated executable separate from independent source experiments.
2. **R9.1 / 3–4-leaf Library Rewriting, not a full framework rewrite.** On an AIG/AND–OR–NOT DAG, collect small k-feasible cuts and compute exact k-bit Boolean signatures. Enumerate a bounded template library (including De Morgan, distributivity/factoring, and Shannon/MUX-inspired forms). All templates must map to AND2/OR2/NOT; XOR is not a native gate. Re-evaluate with per-case gate weights. A candidate is accepted only with equivalent cut truth, no cycle, valid full-DAG area, target delay constraints, and runtime budget.
3. **R9.2 / Resubstitution only if R9.1 demonstrates reusable opportunities.** Try available divisors with safe dependency ordering. If a divisor is not a pure function of the current cut leaves, a local k-input truth signature is not a sufficient proof: either restrict divisors to cut-leaf-expressible signals or use a globally valid proof before replacement. Account for shared-node MFFC removability and final full-DAG metric, not local gate count alone.
4. **Independent harder bank:** freeze generator/manifest *before* algorithm comparison. Build circuits intentionally rich in cut candidates, shared fanout, output interactions and tight delay. Separate a development set and a one-time lockbox; do not select winners by repeated lockbox tuning. Ensure strict PDF input formatting. Track `visited_roots`, cut-evaluated counts, accepted rewrites, reusable divisors, full Area/Delay, per-case runtime and tail quantiles, netlist hashes, RSS and official PASS.
5. **R10 / Team integration & freeze:** integrate only proven improvements; handle teammate's still-open integrated-BDD budget item and clean-checkout README; compile submitted source without extra environment variables, run official 50 public cases, an independent bank, and then freeze. Complete the required report and prepare the Q&A.

**Go / No-Go rule:** no new algorithm is merged unless correct on every generated and public case, target constraints preserved (or documented objective tradeoffs justified), hard runtime PASS maintained, and the change adds replicable quality improvement beyond increased runtime. If the local gain is confined to previously tuned public cases, or cannot be reproduced on a frozen hard bank, retain the frozen R8.6 extra-SOP fallback and proceed to integration. A runtime regression cannot be ignored because the rubric includes runtime as a scoring dimension but does not disclose weights.

**Timeline (planning, not a guarantee):** 2026-11-22/23 P0+stress conformity; Nov 23–26 library prototype + independent hard bank; Nov 27–28 optional resubstitution only if promising; Nov 29–Dec 2 team integration and report; Dec 3–4 freeze, regression, submission buffer (deadline Dec 4, 23:59).

## G. What NOT to conclude

- 216/216 self-generated checks are neither official hidden tests nor proof of quality generalization.
- Zero wall hits in easy holdouts does not imply deterministic behavior in complex official or hidden tests.
- A strictly smaller sum of area does not imply a higher grade when runtime/delay weights are unknown.
- An earlier `MEMORY_LIMIT` from a custom positive-RAM case is not an official grading blocker after the TA clarified no public or hidden case has a positive RAM cap; engineering RSS can still affect runtime and reliability.
- Frozen research source with `UFUG_R86_POLICY` flags is not automatically a submission-ready algorithm.

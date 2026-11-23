# Round 8.1 — Controlled Experimental Protocol

## A. Frozen reference and environmental control

Do not modify existing Round 7.2 or Round 8.0 folders. `bootstrap_round81.py` requires the SHA-256-frozen Round8.0 source `9ec7dc97161d3dc906dfad7960e0fc232b8e2cf0399908c6c4e99b756d8bacd8`. All C++ builds use `-O2 -std=c++17 -DNDEBUG`, single threaded by default. The official evaluator is `./evaluator` from project root; the runner copies it to an executable Linux temporary directory, avoiding /mnt/e permission quirks.

## B. Main factor ablations

Run the variants `r72` (frozen baseline), `r80_iterate`, `r81_sop`, `r81_shannon`, `r81_all`, `r81_branch`, `r81_strict`, `r81_reverse`, on Stage1 and Stage2 full 25 cases, in each of two reversed-order repetitions. `r81_sop`/`shannon`/`all` set `UFUG_R8_POLICY=off` to isolate cut effects. `r81_branch` enables Round8.0 upstream and selects among independent cut implementation branches. `r81_strict` requires no delay increase relative to baseline. `r81_reverse` places cut resynthesis before the Round8.0 pattern rewriter.

**No post-hoc per-case switches:** the `data/stage*` case names never influence solver branch selection. Gate costs, target delay, runtime limit and circuit DAG are allowed.

## C. Correctness and safety

Run `tests/test_cut_random.py` first: 180 seeded random DAGs × 4 exact-cut modes = 720 exhaustive semantic checks. Then full direct truth table verification on Stage2 `case_003`, `case_005`, `case_021`, `case_016` and Stage1 `case_020`. This direct-run verification is **not** a substitute for official evaluator scores; it ensures the optimizer has not introduced obvious Boolean errors. The evaluator enforces full legality and case runtime/RAM rules and is authoritative for public-case status.

## D. Measurements (mandatory)

Per case and variant: `status`, `target_met`, true weighted Area, true Delay, `runtime_ms`, declared runtime limit, and `case`. Cross-version comparisons use only cases with PASS in both variants. A case failed in the baseline is a failure recovery, not a fictitious infinite area ratio. Report Stage1 and Stage2 separately and jointly, with a `complete_area` flag. Use geometric mean of positive paired runtime ratios to avoid mixing ms and logarithmic improvement distributions; retain min/max/median and high-tail warning.

For variant A vs B, `delta_area=A_new-A_old`, `delta_delay=D_new-D_old`. A is Pareto dominant only if both deltas are ≤0 with at least one strict. A smaller Area with a longer delay is a genuine tradeoff. Delay target adherence and official functional PASS are distinct.

## E. Release gates

The research candidate is acceptable only if both stages are 25/25 PASS and target-met in both paired runs, with no new per-case area regressions under the area-priority branch. `r81_strict` separately checks delay non-regression; it need not have the same Area as area-priority. If no variant yields meaningful benefit after actual runtime, freeze R7.2 and retain R8.1 solely as research evidence. Hidden-case generality is not guaranteed by public tests.

## F. Feedback package and integrity

The shell script registers an EXIT trap before any build or evaluator call. It generates `Round8.1_Feedback_<timestamp>.zip` on success *and* failure, including `summary.json`, raw CSV, full stderr/stdout logs, case profiles, code snapshot, source hash manifest, research docs, and latest test transcript. It returns the evaluator failure status so the user cannot mistake a failed run for PASS. File hashes provide traceability, not correctness.

## G. Threats to validity

- Public benchmark overfitting (all development uses public cases).
- Machine/WSL runtime variability, first-run/cold-cache effects, and highly permissive runtime limits for some cases.
- Bounded root sample selection and cut enumeration policy may correlate with gate ID order.
- Partial truth-mask candidate generation is exact within the cut but not globally optimal.
- Official grading formula and hidden-case structure unknown.
- Independent source verifier confirms functional output but does not model RAM.
- Candidate order influences upstream synthesis under real-time cutoffs; hashes and paired runs are necessary.

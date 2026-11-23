#!/usr/bin/env python3
"""Reproduce Round 8.1 diagnostic tables from the exact uploaded feedback archive.
No scoring formula is assumed; local data are distinguished from official evaluator CSVs.
"""
import argparse, csv, hashlib, json, math, statistics, zipfile
from pathlib import Path
from collections import defaultdict

parser=argparse.ArgumentParser(description='Analyze Round 8.1 official evaluator feedback ZIP')
parser.add_argument('--feedback', type=Path, required=True)
parser.add_argument('--out', type=Path, default=Path('round81_audit_out'))
args=parser.parse_args()
ARCHIVE=args.feedback
OUT=args.out
OUT.mkdir(parents=True, exist_ok=True)
variants=['r72','r80_iterate','r81_sop','r81_shannon','r81_all','r81_branch','r81_strict','r81_reverse']
records={}
with zipfile.ZipFile(ARCHIVE) as z:
    for run in (1,2):
        for stage in ('stage1','stage2'):
            for variant in variants:
                name=f'official_run/run{run}_{stage}_{variant}.csv'
                rows=list(csv.DictReader(z.read(name).decode().splitlines()))
                assert len(rows)==25 and all(q['status']=='PASS' and q['target_met']=='yes' for q in rows)
                for q in rows:
                    for key in ('area','delay'):q[key]=int(q[key])
                    q['runtime_ms']=float(q['runtime_ms'])
                records[(run,stage,variant)]={row['case']:row for row in rows}
    summary=json.loads(z.read('official_run/summary.json'))

comparison=[]
summary_rows=[]
for run in (1,2):
 for stage in ('stage1','stage2'):
  base=records[(run,stage,'r72')]
  for variant in variants:
   curr=records[(run,stage,variant)]
   area_sum=sum(q['area'] for q in curr.values());delay_up=0;improved=0;adp_better=0;adp_worse=0;slower=0
   ratios=[]
   for case in sorted(base):
    a=curr[case];b=base[case];delta=a['area']-b['area'];dd=a['delay']-b['delay'];rr=a['runtime_ms']/b['runtime_ms'];adp=(a['area']*a['delay'])/(b['area']*b['delay'])
    improved+=delta<0;delay_up+=dd>0;adp_better+=adp<1-1e-12;adp_worse+=adp>1+1e-12;slower+=rr>1;ratios.append(rr)
    comparison.append({'run':run,'stage':stage,'case':case,'variant':variant,'area_baseline':b['area'],'area_candidate':a['area'],'area_delta':delta,'delay_baseline':b['delay'],'delay_candidate':a['delay'],'delay_delta':dd,'runtime_baseline_ms':b['runtime_ms'],'runtime_candidate_ms':a['runtime_ms'],'runtime_ratio':round(rr,6),'area_delay_product_ratio':round(adp,6),'pareto_dom_area_delay':int(delta<=0 and dd<=0 and (delta<0 or dd<0)), 'tradeoff':int(delta<0 and dd>0)})
   summary_rows.append({'run':run,'stage':stage,'variant':variant,'pass':25,'target_met':25,'total_area':area_sum,'area_saved':sum(b['area'] for b in base.values())-area_sum,'area_improved_cases':improved,'delay_regressed_cases':delay_up,'area_delay_product_improved_cases':adp_better,'area_delay_product_worsened_cases':adp_worse,'median_runtime_ms':round(statistics.median(a['runtime_ms'] for a in curr.values()),3),'total_runtime_ms':round(sum(a['runtime_ms'] for a in curr.values()),3),'runtime_gmean_ratio':round(math.exp(sum(math.log(q) for q in ratios)/len(ratios)),6),'runtime_slower_cases':slower})

with (OUT/'casewise_800_official_records.csv').open('w',newline='') as f:
 w=csv.DictWriter(f,fieldnames=list(comparison[0]));w.writeheader();w.writerows(comparison)
with (OUT/'stage_run_variant_summary.csv').open('w',newline='') as f:
 w=csv.DictWriter(f,fieldnames=list(summary_rows[0]));w.writeheader();w.writerows(summary_rows)

# Emphasize 6 real tradeoffs in the maximal-area branch; log-weight threshold is only a sensitivity model.
trade=[]
for stage in ('stage1','stage2'):
 a=records[(1,stage,'r81_reverse')];b=records[(1,stage,'r72')]
 for case in sorted(a):
  if a[case]['delay']<=b[case]['delay']:continue
  ar=a[case]['area']/b[case]['area'];dr=a[case]['delay']/b[case]['delay']
  t={'stage':stage,'case':case,'area_before':b[case]['area'],'area_after':a[case]['area'],'delay_before':b[case]['delay'],'delay_after':a[case]['delay'],'area_saved':b[case]['area']-a[case]['area'],'delay_increase':a[case]['delay']-b[case]['delay'],'adp_ratio':round(ar*dr,5),'log_weight_breakeven':round(-math.log(ar)/math.log(dr),4)}
  trade.append(t)
with (OUT/'six_delay_tradeoffs.csv').open('w',newline='') as f:
 w=csv.DictWriter(f,fieldnames=list(trade[0]));w.writeheader();w.writerows(trade)

# Summaries and candidate-path metrics from source. Never treat the hypothetical oracle as executable.
oracles={}
for run in (1,2):
 reverse=sum(rows['area'] for stage in ('stage1','stage2') for rows in records[(run,stage,'r81_reverse')].values())
 oracle=sum(min(records[(run,stage,v)][case]['area'] for v in variants) for stage in ('stage1','stage2') for case in records[(run,stage,'r72')])
 oracles[run]=(reverse,oracle)

ablation_by_run={}
for run in (1,2):
 ablation_by_run[run]={}
 for v in variants:
  selected=[s for s in summary_rows if s['run']==run and s['variant']==v]
  a=sum(r['total_area'] for r in selected)
  baseline=sum(s['total_area'] for s in summary_rows if s['run']==run and s['variant']=='r72')
  allratios=[];adpratios=[];delayplus=[];gains=[]
  for stage in ('stage1','stage2'):
   for case,r in records[(run,stage,v)].items():
    b=records[(run,stage,'r72')][case]
    allratios.append(r['runtime_ms']/b['runtime_ms']);adpratios.append((r['area']*r['delay'])/(b['area']*b['delay']))
    if r['delay']>b['delay']:delayplus.append((stage,case))
    gain=b['area']-r['area']
    if gain>0:gains.append((gain,stage,case))
  top5=sum(k for k,_,_ in sorted(gains,reverse=True)[:5]); area_gain=baseline-a
  ablation_by_run[run][v]={'area':a,'saved':area_gain,'better_cases':len(gains),'delay_regressions':len(delayplus),'runtime_gmean':math.exp(sum(math.log(z) for z in allratios)/len(allratios)),'adp_gmean':math.exp(sum(math.log(z) for z in adpratios)/len(adpratios)),'top5_gain':top5}

# Per-case Pareto selection from measured variants: upper bound on *observable* selection benefit (not attainable for free).
report=f'''# Round 8.1 — 2026-11-21 Official Feedback Postmortem

**Evidence source:** `{ARCHIVE.name}`; SHA-256 `{hashlib.sha256(ARCHIVE.read_bytes()).hexdigest()}`.  
**Observation unit:** 2 runs × 2 stages × 25 cases × 8 variants = **800 evaluator results**. All are PASS and all are Target Met.  
**Scope:** public benchmarks and same-host WSL2 evaluator, not hidden-case quality or official course grading formula.  
**Method:** inspect raw source CSVs, align by `(run,stage,case)`, compare each candidate to **the paired Round 7.2 run**; never infer area savings from failed-case omissions.

## 1. Executive decision

**Round 8.1 is validated as a structural synthesis research milestone, not as a confirmed score-optimal submission.**

- **Area exploration has materially improved:** `r81_reverse` saves 14,355 (run 1) / 14,263 (run 2) of 1,037,549 weighted-area units, with 30/50 improved cases and no per-case area regressions.
- **Delay and runtime remain real costs:** six area-improving cases have higher delay; all six produce worse *area×delay products*. Overall reverse geometric mean runtime factor is {ablation_by_run[1]['r81_reverse']['runtime_gmean']:.3f}× / {ablation_by_run[2]['r81_reverse']['runtime_gmean']:.3f}×. Area×delay geometric mean ratios are {ablation_by_run[1]['r81_reverse']['adp_gmean']:.5f} / {ablation_by_run[2]['r81_reverse']['adp_gmean']:.5f} (>1 means worse under this **hypothetical** proxy).
- **Strict policy is a small improvement at high runtime cost:** 303 / 305 total area savings, no delay regressions, runtime 2.53× / 2.39× baseline in pairwise geometric mean.
- **`r81_shannon` is a practical speed/quality contender:** 13,056 / 12,944 saved with runtime 1.57× / 1.51×, capturing over 90% of reverse's area savings in these runs but without claiming dominance in any actual grading formula.
- **Candidate choice is nontrivial:** `r81_all` is worse in total area than SOP, Shannon, and independent branch. This is consistent with structural path dependence under greedy mapping, not evidence that SOP and Shannon are mathematically incompatible.

## 2. Complete 50-case aggregate metrics

Baseline area total in each run: **1,037,549**. R8.0 iterative total: **1,037,494**.

| Variant | Run1 Area | Run2 Area | Mean saving | Cases improving (each run) | Delay regressions | Runtime geom. factor (Run1/Run2) |
|---|---:|---:|---:|---:|---:|---:|
'''
for v in variants:
 p=ablation_by_run[1][v];q=ablation_by_run[2][v]
 report+=f"| `{v}` | {p['area']:,} | {q['area']:,} | {(p['saved']+q['saved'])/2:,.1f} | {p['better_cases']}/{q['better_cases']} | {p['delay_regressions']}/{q['delay_regressions']} | {p['runtime_gmean']:.3f}× / {q['runtime_gmean']:.3f}× |\n"
report+='''
**Note:** The 800 official evaluator results are not 800 independent cases: they reuse 50 public cases under eight policies and two repetitions. Two repetitions are insufficient to make strong confidence-interval claims about performance stability.

## 3. Area–delay tradeoff diagnostic (`r81_reverse`, Run 1)

| Case | Area | Delay | Area saved | Increase in delay | ADP ratio | Max delay-vs-area log-weight ratio for preferring new candidate |
|---|---|---|---:|---:|---:|---:|
'''
for t in trade:
 report+=f"| {t['stage']}/{t['case']} | {t['area_before']:,}→{t['area_after']:,} | {t['delay_before']}→{t['delay_after']} | {t['area_saved']:,} | +{t['delay_increase']} | {t['adp_ratio']:.4f} | {t['log_weight_breakeven']:.3f} |\n"
report+=r'''
For sensitivity only, consider the hypothetical weighted-log objective

\[
J(G)=\alpha\log A(G)+\beta\log D(G),\quad \alpha,\beta\ge0.
\]

For a candidate that lowers area but raises delay, this proxy prefers it over the baseline only when

\[
\frac{\beta}{\alpha} < \frac{-\log(A_{\rm new}/A_{\rm old})}{\log(D_{\rm new}/D_{\rm old})}.
\]

**These are break-even sensitivities, NOT the course's official scoring rule.** Even when a case satisfies its target, increasing delay may still harm its actual score. Runtime must also be included when the official formula becomes available.

Six reverse tradeoff cases produce worse Area×Delay products (both repetitions). The overall Area×Delay geometric mean also worsens, despite area reductions in 30 cases. This demonstrates objective-function mismatch, not a universal defeat of cut resynthesis.

## 4. Distribution of area gains

'''
for run in (1,2):
 a=ablation_by_run[run]['r81_reverse']
 report+=f"- Run {run}: top five cases account for **{a['top5_gain']:,}/{a['saved']:,} = {100*a['top5_gain']/a['saved']:.2f}%** of all area savings. The other 25 improved cases contribute only **{a['saved']-a['top5_gain']:,}** units.\n"
report+='''
The top five Run 1 contributors are Stage2/005, Stage2/003, Stage1/010, Stage1/012, and Stage2/023. All five have delay regressions. Thus the bulk of area savings is tied to spending timing slack; the many smaller strict improvements are real but contribute little total area.

**Example area-only oracle over already measured variants:** choose, *after the fact*, the smallest area for each case across all eight configurations. This gives: 
'''
for run,(reverse,oracle) in oracles.items():
 report+=f'- Run {run}: oracle measured-variant area = **{oracle:,}**, vs `r81_reverse` **{reverse:,}**, an extra **{reverse-oracle}** area units.\n'
report+='''
This oracle is *not* an implementable single-run synthesis result: it assumes prior knowledge of all variant outputs and ignores the time spent to obtain them. It does suggest that simply evaluating more of the *same* branch portfolio may yield diminishing returns compared with reducing overhead and improving timing-aware local mapping.

## 5. Repeatability and search-budget sensitivity

- Frozen `r72` and `r80_iterate` produce exactly the same per-case Area/Delay in both WSL runs.
- `r81_reverse`: **2/50 cases differ in area** across runs, and one differs in delay. Stage1/012: 3,778 → 3,684 area; Stage2/005: 106,770/57 → 106,956/58.
- `r81_branch`: 2/50 cases differ in area; Stage2/005 varies by 651 units. `r81_shannon` varies in two cases; `r81_strict` in one.
- Diagnostic profiles for Stage2/005 record `budget_hit=1` on at least some cut branches and show hundreds of milliseconds of accumulated search (see `official_run/diagnostics/`). Together with wall-time cutoffs in source code this supports **timing-sensitive search truncation** as a plausible cause of run-to-run variation; it is not yet a controlled demonstration of the sole cause.

**Research intervention:** add work-unit determinism (root/cut/candidate counters) *alongside* absolute time caps. Measure fixed-work vs wall-time policies under paired WSL testing. A time-only scheduler may finish a different prefix of the candidate space depending on host scheduling.

## 6. Source-level algorithm reconstruction and limitations

Based on the delivered `source_snapshot/src/synth_round81.cpp` and `r81_cut.hpp`:

1. Once a valid Round7.2 / optional Round8.0 incumbent exists, for declared limit ≥1000 ms and elapsed time below 71% of the limit, attempt a bounded cut optimization stage. Sub-1000ms cases skip it.
2. Each local cut has at most four leaf variables; its exact truth function is computed as a 16-bit mask. Cut enumeration retains at most nine cut frontiers per node and samples at most 2500 candidate roots per branch.
3. Candidate families are greedy SOP/POS prime covers and several Shannon variable-order decompositions; “exact truth mask” does **not** mean globally exact minimum circuit synthesis.
4. Candidate admission accounts conservatively for private gate reclamation using fanout and rejects replacements exceeding propagated required-time bounds. It uses structural hashing while building candidate DAGs.
5. Whole-graph acceptance requires a valid netlist, lower actual weighted area (or equal area with lower delay), and delay at or below target. `branch_strict` additionally forbids delay regressions relative to its basegraph.
6. Branches are independent whole-graph trials (sop/shannon/all). The per-invocation cut stage has a 450 ms/16%-of-limit total cap, with per-branch 160 ms/6.5%-of-limit caps; these caps are heuristic and allow small overshoots. `reverse` additionally runs the Round8.0 structural rewrite after each cut branch.
7. Profiling on Stage2/003 shows SOP/Shannon/All yield distinct area/delay results. Stage2/021 logs tens of thousands of locally rejected timing candidates. These counters show active exploration and constraint filtering; they do not independently prove each rejected candidate was globally inferior.

**Correctness:** replacing a cut root by a functionally identical expression on its separating frontier preserves the entire output function by substitution. The official evaluator provides independent passing functional/timing tests for all 800 evaluations in this feedback; randomized local testing was also included in the previous delivery. This is *not* a formal proof of timing compliance on future hidden inputs.

**Efficiency caveats:** a larger cut-candidate menu can increase speculative allocations, local mapping overhead, and preprocessing cost even if the final accepted graph is small. Local private-reclaim cost is conservative and may miss opportunities that require several coupled rewrites. Bounds on cuts, roots and time imply incomplete search.

## 7. Recommendations for Round 8.2 — Timing-regularized, budget-aware resynthesis

Prioritize **better selection and better cost-efficiency**, not merely adding more transformations:

1. **Objective-aware Pareto archive:** preserve legal incumbents spanning (area, delay, observed time) where meaningful. Since output timing is computed exactly, use a delay cap relative to baseline (0, 1, a small amount, or full target slack) and compare across policies. Until scoring formula is known, retain an area-priority and a conservative delay-priority candidate.
2. **Work-metered cut scheduling:** deterministic cut/root budgets complemented by a hard wall-clock reserve. Instrument discovery counts, candidate rejection causes, true live-DAG gain, and candidate value per millisecond to identify costly low-yield search.
3. **Adaptive representation routing (not testcase-ID routing):** cut statistics and available required-time slack decide whether to attempt SOP, Shannon, or both. Preserve controls in ablation. Avoid deriving a general rule from the already repeatedly viewed 50 public cases.
4. **Reduce expensive branch duplication:** `r81_shannon` already retains around 90% of reverse's measured total area savings for roughly 1.5–1.6× instead of 2.45–2.51× runtime; incremental last-mile gain may not justify all parallel branch runs.
5. **Independent holdout:** freeze a fresh, deterministic suite *before* any tuning; include distinct function families, gate price skews, input/output counts, and timing limits. Record seeds, hashes, and all failed runs. Evaluate once after design decisions, clearly distinguishing this from 50 public development cases.
6. **Score sensitivity:** request the official syllabus grading formula. Absent a published formula, report the full Pareto frontier; do not invent weights or silently treat meeting the delay target as the only timing objective.

**Go/no-go for Round8.1:** GO as a verified research building block. NO to declaring `r81_reverse` universally best. Preserve R7.2 as fast safe fallback, `r81_shannon` as balanced exploratory control, and `r81_reverse` as area-oriented experimental control pending actual grading weights.

## 8. Threats to validity

- **Selection bias:** same 50 public cases have been reused repeatedly across prior rounds, so they are development data, not blind generalization evidence.
- **Temporal noise:** two paired passes do not establish reproducible runtime ordering with statistical confidence.
- **Infrastructure:** WSL2 + Windows-mounted project path differs from an Ubuntu 22.04 evaluator on native Linux; absolute timings are not portable.
- **Aggregation:** area sum and median runtime are descriptive, not necessarily the assignment's score function. Cases with different input/output counts and targets may be implicitly weighted differently.
- **Causality:** correlations between structure, timing budgets and gains do not identify a sole cause without controlled offline fixed-work experiments.
- **Optimality:** exact cut truth-table evaluation does not imply exact global optimality, even for fixed four-leaf boundaries (greedy gate realization).

## 9. Evidence map and reproduction

- `casewise_800_official_records.csv`: every observed case × variant × run, including area/delay/runtime, normalized runtime and proxy scores.
- `stage_run_variant_summary.csv`: per run, stage and variant aggregates.
- `six_delay_tradeoffs.csv`: detailed six-case area-delay sensitivity and log-weight break-even thresholds.
- `source_snapshot/*`: current Cut engine and baseline/rewriter implementation contained in the uploaded archive.
- `official_run/*.csv` + `*.log`: authoritative official evaluation raw data; `official_run/diagnostics/*.log` provide candidate-stage counters.

Every figure in this postmortem can be regenerated by the accompanying `build_audit.py` with the exact feedback ZIP at the recorded path. No background experiments or invented evaluator runs are included.
'''
(OUT/'Round8_1_Official_Postmortem_20261121.md').write_text(report,encoding='utf-8')
summary={'source_sha256':hashlib.sha256(ARCHIVE.read_bytes()).hexdigest(),'count_official_evaluations':sum(len(q) for q in records.values()),'all_pass':True,'all_target_met':True,'by_run':ablation_by_run,'measured_variant_area_only_oracle':oracles}
(OUT/'metrics_summary.json').write_text(json.dumps(summary,indent=2,ensure_ascii=False),encoding='utf-8')
zip_dest=OUT/'Round8_1_Postmortem_Evidence_20261121.zip'
with zipfile.ZipFile(zip_dest,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as zout:
 for file in [OUT/'Round8_1_Official_Postmortem_20261121.md',OUT/'casewise_800_official_records.csv',OUT/'stage_run_variant_summary.csv',OUT/'six_delay_tradeoffs.csv',OUT/'metrics_summary.json',OUT/'build_audit.py']:
  zout.write(file,arcname=file.name)
print('wrote',zip_dest,'size',zip_dest.stat().st_size)
print('report bytes',(OUT/'Round8_1_Official_Postmortem_20261121.md').stat().st_size)
print('summary',len(summary_rows),'casewise',len(comparison),'tradeoffs',len(trade))

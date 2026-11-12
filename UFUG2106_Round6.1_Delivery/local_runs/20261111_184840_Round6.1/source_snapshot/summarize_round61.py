#!/usr/bin/env python3
"""Generate local experiment summary from primary official Evaluator CSV evidence."""
import csv,json,statistics,sys
from pathlib import Path

def load(path):
 with Path(path).open(newline='') as f:return list(csv.DictReader(f))

def totals(path):
 rows=load(path)
 return {'cases':len(rows),'pass':sum(x['status']=='PASS' for x in rows),
         'target_met':sum(x['target_met']=='yes' for x in rows),
         'area_sum':sum(int(x['area']) for x in rows),
         'median_runtime_ms':round(statistics.median(float(x['runtime_ms']) for x in rows),3),
         'runtime_sum_ms':round(sum(float(x['runtime_ms']) for x in rows),3)}

def main(path):
 root=Path(path);out=root/'report_ready';out.mkdir(exist_ok=True)
 pairs={}
 for k in (1,2):
  pairs[str(k)]={mode:totals(root/f'benchmark/run{k}_{mode}.csv') for mode in ('reference','round61')}
 holdouts={}
 for group in ('holdout_round61_fresh_v1','holdout_round61_large_v1'):
  holdouts[group]={mode:totals(root/f'holdout/{group}_{mode}.csv') for mode in ('reference','round61')}
 left=load(root/'benchmark/run1_reference.csv');right={x['case']:x for x in load(root/'benchmark/run1_round61.csv')}
 rows=[]
 for x in left:
  y=right[x['case']];rows.append(dict(case=x['case'],reference_area=x['area'],round61_area=y['area'],area_saving=int(x['area'])-int(y['area']),
         reference_delay=x['delay'],round61_delay=y['delay'],reference_runtime_ms=x['runtime_ms'],round61_runtime_ms=y['runtime_ms']))
 with (root/'official_per_case.csv').open('w',newline='') as f:
  w=csv.DictWriter(f,rows[0].keys());w.writeheader();w.writerows(rows)
 summary={'official_pairs':pairs,'holdouts':holdouts,
    'per_case_area_improved':sum(x['area_saving']>0 for x in rows),
    'per_case_area_regressed':sum(x['area_saving']<0 for x in rows)}
 (root/'summary.json').write_text(json.dumps(summary,indent=2))
 a=statistics.mean(pairs[str(k)]['reference']['median_runtime_ms'] for k in (1,2))
 b=statistics.mean(pairs[str(k)]['round61']['median_runtime_ms'] for k in (1,2))
 delta_pct=100*(b/a-1)
 lines=['# Round 6.1 — WSL Local Reproduction Report','','## Two official paired runs','',
 '| Metric | Run 1: Reference | Run 1: Round 6.1 | Run 2: Reference | Run 2: Round 6.1 |',
 '|---|---:|---:|---:|---:|']
 for label,key in [('Functional PASS','pass'),('Target Met','target_met'),('Area Sum','area_sum'),('Median Runtime (ms)','median_runtime_ms'),('Sum Runtime (ms)','runtime_sum_ms')]:
  vals=[pairs[str(k)][m][key] for k,m in ((1,'reference'),(1,'round61'),(2,'reference'),(2,'round61'))]
  lines.append('| '+label+' | '+' | '.join(map(str,vals))+' |')
 lines += ['','Average of pairwise median runtimes: %.3f ms → %.3f ms (%+.2f%%).'%(a,b,delta_pct),
  'Pass/Target status is distinct from Area and synthesis runtime. Median runtime is not an amortized estimate.',
  'Both programs are rebuilt under the same compiler/environment. The order of the two executable modes is reversed in the second paired run.',
  'Candidate cutoff is based on wall-clock time, hence two successful runs can emit different equivalent netlists.','',
  '## New holdouts (not used for algorithm or threshold selection)','',
  '| Distribution | PASS | Target | Reference Area | R6.1 Area | Reference Median | R6.1 Median |',
  '|---|---:|---:|---:|---:|---:|---:|']
 for g,d in holdouts.items():
  x,y=d['reference'],d['round61']
  lines.append(f'| {g} | {y["pass"]}/{y["cases"]} | {y["target_met"]}/{y["cases"]} | {x["area_sum"]} | {y["area_sum"]} | {x["median_runtime_ms"]:.3f} | {y["median_runtime_ms"]:.3f} |')
 lines += ['','## Per-case official comparison','', '| Case | Reference Area | R6.1 Area | Saving | Delay baseline → R6.1 |','|---|---:|---:|---:|---:|']
 for x in rows:lines.append(f'| {x["case"]} | {x["reference_area"]} | {x["round61_area"]} | {x["area_saving"]} | {x["reference_delay"]} → {x["round61_delay"]} |')
 lines+=['','## Interpretation / stop condition','',
  'Freeze Round 5.1 as the default baseline. Round 6.1 is a bounded optional area-improvement branch. A default switch is justified only if an externally known scoring formula makes its small area improvement worthwhile.',
  'Correctness is supported by the official evaluator and by independent exhaustive/sampled netlist simulation. A finite synthetic holdout cannot prove performance on unknown Stage 2.',
  'This is a heuristic local rewriting engine, not exhaustive 4-input technology mapping, and its Area improvement is not guaranteed on every benchmark seed.',
  'See `benchmark/independent_verification.log`, `cases_sha256.txt`, `holdout_cases_sha256.txt`, `environment.txt`, saved outputs and the raw CSV files.', '']
 (out/'local_reproduction_report.md').write_text('\n'.join(lines))
 print(json.dumps({'first_area_saved':pairs['1']['reference']['area_sum']-pairs['1']['round61']['area_sum'],
  'median_reference_ms':round(a,3),'median_round61_ms':round(b,3),'runtime_pct':round(delta_pct,3),
  'pass_each_run':[(pairs[str(k)]['round61']['pass'],pairs[str(k)]['round61']['target_met']) for k in (1,2)]},indent=2))
if __name__=='__main__':main(sys.argv[1])

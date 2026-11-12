#!/usr/bin/env python3
"""Round 5.1: compare true paired local results, retaining both run orders."""
import csv,hashlib,json,statistics,sys
from pathlib import Path
root=Path(sys.argv[1])
reference="reference";candidate="round51"
def read(path):
 with path.open(newline='') as f:return {r['case']:r for r in csv.DictReader(f)}
def stat(rs):
 xs=[float(v['runtime_ms']) for v in rs.values()]
 return dict(pass_count=sum(v['status']=='PASS' for v in rs.values()),target_count=sum(v['target_met']=='yes' for v in rs.values()),area=sum(int(v['area']) for v in rs.values() if v['area']),median_runtime_ms=statistics.median(xs),sum_runtime_ms=sum(xs),max_runtime_ms=max(xs))
all_runs={};rows=[]
for run in (1,2):
 a=read(root/f'benchmark/run{run}_{reference}.csv');b=read(root/f'benchmark/run{run}_{candidate}.csv')
 assert len(a)==len(b)==25 and set(a)==set(b)
 all_runs[str(run)]={'round5':stat(a),'round51':stat(b)}
 for key in sorted(a):
  a0=a[key];b0=b[key]
  rows.append({'run':run,'case':key,'area_round5':a0['area'],'area_round51':b0['area'],'delay_round5':a0['delay'],'delay_round51':b0['delay'],'runtime_round5_ms':a0['runtime_ms'],'runtime_round51_ms':b0['runtime_ms'],'speedup_pct':round(100*(float(a0['runtime_ms'])-float(b0['runtime_ms']))/float(a0['runtime_ms']),3)})
keys=list(rows[0]);
with (root/'per_case_comparison.csv').open('w',newline='') as f:
 w=csv.DictWriter(f,fieldnames=keys);w.writeheader();w.writerows(rows)
ind=[]
for x in sorted((root/'benchmark'/'run1_reference_outputs').glob('*.txt')):
 y=root/'benchmark'/'run1_round51_outputs'/x.name
 ind.append(dict(case=x.name,identical=y.exists() and hashlib.sha256(x.read_bytes()).digest()==hashlib.sha256(y.read_bytes()).digest()))
summary={'runs':all_runs,'byte_identical_run1':sum(x['identical'] for x in ind),'per_case_byte_checks':ind}
for r in all_runs.values():
 for x in r.values():
  if x['pass_count']!=25 or x['target_count']!=25:summary['warning']='not all official cases pass and meet target'
summary['mean_of_run_medians']={key:statistics.mean(all_runs[str(i)][key]['median_runtime_ms'] for i in (1,2)) for key in ('round5','round51')}
a=summary['mean_of_run_medians'];summary['median_reduction_pct']=100*(a['round5']-a['round51'])/a['round5']
for subset in ('generated_110','holdout_v1','holdout_large_v1','stress'):
 f=root/f'holdout/{subset}_round51.csv'
 if f.exists():
  r=read(f);summary[subset]={'count':len(r),'pass_count':sum(x['status']=='PASS' for x in r.values()),'target_count':sum(x['target_met']=='yes' for x in r.values()),'area':sum(int(x['area']) for x in r.values() if x['area'])}
  g=root/f'holdout/{subset}_reference.csv'
  if g.exists():
   ref=read(g)
   summary[subset]['area_equal']=all(r[k]['area']==ref[k]['area'] for k in r)
   summary[subset]['delay_equal']=all(r[k]['delay']==ref[k]['delay'] for k in r)
(root/'summary.json').write_text(json.dumps(summary,indent=2))
md=['# Round 5.1 Local Reproduction Report','', 'Local measurements (both executables recompiled on this machine).','', '| Paired run | Round 5 median (ms) | Round 5.1 median (ms) | Round 5 area | Round 5.1 area |','|---|---:|---:|---:|---:|']
for i in (1,2):
 a,b=all_runs[str(i)]['round5'],all_runs[str(i)]['round51'];md.append(f'| {i} | {a["median_runtime_ms"]:.3f} | {b["median_runtime_ms"]:.3f} | {a["area"]:,} | {b["area"]:,} |')
md+=['',f'Mean-of-medians reduction: **{summary["median_reduction_pct"]:.2f}%**.',f'Run 1 netlist byte-identical: **{summary["byte_identical_run1"]}/25**.', '','This figure is descriptive, not a statistical confidence interval. Time-based candidate cutoffs may sometimes change netlists despite correct fixed-candidate transformations.','', '## Generalization check']
for subset in ('generated_110','holdout_v1','holdout_large_v1','stress'):
 if subset in summary:
  x=summary[subset];md.append(f'- {subset}: {x["pass_count"]}/{x["count"]} functional PASS; {x["target_count"]}/{x["count"]} target met; area_equal={x.get("area_equal","not compared")}; delay_equal={x.get("delay_equal","not compared")}.')
md+=['', '## Archival notes','', 'Evaluator logs, official CSVs, saved circuits, compiler and source hashes, independent verification and source snapshot are retained outside `report_ready/`, alongside this report.','', 'Stage 2 remains unobserved. This test set does not establish zero overfitting or universal performance improvement.']
(root/'report_ready/local_reproduction_report.md').write_text('\n'.join(md)+'\n')
print(json.dumps({k:summary[k] for k in ('mean_of_run_medians','median_reduction_pct','byte_identical_run1')},indent=2))

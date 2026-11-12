#!/usr/bin/env python3
"""Generate Round 6.0 local-run report with traceable paired CSV evidence."""
import csv, json, statistics, sys
from pathlib import Path

def load(p):
 with p.open(newline='') as f:return list(csv.DictReader(f))

def main(path):
 root=Path(path); bench=root/'benchmark';g=root/'holdout'; report=root/'report_ready'
 report.mkdir(exist_ok=True)
 def stats(file):
  a=load(file);return {'pass':sum(x['status']=='PASS' for x in a),'target':sum(x['target_met']=='yes' for x in a),'cases':len(a),'area':sum(int(x['area']) for x in a),'median_ms':statistics.median(float(x['runtime_ms']) for x in a),'sum_ms':sum(float(x['runtime_ms']) for x in a)}
 summary={'official':{},'holdouts':{}}
 for pair in (1,2):
  summary['official'][f'pair{pair}']={name:stats(bench/f'run{pair}_{name}.csv') for name in ('reference','round60')}
 for group in ('holdout_round60_v1','previous_holdout_v1','previous_holdout_large_v1'):
  summary['holdouts'][group]={name:stats(g/f'{group}_{name}.csv') for name in ('reference','round60')}
 r=load(bench/'run1_reference.csv');v=load(bench/'run1_round60.csv');idx={x['case']:x for x in v}
 cases=[]
 for a in r:
  b=idx[a['case']]
  cases.append({'case':a['case'],'reference_area':int(a['area']),'round60_area':int(b['area']),'saving':int(a['area'])-int(b['area']),'reference_delay':int(a['delay']),'round60_delay':int(b['delay']),'reference_runtime_ms':float(a['runtime_ms']),'round60_runtime_ms':float(b['runtime_ms'])})
 with (root/'official_per_case.csv').open('w',newline='') as f:
  dw=csv.DictWriter(f,cases[0].keys());dw.writeheader();dw.writerows(cases)
 summary['strict_area_reductions']=sum(x['saving']>0 for x in cases)
 summary['strict_area_regressions']=sum(x['saving']<0 for x in cases)
 summary['netlist_equal_count']=sum((bench/'run1_reference_outputs'/(x['case'].replace('.txt','.output.txt'))).read_bytes()==(bench/'run1_round60_outputs'/(x['case'].replace('.txt','.output.txt'))).read_bytes() for x in cases)
 (root/'summary.json').write_text(json.dumps(summary,indent=2))
 x=summary['official']['pair1']; y=summary['official']['pair2'];
 med_base=statistics.mean([x['reference']['median_ms'],y['reference']['median_ms']]);med_new=statistics.mean([x['round60']['median_ms'],y['round60']['median_ms']])
 out=['# Round 6.0 — WSL local reproduction','',
 '## Acceptance','',
 f'- Paired runs: 2; reference and Round 6.0 tested in alternating orders.',
 f'- Official functional PASS: {x["round60"]["pass"]}/{x["round60"]["cases"]} and {y["round60"]["pass"]}/{y["round60"]["cases"]}.',
 f'- Official delay targets: {x["round60"]["target"]}/{x["round60"]["cases"]} and {y["round60"]["target"]}/{y["round60"]["cases"]}.',
 f'- Area sums: {x["reference"]["area"]} → {x["round60"]["area"]} in run 1; {y["reference"]["area"]} → {y["round60"]["area"]} in run 2.',
 f'- Median runtime averaged across the two runs: {med_base:.3f} ms → {med_new:.3f} ms ({100*(med_new/med_base-1):+.2f}%).',
 f'- First-run outputs byte-identical: {summary["netlist_equal_count"]}/25 (rewriting should change some outputs).',
 '', '## Holdout distributions','', '| Group | Functional PASS | Target Met | Area before → after | Median before → after (ms) |','|---|---:|---:|---:|---:|']
 for group, vals in summary['holdouts'].items():
  a,b=vals['reference'],vals['round60']
  out.append(f'| {group} | {b["pass"]}/{b["cases"]} | {b["target"]}/{b["cases"]} | {a["area"]} → {b["area"]} | {a["median_ms"]:.3f} → {b["median_ms"]:.3f} |')
 out+=['','## Area improvement per official case','','| Case | Baseline Area | Round 6.0 Area | Saving | Delay baseline → new |','|---|---:|---:|---:|---:|']
 for c in cases:out.append(f'| {c["case"]} | {c["reference_area"]} | {c["round60_area"]} | {c["saving"]} | {c["reference_delay"]} → {c["round60_delay"]} |')
 out+=['', '## Interpretation','',
 'This prototype is a bounded post-mapping Cut Rewriter. It is not an optimal 4-input Boolean synthesizer.',
 'It ranks local candidates using a conservative private-cone cost estimate and makes its final decision using complete, exact Gate Area and critical-path Delay.',
 'Runtime is a cost of the synthesis procedure, not the circuit delay. If the extra Area reduction is not worth the time, keep the frozen Round 5.1 executable.',
 'The new 40-case holdout functions were fixed before formal performance measurements; their input-line encoding was corrected without altering the Boolean functions.',
 'The prior 96-case suite is reused from Round 5.1; neither collection guarantees generalization to hidden Stage 2.',
 '', '## Independent evidence','', 'See `benchmark/independent_verification.log` and the CSVs/logs in this local run.','']
 (report/'local_reproduction_report.md').write_text('\n'.join(out))
 print(json.dumps({'reference_median_ms':med_base,'round60_median_ms':med_new,'area_before':x['reference']['area'],'area_after':x['round60']['area'],'netlist_equal':summary['netlist_equal_count'],'holdouts':summary['holdouts']},indent=2))
if __name__=='__main__':main(sys.argv[1])

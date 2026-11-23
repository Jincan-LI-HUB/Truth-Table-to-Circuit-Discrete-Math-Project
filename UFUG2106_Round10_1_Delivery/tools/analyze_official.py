#!/usr/bin/env python3
"""No unadvertised score formula. Only paired observations and Pareto deltas."""
from pathlib import Path
from collections import defaultdict
import argparse,csv,json,math,statistics

def rows(path):
 with path.open(newline='') as f:return list(csv.DictReader(f))
def main():
 p=argparse.ArgumentParser();p.add_argument('--official-dir',type=Path,required=True);a=p.parse_args()
 d=a.official_dir
 allobs={};configs=set()
 for path in d.glob('stage?_run*_*.csv'):
  parts=path.stem.split('_',2)
  if len(parts)!=3:continue
  stage,run,policy=parts
  configs.add(policy)
  for v in rows(path):allobs[stage,run,policy,v['case']]=v
 baseline='r100_frozen'
 if baseline not in configs:raise RuntimeError('Missing frozen R10 baseline')
 paired=[]
 for (stage,run,policy,case),v in sorted(allobs.items()):
  if policy==baseline:continue
  base=allobs.get((stage,run,baseline,case))
  if base is None:raise RuntimeError(f'Missing paired baseline {stage} {run} {case}')
  if base.get('status')!='PASS' or v.get('status')!='PASS':
   paired.append(dict(stage=stage,run=run,case=case,policy=policy,status=v.get('status'),area_saved='',delay_delta='',runtime_ratio=''))
   continue
  t0=float(base['runtime_ms']);t1=float(v['runtime_ms'])
  paired.append(dict(stage=stage,run=run,case=case,policy=policy,status=v.get('status'),area_saved=int(base['area'])-int(v['area']),delay_delta=int(v['delay'])-int(base['delay']),runtime_ratio=round(t1/t0,6) if min(t0,t1)>0 else ''))
 if not paired:raise RuntimeError('Missing paired rows')
 with (d/'paired_runtime_area_delay.csv').open('w',newline='') as f:
  w=csv.DictWriter(f,fieldnames=list(paired[0]));w.writeheader();w.writerows(paired)
 summary=[]
 for pol in sorted(configs-{baseline}):
  vals=[v for v in paired if v['policy']==pol]
  ratios=[float(v['runtime_ratio']) for v in vals if v['runtime_ratio']!='']
  summary.append(dict(policy=pol,paired=len(vals),improved_cases=sum(isinstance(v['area_saved'],int) and v['area_saved']>0 for v in vals),regressed_cases=sum(isinstance(v['area_saved'],int) and v['area_saved']<0 for v in vals),area_saved_total=sum(v['area_saved'] for v in vals if isinstance(v['area_saved'],int)),delay_delta_total=sum(v['delay_delta'] for v in vals if isinstance(v['delay_delta'],int)),runtime_geom_ratio=round(math.exp(statistics.mean(math.log(r) for r in ratios)),6) if ratios else '',runtime_median_ratio=round(statistics.median(ratios),6) if ratios else '',runtime_95pct_ratio=round(sorted(ratios)[min(len(ratios)-1,int(.95*len(ratios)))],6) if ratios else ''))
 with (d/'paired_policy_summary.csv').open('w',newline='') as f:
  w=csv.DictWriter(f,fieldnames=list(summary[0]));w.writeheader();w.writerows(summary)
 (d/'INTERPRETATION.txt').write_text('All numbers compare paired cases within a specific official run; negative area_saved means regression. Runtime geometric ratio is a casewise multiplicative summary, not the course grading function. Area sums are not normalized per instance and cannot establish final score.\n')
 for x in summary:print('PAIRED_AUDIT',x['policy'],'area_saved',x['area_saved_total'],'delay_delta',x['delay_delta_total'],'runtime_ratio',x['runtime_geom_ratio'],flush=True)
if __name__=='__main__':main()

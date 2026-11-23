#!/usr/bin/env python3
"""ONE-SHOT synthetic holdout test; hashes frozen before evaluating; no retuning."""
from pathlib import Path
import csv,subprocess,os,hashlib,json,time,statistics
P=Path(__file__).resolve().parents[1];R=P.parent;H=P/'evidence/holdout_structured_v2'
manifest=json.loads((H/'FROZEN_MANIFEST.json').read_text())
for name,dig in manifest['cases'].items():
 if hashlib.sha256((H/name).read_bytes()).hexdigest()!=dig:raise RuntimeError('holdout hash drift '+name)
C=[('r72',R/'UFUG2106_Round7_2_Delivery/build/synth_round72',{}),
   ('r82_fast_area',P/'build/synth_round82',{'UFUG_R82_POLICY':'fast_area','UFUG_R8_POLICY':'off'}),
   ('r82_fast_adp',P/'build/synth_round82',{'UFUG_R82_POLICY':'fast_adp','UFUG_R8_POLICY':'off'}),
   ('r82_dual_area',P/'build/synth_round82',{'UFUG_R82_POLICY':'dual_area','UFUG_R8_POLICY':'off'})]
outputs=H/'netlists';outputs.mkdir(exist_ok=True)
rows=[]
for f in sorted(H.glob('structured_*.txt')):
 for label,program,e in C:
  net=outputs/(f.stem+'_'+label+'.netlist');env=os.environ.copy();env.update(e)
  for var in ('UFUG_R82_POLICY','UFUG_R8_POLICY','UFUG_R81_POLICY'):
   if var not in e:env.pop(var,None)
  t=time.perf_counter();p=subprocess.run([str(program),str(f),str(net)],env=env,capture_output=True,text=True,timeout=60)
  dt=(time.perf_counter()-t)*1000
  if p.returncode:raise RuntimeError(f'{f.name}:{label} synth failed: {p.stderr[-200:]}')
  test=subprocess.run([str(P/'build/verify_exhaustive'),str(f),str(net)],capture_output=True,text=True,timeout=60)
  if test.returncode:raise RuntimeError(f'{f.name}:{label} equivalent failed: {test.stderr[-200:]}')
  import re
  met=re.search(r'area=(\d+) delay=(\d+) target=(\d+)',test.stdout)
  assert met
  a,d,target=map(int,met.groups())
  rows.append({'case':f.name,'variant':label,'area':a,'delay':d,'target':target,
               'target_met':d<=target,'runtime_ms_nonofficial':round(dt,4),'exact_assignments':1<<int(f.read_text().split()[0])})
with (H/'structured_results.csv').open('w',newline='') as file:
 w=csv.DictWriter(file,list(rows[0]));w.writeheader();w.writerows(rows)
base={x['case']:x for x in rows if x['variant']=='r72'}
summary={}
for label,*_ in C:
 sub=[x for x in rows if x['variant']==label]
 summary[label]={'area_sum':sum(x['area'] for x in sub),'target_met':sum(x['target_met'] for x in sub),
                 'median_ms_nonofficial':round(statistics.median(x['runtime_ms_nonofficial'] for x in sub),3),
                 'area_better_than_r72':sum(x['area']<base[x['case']]['area'] for x in sub),
                 'area_regression':sum(x['area']>base[x['case']]['area'] for x in sub)}
(H/'structured_summary.json').write_text(json.dumps(summary,indent=2)+'\n')
print(json.dumps(summary,indent=2))

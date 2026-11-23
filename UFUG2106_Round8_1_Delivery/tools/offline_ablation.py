#!/usr/bin/env python3
"""Optional exact offline cut experiment, independent of official evaluator.
Reconstruct R7.2 netlists from input truth tables, then test SOP/Shannon/mixed.
This does not claim an official benchmark score.
"""
import argparse,csv,datetime,os,subprocess,time
from pathlib import Path
H=Path(__file__).resolve().parents[1];ROOT=H.parent
p=argparse.ArgumentParser();p.add_argument('--stage',choices=['stage1','stage2'],default='stage2')
p.add_argument('--limit-cases',type=int,default=25)
a=p.parse_args();folder=ROOT/'data'/a.stage
r72=ROOT/'UFUG2106_Round7_2_Delivery/build/synth_round72'
opt=H/'build/optimize_cut';verify=H/'build/verify_exhaustive'
for path in [r72,opt,verify,folder]:
 if not path.exists():p.error('Missing '+str(path))
stamp=datetime.datetime.now().strftime('%Y%m%d_%H%M%S_%f');out=H/'results'/('offline_'+a.stage+'_'+stamp);out.mkdir(parents=True)
items=[]
def check(case,net):
 ck=subprocess.run([str(verify),str(case),str(net)],capture_output=True,text=True,timeout=100)
 if ck.returncode:raise RuntimeError(f'FAIL equivalence: {case} {net}: {ck.stdout} {ck.stderr}')
 return {x.split('=')[0]:int(x.split('=')[1]) for x in ck.stdout.split() if '=' in x and x.split('=')[1].isdigit()}
for case in sorted(folder.glob('case_*.txt'))[:a.limit_cases]:
 ref=out/(case.stem+'_r72.netlist');t0=time.perf_counter()
 b=subprocess.run([str(r72),str(case),str(ref)],capture_output=True,text=True,timeout=110)
 if b.returncode:raise RuntimeError(f'Baseline failed {case}: {b.stderr[-500:]}')
 orig=check(case,ref)
 for mode in ['sop','shannon','all','choices']:
  dest=out/(case.stem+'_'+mode+'.netlist');t1=time.perf_counter()
  z=subprocess.run([str(opt),str(case),str(ref),str(dest),mode],capture_output=True,text=True,timeout=100)
  if z.returncode:raise RuntimeError(f'Cut failed {case} {mode}: {z.stderr[-500:]}')
  got=check(case,dest)
  items.append({'case':case.name,'stage':a.stage,'mode':mode,'area_before':orig['area'],
   'area_after':got['area'],'delta_area':got['area']-orig['area'],
   'delay_before':orig['delay'],'delay_after':got['delay'],'target':got['target'],
   'cut_wall_ms':round((time.perf_counter()-t1)*1000,3),'truth_rows_verified':got['exact_assignments']})
  if got['area']<orig['area']:print(case.name,mode,orig['area'],'->',got['area'],flush=True)
if items:
 with (out/'OFFLINE_ABLATION.csv').open('w',newline='') as f:
  w=csv.DictWriter(f,list(items[0]));w.writeheader();w.writerows(items)
 print('OFFLINE RESULTS:',out,'cases',len({x['case'] for x in items}))
 for mode in ['sop','shannon','all','choices']:
  q=[x for x in items if x['mode']==mode]
  print(mode,'saved_area',-sum(x['delta_area'] for x in q),'improved',sum(x['delta_area']<0 for x in q))

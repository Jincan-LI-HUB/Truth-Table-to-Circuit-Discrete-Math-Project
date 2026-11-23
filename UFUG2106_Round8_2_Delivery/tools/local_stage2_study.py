#!/usr/bin/env python3
"""NON-OFFICIAL developmental exhaustive Stage2 experiment (not blind holdout)."""
from pathlib import Path
import csv,os,re,subprocess,time,concurrent.futures,hashlib,json
P=Path(__file__).resolve().parents[1];ROOT=P.parent
CASE_DIR=ROOT/'round7_local_data/stage2'
if not CASE_DIR.exists():CASE_DIR=ROOT/'data/stage2'
PROG=P/'build/synth_round82';CHECK=P/'build/verify_exhaustive'
DEST=P/'evidence/local_stage2';DEST.mkdir(exist_ok=True,parents=True)
configs=[('stride_area','fast_area','stride',False),('priority_area','fast_area','priority',True),
         ('priority_adp','fast_adp','priority',False),('priority_slack','fast_slack','priority',False),
         ('priority_dual_area','dual_area','priority',True),('priority_dual_strict','dual_strict','priority',False)]
cases=sorted(CASE_DIR.glob('case_*.txt'))
if len(cases)!=25:raise SystemExit(f'Stage2 incomplete: {len(cases)} files')
def run(item):
 case,(label,policy,sampling,verify)=item
 out=DEST/(case.stem+'_'+label+'.netlist')
 env=os.environ.copy();env.update(UFUG_R8_POLICY='off',UFUG_R81_POLICY='off',UFUG_R82_POLICY=policy,
                             UFUG_R82_SAMPLING=sampling,UFUG_R82_ROOT_CAP='1500',UFUG_R82_PROFILE='1')
 t=time.perf_counter()
 pr=subprocess.run([str(PROG),str(case),str(out)],env=env,capture_output=True,text=True,timeout=90)
 elapsed=(time.perf_counter()-t)*1000
 if pr.returncode:raise RuntimeError(f'{case.name} {label} synthesis: {pr.stderr[-600:]}')
 text=pr.stdout+pr.stderr
 (DEST/(case.stem+'_'+label+'.log')).write_text(text)
 match=re.search(r'completed=\d+ chosen=\d+ area=(\d+) delay=(\d+)',text)
 if not match:raise RuntimeError(f'{case.name} {label} cannot parse metrics: {text[-500:]}')
 area,delay=map(int,match.groups());n=int(case.open().readline().split()[0]);full=False
 if verify:
  ck=subprocess.run([str(CHECK),str(case),str(out)],capture_output=True,text=True,timeout=90)
  if ck.returncode:raise RuntimeError(f'{case.name} {label} exhaustive check FAIL: {ck.stderr[-400:]}')
  full=True
 return {'case':case.name,'label':label,'policy':policy,'sampling':sampling,'area':area,'delay':delay,
         'elapsed_ms_unofficial':round(elapsed,3),'n':n,'full_truth_verified':full,
         'netlist_sha256':hashlib.sha256(out.read_bytes()).hexdigest(),
         'budget_hit':int('budget_hit=1' in text)}
jobs=[(case,config) for case in cases for config in configs]
rows=[]
with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:
 futs=[pool.submit(run,x) for x in jobs]
 for i,f in enumerate(concurrent.futures.as_completed(futs),1):
  rows.append(f.result())
  if i%15==0:print(f'local stage2 study {i}/{len(jobs)} completed',flush=True)
rows.sort(key=lambda r:(r['case'],r['label']))
with (DEST/'stage2_local_ablation.csv').open('w',newline='') as f:
 w=csv.DictWriter(f,list(rows[0]));w.writeheader();w.writerows(rows)
summary={'comparison_type':'nonofficial_same_container_study','configurations':{},'fully_verified_netlists':sum(r['full_truth_verified'] for r in rows)}
for label,*_ in configs:
 sub=[r for r in rows if r['label']==label]
 summary['configurations'][label]={'cases':len(sub),'area_sum':sum(r['area'] for r in sub),
                 'median_ms_unofficial':sorted(r['elapsed_ms_unofficial'] for r in sub)[len(sub)//2],
                 'delay_sum':sum(r['delay'] for r in sub),'budget_hits':sum(r['budget_hit'] for r in sub)}
(DEST/'stage2_local_summary.json').write_text(json.dumps(summary,indent=2)+'\n')
print(json.dumps(summary,indent=2),flush=True)

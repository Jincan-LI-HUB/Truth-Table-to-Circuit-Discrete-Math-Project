#!/usr/bin/env python3
import argparse,subprocess,csv,os,time,hashlib
from pathlib import Path
H=Path(__file__).resolve().parents[1]
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def main():
 p=argparse.ArgumentParser();p.add_argument('--out',type=Path,required=True);p.add_argument('--quick',action='store_true');a=p.parse_args()
 a.out.mkdir(parents=True,exist_ok=True)
 configs=[('frozen','synth_round100_frozen',{}),('trial_default','synth_round101',{}),('trial_cap40','synth_round101',{'UFUG_R91_ROOT_CAP':'40'}),('trial_cap80','synth_round101',{'UFUG_R91_ROOT_CAP':'80'}),('trial_budget45','synth_round101',{'UFUG_R101_BUDGET_CAP_MS':'45'}),('trial_off','synth_round101',{'UFUG_R91_POLICY':'off'}),('trial_submission','trial_submission',{})]
 cases=list(sorted((H/'fixtures').glob('*.txt')))
 if a.quick:cases=[x for x in cases if x.name.startswith(('hard_003','holdout_016','stress_001'))]
 rows=[]
 for case in cases:
  for label,exe,extra in configs:
   output=a.out/(case.stem+'_'+label+'.net')
   env=os.environ.copy()
   for k in list(env):
    if k.startswith(('UFUG_','R90_','R10_')):env.pop(k)
   env.update(extra);env['UFUG_R91_PROFILE']='1'
   t=time.monotonic()
   r=subprocess.run([str(H/'build'/exe),str(case),str(output)],env=env,capture_output=True,text=True,timeout=35)
   ms=(time.monotonic()-t)*1000
   (a.out/(case.stem+'_'+label+'.log')).write_text(r.stderr+'\n'+r.stdout)
   v=subprocess.run([str(H/'build/verify_exhaustive'),str(case),str(output)],capture_output=True,text=True,timeout=35) if r.returncode==0 and output.is_file() else None
   if r.returncode or v is None or v.returncode:raise RuntimeError(f'EXACT_FAIL {case.name} {label} synth={r.returncode} verify={v.returncode if v else "-"}')
   import re
   mt=re.search(r'area=(\d+) delay=(\d+) target=(\d+)',v.stdout)
   assert mt,(case,label,v.stdout)
   area,delay,target=map(int,mt.groups())
   if delay>target:raise RuntimeError(f'DELAY_FAIL {case.name} {label}: {delay}>{target}')
   rows.append(dict(case=case.name,config=label,area=area,delay=delay,target=target,wall_ms=round(ms,3),net_sha=sha(output)))
  print('EXACT',case.name,f'{len(configs)}/{len(configs)}',flush=True)
 with (a.out/'local_exact.csv').open('w',newline='') as f:
  wr=csv.DictWriter(f,fieldnames=list(rows[0]));wr.writeheader();wr.writerows(rows)
 print('R101_LOCAL_EXACT_PASS',len(rows),'fully exhaustive verified netlists',flush=True)
if __name__=='__main__':main()

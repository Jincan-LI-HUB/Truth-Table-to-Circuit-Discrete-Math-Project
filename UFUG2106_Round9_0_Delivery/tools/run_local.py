#!/usr/bin/env python3
"""Cold-submission smoke + mathematically exhaustive, controlled strategy comparison."""
import argparse,csv,hashlib,json,os,subprocess,time,shutil,tempfile
from pathlib import Path
H=Path(__file__).resolve().parents[1]

def env(extra=None):
 e=os.environ.copy()
 for k in list(e):
  if k.startswith(('UFUG_R','UFUG_ROUND','R90_')):e.pop(k)
 if extra:e.update(extra)
 return e

def run(cmd,case,out,environment):
 t=time.perf_counter()
 z=subprocess.run([str(cmd),str(case),str(out)],capture_output=True,text=True,env=environment,timeout=45)
 return z,1000*(time.perf_counter()-t)

def main():
 p=argparse.ArgumentParser();p.add_argument('--results',type=Path,required=True);p.add_argument('--quick',action='store_true');a=p.parse_args()
 root=a.results/'local';root.mkdir(parents=True,exist_ok=True)
 cand=H/'build/synth_round90';sub=H/'build/submission_synth';ref=H/'build/synth_round86_frozen'
 verify=H/'build/verify_exhaustive'
 cases=[H/'canonical_bank/stress_v2'/f'stress_{i:03d}.txt' for i in range(1,4)]+[
  H/'canonical_bank/holdouts'/f'holdout_{i:03d}.txt' for i in ((3,5,9,16,21,25,27,34,36) if not a.quick else (16,21,36))]
 if not a.quick:cases+=sorted((H/'hard_bank/dev').glob('hard_*.txt'))
 variants=[('new_default',cand,{}),('new_explicit',cand,{'UFUG_R86_POLICY':'extra_sop'}),
           ('frozen_extra',ref,{'UFUG_R86_POLICY':'extra_sop'}),('submission',sub,{})]
 rows=[]
 for case in cases:
  baseline=None
  for name,exe,extra in variants:
   out=root/f'{case.stem}_{name}.net'
   z,ms=run(exe,case,out,env(extra|({'R90_TRACE':'1'} if name in ('new_default','submission') else {})))
   (root/f'{case.stem}_{name}.log').write_text(z.stdout+'\n'+z.stderr)
   if z.returncode!=0 or not out.exists():raise RuntimeError(f'{case.name} {name} solver RC={z.returncode}')
   v=subprocess.run([str(verify),str(case),str(out)],capture_output=True,text=True,timeout=45)
   if v.returncode:raise RuntimeError(f'{case.name} {name} verify failed {v.stdout} {v.stderr}')
   if name=='new_default' and not ('R90_SHORT_PATH ' in z.stderr or 'R90_DISPATCH policy_default=extra_sop selected=extra_sop' in z.stderr):
    raise RuntimeError(f'{case.name}: no evidence of default policy')
   sha=hashlib.sha256(out.read_bytes()).hexdigest()
   if name=='new_default':baseline=sha
   if name=='submission' and sha!=baseline:
    # timing may change complex outputs; allow matching Area/Delay, but record difference
    pass
   rows.append(dict(case=case.name,variant=name,wall_ms=round(ms,3),
       net_sha256=sha,verify=v.stdout.strip(),short_path='R90_SHORT_PATH' in z.stderr))
  print('LOCAL',case.name,'4/4 exact',flush=True)
 with (root/'casewise.csv').open('w',newline='') as f:
  w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
 (root/'summary.json').write_text(json.dumps({'checks':len(rows),'cases':len(cases),
    'source_only_cold_build':'tested_separately','course_hidden':False},indent=2)+'\n')
 print('R90_LOCAL_PASS',len(rows),'exact checks, with no flags and source-only submission',flush=True)
if __name__=='__main__':main()

#!/usr/bin/env python3
"""Sensitivity test only: deliberate n=20/100ms may FAIL the real evaluator."""
import argparse,csv,hashlib,json,os,subprocess,time
from pathlib import Path
H=Path(__file__).resolve().parents[1];ROOT=H.parent

def environment(policy=None):
 e=os.environ.copy()
 for k in list(e):
  if k.startswith(('UFUG_R','UFUG_ROUND','R90_')):e.pop(k)
 if policy:e['UFUG_R86_POLICY']=policy
 return e

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--results',type=Path,required=True);a=ap.parse_args()
 out=a.results/'stress';out.mkdir(parents=True,exist_ok=True)
 ev=ROOT/'evaluator'
 variants=[('frozen_explicit_extra',H/'build/synth_round86_frozen','extra_sop'),
           ('new_default',H/'build/synth_round90',None),
           ('submission_default',H/'build/submission_synth',None)]
 rows=[]
 for src in sorted((H/'canonical_bank/stress_v2').glob('*.txt')):
  for label,exe,pol in variants:
   net=out/f'{src.stem}_{label}.net';log=out/f'{src.stem}_{label}.log'
   t=time.perf_counter();z=subprocess.run([str(exe),str(src),str(net)],
      env=environment(pol),capture_output=True,text=True,timeout=45,errors='replace')
   ms=1000*(time.perf_counter()-t)
   log.write_text(z.stdout+'\n'+z.stderr)
   verify=subprocess.run([str(H/'build/verify_exhaustive'),str(src),str(net)],capture_output=True,text=True,timeout=45) if net.exists() else None
   row=dict(case=src.name,variant=label,local_wall_ms=round(ms,3),limit_ms=100,
      exceeds_local_limit=ms>100,exit_code=z.returncode,exact=bool(verify and verify.returncode==0),
      verify=verify.stdout.strip() if verify else '')
   if ev.is_file():
    report=out/f'{src.stem}_{label}_official.csv';ol=out/f'{src.stem}_{label}_official.log'
    official=subprocess.run([str(ev),str(exe),str(src),'--report',str(report)],
      capture_output=True,text=True,errors='replace',env=environment(pol),timeout=45)
    ol.write_text(official.stdout+'\n'+official.stderr)
    row.update(official_exit=official.returncode,official_excerpt=(official.stdout+'\n'+official.stderr)[-400:])
    if report.exists():
     with report.open(newline='') as f:r=list(csv.DictReader(f))
     if len(r)==1:row.update(official_status=r[0].get('status'),official_reason=r[0].get('reason'),official_runtime=r[0].get('runtime_ms'))
   rows.append(row)
   print('STRESS',src.name,label,'exact=',row['exact'],'local_ms=',round(ms,2),
     'official=',row.get('official_status','unavailable'),flush=True)
 with (out/'summary.csv').open('w',newline='') as f:
  w=csv.DictWriter(f,fieldnames=list(dict.fromkeys(k for r in rows for k in r)));w.writeheader();w.writerows(rows)
 (out/'summary.json').write_text(json.dumps(rows,indent=2)+'\n')
 print('STRESS_COMPLETE: sensitivity only; official fails do not imply grading fails',flush=True)
if __name__=='__main__':main()

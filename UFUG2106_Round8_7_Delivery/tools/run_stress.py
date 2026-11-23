#!/usr/bin/env python3
"""Stress-only sensitivity test. Never a release gate or proof of official grading failure."""
import argparse, csv, json, os, re, shutil, subprocess,time
from pathlib import Path
H=Path(__file__).resolve().parents[1];ROOT=H.parent
p=argparse.ArgumentParser();p.add_argument('--results',type=Path,required=True);a=p.parse_args()
out=a.results/'adversarial_stress';out.mkdir(parents=True,exist_ok=True)
rows=[]
for case in sorted((H/'stress_v2').glob('stress_*.txt')):
 for label,exe,key,val in [('r86_baseline','synth_round86','UFUG_R86_POLICY','baseline'),('r86_extra_sop','synth_round86','UFUG_R86_POLICY','extra_sop')]:
  env=os.environ.copy()
  for k in list(env):
   if k.startswith(('UFUG_R','UFUG_ROUND')):env.pop(k)
  env.update(UFUG_R71_POLICY='guard',UFUG_R8_POLICY='off',UFUG_R81_POLICY='off',
    UFUG_R82_POLICY='off',UFUG_R83_POLICY='off',UFUG_R84_POLICY='off',
    UFUG_R85_POLICY='off',UFUG_R86_POLICY='off');env[key]=val
  net=out/f'{case.stem}_{label}.net';log=out/f'{case.stem}_{label}.log'
  start=time.perf_counter()
  command=[str(H/'build'/exe),str(case),str(net)]
  z=subprocess.run(command,env=env,capture_output=True,text=True,errors='replace',timeout=30)
  elapsed_ms=(time.perf_counter()-start)*1000
  log.write_text(z.stdout+'\n'+z.stderr)
  v=subprocess.run([str(H/'build/verify_exhaustive'),str(case),str(net)],capture_output=True,text=True) if net.exists() else None
  exact=bool(v and v.returncode==0)
  row={'case':case.name,'policy':label,'supervisor_wall_ms':round(elapsed_ms,3),
       'limit_ms':100,'wall_exceeds_limit':elapsed_ms>100,'exit_code':z.returncode,
       'exact':exact,'verify':v.stdout.strip() if v else ''}
  # Official evaluator is called on the exact same custom cases when available.
  ev=ROOT/'evaluator'
  if ev.is_file():
   report=out/f'{case.stem}_{label}_official.csv';official_log=out/f'{case.stem}_{label}_official.log'
   q=subprocess.run([str(ev),str(H/'build'/exe),str(case),'--report',str(report)],
     capture_output=True,text=True,env=env,errors='replace',timeout=45)
   official_log.write_text(q.stdout+'\n'+q.stderr)
   row['official_evaluator_exit']=q.returncode
   row['official_raw']=(q.stdout+' '+q.stderr).strip()[:350]
   row['official_report_present']=report.is_file()
  rows.append(row)
  print('ADVERSARIAL',case.name,label,'exact',exact,'wall_ms',round(elapsed_ms,2),
        'over100ms',elapsed_ms>100,'official',row.get('official_raw','not available'),flush=True)
with (out/'summary.csv').open('w',newline='') as f:
 writer=csv.DictWriter(f,fieldnames=list(dict.fromkeys(k for r in rows for k in r)))
 writer.writeheader();writer.writerows(rows)
(out/'summary.json').write_text(json.dumps(rows,indent=2)+'\n')
print('ADVERSARIAL_COMPLETE: sensitivity evidence only; NOT a release PASS or hidden-test predictor')

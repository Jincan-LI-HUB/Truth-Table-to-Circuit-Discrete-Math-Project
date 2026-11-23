#!/usr/bin/env python3
"""Genuine course evaluator on unmodified 50 public cases, candidate w/o custom flags."""
import argparse,csv,hashlib,json,os,platform,shutil,subprocess,tempfile
from pathlib import Path
H=Path(__file__).resolve().parents[1];ROOT=H.parent

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def environment(policy=None):
 e=os.environ.copy()
 for k in list(e):
  if k.startswith(('UFUG_R','UFUG_ROUND','R90_')):e.pop(k)
 if policy:e['UFUG_R86_POLICY']=policy
 return e

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--results',type=Path,required=True);ap.add_argument('--runs',type=int,default=2)
 args=ap.parse_args();out=args.results/'official';out.mkdir(parents=True,exist_ok=True)
 ev=ROOT/'evaluator'
 if not ev.is_file():raise RuntimeError('Course evaluator missing: '+str(ev))
 combinations=[('frozen_explicit_extra','synth_round86_frozen','extra_sop'),
               ('r90_no_flags','synth_round90',None),
               ('r90_explicit_extra','synth_round90','extra_sop'),
               ('submission_no_flags','submission_synth',None)]
 state={'evaluator_sha256':sha(ev),'source_sha256':sha(H/'src/synth_round90.cpp'),
        'submission_sha256':sha(H/'submission/synth.cpp'),'hidden':False,'records':[]}
 with tempfile.TemporaryDirectory(prefix='r90_real_course_evaluator_') as d:
  copied=Path(d)/'evaluator';shutil.copy2(ev,copied);copied.chmod(copied.stat().st_mode|0o111)
  for run in range(1,args.runs+1):
   for stage in ('stage1','stage2'):
    bank=ROOT/'data'/stage
    if not bank.is_dir():raise RuntimeError('Missing official public bank: '+str(bank))
    order=combinations if run%2 else list(reversed(combinations))
    for label,bin_name,policy in order:
     exe=H/'build'/bin_name
     report=out/f'{stage}_run{run}_{label}.csv';log=out/f'{stage}_run{run}_{label}.log'
     z=subprocess.run([str(copied),str(exe),str(bank.resolve()),'--report',str(report)],
         capture_output=True,text=True,errors='replace',env=environment(policy),timeout=180)
     log.write_text(z.stdout+'\n'+z.stderr)
     if not report.exists():raise RuntimeError(f'No evaluator report for {label}: see {log}')
     with report.open(newline='') as f:rows=list(csv.DictReader(f))
     if len(rows)!=25:raise RuntimeError(f'Public {stage} expected 25: saw {len(rows)}')
     passed=sum(r['status']=='PASS' for r in rows)
     met=sum(r['target_met']=='yes' for r in rows)
     area=sum(int(r['area']) for r in rows if r['status']=='PASS')
     delay=sum(int(r['delay']) for r in rows if r['status']=='PASS')
     item=dict(run=run,stage=stage,policy=label,source=bin_name,sha256=sha(exe),
        exit_code=z.returncode,passed=passed,target_met=met,area_sum=area,delay_sum=delay)
     state['records'].append(item)
     (out/'summary.json').write_text(json.dumps(state,indent=2)+'\n')
     print('PUBLIC',stage,'run',run,label,f'{passed}/25',f'target={met}',f'area={area}',flush=True)
     if z.returncode or passed!=25 or met!=25:raise RuntimeError('Official public gate FAILED '+str(item))
 print('R90_PUBLIC_GATE_PASS (public only; no grading/hidden claim)',flush=True)
if __name__=='__main__':main()

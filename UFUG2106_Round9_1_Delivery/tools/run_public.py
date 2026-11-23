#!/usr/bin/env python3
"""Real, supplied evaluator only. 5 strategies × 2 banks × 2 runs × 25 = 500 cases."""
import argparse,csv,hashlib,json,os,subprocess,shutil,tempfile
from pathlib import Path
H=Path(__file__).resolve().parents[1];ROOT=H.parent

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def env(kind):
 d=os.environ.copy()
 for k in list(d):
  if k.startswith(('UFUG_', 'R90_')):d.pop(k)
 if kind:d['UFUG_R91_POLICY']=kind
 return d

def main():
 p=argparse.ArgumentParser();p.add_argument('--results',type=Path,required=True);p.add_argument('--runs',type=int,default=2);a=p.parse_args()
 out=a.results/'official';out.mkdir(parents=True,exist_ok=True)
 ev=ROOT/'evaluator'
 if not ev.is_file():raise RuntimeError('Genuine course evaluator not found at '+str(ev))
 configs=[('r90_frozen','synth_round90_frozen',None),('r91_off','synth_round91','off'),('r91_library','synth_round91','library'),('r91_repeat_sop','synth_round91','repeat_sop'),('r91_repeat_shannon','synth_round91','repeat_shannon')]
 state=dict(hidden=False,evaluator_sha256=sha(ev),frozen_source=sha(H/'src/synth_round90.cpp'),candidate_source=sha(H/'src/synth_round91.cpp'),records=[])
 with tempfile.TemporaryDirectory(prefix='r91_real_evaluator_') as tmp:
  temp_ev=Path(tmp)/'evaluator';shutil.copy2(ev,temp_ev);temp_ev.chmod(temp_ev.stat().st_mode|0o111)
  for run in range(1,a.runs+1):
   for stage in ('stage1','stage2'):
    bank=ROOT/'data'/stage
    if not bank.is_dir():raise RuntimeError('Missing course '+str(bank))
    for label,exe_name,kind in (configs if run%2 else list(reversed(configs))):
     exe=H/'build'/exe_name
     report=out/f'{stage}_run{run}_{label}.csv';log=out/f'{stage}_run{run}_{label}.log'
     z=subprocess.run([str(temp_ev),str(exe),str(bank.resolve()),'--report',str(report)],capture_output=True,text=True,errors='replace',env=env(kind),timeout=240)
     log.write_text(z.stdout+'\n'+z.stderr)
     if not report.is_file():raise RuntimeError('Evaluator omitted report '+str(log))
     with report.open(newline='') as f:rows=list(csv.DictReader(f))
     if len(rows)!=25:raise RuntimeError('Unexpected case count '+str(len(rows)))
     passed=sum(x.get('status')=='PASS' for x in rows)
     met=sum(x.get('target_met')=='yes' for x in rows)
     area=sum(int(x.get('area') or 0) for x in rows if x.get('status')=='PASS')
     delay=sum(int(x.get('delay') or 0) for x in rows if x.get('status')=='PASS')
     entry=dict(stage=stage,run=run,policy=label,sha256=sha(exe),passed=passed,target_met=met,area=area,delay=delay,exit_code=z.returncode)
     state['records'].append(entry)
     (out/'summary.json').write_text(json.dumps(state,indent=2)+'\n')
     print('PUBLIC',stage,'run',run,label,f'{passed}/25',f'target={met}',f'area={area}',f'delay={delay}',flush=True)
     if z.returncode or passed!=25 or met!=25:raise RuntimeError('Official public gate FAILED '+str(entry))
 print('R91_PUBLIC_PASS; 50 public cases only; hidden cases not checked',flush=True)
if __name__=='__main__':main()

#!/usr/bin/env python3
"""Paired genuine course evaluator (no other evaluator substituted)."""
import argparse,csv,hashlib,json,os,platform,shutil,subprocess,tempfile
from pathlib import Path
H=Path(__file__).resolve().parents[1];ROOT=H.parent

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 p=argparse.ArgumentParser();p.add_argument('--results',required=True,type=Path);p.add_argument('--runs',type=int,default=2);a=p.parse_args()
 out=a.results/'official';out.mkdir(parents=True,exist_ok=True)
 ev=ROOT/'evaluator';assert ev.exists(),f'Genuine evaluator absent: {ev}'
 combos=[('r86_baseline',H/'build/synth_round86','UFUG_R86_POLICY','baseline'),
         ('r86_extra_sop',H/'build/synth_round86','UFUG_R86_POLICY','extra_sop'),
         ('r85_reclaim',H/'build/synth_round85_frozen','UFUG_R85_POLICY','budget_reclaim')]
 state={'evaluated_by_course_binary':True,'actual_hidden_cases':False,'case_count_per_stage':25,
        'runs':a.runs,'source_sha256':{'r86':sha(H/'src/synth_round86.cpp'),'r85':sha(H/'src/synth_round85_frozen.cpp')},
        'binary_sha256':{x[0]:sha(x[1]) for x in combos},'evaluator_sha256':sha(ev),
        'platform':platform.platform(),'records':[]}
 with tempfile.TemporaryDirectory(prefix='r87_original_evaluator_') as tmp:
  copied=Path(tmp)/'evaluator';shutil.copy2(ev,copied);copied.chmod(copied.stat().st_mode|0o111)
  for run in range(1,a.runs+1):
   for stage in ('stage1','stage2'):
    bank=ROOT/'data'/stage
    if not bank.is_dir():raise RuntimeError('Missing public bank '+str(bank))
    for label,exe,ek,policy in (combos if run%2 else list(reversed(combos))):
     env=os.environ.copy()
     for k in list(env):
      if k.startswith(('UFUG_R','UFUG_ROUND')):env.pop(k)
     env.update(UFUG_R71_POLICY='guard',UFUG_R8_POLICY='off',UFUG_R81_POLICY='off',
          UFUG_R82_POLICY='off',UFUG_R83_POLICY='off',UFUG_R84_POLICY='off',
          UFUG_R85_POLICY='off',UFUG_R86_POLICY='off')
     env[ek]=policy
     report=out/f'{stage}_run{run}_{label}.csv';log=out/f'{stage}_run{run}_{label}.log'
     z=subprocess.run([str(copied),str(exe),str(bank.resolve()),'--report',str(report)],
            capture_output=True,text=True,errors='replace',env=env)
     log.write_text(z.stdout+'\n'+z.stderr)
     if not report.exists():raise RuntimeError(f'No evaluator CSV: {label}, see {log}')
     with report.open(newline='') as f:rows=list(csv.DictReader(f))
     if len(rows)!=25:raise RuntimeError('Bad public bank case count')
     passes=sum(r['status']=='PASS' for r in rows)
     targets=sum(r['target_met']=='yes' for r in rows)
     area=sum(int(r['area']) for r in rows if r['status']=='PASS')
     state['records'].append(dict(run=run,stage=stage,policy=label,
                                 evaluator_exit=z.returncode,passed=passes,target_met=targets,area_sum=area))
     (out/'summary.json').write_text(json.dumps(state,indent=2)+'\n')
     print('PUBLIC',stage,'run',run,label,passes,'/25 target=',targets,'area=',area,flush=True)
     if z.returncode or passes!=25 or targets!=25:
      raise RuntimeError('Official public gate FAILED: '+str((run,stage,label)))
 print('ROUND8.7 PUBLIC GATE PASS (50 public cases only; hidden cases not tested)',flush=True)
if __name__=='__main__':main()

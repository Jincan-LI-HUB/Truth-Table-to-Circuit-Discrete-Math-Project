#!/usr/bin/env python3
"""Course evaluator only. Does not claim grading-hidden performance."""
import argparse,subprocess,os,csv,json,tempfile,shutil,hashlib,math,statistics
from pathlib import Path
H=Path(__file__).resolve().parents[1]
ROOT=H.parent
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def clean(extra):
 env=os.environ.copy()
 for k in list(env):
  if k.startswith(('UFUG_','R90_','R10_')):env.pop(k)
 env.update(extra)
 return env
CONFIGS=[
 ('r100_frozen','synth_round100_frozen',{}),
 ('r101_default','synth_round101',{}),
 ('r101_cap80','synth_round101',{'UFUG_R91_ROOT_CAP':'80'}),
 ('r101_cap40','synth_round101',{'UFUG_R91_ROOT_CAP':'40'}),
 ('r101_budget45','synth_round101',{'UFUG_R101_BUDGET_CAP_MS':'45'}),
 ('r101_off','synth_round101',{'UFUG_R91_POLICY':'off'}),
 ('trial_submission','trial_submission',{})]
def main():
 p=argparse.ArgumentParser();p.add_argument('--out',type=Path,required=True);p.add_argument('--quick',action='store_true');a=p.parse_args()
 ev=ROOT/'evaluator'
 if not ev.is_file():raise RuntimeError('Genuine evaluator is missing: '+str(ev))
 for stage in ('stage1','stage2'):
  if not (ROOT/'data'/stage).is_dir():raise RuntimeError('Original public cases missing: '+stage)
 out=a.out/'official';out.mkdir(parents=True,exist_ok=True)
 configs=CONFIGS if not a.quick else [CONFIGS[i] for i in (0,1,2,5)]
 runs=1 if a.quick else 2
 summary=[]
 with tempfile.TemporaryDirectory(prefix='r101_eval_') as tmp:
  exe=Path(tmp)/'evaluator';shutil.copy2(ev,exe);exe.chmod(exe.stat().st_mode|0o111)
  for run in range(1,runs+1):
   for stage in ('stage1','stage2'):
    for label,binary,env in (configs if run%2 else reversed(configs)):
     report=out/f'{stage}_run{run}_{label}.csv';log=out/f'{stage}_run{run}_{label}.log'
     r=subprocess.run([str(exe),str(H/'build'/binary),str((ROOT/'data'/stage).resolve()),'--report',str(report)],env=clean(env),capture_output=True,text=True,errors='replace',timeout=240)
     log.write_text(r.stdout+'\n'+r.stderr)
     if not report.is_file():raise RuntimeError('NO_OFFICIAL_REPORT '+str(log))
     with report.open(newline='') as f:rows=list(csv.DictReader(f))
     if len(rows)!=25:raise RuntimeError('EXPECTED_25_CASES '+str(report))
     passed=sum(x.get('status')=='PASS' for x in rows)
     met=sum(x.get('target_met')=='yes' for x in rows)
     area=sum(int(x['area']) for x in rows if x['status']=='PASS')
     delay=sum(int(x['delay']) for x in rows if x['status']=='PASS')
     values=[float(x['runtime_ms']) for x in rows if x['status']=='PASS']
     item=dict(stage=stage,run=run,policy=label,passed=passed,target_met=met,area=area,delay=delay,median_runtime_ms=statistics.median(values) if values else None,max_runtime_ms=max(values) if values else None,exe_sha256=sha(H/'build'/binary),exit_code=r.returncode)
     summary.append(item);(out/'summary.json').write_text(json.dumps(dict(evaluator_sha256=sha(ev),public_only=True,records=summary),indent=2)+'\n')
     print('PUBLIC',stage,'run',run,label,f'{passed}/25',f'target={met}',f'area={area}',f'delay={delay}',f'median_ms={item["median_runtime_ms"]:.2f}',flush=True)
     if r.returncode or passed!=25 or met!=25:raise RuntimeError('OFFICIAL_GATE_FAIL '+str(item))
 print('R101_PUBLIC_RELEASE_GATE_PASS; official public only, no grading-hidden claim',flush=True)
if __name__=='__main__':main()

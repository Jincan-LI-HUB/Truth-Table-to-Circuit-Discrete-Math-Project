#!/usr/bin/env python3
"""Genuine course evaluator only, paired Stage1/Stage2, frozen R8.4 comparator embedded."""
import argparse,csv,hashlib,json,os,platform,statistics,math,subprocess,tempfile,shutil
from pathlib import Path
H=Path(__file__).resolve().parents[1];ROOT=H.parent

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def parse_report(p):
 with p.open(newline='') as f:rows=list(csv.DictReader(f))
 if len(rows)!=25:raise RuntimeError(f'Expected 25 rows in {p}, got {len(rows)}')
 d={r['case']:r for r in rows}
 if len(d)!=25:raise RuntimeError(f'Duplicate case in {p}')
 return d

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--results',required=True,type=Path)
 ap.add_argument('--runs',type=int,default=2);ap.add_argument('--quick',action='store_true');a=ap.parse_args()
 if a.runs<1:raise ValueError('runs must >=1')
 out=a.results/'official';out.mkdir(parents=True,exist_ok=True)
 ev=ROOT/'evaluator';r84=H/'build/synth_round84_frozen';r85=H/'build/synth_round85'
 for path in (ev,r84,r85):
  if not path.is_file():raise RuntimeError(f'missing binary: {path}')
 variants=[
  ('r84_topq_dual',r84,{'UFUG_R84_POLICY':'topq_dual'}),
  ('r84_topq_dense',r84,{'UFUG_R84_POLICY':'topq_dense'}),
  ('r84_mixed66',r84,{'UFUG_R84_POLICY':'mixed66_dual'}),
  ('r85_shannon_first',r85,{'UFUG_R85_POLICY':'dual_shannon_first'}),
  ('r85_sop_first',r85,{'UFUG_R85_POLICY':'dual_sop_first'}),
  ('r85_dense_sop_first',r85,{'UFUG_R85_POLICY':'dense_sop_first'}),
  ('r85_budget_reclaim',r85,{'UFUG_R85_POLICY':'budget_reclaim'})]
 if a.quick:variants=[v for v in variants if v[0] in ('r84_topq_dual','r85_sop_first','r85_budget_reclaim')]
 state={'milestone':'Round8.5','course_official_evaluator_used':True,'runs':a.runs,'quick':a.quick,
   'platform':platform.platform(),'fingerprints':{'evaluator':sha(ev),'r84_executable':sha(r84),'r85_executable':sha(r85)},
   'records':[],'paired':[], 'no_positive_RAM_assessment':True}
 (out/'summary.json').write_text(json.dumps(state,indent=2)+'\n')
 with tempfile.TemporaryDirectory(prefix='r85_evaluator_') as t:
  e=Path(t)/'evaluator';shutil.copy2(ev,e);e.chmod(e.stat().st_mode|0o111)
  for run in range(1,a.runs+1):
   for stage in ('stage1','stage2'):
    bank=ROOT/'data'/stage
    if not bank.is_dir():raise RuntimeError('Missing bank '+str(bank))
    current={}
    for label,exe,settings in (variants if run%2 else list(reversed(variants))):
     report=out/f'{stage}_run{run}_{label}.csv';log=out/f'{stage}_run{run}_{label}.log'
     env=os.environ.copy()
     for k in list(env):
      if k.startswith('UFUG_R') or k.startswith('UFUG_ROUND'):env.pop(k)
     env.update(settings);env.update(UFUG_R71_POLICY='guard',UFUG_R8_POLICY='off',UFUG_R81_POLICY='off',UFUG_R82_POLICY='off',UFUG_R83_POLICY='off')
     if exe==r85:env.update(UFUG_R84_POLICY='off')
     else:env.pop('UFUG_R85_POLICY',None)
     q=subprocess.run([str(e),str(exe),str(bank.resolve()),'--report',str(report)],text=True,capture_output=True,errors='replace',env=env)
     log.write_text(q.stdout+'\n'+q.stderr)
     if not report.is_file():raise RuntimeError(f'{label} no official CSV exit={q.returncode}, see {log}')
     cases=parse_report(report);current[label]=cases
     count=sum(r['status']=='PASS' for r in cases.values())
     target=sum(r.get('target_met')=='yes' for r in cases.values())
     if count:area=sum(int(r['area']) for r in cases.values() if r['status']=='PASS')
     else:area=0
     runtime=statistics.median(float(r['runtime_ms']) for r in cases.values() if r['status']=='PASS') if count else None
     state['records'].append(dict(run=run,stage=stage,variant=label,exit=q.returncode,passed=count,target_met=target,area_sum=area,median_ms=runtime))
     (out/'summary.json').write_text(json.dumps(state,indent=2)+'\n')
     print(f'{stage} run{run} {label:22s} {count}/25 target={target} area={area}',flush=True)
     if q.returncode!=0 or count!=25 or target!=25:raise RuntimeError(f'OFFICIAL FAIL {stage} run{run} {label}')
    ref=current['r84_topq_dual']
    for label,others in current.items():
     equalA=sum(int(ref[k]['area'])==int(others[k]['area']) for k in ref)
     equalD=sum(int(ref[k]['delay'])==int(others[k]['delay']) for k in ref)
     ratio=math.exp(statistics.mean(math.log(float(others[k]['runtime_ms'])/float(ref[k]['runtime_ms'])) for k in ref if float(ref[k]['runtime_ms'])>0 and float(others[k]['runtime_ms'])>0))
     state['paired'].append(dict(run=run,stage=stage,variant=label,reference='r84_topq_dual',
       delta_area=sum(int(others[k]['area'])-int(ref[k]['area']) for k in ref),area_equal=equalA,delay_equal=equalD,geomean_runtime_ratio=ratio))
     (out/'summary.json').write_text(json.dumps(state,indent=2)+'\n')
 print('ROUND8.5 OFFICIAL PUBLIC RELEASE_GATE PASS; no hidden-test or RAM-limit claim',flush=True)
if __name__=='__main__':
 try:main()
 except Exception as e:
  print('R85_OFFICIAL_FAILED:',repr(e),flush=True)
  raise

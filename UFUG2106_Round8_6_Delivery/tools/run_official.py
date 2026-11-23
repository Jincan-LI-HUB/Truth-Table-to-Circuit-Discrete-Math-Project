#!/usr/bin/env python3
"""Unmodified course evaluator. Seven paired configurations, 2 banks, reversed order."""
import argparse,csv,hashlib,json,os,platform,statistics,math,subprocess,tempfile,shutil
from pathlib import Path
H=Path(__file__).resolve().parents[1];ROOT=H.parent
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def parse_report(p):
 with p.open(newline='') as f:rows=list(csv.DictReader(f))
 if len(rows)!=25:raise RuntimeError(f'Expected 25 rows in {p}, got {len(rows)}')
 d={r['case']:r for r in rows}
 if len(d)!=25:raise RuntimeError(f'Duplicate cases in {p}')
 return d

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--results',required=True,type=Path)
 ap.add_argument('--runs',type=int,default=2);ap.add_argument('--quick',action='store_true');a=ap.parse_args()
 if a.runs<1:raise ValueError('runs must >=1')
 out=a.results/'official';out.mkdir(parents=True,exist_ok=True)
 ev=ROOT/'evaluator';r85=H/'build/synth_round85_frozen';r86=H/'build/synth_round86'
 for path in (ev,r85,r86):
  if not path.is_file():raise RuntimeError('Missing genuine required executable '+str(path))
 variants=[('r85_dual',r85,{'UFUG_R85_POLICY':'dual_shannon_first'}),
 ('r85_reclaim',r85,{'UFUG_R85_POLICY':'budget_reclaim'}),
 ('r86_baseline',r86,{'UFUG_R86_POLICY':'baseline'}),
 ('r86_extra_sop',r86,{'UFUG_R86_POLICY':'extra_sop'}),
 ('r86_time_reclaim',r86,{'UFUG_R86_POLICY':'time_reclaim'}),
 ('r86_combined',r86,{'UFUG_R86_POLICY':'combined'}),
 ('r86_reverse',r86,{'UFUG_R86_POLICY':'reverse_allocation'})]
 if a.quick:variants=[v for v in variants if v[0] in ('r85_reclaim','r86_baseline','r86_combined')]
 state={'milestone':'Round8.6','course_official_evaluator_used':True,'runs':a.runs,'quick':a.quick,
  'platform':platform.platform(),'fingerprints':{'evaluator':sha(ev),'r85_executable':sha(r85),'r86_executable':sha(r86),
  'r85_source':sha(H/'src/synth_round85_frozen.cpp'),'r86_source':sha(H/'src/synth_round86.cpp')},
  'records':[],'paired':[],'no_hidden_test_claim':True,'no_positive_ram_claim':True}
 (out/'summary.json').write_text(json.dumps(state,indent=2)+'\n')
 with tempfile.TemporaryDirectory(prefix='r86_evaluator_') as t:
  e=Path(t)/'evaluator';shutil.copy2(ev,e);e.chmod(e.stat().st_mode|0o111)
  for run in range(1,a.runs+1):
   for stage in ('stage1','stage2'):
    bank=ROOT/'data'/stage;current={}
    if not bank.is_dir():raise RuntimeError('Missing data bank '+str(bank))
    for label,exe,settings in (variants if run%2 else list(reversed(variants))):
     report=out/f'{stage}_run{run}_{label}.csv';log=out/f'{stage}_run{run}_{label}.log'
     env=os.environ.copy()
     for k in list(env):
      if k.startswith('UFUG_R') or k.startswith('UFUG_ROUND'):env.pop(k)
     env.update(UFUG_R71_POLICY='guard',UFUG_R8_POLICY='off',UFUG_R81_POLICY='off',UFUG_R82_POLICY='off',UFUG_R83_POLICY='off',UFUG_R84_POLICY='off')
     env.update(settings)
     if exe==r86:env['UFUG_R85_POLICY']='off'
     else:env.pop('UFUG_R86_POLICY',None)
     q=subprocess.run([str(e),str(exe),str(bank.resolve()),'--report',str(report)],text=True,capture_output=True,errors='replace',env=env)
     log.write_text(q.stdout+'\n'+q.stderr)
     if not report.is_file():raise RuntimeError(f'{label} missing report exit={q.returncode}; see {log}')
     cases=parse_report(report);current[label]=cases
     passed=sum(r['status']=='PASS' for r in cases.values())
     target=sum(r.get('target_met')=='yes' for r in cases.values())
     area=sum(int(r['area']) for r in cases.values() if r['status']=='PASS')
     runtime=statistics.median(float(r['runtime_ms']) for r in cases.values() if r['status']=='PASS') if passed else None
     state['records'].append(dict(run=run,stage=stage,variant=label,exit=q.returncode,passed=passed,target_met=target,area_sum=area,median_ms=runtime))
     (out/'summary.json').write_text(json.dumps(state,indent=2)+'\n')
     print(f'{stage} run{run} {label:22s} {passed}/25 target={target} area={area}',flush=True)
     if q.returncode!=0 or passed!=25 or target!=25:raise RuntimeError(f'OFFICIAL FAIL {stage} run{run} {label}')
    ref=current['r86_baseline']
    for label,others in current.items():
     equal_a=sum(int(ref[k]['area'])==int(others[k]['area']) for k in ref)
     equal_d=sum(int(ref[k]['delay'])==int(others[k]['delay']) for k in ref)
     valid_ratios=[float(others[k]['runtime_ms'])/float(ref[k]['runtime_ms']) for k in ref
                   if float(ref[k]['runtime_ms'])>0 and float(others[k]['runtime_ms'])>0]
     ratio=math.exp(statistics.mean(map(math.log,valid_ratios))) if valid_ratios else None
     state['paired'].append(dict(run=run,stage=stage,variant=label,reference='r86_baseline',
       delta_area=sum(int(others[k]['area'])-int(ref[k]['area']) for k in ref),
       area_equal=equal_a,delay_equal=equal_d,geomean_runtime_ratio=ratio))
     (out/'summary.json').write_text(json.dumps(state,indent=2)+'\n')
 print('ROUND8.6 OFFICIAL PUBLIC RELEASE_GATE PASS; no hidden-test or RAM-limit claim',flush=True)
if __name__=='__main__':
 try:main()
 except Exception as e:
  print('R86_OFFICIAL_FAILED:',repr(e),flush=True);raise

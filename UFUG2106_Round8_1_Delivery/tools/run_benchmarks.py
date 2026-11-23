#!/usr/bin/env python3
"""Same-host paired official evaluation of R7.2, R8.0 and R8.1 modes.
No assumed course scoring formula. Failed cases never contribute to total-area
claims. Always emits raw CSV, logs, structured summaries and pairwise deltas.
"""
from __future__ import annotations
import argparse,csv,datetime,hashlib,json,math,os,platform,shutil,statistics,subprocess,tempfile
from pathlib import Path
H=Path(__file__).resolve().parents[1];ROOT=H.parent

def sha(path):
 h=hashlib.sha256()
 with open(path,'rb') as f:
  for chunk in iter(lambda:f.read(1048576),b''):h.update(chunk)
 return h.hexdigest()

def parse(path):
 with open(path,newline='') as f:rows=list(csv.DictReader(f))
 if len(rows)!=25:raise RuntimeError(f'Expected 25 rows in {path}, got {len(rows)}')
 return {r['case']:r for r in rows}

def ok(row):return row['status']=='PASS'
def aggregate(data):
 good=[r for r in data.values() if ok(r)]
 t=[float(r['runtime_ms']) for r in good if r.get('runtime_ms')]
 return dict(passed=len(good),target_met=sum(r.get('target_met')=='yes' for r in good),
  area_passed=sum(int(r['area']) for r in good),area_complete=(len(good)==len(data)),
  median_ms=round(statistics.median(t),3) if t else None,
  max_ms=round(max(t),3) if t else None,
  failures=[k for k,r in data.items() if not ok(r)])

def gmean(xs):return round(math.exp(statistics.mean(map(math.log,xs))),6) if xs else None

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--runs',type=int,default=2)
 ap.add_argument('--quick',action='store_true',help='baseline + branch + strict, rather than full method/order ablations')
 ap.add_argument('--profiles',action='store_true',help='direct synth logs and outputs on representative cases (not official time)')
 a=ap.parse_args()
 if a.runs<1:raise ValueError('runs must be >=1')
 r72=ROOT/'UFUG2106_Round7_2_Delivery/build/synth_round72'
 r80=ROOT/'UFUG2106_Round8_Prototype/build/synth_round8'
 r81=H/'build/synth_round81';ev=ROOT/'evaluator'
 for path in (r72,r80,r81,ev):
  if not path.is_file():raise RuntimeError(f'Missing program: {path}')
 variants=[('r72',r72,{}),
  ('r80_iterate',r80,{'UFUG_R8_POLICY':'iterate'}),
  ('r81_sop',r81,{'UFUG_R8_POLICY':'off','UFUG_R81_POLICY':'sop'}),
  ('r81_shannon',r81,{'UFUG_R8_POLICY':'off','UFUG_R81_POLICY':'shannon'}),
  ('r81_all',r81,{'UFUG_R8_POLICY':'off','UFUG_R81_POLICY':'all'}),
  ('r81_branch',r81,{'UFUG_R8_POLICY':'iterate','UFUG_R81_POLICY':'branch'}),
  ('r81_strict',r81,{'UFUG_R8_POLICY':'iterate_strict','UFUG_R81_POLICY':'branch_strict'}),
  ('r81_reverse',r81,{'UFUG_R8_POLICY':'off','UFUG_R81_POLICY':'reverse'})]
 if a.quick:variants=[x for x in variants if x[0] in {'r72','r81_branch','r81_strict'}]
 stamp=datetime.datetime.now().strftime('%Y%m%d_%H%M%S_%f');out=H/'results'/stamp;out.mkdir(parents=True)
 (H/'latest_run.txt').write_text(str(out.resolve())+'\n',encoding='utf8')
 summary={'milestone':'Round8.1','runs':a.runs,'quick':a.quick,
          'official_grading_formula_known':False,
          'fingerprints':{'r72':sha(r72),'r80':sha(r80),'r81':sha(r81),'evaluator':sha(ev)},
          'host':{'platform':platform.platform(),'python':platform.python_version()},
          'raw_runs':[],'comparison':[]}
 def save():(out/'summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n')
 save();records=[]
 with tempfile.TemporaryDirectory(prefix='ufug_r81_eval_') as tmp:
  binary=Path(tmp)/'evaluator';shutil.copy2(ev,binary);binary.chmod(binary.stat().st_mode|0o111)
  for run in range(1,a.runs+1):
   for stage in ('stage1','stage2'):
    path=(ROOT/'data'/stage).resolve()
    if not path.is_dir():raise RuntimeError(f'Missing data directory: {path}')
    observed={}
    seq=variants if run%2==1 else list(reversed(variants))
    for name,program,env_changes in seq:
     report=out/f'run{run}_{stage}_{name}.csv'
     env=os.environ.copy()
     for key in ('UFUG_R8_POLICY','UFUG_R81_POLICY','UFUG_R8_PROFILE','UFUG_R81_PROFILE','UFUG_R72_POLICY','UFUG_R71_POLICY','UFUG_R7_LEGACY_MERGE','UFUG_R7_LEGACY_COVER','UFUG_ROUND5_PROFILE'):
      env.pop(key,None)
     env.update(env_changes)
     result=subprocess.run([str(binary),str(program),str(path),'--report',str(report)],stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True,errors='replace',env=env)
     (out/f'run{run}_{stage}_{name}.log').write_text(result.stdout,encoding='utf8')
     if not report.exists():
      summary['raw_runs'].append({'stage':stage,'run':run,'variant':name,'exit':result.returncode,'error':'missing CSV'})
      save();raise RuntimeError(f'Evaluator failed to create {report}')
     dat=parse(report);observed[name]=dat;metric=aggregate(dat)
     summary['raw_runs'].append({'stage':stage,'run':run,'variant':name,'exit':result.returncode,
                                  'metrics':metric,'csv':report.name})
     save()
     print(f'{stage} run{run} {name:14s} {metric["passed"]}/25 PASS target={metric["target_met"]} area_passed={metric["area_passed"]}',flush=True)
    for name in observed:
     if name=='r72':continue
     for key in sorted(observed['r72']):
      old=observed['r72'][key];new=observed[name][key];both=ok(old) and ok(new)
      x={'stage':stage,'run':run,'variant':name,'case':key,
         'base_status':old['status'],'new_status':new['status'],'target_met':new.get('target_met','')}
      if both:
       aa=int(old['area']);bb=int(new['area']);dd=int(old['delay']);ee=int(new['delay'])
       t0=float(old['runtime_ms']);t1=float(new['runtime_ms'])
       x.update(base_area=aa,new_area=bb,delta_area=bb-aa,base_delay=dd,new_delay=ee,delta_delay=ee-dd,
                base_ms=t0,new_ms=t1,runtime_ratio=t1/t0 if t0>0 else '',
                pareto_dominate=(bb<=aa and ee<=dd and (bb<aa or ee<dd)))
      else:
       x.update(base_area='',new_area='',delta_area='',base_delay='',new_delay='',delta_delay='',
                base_ms='',new_ms='',runtime_ratio='',pareto_dominate='')
      records.append(x)
 if records:
  with (out/'casewise_comparison.csv').open('w',newline='') as f:
   w=csv.DictWriter(f,list(records[0]));w.writeheader();w.writerows(records)
 for stage in ('stage1','stage2'):
  for name,*_ in variants:
   if name=='r72':continue
   q=[x for x in records if x['stage']==stage and x['variant']==name];common=[x for x in q if isinstance(x['delta_area'],int)]
   summary['comparison'].append({'stage':stage,'variant':name,'paired_common':len(common),
       'area_delta_on_common':sum(x['delta_area'] for x in common),
       'area_improvement_cases':sum(x['delta_area']<0 for x in common),
       'area_regression_cases':sum(x['delta_area']>0 for x in common),
       'delay_regression_cases':sum(x['delta_delay']>0 for x in common),
       'pareto_domination_cases':sum(x['pareto_dominate'] is True for x in common),
       'runtime_gmean_ratio':gmean([x['runtime_ratio'] for x in common if x['runtime_ratio']]),
       'new_failures':[x['case'] for x in q if x['base_status']=='PASS' and x['new_status']!='PASS']})
 if a.profiles:
  diag=out/'diagnostics';diag.mkdir(exist_ok=True)
  for stage,case in (('stage2','case_003'),('stage2','case_005'),('stage2','case_016'),('stage2','case_021'),('stage2','case_023'),('stage1','case_020')):
   source=ROOT/'data'/stage/(case+'.txt')
   if not source.exists():continue
   for name,prog,change in (('r72',r72,{}),('r81_branch',r81,{'UFUG_R8_POLICY':'iterate','UFUG_R81_POLICY':'branch','UFUG_R81_PROFILE':'1'}),('r81_strict',r81,{'UFUG_R8_POLICY':'iterate_strict','UFUG_R81_POLICY':'branch_strict','UFUG_R81_PROFILE':'1'})):
    fn=diag/f'{stage}_{case}_{name}.netlist'
    env=os.environ.copy();env.update(change)
    pr=subprocess.run([str(prog),str(source),str(fn)],capture_output=True,text=True,env=env,timeout=120)
    (diag/f'{stage}_{case}_{name}.log').write_text(pr.stdout+pr.stderr)
    if pr.returncode:raise RuntimeError(f'diagnostic process failed {stage} {case} {name}')
 gates={}
 for name in ('r81_branch','r81_strict'):
  vals=[x for x in summary['raw_runs'] if x['variant']==name]
  feasible=len(vals)==2*a.runs and all(x['metrics']['passed']==25 and x['metrics']['target_met']==25 for x in vals)
  q=[x for x in records if x['variant']==name and isinstance(x['delta_area'],int)]
  noregress=all(x['delta_area']<=0 for x in q)
  no_delay_regress=all(x['delta_delay']<=0 for x in q)
  gates[name]={'50_case_pass_target_each_run':feasible,'no_area_regression_on_paired_pass':noregress,
              'no_delay_regression_on_paired_pass':no_delay_regress,'release_candidate':feasible and noregress}
 summary['gates']=gates
 report=['# Round 8.1 — Official evaluator paired study','',
         'Raw evaluator CSV and log files are authoritative. No course scoring formula was assumed.','',
         '| Stage | Variant | Runs PASS | Passed-case Area (asterisk=incomplete) |',
         '|---|---|---|---|']
 for stage in ('stage1','stage2'):
  for name,*_ in variants:
   vals=[x['metrics'] for x in summary['raw_runs'] if x['stage']==stage and x['variant']==name]
   report.append(f'|{stage}|{name}|'+', '.join(str(x['passed'])+'/25' for x in vals)+'|'+', '.join(str(x['area_passed'])+('' if x['area_complete'] else '*') for x in vals)+'|')
 report.extend(['','**Release gates:** '+json.dumps(gates,ensure_ascii=False),
                '', 'See `casewise_comparison.csv`, `summary.json`, direct diagnostics, and official evaluator logs.',
                'Area decreases with delay regressions are *not* Pareto improvements.'])
 (out/'EXPERIMENT_REPORT.md').write_text('\n'.join(report)+'\n')
 save();print('RESULT_DIRECTORY:',out)
 print('RELEASE_GATE:', 'PASS' if gates['r81_branch']['release_candidate'] and gates['r81_strict']['release_candidate'] else 'FAIL')
 return 0 if gates['r81_branch']['release_candidate'] and gates['r81_strict']['release_candidate'] else 2
if __name__=='__main__':
 try:raise SystemExit(main())
 except Exception as e:print('EXPERIMENT_ERROR:',repr(e),flush=True);raise

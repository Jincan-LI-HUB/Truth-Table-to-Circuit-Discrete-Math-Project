#!/usr/bin/env python3
"""Controlled 50-case Round 8 prototype paired evaluation under official evaluator.
No fabricated scoring formula; FAIL cases excluded from complete area comparisons.
"""
import argparse,csv,datetime,hashlib,json,math,os,platform,shutil,statistics,subprocess,tempfile
from pathlib import Path
H=Path(__file__).resolve().parents[1]; ROOT=H.parent

def sha(p):
 h=hashlib.sha256()
 with open(p,'rb') as f:
  for x in iter(lambda:f.read(1<<20),b''):h.update(x)
 return h.hexdigest()
def load(p):
 with p.open(newline='') as f:rows=list(csv.DictReader(f))
 if len(rows)!=25:raise RuntimeError(f'{p}: expected 25 rows got {len(rows)}')
 return {x['case']:x for x in rows}
def ok(r):return r['status']=='PASS'
def summarize(d):
 good=[r for r in d.values() if ok(r)]
 rr=[float(r['runtime_ms']) for r in good if r.get('runtime_ms')]
 area=sum(int(r['area']) for r in good)
 return {'pass':len(good),'target_met':sum(r.get('target_met')=='yes' for r in good),
         'area_passed':area,'area_complete':len(good)==len(d),
         'median_runtime_ms':round(statistics.median(rr),3) if rr else None,
         'max_runtime_ms':round(max(rr),3) if rr else None,
         'failed':[k for k,r in d.items() if not ok(r)]}
def gmean(nums):
 return round(math.exp(statistics.mean(map(math.log,nums))),6) if nums else None

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--runs',type=int,default=2)
 ap.add_argument('--quick',action='store_true',help='compare only frozen R7.2 and iterative Round8 once by default')
 ap.add_argument('--case-profiles',action='store_true',help='direct synth run of case_021 and save R8_STAGE logs')
 args=ap.parse_args()
 if args.runs<1:raise ValueError('runs must be positive')
 r72=ROOT/'UFUG2106_Round7_2_Delivery/build/synth_round72'
 r8=H/'build/synth_round8'; ev=ROOT/'evaluator'
 for f in (r72,r8,ev):
  if not f.is_file():raise RuntimeError(f'Missing {f}')
 variants=[('r72',r72,{}),('r8_iterate',r8,{'UFUG_R8_POLICY':'iterate'})]
 if not args.quick:
  variants=[('r72',r72,{}),('r8_off',r8,{'UFUG_R8_POLICY':'off'}),
   ('r8_factor',r8,{'UFUG_R8_POLICY':'factor'}),
   ('r8_reuse',r8,{'UFUG_R8_POLICY':'reuse'}),
   ('r8_strict',r8,{'UFUG_R8_POLICY':'iterate_strict'}),
   ('r8_all',r8,{'UFUG_R8_POLICY':'all'}),
   ('r8_iterate',r8,{'UFUG_R8_POLICY':'iterate'})]
 stamp=datetime.datetime.now().strftime('%Y%m%d_%H%M%S_%f');out=H/'results'/stamp;out.mkdir(parents=True)
 (H/'latest_run.txt').write_text(str(out.resolve())+'\n')
 (out/'STARTED.txt').write_text('Audit-compatible run started.\n')
 summary={'milestone':'Round 8 research prototype','run_count':args.runs,'quick':args.quick,
          'objective':'QoR-first structural optimization after R7.2 incumbent; official scoring unknown',
          'fingerprints':{'round72':sha(r72),'round8':sha(r8),'evaluator':sha(ev)},
          'host':{'platform':platform.platform(),'python':platform.python_version()},'runs':[]}
 def save(): (out/'summary.json').write_text(json.dumps(summary,indent=2,ensure_ascii=False)+'\n')
 save();joint=[]
 with tempfile.TemporaryDirectory(prefix='ufug_r8_eval_') as tmp:
  exe=Path(tmp)/'evaluator';shutil.copy2(ev,exe);exe.chmod(exe.stat().st_mode|0o111)
  for run in range(1,args.runs+1):
   for stage in ('stage1','stage2'):
    folder=(ROOT/'data'/stage).resolve()
    if not folder.is_dir():raise RuntimeError(f'Missing {folder}')
    observed={}
    order=variants if run%2 else variants[::-1]
    for label,prog,custom in order:
     report=out/f'run{run}_{stage}_{label}.csv'
     env=os.environ.copy()
     for k in ('UFUG_R8_POLICY','UFUG_R8_PROFILE','UFUG_R72_POLICY','UFUG_R71_POLICY','UFUG_R7_LEGACY_MERGE','UFUG_R7_LEGACY_COVER','UFUG_ROUND5_PROFILE'):
      env.pop(k,None)
     env.update(custom)
     proc=subprocess.run([str(exe),str(prog),str(folder),'--report',str(report)],
        stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True,errors='replace',env=env)
     (out/f'run{run}_{stage}_{label}.log').write_text(proc.stdout,encoding='utf-8')
     if not report.exists():
      summary['runs'].append({'run':run,'stage':stage,'variant':label,'failure':'missing report','exit':proc.returncode});save()
      raise RuntimeError(f'evaluator did not create {report}')
     d=load(report);observed[label]=d;sm=summarize(d)
     summary['runs'].append({'run':run,'stage':stage,'variant':label,'exit':proc.returncode,'metrics':sm,'csv':report.name})
     save();print(f'{stage} run{run} {label:14} {sm["pass"]}/25 PASS, target={sm["target_met"]}, area_passed={sm["area_passed"]}',flush=True)
    for label in observed:
     if label=='r72':continue
     base=observed['r72'];new=observed[label]
     for name in sorted(base):
      a,b=base[name],new[name];both=ok(a) and ok(b)
      oa,na=(int(a['area']),int(b['area'])) if both else ('','')
      od,nd=(int(a['delay']),int(b['delay'])) if both else ('','')
      t0,t1=(float(a['runtime_ms']),float(b['runtime_ms'])) if both else ('','')
      joint.append(dict(run=run,stage=stage,variant=label,case=name,
         base_status=a['status'],new_status=b['status'],
         base_area=oa,new_area=na,delta_area=(na-oa if both else ''),
         base_delay=od,new_delay=nd,delta_delay=(nd-od if both else ''),
         base_runtime_ms=t0,new_runtime_ms=t1,runtime_ratio=(t1/t0 if both and t0>0 else ''),
         target_met=b.get('target_met','')))
 with (out/'casewise_comparison.csv').open('w',newline='') as f:
  w=csv.DictWriter(f,list(joint[0]));w.writeheader();w.writerows(joint)
 summary['comparisons']=[]
 for stage in ('stage1','stage2'):
  for label,*_ in variants:
   if label=='r72':continue
   q=[r for r in joint if r['stage']==stage and r['variant']==label]
   common=[r for r in q if isinstance(r['delta_area'],int)]
   summary['comparisons'].append({'stage':stage,'variant':label,
    'area_delta_common_passed':sum(r['delta_area'] for r in common),
    'area_improvements':sum(r['delta_area']<0 for r in common),
    'delay_regressions':sum(r['delta_delay']>0 for r in common),
    'runtime_gmean_ratio':gmean([r['runtime_ratio'] for r in common if r['runtime_ratio']]),
    'new_failures':[r['case'] for r in q if r['base_status']=='PASS' and r['new_status']!='PASS']})
 if args.case_profiles:
  diag=out/'diagnostics';diag.mkdir(exist_ok=True)
  for stage,case in (('stage2','case_021'),('stage2','case_016'),('stage1','case_020')):
   src=ROOT/'data'/stage/(case+'.txt')
   if not src.exists():continue
   for label,prog,custom in (('r72',r72,{}),('r8_iterate',r8,{'UFUG_R8_POLICY':'iterate','UFUG_R8_PROFILE':'1'})):
    fn=diag/f'{stage}_{case}_{label}.txt'
    env={**os.environ,**custom};run=subprocess.run([str(prog),str(src),str(fn)],capture_output=True,text=True,env=env,timeout=120)
    (diag/f'{stage}_{case}_{label}.log').write_text(run.stdout+run.stderr)
    if run.returncode:raise RuntimeError(f'diagnostic failed: {case} {label}')
 feasible=all(x['metrics']['pass']==25 and x['metrics']['target_met']==25 for x in summary['runs'] if x['variant']=='r8_iterate')
 iterate=[r for r in joint if r['variant']=='r8_iterate']
 quality=all(not isinstance(r['delta_area'],int) or r['delta_area']<=0 for r in iterate)
 summary['release_gate']={'feasibility':feasible,'no_area_regression_on_common_pass':quality}
 lines=['# Round 8 Prototype — official paired experiment','','This is an experiment, not an official grading formula.',
  f'**Feasibility gate:** {feasible}; **area regression gate:** {quality}',
  '', '| Stage | Variant | Runs PASS | Area sum of passed |','|---|---|---|---|']
 for stage in ('stage1','stage2'):
  for label,*_ in variants:
   vals=[x['metrics'] for x in summary['runs'] if x['stage']==stage and x['variant']==label]
   lines.append(f'|{stage}|{label}|'+', '.join(f'{v["pass"]}/25' for v in vals)+'|'+', '.join(str(v['area_passed'])+('' if v['area_complete'] else '*') for v in vals)+'|')
 lines+=['','* means the area sum is incomplete because some case failed.','',
  'See casewise_comparison.csv and raw official evaluator logs; direct-run diagnostics are not official timings.']
 (out/'EXPERIMENT_REPORT.md').write_text('\n'.join(lines)+'\n')
 save();print('RESULT_DIRECTORY:',out);print('RELEASE_GATE:', 'PASS' if feasible and quality else 'FAIL')
 return 0 if feasible and quality else 2
if __name__=='__main__':
 try:raise SystemExit(main())
 except Exception as e:print('EXPERIMENT_ERROR:',repr(e),flush=True);raise

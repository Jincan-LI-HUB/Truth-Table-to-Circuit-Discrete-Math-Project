#!/usr/bin/env python3
"""R7.2 paired official evaluation, per-case quality assessment, ablations.
Does not invent an official grade; FAIL area is never counted as if a success.
See docs/EXPERIMENT_PROTOCOL.md. Requires instructor evaluator and stage{1,2}.
"""
from __future__ import annotations
import argparse,csv,datetime,hashlib,json,math,os,platform,shutil,statistics,subprocess,sys,tempfile
from pathlib import Path
HERE=Path(__file__).resolve().parents[1]
ROOT=HERE.parent

def sha(p):
    h=hashlib.sha256()
    with open(p,'rb') as f:
        for v in iter(lambda:f.read(1<<20),b''):h.update(v)
    return h.hexdigest()

def load_csv(p):
    with p.open(newline='') as f:
        d=list(csv.DictReader(f))
    if len(d)!=25:raise RuntimeError(f'Expected 25 test cases in {p}, got {len(d)}')
    key='case' if 'case' in d[0] else 'case_file'
    return {r[key]:r for r in d}

def pass_row(r):return r.get('status')=='PASS'
def number(r,key):
    try:return float(r[key])
    except (ValueError,TypeError,KeyError):return None

def metric(d):
    p=[v for v in d.values() if pass_row(v)]
    rr=[number(v,'runtime_ms') for v in p];rr=[x for x in rr if x is not None]
    area=[number(v,'area') for v in p];area=[x for x in area if x is not None]
    return {'pass_count':len(p),'target_met':sum(x.get('target_met')=='yes' for x in p),
       'area_sum_of_passed':int(sum(area)),'area_complete':len(p)==len(d),
       'median_runtime_ms':round(statistics.median(rr),4) if rr else None,
       'p95_runtime_ms':round(sorted(rr)[int((len(rr)-1)*.95)],4) if rr else None,
       'worst_runtime_fraction':max((number(x,'runtime_ms')/number(x,'runtime_limit_ms')
          for x in p if number(x,'runtime_ms') is not None and number(x,'runtime_limit_ms')),default=None),
       'failures':[k for k,v in d.items() if not pass_row(v)]}

def compare(base,candidate,run,stage,label):
    rows=[]
    for name in sorted(base):
        a,b=base[name],candidate[name]
        oldok,newok=pass_row(a),pass_row(b)
        ao,an=number(a,'area'),number(b,'area')
        do,dn=number(a,'delay'),number(b,'delay')
        to,tn=number(a,'runtime_ms'),number(b,'runtime_ms')
        valid=oldok and newok
        rows.append({'run':run,'stage':stage,'variant':label,'case':name,
            'old_status':a.get('status'),'new_status':b.get('status'),
            'old_area':ao if oldok else '', 'new_area':an if newok else '',
            'area_delta':an-ao if valid else '', 'old_delay':do if oldok else '',
            'new_delay':dn if newok else '', 'delay_delta':dn-do if valid else '',
            'old_runtime_ms':to if oldok else '', 'new_runtime_ms':tn if newok else '',
            'runtime_ratio':tn/to if valid and to and tn else '',
            'area_ratio':an/ao if valid and ao else '',
            'new_target_met':b.get('target_met',''),
            'quality_regression':int(valid and (an>ao or dn>do))})
    return rows

def geometric(vals):
    xs=[float(x) for x in vals if isinstance(x,(int,float)) and x>0]
    return round(math.exp(statistics.mean(math.log(x) for x in xs)),6) if xs else None

def main():
    p=argparse.ArgumentParser();p.add_argument('--runs',type=int,default=2)
    p.add_argument('--quick',action='store_true',help='Only the frozen R7.1 and R7.2 shortlisted variants')
    p.add_argument('--diagnostic-runs',type=int,default=3)
    a=p.parse_args()
    if a.runs<1:raise SystemExit('Need --runs >= 1')
    src=ROOT/'UFUG2106_Round5.1_Delivery/build/synth_round51'
    r71=ROOT/'UFUG2106_Round7_1_Delivery/build/synth_round71'
    r72=HERE/'build/synth_round72'
    evaluator=ROOT/'evaluator'
    for x in ([r71,r72,evaluator] if a.quick else [src,r71,r72,evaluator]):
        if not x.is_file():raise SystemExit(f'Missing executable: {x}')
    stamp=datetime.datetime.now().strftime('%Y%m%d_%H%M%S_%f')
    out=HERE/'results'/stamp;out.mkdir(parents=True)
    (HERE/'latest_run.txt').write_text(str(out.resolve())+'\n')
    (out/'STARTED.txt').write_text('Run created. Failed runs should still be packaged.\n')
    variants=[('r71_guard',r71,{}),('r72_shortlist',r72,{'UFUG_R72_POLICY':'shortlist'})]
    if not a.quick:
        variants=[('r51',src,{}),*variants,
           ('r72_guard',r72,{'UFUG_R72_POLICY':'guard'}),
           ('r72_nocancel',r72,{'UFUG_R72_POLICY':'shortlist_nocancel'})]
    summary={'milestone':'Round 7.2','official_grading_formula':'not provided',
       'conditions':{'runs':a.runs,'quick':a.quick,'diagnostic_reps':a.diagnostic_runs,
           'variants':[x[0] for x in variants],
           'core_hypothesis':'short-budget bounded cubemode0 legacy candidate recovers QoR'},
       'fingerprints':{'evaluator':sha(evaluator),'round71':sha(r71),'round72':sha(r72),
           'round51':sha(src) if src.is_file() else None},
       'machine':{'platform':platform.platform(),'python':platform.python_version()},
       'runs':[],'casewise_file':'casewise_comparison.csv'}
    def save():
        (out/'summary.json').write_text(json.dumps(summary,indent=2,ensure_ascii=False)+'\n')
    save()
    allrows=[]
    with tempfile.TemporaryDirectory(prefix='ufug_r72_eval_') as tmp:
        ev=Path(tmp)/'evaluator';shutil.copy2(evaluator,ev);ev.chmod(ev.stat().st_mode|0o111)
        for rep in range(1,a.runs+1):
            order=variants if rep%2 else list(reversed(variants))
            for stage in ('stage1','stage2'):
                folder=(ROOT/'data'/stage).resolve()
                if not folder.is_dir():raise RuntimeError(f'Missing truth tables: {folder}')
                observed={}
                for label,exe,extra in order:
                    target=out/f'run{rep}_{stage}_{label}.csv'
                    env=os.environ.copy()
                    for k in ['UFUG_R72_POLICY','UFUG_R71_POLICY','UFUG_R71_TRACE',
                              'UFUG_R7_LEGACY_MERGE','UFUG_R7_LEGACY_COVER','UFUG_ROUND5_PROFILE']:
                        env.pop(k,None)
                    env.update(extra)
                    cmd=[str(ev),str(exe),str(folder),'--report',str(target)]
                    proc=subprocess.run(cmd,env=env,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,
                        text=True,errors='replace')
                    (out/f'run{rep}_{stage}_{label}.log').write_text(proc.stdout,encoding='utf-8')
                    if not target.exists():
                        summary['runs'].append({'run':rep,'stage':stage,'variant':label,
                            'evaluator_exit':proc.returncode,'error':'MISSING_REPORT'})
                        save();raise RuntimeError(f'Missing official evaluator report {target.name}')
                    d=load_csv(target);observed[label]=d
                    statistics_=metric(d)
                    summary['runs'].append({'run':rep,'stage':stage,'variant':label,
                       'evaluator_exit':proc.returncode,'report':target.name,'metrics':statistics_})
                    save()
                    print(f'{stage} run{rep} {label:18s} '
                       f'{statistics_["pass_count"]}/25 PASS, target={statistics_["target_met"]}, '
                       f'area_passed={statistics_["area_sum_of_passed"]}',flush=True)
                old=observed['r71_guard']
                for label in observed:
                    if label!='r71_guard':allrows.extend(compare(old,observed[label],rep,stage,label))
    if allrows:
        with (out/'casewise_comparison.csv').open('w',newline='',encoding='utf-8') as f:
            w=csv.DictWriter(f,fieldnames=list(allrows[0]));w.writeheader();w.writerows(allrows)
    summary['comparisons']=[]
    for rep in range(1,a.runs+1):
        for stage in ('stage1','stage2'):
            for label,_,_ in variants:
                if label=='r71_guard':continue
                q=[x for x in allrows if x['run']==rep and x['stage']==stage and x['variant']==label]
                summary['comparisons'].append({'run':rep,'stage':stage,'variant':label,
                   'jointly_passed':sum(x['old_status']=='PASS' and x['new_status']=='PASS' for x in q),
                   'area_delta_on_common_pass':sum(x['area_delta'] for x in q if isinstance(x['area_delta'],(float,int))),
                   'area_geomean_ratio':geometric([x['area_ratio'] for x in q]),
                   'runtime_geomean_ratio':geometric([x['runtime_ratio'] for x in q]),
                   'regressions':[x['case'] for x in q if x['quality_regression']],
                   'failures_recovered':[x['case'] for x in q if x['old_status']!='PASS' and x['new_status']=='PASS'],
                   'new_failures':[x['case'] for x in q if x['old_status']=='PASS' and x['new_status']!='PASS']})
    save()
    if a.diagnostic_runs:
        cmd=[sys.executable,str(HERE/'tools/profile_critical.py'),'--runs',str(a.diagnostic_runs),
            '--output',str(out/'diagnostics')]
        pr=subprocess.run(cmd,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True,errors='replace')
        (out/'diagnostics_driver.log').write_text(pr.stdout,encoding='utf-8')
        summary['diagnostics_exit']=pr.returncode
        print('critical-case diagnostics:',pr.returncode,flush=True)
        save()
    top=[x for x in summary['runs'] if x['variant']=='r72_shortlist']
    feasible=(len(top)==2*a.runs and all(x['metrics']['pass_count']==25 and
             x['metrics']['target_met']==25 for x in top))
    regress=[x for x in summary['comparisons'] if x['variant']=='r72_shortlist' and x['regressions']]
    quality_ok=not regress
    summary['release_gate_public_50_pass_target']=feasible
    summary['quality_gate_vs_round71']=quality_ok
    report=['# Round 7.2 — WSL Official Paired Evaluation','',
      f'**Correctness/target gate:** {"PASS" if feasible else "FAIL"}',
      f'**No per-case area/delay regression relative to R7.1 Guard:** {"PASS" if quality_ok else "FAIL"}',
      '', '| Stage | Variant | PASS per run | Sum of area on passed cases per run |',
       '|---|---|---|---|']
    for stage in ('stage1','stage2'):
        for label,_,_ in variants:
            data=[x['metrics'] for x in summary['runs'] if x['stage']==stage and x['variant']==label]
            report.append(f'| {stage} | {label} | '+', '.join(str(x['pass_count'])+'/25' for x in data)
              +' | '+', '.join(str(x['area_sum_of_passed'])+('' if x['area_complete'] else '*') for x in data)+' |')
    report += ['','*An asterisk denotes incomplete area because at least one case failed.*',
      'No official grading formula is implied. Direct profiles are NOT official timing.',
      'Quality regression report compares every jointly passing case to R7.1 Guard.',
      '', '## Pre-registered hypotheses',
      '- H1: R7.2 shortlist recovers Stage1 case020 QoR without worsening Stage2 case016 QoR.',
      '- H2: R7.2 shortlist remains within the official 100ms constraint for both cases.',
      '- H3: Most larger-budget cases remain byte-for-byte quality-equivalent to R7.1.',
      'See casewise_comparison.csv and all per-run original evaluator logs for evidence.',
      '']
    (out/'EXPERIMENT_REPORT.md').write_text('\n'.join(report),encoding='utf-8')
    save()
    print('RESULT_DIRECTORY:',out,flush=True)
    print('RELEASE_GATE:', 'PASS' if feasible else 'FAIL',flush=True)
    print('QUALITY_GATE:', 'PASS' if quality_ok else 'FAIL',flush=True)
    return 0 if feasible and quality_ok else 2
if __name__=='__main__':
    try:raise SystemExit(main())
    except Exception as exc:print('EXPERIMENT_ERROR:',repr(exc),flush=True);raise

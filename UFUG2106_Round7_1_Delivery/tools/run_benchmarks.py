#!/usr/bin/env python3
"""All 50 public cases; paired same-host R5.1 vs R7.1 with independent ablations.
Writes every result before proceeding. DOES NOT invent a score or include FAIL area
in complete-area totals. A return code of 2 means the release gate is not met.
"""
from __future__ import annotations
import argparse, csv, datetime, hashlib, json, math, os, platform, shutil, statistics, subprocess, sys, tempfile
from pathlib import Path
HERE=Path(__file__).resolve().parents[1]
ROOT=HERE.parent

def sha256(p):
    h=hashlib.sha256()
    with open(p,'rb') as f:
        for data in iter(lambda:f.read(1<<20),b''):h.update(data)
    return h.hexdigest()

def read_csv(p):
    with open(p,newline='',encoding='utf-8') as f:
        return {r['case']:r for r in csv.DictReader(f)}

def metrics(d):
    p=[v for v in d.values() if v.get('status')=='PASS']
    a=sum(int(v['area']) for v in p if v.get('area'))
    t=[float(v['runtime_ms']) for v in p if v.get('runtime_ms')]
    return {'total':len(d),'passed':len(p),'target_met':sum(v.get('target_met')=='yes' for v in p),
      'area_sum_of_passed':a,'area_sum_complete':len(p)==len(d),
      'median_passed_runtime_ms':statistics.median(t) if t else None,
      'max_passed_runtime_ms':max(t) if t else None,
      'failures':[v['case'] for v in d.values() if v.get('status')!='PASS']}

def paired_comparison(reference,candidate):
    out=[]
    for key in sorted(reference.keys() & candidate.keys()):
        a,b=reference[key],candidate[key]
        pair={'case':key,'old_status':a.get('status'), 'new_status':b.get('status'),
            'old_area':a.get('area'), 'new_area':b.get('area'),
            'old_delay':a.get('delay'),'new_delay':b.get('delay'),
            'old_runtime_ms':a.get('runtime_ms'),'new_runtime_ms':b.get('runtime_ms')}
        if a.get('status')=='PASS' and b.get('status')=='PASS':
            pair['area_ratio']=float(b['area'])/float(a['area']) if int(a['area']) else None
            pair['area_delta']=int(b['area'])-int(a['area'])
            pair['delay_delta']=int(b['delay'])-int(a['delay'])
        else:pair['area_ratio']=pair['area_delta']=pair['delay_delta']=None
        out.append(pair)
    return out

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--runs',type=int,default=2)
    parser.add_argument('--quick',action='store_true',help='Only R5.1 + R7.1 default (both stages); no research ablations')
    parser.add_argument('--case-profile-runs',type=int,default=3)
    args=parser.parse_args()
    if args.runs<1:raise SystemExit('--runs must be positive')
    r71=(HERE/'build/synth_round71').resolve()
    r51=(ROOT/'UFUG2106_Round5.1_Delivery/build/synth_round51').resolve()
    evaluator=(ROOT/'evaluator').resolve()
    for f in (r71,r51,evaluator):
        if not f.is_file():raise SystemExit(f'Missing executable: {f}')
    run_dir=HERE/'results'/datetime.datetime.now().strftime('%Y%m%d_%H%M%S_%f')
    run_dir.mkdir(parents=True)
    (HERE/'latest_run.txt').write_text(str(run_dir)+'\n',encoding='utf-8')
    (run_dir/'STARTED.txt').write_text('A nonzero exit does not delete results.\n')
    variants=[('r51',r51,{}) , ('r71_guard',r71,{}),('r71_policy_off',r71,{'UFUG_R71_POLICY':'off'})]
    if not args.quick:
        variants += [('r71_legacy_merge',r71,{'UFUG_R7_LEGACY_MERGE':'1'}),
                     ('r71_legacy_cover',r71,{'UFUG_R7_LEGACY_COVER':'1'})]
    summary={'experiment':'Round7.1 paired official evaluator','runs':[], 'comparisons':[],
       'conditions':{'repetitions':args.runs,'variants':[v[0] for v in variants],
           'stage1_and_stage2':True,'default_policy':'guard'},
       'machine':{'platform':platform.platform(),'python':platform.python_version(),
           'evaluator_sha256':sha256(evaluator),'r51_sha256':sha256(r51),'r71_sha256':sha256(r71)}}
    (run_dir/'summary.json').write_text(json.dumps(summary,indent=2)+'\n')
    with tempfile.TemporaryDirectory(prefix='r71_official_') as tmp:
        real_eval=Path(tmp)/'evaluator';shutil.copy2(evaluator,real_eval)
        real_eval.chmod(real_eval.stat().st_mode|0o111)
        for k in range(1,args.runs+1):
            for st in ('stage1','stage2'):
                case_dir=(ROOT/'data'/st).resolve()
                if not case_dir.is_dir():raise SystemExit(f'Missing dataset: {case_dir}')
                ordered=variants if k%2 else list(reversed(variants))
                for name,program,extra in ordered:
                    out=run_dir/f'run{k}_{st}_{name}.csv'
                    env=os.environ.copy()
                    for f in ('UFUG_R71_POLICY','UFUG_R71_TRACE','UFUG_R7_LEGACY_MERGE','UFUG_R7_LEGACY_COVER','UFUG_ROUND5_PROFILE'):
                        env.pop(f,None)
                    env.update(extra)
                    command=[str(real_eval),str(program),str(case_dir),'--report',str(out)]
                    proc=subprocess.run(command,env=env,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True,errors='replace')
                    (run_dir/f'run{k}_{st}_{name}.log').write_text(proc.stdout,encoding='utf-8')
                    if not out.exists():
                        summary['runs'].append({'run':k,'stage':st,'variant':name,'error':'missing CSV',
                            'evaluator_exit':proc.returncode})
                        (run_dir/'summary.json').write_text(json.dumps(summary,indent=2)+'\n')
                        raise RuntimeError(f'No CSV from evaluator: {out.name}')
                    result=read_csv(out)
                    if len(result)!=25:raise RuntimeError(f'Expected 25 cases: {out}, got {len(result)}')
                    stats=metrics(result)
                    summary['runs'].append({'run':k,'stage':st,'variant':name,
                       'csv':out.name,'evaluator_exit':proc.returncode,'metrics':stats})
                    (run_dir/'summary.json').write_text(json.dumps(summary,indent=2)+'\n')
                    print(f'{st} run{k} {name:18s} {stats["passed"]}/25 PASS, target={stats["target_met"]}, area_passed={stats["area_sum_of_passed"]}',flush=True)
                baseline=read_csv(run_dir/f'run{k}_{st}_r51.csv')
                for name,_,_ in ordered:
                    if name=='r51':continue
                    pairs=paired_comparison(baseline,read_csv(run_dir/f'run{k}_{st}_{name}.csv'))
                    complete=[x for x in pairs if x['area_ratio'] is not None]
                    summary['comparisons'].append({'run':k,'stage':st,'variant':name,
                       'common_passed':len(complete),
                       'gmean_area_ratio':math.exp(statistics.mean(math.log(x['area_ratio']) for x in complete)) if complete else None,
                       'common_area_delta':sum(x['area_delta'] for x in complete),
                       'new_failures':[x['case'] for x in pairs if x['old_status']=='PASS' and x['new_status']!='PASS'],
                       'failure_recovered':[x['case'] for x in pairs if x['old_status']!='PASS' and x['new_status']=='PASS']})
                (run_dir/'summary.json').write_text(json.dumps(summary,indent=2)+'\n')
    cases=[]
    for k in range(1,args.runs+1):
        for st in ('stage1','stage2'):
            baseline=read_csv(run_dir/f'run{k}_{st}_r51.csv')
            for name,_,_ in variants:
                if name=='r51':continue
                for x in paired_comparison(baseline,read_csv(run_dir/f'run{k}_{st}_{name}.csv')):
                    cases.append({'run':k,'stage':st,'variant':name,**x})
    if cases:
        with (run_dir/'casewise_comparison.csv').open('w',newline='',encoding='utf-8') as f:
            w=csv.DictWriter(f,fieldnames=cases[0].keys());w.writeheader();w.writerows(cases)
    # Cross-stage quality metric on jointly passing cases only; do not impute
    # zero area to an old/new failure. Recovery is reported by stage above.
    summary['joint_comparisons']=[]
    for k in range(1,args.runs+1):
        for label,_,_ in variants:
            if label=='r51':continue
            parts=[q for q in summary['comparisons']
                   if q['run']==k and q['variant']==label]
            if len(parts)!=2:continue
            n=sum(q['common_passed'] for q in parts)
            if n==0:continue
            logsum=sum(q['common_passed']*math.log(q['gmean_area_ratio'])
                       for q in parts if q['common_passed'] and q['gmean_area_ratio'])
            summary['joint_comparisons'].append({
              'run':k,'variant':label,'common_passed':n,
              'joint_gmean_area_ratio':math.exp(logsum/n),
              'joint_common_area_delta':sum(q['common_area_delta'] for q in parts),
              'old_failures_recovered':{q['stage']:q['failure_recovered'] for q in parts},
              'new_failures':{q['stage']:q['new_failures'] for q in parts}})
    # Diagnostic runs intentionally outside the official 100 ms timeout.
    if args.case_profile_runs>0:
        command=[sys.executable,str(HERE/'tools/profile_case016.py'), '--runs',str(args.case_profile_runs),'--output',str(run_dir/'diagnostics')]
        diag=subprocess.run(command,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True,errors='replace')
        (run_dir/'diagnostics_driver.log').write_text(diag.stdout,encoding='utf-8')
        summary['diagnostics_exit']=diag.returncode
        print('case016 diagnostics:',diag.returncode,flush=True)
    base=[x for x in summary['runs'] if x['variant']=='r71_guard']
    gate=all(x['metrics']['passed']==25 and x['metrics']['target_met']==25 for x in base) and len(base)==2*args.runs
    summary['release_gate_public_50_pass_target']=gate
    (run_dir/'summary.json').write_text(json.dumps(summary,indent=2,ensure_ascii=False)+'\n')
    lines=['# Round 7.1 — Local Paired Experiment','',
      f'- Official-evaluator release gate: **{"PASS" if gate else "FAIL"}**',
      f'- Runs: {args.runs}; variants: {", ".join(v[0] for v in variants)}','',
      '| Stage | Version | PASS counts | Area sums of passed |','|---|---|---|---|']
    for st in ('stage1','stage2'):
        for name,_,_ in variants:
            rr=[x['metrics'] for x in summary['runs'] if x['stage']==st and x['variant']==name]
            passed_str=", ".join(str(q["passed"])+"/25" for q in rr)
            area_str=", ".join(str(q["area_sum_of_passed"])+( "*" if not q["area_sum_complete"] else "") for q in rr)
            lines.append(f"| {st} | {name} | {passed_str} | {area_str} |")
    lines += ['','*Asterisk: area sum excludes a failed case; never compare it as a complete 25-case score.*',
       '', 'The official grading formula is unknown. Failed cases cannot be assigned area zero.',
       'The bundled diagnostic runs are not official time-limited measurements.']
    (run_dir/'EXPERIMENT_REPORT.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
    print('RESULT_DIRECTORY:',run_dir,flush=True)
    print('RELEASE_GATE:', 'PASS' if gate else 'FAIL',flush=True)
    return 0 if gate else 2
if __name__=='__main__':
    try:raise SystemExit(main())
    except Exception as exc:
        print('EXPERIMENT_ERROR:',repr(exc),flush=True)
        raise

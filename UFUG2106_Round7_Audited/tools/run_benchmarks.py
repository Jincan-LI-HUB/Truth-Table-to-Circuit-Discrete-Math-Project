#!/usr/bin/env python3
"""Paired, repeatable official-evaluator runs for both public data stages.

Invokes exactly the user's local `evaluator PROGRAM BENCHMARK_FOLDER --report FILE`.
Source and output filenames are preserved; no invented grading formula.
"""
from __future__ import annotations
import argparse
import csv
import datetime as dt
import hashlib
import json
import math
import os
import platform
import shutil
import statistics
import subprocess
import tempfile
from pathlib import Path

DELIVERY = Path(__file__).resolve().parents[1]
DEFAULT_ROOT = DELIVERY.parent

def digest(p):
    h=hashlib.sha256()
    with open(p,'rb') as f:
        for block in iter(lambda:f.read(1<<20),b''):h.update(block)
    return h.hexdigest()

def rows(p):
    with open(p,newline='',encoding='utf-8') as f:return {r['case']:r for r in csv.DictReader(f)}

def stat(r):
    passrows=[x for x in r.values() if x.get('status')=='PASS']
    times=[float(x['runtime_ms']) for x in passrows if x.get('runtime_ms')]
    areas=[int(x['area']) for x in passrows if x.get('area')]
    return {
        'total_cases':len(r), 'passed':len(passrows),
        'target_met':sum(x.get('target_met')=='yes' for x in passrows),
        'area_sum_of_passed':sum(areas),
        'area_sum_is_complete':len(passrows)==len(r),
        'median_passed_runtime_ms':statistics.median(times) if times else None,
        'max_passed_runtime_ms':max(times) if times else None,
        'failure_cases':[x['case'] for x in r.values() if x['status']!='PASS'],
    }

def compare(a,b):
    common=[];improved=[];regressed=[];equal=[];delay_regr=[]
    for name in sorted(a.keys() & b.keys()):
        aa=a[name]; bb=b[name]
        if aa['status']!='PASS' or bb['status']!='PASS':continue
        old=int(aa['area']);new=int(bb['area']);common.append((name,old,new))
        if new<old:improved.append(name)
        elif new>old:regressed.append(name)
        else:equal.append(name)
        if int(bb['delay'])>int(aa['delay']):delay_regr.append(name)
    gmean=math.exp(statistics.mean(math.log(new/old) for _,old,new in common)) if common else None
    return {
      'common_passed_count':len(common),
      'aggregate_common_area_old':sum(old for _,old,new in common),
      'aggregate_common_area_new':sum(new for _,old,new in common),
      'common_area_improved_cases':improved,
      'common_area_regressed_cases':regressed,
      'common_area_equal_cases':equal,
      'delay_regressed_cases':delay_regr,
      'geometric_mean_area_ratio':gmean,
      'failure_recovery':[name for name in sorted(a.keys() & b.keys()) if a[name]['status']!='PASS' and b[name]['status']=='PASS'],
      'new_failures':[name for name in sorted(a.keys() & b.keys()) if a[name]['status']=='PASS' and b[name]['status']!='PASS'],
    }

def evaluate(evaluator, program, cases, dest, env=None):
    cmd=[str(evaluator), str(program), str(cases),'--report',str(dest)]
    proc=subprocess.run(cmd,env=env,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True)
    (dest.with_suffix('.log')).write_text(proc.stdout,encoding='utf-8')
    if not dest.is_file():
        raise RuntimeError('Evaluator did not produce CSV: '+proc.stdout[-2000:])
    data=rows(dest)
    if not data:raise RuntimeError('Evaluator produced an empty report')
    print(f'  {program.name:>16} | {cases.name:<6} | {len([v for v in data.values() if v["status"]=="PASS"])}/{len(data)} PASS | report {dest.name}')
    return {'command':cmd,'exit_code':proc.returncode,'csv':str(dest),'sha256':digest(dest),'metrics':stat(data)}

def main():
    p=argparse.ArgumentParser()
    p.add_argument('--root',type=Path,default=DEFAULT_ROOT,help='Final Project repository root')
    p.add_argument('--runs',type=int,default=2)
    p.add_argument('--paired',action='store_true',help='Rerun frozen Round 5.1 in alternating order in each repetition')
    p.add_argument('--ablate',action='store_true',help='Additionally test old merge, old greedy, and both old modes')
    args=p.parse_args()
    if args.runs<1:raise SystemExit('--runs must be >= 1')
    root=args.root.resolve()
    exe=(DELIVERY/'build/synth_round7').resolve()
    old=(root/'UFUG2106_Round5.1_Delivery/build/synth_round51').resolve()
    if not exe.is_file():raise SystemExit('First compile with make -C UFUG2106_Round7_Delivery')
    if args.paired and not old.is_file():raise SystemExit(f'Missing frozen Round 5.1 executable: {old}')
    original=root/'evaluator'
    if not original.is_file():raise SystemExit(f'Missing official evaluator: {original}')
    folder=DELIVERY/'results'/'round7'/dt.datetime.now().strftime('%Y%m%d_%H%M%S')
    folder.mkdir(parents=True,exist_ok=False)
    baseline={s:rows(DELIVERY/'results'/'baseline'/f'round51_{s}.csv') for s in ('stage1','stage2')}
    summary={'environment':{'platform':platform.platform(), 'python':platform.python_version(),
        'processor':platform.processor(), 'r7_binary_sha256':digest(exe),
        'r51_binary_sha256':digest(old) if old.is_file() else None,
        'evaluator_sha256':digest(original)},
      'runs':[], 'frozen_baseline':{s:stat(baseline[s]) for s in baseline},
      'comparisons':[]}
    variations=[('default',{})]
    if args.ablate:
        variations.extend([
            ('legacy_merge',{'UFUG_R7_LEGACY_MERGE':'1'}),
            ('legacy_cover',{'UFUG_R7_LEGACY_COVER':'1'}),
            ('legacy_both',{'UFUG_R7_LEGACY_MERGE':'1','UFUG_R7_LEGACY_COVER':'1'}),
        ])
    with tempfile.TemporaryDirectory(prefix='r7_evaluator_') as tmp:
        official=Path(tmp)/'evaluator'
        shutil.copy2(original,official);official.chmod(official.stat().st_mode|0o111)
        for k in range(1,args.runs+1):
            for stage in ('stage1','stage2'):
                cases=(root/'data'/stage).resolve()
                if not cases.is_dir():raise SystemExit(f'Missing test folder: {cases}')
                tasks=[]
                if args.paired:
                    tasks.append(('round51',old,{}))
                tasks.extend((variant,exe,environment) for variant,environment in variations)
                if args.paired and k%2==0:tasks.reverse()
                for label,program,extra_env in tasks:
                    env=os.environ.copy()
                    env.pop('UFUG_R7_LEGACY_MERGE',None)
                    env.pop('UFUG_R7_LEGACY_COVER',None)
                    env.pop('UFUG_ROUND5_PROFILE',None)  # avoid I/O/profiling noise in official timings
                    env.update(extra_env)
                    out=folder/f'run{k}_{stage}_{label}.csv'
                    record=evaluate(official,program,cases,out,env=env)
                    record.update({'iteration':k,'stage':stage,'variant':label})
                    summary['runs'].append(record)
                    (folder/'summary.json').write_text(json.dumps(summary,indent=2,ensure_ascii=False)+'\n')
                # Compute comparisons only after every variant in the pair is available.
                for label,_,_ in tasks:
                    if label=='round51':continue
                    variant_rows=rows(folder/f'run{k}_{stage}_{label}.csv')
                    base=rows(folder/f'run{k}_{stage}_round51.csv') if args.paired else baseline[stage]
                    summary['comparisons'].append({'iteration':k,'stage':stage,'variant':label,
                        'baseline':'paired' if args.paired else 'frozen',**compare(base,variant_rows)})
                (folder/'summary.json').write_text(json.dumps(summary,indent=2,ensure_ascii=False)+'\n')
    # Cross-stage quality metric is computed only on paired PASS/PASS cases;
    # recovered failures are reported separately instead of being assigned zero area.
    summary['joint_comparisons']=[]
    for k in range(1,args.runs+1):
        for label,_ in variations:
            parts=[x for x in summary['comparisons']
                   if x['iteration']==k and x['variant']==label]
            if len(parts)!=2:continue
            n=sum(x['common_passed_count'] for x in parts)
            if not n:continue
            joint_geo=math.exp(sum(
                x['common_passed_count']*math.log(x['geometric_mean_area_ratio'])
                for x in parts if x['common_passed_count'])/n)
            summary['joint_comparisons'].append({
                'iteration':k,'variant':label,
                'stages':[x['stage'] for x in parts],
                'common_passed_count':n,
                'joint_geometric_mean_area_ratio':joint_geo,
                'common_area_sum_before':sum(x['aggregate_common_area_old'] for x in parts),
                'common_area_sum_after':sum(x['aggregate_common_area_new'] for x in parts),
                'newly_recovered_failures':{x['stage']:x['failure_recovery'] for x in parts},
                'new_regressions':{x['stage']:x['new_failures'] for x in parts},
            })
    (folder/'summary.json').write_text(json.dumps(summary,indent=2,ensure_ascii=False)+'\n')
    print(f'\nResults: {folder}')
    all_default=[v for v in summary['runs'] if v['variant']=='default']
    for t in all_default:
        print(f'  {t["stage"]} run{t["iteration"]}: {t["metrics"]["passed"]}/25 PASS, '
              f'target={t["metrics"]["target_met"]}, area={t["metrics"]["area_sum_of_passed"]}')
    if any(t['metrics']['passed']!=25 or t['metrics']['target_met']!=25 for t in all_default):
        print('RELEASE GATE NOT MET: at least one official evaluation failed or missed its delay target.')
        raise SystemExit(2)
    print('RELEASE GATE MET (public cases only): all default runs PASS and meet targets.')

if __name__=='__main__':main()

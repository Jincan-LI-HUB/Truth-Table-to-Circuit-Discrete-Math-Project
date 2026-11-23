#!/usr/bin/env python3
"""Frozen unseen-case paired robustness gate; exact truth verification, time/RSS.
Outputs data and diagnostics on failures. Never claims hidden-case performance.
"""
import argparse, csv, hashlib, json, math, os, re, shutil, statistics, subprocess, time
from pathlib import Path

H=Path(__file__).resolve().parents[1]
VARIANTS=[('r86_baseline','synth_round86','UFUG_R86_POLICY','baseline'),
          ('r86_extra_sop','synth_round86','UFUG_R86_POLICY','extra_sop'),
          ('r85_reclaim','synth_round85_frozen','UFUG_R85_POLICY','budget_reclaim')]
QUICK_IDS={1,2,4,7,11,15,16,18,20,25,29,34}
FIELDS=['run','case','family','n','m','runtime_limit_ms','variant','return_code','exact','target_met',
        'area','delay','wall_ms','peak_rss_kib','runtime_budget_ratio','wall_hit_count','work_hit_count',
        'net_sha256','error']

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()

def evaluate(case,variant,run,out,metadata):
    _,binary,env_key,policy=variant
    input_path=H/'holdouts'/metadata['file'];exe=H/'build'/binary;valid=H/'build/verify_exhaustive'
    stem=f"{case:03d}_run{run}_{variant[0]}"
    net=out/'nets'/f'{stem}.net';log=out/'logs'/f'{stem}.log';peak=out/'logs'/f'{stem}.rss'
    data={'run':run,'case':f'{case:03d}','family':metadata['family'],'n':metadata['n'],
          'm':metadata['m'],'runtime_limit_ms':metadata['runtime_limit_ms'],
          'variant':variant[0],'return_code':None,'exact':False,'target_met':None,
          'area':None,'delay':None,'wall_ms':None,'peak_rss_kib':None,
          'runtime_budget_ratio':None,'wall_hit_count':0,'work_hit_count':0,'net_sha256':'','error':''}
    env=os.environ.copy()
    for k in list(env):
        if k.startswith(('UFUG_R','UFUG_ROUND')):env.pop(k)
    env.update(UFUG_R71_POLICY='guard',UFUG_R8_POLICY='off',UFUG_R81_POLICY='off',
      UFUG_R82_POLICY='off',UFUG_R83_POLICY='off',UFUG_R84_POLICY='off',
      UFUG_R85_POLICY='off',UFUG_R86_POLICY='off',UFUG_R85_PROFILE='1',UFUG_R86_PROFILE='1')
    env[env_key]=policy
    binary_call=[str(exe),str(input_path),str(net)]
    if shutil.which('/usr/bin/time'):
        command=['/usr/bin/time','-f','PEAK_RSS_KIB=%M','-o',str(peak)]+binary_call
    else:command=binary_call
    # Independent supervisor timeout: avoid a hung stress case blocking the bank.
    # Not equal to the course evaluator's hard wall-time measurement.
    supervisor=max(8.0, metadata['runtime_limit_ms']/1000*3.0+5)
    start=time.perf_counter()
    try:
        q=subprocess.run(command,capture_output=True,text=True,errors='replace',env=env,timeout=supervisor)
        data['wall_ms']=round((time.perf_counter()-start)*1000,4)
        data['return_code']=q.returncode
        log.write_text('COMMAND: '+' '.join(command)+'\n'+q.stdout+'\n'+q.stderr)
        data['wall_hit_count']=len(re.findall(r'\bwall_hit=(?:1|true)\b',q.stderr))
        data['work_hit_count']=len(re.findall(r'\bwork_hit=(?:1|true)\b',q.stderr))
        if peak.exists():
            m=re.search(r'PEAK_RSS_KIB=(\d+)',peak.read_text())
            if m:data['peak_rss_kib']=int(m.group(1))
        data['runtime_budget_ratio']=round(data['wall_ms']/metadata['runtime_limit_ms'],6)
        if q.returncode:raise RuntimeError('synth_exit_'+str(q.returncode))
        if not net.exists():raise RuntimeError('missing_netlist')
        data['net_sha256']=sha(net)
        z=subprocess.run([str(valid),str(input_path),str(net)],capture_output=True,text=True,
                         errors='replace',timeout=max(20,supervisor))
        (out/'logs'/f'{stem}.verify.log').write_text(z.stdout+'\n'+z.stderr)
        if z.returncode:raise RuntimeError('exhaustive_verify_exit_'+str(z.returncode))
        m=re.search(r'PASS\s+exact_assignments=(\d+)\s+area=(\d+)\s+delay=(\d+)\s+target=(\d+)',z.stdout)
        if not m:raise RuntimeError('invalid_verifier_output')
        assert int(m.group(1))==1<<metadata['n']
        data['exact']=True;data['area']=int(m.group(2));data['delay']=int(m.group(3))
        data['target_met']=data['delay']<=metadata['target']
    except Exception as e:
        data['error']=repr(e)
        if data['wall_ms'] is None:data['wall_ms']=round((time.perf_counter()-start)*1000,4)
        if not log.exists():log.write_text(data['error']+'\n')
    return data

def summarize(rows,all_cases):
    out={'records':len(rows),'case_count':len(all_cases),'variants':{},'pairwise':{},
         'warnings':[],'official_hidden_cases_used':False}
    for label,_,_,_ in VARIANTS:
        group=[r for r in rows if r['variant']==label]
        pass_rows=[r for r in group if r['exact']]
        times=[r['wall_ms'] for r in pass_rows];rss=[r['peak_rss_kib'] for r in group if r['peak_rss_kib'] is not None]
        out['variants'][label]={
         'runs':len(group),'exact_pass':len(pass_rows),'target_met':sum(r['target_met'] is True for r in pass_rows),
         'runtime_within_limit':sum(r['wall_ms']<=r['runtime_limit_ms'] for r in pass_rows),
         'runtime_near_limit_90pct':sum(r['runtime_budget_ratio']>=.9 for r in pass_rows),
         'wall_hit_events':sum(r['wall_hit_count'] for r in group),
         'median_wall_ms':statistics.median(times) if times else None,
         'p95_wall_ms':sorted(times)[math.ceil(.95*len(times))-1] if times else None,
         'max_rss_kib':max(rss) if rss else None,
         'total_area':sum(r['area'] for r in pass_rows),
         'total_delay':sum(r['delay'] for r in pass_rows),
         'failures':[r['case'] for r in group if not r['exact'] or r['target_met'] is False]}
    by={(r['case'],r['run'],r['variant']):r for r in rows}
    for v in ('r86_extra_sop','r85_reclaim'):
        eq=ae=de=improve=degrade=0;deltas=[];runtime=[]
        for idx in all_cases:
            for run in sorted({r['run'] for r in rows}):
                a=by.get((idx,run,'r86_baseline'));b=by.get((idx,run,v))
                if not a or not b or not a['exact'] or not b['exact']:continue
                eq+=1; da=b['area']-a['area'];dd=b['delay']-a['delay']
                ae+=da==0;de+=dd==0;improve+=da<0;degrade+=da>0;deltas.append(da)
                if a['wall_ms'] and b['wall_ms'] and a['wall_ms']>0:
                    runtime.append(b['wall_ms']/a['wall_ms'])
        out['pairwise'][v+'_vs_baseline']={
           'paired_exact':eq,'area_equal':ae,'delay_equal':de,
           'area_improved':improve,'area_degraded':degrade,'delta_total_area':sum(deltas),
           'geomean_wall_ratio':math.exp(statistics.mean(map(math.log,runtime))) if runtime else None}
    # Cross-run consistency measured by area/delay AND by netlist digest.
    for v,_,_,_ in VARIANTS:
        pairs=[];has_two=any(r['run']==2 for r in rows)
        if has_two:
            for idx in all_cases:
                a=by.get((idx,1,v));b=by.get((idx,2,v))
                if a and b and a['exact'] and b['exact']:pairs.append((a,b))
        out['variants'][v]['repeat_compared']=len(pairs)
        out['variants'][v]['repeat_area_delay_equal']=sum(x['area']==y['area'] and x['delay']==y['delay'] for x,y in pairs)
        out['variants'][v]['repeat_net_sha_equal']=sum(x['net_sha256']==y['net_sha256'] for x,y in pairs)
    return out

def main():
    p=argparse.ArgumentParser();p.add_argument('--results',type=Path,required=True);p.add_argument('--quick',action='store_true')
    p.add_argument('--runs',type=int,default=2);a=p.parse_args()
    if a.runs not in (1,2,3):raise ValueError('runs must be 1,2,3')
    out=a.results/'holdout';(out/'logs').mkdir(parents=True,exist_ok=True);(out/'nets').mkdir(exist_ok=True)
    source=json.loads((H/'holdouts/FROZEN_MANIFEST.json').read_text())
    cases=[(int(q['file'][8:11]),q) for q in source['cases'] if not a.quick or int(q['file'][8:11]) in QUICK_IDS]
    meta={'manifest_sha256':sha(H/'holdouts/FROZEN_MANIFEST.json'),
      'source_sha256':{'r86':sha(H/'src/synth_round86.cpp'),'r85':sha(H/'src/synth_round85_frozen.cpp')},
      'executables_sha256':{x:sha(H/'build'/x) for x in ('synth_round86','synth_round85_frozen','verify_exhaustive')},
      'cases':len(cases),'runs':a.runs,'candidate_count':len(VARIANTS),'no_hidden_claim':True}
    (out/'PROVENANCE.json').write_text(json.dumps(meta,indent=2)+'\n')
    rows=[];variants=VARIANTS
    for run in range(1,a.runs+1):
        for idx,q in cases:
            for v in (variants if run%2 else list(reversed(variants))):
                result=evaluate(idx,v,run,out,q);rows.append(result)
                with (out/'casewise.csv').open('w',newline='') as f:
                    writer=csv.DictWriter(f,fieldnames=FIELDS);writer.writeheader();writer.writerows(rows)
                state=summarize(rows,[f'{i:03d}' for i,_ in cases]);(out/'summary.json').write_text(json.dumps(state,indent=2)+'\n')
                tag='PASS' if result['exact'] and result['target_met'] else 'WARN' if result['exact'] else 'FAIL'
                print('HOLDOUT',run,result['case'],q['family'],v[0],tag,
                      'area=',result['area'],'delay=',result['delay'],
                      'wall_ms=',result['wall_ms'],'rss_kib=',result['peak_rss_kib'],
                      ('error='+result['error'] if result['error'] else ''),flush=True)
    state=summarize(rows,[f'{i:03d}' for i,_ in cases]);(out/'summary.json').write_text(json.dumps(state,indent=2)+'\n')
    # Gate: all full truth checks required; partial performance warnings are explicit.
    problems=[r for r in rows if not r['exact']]
    if problems:
        print('R87_HOLDOUT_CORRECTNESS_GATE FAIL',len(problems),'failures',flush=True);return 4
    print('R87_HOLDOUT_CORRECTNESS_GATE PASS',len(rows),'full exhaustive checks;',
          'target & runtime are reported separately',flush=True)
    if any(r['target_met'] is False for r in rows):
        print('R87_WARNING target delay unmet on locally generated case(s)',flush=True)
    if any(r['wall_ms']>r['runtime_limit_ms'] for r in rows):
        print('R87_WARNING local process wall time exceeds case limit on some runs; NOT an official FAIL',flush=True)
    return 0
if __name__=='__main__':raise SystemExit(main())

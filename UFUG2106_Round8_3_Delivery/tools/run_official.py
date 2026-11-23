#!/usr/bin/env python3
"""Two-run, two-stage paired official evaluation. Never fabricates evaluator PASS."""
import argparse,csv,hashlib,json,os,platform,statistics,math,subprocess,tempfile,shutil
from pathlib import Path
H=Path(__file__).resolve().parents[1];ROOT=H.parent

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def parse_report(p):
    with p.open(newline='') as f:rows=list(csv.DictReader(f))
    if len(rows)!=25:raise RuntimeError(f'{p}: expected 25 records, found {len(rows)}')
    v={row['case']:row for row in rows}
    if len(v)!=25:raise RuntimeError(f'{p}: duplicate case names')
    return v

def aggregate(rows):
    items=list(rows.values());valid=[x for x in items if x['status']=='PASS']
    return {'pass':len(valid),'target_met':sum(x.get('target_met')=='yes' for x in items),
            'area_passed':sum(int(x['area']) for x in valid),
            'delay_sum_passed':sum(int(x['delay']) for x in valid),
            'median_runtime_ms':statistics.median(float(x['runtime_ms']) for x in valid) if valid else None}

def variants(b0,b1):
    return [
      ('r821_fast_area',b0,{'UFUG_R83_POLICY':'off','UFUG_R82_POLICY':'fast_area'}),
      ('r821_dual_area',b0,{'UFUG_R83_POLICY':'off','UFUG_R82_POLICY':'dual_area'}),
      ('r83_fast_area',b1,{'UFUG_R83_POLICY':'stable_fast_area','UFUG_R82_POLICY':'off'}),
      ('r83_stable_dual',b1,{'UFUG_R83_POLICY':'stable_dual_area','UFUG_R82_POLICY':'off'}),
      ('r83_stable_adp',b1,{'UFUG_R83_POLICY':'stable_dual_adp','UFUG_R82_POLICY':'off'}),
      ('r83_dense_dual',b1,{'UFUG_R83_POLICY':'stable_dual_area','UFUG_R82_POLICY':'off','UFUG_R83_ROOT_CAP':'1100'})]

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--results',type=Path,required=True)
    ap.add_argument('--runs',type=int,default=2);ap.add_argument('--quick',action='store_true')
    a=ap.parse_args();assert a.runs>=1
    out=a.results/'official';out.mkdir(exist_ok=True,parents=True)
    b0=ROOT/'UFUG2106_Round8_2_1_Delivery/build/synth_round821'
    b1=H/'build/synth_round83';ev=ROOT/'evaluator'
    for p in (b0,b1,ev):
        if not p.is_file():raise RuntimeError('missing genuine comparator/evaluator '+str(p))
    vv=variants(b0,b1)
    if a.quick:vv=[x for x in vv if x[0] in ('r821_dual_area','r83_stable_dual','r83_dense_dual')]
    results={'milestone':'Round8.3','official_results':True,'runs':a.runs,'quick':a.quick,
      'fingerprints':{p.name:sha(p) for p in (b0,b1,ev)},'platform':platform.platform(),
      'records':[],'paired':[], 'known_ram_evaluator_discrepancy_not_retested':True}
    (out/'summary.json').write_text(json.dumps(results,indent=2)+'\n')
    with tempfile.TemporaryDirectory(prefix='r83_official_') as t:
        e=Path(t)/'evaluator';shutil.copy2(ev,e);e.chmod(e.stat().st_mode|0o111)
        for run in range(1,a.runs+1):
            for stage in ('stage1','stage2'):
                data=ROOT/'data'/stage
                if not data.is_dir():raise RuntimeError('missing dataset '+str(data))
                current={}
                order=vv if run%2 else list(reversed(vv))
                for name,prog,settings in order:
                    report=out/f'{stage}_run{run}_{name}.csv';log=out/f'{stage}_run{run}_{name}.log'
                    env=os.environ.copy()
                    for k in list(env):
                        if k.startswith('UFUG_R') or k.startswith('UFUG_ROUND'):env.pop(k)
                    env.update(settings);env.update(UFUG_R8_POLICY='off',UFUG_R81_POLICY='off',UFUG_R71_POLICY='guard')
                    process=subprocess.run([str(e),str(prog),str(data.resolve()),'--report',str(report)],
                        text=True,capture_output=True,errors='replace',env=env)
                    log.write_text(process.stdout+'\n'+process.stderr)
                    if not report.exists():raise RuntimeError(f'no official CSV {name}: exit={process.returncode}; inspect {log}')
                    cases=parse_report(report);current[name]=cases
                    agg=aggregate(cases)
                    results['records'].append(dict(run=run,stage=stage,variant=name,
                              evaluator_exit=process.returncode,**agg))
                    (out/'summary.json').write_text(json.dumps(results,indent=2)+'\n')
                    print(f'{stage} run{run} {name:19s} {agg["pass"]}/25 target={agg["target_met"]} area={agg["area_passed"]}',flush=True)
                    if process.returncode!=0 or agg['pass']!=25 or agg['target_met']!=25:
                        raise RuntimeError(f'official gate FAIL {stage} run{run} {name}')
                ref=current['r821_dual_area']
                for name in current:
                    alt=current[name]
                    casewise=[]
                    for case in sorted(ref):
                        x,y=ref[case],alt[case]
                        casewise.append(dict(case=case,area_delta=int(y['area'])-int(x['area']),
                           delay_delta=int(y['delay'])-int(x['delay']),
                           runtime_ratio=float(y['runtime_ms'])/float(x['runtime_ms']) if float(x['runtime_ms'])>0 else None))
                    result=dict(run=run,stage=stage,variant=name,vs='r821_dual_area',
                       area_delta=sum(v['area_delta'] for v in casewise),
                       identical_area=sum(v['area_delta']==0 for v in casewise),
                       identical_delay=sum(v['delay_delta']==0 for v in casewise),
                       runtime_ratio_geomean=math.exp(statistics.mean(math.log(v['runtime_ratio']) for v in casewise if v['runtime_ratio'])),
                       casewise=casewise)
                    results['paired'].append(result)
                    (out/'summary.json').write_text(json.dumps(results,indent=2)+'\n')
    print('RELEASE_GATE: PASS (official public Stage1/2 only; RAM issue remains open)',flush=True)
if __name__=='__main__':
    try:main()
    except Exception as e:print('R83_OFFICIAL_FAIL:',repr(e),flush=True);raise

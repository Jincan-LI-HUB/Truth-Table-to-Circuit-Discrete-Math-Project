#!/usr/bin/env python3
"""Paired official evaluator: unchanged R8.2 vs R8.2.1 under identical policies."""
import argparse,csv,datetime,hashlib,json,os,platform,statistics,math,subprocess,tempfile,shutil
from pathlib import Path
H=Path(__file__).resolve().parents[1];ROOT=H.parent

def checksum(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def parse(p):
    with p.open() as f:rows=list(csv.DictReader(f))
    if len(rows)!=25:raise RuntimeError(f'{p.name}: expected 25 rows, got {len(rows)}')
    return {x['case']:x for x in rows}
def aggregate(rows):
    r=list(rows.values());t=[float(z['runtime_ms']) for z in r if z.get('runtime_ms')]
    return {'pass':sum(z['status']=='PASS' for z in r),
        'target':sum(z.get('target_met')=='yes' for z in r),
        'area':sum(int(z['area']) for z in r if z['status']=='PASS'),
        'median_ms':statistics.median(t) if t else None}
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--results',type=Path,required=True)
    ap.add_argument('--runs',type=int,default=2);ap.add_argument('--quick',action='store_true')
    args=ap.parse_args();out=args.results/'official';out.mkdir(exist_ok=True,parents=True)
    r82=ROOT/'UFUG2106_Round8_2_Delivery/build/synth_round82'
    r821=H/'build/synth_round821';ev=ROOT/'evaluator'
    for f in (r82,r821,ev):
        if not f.is_file():raise RuntimeError('Missing official comparator or evaluator: '+str(f))
    variants=[
     ('r82_fast_adp',r82,{'UFUG_R82_POLICY':'fast_adp'}),
     ('r821_fast_adp',r821,{'UFUG_R82_POLICY':'fast_adp'}),
     ('r82_fast_area',r82,{'UFUG_R82_POLICY':'fast_area'}),
     ('r821_fast_area',r821,{'UFUG_R82_POLICY':'fast_area'}),
     ('r82_dual_area',r82,{'UFUG_R82_POLICY':'dual_area'}),
     ('r821_dual_area',r821,{'UFUG_R82_POLICY':'dual_area'}),
    ]
    if args.quick:variants=[x for x in variants if x[0] in {'r82_fast_adp','r821_fast_adp','r821_dual_area'}]
    summary={'milestone':'Round8.2.1','runs':args.runs,'quick':args.quick,
       'fingerprints':{'r82':checksum(r82),'r821':checksum(r821),'evaluator':checksum(ev)},
       'platform':platform.platform(),'records':[],'comparisons':[]}
    (out/'summary.json').write_text(json.dumps(summary,indent=2))
    with tempfile.TemporaryDirectory(prefix='r821_official_') as tmp:
        f=Path(tmp)/'evaluator';shutil.copy2(ev,f);f.chmod(f.stat().st_mode|0o111)
        for i in range(1,args.runs+1):
            for stage in ('stage1','stage2'):
                datadir=ROOT/'data'/stage
                if not datadir.exists():raise RuntimeError('Missing '+str(datadir))
                sequence=variants if i%2 else list(reversed(variants))
                obs={}
                for name,program,env_vars in sequence:
                    report=out/f'{stage}_run{i}_{name}.csv'
                    env=os.environ.copy()
                    for key in ('UFUG_R8_POLICY','UFUG_R81_POLICY','UFUG_R82_POLICY','UFUG_R82_PROFILE','UFUG_R82_SAMPLING','UFUG_R82_ROOT_CAP','UFUG_R71_POLICY','UFUG_R72_POLICY','UFUG_ROUND5_PROFILE'):
                        env.pop(key,None)
                    env.update(env_vars);env['UFUG_R8_POLICY']='off'
                    z=subprocess.run([str(f),str(program),str(datadir.resolve()),'--report',str(report)],
                        stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True,errors='replace',env=env)
                    (out/f'{stage}_run{i}_{name}.log').write_text(z.stdout)
                    if not report.exists():raise RuntimeError(f'Evaluator did not create {report}: exit={z.returncode}')
                    rows=parse(report);obs[name]=rows;metric=aggregate(rows)
                    summary['records'].append({'run':i,'stage':stage,'variant':name,'exit':z.returncode,**metric})
                    (out/'summary.json').write_text(json.dumps(summary,indent=2)+'\n')
                    print(f'{stage} run{i} {name:18s} {metric["pass"]}/25 target={metric["target"]} area={metric["area"]}',flush=True)
                    if z.returncode!=0 or metric['pass']<25 or metric['target']<25:
                        raise RuntimeError(f'Official gate failed {stage} run{i} {name}')
                for policy in ('fast_adp','fast_area','dual_area'):
                    a,b='r82_'+policy,'r821_'+policy
                    if a not in obs or b not in obs:continue
                    diffs=[]
                    for case in sorted(obs[a]):
                        x,y=obs[a][case],obs[b][case]
                        diffs.append({'case':case,'area_diff':int(y['area'])-int(x['area']),
                          'delay_diff':int(y['delay'])-int(x['delay']),
                          'time_ratio':float(y['runtime_ms'])/float(x['runtime_ms']) if float(x['runtime_ms']) else None})
                    summary['comparisons'].append({'stage':stage,'run':i,'policy':policy,
                      'areas_equal':sum(v['area_diff']==0 for v in diffs),
                      'delays_equal':sum(v['delay_diff']==0 for v in diffs),
                      'delta_area':sum(v['area_diff'] for v in diffs),'casewise':diffs})
                    (out/'summary.json').write_text(json.dumps(summary,indent=2)+'\n')
    return 0
if __name__=='__main__':
    try:raise SystemExit(main())
    except Exception as e:print('OFFICIAL_ERROR:',repr(e),flush=True);raise

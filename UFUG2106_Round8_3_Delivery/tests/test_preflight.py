#!/usr/bin/env python3
"""Local exact verification on real critical cases; no official timing claims."""
import argparse,hashlib,json,os,subprocess,time
from pathlib import Path
H=Path(__file__).resolve().parents[1];ROOT=H.parent
p=argparse.ArgumentParser();p.add_argument('--results',type=Path,required=True);p.add_argument('--quick',action='store_true');a=p.parse_args()
a.results.mkdir(parents=True,exist_ok=True);cases=['016','017'] if a.quick else ['003','005','016','017','021']
rows=[]
for case in cases:
    f=ROOT/'data/stage2'/f'case_{case}.txt'
    if not f.is_file():raise RuntimeError(f'actual course Stage2 file missing: {f}')
    net=a.results/f'case_{case}.net';log=a.results/f'case_{case}.log';env=os.environ.copy()
    for k in list(env):
        if k.startswith('UFUG_R') or k.startswith('UFUG_ROUND'):env.pop(k)
    env.update(UFUG_R83_POLICY='stable_dual_area',UFUG_R83_PROFILE='1')
    t=time.perf_counter();z=subprocess.run([str(H/'build/synth_round83'),str(f),str(net)],text=True,capture_output=True,env=env)
    elapsed=round((time.perf_counter()-t)*1000,3);log.write_text(z.stderr+'\n'+z.stdout)
    if z.returncode!=0:raise RuntimeError(f'preflight synthesis failed {case} exit={z.returncode}')
    y=subprocess.run([str(H/'build/verify_exhaustive'),str(f),str(net)],capture_output=True,text=True)
    if y.returncode!=0:raise RuntimeError(f'equivalence FAIL {case}: {y.stderr}')
    stages=[dict(x.split('=',1) for x in line.split() if '=' in x) for line in z.stderr.splitlines() if line.startswith('R83_STAGE')]
    item={'case':case,'sha256':hashlib.sha256(net.read_bytes()).hexdigest(),
          'elapsed_ms_local':elapsed,'verification':y.stdout.strip(),'stages':stages}
    rows.append(item);(a.results/'preflight.json').write_text(json.dumps(rows,indent=2)+'\n')
    print('PASS Stage2 case_'+case,y.stdout.strip(),'wall_hit='+str(any(x.get('wall_hit')=='1' for x in stages)),flush=True)
print('LOCAL_EXHAUSTIVE_PREFLIGHT: PASS',flush=True)

#!/usr/bin/env python3
"""Actual course cases, independently exhaustively verified; never an official performance claim."""
import argparse,hashlib,json,os,subprocess,time
from pathlib import Path
H=Path(__file__).resolve().parents[1];ROOT=H.parent
p=argparse.ArgumentParser();p.add_argument('--results',type=Path,required=True);p.add_argument('--quick',action='store_true');a=p.parse_args()
a.results.mkdir(parents=True,exist_ok=True)
cases=['016','017'] if a.quick else ['003','005','016','017','021']
policies=['topq_dual'] if a.quick else ['topology_dual','topq_dual','topq_dense','adaptive_dual','mixed33_dual']
rows=[]
for case in cases:
  f=ROOT/'data/stage2'/f'case_{case}.txt'
  if not f.is_file():raise RuntimeError('Real Stage2 file missing '+str(f))
  for policy in policies:
    net=a.results/f'case_{case}_{policy}.net';log=a.results/f'case_{case}_{policy}.log'
    env=os.environ.copy()
    for k in list(env):
      if k.startswith('UFUG_R') or k.startswith('UFUG_ROUND'):env.pop(k)
    env.update(UFUG_R84_POLICY=policy,UFUG_R84_PROFILE='1')
    start=time.perf_counter()
    z=subprocess.run([str(H/'build/synth_round84'),str(f),str(net)],capture_output=True,text=True,env=env,timeout=120)
    elapsed=(time.perf_counter()-start)*1000
    log.write_text(z.stderr+'\n'+z.stdout)
    if z.returncode:raise RuntimeError(f'synth failed {case} {policy}: {z.stderr[-400:]}')
    v=subprocess.run([str(H/'build/verify_exhaustive'),str(f),str(net)],capture_output=True,text=True,timeout=120)
    if v.returncode:raise RuntimeError(f'exact truth mismatch {case} {policy}: {v.stderr[-400:]}')
    stages=[x for x in z.stderr.splitlines() if x.startswith('R84_STAGE')]
    item={'case':case,'policy':policy,'net_sha256':hashlib.sha256(net.read_bytes()).hexdigest(),
          'elapsed_ms_local':round(elapsed,3),'verified':v.stdout.strip(),'stage_logs':stages}
    rows.append(item)
    (a.results/'preflight.json').write_text(json.dumps(rows,indent=2)+'\n')
    print('PASS',case,policy,v.stdout.strip(), 'wall_hit='+str(any('wall_hit=1' in x for x in stages)),flush=True)
print('R84_LOCAL_EXHAUSTIVE_PASS',len(rows),'checks')

#!/usr/bin/env python3
"""Exact verifier on public course cases if present, else frozen structured fixtures."""
import argparse,hashlib,json,os,subprocess,time
from pathlib import Path
H=Path(__file__).resolve().parents[1];ROOT=H.parent
arg=argparse.ArgumentParser();arg.add_argument('--results',type=Path,required=True);arg.add_argument('--quick',action='store_true');a=arg.parse_args()
a.results.mkdir(parents=True,exist_ok=True)
stage=ROOT/'data/stage2'
if stage.is_dir():
 cases=[stage/f'case_{x}.txt' for x in (['016','021'] if a.quick else ['003','005','016','017','021'])]
 source='actual_Stage2'
else:
 cases=sorted((H/'evidence/holdout_structured_v2').glob('structured_*.txt'))
 if a.quick:cases=cases[:2]
 source='reused_structured_holdout'
policies=['dual_sop_first'] if a.quick else ['dual_shannon_first','dual_sop_first','dense_sop_first','budget_reclaim']
records=[]
for f in cases:
 for policy in policies:
  env=os.environ.copy()
  for k in list(env):
   if k.startswith('UFUG_R') or k.startswith('UFUG_ROUND'):env.pop(k)
  env.update(UFUG_R85_POLICY=policy,UFUG_R85_PROFILE='1')
  net=a.results/f'{f.stem}_{policy}.net';log=a.results/f'{f.stem}_{policy}.log'
  t=time.perf_counter()
  z=subprocess.run([str(H/'build/synth_round85'),str(f),str(net)],env=env,capture_output=True,text=True,timeout=120)
  elapsed=(time.perf_counter()-t)*1000
  log.write_text(z.stderr+'\n'+z.stdout)
  if z.returncode:raise RuntimeError(f'{f.name} {policy} synth exit={z.returncode}: {z.stderr[-300:]}')
  v=subprocess.run([str(H/'build/verify_exhaustive'),str(f),str(net)],capture_output=True,text=True,timeout=120)
  if v.returncode:raise RuntimeError(f'{f.name} {policy} exhaustive mismatch: {v.stderr[-300:]}')
  stages=[x for x in z.stderr.splitlines() if x.startswith('R85_STAGE')]
  records.append(dict(case=f.name,policy=policy,data_origin=source,elapsed_ms=round(elapsed,3),verify=v.stdout.strip(),net_sha256=hashlib.sha256(net.read_bytes()).hexdigest(),stages=stages))
  (a.results/'results.json').write_text(json.dumps(records,indent=2)+'\n')
  print('LOCAL_EXACT_PASS',f.name,policy,v.stdout.strip(),flush=True)
# Additional frozen synthetic cases: correctness-only, not claims about hidden grading.
fresh=sorted((H/'evidence/fresh_synthetic_v1').glob('synthetic_*.txt'))
if a.quick:fresh=fresh[:2]
for f in fresh:
 env=os.environ.copy()
 for k in list(env):
  if k.startswith('UFUG_R') or k.startswith('UFUG_ROUND'):env.pop(k)
 env['UFUG_R85_POLICY']='dual_sop_first'
 output=a.results/f'{f.stem}_fresh.net'
 z=subprocess.run([str(H/'build/synth_round85'),str(f),str(output)],env=env,text=True,capture_output=True,timeout=120)
 if z.returncode:raise RuntimeError(f'fresh synthetic {f.name} failed: {z.stderr[-300:]}')
 v=subprocess.run([str(H/'build/verify_exhaustive'),str(f),str(output)],capture_output=True,text=True,timeout=120)
 if v.returncode:raise RuntimeError(f'fresh synthetic {f.name} mismatch: {v.stderr[-300:]}')
 records.append(dict(case=f.name,policy='dual_sop_first',data_origin='fresh_synthetic_v1',verify=v.stdout.strip(),net_sha256=hashlib.sha256(output.read_bytes()).hexdigest()))
 (a.results/'results.json').write_text(json.dumps(records,indent=2)+'\n')
 print('FRESH_SYNTHETIC_PASS',f.name,v.stdout.strip(),flush=True)
print('R85_LOCAL_EXHAUSTIVE_PASS',len(records),'checks; includes',len(fresh),'fresh synthetic cases')

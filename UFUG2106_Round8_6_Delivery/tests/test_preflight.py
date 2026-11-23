#!/usr/bin/env python3
"""Exhaustive correctness on real Stage 2 and new independent synthetic fixtures."""
import argparse,hashlib,json,os,subprocess
from pathlib import Path
H=Path(__file__).resolve().parents[1];ROOT=H.parent
ap=argparse.ArgumentParser();ap.add_argument('--results',type=Path,required=True);ap.add_argument('--quick',action='store_true');a=ap.parse_args()
a.results.mkdir(parents=True,exist_ok=True)
bank=ROOT/'data/stage2'
if bank.is_dir():
 cases=[bank/f'case_{x}.txt' for x in (['016','021'] if a.quick else ['003','005','016','017','021'])]
 origin='actual_Stage2'
else:
 cases=sorted((H/'evidence/holdout_structured_v2').glob('structured_*.txt'))[:2 if a.quick else 5]
 origin='reused_structured_holdout'
policies=['baseline','combined'] if a.quick else ['baseline','extra_sop','time_reclaim','combined','reverse_allocation']
records=[]
def test(f,policy):
 env=os.environ.copy()
 for k in list(env):
  if k.startswith('UFUG_R') or k.startswith('UFUG_ROUND'):env.pop(k)
 env.update(UFUG_R86_POLICY=policy,UFUG_R86_PROFILE='1')
 net=a.results/f'{f.stem}_{policy}.net'
 z=subprocess.run([str(H/'build/synth_round86'),str(f),str(net)],env=env,capture_output=True,text=True,timeout=120)
 (a.results/f'{f.stem}_{policy}.log').write_text(z.stderr+'\n'+z.stdout)
 if z.returncode:raise RuntimeError(f'{f} {policy} synthesis exit={z.returncode}: {z.stderr[-500:]}')
 v=subprocess.run([str(H/'build/verify_exhaustive'),str(f),str(net)],capture_output=True,text=True,timeout=180)
 if v.returncode:raise RuntimeError(f'{f} {policy} exhaustive mismatch: {v.stderr[-500:]}')
 print('R86_EXACT_PASS',f.name,policy,v.stdout.strip(),flush=True)
 records.append(dict(file=f.name,policy=policy,origin=origin,verify=v.stdout.strip(),net_sha256=hashlib.sha256(net.read_bytes()).hexdigest()))
 (a.results/'results.json').write_text(json.dumps(records,indent=2)+'\n')
for f in cases:
 for p in policies:test(f,p)
synthetics=sorted((H/'evidence/fresh_synthetic_v1').glob('synthetic_*.txt'))[:2 if a.quick else 18]
for f in synthetics:
 test(f,'baseline')
 records[-1]['origin']='fresh_synthetic_v1'
print('R86_LOCAL_EXHAUSTIVE_PASS',len(records),'checks, including',len(synthetics),'synthetic fixtures')

#!/usr/bin/env python3
"""Offline genuine cases: use independent exhaustive netlist verifier; no course score claims."""
import argparse,csv,hashlib,os,re,subprocess,time,json
from pathlib import Path
H=Path(__file__).resolve().parents[1]
ap=argparse.ArgumentParser();ap.add_argument('--bank',type=Path,required=True);ap.add_argument('--results',type=Path,required=True)
ap.add_argument('--cases',type=int,default=25);ap.add_argument('--resume',action='store_true');ap.add_argument('--policies',default='baseline,extra_sop,time_reclaim,combined,reverse_allocation,r85_reclaim')
a=ap.parse_args();a.results.mkdir(parents=True,exist_ok=True)
cases=sorted(a.bank.glob('case_*.txt'))[:a.cases]
policies=a.policies.split(',')
rows=[];csv_path=a.results/'local_ablation.csv'
if a.resume and csv_path.exists():
 with csv_path.open() as f: rows=list(csv.DictReader(f))
seen={(r['case'],r['policy']) for r in rows}
for c in cases:
 for policy in policies:
  if (c.stem,policy) in seen: continue
  prog=H/'build/synth_round85_frozen' if policy=='r85_reclaim' else H/'build/synth_round86'
  env=os.environ.copy()
  for k in list(env):
   if k.startswith('UFUG_R') or k.startswith('UFUG_ROUND'):env.pop(k)
  env.update(UFUG_R71_POLICY='guard',UFUG_R8_POLICY='off',UFUG_R81_POLICY='off',UFUG_R82_POLICY='off',UFUG_R83_POLICY='off',UFUG_R84_POLICY='off')
  if policy=='r85_reclaim':env['UFUG_R85_POLICY']='budget_reclaim';env['UFUG_R85_PROFILE']='1'
  else:env['UFUG_R86_POLICY']=policy;env['UFUG_R86_PROFILE']='1';env['UFUG_R85_POLICY']='off'
  net=a.results/f'{c.stem}_{policy}.net'
  t=time.perf_counter();z=subprocess.run([str(prog),str(c),str(net)],env=env,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True,timeout=80)
  elapsed=(time.perf_counter()-t)*1000
  (a.results/f'{c.stem}_{policy}.log').write_text(z.stderr+'\n'+z.stdout)
  if z.returncode:raise RuntimeError(f'{c.name} {policy} exit {z.returncode}: {z.stderr[-500:]}')
  verify=subprocess.run([str(H/'build/verify_exhaustive'),str(c),str(net)],text=True,capture_output=True,timeout=180)
  if verify.returncode:raise RuntimeError(f'{c.name} {policy} verification FAILED: {verify.stdout} {verify.stderr}')
  ma=re.search(r'area=(\d+)\s+delay=(\d+)',verify.stdout)
  if not ma:raise RuntimeError('unexpected verifier format: '+verify.stdout)
  stages=[x for x in z.stderr.splitlines() if x.startswith('R86_STAGE') or x.startswith('R85_STAGE')]
  row={'case':c.stem,'policy':policy,'area':int(ma[1]),'delay':int(ma[2]),'elapsed_ms':round(elapsed,3),
       'net_sha256':hashlib.sha256(net.read_bytes()).hexdigest(), 'verified':True,
       'wall_hits':sum('wall_hit=1' in x for x in stages), 'trace': ' | '.join(stages)}
  rows.append(row);seen.add((c.stem,policy))
  with csv_path.open('w',newline='') as f:
   w=csv.DictWriter(f,fieldnames=list(row));w.writeheader();w.writerows(rows)
  print(c.stem,policy,'PASS',row['area'],row['delay'],'wall',row['wall_hits'],flush=True)
print('LOCAL_VALIDATED',len(rows),'records')

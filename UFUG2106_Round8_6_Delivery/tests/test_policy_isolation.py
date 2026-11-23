#!/usr/bin/env python3
import os,hashlib,subprocess,tempfile
from pathlib import Path
H=Path(__file__).resolve().parents[1];ROOT=H.parent
f=ROOT/'data/stage2/case_021.txt'
if not f.exists():f=H/'evidence/holdout_structured_v2/structured_008.txt'
with tempfile.TemporaryDirectory(prefix='r86_iso_') as d:
 hashes=[]
 for index in range(2):
  output=Path(d)/f'{index}.net';env=os.environ.copy()
  for k in list(env):
   if k.startswith('UFUG_R') or k.startswith('UFUG_ROUND'):env.pop(k)
  env.update(UFUG_R86_POLICY='baseline',UFUG_R86_PROFILE='1')
  if index:env.update(UFUG_R8_POLICY='iterate',UFUG_R81_POLICY='branch',UFUG_R82_POLICY='dual_area',UFUG_R83_POLICY='stable_dual_area',UFUG_R84_POLICY='topq_dense',UFUG_R85_POLICY='budget_reclaim')
  z=subprocess.run([str(H/'build/synth_round86'),str(f),str(output)],env=env,text=True,capture_output=True,timeout=120)
  if z.returncode:raise RuntimeError(f'policy isolation exited {z.returncode}: {z.stderr[-500:]}')
  if any(x in z.stderr for x in ('R85_STAGE','R84_STAGE','R83_STAGE','R82_STAGE')):
   raise RuntimeError('unexpected earlier postprocessor ran')
  hashes.append(hashlib.sha256(output.read_bytes()).hexdigest())
 if hashes[0]!=hashes[1]:raise RuntimeError('conflicting flags altered R86 netlist')
print('PASS R86 policy isolation, R8–R85 flags cannot contaminate R86')

#!/usr/bin/env python3
"""Check that earlier R8 policy flags cannot silently enable older postprocessors."""
import os,hashlib,subprocess,tempfile,sys
from pathlib import Path
H=Path(__file__).resolve().parents[1];ROOT=H.parent
f=ROOT/'data/stage2/case_021.txt'
if not f.exists():f=H/'evidence/holdout_structured_v2/structured_008.txt'
with tempfile.TemporaryDirectory(prefix='r85_iso_') as d:
 hashes=[]
 for index in range(2):
  output=Path(d)/f'{index}.net';env=os.environ.copy()
  for k in list(env):
   if k.startswith('UFUG_R') or k.startswith('UFUG_ROUND'):env.pop(k)
  env.update(UFUG_R85_POLICY='dual_sop_first',UFUG_R85_PROFILE='1')
  if index:env.update(UFUG_R8_POLICY='iterate',UFUG_R81_POLICY='branch',UFUG_R82_POLICY='dual_area',UFUG_R83_POLICY='stable_dual_area',UFUG_R84_POLICY='topq_dense')
  z=subprocess.run([str(H/'build/synth_round85'),str(f),str(output)],env=env,text=True,capture_output=True,timeout=120)
  if z.returncode:raise RuntimeError(f'policy isolation run {index} exit={z.returncode}: {z.stderr[-300:]}')
  if 'R84_STAGE' in z.stderr or 'R83_STAGE' in z.stderr or 'R82_STAGE' in z.stderr:
   raise RuntimeError('legacy policy contamination in stderr')
  hashes.append(hashlib.sha256(output.read_bytes()).hexdigest())
  if 'R85_STAGE' not in z.stderr and 'R85_FINAL' not in z.stderr:
   print('NOTE: no R85 Stage invoked for this small fixture')
 if hashes[0]!=hashes[1]:raise RuntimeError('conflicting flags changed netlist')
print('PASS R85 policy isolation; earlier flags cannot contaminate R85')

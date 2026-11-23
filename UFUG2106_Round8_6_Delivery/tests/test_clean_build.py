#!/usr/bin/env python3
"""Cold compile in directory without any Round delivery or external snapshots."""
from pathlib import Path
import argparse,hashlib,shutil,subprocess,tempfile,json,os
H=Path(__file__).resolve().parents[1]
ap=argparse.ArgumentParser();ap.add_argument('--results',type=Path,required=True);a=ap.parse_args();a.results.mkdir(parents=True,exist_ok=True)
with tempfile.TemporaryDirectory(prefix='r86_cold_') as tmp:
 d=Path(tmp);shutil.copytree(H/'src',d/'src');shutil.copytree(H/'tests',d/'tests')
 for name,src,out in [('synth_round86','src/synth_round86.cpp','synth'),('verify_exhaustive','tests/verify_exhaustive.cpp','verify')]:
  z=subprocess.run(['g++','-O2','-std=c++17','-pipe','-DNDEBUG',str(d/src),'-o',str(d/out)],text=True,capture_output=True,timeout=120)
  if z.returncode:raise RuntimeError(f'cold {name} compile FAILED {z.stderr[-1200:]}')
 f=H/'evidence/holdout_structured_v2/structured_008.txt'
 net=d/'result.net'
 env=os.environ.copy()
 for k in list(env):
  if k.startswith('UFUG_R') or k.startswith('UFUG_ROUND'):env.pop(k)
 env['UFUG_R86_POLICY']='baseline'
 z=subprocess.run([str(d/'synth'),str(f),str(net)],env=env,text=True,capture_output=True,timeout=120)
 if z.returncode:raise RuntimeError('cold solver failed '+z.stderr[-600:])
 v=subprocess.run([str(d/'verify'),str(f),str(net)],text=True,capture_output=True,timeout=120)
 if v.returncode:raise RuntimeError('cold solver truth table failed '+v.stderr[-600:])
 (a.results/'result.json').write_text(json.dumps({'clean_build':'PASS','truth_check':v.stdout.strip(),'source_sha256':hashlib.sha256((H/'src/synth_round86.cpp').read_bytes()).hexdigest(),'binary_sha256':hashlib.sha256((d/'synth').read_bytes()).hexdigest()},indent=2)+'\n')
 print('PASS isolated cold C++17 build and exhaustive netlist verification',flush=True)

#!/usr/bin/env python3
"""Compile in a clean directory without any previous Round delivery folders."""
from pathlib import Path
import argparse,hashlib,shutil,subprocess,tempfile,json,os
H=Path(__file__).resolve().parents[1]
ap=argparse.ArgumentParser();ap.add_argument('--results',type=Path,required=True);args=ap.parse_args();args.results.mkdir(parents=True,exist_ok=True)
with tempfile.TemporaryDirectory(prefix='r85_fresh_checkout_') as d:
 d=Path(d);shutil.copytree(H/'src',d/'src');shutil.copytree(H/'tests',d/'tests');shutil.copytree(H/'integration',d/'integration');shutil.copy2(H/'Makefile',d/'Makefile')
 # Compile exactly the standalone candidate and independent checker, not the
 # optional frozen comparison executable or unrelated integration unit tests.
 compiles=[['g++','-O2','-std=c++17','-pipe','-DNDEBUG',str(d/'src/synth_round85.cpp'),'-o',str(d/'synth_round85')],
           ['g++','-O2','-std=c++17','-pipe','-DNDEBUG',str(d/'tests/verify_exhaustive.cpp'),'-o',str(d/'verify_exhaustive')]]
 m=None
 for command in compiles:
  m=subprocess.run(command,text=True,capture_output=True,timeout=120)
  if m.returncode:break
 if m.returncode:raise RuntimeError('Fresh compile failed '+m.stderr[-1000:])
 case=H/'evidence/holdout_structured_v2/structured_008.txt'
 executable=d/'synth_round85'
 env=os.environ.copy()
 for k in list(env):
  if k.startswith('UFUG_R') or k.startswith('UFUG_ROUND'):env.pop(k)
 env['UFUG_R85_POLICY']='dual_sop_first'
 net=d/'fresh.net';r=subprocess.run([str(executable),str(case),str(net)],env=env,text=True,capture_output=True,timeout=120)
 if r.returncode:raise RuntimeError(f'Fresh binary run failed: {r.stderr[-400:]}')
 v=subprocess.run([str(d/'verify_exhaustive'),str(case),str(net)],capture_output=True,text=True,timeout=120)
 if v.returncode:raise RuntimeError(f'Fresh binary mismatched truth table: {v.stderr[-400:]}')
 result={'clean_build':'PASS','truth_check':v.stdout.strip(),'source_sha256':hashlib.sha256((H/'src/synth_round85.cpp').read_bytes()).hexdigest(),'binary_sha256':hashlib.sha256(executable.read_bytes()).hexdigest(),'net_sha256':hashlib.sha256(net.read_bytes()).hexdigest()}
 (args.results/'result.json').write_text(json.dumps(result,indent=2)+'\n')
 print('PASS clean standalone Round8.5 source build, no historical deliveries, exhaustive equivalence',flush=True)

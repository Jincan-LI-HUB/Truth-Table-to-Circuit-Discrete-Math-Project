#!/usr/bin/env python3
"""Actual source-only build in a directory containing NO parent Round packages."""
import argparse,os,shutil,subprocess,tempfile
from pathlib import Path
H=Path(__file__).resolve().parents[1]
def main():
 a=argparse.ArgumentParser();a.add_argument('--results',type=Path,required=True);args=a.parse_args()
 args.results.mkdir(parents=True,exist_ok=True)
 with tempfile.TemporaryDirectory(prefix='round90_cold_checkout_') as raw:
  tmp=Path(raw)
  shutil.copytree(H/'submission',tmp/'submission')
  (tmp/'tests').mkdir()
  (tmp/'src').mkdir()
  shutil.copy2(H/'tests/verify_exhaustive.cpp',tmp/'tests/verify_exhaustive.cpp')
  shutil.copy2(H/'src/typed_netgraph.hpp',tmp/'src/typed_netgraph.hpp')
  src=tmp/'submission/synth.cpp';exe=tmp/'synth'
  compiler=['g++','-O2','-std=c++17','-pipe','-DNDEBUG']
  z=subprocess.run(compiler+[str(src),'-o',str(exe)],capture_output=True,text=True,timeout=90)
  (args.results/'build.log').write_text(z.stdout+z.stderr)
  if z.returncode:raise RuntimeError('Source-only compile failed')
  z=subprocess.run(compiler+[str(tmp/'tests/verify_exhaustive.cpp'),'-o',str(tmp/'verify')],capture_output=True,text=True,timeout=50)
  if z.returncode:raise RuntimeError('Isolated verifier compile failed: '+z.stderr)
  for kind in ['stress_v2/stress_001.txt','stress_v2/stress_002.txt','holdouts/holdout_016.txt']:
   source=H/'canonical_bank'/kind;net=tmp/'candidate.net'
   e={k:v for k,v in os.environ.items() if not k.startswith(('UFUG_R','UFUG_ROUND','R90_'))}
   r=subprocess.run([str(exe),str(source),str(net)],capture_output=True,text=True,timeout=45,env=e)
   if r.returncode:raise RuntimeError('Cold synth failed for '+kind+' '+r.stderr)
   v=subprocess.run([str(tmp/'verify'),str(source),str(net)],capture_output=True,text=True,timeout=45)
   if v.returncode:raise RuntimeError('Cold exhaust failed for '+kind+' '+v.stdout)
   print('COLD_BUILD',kind,'PASS',v.stdout.strip(),flush=True)
  (args.results/'status.txt').write_text('PASS: isolated source-only cold C++17 build and three exact checks\n')
 print('PASS independent cold source-only compile and exact verification',flush=True)
if __name__=='__main__':main()

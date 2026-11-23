#!/usr/bin/env python3
"""Compile actual R10.0 and trial submission directories independently in empty dirs."""
from pathlib import Path
import tempfile,shutil,subprocess,sys
H=Path(__file__).resolve().parents[1]
def main():
 case=H/'fixtures/holdout_016.txt'
 with tempfile.TemporaryDirectory(prefix='ufug_r101_cold_') as t:
  root=Path(t)
  for name in ('frozen_submission','trial_submission'):
   dest=root/name;shutil.copytree(H/name,dest)
   exe=dest/'synth'
   cmd=['g++','-O2','-std=c++17','-DNDEBUG',str(dest/'synth.cpp'),'-o',str(exe)]
   c=subprocess.run(cmd,capture_output=True,text=True,timeout=120)
   if c.returncode:raise RuntimeError(name+' COLD_COMPILE_FAIL '+c.stderr[-1500:])
   net=dest/'output.net'
   z=subprocess.run([str(exe),str(case),str(net)],capture_output=True,text=True,timeout=30)
   if z.returncode:raise RuntimeError(name+' COLD_SOLVER_FAIL '+z.stderr[-1500:])
   q=subprocess.run([str(H/'build/verify_exhaustive'),str(case),str(net)],capture_output=True,text=True,timeout=30)
   if q.returncode:raise RuntimeError(name+' COLD_EQUIVALENCE_FAIL '+q.stderr)
   print('PASS',name,'COLD_BUILD',q.stdout.strip(),flush=True)
if __name__=='__main__':main()

#!/usr/bin/env python3
"""Source-only cold checkout: no historical rounds or prebuilt binaries."""
from pathlib import Path
import argparse,subprocess,shutil,tempfile,hashlib
H=Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser();p.add_argument('--results',required=True,type=Path);a=p.parse_args()
a.results.mkdir(parents=True,exist_ok=True)
with tempfile.TemporaryDirectory(prefix='r87_cold_source_') as tmp:
 t=Path(tmp)
 for name in ('src','tests'):shutil.copytree(H/name,t/name)
 shutil.copy2(H/'Makefile',t/'Makefile')
 z=subprocess.run(['make','-C',str(t),'-j2'],capture_output=True,text=True,timeout=180)
 (a.results/'make.log').write_text(z.stdout+'\n'+z.stderr)
 if z.returncode:raise RuntimeError('Cold build failed, see '+str(a.results/'make.log'))
 src=H/'holdouts/holdout_016.txt';case=t/'standalone_case.txt';shutil.copy2(src,case)
 net=t/'standalone.net';cmd=[str(t/'build/synth_round86'),str(case),str(net)]
 import os
 env=os.environ.copy()
 for k in list(env):
  if k.startswith(('UFUG_R','UFUG_ROUND')):env.pop(k)
 env['UFUG_R86_POLICY']='extra_sop'
 q=subprocess.run(cmd,capture_output=True,text=True,env=env,timeout=30)
 if q.returncode:raise RuntimeError('Cold synth failed: '+q.stderr[-800:])
 v=subprocess.run([str(t/'build/verify_exhaustive'),str(case),str(net)],capture_output=True,text=True,timeout=30)
 (a.results/'exact.log').write_text(v.stdout+'\n'+v.stderr)
 if v.returncode:raise RuntimeError('Cold independent truth check failed: '+v.stderr)
 print('PASS Round8.7 source-only isolated build and exact truth check',v.stdout.strip(),flush=True)

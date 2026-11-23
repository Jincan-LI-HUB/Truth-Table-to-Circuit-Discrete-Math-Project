#!/usr/bin/env python3
"""End-to-end experiment orchestration smoke test with a FAKE evaluator.
NO fake CSV or output from this test is ever placed in real evidence/results.
"""
from pathlib import Path
import tempfile,shutil,subprocess,sys,os,zipfile,json
P=Path(__file__).resolve().parents[1]
FAKE='''#!/usr/bin/env python3
import csv,sys,os
from pathlib import Path
rep=Path(sys.argv[sys.argv.index('--report')+1]);rep.parent.mkdir(parents=True,exist_ok=True)
with rep.open('w',newline='') as f:
 w=csv.DictWriter(f,fieldnames=['case','status','area','delay','runtime_ms','target_met']);w.writeheader()
 for i in range(1,26):
  fail=os.environ.get('FAKE_FAIL')=='1' and i==16 and 'r82_fast_area' in str(rep)
  w.writerow({'case':f'case_{i:03}.txt','status':'TIME_LIMIT' if fail else 'PASS','area':100 if not fail else '',
              'delay':10 if not fail else '', 'runtime_ms':1 if not fail else '', 'target_met':'no' if fail else 'yes'})
print('synthetic evaluator only')
'''
with tempfile.TemporaryDirectory(prefix='r82_packaging_SMOKE_ONLY_') as temp:
 root=Path(temp);h=root/P.name;h.mkdir();(h/'tools').mkdir();(h/'build').mkdir(parents=True);(h/'results').mkdir();(h/'feedback').mkdir()
 for src in ('run_benchmarks.py','export_feedback.py'):shutil.copy2(P/'tools'/src,h/'tools'/src)
 for n,sub in (('UFUG2106_Round7_2_Delivery','synth_round72'),('UFUG2106_Round8_1_Delivery','synth_round81')):
  folder=root/n/'build';folder.mkdir(parents=True);p=folder/sub;p.write_text('#!/bin/sh\nexit 0\n');p.chmod(0o755)
 q=h/'build/synth_round82';q.write_text('#!/bin/sh\nexit 0\n');q.chmod(0o755)
 for stage in ('stage1','stage2'):(root/'data'/stage).mkdir(parents=True)
 eval=root/'evaluator';eval.write_text(FAKE);eval.chmod(0o755)
 for fail in (False,True):
  env=os.environ.copy();env['FAKE_FAIL']='1' if fail else '0'
  run=subprocess.run([sys.executable,str(h/'tools/run_benchmarks.py'),'--runs','1','--quick'],capture_output=True,text=True,env=env)
  want=2 if fail else 0
  if run.returncode!=want:raise RuntimeError(f'Expected {want}, got {run.returncode}: '+run.stdout[-900:]+run.stderr[-900:])
  package=subprocess.run([sys.executable,str(h/'tools/export_feedback.py'),'--exit-code',str(run.returncode)],capture_output=True,text=True,env=env)
  if package.returncode:raise RuntimeError('Packager failed: '+package.stderr)
  files=sorted((h/'feedback').glob('Round8.2_Feedback_*.zip'))
  if not files:raise RuntimeError('Missing feedback archive')
  with zipfile.ZipFile(files[-1]) as z:
   assert z.testzip() is None
   assert 'official_run/summary.json' in z.namelist()
   assert json.loads(z.read('FEEDBACK_METADATA.json'))['exit_code']==want
  print('PASS isolated smoke', 'failure-path' if fail else 'success-path','feedback ZIP created, rc=',want)
print('All simulated results isolated under deleted temporary directory.')

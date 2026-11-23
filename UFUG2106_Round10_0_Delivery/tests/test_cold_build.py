#!/usr/bin/env python3
"""Build the submission without any Round archive, external header, or env flag."""
from pathlib import Path
import tempfile,shutil,subprocess,os
H=Path(__file__).resolve().parents[1]
with tempfile.TemporaryDirectory(prefix='r100_independent_submission_') as d:
    p=Path(d);shutil.copytree(H/'submission',p/'src');(p/'tests').mkdir()
    shutil.copy2(H/'tests/verify_exhaustive.cpp',p/'tests/verify_exhaustive.cpp')
    for src,dest in [('src/synth.cpp','solver'),('tests/verify_exhaustive.cpp','verify')]:
        subprocess.run(['g++','-O2','-std=c++17','-pipe','-DNDEBUG',str(p/src),'-o',str(p/dest)],check=True,timeout=90)
    for f in [H/'fixtures/dev/hard_003.txt',H/'fixtures/stress_v2/stress_001.txt']:
        net=p/(f.stem+'.net')
        e=os.environ.copy()
        for k in list(e):
            if k.startswith(('UFUG_','R90_','R10_')):del e[k]
        subprocess.run([str(p/'solver'),str(f),str(net)],env=e,capture_output=True,text=True,check=True,timeout=80)
        v=subprocess.run([str(p/'verify'),str(f),str(net)],capture_output=True,text=True,check=True,timeout=80)
        print('COLD_SUBMISSION_EXACT',f.name,v.stdout.strip(),flush=True)
print('PASS cold standalone source-only submission with no custom environment',flush=True)

#!/usr/bin/env python3
"""Cold compile from isolated submission/ tree with no historical Round directories."""
import tempfile,shutil,subprocess
from pathlib import Path
H=Path(__file__).resolve().parents[1]
with tempfile.TemporaryDirectory(prefix='r91_clean_submission_') as tmp:
 p=Path(tmp);shutil.copytree(H/'submission',p/'src');(p/'tests').mkdir()
 shutil.copy2(H/'tests/verify_exhaustive.cpp',p/'tests/verify_exhaustive.cpp')
 for cpp,out in [('src/synth.cpp','synth'),('tests/verify_exhaustive.cpp','verify')]:
  subprocess.run(['g++','-O2','-std=c++17','-pipe','-DNDEBUG',str(p/cpp),'-o',str(p/out)],check=True,timeout=90)
 src=H/'hard_bank/dev/hard_003.txt';net=p/'out.net'
 subprocess.run([str(p/'synth'),str(src),str(net)],check=True,timeout=60)
 v=subprocess.run([str(p/'verify'),str(src),str(net)],capture_output=True,text=True,timeout=60,check=True)
 print('PASS R91 COLD_BUILD:',v.stdout.strip())

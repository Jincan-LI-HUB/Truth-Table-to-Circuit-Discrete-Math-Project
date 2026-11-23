#!/usr/bin/env python3
"""Non-blind adversarial runtime sensitivity checks, separate from frozen holdouts."""
from pathlib import Path
import hashlib,json,sys
H=Path(__file__).resolve().parents[1]
s=H/'stress_v2';s.mkdir(exist_ok=True)
manifest=s/'MANIFEST.json'
if len(sys.argv)>1 and sys.argv[1]=='--verify':
 a=json.loads(manifest.read_text())
 for x in a['cases']:
  p=s/x['file']
  assert p.is_file() and hashlib.sha256(p.read_bytes()).hexdigest()==x['sha256']
 print('PASS adversarial stress bank frozen hashes',len(a['cases']));sys.exit(0)
if manifest.exists():raise RuntimeError('Stress bank already frozen')
a={'purpose':'Stress only. Deliberately tighten runtime of existing independent truth tables; no official hidden-case claim.','cases':[]}
for i,source in enumerate((1,2,34),1):
 p=H/'holdouts'/f'holdout_{source:03d}.txt';dst=s/f'stress_{i:03d}.txt'
 data=p.read_bytes()
 # In this format the last TWO nonempty lines are target and runtime.
 lines=data.splitlines()
 if len(lines)<(1<<int(lines[0].split()[0]))+6:raise RuntimeError('invalid input length')
 original_target=int(lines[-2]);original_runtime=int(lines[-1])
 lines[-1]=b'100'
 new=b'\n'.join(lines)+b'\n';dst.write_bytes(new)
 assert int(dst.read_bytes().splitlines()[-2])==original_target
 assert int(dst.read_bytes().splitlines()[-1])==100
 a['cases'].append({'file':dst.name,'source_holdout':p.name,'runtime_limit_ms':100,
    'sha256':hashlib.sha256(dst.read_bytes()).hexdigest(),'size_bytes':dst.stat().st_size})
manifest.write_text(json.dumps(a,indent=2)+'\n')
print('FROZEN stress bank',len(a['cases']))

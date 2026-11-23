#!/usr/bin/env python3
"""Deterministic synthetic DAG-function holdout; NOT sampled from course hidden distribution.
Freeze hashes BEFORE evaluating any synthesizer. Generated once, no tuning on results.
"""
from pathlib import Path
import random,hashlib,json
P=Path(__file__).resolve().parents[1];OUT=P/'evidence/holdout_frozen';OUT.mkdir(exist_ok=True,parents=True)
seed=820201;R=random.Random(seed);manifest={'seed':seed,'cases':{},'method':'random acyclic 2-input AND/OR/NOT gate networks; bit-exact truth tables'}
for trial in range(24):
 n=R.randint(5,10);m=R.randint(2,6);gates=R.randint(35,115)
 nodes=[];arrival=[0]*(n+1)
 aa,ao,an=R.randint(1,8),R.randint(1,8),R.randint(1,3)
 da,dor,dn=R.randint(1,4),R.randint(1,4),R.randint(1,3)
 for g in range(gates):
  op=R.choices((0,1,2),weights=(5,4,2))[0]
  a=R.randrange(1,n+1+g) if R.random()<0.92 else 0
  if op==2:b=0
  else:
   b=R.randrange(1,n+1+g) if R.random()<0.92 else 0
  nodes.append((op,a,b));arrival.append(arrival[a]+dn if op==2 else max(arrival[a],arrival[b])+(da if op==0 else dor))
 # Use shared and independent output cones, but never depend on generator case name at runtime
 outputs=[R.randrange(n+1,n+gates+1) for _ in range(m)]
 d=max(arrival[o] for o in outputs);target=d+R.randint(8,25)
 rows=[]
 for inp in range(1<<n):
  vals=[0]+[(inp>>(n-1-v))&1 for v in range(n)]
  for op,a,b in nodes:
   vals.append((1-vals[a]) if op==2 else (vals[a]&vals[b]) if op==0 else (vals[a]|vals[b]))
  rows.append(''.join(str(vals[o]) for o in outputs))
 content=f'{n} {m}\n'+'\n'.join(rows)+f'\n{aa} {da}\n{ao} {dor}\n{an} {dn}\n{target}\n10000\n'
 f=OUT/f'holdout_{trial+1:03}.txt';f.write_text(content)
 manifest['cases'][f.name]=hashlib.sha256(f.read_bytes()).hexdigest()
(OUT/'FROZEN_MANIFEST.json').write_text(json.dumps(manifest,indent=2)+'\n')
print('FROZEN_HOLDOUT',len(manifest['cases']),'manifest_sha256',hashlib.sha256((OUT/'FROZEN_MANIFEST.json').read_bytes()).hexdigest())

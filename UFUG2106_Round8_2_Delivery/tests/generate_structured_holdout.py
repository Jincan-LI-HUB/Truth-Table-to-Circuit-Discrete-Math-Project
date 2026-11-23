#!/usr/bin/env python3
"""Generate and freeze a SECOND nontrivial synthetic holdout, before running any solver.
Balanced XOR/MUX/MAJ/composite functions prevent the all-constant trap in holdout v1.
This is *synthetic* and not guaranteed representative of the course hidden tests.
"""
from pathlib import Path
import random,hashlib,json
P=Path(__file__).resolve().parents[1];OUT=P/'evidence/holdout_structured_v2';OUT.mkdir(parents=True,exist_ok=True)
seed=820202;R=random.Random(seed);manifest={'seed':seed,'cases':{},'design':'balanced XOR/MUX/Majority/function composites, support>=3, frozen prior to solver evaluation'}
for case in range(24):
 n=R.randint(6,11);m=R.randint(3,6);N=1<<n;allmask=(1<<N)-1
 vec=[];deps=[]
 for i in range(n):
  x=sum(1<<row for row in range(N) if (row>>(n-i-1))&1)
  vec.append(x);deps.append(frozenset([i]))
 for step in range(R.randint(45,85)):
  op=R.choices(['xor','maj','mux','and','or'],[32,20,28,10,10])[0]
  k=3 if op in ('maj','mux') else 2
  ids=[R.randrange(len(vec)) if R.random()<.48 else R.randrange(max(0,len(vec)-25),len(vec)) for _ in range(k)]
  a,b=vec[ids[0]],vec[ids[1]]
  if op=='xor':v=a^b
  elif op=='maj':
   c=vec[ids[2]];v=(a&b)|(a&c)|(b&c)
  elif op=='mux':
   c=vec[ids[2]];v=(a&b)|((allmask^a)&c)
  elif op=='and':v=a&b
  else:v=a|b
  if v==0 or v==allmask:continue
  vec.append(v);deps.append(frozenset.union(*(deps[i] for i in ids)))
 cand=[i for i,v in enumerate(vec) if len(deps[i])>=3 and .14<(v.bit_count()/N)<.86]
 if len(cand)<m:raise RuntimeError(f'insufficient nontrivial outputs for case {case}')
 chosen=R.sample(cand,m)
 outputs=[vec[i] for i in chosen]
 lines=[''.join('1' if (v>>s)&1 else '0' for v in outputs) for s in range(N)]
 aa,ao,an=R.randint(1,8),R.randint(1,8),R.randint(1,3)
 da,dor,dn=R.randint(1,4),R.randint(1,4),R.randint(1,3)
 target=R.randint(60,90);limit=10000
 content=f'{n} {m}\n'+'\n'.join(lines)+f'\n{aa} {da}\n{ao} {dor}\n{an} {dn}\n{target}\n{limit}\n'
 f=OUT/f'structured_{case+1:03}.txt';f.write_text(content)
 manifest['cases'][f.name]=hashlib.sha256(f.read_bytes()).hexdigest()
(OUT/'FROZEN_MANIFEST.json').write_text(json.dumps(manifest,indent=2)+'\n')
print('STRUCTURED_HOLDOUT_FROZEN cases=',len(manifest['cases']),'manifest_sha256=',hashlib.sha256((OUT/'FROZEN_MANIFEST.json').read_bytes()).hexdigest())

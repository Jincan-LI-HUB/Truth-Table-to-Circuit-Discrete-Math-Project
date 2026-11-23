#!/usr/bin/env python3
"""Reproducible synthetic correctness bank, independent of Round8 synthesizer."""
from pathlib import Path
import random,hashlib,json
H=Path(__file__).resolve().parents[1];out=H/'evidence/fresh_synthetic_v1';out.mkdir(parents=True,exist_ok=True)
seed=20261122085;rg=random.Random(seed)
def expr(which,b,x):
 n=len(b);a=which%n;z=(which*3+1)%n;k=(which*5+2)%n
 if which%7==0:return b[a]&b[z]
 if which%7==1:return b[a]^b[z]
 if which%7==2:return (b[a]&b[z]) | (b[k]& (not b[z]))
 if which%7==3:return ((sum(b)>n//2) ^ b[a])
 if which%7==4:return ((sum(b[i] for i in range(0,n,2))%2)==1)
 if which%7==5:return (not b[a]) | (b[k] and b[z])
 return ((sum(b[i] for i in range(n) if i%3!=2)%3)==1)
manifest={}
for c in range(1,19):
 n=rg.randint(5,10);m=rg.randint(1,5);which=rg.randint(0,120)
 token=[]
 for row in range(1<<n):
  bits=[(row>>(n-i-1))&1 for i in range(n)]
  token.append(''.join('1' if expr(which+j*7+1,bits,row) else '0' for j in range(m)))
 aa,da=rg.randint(1,8),rg.randint(1,4);ao,dor=rg.randint(1,8),rg.randint(1,4);an,dn=rg.randint(1,3),rg.randint(1,3)
 target=rg.randint(45,95)
 runtime=10000 if c%3==0 else 1000
 p=out/f'synthetic_{c:03d}.txt'
 p.write_text(f'{n}\n{m}\n'+ ' '.join(token)+f'\n{aa} {da}\n{ao} {dor}\n{an} {dn}\n{target}\n{runtime}\n')
 manifest[p.name]={'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'n':n,'m':m,'target':target,'runtime_limit':runtime}
(out/'MANIFEST.json').write_text(json.dumps({'generator_seed':seed,'cases':manifest},indent=2)+'\n')
print('generated',len(manifest),'independent functional fixtures')

#!/usr/bin/env python3
"""Frozen independent n<=12 random/nonlinear logic functions for R9.1 discovery.
Development bank can diagnose cut activity; lockbox must remain sealed until
candidate algorithms/parameters are frozen. Never represent it as course hidden.
"""
import hashlib,json,random
from pathlib import Path
H=Path(__file__).resolve().parents[1]
seed=2026112290
cases=[('dev',1,9,4,'random'),('dev',2,10,6,'random'),
       ('dev',3,11,5,'shared'),('dev',4,12,8,'random'),
       ('lockbox',5,9,5,'random'),('lockbox',6,10,8,'shared'),
       ('lockbox',7,11,6,'random'),('lockbox',8,12,10,'shared')]

def generate(n,m,family,rng):
 N=1<<n
 if family=='random':
  output=[rng.getrandbits(N) for j in range(m)]
 else:
  mask=(1<<N)-1
  inp=[]
  for v in range(n):
   x=0
   for r in range(N):
    if (r>>(n-1-v))&1:x|=1<<r
   inp.append(x)
  pool=inp[:]
  for i in range(n*30):
   x=rng.choice(pool);y=rng.choice(pool[-min(50,len(pool)):])
   z=rng.choice([x&y,x|y,x^y])
   if rng.random()<.15:z^=mask
   pool.append(z)
  output=[]
  for j in range(m):
   a=pool[-1-(j*7)%(n*15)]
   b=pool[-1-(j*11)%(n*25)]
   output.append(a^b if j%3==0 else (a|b if j%3==1 else a&b))
 return output

def main():
 manifest=H/'hard_bank/FROZEN_MANIFEST.json'
 if manifest.exists():raise RuntimeError('Frozen bank exists; do not regenerate')
 manifest.parent.mkdir(parents=True,exist_ok=True)
 details=[]
 for group,case_id,n,m,family in cases:
  rng=random.Random(seed*100+case_id)
  N=1<<n;outs=generate(n,m,family,rng)
  path=H/'hard_bank'/group/f'hard_{case_id:03d}.txt'
  path.parent.mkdir(exist_ok=True)
  # Use strict PDF layout. Limit permits optimizing but can be revised only in
  # a separate *derived* bank, never edit these frozen cases.
  aa,da,ao,dor,an,dn=3,2,4,2,1,1
  with path.open('w') as f:
   f.write(f'{n}\n{m}\n')
   f.write(' '.join(''.join('1' if (bits>>r)&1 else '0' for bits in outs) for r in range(N))+'\n')
   f.write(f'{aa} {da}\n{ao} {dor}\n{an} {dn}\n200\n3000\n')
  details.append({'group':group,'file':str(path.relative_to(H)),'family':family,'n':n,'m':m,
      'sha256':hashlib.sha256(path.read_bytes()).hexdigest()})
 manifest.write_text(json.dumps({'seed':seed,'course_hidden':False,
    'frozen_before_round91_algorithm':True,'do_not_tune_on_lockbox':True,
    'cases':details},indent=2)+'\n')
 print('HARD_BANK_FROZEN',len(details),'cases (4 dev + 4 sealed lockbox)')
if __name__=='__main__':main()

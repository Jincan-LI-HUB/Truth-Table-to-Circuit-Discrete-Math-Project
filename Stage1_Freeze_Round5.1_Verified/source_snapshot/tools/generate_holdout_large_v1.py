from pathlib import Path
import random,hashlib,json
seed=0x515A7E11
r=random.Random(seed)
root=Path(__file__).resolve().parents[1]/'tests'/'holdout_large_v1';root.mkdir(parents=True,exist_ok=True)
manifest=[]
for case in range(16):
 n=[12,14,16,17][case%4]
 m=[8,10,12,14][case%4]
 kind=['local_lookups','shared_ensemble','xor_of_lookups','cascaded_mux'][case%4]
 funcs=[]
 for j in range(m):
  s1=r.sample(range(n),r.randint(4,7)); s2=r.sample(range(n),r.randint(4,7))
  l1=[r.getrandbits(1) for _ in range(1<<len(s1))]
  l2=[r.getrandbits(1) for _ in range(1<<len(s2))]
  funcs.append((s1,s2,l1,l2,r.randrange(n)))
 shared=r.sample(range(n),5);shared_t=[r.getrandbits(1) for _ in range(1<<5)]
 out=[]
 def lut(x,ix,tbl):
  k=0
  for i in ix:k=(k<<1)|((x>>(n-1-i))&1)
  return tbl[k]
 for x in range(1<<n):
  sh=lut(x,shared,shared_t)
  row=[]
  for j,(s1,s2,l1,l2,sel) in enumerate(funcs):
   a=lut(x,s1,l1);b=lut(x,s2,l2)
   if kind=='local_lookups':v=a^b
   elif kind=='shared_ensemble':v=(a&sh)^(b & (j%2))
   elif kind=='xor_of_lookups':v=(a^b^sh)
   else:v=a if ((x>>(n-1-sel))&1) else b
   row.append(str(v))
  out.append(''.join(row))
 costs=[r.randint(1,8),r.randint(1,5),r.randint(1,8),r.randint(1,5),r.randint(1,6),r.randint(1,4)]
 target=150;limit=10000
 content=f'{n}\n{m}\n'+' '.join(out)+f'\n{costs[0]} {costs[1]}\n{costs[2]} {costs[3]}\n{costs[4]} {costs[5]}\n{target}\n{limit}\n'
 name=f'case_{case:03d}.txt';(root/name).write_text(content)
 manifest.append(dict(case=name,kind=kind,n=n,m=m,sha256=hashlib.sha256(content.encode()).hexdigest()))
(root.parent/'holdout_large_manifest.json').write_text(json.dumps(dict(seed=seed,designed_before_testing=True,rows=manifest),indent=2))
print('LARGE HOLDOUT',len(manifest),'manifestsha',hashlib.sha256((root.parent/'holdout_large_manifest.json').read_bytes()).hexdigest())

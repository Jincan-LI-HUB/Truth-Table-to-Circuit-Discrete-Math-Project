from pathlib import Path
import random, hashlib, json
seed=0x51A17C0DE
rng=random.Random(seed)
root=Path(__file__).resolve().parents[1]/'tests'/'holdout_v1'
root.mkdir(parents=True,exist_ok=True)
rows=[]
kinds=['affine','sparse','threshold','mux','arithmetic','shared','structured','dense']
for idx in range(80):
 kind=kinds[idx%len(kinds)]
 n=rng.randint(4,10) if kind=='dense' else rng.randint(5,15)
 if kind in ('sparse','structured') and n>12: n=12
 m=rng.randint(1,4)
 if kind=='shared':m=rng.randint(3,7)
 selectors=[rng.sample(range(n),min(n,rng.randint(2,5))) for _ in range(m)]
 masks=[rng.getrandbits(n) for _ in range(m)]
 threshold=[rng.randint(1,len(a)) for a in selectors]
 sparse=[[(rng.getrandbits(n), rng.getrandbits(n)) for _ in range(rng.randint(1,6))] for _ in range(m)]
 fam=[rng.sample(range(n),min(n,rng.randint(2,5))) for _ in range(m)]
 truth=[]
 for a in range(1<<n):
  row=[]
  for j in range(m):
   x=lambda b:(a>>(n-1-b))&1
   if kind=='affine':v=(a&masks[j]).bit_count()%2
   elif kind=='sparse':v=int(any((a&ms)==(v&ms) for v,ms in sparse[j]))
   elif kind=='threshold':v=int(sum(x(b) for b in selectors[j])>=threshold[j])
   elif kind=='mux':
    bits=fam[j];v=x(bits[1] if x(bits[0]) else bits[-1])
   elif kind=='arithmetic':
    shift=min(n-1,1+j);v=((a + (a>>shift))>>j)&1
   elif kind=='shared':
    base=int(sum(x(b) for b in selectors[0])>=threshold[0]);v=base if j%3==0 else base^((a&masks[j]).bit_count()%2) if j%3==1 else base & x(selectors[j][0])
   elif kind=='structured':
    bits=fam[j];v=0
    for b in bits:v^=(x(b)&x(bits[0]))
   else:
    # deterministic pseudo-random dense truth, independent of optimization
    v=int(hashlib.blake2s(f'{seed}:{idx}:{a}:{j}'.encode(),digest_size=1).digest()[0]&1)
   row.append(str(v))
  truth.append(''.join(row))
 cost=[rng.randint(1,8),rng.randint(1,5),rng.randint(1,8),rng.randint(1,5),rng.randint(1,6),rng.randint(1,4)]
 target=rng.randint(80,160) # correctness focus; not tuned against implementation
 runtime=10000
 content=f'{n}\n{m}\n'+' '.join(truth)+'\n'+f'{cost[0]} {cost[1]}\n{cost[2]} {cost[3]}\n{cost[4]} {cost[5]}\n{target}\n{runtime}\n'
 f=root/f'case_{idx:03d}.txt';f.write_text(content)
 rows.append(dict(case=f.name,kind=kind,n=n,m=m,sha256=hashlib.sha256(content.encode()).hexdigest()))
(root.parent/'holdout_manifest.json').write_text(json.dumps(dict(seed=seed,generated_before_implementation=True,rows=rows),indent=2))
print('FROZEN_HOLDOUT',len(rows), 'sha256 manifest',hashlib.sha256((root.parent/'holdout_manifest.json').read_bytes()).hexdigest())

#!/usr/bin/env python3
"""Precommitted Round 6.0 distribution holdout. Seed 602106; never tuned to official cases."""
from pathlib import Path
from random import Random
import hashlib, json
SEED=602106
rng=Random(SEED)
root=Path(__file__).resolve().parents[1]/'tests'/'holdout_round60_v1'
root.mkdir(parents=True,exist_ok=True)
manifest={'seed':SEED,'cases':[],'description':'40 cases, 5 distinct function families, n=8..13, 3-5 outputs; held out from algorithm tuning'}
for i in range(40):
    family=['affine','mux','threshold','sop','random_dag'][i%5]
    n=8+(i//5)%6;m=3+(i%3)
    rr=Random(SEED+i*1009); funcs=[]
    for j in range(m):
        if family=='affine':
            mask=rr.randrange(1,1<<n);bias=rr.randrange(2)
            funcs.append(lambda x,mask=mask,bias=bias:((x&mask).bit_count()+bias)%2)
        elif family=='mux':
            s=rr.sample(range(n),4);a,b,c,d=s
            funcs.append(lambda x,a=a,b=b,c=c,d=d:((x>>a&1) if (x>>b&1) else ((x>>c&1)^(x>>d&1))))
        elif family=='threshold':
            variables=rr.sample(range(n),max(3,n-2));threshold=rr.randint(2,len(variables)-1)
            funcs.append(lambda x,variables=variables,threshold=threshold:int(sum(x>>v&1 for v in variables)>=threshold))
        elif family=='sop':
            cubes=[]
            for _ in range(5):
                pos=rr.sample(range(n),rr.randint(2,4));want=[rr.randrange(2) for _ in pos];cubes.append(list(zip(pos,want)))
            funcs.append(lambda x,cubes=cubes:int(any(all((x>>v&1)==b for v,b in cube) for cube in cubes)))
        else:
            # fixed seeded random gate network with shared intermediate gates
            # (no per-case optimizing or observed-result feedback).
            ops=[]
            for t in range(45):
                a=rr.randrange(n+t);b=rr.randrange(n+t)
                ops.append((rr.randrange(3),a,b))
            root_id=n+rr.randrange(24,45)
            def f(x,ops=ops,root_id=root_id,n=n):
                val=[(x>>k)&1 for k in range(n)]
                for op,a,b in ops:
                    val.append((val[a]&val[b]) if op==0 else (val[a]|val[b]) if op==1 else (val[a]^1))
                return val[root_id]
            funcs.append(f)
    parts=[str(n),str(m),' '.join(''.join(str(f(x)) for f in funcs) for x in range(1<<n))]
    costs=[rr.randint(2,8),rr.randint(1,4),rr.randint(2,8),rr.randint(1,4),rr.randint(1,5),rr.randint(1,3)]
    parts+=[' '.join(map(str,costs[0:2])),' '.join(map(str,costs[2:4])),' '.join(map(str,costs[4:6])),'130','10000']
    p=root/f'case_{i:03}.txt';p.write_text('\n'.join(parts)+'\n')
    manifest['cases'].append({'case':p.name,'n':n,'m':m,'family':family,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
(root.parent/'holdout_round60_v1_manifest.json').write_text(json.dumps(manifest,indent=2))
print('frozen',len(manifest['cases']),'manifest',root.parent/'holdout_round60_v1_manifest.json')

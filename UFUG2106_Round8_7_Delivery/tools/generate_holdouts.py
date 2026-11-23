#!/usr/bin/env python3
"""New, reproducible R8.7 generalization bank. Not course-hidden cases.
All Boolean functions are generated INDEPENDENTLY of the solver and then
frozen, with SHA256 provenance. No learning/tuning on generated results.
"""
import argparse, hashlib, json, random
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
SEED=2026112287
CASES=[
 # id, family, input size, outputs, runtime limit(ms)
 (1,'direct',20,3,1000),(2,'parity',20,3,3000),
 (3,'mux',18,5,3000),(4,'shared',16,8,3000),
 (5,'majority',12,5,1000),(6,'sparse',16,4,3000),
 (7,'random',10,5,3000),(8,'random',12,5,3000),
 (9,'mux',12,8,1000),(10,'shared',10,12,1000),
 (11,'parity',14,5,1000),(12,'majority',16,4,3000),
 (13,'sparse',12,6,1000),(14,'random',8,8,1000),
 (15,'direct',14,8,100),(16,'mux',10,6,100),
 (17,'shared',8,12,100),(18,'parity',10,4,100),
 (19,'majority',8,6,100),(20,'sparse',9,8,100),
 (21,'random',7,6,100),(22,'random',9,9,1000),
 (23,'parity',18,3,3000),(24,'mux',16,6,3000),
 (25,'shared',14,16,3000),(26,'majority',10,7,1000),
 (27,'sparse',14,8,3000),(28,'random',11,8,3000),
 (29,'direct',6,20,100),(30,'shared',6,20,1000),
 (31,'mux',8,18,1000),(32,'parity',8,20,1000),
 (33,'majority',13,5,3000),(34,'sparse',18,3,3000),
 (35,'random',6,9,100),(36,'random',14,4,3000),
]

def one_input_mask(N,j):
    """For row r, bit r indicates truth bit of variable with index from LSB j."""
    if j<3:
        by=bytes([sum(((r>>j)&1)<<r for r in range(8))])*(N//8)
    else:
        length=1<<(j-3)
        by=(bytes(length)+b'\xff'*length)*(N>>(j+1))
    return int.from_bytes(by,'little')

def combine(family,n,m,rng):
    N=1<<n; full=(1<<N)-1
    inp=[one_input_mask(N,n-i-1) for i in range(n)]
    pool=list(inp)
    neg=lambda x: full^x
    def gate(op,a,b):
        if op=='and':return a&b
        if op=='or':return a|b
        if op=='xor':return a^b
        raise ValueError(op)
    def random_circuit(k,style):
        for z in range(k):
            if style=='shared':
                a=rng.choice(pool[-max(3,min(len(pool),18)):]);b=rng.choice(pool)
            else:
                a=rng.choice(pool);b=rng.choice(pool)
            if rng.random()<.14:a=neg(a)
            if rng.random()<.15:b=neg(b)
            op=rng.choices(['and','or','xor'],[4,4,2] if style=='shared' else [3,3,4])[0]
            pool.append(gate(op,a,b))
    if family=='shared':random_circuit(2*n+3,'shared')
    if family=='random':random_circuit(5*n+7,'random')
    outputs=[]
    for k in range(m):
        if family=='direct':
            val=pool[(k*7+1)%n]; val=neg(val) if k%4==3 else val
        elif family=='parity':
            idx=rng.sample(range(n),k=rng.randint(3,min(n,15)))
            val=0
            for t in idx:val^=inp[t]
            if k%4==2:val=neg(val)
        elif family=='mux':
            sel=inp[(k+1)%n];a=inp[(k*3+2)%n];b=inp[(k*5+3)%n]
            val=(sel&a)|(neg(sel)&b)
            if k%3==2:
                val=(val & inp[(k+4)%n]) | (neg(val)&inp[(k+6)%n])
        elif family=='majority':
            v=rng.sample(range(n),k=min(n,7));v=v[:len(v)//2*2+1]
            # Majority-of-3 trees plus additional combiners: no hidden oracle needed.
            a,b,c=[inp[t] for t in v[:3]]
            val=(a&b)|(a&c)|(b&c)
            for ix in range(3,len(v),2):
                a,b=inp[v[ix]],inp[v[ix+1]]
                val=(val&a)|(val&b)|(a&b)
        elif family=='sparse':
            val=0
            for _ in range(rng.randint(3,7)):
                t=full
                for ix in rng.sample(range(n),k=rng.randint(2,min(n,5))):
                    t &= (neg(inp[ix]) if rng.random()<.5 else inp[ix])
                val|=t
            if k%3==1:val=neg(val)
        elif family in ('shared','random'):
            val=pool[-1-k%min(len(pool),2*n)]
            if k%3==0:val=val^inp[k%n]
            if k%5==4:val=neg(val)
        else:raise ValueError(family)
        outputs.append(val)
    return outputs

def write_case(path,n,m,ms,rng,outputs):
    N=1<<n
    # Independent little-endian truth column representation; output row 0 first.
    columns=[v.to_bytes(N//8,'little') for v in outputs]
    aa=rng.randint(1,8);ao=rng.randint(1,8);an=rng.randint(1,4)
    da=rng.randint(1,4);dor=rng.randint(1,4);dn=rng.randint(1,4)
    # Conservative target, so we primarily measure runtime/correctness rather than
    # accidental target infeasibility from arbitrary generated gate weights.
    target=170 if ms!=100 else 140
    with path.open('w') as f:
        f.write(f'{n} {m}\n')
        chunk=[]
        for byteset in zip(*columns):
            for bit in range(8):
                chunk.append(''.join('1' if (b>>bit)&1 else '0' for b in byteset))
            if len(chunk)>=4096:
                f.write('\n'.join(chunk)+'\n');chunk=[]
        if chunk:f.write('\n'.join(chunk)+'\n')
        f.write(f'{aa} {da}\n{ao} {dor}\n{an} {dn}\n{target}\n{ms}\n')
    return {'and_area':aa,'and_delay':da,'or_area':ao,'or_delay':dor,
            'not_area':an,'not_delay':dn,'target':target}

def main():
    a=argparse.ArgumentParser();a.add_argument('--verify',action='store_true');a=a.parse_args()
    out=ROOT/'holdouts';out.mkdir(exist_ok=True)
    mpath=out/'FROZEN_MANIFEST.json'
    if a.verify:
        meta=json.loads(mpath.read_text());assert meta['generator_seed']==SEED
        assert len(meta['cases'])==len(CASES)
        for case in meta['cases']:
            p=out/case['file']
            if not p.is_file() or hashlib.sha256(p.read_bytes()).hexdigest()!=case['sha256']:
                raise RuntimeError('Frozen holdout changed: '+str(p))
        print('PASS frozen holdout hash validation',len(meta['cases']),flush=True);return
    if mpath.exists():raise RuntimeError('Refusing to regenerate frozen holdouts')
    meta={'generator_seed':SEED,'course_hidden':False,'selected_before_scores':True,
          'source':'Independent bit-vector Boolean circuit generator','cases':[]}
    for idx,family,n,m,ms in CASES:
        rng=random.Random(SEED*1000+idx)
        filename=f'holdout_{idx:03d}.txt';p=out/filename
        output=combine(family,n,m,rng)
        costs=write_case(p,n,m,ms,rng,output)
        meta['cases'].append(dict(file=filename,sha256=hashlib.sha256(p.read_bytes()).hexdigest(),
            family=family,n=n,m=m,runtime_limit_ms=ms,bytes=p.stat().st_size,**costs))
        print('GENERATED',filename,family,n,m,ms,p.stat().st_size,flush=True)
    mpath.write_text(json.dumps(meta,indent=2)+'\n')
    print('FROZEN',len(CASES),'cases; seed=',SEED,flush=True)
if __name__=='__main__':main()

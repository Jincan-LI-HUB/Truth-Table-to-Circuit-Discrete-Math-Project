#!/usr/bin/env python3
"""Independent bit-parallel evaluator. Exhaustive if n<=13; seeded sample otherwise.
For large n this is a regression smoke test, NOT a formal equivalence proof.
"""
from __future__ import annotations
import argparse, random
from pathlib import Path

def run(case_path:Path,net_path:Path,sample=768):
    tokens=case_path.read_text().split();n=int(tokens[0]);m=int(tokens[1]);N=1<<n
    assert len(tokens)>=2+N+7,'Bad input'
    tt=tokens[2:2+N]
    aa,da,ao,do,an,dn,target=map(int,tokens[2+N:2+N+7])
    if n<=13:rows=list(range(N));exhaustive=True
    else:
        rng=random.Random(2106)
        rows=sorted(set([0,N-1,*[1<<k for k in range(n)],
            *[N-1-(1<<k) for k in range(n)],*(rng.randrange(N) for _ in range(sample))]));exhaustive=False
    width=len(rows);mask=(1<<width)-1
    sig=[0]
    for j in range(n):sig.append(sum(((row>>(n-j-1))&1)<<i for i,row in enumerate(rows)))
    arr=[0]*(n+1);area=0
    net=[line.split() for line in net_path.read_text().splitlines() if line.strip()]
    assert net,'Empty netlist'
    for g in net[:-1]:
        id=int(g[0]);typ=g[1];a=int(g[2]);b=int(g[3]) if len(g)>3 else None
        assert id==len(sig) and 0<=a<id,(id,a,len(sig))
        if typ=='NOT':
            assert b is None
            x=(~sig[a])&mask;t=arr[a]+dn;area+=an
        else:
            assert b is not None and 0<=b<id
            if typ=='AND2':x=sig[a]&sig[b];t=max(arr[a],arr[b])+da;area+=aa
            elif typ=='OR2':x=sig[a]|sig[b];t=max(arr[a],arr[b])+do;area+=ao
            else:raise AssertionError('Invalid op '+typ)
        sig.append(x);arr.append(t)
    outs=list(map(int,net[-1]));assert len(outs)==m and all(0<=x<len(sig) for x in outs)
    for j,id in enumerate(outs):
        expected=sum((tt[row][j]=='1')<<i for i,row in enumerate(rows))
        assert sig[id]==expected,(j,len(rows),'output mismatch')
    return {'matched':True,'exhaustive':exhaustive,'assignments':width,'area':area,
      'delay':max(arr[x] for x in outs),'target':target}
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('case',type=Path);p.add_argument('net',type=Path)
    p.add_argument('--samples',type=int,default=768);a=p.parse_args()
    print(run(a.case,a.net,a.samples))

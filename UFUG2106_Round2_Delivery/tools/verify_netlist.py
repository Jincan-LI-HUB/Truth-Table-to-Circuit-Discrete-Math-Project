#!/usr/bin/env python3
"""Independent bit-parallel verifier. Exhaustive if n<=13, sampled otherwise.
Not a replacement for the official evaluator on large inputs."""
import argparse
import random
from pathlib import Path

def run(case_path: Path, net_path: Path, sample=256):
    tokens=case_path.read_text().split()
    n,m=int(tokens[0]),int(tokens[1]); rows=1<<n
    assert len(tokens)>=2+rows+7, 'incomplete input'
    tt=tokens[2:2+rows]
    aa,da,ao,dor,an,dn,target=map(int,tokens[2+rows:2+rows+7])
    if n<=13: indices=list(range(rows)); exhaustive=True
    else:
        rng=random.Random(2106)
        indices=sorted(set([0,rows-1,*[1<<k for k in range(n)],
                            *[rows-1-(1<<k) for k in range(n)],
                            *(rng.randrange(rows) for _ in range(sample))]))
        exhaustive=False
    width=len(indices); mask=(1<<width)-1
    signals=[0]
    for j in range(n):
        b=sum(((r>>(n-1-j))&1)<<i for i,r in enumerate(indices))
        signals.append(b)
    area=0; arrival=[0]*(n+1)
    lines=[line.split() for line in net_path.read_text().splitlines() if line.strip()]
    assert lines,'empty netlist'
    for g in lines[:-1]:
        assert len(g) in (3,4),g
        id=int(g[0]);typ=g[1];a=int(g[2]);b=int(g[3]) if len(g)==4 else None
        assert id==len(signals) and 0<=a<id,(id,len(signals))
        if typ=='NOT':
            assert b is None
            sig=(~signals[a])&mask; t=arrival[a]+dn;area+=an
        else:
            assert b is not None and 0<=b<id
            if typ=='AND2':sig=signals[a]&signals[b];t=max(arrival[a],arrival[b])+da;area+=aa
            elif typ=='OR2':sig=signals[a]|signals[b];t=max(arrival[a],arrival[b])+dor;area+=ao
            else:raise AssertionError('unsupported gate: '+typ)
        signals.append(sig);arrival.append(t)
    outputs=list(map(int,lines[-1]))
    assert len(outputs)==m and all(0<=v<len(signals) for v in outputs)
    for j,oid in enumerate(outputs):
        expected=sum((tt[r][j]=='1')<<i for i,r in enumerate(indices))
        assert signals[oid]==expected,(j,len(indices),'mismatch')
    return dict(exhaustive=exhaustive,assignments=len(indices),area=area,
                delay=max(arrival[v] for v in outputs),target=target,
                matched=True)

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('case');parser.add_argument('netlist');parser.add_argument('--samples',type=int,default=256)
    a=parser.parse_args();print(run(Path(a.case),Path(a.netlist),a.samples))

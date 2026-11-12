#!/usr/bin/env python3
"""Reproduce and independently verify the pedagogical 3-input, 2-output example.
No external packages or benchmark inputs required.
"""
import csv
from pathlib import Path
from itertools import product

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'data' / 'worked_example_truth_table.csv'
COST = {'AND2':(2,2), 'OR2':(3,2), 'NOT':(1,1)}
BASE = [(4,'NOT',1,None),(5,'AND2',1,2),(6,'AND2',4,3),(7,'OR2',5,6),(8,'OR2',7,2)]
FAST = BASE[:-1] + [(8,'OR2',2,6)]

def simulate(net,a,b,c):
    sig={0:0,1:a,2:b,3:c}
    arrival={0:0,1:0,2:0,3:0}
    for ident,op,x,y in net:
        if op=='NOT':
            sig[ident]=1-sig[x]
            arrival[ident]=arrival[x]+COST[op][1]
        else:
            sig[ident]=(sig[x] & sig[y]) if op=='AND2' else (sig[x] | sig[y])
            arrival[ident]=max(arrival[x],arrival[y])+COST[op][1]
    area=sum(COST[op][0] for _,op,_,_ in net)
    return (sig[7],sig[8]),area,max(arrival[7],arrival[8]),arrival[7],arrival[8]

rows=[]
for a,b,c in product((0,1),repeat=3):
    f1=(a & b) | ((1-a)&c)
    f2=f1|b
    v0,area0,d0,t7,t8=simulate(BASE,a,b,c)
    v1,area1,d1,_,t8_fast=simulate(FAST,a,b,c)
    assert v0==v1==(f1,f2)
    assert area0==area1==11
    assert d0==7 and d1==5 and t7==5 and t8==7 and t8_fast==5
    rows.append((a,b,c,f1,f2))
OUT.parent.mkdir(parents=True,exist_ok=True)
with OUT.open('w',newline='') as fh:
    wr=csv.writer(fh);wr.writerow(['a','b','c','f1','f2']);wr.writerows(rows)
print('PASS: exhaustive 8/8 assignments; baseline area=11 delay=7; rewritten area=11 delay=5')
print(f'Wrote {OUT}')

#!/usr/bin/env python3
"""Generic low-RAM regression cases, including original Issue #2 and nontrivial functions."""
from pathlib import Path
import argparse

def generate(out:Path,n:int,kind:str,ram:int,limit:int=0,target:int=10):
    fns={
     'wire':lambda x:(x&1,),
     'not_wire':lambda x:(1-(x&1),),
     'constant_one':lambda x:(1,),
     'xor2':lambda x:(((x&1)^((x>>1)&1)),),
     'majority3':lambda x:(int(((x&1)+((x>>1)&1)+((x>>2)&1))>=2),),
     'multi':lambda x:(x&1,1-((x>>1)&1),(x&1)^((x>>1)&1)),
     'four_var':lambda x:((((x&1)^((x>>1)&1)) & (((x>>2)&1)|((x>>3)&1))),),
     'parity_all':lambda x:(x.bit_count()&1,),
     'and_all':lambda x:(int(x==(1<<n)-1),),
     'or_all':lambda x:(int(x!=0),),
    }
    fn=fns[kind]
    m=len(fn(0))
    out.parent.mkdir(parents=True,exist_ok=True)
    with out.open('w') as f:
        f.write(f'{n}\n{m}\n')
        for row in range(1<<n):
            f.write(''.join(map(str,fn(row))))
            f.write(' ' if row+1!=(1<<n) else '\n')
        f.write(f'1 1\n1 1\n1 1\n{target}\n')
        f.write(f'{limit}\n{ram}\n')
    return out

if __name__=='__main__':
    ap=argparse.ArgumentParser()
    ap.add_argument('output',type=Path)
    ap.add_argument('--n',type=int,default=20)
    ap.add_argument('--kind',choices=['wire','not_wire','constant_one','xor2','majority3','multi','four_var','parity_all','and_all','or_all'],default='wire')
    ap.add_argument('--ram',type=int,default=9000)
    ap.add_argument('--limit',type=int,default=0)
    ap.add_argument('--target',type=int,default=10)
    a=ap.parse_args()
    print(generate(a.output,a.n,a.kind,a.ram,a.limit,a.target),flush=True)

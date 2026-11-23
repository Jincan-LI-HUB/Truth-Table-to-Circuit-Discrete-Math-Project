#!/usr/bin/env python3
"""Deterministic randomized exhaustive checker for isolated R8.1 cut resynthesis.
For every generated small DAG, verify all 2^n assignments after each mode.
"""
from pathlib import Path
import random,subprocess,tempfile
H=Path(__file__).resolve().parents[1];tool=H/'build/optimize_cut';checker=H/'build/verify_exhaustive'
R=random.Random(0x8100C0DE)
MODES=['sop','shannon','all','choices']
count=0
with tempfile.TemporaryDirectory(prefix='r81_random_') as t:
 T=Path(t)
 for test in range(180):
  n=R.randint(2,5);m=R.randint(1,4);size=R.randint(10,36)
  nodes=[]
  for g in range(size):
   op=R.choices((0,1,2),(4,4,2))[0]
   a=R.randrange(n+1+g)
   b=R.randrange(n+1+g) if op!=2 else 0
   nodes.append((op,a,b))
  outs=[R.randrange(1,n+1+size) for _ in range(m)]
  aa=R.randint(1,8);ao=R.randint(1,8);an=R.randint(1,3)
  da=R.randint(1,4);do=R.randint(1,4);dn=R.randint(1,3)
  v=0;ready=[0]*(n+1)
  for op,a,b in nodes:
   ready.append((ready[a]+dn) if op==2 else max(ready[a],ready[b])+(da if op==0 else do))
  target=max(ready[o] for o in outs)+R.randint(0,7)
  case=T/'in.txt';net=T/'before.txt'
  lines=[]
  for mask in range(1<<n):
   values=[0]+[(mask>>(n-i-1))&1 for i in range(n)]
   for op,a,b in nodes:values.append((values[a] if op==2 else values[a] & values[b] if op==0 else values[a] | values[b]) if op!=2 else 1-values[a])
   lines.append(''.join(str(values[o]) for o in outs))
  case.write_text(f'{n} {m}\n'+'\n'.join(lines)+f'\n{aa} {da}\n{ao} {do}\n{an} {dn}\n{target}\n100000\n')
  net.write_text(''.join(f'{n+1+i} {"AND2" if op==0 else "OR2" if op==1 else "NOT"} {a}'+(f' {b}' if op!=2 else '')+'\n' for i,(op,a,b) in enumerate(nodes))+' '.join(map(str,outs))+'\n')
  baseline=subprocess.run([str(checker),str(case),str(net)],capture_output=True,text=True)
  if baseline.returncode:raise RuntimeError('baseline check '+baseline.stderr)
  for mode in MODES:
   out=T/'after.txt';pr=subprocess.run([str(tool),str(case),str(net),str(out),mode],capture_output=True,text=True,timeout=7)
   if pr.returncode:raise RuntimeError(f'optimizer FAIL case={test} mode={mode} stderr={pr.stderr}')
   ck=subprocess.run([str(checker),str(case),str(out)],capture_output=True,text=True,timeout=7)
   if ck.returncode:raise RuntimeError(f'EQUIVALENCE FAIL case={test} mode={mode} stderr={ck.stderr}')
   count+=1
print(f'PASS randomized_cut_resynthesis: {count} exhaustive equivalence comparisons on 180 independent DAGs, seed=0x8100C0DE')

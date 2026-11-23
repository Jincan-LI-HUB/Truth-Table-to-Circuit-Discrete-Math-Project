#!/usr/bin/env python3
"""Reproducible random truth-table / netlist equality checks for every R8 mode.
All n<=6 cases are verified exhaustively by an independent C++ simulator.
"""
import argparse,random,tempfile,subprocess,json
from pathlib import Path
H=Path(__file__).resolve().parents[1];p=argparse.ArgumentParser();p.add_argument('--count',type=int,default=140);a=p.parse_args()
R=random.Random(21060821)
ops=['AND2','OR2','NOT'];modes=['absorb','factor','factor_relaxed','phase','reuse','combined','combined_relaxed']
verifications=0;improved=0
with tempfile.TemporaryDirectory(prefix='r8_equivalence_') as t:
 T=Path(t)
 for it in range(a.count):
  n=R.randint(3,6);m=R.randint(1,4);gate_count=R.randint(14,90)
  rows=1<<n;gates=[]
  for k in range(gate_count):
   node=n+1+k;op=R.choices(ops,[4,4,2])[0]
   x=R.randrange(node);z=R.randrange(node) if op!='NOT' else 0
   gates.append((op,x,z))
  out=[R.randrange(n+gate_count+1) for _ in range(m)]
  gate_text='\n'.join(f'{n+1+i} {op} {x}'+(f' {z}' if op!='NOT' else '') for i,(op,x,z) in enumerate(gates))
  nl=T/'old.txt';nl.write_text(gate_text+'\n'+' '.join(map(str,out))+'\n')
  truth=[]
  for r in range(rows):
   sig=[0]+[(r>>(n-1-j))&1 for j in range(n)]
   for op,x,z in gates:
    sig.append((sig[x]&sig[z]) if op=='AND2' else (sig[x]|sig[z]) if op=='OR2' else (1-sig[x]))
   truth.append(''.join(str(sig[o]) for o in out))
  aa,ao,an=[R.randint(1,8) for _ in range(3)];da,dor,dn=[R.randint(1,4) for _ in range(3)]
  case=T/'case.txt';case.write_text(f'{n}\n{m}\n'+'\n'.join(truth)+f'\n{aa} {da}\n{ao} {dor}\n{an} {dn}\n999\n10000\n')
  for mode in modes:
   output=T/'new.txt'
   res=subprocess.run([str(H/'build/optimize_netlist'),str(case),str(nl),str(output),mode],capture_output=True,text=True)
   if res.returncode:raise RuntimeError(f'{it} {mode} optimizing failed: {res.stderr}')
   chk=subprocess.run([str(H/'build/verify_exhaustive'),str(case),str(output)],capture_output=True,text=True)
   if chk.returncode:raise RuntimeError(f'{it} {mode}: Boolean mismatch: {chk.stdout} {chk.stderr}')
   verifications+=1
   import re
   x=re.search(r'R8_RESULT base_area=(\d+) base_delay=(\d+) area=(\d+) delay=(\d+)',res.stderr)
   if x and int(x.group(3))<int(x.group(1)):improved+=1
print(json.dumps({'random_seed':21060821,'circuits':a.count,'mode_comparisons':verifications,'equivalence_failures':0,'improving_comparisons':improved},indent=2))

#!/usr/bin/env python3
"""Offline iterative structural rewrite experiment on saved R7.2 netlists.
Uses input metadata only for mapping cost; no claim of original truth equivalence
except when the independent full truth-table checker is also run.
"""
from pathlib import Path
import subprocess,re,csv,tempfile,shutil
HERE=Path(__file__).resolve().parents[1]; ROOT=HERE.parent
src=ROOT/'round8_research/netlists';meta=HERE/'evidence/stage2_metadata'
out=HERE/'results/offline_iteration';out.mkdir(parents=True,exist_ok=True)
rows=[]
for f in sorted(src.glob('case_*.txt')):
 with tempfile.TemporaryDirectory() as tmp:
  current=Path(tmp)/'current.txt';shutil.copy(f,current)
  for iteration in range(1,6):
   output=Path(tmp)/'next.txt'
   run=subprocess.run([str(HERE/'build/optimize_netlist'),str(meta/(f.stem+'.meta')),str(current),str(output),'all'],capture_output=True,text=True,timeout=40)
   if run.returncode:raise RuntimeError(f'{f.name} pass {iteration}: {run.stderr}')
   m=re.search(r'R8_RESULT base_area=(\d+) base_delay=(\d+) area=(\d+) delay=(\d+)',run.stderr)
   a,d,na,nd=map(int,m.groups());rows.append(dict(case=f.stem,iteration=iteration,base_area=a,base_delay=d,area=na,delay=nd,improvement=a-na))
   shutil.move(output,current)
  if f.stem=='case_021':shutil.copy(current,out/'case_021_iterated.netlist')
 print(f'{f.stem} final area {rows[-1]["area"]}, savings {rows[-5]["base_area"]-rows[-1]["area"]}',flush=True)
with (out/'iterations.csv').open('w',newline='') as f:
 w=csv.DictWriter(f,list(rows[0]));w.writeheader();w.writerows(rows)
print('total savings',sum(r['improvement'] for r in rows),'nonzero passes',sum(r['improvement']>0 for r in rows))

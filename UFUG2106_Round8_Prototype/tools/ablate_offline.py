#!/usr/bin/env python3
"""One-pass ablation across the same frozen 25 Stage 2 netlists."""
from pathlib import Path
import csv,re,subprocess,tempfile
H=Path(__file__).resolve().parents[1]; ROOT=H.parent
modes=['absorb','factor','factor_relaxed','phase','reuse','combined','combined_relaxed']
rows=[]
for case in sorted((ROOT/'round8_research/netlists').glob('case_*.txt')):
 for mode in modes:
  with tempfile.TemporaryDirectory() as t:
   proc=subprocess.run([str(H/'build/optimize_netlist'),str(H/'evidence/stage2_metadata'/(case.stem+'.meta')),str(case),str(Path(t)/'output.txt'),mode],capture_output=True,text=True,timeout=20)
   if proc.returncode:raise RuntimeError(f'{case.stem} {mode} {proc.stderr}')
   m=re.search(r'R8_PROBE mode=\S+ area=(\d+) delay=(\d+) ms=([\d.]+) attempts=(\d+) factor=(\d+) absorb=(\d+) expand=(\d+) phase=(\d+) accepted=(\d+)',proc.stderr)
   b=re.search(r'R8_RESULT base_area=(\d+) base_delay=(\d+) area=(\d+) delay=(\d+)',proc.stderr)
   if not m or not b:raise RuntimeError(proc.stderr)
   a,d,ms,att,factor,absorb,expand,phase,accepted=m.groups();prev,prev_delay,now,now_delay=map(int,b.groups())
   rows.append(dict(case=case.stem,mode=mode,base_area=prev,base_delay=prev_delay,actual_area=int(a),actual_delay=int(d),selected_area=now,selected_delay=now_delay,area_saved=prev-now,rewrite_ms=float(ms),attempts=int(att),factoring=int(factor),absorption=int(absorb),divisor_expansion=int(expand),phase=int(phase),accepted=int(accepted)))
out=H/'evidence/stage2_onepass_ablation.csv'
with out.open('w',newline='') as f:
 w=csv.DictWriter(f,list(rows[0]));w.writeheader();w.writerows(rows)
for mode in modes:
 q=[r for r in rows if r['mode']==mode]
 print(f'{mode:18s} savings={sum(r["area_saved"] for r in q):4d} improved={sum(r["area_saved"]>0 for r in q):2d} total_patterns={sum(r["attempts"] for r in q):6d}')
print('Saved',out)

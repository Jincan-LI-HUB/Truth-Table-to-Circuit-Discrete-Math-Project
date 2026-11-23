#!/usr/bin/env python3
"""Local direct-run preliminary validation; does not invoke instructor evaluator."""
from pathlib import Path
import csv,subprocess,time,re,json,argparse
D=Path(__file__).resolve().parents[1]; ROOT=D.parent
p=argparse.ArgumentParser();p.add_argument('--cases',type=Path,default=ROOT/'round7_local_data/stage2');p.add_argument('--netlists',type=Path,default=ROOT/'round8_research/netlists');p.add_argument('--full-exhaustive',action='store_true');a=p.parse_args()
result=D/'results'/'local_preflight';result.mkdir(parents=True,exist_ok=True)
base={x['case']:x for x in csv.DictReader(open(ROOT/'round8_research/structural_baseline.csv'))}
rows=[]
for case in sorted(a.cases.glob('case_*.txt')):
 output=result/(case.stem+'.r8.txt');logs=result/(case.stem+'.log')
 t0=time.perf_counter();proc=subprocess.run([str(D/'build/synth_round8'),str(case),str(output)],env={**__import__('os').environ,'UFUG_R8_POLICY':'all','UFUG_R8_PROFILE':'1'},capture_output=True,text=True,timeout=80)
 dur=(time.perf_counter()-t0)*1000
 logs.write_text(proc.stdout+proc.stderr)
 if proc.returncode:raise RuntimeError(f'{case.stem} failed exit={proc.returncode}: {proc.stderr[:1000]}')
 m=re.search(r'completed=\d+ chosen=-?\d+ area=(\d+) delay=(\d+)',proc.stderr)
 if not m:raise RuntimeError(f'Cannot extract circuit metrics from {case.stem}')
 area,delay=map(int,m.groups());b=base[case.stem]
 vres=None
 if a.full_exhaustive or int(b['n'])<=13 or area!=int(b['area']):
  v=subprocess.run([str(D/'build/verify_exhaustive'),str(case),str(output)],capture_output=True,text=True,timeout=120)
  if v.returncode:raise RuntimeError(f'Equivalence failed {case.stem}: {v.stdout} {v.stderr}')
  vres=v.stdout.strip()
 rows.append(dict(case=case.stem,base_area=int(b['area']),r8_area=area,delta_area=area-int(b['area']),base_delay=int(b['delay']),r8_delay=delay,delta_delay=delay-int(b['delay']),runtime_local_ms=round(dur,3),exhaustive=bool(vres)))
 print(f'{case.stem}: area {b["area"]} -> {area}, delay {b["delay"]} -> {delay}, local {dur:.1f}ms, exhaustive={bool(vres)}',flush=True)
with (result/'stage2_direct_compare.csv').open('w',newline='') as f:
 w=csv.DictWriter(f,list(rows[0]));w.writeheader();w.writerows(rows)
print('SUMMARY',json.dumps({'cases':len(rows),'improved':sum(x['delta_area']<0 for x in rows),'savings':-sum(x['delta_area'] for x in rows),'verified_exhaustive':sum(x['exhaustive'] for x in rows)},indent=2))

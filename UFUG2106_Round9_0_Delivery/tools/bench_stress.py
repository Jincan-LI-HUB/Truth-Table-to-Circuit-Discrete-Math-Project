#!/usr/bin/env python3
"""Nonofficial direct-process latency/RSS paired stress benchmark (not scoring)."""
import argparse,csv,os,statistics,subprocess,time
from pathlib import Path
H=Path(__file__).resolve().parents[1]
def main():
 a=argparse.ArgumentParser();a.add_argument('--results',type=Path,required=True);a.add_argument('--reps',type=int,default=3);x=a.parse_args()
 out=x.results/'latency_benchmark';out.mkdir(parents=True,exist_ok=True)
 env={k:v for k,v in os.environ.items() if not k.startswith(('UFUG_R','UFUG_ROUND','R90_'))}
 rows=[]
 for i in (1,2,3):
  c=H/'canonical_bank/stress_v2'/f'stress_{i:03d}.txt'
  for rep in range(1,x.reps+1):
   for policy,exe,flags in [('r86_explicit_extra',H/'build/synth_round86_frozen',{'UFUG_R86_POLICY':'extra_sop'}),
                            ('r90_no_flags',H/'build/synth_round90',{})] if rep%2 else [
                            ('r90_no_flags',H/'build/synth_round90',{}),
                            ('r86_explicit_extra',H/'build/synth_round86_frozen',{'UFUG_R86_POLICY':'extra_sop'})]:
    output=out/f'stress_{i:03d}_{policy}_r{rep}.net'
    begin=time.perf_counter()
    z=subprocess.run([str(exe),str(c),str(output)],env=env|flags,
       capture_output=True,text=True,timeout=40)
    ms=1000*(time.perf_counter()-begin)
    if z.returncode or not output.exists():raise RuntimeError(f'Bad benchmark {i}, {policy} RC={z.returncode}')
    rows.append(dict(case=i,rep=rep,policy=policy,wall_ms=round(ms,3),reason=z.stderr.strip().split('\n')[0]))
    print('BENCH',i,rep,policy,round(ms,2),'ms',flush=True)
 with (out/'paired.csv').open('w',newline='') as f:
  w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
 for i in (1,2,3):
  print('BENCH_MEDIAN',i,{p:round(statistics.median(r['wall_ms'] for r in rows if r['case']==i and r['policy']==p),2)
     for p in ('r86_explicit_extra','r90_no_flags')},flush=True)
 print('NOTE: same-host direct-process latency, not official evaluator timing')
if __name__=='__main__':main()

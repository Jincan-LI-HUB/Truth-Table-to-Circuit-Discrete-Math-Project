#!/usr/bin/env python3
"""Exact truth-table comparisons; public and lockbox are not used for tuning."""
import os,subprocess,time,csv,hashlib,argparse
from pathlib import Path
H=Path(__file__).resolve().parents[1]

def run(inp,tag,kind,output):
 exe=H/'build'/('synth_round90_frozen' if kind is None else 'synth_round91')
 env=os.environ.copy()
 for k in list(env):
  if k.startswith(('UFUG_', 'R90_')):env.pop(k)
 if kind:env['UFUG_R91_POLICY']=kind
 if kind=='library':env['UFUG_R91_PROFILE']='1'
 t=time.perf_counter()
 p=subprocess.run([str(exe),str(inp),str(output)],env=env,text=True,capture_output=True,timeout=60)
 ms=(time.perf_counter()-t)*1000
 v=subprocess.run([str(H/'build/verify_exhaustive'),str(inp),str(output)],text=True,capture_output=True,timeout=60) if output.is_file() else None
 if p.returncode or v is None or v.returncode:raise RuntimeError(f'FAILED {inp} {tag} exe={p.returncode} verifier={v.stdout if v else "missing"} stderr={p.stderr[-300:]}')
 import re
 area=int(re.search(r'area=(\d+)',v.stdout).group(1));delay=int(re.search(r'delay=(\d+)',v.stdout).group(1))
 (output.with_suffix('.log')).write_text(p.stdout+'\n'+p.stderr)
 return dict(case=inp.name,config=tag,area=area,delay=delay,wall_ms=round(ms,3),net_sha=hashlib.sha256(output.read_bytes()).hexdigest())

def main():
 p=argparse.ArgumentParser();p.add_argument('--results',type=Path,required=True);p.add_argument('--quick',action='store_true');a=p.parse_args()
 out=a.results/'preflight';out.mkdir(parents=True,exist_ok=True)
 tests=sorted((H/'hard_bank/dev').glob('*.txt'))
 tests+= [H/'stress_v2/stress_001.txt',H/'stress_v2/stress_002.txt',H/'stress_v2/stress_003.txt',H/'holdouts/holdout_016.txt']
 if a.quick:tests=tests[:2]+tests[4:6]
 configs=[('frozen',None),('off','off'),('library','library'),('repeat_sop','repeat_sop'),('repeat_shannon','repeat_shannon')]
 rows=[]
 for f in tests:
  for label,mode in configs:
   row=run(f,label,mode,out/f'{f.stem}_{label}.net');rows.append(row)
  v=[x for x in rows if x['case']==f.name and x['config'] in ('frozen','off')]
  if len(v)!=2 or (v[0]['area'],v[0]['delay'],v[0]['net_sha'])!=(v[1]['area'],v[1]['delay'],v[1]['net_sha']):raise RuntimeError('R91 off must be bitwise frozen-identical '+f.name)
  print('EXACT',f.name,'5/5 PASS; frozen vs off identical',flush=True)
 with (out/'casewise.csv').open('w',newline='') as file:
  w=csv.DictWriter(file,fieldnames=rows[0].keys());w.writeheader();w.writerows(rows)
 print('R91_EXACT_GATE_PASS',len(rows),'full truth-table checks',flush=True)
if __name__=='__main__':main()

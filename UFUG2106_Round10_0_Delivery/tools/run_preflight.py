#!/usr/bin/env python3
"""Full Boolean equivalence for release and frozen controls on independent fixtures."""
from pathlib import Path
import os,subprocess,time,hashlib,csv,argparse,re,sys
H=Path(__file__).resolve().parents[1]

def env(kind):
    d=os.environ.copy()
    for k in list(d):
        if k.startswith(('UFUG_','R90_','R10_')):d.pop(k)
    if kind is not None:d['UFUG_R91_POLICY']=kind
    return d

def main():
    p=argparse.ArgumentParser();p.add_argument('--results',type=Path,required=True);p.add_argument('--quick',action='store_true');a=p.parse_args()
    out=a.results/'preflight';out.mkdir(parents=True,exist_ok=True)
    fs=sorted((H/'fixtures/dev').glob('*.txt'))+sorted((H/'fixtures/holdouts').glob('*.txt'))+sorted((H/'fixtures/stress_v2').glob('*.txt'))
    if a.quick:fs=fs[:2]+fs[4:5]+fs[-1:]
    configs=[('frozen_r90','synth_round90_frozen',None),('frozen_r91_sop','synth_round91_frozen','repeat_sop'),('r100_default','synth_round100',None),('r100_sop','synth_round100','repeat_sop'),('r100_off','synth_round100','off'),('submission_default','submission_synth',None)]
    rows=[]
    for f in fs:
        by={}
        for label,exe,mode in configs:
            net=out/f'{f.stem}_{label}.net'
            tic=time.perf_counter()
            z=subprocess.run([str(H/'build'/exe),str(f),str(net)],capture_output=True,text=True,env=env(mode),timeout=80)
            wall_ms=(time.perf_counter()-tic)*1000
            if z.returncode or not net.exists():
                raise RuntimeError(f'{f.name} {label} solver rc={z.returncode} {z.stderr[-400:]}')
            v=subprocess.run([str(H/'build/verify_exhaustive'),str(f),str(net)],capture_output=True,text=True,timeout=80)
            if v.returncode:raise RuntimeError(f'{f.name} {label} equivalence failure {v.stdout[-300:]} {v.stderr[-300:]}')
            area=int(re.search(r'area=(\d+)',v.stdout).group(1))
            delay=int(re.search(r'delay=(\d+)',v.stdout).group(1))
            row=dict(case=f.name,policy=label,area=area,delay=delay,wall_ms=round(wall_ms,3),net_sha256=hashlib.sha256(net.read_bytes()).hexdigest())
            rows.append(row);by[label]=row
            (out/f'{f.stem}_{label}.log').write_text(z.stdout+'\n'+z.stderr+'\n'+v.stdout)
        # No mode-dependent global state should affect truth-table semantics.
        # Different wall-clock search trajectories may cause different valid netlists.
        mismatches=[label for label in ('r100_default','r100_sop','submission_default') if (by[label]['area'],by[label]['delay'])!=(by['frozen_r91_sop']['area'],by['frozen_r91_sop']['delay'])]
        print('LOCAL_EXACT',f.name,'6/6 PASS', 'candidate_area_delay_differences='+','.join(mismatches) if mismatches else 'candidate_area_delay_equal',flush=True)
    with (out/'casewise.csv').open('w',newline='') as w:
        writer=csv.DictWriter(w,fieldnames=rows[0].keys());writer.writeheader();writer.writerows(rows)
    print('R100_LOCAL_GATE_PASS',len(rows),'exact equivalence checks',flush=True)
if __name__=='__main__':main()

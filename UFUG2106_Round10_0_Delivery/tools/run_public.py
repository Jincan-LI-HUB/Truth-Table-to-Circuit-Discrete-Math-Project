#!/usr/bin/env python3
"""Uses ONLY the genuine external course evaluator and original Stage1/Stage2 banks."""
import argparse,csv,hashlib,json,os,subprocess,shutil,tempfile
from pathlib import Path
H=Path(__file__).resolve().parents[1];ROOT=H.parent
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def clean_env(mode):
    d=os.environ.copy()
    for k in list(d):
        if k.startswith(('UFUG_','R90_','R10_')):d.pop(k)
    if mode is not None:d['UFUG_R91_POLICY']=mode
    return d

def main():
    p=argparse.ArgumentParser();p.add_argument('--results',type=Path,required=True);p.add_argument('--runs',type=int,default=2);p.add_argument('--quick',action='store_true');a=p.parse_args()
    ev=ROOT/'evaluator'
    if not ev.is_file():raise RuntimeError('Course evaluator missing: '+str(ev))
    cases=ROOT/'data'
    for stage in ('stage1','stage2'):
        if not (cases/stage).is_dir():raise RuntimeError('Public bank missing '+str(cases/stage))
    configs=[('r90_frozen','synth_round90_frozen',None),('r91_sop_explicit','synth_round91_frozen','repeat_sop'),('r100_default','synth_round100',None),('r100_sop_explicit','synth_round100','repeat_sop'),('r100_off','synth_round100','off'),('submission_default','submission_synth',None)]
    if a.quick:configs=[configs[i] for i in (0,1,2,5)]
    out=a.results/'official';out.mkdir(parents=True,exist_ok=True)
    state=dict(evaluator_sha256=sha(ev),public=True,hidden=False,policies=[x[0] for x in configs],records=[])
    with tempfile.TemporaryDirectory(prefix='r100_official_evaluator_') as tmp:
        executable=Path(tmp)/'evaluator';shutil.copy2(ev,executable);executable.chmod(executable.stat().st_mode|0o111)
        for run in range(1,a.runs+1):
            for stage in ('stage1','stage2'):
                for label,exe,mode in (configs if run%2 else list(reversed(configs))):
                    report=out/f'{stage}_run{run}_{label}.csv'
                    log=out/f'{stage}_run{run}_{label}.log'
                    z=subprocess.run([str(executable),str(H/'build'/exe),str((cases/stage).resolve()),'--report',str(report)],capture_output=True,text=True,errors='replace',env=clean_env(mode),timeout=240)
                    log.write_text(z.stdout+'\n'+z.stderr)
                    if not report.is_file():raise RuntimeError('No official report '+str(log))
                    with report.open(newline='') as f:rows=list(csv.DictReader(f))
                    if len(rows)!=25:raise RuntimeError('Expected 25 public cases '+str(report))
                    passed=sum(r.get('status')=='PASS' for r in rows)
                    met=sum(r.get('target_met')=='yes' for r in rows)
                    area=sum(int(r.get('area') or 0) for r in rows if r.get('status')=='PASS')
                    delay=sum(int(r.get('delay') or 0) for r in rows if r.get('status')=='PASS')
                    obj=dict(stage=stage,run=run,policy=label,passed=passed,target_met=met,area=area,delay=delay,exit_code=z.returncode,exe_sha256=sha(H/'build'/exe))
                    state['records'].append(obj);(out/'summary.json').write_text(json.dumps(state,indent=2)+'\n')
                    print('PUBLIC',stage,'run',run,label,f'{passed}/25',f'target={met}',f'area={area}',f'delay={delay}',flush=True)
                    if z.returncode or passed!=25 or met!=25:raise RuntimeError('Official gate FAILED '+str(obj))
    # Diagnostic only: wall-clock-driven trajectories can vary across identical builds.
    import collections
    table=collections.defaultdict(dict)
    for r in state['records']:table[(r['stage'],r['run'])][r['policy']]=r
    for (stage,run),d in sorted(table.items()):
        if 'r91_sop_explicit' in d and 'r100_default' in d:
            b=d['r91_sop_explicit'];c=d['r100_default']
            print('CANDIDATE_SUM_DELTA',stage,'run',run,'area',c['area']-b['area'],'delay',c['delay']-b['delay'],flush=True)
    print('R100_OFFICIAL_PUBLIC_PASS; grading hidden cases not tested',flush=True)
if __name__=='__main__':main()

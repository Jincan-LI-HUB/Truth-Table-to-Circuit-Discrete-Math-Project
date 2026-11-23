#!/usr/bin/env python3
"""Two structural probes (stage1 case020, stage2 case016).
Direct process timing is unbounded by instructor's evaluator and is NOT PASS evidence.
"""
from __future__ import annotations
import argparse,csv,hashlib,os,re,subprocess,sys,time
from pathlib import Path
HERE=Path(__file__).resolve().parents[1];ROOT=HERE.parent
sys.path.insert(0,str(HERE/'tests'))
from verify_netlist import run as verify

def main():
    p=argparse.ArgumentParser();p.add_argument('--runs',type=int,default=3)
    p.add_argument('--output',type=Path,default=HERE/'results'/'diagnostics')
    p.add_argument('--timeout',type=float,default=10)
    a=p.parse_args();a.output.mkdir(parents=True,exist_ok=True)
    variants=[('r71_guard',ROOT/'UFUG2106_Round7_1_Delivery/build/synth_round71',{}),
      ('r72_shortlist',HERE/'build/synth_round72',{'UFUG_R72_POLICY':'shortlist'}),
      ('r72_guard',HERE/'build/synth_round72',{'UFUG_R72_POLICY':'guard'}),
      ('r72_nocancel',HERE/'build/synth_round72',{'UFUG_R72_POLICY':'shortlist_nocancel'})]
    cases=[('stage1','case_020.txt'),('stage2','case_016.txt')]
    rec=[]
    for rep in range(1,a.runs+1):
        order=variants if rep%2 else variants[::-1]
        for st,c in cases:
            case=ROOT/'data'/st/c
            for name,exe,extra in order:
                base=f'run{rep}_{st}_{Path(c).stem}_{name}'
                output=a.output/(base+'.net')
                env=os.environ.copy()
                for k in ['UFUG_R72_POLICY','UFUG_R71_POLICY','UFUG_R71_TRACE',
                          'UFUG_ROUND5_PROFILE','UFUG_R7_LEGACY_MERGE','UFUG_R7_LEGACY_COVER']:
                    env.pop(k,None)
                env.update(extra);env['UFUG_R71_TRACE']='1';env['UFUG_ROUND5_PROFILE']='1'
                start=time.perf_counter()
                try:
                    proc=subprocess.run([str(exe),str(case),str(output)],env=env,capture_output=True,
                        text=True,errors='replace',timeout=a.timeout)
                    code=proc.returncode;log=proc.stdout+'\n'+proc.stderr
                except subprocess.TimeoutExpired as exc:
                    code=124;log=str(exc)
                elapsed=1000*(time.perf_counter()-start)
                (a.output/(base+'.profile.log')).write_text(log)
                v={'matched':False,'area':None,'delay':None,'exhaustive':None,'assignments':None}
                netsha=''
                if code==0 and output.is_file():
                    netsha=hashlib.sha256(output.read_bytes()).hexdigest()
                    try:v=verify(case,output)
                    except Exception as exc:(a.output/(base+'.verify_error.txt')).write_text(repr(exc))
                trace=re.findall(r'R72_TRACE[^\n]*',log)
                summary=re.findall(r'completed=\d+ chosen=-?\d+ area=\d+ delay=\d+',log)
                rec.append({'run':rep,'stage':st,'case':c,'variant':name,'exit_code':code,
                  'direct_ms':round(elapsed,3),'verified':v['matched'],'exhaustive':v['exhaustive'],
                  'area':v['area'],'delay':v['delay'],'net_sha256':netsha,
                  'completed_line':summary[-1] if summary else '',
                  'shortlist_status':next((t for t in trace if 'event=shortlist' in t),''),
                  'profile_log':base+'.profile.log','net':base+'.net'})
                print(f'DIAGNOSTIC {rep} {st}/{c} {name:16} '
                  f'exit={code} direct_ms={elapsed:.3f} area={v["area"]} delay={v["delay"]}',flush=True)
    with (a.output/'critical_case_diagnostics.csv').open('w',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f,fieldnames=list(rec[0]));w.writeheader();w.writerows(rec)
    (a.output/'MEASUREMENT_SCOPE.md').write_text('# Non-official profiling\n\n'
      'Direct process executions are NOT evaluated under the official runtime and memory limits. '
      'Log emission adds overhead. Official PASS statuses must come only from the instructor evaluator.\n'
      'For n<=13 the independent checker uses all input assignments.\n')
    return 0 if all(x['verified'] for x in rec) else 3
if __name__=='__main__':raise SystemExit(main())

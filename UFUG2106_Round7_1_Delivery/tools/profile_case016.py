#!/usr/bin/env python3
"""Candidate-level R7.1 diagnostic; NOT official time-limited evaluation."""
from __future__ import annotations
import argparse, csv, hashlib, os, re, subprocess, time, sys
from pathlib import Path
D=Path(__file__).resolve().parents[1]; ROOT=D.parent

def digest(p):
    h=hashlib.sha256()
    with open(p,'rb') as f:
        for chunk in iter(lambda:f.read(1<<20),b''):h.update(chunk)
    return h.hexdigest()

def main():
    p=argparse.ArgumentParser();p.add_argument('--runs',type=int,default=3)
    p.add_argument('--timeout',type=float,default=5.0)
    p.add_argument('--output',type=Path,default=D/'results'/'diagnostics')
    args=p.parse_args();folder=args.output.resolve();folder.mkdir(parents=True,exist_ok=True)
    case=ROOT/'data/stage2/case_016.txt'
    if not case.is_file():raise SystemExit(f'Missing {case}')
    items=[('r51',ROOT/'UFUG2106_Round5.1_Delivery/build/synth_round51',{}),
           ('r71_guard',D/'build/synth_round71',{}),
           ('r71_policy_off',D/'build/synth_round71',{'UFUG_R71_POLICY':'off'}),
           ('r71_legacy_merge',D/'build/synth_round71',{'UFUG_R7_LEGACY_MERGE':'1'}),
           ('r71_legacy_cover',D/'build/synth_round71',{'UFUG_R7_LEGACY_COVER':'1'})]
    records=[]
    verifier=ROOT/'UFUG2106_Round5.1_Delivery/tools/verify_netlist.py'
    for r in range(1,args.runs+1):
        seq=items if r%2 else list(reversed(items))
        for name,exe,extra in seq:
            if not exe.is_file():raise RuntimeError('Missing '+str(exe))
            net=folder/f'run{r}_{name}.net'
            env=os.environ.copy()
            for key in ('UFUG_R71_POLICY','UFUG_R71_TRACE','UFUG_R7_LEGACY_MERGE','UFUG_R7_LEGACY_COVER','UFUG_ROUND5_PROFILE'):
                env.pop(key,None)
            env.update(extra);env['UFUG_R71_TRACE']='1';env['UFUG_ROUND5_PROFILE']='1'
            started=time.perf_counter()
            try:
                cmd=subprocess.run([str(exe),str(case),str(net)],env=env,capture_output=True,text=True,timeout=args.timeout,errors='replace')
                code=cmd.returncode;log=cmd.stdout+'\n'+cmd.stderr
            except subprocess.TimeoutExpired as ex:
                code=124
                log=f'DIAGNOSTIC_TIMEOUT: {args.timeout}s\n'+(ex.stderr.decode(errors='replace') if isinstance(ex.stderr,bytes) else (ex.stderr or ''))
            elapsed=(time.perf_counter()-started)*1000
            (folder/f'run{r}_{name}.profile.log').write_text(log,encoding='utf-8')
            success='NOT_RUN';net_sha=''
            if code==0 and net.exists():
                net_sha=digest(net)
                if verifier.is_file():
                    chk=subprocess.run([sys.executable,str(verifier),str(case),str(net)],capture_output=True,text=True,timeout=30)
                    (folder/f'run{r}_{name}.verify.log').write_text(chk.stdout+chk.stderr,encoding='utf-8')
                    success='PASS' if chk.returncode==0 and "'matched': True" in chk.stdout else 'CHECK_LOG'
            trial=re.findall(r'R5_STAGE stage=trial_total[^\n]*',log)
            status=re.findall(r'completed=\d+ chosen=\d+ area=\d+ delay=\d+',log)
            trace=re.findall(r'R71_TRACE[^\n]*',log)
            records.append({'run':r,'variant':name,'elapsed_direct_ms':round(elapsed,3),
               'exit_code':code,'independent_verify':success,'net_sha256':net_sha,
               'primary_trial_count':len(trial),'status_line':status[-1] if status else '',
               'legacy_skipped':any('event=legacy_skipped' in x for x in trace),
               'legacy_candidate_count':sum('event=legacy ' in x for x in trace),
               'trace_log':f'run{r}_{name}.profile.log'})
            print(f'diagnostic {r} {name:19s} {elapsed:8.3f}ms {status[-1] if status else "not_completed"}',flush=True)
    with (folder/'case016_diagnostics.csv').open('w',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f,fieldnames=records[0].keys());w.writeheader();w.writerows(records)
    (folder/'DIAGNOSTIC_LIMITATION.md').write_text('# Non-official direct run\n\n'
      'No evaluator 100 ms deadline applies here. Profiling changes runtime; no direct elapsed_ms should be compared as official PASS.\n',encoding='utf-8')
    return 0 if all(v['independent_verify']=='PASS' for v in records) else 3
if __name__=='__main__':raise SystemExit(main())

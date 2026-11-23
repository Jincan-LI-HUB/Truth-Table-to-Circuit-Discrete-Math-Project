#!/usr/bin/env python3
"""Diagnose the 100ms case with profiled direct (non-official) runs.

Each execution is deliberately allowed >100ms to reveal candidate completion.
These measurements are NOT substitutes for official evaluator results.
"""
from __future__ import annotations
import argparse,csv,datetime as dt,hashlib,os,re,subprocess,time
from pathlib import Path

DELIVERY=Path(__file__).resolve().parents[1]
ROOT=DELIVERY.parent

VARIANTS=[('round51',None,{}),('r7_default',True,{}),
  ('r7_legacy_merge',True,{'UFUG_R7_LEGACY_MERGE':'1'}),
  ('r7_legacy_cover',True,{'UFUG_R7_LEGACY_COVER':'1'}),
  ('r7_legacy_both',True,{'UFUG_R7_LEGACY_MERGE':'1','UFUG_R7_LEGACY_COVER':'1'})]

def main():
    arg=argparse.ArgumentParser()
    arg.add_argument('--runs',type=int,default=3)
    arg.add_argument('--timeout',type=float,default=5)
    arg.add_argument('--case',type=Path,default=ROOT/'data/stage2/case_016.txt')
    opt=arg.parse_args()
    old=ROOT/'UFUG2106_Round5.1_Delivery/build/synth_round51'
    r7=DELIVERY/'build/synth_round7'
    verify=ROOT/'UFUG2106_Round5.1_Delivery/tools/verify_netlist.py'
    folder=DELIVERY/'results'/'diagnostics'/dt.datetime.now().strftime('%Y%m%d_%H%M%S')
    folder.mkdir(parents=True,exist_ok=False)
    records=[]
    for i in range(1,opt.runs+1):
        methods=VARIANTS if i%2 else list(reversed(VARIANTS))
        for name,r7_mode,extra in methods:
            prog=r7 if r7_mode else old
            if not prog.is_file():raise SystemExit(f'Missing executable: {prog}')
            outfile=folder/f'run{i}_{name}.net'
            env=os.environ.copy();env['UFUG_ROUND5_PROFILE']='1'
            for key in ('UFUG_R7_LEGACY_MERGE','UFUG_R7_LEGACY_COVER'):env.pop(key,None)
            env.update(extra)
            started=time.perf_counter()
            try:
                proc=subprocess.run([str(prog),str(opt.case),str(outfile)],env=env,
                  capture_output=True,text=True,timeout=opt.timeout)
                exit_code=proc.returncode;std=proc.stderr
            except subprocess.TimeoutExpired as e:
                exit_code=124;std=(e.stderr or b'').decode(errors='replace') if isinstance(e.stderr,bytes) else (e.stderr or '')
            elapsed=1000*(time.perf_counter()-started)
            log=folder/f'run{i}_{name}.profile.log';log.write_text(std,encoding='utf-8')
            last=(re.findall(r'completed=\d+[^\n]*',std) or [''])[-1]
            covers=(re.findall(r'R7_STAGE stage=covers[^\n]*',std) or [''])[-1]
            mapping=(re.findall(r'R5_STAGE stage=mapping[^\n]*',std) or [''])[-1]
            selected=(re.findall(r'R5_STAGE stage=trial_total[^\n]*',std) or [])
            verified='NOT_RUN'
            if exit_code==0 and outfile.exists() and verify.exists():
                val=subprocess.run(['python3',str(verify),str(opt.case),str(outfile)],capture_output=True,text=True,timeout=30)
                (folder/f'run{i}_{name}.verify.log').write_text(val.stdout+'\n'+val.stderr)
                verified='PASS' if val.returncode==0 and "'matched': True" in val.stdout else 'CHECK_LOG'
            records.append({'run':i,'variant':name,'exit_code':exit_code,'direct_elapsed_ms':round(elapsed,3),
              'verified':verified,'finished':bool(last),'last_status_line':last,
              'cover_profile':covers,'mapping_profile':mapping,'trial_count':len(selected),'profile_log':log.name})
            print(f'{i} {name:20} exit={exit_code:3} elapsed={elapsed:8.3f} ms  verified={verified}  {last}')
    path=folder/'case016_profile_comparison.csv'
    with path.open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=records[0].keys());w.writeheader();w.writerows(records)
    print('Saved:',folder)
    print('IMPORTANT: direct profiling does NOT apply the official 100ms limit and includes logging overhead.')

if __name__=='__main__':main()

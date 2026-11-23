#!/usr/bin/env python3
"""Run actual evaluator on an isolated single-case folder or file.

Unlike Round 8.2.1's original harness, the evaluator input directory contains
EXACTLY one .txt case, with no netlists, diagnostics or CSV reports inside.
Every attempt's stdout/stderr, return code and report are retained.  A failed
folder-mode attempt optionally triggers the separately documented single-file
mode.  Neither case can be declared PASS without an actual evaluator PASS row.
"""
import argparse
import csv
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import time

PATCH_ROOT = Path(__file__).resolve().parents[1]
ORIGINAL = PATCH_ROOT.parent / 'UFUG2106_Round8_2_1_Delivery'
PROJECT = PATCH_ROOT.parent
KINDS = ('wire','xor2','multi','and_all')

def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def attempt(evaluator, program, input_path, report, log, mode, timeout):
    if report.exists():
        report.unlink()
    cmd = [str(evaluator),str(program),str(input_path),'--report',str(report)]
    started=time.monotonic()
    try:
        p=subprocess.run(cmd,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,
                         text=True,errors='replace',timeout=timeout)
        rc=p.returncode
        output=p.stdout
    except subprocess.TimeoutExpired as exc:
        rc=124
        output=f'EVALUATOR_TIMEOUT mode={mode} timeout={timeout} seconds\n'
        if exc.stdout:
            output+=exc.stdout.decode('utf8','replace') if isinstance(exc.stdout,bytes) else exc.stdout
    log.write_text('COMMAND: '+repr(cmd)+'\nEXIT: '+str(rc)+'\nELAPSED_S: '+str(round(time.monotonic()-started,3))+'\n\n'+output,encoding='utf8')
    rows=[]
    if report.is_file():
        try:
            with report.open(newline='',encoding='utf8') as f:
                rows=list(csv.DictReader(f))
        except Exception as exc:
            output+='\nREPORT_PARSE_ERROR: '+repr(exc)
    passed=rc==0 and len(rows)==1 and rows[0].get('status')=='PASS' and rows[0].get('target_met')=='yes'
    return {'mode':mode,'returncode':rc,'report_exists':report.is_file(),
            'rows':rows,'passed':passed,'log':str(log),'report':str(report),
            'tail':output[-1200:]}

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--results',type=Path,required=True)
    ap.add_argument('--quick',action='store_true')
    ap.add_argument('--single-file-only',action='store_true')
    ap.add_argument('--no-fallback',action='store_true')
    ap.add_argument('--evaluator',type=Path,help='Use only for isolated wrapper self-tests; normal runner uses the real evaluator')
    ap.add_argument('--program',type=Path)
    ap.add_argument('--n',type=int,default=20,help='Default 20. Smaller n is for wrapper self-test only')
    ap.add_argument('--timeout',type=int,default=360)
    args=ap.parse_args()
    out=args.results.resolve()/'resource_official_probe'
    out.mkdir(parents=True,exist_ok=True)
    evaluator=(args.evaluator or PROJECT/'evaluator').resolve()
    program=(args.program or ORIGINAL/'build/synth_round821').resolve()
    generate=ORIGINAL/'tests/generate_resource_cases.py'
    records=[]
    summary=out/'official_resource_summary.json'
    for obj in (evaluator,program,generate):
        if not obj.is_file():
            raise FileNotFoundError(f'Missing required file: {obj}')
    if args.n != 20:
        print('WRAPPER_SELFTEST: n differs from official 20-input reproduction',flush=True)
    for kind in (KINDS[:1] if args.quick else KINDS):
        dest=out/kind
        dest.mkdir(exist_ok=True)
        case=dest/'case_001.txt'
        target=40 if kind=='parity_all' else 10
        gen=subprocess.run([sys.executable,str(generate),str(case),
                            '--n',str(args.n),'--kind',kind,'--ram','9000',
                            '--limit','0','--target',str(target)],
                           capture_output=True,text=True,timeout=120)
        (dest/'generate.log').write_text(gen.stdout+'\n'+gen.stderr,encoding='utf8')
        if gen.returncode:
            raise RuntimeError(f'Cannot generate {kind}: {gen.stderr}')
        record={'case':kind,'ram_limit_kib':9000,'input_sha256':sha256(case),
                'evaluator_sha256':sha256(evaluator),'program_sha256':sha256(program),
                'attempts':[],'official_pass':False}
        records.append(record)
        # Exclude output netlists, reports and logs from the evaluator's input.
        with tempfile.TemporaryDirectory(prefix='r821_isolated_') as tmp:
            isolated=Path(tmp)/'input'
            isolated.mkdir()
            copied=isolated/'case_001.txt'
            shutil.copyfile(case,copied)
            assert sha256(copied)==record['input_sha256']
            assert sorted(p.name for p in isolated.iterdir())==['case_001.txt']
            record['isolated_file_count']=1
            modes=['single'] if args.single_file_only else ['folder']
            if not args.single_file_only and not args.no_fallback:
                modes+=['single']
            for mode in modes:
                source=copied if mode=='single' else isolated
                result=attempt(evaluator,program,source,
                               dest/f'official_{mode}.csv',dest/f'official_{mode}.log',
                               mode,args.timeout)
                record['attempts'].append(result)
                if result['passed']:
                    record['official_pass']=True
                    record['successful_mode']=mode
                    break
        summary.write_text(json.dumps({'results':records},indent=2,ensure_ascii=False)+'\n',encoding='utf8')
        state='PASS' if record['official_pass'] else 'FAIL'
        print(f'RESOURCE_OFFICIAL {kind}: {state}; modes='+','.join(
            x['mode']+':'+str(x['returncode'])+'/'+str(x['passed']) for x in record['attempts']),flush=True)
        if not record['official_pass']:
            for result in record['attempts']:
                print(f'--- {result["mode"]} evaluator log tail ---\n{result["tail"][-1200:]}',flush=True)
            raise RuntimeError(f'Official resource evaluator failed for {kind}; original logs preserved: {dest}')
    print(f'RESOURCE_OFFICIAL_GATE: PASS ({len(records)}/{len(records)}); default_evaluator={args.evaluator is None}',flush=True)
    return 0

if __name__=='__main__':
    try:raise SystemExit(main())
    except Exception as exc:
        print('RESOURCE_OFFICIAL_DIAGNOSTIC:',repr(exc),file=sys.stderr,flush=True)
        raise

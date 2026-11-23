#!/usr/bin/env python3
"""Diagnostic attribution matrix, not a grader or proof of solver RAM compliance.
Runs tiny C and frozen R8.2.1 executable under the actual course evaluator.
"""
import argparse,csv,hashlib,json,os,platform,subprocess,sys,tempfile,time,zipfile
from pathlib import Path

HERE=Path(__file__).resolve().parents[1]
ROOT=HERE.parent
OUT=HERE/'results'
LOG=HERE/'logs'

def cmd(argv,path,timeout=360,env=None):
    st=time.monotonic()
    try:
        p=subprocess.run([str(x) for x in argv],capture_output=True,text=True,errors='replace',timeout=timeout,env=env)
        text=(p.stdout or '')+("\n[stderr]\n"+p.stderr if p.stderr else '')
        code=p.returncode
    except subprocess.TimeoutExpired as e:
        text=f'TIMEOUT after {timeout}s\n'+str(e)
        code=124
    path.write_text(text,encoding='utf-8')
    return dict(exit_code=code,wall_s=round(time.monotonic()-st,4),log=str(path.relative_to(HERE)))

def wire_case(p,n,ram):
    # Last physical input x_(n-1) alternates 0, 1 in row-order.
    p.parent.mkdir(parents=True,exist_ok=True)
    with p.open('w',encoding='ascii') as f:
        f.write(f'{n}\n1\n')
        block='0 1 '*8192
        pairs=(1<<n)//2
        while pairs>=8192:
            f.write(block)
            pairs-=8192
        f.write('0 1 '*pairs)
        f.write('\n1 1\n1 1\n1 1\n10\n0\n'+str(ram)+'\n')

def readcsv(p):
    if not p.is_file():return None
    with p.open(newline='') as f:return list(csv.DictReader(f))

def sha(p):
    h=hashlib.sha256()
    with p.open('rb') as f:
        for b in iter(lambda:f.read(1<<20),b''):h.update(b)
    return h.hexdigest()

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--quick',action='store_true',help='six core controls; full is 14 comparisons')
    a=ap.parse_args()
    stamp=time.strftime('%Y%m%d_%H%M%S')
    run=OUT/('memory_attribution_'+stamp)
    run.mkdir(parents=True,exist_ok=True)
    diag=run/'cases';diag.mkdir()
    evaluator=ROOT/'evaluator'
    solver=ROOT/'UFUG2106_Round8_2_1_Delivery/build/synth_round821'
    tiny=HERE/'build/tiny_wire'
    runner=HERE/'build/lightweight_mem_runner'
    if not evaluator.is_file():raise RuntimeError('Missing genuine '+str(evaluator))
    if not solver.is_file():raise RuntimeError('Missing patched synthesizer '+str(solver))
    for k in (tiny,runner):
        if not k.is_file():raise RuntimeError('Missing compiled diagnostic: '+str(k))
    summary={"purpose":"measure attribution of official MEMORY_LIMIT, NOT official release gate",
        "platform":platform.platform(),"evaluator_sha256":sha(evaluator),
        "solver_sha256":sha(solver),"tiny_sha256":sha(tiny),
        "records":[],"experimental_note":"tiny_wire is correct ONLY for f=x_last fixtures; it is NOT a project solver"}
    (run/'summary.json').write_text(json.dumps(summary,indent=2))
    cases=[
      (20,0,'patched','file'), (20,0,'tiny','file'),
      (20,9000,'patched','file'), (20,9000,'tiny','file'),
      (12,9000,'patched','file'), (12,9000,'tiny','file'),
    ]
    if not a.quick:
      cases += [
        (20,9000,'patched','folder'),(20,9000,'tiny','folder'),
        (20,16000,'patched','file'),(20,16000,'tiny','file'),
        (20,32768,'patched','file'),(20,32768,'tiny','file'),
        (20,65536,'patched','file'),(20,65536,'tiny','file'),
      ]
    input_cache={}
    for idx,(n,ram,variant,mode) in enumerate(cases,1):
        name=f'{idx:02d}_n{n}_ram{ram}_{variant}_{mode}'
        folder=diag/name;folder.mkdir()
        case_folder=folder/'input_only';case_folder.mkdir()
        case=case_folder/'case_001.txt'
        wire_case(case,n,ram)
        exe=solver if variant=='patched' else tiny
        data={'id':name,'n':n,'ram_limit_kib':ram,'variant':variant,'mode':mode,
              'input_sha256':sha(case)}
        net=folder/'direct.netlist'
        data['direct']=cmd([runner,exe,case,net],folder/'direct.log',timeout=60)
        data['direct_netlist']=net.read_text().strip() if net.exists() else None
        if variant=='tiny':
            environment=os.environ.copy();environment['R821_MEMORY_PROBE_LOG']=str(folder/'tiny_self_memory.txt')
        else:environment=os.environ.copy()
        report=folder/'official.csv'
        input_arg=case if mode=='file' else case_folder
        data['official']=cmd([evaluator,exe,input_arg,'--report',report],folder/'official.log',timeout=360,env=environment)
        rows=readcsv(report)
        data['official_report']=rows
        data['reported_memory_limit']=None
        # Raw stdout/stderr and report are authoritative; never infer PASS from an exit code alone.
        raw=(folder/'official.log').read_text()
        if 'reason=MEMORY_LIMIT' in raw:data['reported_memory_limit']=True
        status=rows[0].get('status') if rows and len(rows)==1 else 'NO_SINGLE_ROW'
        data['status']=status
        summary['records'].append(data)
        (run/'summary.json').write_text(json.dumps(summary,indent=2)+'\n')
        print(f'[{idx}/{len(cases)}] n={n} cap={ram:6d} {variant:7} {mode:6} official={status:12} memory_limit={data["reported_memory_limit"]} exit={data["official"]["exit_code"]}',flush=True)
    print('\nPROBE_COMPLETE: diagnostics only; no release PASS is claimed.')
    return 0

if __name__=='__main__':
    try:raise SystemExit(main())
    except Exception as e:
        print('MEMORY_ATTRIBUTION_PROBE_ERROR:',repr(e),file=sys.stderr,flush=True)
        raise

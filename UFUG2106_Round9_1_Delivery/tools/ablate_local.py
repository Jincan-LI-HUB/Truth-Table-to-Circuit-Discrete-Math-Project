#!/usr/bin/env python3
"""Candidate vs exact frozen R9.0; does not claim official grading."""
import csv,hashlib,os,subprocess,time,argparse,sys
from pathlib import Path
P=Path(__file__).resolve().parents[1]

def env91(mode):
    d=os.environ.copy()
    for k in list(d):
        if k.startswith(('UFUG_','R90_')):d.pop(k)
    d['UFUG_R91_POLICY']=mode
    d['UFUG_R91_PROFILE']='1'
    return d

def run(inp,tag,kind,out):
    exe=P/'build/synth_round91'
    net=out/f'{inp.stem}_{tag}.net'
    t=time.perf_counter()
    proc=subprocess.run([str(exe),str(inp),str(net)],env=env91(kind),capture_output=True,text=True,timeout=90)
    sec=(time.perf_counter()-t)*1000
    verify=subprocess.run([str(P/'build/verify_exhaustive'),str(inp),str(net)],capture_output=True,text=True,timeout=30) if net.exists() else None
    if proc.returncode or verify is None or verify.returncode:
        raise RuntimeError(f'INVALID {inp} {tag}: exe={proc.returncode} verify={verify.stdout if verify else "missing"} stderr={proc.stderr[-2000:]}')
    metric=verify.stdout.strip()
    import re
    area=int(re.search(r'area=(\d+)',metric).group(1));delay=int(re.search(r'delay=(\d+)',metric).group(1))
    (out/f'{inp.stem}_{tag}.log').write_text(proc.stdout+'\n'+proc.stderr)
    row=dict(case=inp.name,bank=out.name,tag=tag,wall_ms=round(sec,3),area=area,delay=delay,net_sha256=hashlib.sha256(net.read_bytes()).hexdigest(),exact=True)
    for k in ['visited','cuts','matching','recipes','local','rejected','wall_hit','ms','accepted','before','after']:
        m=re.search(r'\b'+k+r'=(\S+)',proc.stderr);row['lib_'+k]=m.group(1) if m else ''
    return row

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--bank',choices=['dev','stage2','holdout','lockbox'],default='dev');ap.add_argument('--num',type=int,default=0);ap.add_argument('--start',type=int,default=1);args=ap.parse_args()
    if args.bank=='dev':cases=sorted((P/'hard_bank/dev').glob('*.txt'))
    elif args.bank=='lockbox':cases=sorted((P/'hard_bank/lockbox').glob('*.txt'))
    elif args.bank=='holdout':cases=sorted((P/'holdouts').glob('*.txt'))
    else:cases=sorted(Path('/mnt/data/r85_workspace/datasets/stage2').glob('*.txt'))
    if args.num:cases=cases[:args.num]
    out=P/'evidence'/f'ablation_{args.bank}';out.mkdir(parents=True,exist_ok=True)
    previous=out/'casewise.csv'
    rows=list(csv.DictReader(previous.open())) if previous.exists() and args.start>1 else []
    for i,inp in enumerate(cases,1):
        if i<args.start:continue
        for tag,mode in [('frozen','off'),('library','library'),('repeat_sop','repeat_sop'),('repeat_shannon','repeat_shannon')]:
            row=run(inp,tag,mode,out);rows.append(row)
            print('ABLATE',args.bank,inp.name,tag,row['area'],row['delay'],row['wall_ms'],'accepted',row['lib_accepted'],'local',row['lib_local'],flush=True)
        with (out/'casewise.csv').open('w',newline='') as f:
            w=csv.DictWriter(f,fieldnames=rows[0].keys());w.writeheader();w.writerows(rows)
    print('ABLATION_DONE',args.bank,len(rows),flush=True)
if __name__=='__main__':main()

#!/usr/bin/env python3
"""Independent local smoke/equivalence check for preserved solvers.
Not the course evaluator and not representative of official 50-case performance.
"""
from __future__ import annotations
import csv,os,pathlib,subprocess,sys,time,itertools,hashlib
ROOT=pathlib.Path(__file__).resolve().parent
SOLVERS={'zeyun_stage1': ROOT/'zeyun_synth','r100_frozen':ROOT/'r100_synth'}

def fixture(n,m,fn,prices=(2,2,8,3,1,1),target=20,limit=2000,ram=0):
    bits=[''.join(str(int(x)) for x in fn(tuple((row>>(n-1-i))&1 for i in range(n)))) for row in range(1<<n)]
    assert all(len(x)==m for x in bits)
    return f'{n}\n{m}\n'+ ' '.join(bits) +'\n' + '\n'.join(f'{prices[j]} {prices[j+1]}' for j in range(0,6,2))+ f'\n{target}\n{limit}\n{ram}\n',bits

def evaluate_netlist(net,n,m,truth,prices):
    lines=[l.strip().split() for l in net.splitlines() if l.strip()]
    if not lines:return (False,'empty',None,None)
    gate_types={'AND2','OR2','NOT'};gates=[]
    for i,row in enumerate(lines[:-1]):
        idx=n+1+i
        if len(row)<3 or int(row[0])!=idx or row[1] not in gate_types:return (False,'bad_gate',None,None)
        typ=row[1];expected=3 if typ=='NOT' else 4
        if len(row)!=expected:return (False,'bad_arity',None,None)
        ins=list(map(int,row[2:]));
        if any(v<0 or v>=idx for v in ins):return (False,'bad_dependency',None,None)
        gates.append((typ,ins))
    if len(lines[-1])!=m:return (False,'bad_outputs',None,None)
    outs=list(map(int,lines[-1]));
    if any(o<0 or o>n+len(gates) for o in outs):return (False,'bad_output_id',None,None)
    area={'AND2':prices[0],'OR2':prices[2],'NOT':prices[4]}
    delay={'AND2':prices[1],'OR2':prices[3],'NOT':prices[5]}
    a=sum(area[t] for t,_ in gates)
    t=[0]*(n+1)
    for typ,ins in gates: t.append(max(t[x] for x in ins)+delay[typ])
    d=max(t[x] for x in outs)
    for row in range(1<<n):
        values=[0]+[(row>>(n-1-i))&1 for i in range(n)]
        for typ,ins in gates:
            x=values[ins[0]]
            values.append(1-x if typ=='NOT' else (x&values[ins[1]] if typ=='AND2' else x|values[ins[1]]))
        actual=''.join(str(values[o]) for o in outs)
        if actual!=truth[row]:return (False, 'truth_row_'+str(row),a,d)
    return (True,'verified_exhaustive',a,d)

def mkcases():
    return {
        'course_example':fixture(3,2,lambda x:(x[0]|x[1],(x[0]|x[1])&x[2]),target=5),
        'xor4':fixture(4,1,lambda x:(sum(x)%2,),prices=(1,3,2,2,1,1),target=40),
        'multi_share':fixture(5,3,lambda x:(x[0]&(x[1]|x[2]),(x[0]&(x[1]|x[2]))|x[4],int((sum(x)>2))),target=35),
        'truth_dense':fixture(6,2,lambda x:(int((sum(x)%3)==1),int((x[0]^x[1]) and (x[2] or x[5]))),prices=(2,2,3,3,1,1),target=60),
        'constant_literal':fixture(4,3,lambda x:(0,1,1-x[2]),target=20),
    }

def main():
    outdir=ROOT/'smoke_outputs';outdir.mkdir(exist_ok=True)
    rows=[]
    for name,(raw,truth) in mkcases().items():
        n=int(raw.splitlines()[0]);m=int(raw.splitlines()[1]); p=list(map(int,raw.splitlines()[3].split()+raw.splitlines()[4].split()+raw.splitlines()[5].split()))
        for limit in [100,2000]:
            t=raw.splitlines();t[-2]=str(limit);raw_run='\n'.join(t)+'\n'
            inp=outdir/f'{name}_{limit}.txt';inp.write_text(raw_run)
            for sol_name,exe in SOLVERS.items():
                output=outdir/f'{name}_{limit}_{sol_name}.output.txt'
                started=time.perf_counter()
                proc=subprocess.run([str(exe),str(inp),str(output)],capture_output=True,text=True,timeout=20)
                duration_ms=(time.perf_counter()-started)*1000
                if proc.returncode==0 and output.exists():
                    passed,reason,area,delay=evaluate_netlist(output.read_text(),n,m,truth,p)
                else:passed,reason,area,delay=False,'process_exit_'+str(proc.returncode),None,None
                rows.append({'case':name,'limit_ms':limit,'method':sol_name,'exit_code':proc.returncode,'exhaustive_correct':passed,'detail':reason,'area':area,'delay':delay,'measured_process_ms':round(duration_ms,3),'output_sha256':hashlib.sha256(output.read_bytes()).hexdigest() if output.exists() else '', 'stderr_tail':proc.stderr[-250:]})
                print(name,limit,sol_name,passed,area,delay,round(duration_ms,2),proc.returncode)
    with (ROOT/'SOURCE_SMOKE_RESULTS.csv').open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=rows[0].keys());w.writeheader();w.writerows(rows)
    assert all(x['exhaustive_correct'] for x in rows),'smoke mismatch'
if __name__=='__main__':main()

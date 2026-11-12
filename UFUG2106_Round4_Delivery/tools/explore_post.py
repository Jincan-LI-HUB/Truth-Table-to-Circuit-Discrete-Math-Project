#!/usr/bin/env python3
import subprocess,csv, pathlib, time
root=pathlib.Path(__file__).resolve().parents[1]
cases=pathlib.Path('/mnt/data/ufug2106_new/Final Project/stage1')
base=pathlib.Path('/mnt/data/UFUG2106_Round3_Delivery/verification_outputs_final')
results=root/'results';generated=root/'verification_outputs';results.mkdir(exist_ok=True);generated.mkdir(exist_ok=True)
pol=root/'polarity_cli';alg=root/'algebraic_cli'
def meta(file):
 tokens=file.read_text().split(); n=int(tokens[0]);m=int(tokens[1]); start=2+(1<<n)
 return n,m,list(map(int,tokens[start:start+7]))

def metric(file,n,m,vals):
 aa,da,ao,dor,an,dn,target=vals
 arr=[0]*(n+1);area=0
 with file.open() as f:
  for line in f:
   z=line.split()
   if not z:continue
   if len(z)>1 and z[1] in {'NOT','OR2','AND2'}:
    op=z[1];u=int(z[2]);v=int(z[3]) if len(z)==4 else u
    if op=='NOT':area+=an;arr.append(arr[u]+dn)
    elif op=='AND2':area+=aa;arr.append(max(arr[u],arr[v])+da)
    else:area+=ao;arr.append(max(arr[u],arr[v])+dor)
   else:return area,max(arr[int(q)] for q in z)
 raise ValueError(file)

def apply(kind,case,source,dest,mode=None):
 exe=pol if kind=='phase' else alg
 args=[str(exe),str(case),str(source),str(dest)]
 if mode is not None:args.append(str(mode))
 p=subprocess.run(args,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True,timeout=80)
 if p.returncode:raise ValueError((args,p.stderr))
rows=[]
for i in range(1,26):
 label=f'case_{i:03}';case=cases/(label+'.txt');source=base/(label+'.output.txt');n,m,vals=meta(case)
 paths={"original":source}
 for label2,chain in {
  'algebra': [('alg',2)],'phase':[('phase',6)],
  'algebra_phase':[('alg',2),('phase',6)],
  'phase_algebra':[('phase',6),('alg',2)],
 }.items():
  prev=source
  for j,(what,mode) in enumerate(chain):
   dest=generated/(label+'_'+label2+'_'+str(j)+'.output.txt')
   apply('phase' if what=='phase' else 'alg',case,prev,dest,mode)
   prev=dest
  paths[label2]=prev
  
 metrics={k:metric(v,n,m,vals) for k,v in paths.items()}
 eligible={k:(a,d) for k,(a,d) in metrics.items() if d<=vals[-1]}
 winner=min(eligible.items(),key=lambda kv:(kv[1][0],kv[1][1]))
 rows.append(dict(case=label+'.txt',original_area=metrics['original'][0],original_delay=metrics['original'][1],best_area=winner[1][0],best_delay=winner[1][1],method=winner[0],algebra_area=metrics['algebra'][0],phase_area=metrics['phase'][0],phase_algebra_area=metrics['phase_algebra'][0],algebra_phase_area=metrics['algebra_phase'][0]))
 if winner[0]!='original':
  import shutil
  shutil.copyfile(paths[winner[0]], generated/(label+'.output.txt'))
 print(i,metrics,'WINNER',winner,flush=True)
with (results/'postprocess_comparison.csv').open('w',newline='') as f:
 w=csv.DictWriter(f,fieldnames=rows[0].keys());w.writeheader();w.writerows(rows)
print('AREA',sum(r['original_area'] for r in rows),sum(r['best_area'] for r in rows),'TOTAL IMPROVEMENT',sum(r['original_area']-r['best_area'] for r in rows),flush=True)

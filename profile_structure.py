import subprocess,time,csv,statistics,argparse
from pathlib import Path
parser=argparse.ArgumentParser(description="Profile structural sharing in an existing synthesizer's complete netlists (NOT the official evaluator)")
parser.add_argument('--cases',type=Path,required=True,help='Directory with case_*.txt truth tables')
parser.add_argument('--program',type=Path,required=True,help='Compiled synthesizer (e.g. Round 7.2)')
parser.add_argument('--output',type=Path,required=True,help='Directory for netlists and structural_baseline.csv')
parser.add_argument('--timeout',type=float,default=60,help='Timeout per direct invocation in seconds')
parser.add_argument('--official-csv',type=Path,default=None,help='Optional official per-case CSV for area/delay validation')
args=parser.parse_args();B=args.cases.resolve();EX=args.program.resolve();O=args.output.resolve();O.mkdir(parents=True,exist_ok=True)
records=[]
for p in sorted(B.glob('case_*.txt')):
 tkn=p.read_text().split();n,m=map(int,tkn[:2]);N=1<<n;aa,da,ao,doo,an,dn,tar,limit=map(int,tkn[2+N:2+N+8]);t=time.monotonic();op=O/p.name
 try:
  r=subprocess.run([str(EX),str(p),str(op)],capture_output=True,text=True,timeout=args.timeout)
  if r.returncode:raise RuntimeError(r.stderr[-120:])
  runtime=(time.monotonic()-t)*1000
  lines=op.read_text().strip().splitlines();gs=[x.split() for x in lines[:-1]];roots=list(map(int,lines[-1].split()));G=len(gs)
  ref=[0]*(n+G+1)
  for g in gs:
   for x in g[2:]:ref[int(x)]+=1
  for x in roots:ref[x]+=1
  mask=[0]*(n+G+1)
  for j,rt in enumerate(roots):mask[rt]|=(1<<j)
  for g in reversed(gs):
   z=mask[int(g[0])]
   if z:
    for x in g[2:]:mask[int(x)]|=z
  ops={s:sum(g[1]==s for g in gs) for s in ('AND2','OR2','NOT')}
  shared=sum(mask[i].bit_count()>1 for i in range(n+1,n+G+1))
  area=ops['AND2']*aa+ops['OR2']*ao+ops['NOT']*an
  arr=[0]*(n+1)
  for g in gs:arr.append(max(arr[int(x)] for x in g[2:])+{'AND2':da,'OR2':doo,'NOT':dn}[g[1]])
  delay=max(arr[x] for x in roots)
  records.append(dict(case=p.stem,n=n,m=m,area=area,delay=delay,runtime_local_ms=round(runtime,2),gates=G,shared_gates=shared,shared_pct=round(100*shared/max(1,G),1),multi_fanout_gates=sum(ref[i]>1 for i in range(n+1,n+G+1)),AND2=ops['AND2'],OR2=ops['OR2'],NOT=ops['NOT']))
  print(p.stem,'gates',G,'shared',shared,'local_ms',round(runtime),flush=True)
 except Exception as e:print(p.name,'ERROR',str(e)[:120],flush=True)
if records:
 with (O/'structural_baseline.csv').open('w',newline='') as f:
  w=csv.DictWriter(f,fieldnames=records[0].keys());w.writeheader();w.writerows(records)
print('COUNT',len(records),'median shared',statistics.median(x['shared_pct'] for x in records),flush=True)

if args.official_csv and records:
 with args.official_csv.open() as f:
  official={r['case'].removesuffix('.txt'):(int(r['area']),int(r['delay'])) for r in csv.DictReader(f) if r.get('status')=='PASS' and r.get('area') and r.get('delay')}
 matches=sum(official.get(r['case'])==(r['area'],r['delay']) for r in records)
 print('AREA_DELAY_MATCHES_OFFICIAL',matches,'/',len(records),flush=True)
 if matches!=len(records):raise SystemExit('Area/delay discrepancy found; investigate inputs/source before using statistics')

from pathlib import Path
import sys
case_id=sys.argv[1] if len(sys.argv)>1 else '005'
fn=Path(f'/mnt/data/r83_audit/case{case_id}_base.net')
case=Path(f'/mnt/data/round83_work/data/stage2/case_{case_id}.txt').read_text().split();n,m=map(int,case[:2]);aa,da,ao,dor,an,dn,target,limit=map(int,case[-8:]);
rows=fn.read_text().splitlines();ops=[None]*(n+1);args=[()]*(n+1)
for s in rows[:-1]:
 z=s.split(); idx=int(z[0]);assert idx==len(ops),(idx,len(ops));ops.append(z[1]);args.append(tuple(map(int,z[2:])))
outputs=list(map(int,rows[-1].split()))
print('n,m',n,m,'nodes',len(ops),'outputs',len(outputs),'costs',aa,ao,an,'delays',da,dor,dn,'target',target)
use=[0]*len(ops);needed=[10**9]*len(ops);arrival=[0]*len(ops)
costs={'AND2':aa,'OR2':ao,'NOT':an};dels={'AND2':da,'OR2':dor,'NOT':dn}
for v in range(n+1,len(ops)):
 for u in args[v]:use[u]+=1
 arrival[v]=max([arrival[u] for u in args[v]]+[0])+dels[ops[v]]
for o in outputs:use[o]+=1;needed[o]=min(needed[o],target)
for v in range(len(ops)-1,n,-1):
 if needed[v]>=10**9:continue
 for u in args[v]:needed[u]=min(needed[u],needed[v]-dels[ops[v]])
ranked=[]
for id in range(n+1,len(ops)):
 if needed[id]>=10**9 or not use[id]:continue
 potential=costs[ops[id]]*16
 for u in args[id]:
  if u>n and use[u]==1:potential+=8*costs[ops[u]]
 potential+=min(8,max(0,needed[id]-arrival[id]))
 ranked.append((-potential,id))
ranked.sort();print('live eligible',len(ranked)); k=1500;Q=900
chosen=ranked[:min(k,len(ranked))]
naive=sorted(chosen,key=lambda z:z[1])[:Q]
ideal=ranked[:Q]
naive_set={x[1] for x in naive};ideal_set={x[1] for x in ideal};rank_map={x[1]:idx+1 for idx,x in enumerate(ranked)}
print('intersection firstQ vs topQ',len(naive_set&ideal_set), 'of',Q)
print('TopQ skipped despite selected',len(ideal_set-naive_set));print('visited candidate priority rank median', sorted(rank_map[id] for id in naive_set)[Q//2], 'max',max(rank_map[id] for id in naive_set))
print('potential sum visits',-sum(x[0] for x in naive),'top Q potential sum',-sum(x[0] for x in ideal))
print('potential lower score visited',min(-x[0] for x in naive), 'best unvisited',max(-x[0] for x in chosen[Q:]) if chosen[Q:] else 0)

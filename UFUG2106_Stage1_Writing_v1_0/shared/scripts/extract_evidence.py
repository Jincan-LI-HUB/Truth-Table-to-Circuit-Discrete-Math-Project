#!/usr/bin/env python3
"""Rebuild the source-linked figure data from historical local_runs ZIPs.
Run with --source-dir /path/containing/*Round*_local_results.zip.
Does not invent missing records and refuses unexpected schema/counts.
"""
import os, csv, io, json, zipfile, hashlib, argparse, pathlib, statistics
p=argparse.ArgumentParser();p.add_argument('--source-dir',default='/mnt/data');p.add_argument('--out-dir',default=None); args=p.parse_args()
ROOT=pathlib.Path(__file__).resolve().parents[1]; OUT=pathlib.Path(args.out_dir or ROOT/'data');OUT.mkdir(parents=True,exist_ok=True)
ORIG=pathlib.Path(args.source_dir)
def pull(zipname,suffix):
 zpath=ORIG/zipname
 if not zpath.exists():raise FileNotFoundError(zpath)
 with zipfile.ZipFile(zpath) as z:
  hits=[x for x in z.namelist() if x.endswith(suffix)]
  if len(hits)!=1: raise RuntimeError(f'{zipname} suffix={suffix} matches {hits}')
  return z.read(hits[0]).decode('utf-8-sig'), hits[0]
def csvpull(zipname,suffix):
 data,loc=pull(zipname,suffix)
 return list(csv.DictReader(io.StringIO(data))),loc
D=[
 ('Round 1','20261111_104006_Round1_local_results.zip','/official.csv'),
 ('Round 2','20261111_104026_Round2_local_results.zip','/official.csv'),
 ('Round 3','20261111_095622_Round3_local_results.zip','/official.csv'),
 ('Round 4','20261111_112447_Round4_local_results.zip','/official.csv'),
 ('Round 4.1 B','20261111_121216_Round4.1_local_results.zip','/balanced/official.csv'),
 ('Round 5','20261111_130515_Round5_local_results.zip','/round5/official.csv'),
 ('Round 5.1','20261111_134547_Round5.1_local_results.zip','/benchmark/run1_round51.csv'),
 ('Round 6.0','20261111_143322_Round6.0_local_results.zip','/benchmark/run1_round60.csv'),
 ('Round 6.1','20261111_184840_Round6.1_local_results.zip','/benchmark/run1_round61.csv'),
]
manifest=[];summaries=[];selected={}
for label,archive,suffix in D:
 rows,loc=csvpull(archive,suffix)
 if len(rows)!=25:raise RuntimeError(f'{label} count={len(rows)}')
 required={'case','status','area','delay','runtime_ms','target_met'}
 if not required.issubset(rows[0]):raise RuntimeError(f'{label} lacks fields: {rows[0].keys()}')
 for r in rows:
  if r['status']!='PASS':raise RuntimeError(f'{label} case failed: {r}')
  r['area']=int(r['area']);r['delay']=int(r['delay']);r['runtime_ms']=float(r['runtime_ms']);r['target_met']=r['target_met'].strip().lower()=='yes'
 arr=[r['area'] for r in rows];ts=[r['runtime_ms'] for r in rows]
 summaries.append({'round':label,'pass':sum(r['status']=='PASS' for r in rows),'target_met':sum(r['target_met'] for r in rows),'area_sum':sum(arr),'median_runtime_ms':round(statistics.median(ts),3),'sum_runtime_ms':round(sum(ts),3),'max_runtime_ms':round(max(ts),3),'data_kind':'WSL archived individual invocation; do not treat as paired across versions','source_zip':archive,'source_member':loc})
 selected[label]={r['case']:r for r in rows}
 with open(OUT/f'official_{label.lower().replace(" ","_").replace(".","_")}.csv','w',newline='') as f:
  w=csv.writer(f);w.writerow(['case','status','area','delay','runtime_ms','target_met'])
  for r in rows:w.writerow([r[k] for k in ['case','status','area','delay','runtime_ms','target_met']])
 manifest.append({'round':label,'source_zip':archive,'sha256':hashlib.sha256((ORIG/archive).read_bytes()).hexdigest(),'member':loc})
with open(OUT/'round_history.csv','w',newline='') as f:
 w=csv.DictWriter(f,fieldnames=list(summaries[0]));w.writeheader();w.writerows(summaries)
with open(OUT/'source_manifest.csv','w',newline='') as f:
 w=csv.DictWriter(f,fieldnames=list(manifest[0]));w.writeheader();w.writerows(manifest)
# Controlled paired comparisons. Use medians already audited from the paired ZIP's official CSVs.
PAIRS=[
 ('5 vs 4.1 B','20261111_130515_Round5_local_results.zip','/reference/official.csv','/round5/official.csv'),
 ('5.1 vs 5 #1','20261111_134547_Round5.1_local_results.zip','/benchmark/run1_reference.csv','/benchmark/run1_round51.csv'),
 ('5.1 vs 5 #2','20261111_134547_Round5.1_local_results.zip','/benchmark/run2_reference.csv','/benchmark/run2_round51.csv'),
 ('6.0 vs 5.1 #1','20261111_143322_Round6.0_local_results.zip','/benchmark/run1_reference.csv','/benchmark/run1_round60.csv'),
 ('6.0 vs 5.1 #2','20261111_143322_Round6.0_local_results.zip','/benchmark/run2_reference.csv','/benchmark/run2_round60.csv'),
 ('6.1 vs 5.1 #1','20261111_184840_Round6.1_local_results.zip','/benchmark/run1_reference.csv','/benchmark/run1_round61.csv'),
 ('6.1 vs 5.1 #2','20261111_184840_Round6.1_local_results.zip','/benchmark/run2_reference.csv','/benchmark/run2_round61.csv'),
]
pair_rows=[]
for label,archive,base,new in PAIRS:
 a,pa=csvpull(archive,base);b,pb=csvpull(archive,new)
 if len(a)!=25 or len(b)!=25:raise RuntimeError(label)
 a={r['case']:r for r in a};b={r['case']:r for r in b}
 if a.keys()!=b.keys():raise RuntimeError(label+' case mismatch')
 area_a=sum(int(r['area']) for r in a.values()); area_b=sum(int(r['area']) for r in b.values())
 med_a=statistics.median(float(r['runtime_ms']) for r in a.values())
 med_b=statistics.median(float(r['runtime_ms']) for r in b.values())
 pair_rows.append({'pair':label,'baseline_area':area_a,'candidate_area':area_b,'baseline_median_ms':round(med_a,3),'candidate_median_ms':round(med_b,3),'runtime_delta_pct':round(100*(med_b/med_a-1),2),'source_zip':archive,'baseline_member':pa,'candidate_member':pb})
with open(OUT/'paired_benchmarks.csv','w',newline='') as f:
 w=csv.DictWriter(f,fieldnames=list(pair_rows[0]));w.writeheader();w.writerows(pair_rows)
# Round 5.1 official table with n=25, pass,target,area,delay,runtime (run 1)
r51=selected['Round 5.1'];r61=selected['Round 6.1']
with open(OUT/'stage1_per_case.csv','w',newline='') as f:
 w=csv.writer(f);w.writerow(['case','round51_status','round51_area','round51_delay','round51_runtime_ms','round51_target_met','round61_area_run1','round61_saving'])
 for case in sorted(r51):
  a=r51[case];b=r61[case]
  w.writerow([case,a['status'],a['area'],a['delay'],a['runtime_ms'],a['target_met'],b['area'],a['area']-b['area']])
# independent controlled holdouts for 6.1
hol=[('mixed40','/holdout/holdout_round61_fresh_v1_reference.csv','/holdout/holdout_round61_fresh_v1_round61.csv'),('large8','/holdout/holdout_round61_large_v1_reference.csv','/holdout/holdout_round61_large_v1_round61.csv')]
hr=[]
for label,a,b in hol:
 A,p1=csvpull('20261111_184840_Round6.1_local_results.zip',a);B,p2=csvpull('20261111_184840_Round6.1_local_results.zip',b)
 if len(A)!=len(B):raise RuntimeError(label+' count')
 hr.append({'set':label,'cases':len(A),'base_area':sum(int(x['area']) for x in A),'cut_area':sum(int(x['area']) for x in B),'base_median_ms':round(statistics.median(float(x['runtime_ms']) for x in A),3),'cut_median_ms':round(statistics.median(float(x['runtime_ms']) for x in B),3),'source_zip':'20261111_184840_Round6.1_local_results.zip','base_member':p1,'cut_member':p2})
with open(OUT/'cut_holdout.csv','w',newline='') as f:
 w=csv.DictWriter(f,fieldnames=list(hr[0]));w.writeheader();w.writerows(hr)
print('Evidence extracted:');print('rounds',[(x['round'],x['area_sum'],x['median_runtime_ms']) for x in summaries]);print('pairs',[(x['pair'],x['baseline_median_ms'],x['candidate_median_ms']) for x in pair_rows]);print('holdout',hr)

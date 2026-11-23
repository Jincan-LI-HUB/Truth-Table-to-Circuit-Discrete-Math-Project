#!/usr/bin/env python3
"""Summarize user-visible local comparisons, not official evaluator scores."""
import csv,statistics,math,json
from pathlib import Path
P=Path(__file__).resolve().parents[1]
summary=[]
for bank in ('dev','stage2','lockbox'):
 path=P/'evidence'/f'ablation_{bank}'/'casewise.csv'
 if not path.exists():continue
 rows=list(csv.DictReader(path.open()))
 grouped={}
 for r in rows:grouped.setdefault(r['case'],{})[r['tag']]=r
 for mode in ('frozen','library','repeat_sop','repeat_shannon'):
  vals=[z[mode] for z in grouped.values() if mode in z]
  base=[z['frozen'] for z in grouped.values() if mode in z and 'frozen' in z]
  if len(vals)!=len(grouped):raise RuntimeError('missing case '+bank+' '+mode)
  summary.append(dict(bank=bank,policy=mode,n=len(vals),area_sum=sum(int(x['area']) for x in vals),delay_sum=sum(int(x['delay']) for x in vals),wall_sum_ms=round(sum(float(x['wall_ms']) for x in vals),3),runtime_geomean_ratio=round(math.exp(statistics.mean(math.log(float(x['wall_ms'])/float(y['wall_ms'])) for x,y in zip(vals,base))),4),area_improved=sum(int(x['area'])<int(y['area']) for x,y in zip(vals,base)),area_worsened=sum(int(x['area'])>int(y['area']) for x,y in zip(vals,base))))
with (P/'evidence/local_4way_summary.csv').open('w',newline='') as f:
 w=csv.DictWriter(f,fieldnames=summary[0].keys());w.writeheader();w.writerows(summary)
print('LOCAL_4WAY_SUMMARY')
for x in summary:print(x)

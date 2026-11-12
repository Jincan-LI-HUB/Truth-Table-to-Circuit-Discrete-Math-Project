#!/usr/bin/env python3
"""Compare measured stage-1 results against the frozen user-local Round 4 CSV."""
from pathlib import Path
import csv,statistics,sys

def read(path):
    with open(path, newline='', encoding='utf-8-sig') as fp:
        rows=list(csv.DictReader(fp))
    assert len(rows)==25 and len({r['case'] for r in rows})==25, (path,len(rows))
    return {r['case']:r for r in rows}

def check(rows):
    return sum(r['status']=='PASS' for r in rows.values()),sum(r['target_met']=='yes' for r in rows.values()),sum(int(r['area']) for r in rows.values()),statistics.median(float(r['runtime_ms']) for r in rows.values()),max(float(r['runtime_ms']) for r in rows.values())

run=Path(sys.argv[1]);ref=read(Path(sys.argv[2]));report=run/'report_ready';report.mkdir(parents=True,exist_ok=True)
all_cases=sorted(ref);variants=[v for v in ['strict','balanced','fast'] if (run/v/'official.csv').is_file()];assert variants
out=['# Round 4.1 — Runtime Optimization — Local WSL Measurements','', 'Reference is the **original frozen Round 4 run on the same WSL machine**, not another host.', '', '| Variant | PASS | Target Met | Area total | Median Runtime (ms) | Max Runtime (ms) |','|---|---:|---:|---:|---:|---:|']
s=check(ref);out.append(f'| Original Round 4 | {s[0]}/25 | {s[1]}/25 | {s[2]:,} | {s[3]:.3f} | {s[4]:.3f} |')
for v in variants:
 d=read(run/v/'official.csv');assert set(d)==set(ref)
 s=check(d);out.append(f'| {v} | {s[0]}/25 | {s[1]}/25 | {s[2]:,} | {s[3]:.3f} | {s[4]:.3f} |')
out.extend(['','Area and Runtime are distinct quality dimensions. All runtimes depend on machine load and filesystem; a single evaluation does not establish a statistical speedup.',''])
(report/'local_runtime_summary.md').write_text('\n'.join(out)+'\n',encoding='utf8')
with (run/'per_case_runtime_comparison.csv').open('w',newline='',encoding='utf8') as f:
 w=csv.writer(f)
 w.writerow(['case','variant','reference_area','area','area_delta','reference_delay','delay','delay_delta','reference_runtime_ms','runtime_ms','runtime_ratio'])
 for v in variants:
  d=read(run/v/'official.csv')
  for c in all_cases:
   a,b=ref[c],d[c];time0=float(a['runtime_ms']);time1=float(b['runtime_ms'])
   w.writerow([c,v,a['area'],b['area'],int(b['area'])-int(a['area']),a['delay'],b['delay'],int(b['delay'])-int(a['delay']),a['runtime_ms'],b['runtime_ms'],round(time1/time0,6) if time0>0 else ''])
print('\n'.join(out))

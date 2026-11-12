#!/usr/bin/env python3
"""Produce local Round 4 reproduction summaries and per-case comparisons.
Only requires the Python standard library.
"""
import csv, pathlib, statistics, sys
if len(sys.argv) != 6:
    raise SystemExit('usage: summarize_round4.py LOCAL.csv R4_REFERENCE.csv ROUND3_REFERENCE.csv SUMMARY.txt COMPARISON.csv')
local_path,r4_path,r3_path,summary_path,comparison_path = map(pathlib.Path,sys.argv[1:])
required={'case','status','area','delay','runtime_ms','target_met'}
def load(p):
    with p.open(newline='',encoding='utf-8-sig') as f:
        reader=csv.DictReader(f)
        if not required.issubset(set(reader.fieldnames or [])):
            raise ValueError(f'{p}: invalid header')
        rows=list(reader)
    if len(rows)!=25 or len({r['case'] for r in rows})!=25:
        raise ValueError(f'{p}: expected 25 unique cases, got {len(rows)}')
    return {r['case']:r for r in rows}
local,r4,r3=map(load,[local_path,r4_path,r3_path])
if set(local)!=set(r4) or set(local)!=set(r3):raise ValueError('case sets differ')
def metrics(rows):
    vals=list(rows.values()); return {
       'pass':sum(x['status']=='PASS' for x in vals),
       'target':sum(x['status']=='PASS' and x['target_met']=='yes' for x in vals),
       'area':sum(int(x['area']) for x in vals if x['status']=='PASS'),
       'med':statistics.median(float(x['runtime_ms']) for x in vals),
       'max':max(float(x['runtime_ms']) for x in vals)}
a,b,c=map(metrics,[local,r4,r3])
fields=['case','status','local_area','round4_reference_area','round3_reference_area','area_delta_vs_round4','area_delta_vs_round3',
        'local_delay','round4_reference_delay','round3_reference_delay','delay_delta_vs_round4',
        'local_target_met','round4_reference_target_met','local_runtime_ms','round4_reference_runtime_ms']
with comparison_path.open('w',encoding='utf-8',newline='') as f:
    w=csv.DictWriter(f,fieldnames=fields);w.writeheader()
    for name in sorted(local):
        x,y,z=local[name],r4[name],r3[name]
        ok=x['status']=='PASS' and y['status']=='PASS'
        w.writerow(dict(case=name,status=x['status'],local_area=x['area'],round4_reference_area=y['area'],round3_reference_area=z['area'],
         area_delta_vs_round4=int(x['area'])-int(y['area']) if ok else '',area_delta_vs_round3=int(x['area'])-int(z['area']) if ok else '',
         local_delay=x['delay'],round4_reference_delay=y['delay'],round3_reference_delay=z['delay'],
         delay_delta_vs_round4=int(x['delay'])-int(y['delay']) if ok else '',
         local_target_met=x['target_met'],round4_reference_target_met=y['target_met'],
         local_runtime_ms=x['runtime_ms'],round4_reference_runtime_ms=y['runtime_ms']))
lines=['# UFUG2106 Round 4 — Local Reproduction',
       f'Official PASS: {a["pass"]}/25 (reference {b["pass"]}/25)',
       f'Target Delay Met: {a["target"]}/25 (reference {b["target"]}/25)',
       f'Area sum: {a["area"]:,} (reference Round 4 {b["area"]:,}; Round 3 {c["area"]:,})',
       f'Area difference vs Round 4 reference: {a["area"]-b["area"]:+,}',
       f'Area difference vs Round 3 reference: {a["area"]-c["area"]:+,}',
       f'Median Runtime: {a["med"]:.3f} ms (reference Round 4 {b["med"]:.3f} ms)',
       f'Max Runtime: {a["max"]:.3f} ms',
       '', 'All runtimes are platform-dependent. Variant search may produce different netlists depending on runtime budget.',
       'Area sum is a descriptive statistic across cases, NOT the instructor grading score.',
       'Correctness PASS and target_met are separate metrics.']
summary_path.write_text('\n'.join(lines)+'\n',encoding='utf8')
print('\n'.join(lines[:8]))

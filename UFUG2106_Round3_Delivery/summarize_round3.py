#!/usr/bin/env python3
"""Summarize a fresh local UFUG2106 Round 3 evaluator run.
Stdlib only. Usage: python3 summarize_round3.py NEW.csv REFERENCE.csv SUMMARY.txt COMPARISON.csv
"""
import csv
import statistics
import sys
from pathlib import Path

if len(sys.argv) != 5:
    raise SystemExit('usage: summarize_round3.py NEW.csv REFERENCE.csv SUMMARY.txt COMPARISON.csv')

new_path, ref_path, text_path, delta_path = map(Path, sys.argv[1:])

def load(p):
    with p.open(newline='', encoding='utf-8-sig') as f:
        rows = list(csv.DictReader(f))
    if not rows or len(rows) != len({r['case'] for r in rows}):
        raise ValueError(f'empty or duplicate case identifiers in {p}')
    for r in rows:
        if r['status'] == 'PASS':
            for k in ('area', 'delay', 'runtime_ms'):
                if not r.get(k):
                    raise ValueError(f'missing {k} in passing case {r["case"]}')
    return {r['case']: r for r in rows}

new, ref = load(new_path), load(ref_path)
if set(new) != set(ref):
    raise ValueError(f'mismatched case sets. new-only={sorted(set(new)-set(ref))}, reference-only={sorted(set(ref)-set(new))}')

def yes(x):
    return str(x).strip().lower() in ('yes', 'true', '1')

def summarize(a):
    good = [v for v in a.values() if v['status'] == 'PASS']
    return {
        'passed': len(good), 'total': len(a),
        'target': sum(yes(r['target_met']) for r in good),
        'area': sum(int(r['area']) for r in good),
        'median_runtime': statistics.median(float(r['runtime_ms']) for r in good) if good else None,
        'max_runtime': max((float(r['runtime_ms']) for r in good), default=None),
    }

ns, rs = summarize(new), summarize(ref)

comparison = []
for case in sorted(new):
    a, b = new[case], ref[case]
    if a['status'] == b['status'] == 'PASS':
        da, dd, dr = int(a['area'])-int(b['area']), int(a['delay'])-int(b['delay']), round(float(a['runtime_ms'])-float(b['runtime_ms']),3)
    else:
        da=dd=dr=''
    comparison.append({
        'case': case,
        'local_status': a['status'], 'reference_status': b['status'],
        'local_area': a.get('area',''), 'reference_area': b.get('area',''), 'area_delta': da,
        'local_delay': a.get('delay',''), 'reference_delay': b.get('delay',''), 'delay_delta': dd,
        'local_runtime_ms': a.get('runtime_ms',''), 'reference_runtime_ms': b.get('runtime_ms',''), 'runtime_delta_ms': dr,
        'local_target_met': a.get('target_met',''), 'reference_target_met': b.get('target_met','')
    })

with delta_path.open('w',newline='',encoding='utf-8') as f:
    w=csv.DictWriter(f, fieldnames=list(comparison[0])); w.writeheader(); w.writerows(comparison)

out=[
    'UFUG2106 Round 3 - fresh local reproduction',
    f'Local evaluator CSV: {new_path}',
    f'Reference CSV: {ref_path}',
    '',
    f'Cases PASS: local {ns["passed"]}/{ns["total"]} | reference {rs["passed"]}/{rs["total"]}',
    f'Target Delay met: local {ns["target"]}/{ns["total"]} | reference {rs["target"]}/{rs["total"]}',
    f'Area sum: local {ns["area"]:,} | reference {rs["area"]:,} | difference {ns["area"]-rs["area"]:+,}',
    f'Median runtime (ms): local {ns["median_runtime"]} | reference {rs["median_runtime"]}',
    f'Max runtime (ms): local {ns["max_runtime"]} | reference {rs["max_runtime"]}',
    '',
    'Area differences by case: local minus reference (negative means local is smaller)',
]
for r in sorted((r for r in comparison if r['area_delta'] != ''), key=lambda x: x['area_delta']):
    if r['area_delta']:
        out.append(f"{r['case']}: area {r['area_delta']:+} (local {r['local_area']}, ref {r['reference_area']}), delay {r['delay_delta']:+}")
if all(r['area_delta'] == 0 for r in comparison if r['area_delta'] != ''):
    out.append('No area changes.')
failed=[r['case'] for r in comparison if r['local_status'] != 'PASS']
late=[r['case'] for r in comparison if r['local_status']=='PASS' and not yes(r['local_target_met'])]
if failed: out += ['', 'Failed cases: '+', '.join(failed)]
if late: out += ['', 'Cases missing Target Delay: '+', '.join(late)]
out += ['', 'NOTES:', '- Runtime changes across CPUs, WSL/Windows I/O, compiler versions and thermal conditions.', '- A change in Area/Delay may arise from deadline-truncated candidate search.', '- Only fresh local evaluator CSV and logs establish local results; reference numbers are historical.']
text_path.write_text('\n'.join(out)+'\n', encoding='utf-8')
print('\n'.join(out[:10]))

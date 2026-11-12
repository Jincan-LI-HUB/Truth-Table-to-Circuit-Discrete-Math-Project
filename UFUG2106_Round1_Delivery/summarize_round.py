#!/usr/bin/env python3
"""Round 1 / Round 2 local-vs-reference statistics (standard library only)."""
import csv
from pathlib import Path
import statistics
import sys
if len(sys.argv) != 6:
    raise SystemExit('usage: python3 summarize_round.py ROUND LOCAL.csv REFERENCE.csv SUMMARY.txt COMPARISON.csv')
round_name=sys.argv[1]
new_path, ref_path, summary_path, comparison_path=map(Path,sys.argv[2:])
required={'case','status','area','delay','runtime_ms','target_met'}
def load(path):
    with path.open('r',encoding='utf-8-sig',newline='') as fp:
        reader=csv.DictReader(fp)
        if not required.issubset(reader.fieldnames or []):
            raise ValueError(f'{path}: missing columns {required-set(reader.fieldnames or [])}')
        rows=list(reader)
    if not rows or len(rows)!=len({r['case'] for r in rows}):
        raise ValueError(f'{path}: empty or duplicate case identifiers')
    return {r['case']:r for r in rows}
new,reference=load(new_path),load(ref_path)
if set(new)!=set(reference):
    raise ValueError('Case mismatch: local-only='+str(sorted(set(new)-set(reference)))+' ref-only='+str(sorted(set(reference)-set(new))))
def yes(v): return v.strip().lower() in {'yes','true','1'}
def summary(dataset):
    passed=[r for r in dataset.values() if r['status']=='PASS']
    return dict(total=len(dataset),pass_count=len(passed),target_count=sum(yes(r['target_met']) for r in passed),
                area_sum=sum(int(r['area']) for r in passed),
                median_ms=statistics.median(float(r['runtime_ms']) for r in passed) if passed else None,
                max_ms=max((float(r['runtime_ms']) for r in passed),default=None))
local=summary(new); ref=summary(reference)
fields=['case','local_status','reference_status','local_area','reference_area','area_delta','local_delay','reference_delay','delay_delta','local_target_met','reference_target_met','local_runtime_ms','reference_runtime_ms','runtime_delta_ms']
with comparison_path.open('w',encoding='utf-8',newline='') as fp:
    writer=csv.DictWriter(fp,fieldnames=fields);writer.writeheader()
    for key in sorted(new):
        a,b=new[key],reference[key]
        ok=a['status']==b['status']=='PASS'
        writer.writerow({'case':key,'local_status':a['status'],'reference_status':b['status'],
          'local_area':a.get('area',''),'reference_area':b.get('area',''),
          'area_delta':int(a['area'])-int(b['area']) if ok else '',
          'local_delay':a.get('delay',''),'reference_delay':b.get('delay',''),
          'delay_delta':int(a['delay'])-int(b['delay']) if ok else '',
          'local_target_met':a.get('target_met',''),'reference_target_met':b.get('target_met',''),
          'local_runtime_ms':a.get('runtime_ms',''),'reference_runtime_ms':b.get('runtime_ms',''),
          'runtime_delta_ms':round(float(a['runtime_ms'])-float(b['runtime_ms']),3) if ok else ''})
lines=[f'UFUG2106 {round_name} - local reproduction',f'Local evaluator CSV: {new_path}',f'Historical reference: {ref_path}',
       f'Official PASS: {local["pass_count"]}/{local["total"]} | reference {ref["pass_count"]}/{ref["total"]}',
       f'Target Delay met: {local["target_count"]}/{local["total"]} | reference {ref["target_count"]}/{ref["total"]}',
       f'Area sum: {local["area_sum"]:,} | reference {ref["area_sum"]:,} | difference {local["area_sum"]-ref["area_sum"]:+,}',
       f'Median runtime ms: {local["median_ms"]} | reference {ref["median_ms"]}',
       f'Max runtime ms: {local["max_ms"]} | reference {ref["max_ms"]}',
       f'Case count: {local["total"]}',
       '', 'CAVEATS:', '- Missing Target Delay alone does not mean official FAIL.',
       '- Area/Delay may be deterministic while runtime differs with CPU/WSL and machine load.',
       '- Historical references are not measurements on your machine.',
       '- Sum of areas is a cross-case diagnostic, not a published grading formula.',
       '- Search cutoffs in later rounds can change which circuit is selected.']
summary_path.write_text('\n'.join(lines)+'\n',encoding='utf8')
print('\n'.join(lines[:9]))

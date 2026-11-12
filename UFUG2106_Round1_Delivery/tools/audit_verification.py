#!/usr/bin/env python3
"""Audit independent verifier outputs against official area/delay (stdlib only)."""
import ast
import csv
import sys
from pathlib import Path
if len(sys.argv)!=3:
    raise SystemExit('usage: audit_verification.py RUN_DIR STAGE1_DIR')
run=Path(sys.argv[1]);cases=Path(sys.argv[2]);case_files=sorted(cases.glob('case_*.txt'))
lines=(run/'independent_verification.log').read_text(encoding='utf8',errors='replace').splitlines()
entries=[]
for line in lines:
    if line.startswith('{'):
        try: entries.append(ast.literal_eval(line))
        except (ValueError,SyntaxError): pass
with (run/'official.csv').open(newline='',encoding='utf-8-sig') as f:
    official={r['case']:r for r in csv.DictReader(f)}
rows=[]
problems=[]
if len(entries)!=len(case_files): problems.append(f'{len(entries)} independent entries for {len(case_files)} cases')
for case,e in zip(case_files,entries):
    r=official.get(case.name)
    if not r:
        problems.append('official CSV missing '+case.name)
        continue
    try:
        agrees=(e.get('matched') is True and r['status']=='PASS' and
                int(e['area'])==int(r['area']) and int(e['delay'])==int(r['delay']))
    except (KeyError,TypeError,ValueError): agrees=False
    rows.append({'case':case.name,'mode':'exhaustive' if e.get('exhaustive') else 'sampled',
       'assignments':e.get('assignments',''),'independent_area':e.get('area',''),
       'official_area':r.get('area',''),'independent_delay':e.get('delay',''),
       'official_delay':r.get('delay',''),'agree':'yes' if agrees else 'no'})
    if not agrees: problems.append('mismatch: '+case.name)
if set(official)!={p.name for p in case_files}: problems.append('case set mismatch')
fields=['case','mode','assignments','independent_area','official_area','independent_delay','official_delay','agree']
with (run/'independent_crosscheck.csv').open('w',newline='',encoding='utf8') as f:
    w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(rows)
summary=(f'Independent entries: {len(entries)}/{len(case_files)}\n'
         f'Exhaustive cases: {sum(r["mode"]=="exhaustive" for r in rows)}\n'
         f'Sampled cases: {sum(r["mode"]=="sampled" for r in rows)}\n'
         f'Area/delay agreement: {sum(r["agree"]=="yes" for r in rows)}/{len(case_files)}\n'
         f'Problems: {problems if problems else "none"}\n')
(run/'verification_summary.txt').write_text(summary,encoding='utf8')
print(summary)
if problems:raise SystemExit(1)

#!/usr/bin/env python3
"""TEST DOUBLE ONLY — NOT the course evaluator. Tests caller's input isolation."""
import csv,os,sys
from pathlib import Path
_,program,source,*rest=sys.argv
assert len(rest)==2 and rest[0]=='--report',rest
p=Path(source)
if p.is_dir():
    entries=list(p.iterdir())
    if len(entries)!=1 or entries[0].name!='case_001.txt':
        print('MOCK REJECT directory contains non-case files:',[e.name for e in entries])
        sys.exit(13)
else:
    assert p.name=='case_001.txt'
with Path(rest[1]).open('w',newline='') as f:
    w=csv.DictWriter(f,fieldnames=('case','status','area','delay','runtime_ms','target_met'))
    w.writeheader();w.writerow({'case':'case_001.txt','status':'PASS','area':'0','delay':'0','runtime_ms':'1','target_met':'yes'})
print('MOCK PASS -- strict isolated-directory invocation')

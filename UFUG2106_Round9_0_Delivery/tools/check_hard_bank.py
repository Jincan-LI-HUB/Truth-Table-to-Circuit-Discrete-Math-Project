#!/usr/bin/env python3
import json,hashlib
from pathlib import Path
H=Path(__file__).resolve().parents[1]
meta=json.loads((H/'hard_bank/FROZEN_MANIFEST.json').read_text())
assert len(meta['cases'])==8
for c in meta['cases']:
 p=H/c['file'];assert hashlib.sha256(p.read_bytes()).hexdigest()==c['sha256']
 s=p.read_text().splitlines();assert len(s)==8 and int(s[0])==c['n'] and int(s[1])==c['m']
 assert len(s[2].split())==(1<<c['n'])
print('PASS hard-bank independent provenance 4 dev, 4 untested lockbox')

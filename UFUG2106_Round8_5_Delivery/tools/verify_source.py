#!/usr/bin/env python3
from pathlib import Path
import hashlib,json
H=Path(__file__).resolve().parents[1]
x=json.loads((H/'SOURCE_MANIFEST.json').read_text())
for name,expected in x['files'].items():
 f=H/name
 assert f.is_file(),f'missing {name}'
 assert hashlib.sha256(f.read_bytes()).hexdigest()==expected,f'mismatch {name}'
assert hashlib.sha256((H/'src/synth_round84_frozen.cpp').read_bytes()).hexdigest()==x['frozen_r84_source_sha256']
print('PASS Round8.5 source manifest and embedded frozen Round8.4 provenance')

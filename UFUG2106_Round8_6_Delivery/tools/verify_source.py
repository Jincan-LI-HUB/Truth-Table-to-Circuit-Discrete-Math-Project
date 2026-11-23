#!/usr/bin/env python3
"""Verify source snapshot and byte-identical embedded Round8.5 parent."""
from pathlib import Path
import hashlib,json
H=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
m=json.loads((H/'SOURCE_MANIFEST.json').read_text())
for name,expected in m['files'].items():
 f=H/name
 if not f.is_file():raise RuntimeError(f'missing {name}')
 if sha(f)!=expected:raise RuntimeError(f'changed {name}')
assert sha(H/'src/synth_round85_frozen.cpp')==m['frozen_r85_source_sha256']
assert sha(H/'src/synth_round86.cpp')==m['r86_source_sha256']
print('PASS R86 SHA-256 manifest and exact frozen R85 source snapshot',flush=True)

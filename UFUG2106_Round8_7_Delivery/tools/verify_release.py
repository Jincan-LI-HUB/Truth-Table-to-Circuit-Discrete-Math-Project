#!/usr/bin/env python3
"""Immutable source + holdout manifest check; no modification of source code."""
from pathlib import Path
import hashlib,json
H=Path(__file__).resolve().parents[1]
base=json.loads((H/'SOURCE_MANIFEST.json').read_text())
for name,hexvalue in base['sha256'].items():
 p=H/name
 if not p.is_file():raise RuntimeError('Missing '+name)
 h=hashlib.sha256(p.read_bytes()).hexdigest()
 if h!=hexvalue:raise RuntimeError('SOURCE TAMPER '+name)
print('PASS Round8.7 frozen source provenance,',len(base['sha256']),'files',flush=True)

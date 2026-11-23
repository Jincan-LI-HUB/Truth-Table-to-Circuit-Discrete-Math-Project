#!/usr/bin/env python3
"""Verify delivered source/evidence integrity using SHA-256 manifest."""
import hashlib,json
from pathlib import Path
P=Path(__file__).resolve().parents[1]
manifest=json.loads((P/'PACKAGE_MANIFEST.json').read_text())
for rel,d in manifest['files'].items():
 p=(P/rel)
 if not p.is_file():raise RuntimeError(f'Missing file: {rel}')
 if hashlib.sha256(p.read_bytes()).hexdigest()!=d['sha256']:raise RuntimeError(f'SHA mismatch: {rel}')
print('PASS package integrity',len(manifest['files']),'files; milestone',manifest['milestone'])

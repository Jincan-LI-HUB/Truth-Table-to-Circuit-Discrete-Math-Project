#!/usr/bin/env python3
"""Original vs spec-line-canonical pairs: exact token equivalence plus line layout."""
import hashlib,json
from pathlib import Path
H=Path(__file__).resolve().parents[1]
rows=[]
for name in ['holdouts','stress_v2']:
 originals=sorted((H/'original_bank'/name).glob('*.txt'))
 assert len(originals)==(36 if name=='holdouts' else 3)
 for src in originals:
  dst=H/'canonical_bank'/name/src.name
  o=src.read_text().split();c=dst.read_text().split()
  assert o==c,(src,'token differences')
  lines=dst.read_text().splitlines()
  n=int(lines[0]);m=int(lines[1]);N=1<<n
  assert len(lines)>=7 and lines[0].strip()==str(n) and lines[1].strip()==str(m)
  groups=lines[2].split()
  assert len(groups)==N
  assert all(len(v)==m and set(v)<={'0','1'} for v in groups)
  assert len(c) in (2+N+7,2+N+8,2+N+9)
  assert len(lines)==3+3+1+(len(c)-(2+N+7)) # header/truth + three gate-pairs + target + optional limits
  rows.append({'file':str(dst.relative_to(H)),'n':n,'m':m,
    'src_sha256':hashlib.sha256(src.read_bytes()).hexdigest(),
    'canonical_sha256':hashlib.sha256(dst.read_bytes()).hexdigest()})
print('PASS canonical-line format + exact 39/39 token-equivalent input pairs')

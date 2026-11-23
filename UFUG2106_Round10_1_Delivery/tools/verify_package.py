#!/usr/bin/env python3
from pathlib import Path
import hashlib,json
H=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 m=json.loads((H/'SOURCE_MANIFEST.json').read_text())
 for name,checksum in m['files'].items():
  p=H/name
  if not p.is_file() or sha(p)!=checksum:raise RuntimeError('SOURCE_CHANGED '+name)
 assert sha(H/'src/synth_round100_frozen.cpp')==m['frozen_r100_sha256']
 assert sha(H/'frozen_submission/synth.cpp')==m['frozen_r100_sha256']
 assert sha(H/'trial_submission/synth.cpp')==sha(H/'src/synth_round101.cpp')
 for h in (H/'src').glob('*.hpp'):
  assert sha(h)==sha(H/'trial_submission'/h.name)==sha(H/'frozen_submission'/h.name),h.name
 s=(H/'src/synth_round101.cpp').read_text()
 assert 'r101_budget_cap_ms=90.0' in s and 'UFUG_R101_BUDGET_CAP_MS' in s
 assert 'const std::string kind=r91env?r91env:"repeat_sop";' in s
 print('PASS R10.1 source manifest',len(m['files']),'files; frozen R10.0 SHA and self-contained trial',flush=True)
if __name__=='__main__':main()

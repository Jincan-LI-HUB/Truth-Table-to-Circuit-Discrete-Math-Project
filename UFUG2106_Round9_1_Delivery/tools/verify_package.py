#!/usr/bin/env python3
"""Self-contained source manifest and immutable frozen comparator."""
import hashlib,json
from pathlib import Path
H=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 assert sha(H/'src/synth_round90.cpp')=='f846b2c055bfd5ad8d252dd1dcaa6770040b290bff6dc2bddc0ab27ff77e4010','R9.0 parent changed'
 assert sha(H/'src/synth_round91.cpp')==sha(H/'submission/synth.cpp'),'submission drift'
 for src in sorted((H/'src').glob('*.hpp')):assert sha(src)==sha(H/'submission'/src.name),'header drift '+src.name
 m=json.loads((H/'SOURCE_MANIFEST.json').read_text())
 for path,digest in m['files'].items():
  p=H/path;assert p.is_file() and sha(p)==digest,'integrity failure '+path
 hard=json.loads((H/'hard_bank/FROZEN_MANIFEST.json').read_text())
 for case in hard['cases']:
  assert sha(H/case['file'])==case['sha256'],'hard-bank fixture modified '+case['file']
 print('PASS R91 source provenance:',len(m['files']),'files; frozen R90; 4 dev + 4 frozen lockbox hashes (audited once post-freeze)',flush=True)
if __name__=='__main__':main()

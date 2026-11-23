#!/usr/bin/env python3
"""Verify immutable frozen parent, exact submission candidate, and all package files."""
import hashlib,json,sys
from pathlib import Path
H=Path(__file__).resolve().parents[1]
SHA_PARENT='6d21a7d3cf80a8662f4f42a965e84c50d6cffcef7766a4d2dccf282c204078d8'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 assert sha(H/'src/synth_round86_frozen.cpp')==SHA_PARENT,'Wrong frozen Round8.6 parent'
 assert sha(H/'src/synth_round90.cpp')==sha(H/'submission/synth.cpp'),'Submission source drift'
 for f in sorted((H/'src').glob('*.hpp')):
  assert sha(f)==sha(H/'submission'/f.name),'Submission header drift: '+f.name
 manifest=json.loads((H/'SOURCE_MANIFEST.json').read_text())
 for path,digest in manifest['files'].items():
  p=H/path;assert p.is_file() and sha(p)==digest,f'Integrity fail {path}'
 assert 'r86env_early?r86env_early:"extra_sop"' in (H/'submission/synth.cpp').read_text()
 print('PASS Round9.0 source provenance, canonical banks and standalone submission manifest',len(manifest['files']),'entries')
if __name__=='__main__':main()

#!/usr/bin/env python3
import hashlib,json
from pathlib import Path
p=Path(__file__).resolve().parents[1]
base=p.parent/'UFUG2106_Round8_2_Delivery/src/synth_round82.cpp'
if base.exists():
 expected='07ca91581854fe3802ae0165674a3352771f1745ea85beee6608ee720f9a1caa'
 actual=hashlib.sha256(base.read_bytes()).hexdigest()
 if actual!=expected:raise RuntimeError('Frozen Round8.2 source SHA drift: '+actual)
man=json.loads((p/'SOURCE_MANIFEST.json').read_text())
for name,sha in man['sha256'].items():
 q=p/name
 if not q.is_file() or hashlib.sha256(q.read_bytes()).hexdigest()!=sha:raise RuntimeError('Source manifest mismatch: '+name)
print('PASS R821 frozen source SHA / all manifest hashes')

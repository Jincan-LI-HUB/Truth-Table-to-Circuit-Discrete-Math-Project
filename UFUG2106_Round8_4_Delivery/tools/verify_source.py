from pathlib import Path
import hashlib,json
H=Path(__file__).resolve().parents[1]
d=json.loads((H/'SOURCE_MANIFEST.json').read_text())
for name,h in d['files'].items():
    p=H/name
    assert p.is_file() and hashlib.sha256(p.read_bytes()).hexdigest()==h,name
par=H.parent/'UFUG2106_Round8_3_Delivery/src/synth_round83.cpp'
assert par.is_file() and hashlib.sha256(par.read_bytes()).hexdigest()==d['frozen_parent_round83_sha256'],'frozen Round8.3 source mismatch'
print('PASS Round8.4 manifest and frozen Round8.3 provenance')

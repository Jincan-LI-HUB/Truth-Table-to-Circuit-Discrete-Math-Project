from pathlib import Path
import hashlib,json
H=Path(__file__).resolve().parents[1]
data=json.loads((H/'SOURCE_MANIFEST.json').read_text())
for name,expected in data['files'].items():
    p=H/name
    assert p.is_file() and hashlib.sha256(p.read_bytes()).hexdigest()==expected,name
parent=H.parent/'UFUG2106_Round8_2_1_Delivery/src/synth_round821.cpp'
if not parent.is_file():raise RuntimeError('frozen parent Round8.2.1 source absent: '+str(parent))
assert hashlib.sha256(parent.read_bytes()).hexdigest()==data['frozen_parent_sha256'], 'frozen parent SHA mismatch'
print('PASS Round8.3 source, manifest and frozen parent hashes',flush=True)

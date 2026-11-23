#!/usr/bin/env python3
"""Check source provenance and frozen test fixtures before executing C++."""
from pathlib import Path
import hashlib,json
H=Path(__file__).resolve().parents[1]
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    m=json.loads((H/'SOURCE_MANIFEST.json').read_text())
    for name,digest in m['files'].items():
        p=H/name
        if not p.is_file() or sha(p)!=digest:
            raise RuntimeError('File missing/modified: '+name)
    expected=m['frozen_sources']
    assert sha(H/'src/synth_round91_frozen.cpp')==expected['r91'],'R9.1 comparator modified'
    assert sha(H/'src/synth_round90_frozen.cpp')==expected['r90'],'R9.0 comparator modified'
    assert sha(H/'src/synth_round100.cpp')==sha(H/'submission/synth.cpp'),'submission source drift'
    for h in (H/'src').glob('*.hpp'):
        assert sha(h)==sha(H/'submission'/h.name),'header drift '+h.name
    s=(H/'src/synth_round100.cpp').read_text()
    parent=(H/'src/synth_round91_frozen.cpp').read_text()
    a='const std::string kind=r91env?r91env:"repeat_sop";'
    b='if(const char* r91env=std::getenv("UFUG_R91_POLICY")){\n  const std::string kind=r91env;'
    assert s.count(a)==1 and b in parent, 'default patch assertion failed'
    print('PASS Round10.0 manifest',len(m['files']),'files; R9.0/R9.1 frozen; R10.0 default SOP; submission source identical',flush=True)
if __name__=='__main__':main()

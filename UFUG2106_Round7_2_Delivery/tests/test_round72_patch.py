#!/usr/bin/env python3
"""Check patch semantics and provide exact-source fingerprint check before benchmarking."""
import hashlib,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
p=ROOT/'src/synth_round72.cpp'
assert p.is_file(),'Run make first; generated source missing'
s=p.read_text()
need=[
 'R72_TRACE event=shortlist result=completed',
 'R72_TRACE event=shortlist result=checkpoint_timeout',
 'r72_checkpoint();in>>bits',
 'r72_checkpoint();int bit=__builtin_ctzll(z)',
 'r72_checkpoint();\n    int lo=cur[2*k]',
 'r72_checkpoint();if(t!=2&&a>b)',
 'const double admission=0.35*double(limit)',
 'const double deadline_fraction=0.60',
 'legacy::Opt cheap={"influence-desc",true,false,true,0,0}',
 'r72_use_shortlist',
 'const bool r71_skip_legacy=r72_short_feasible',
]
for s1 in need:assert s1 in s,'Missing R7.2 patch: '+s1
manifest=json.loads((ROOT/'SOURCE_MANIFEST.json').read_text())
assert manifest['source_sha256']['synth_round72.cpp']==hashlib.sha256(p.read_bytes()).hexdigest()
assert manifest['frozen_upstream_git_blob']=='68ec9f54b27081641ac10358f81eef260acfcbdb'
print('PASS R7.2 source patch, selected policy, checkpoints, and SHA-256 consistency')

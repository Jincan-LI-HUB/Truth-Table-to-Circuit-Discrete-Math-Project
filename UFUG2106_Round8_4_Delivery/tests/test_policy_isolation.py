#!/usr/bin/env python3
"""Conflicting older env policies must not affect R84. Exact Stage 2 fixture."""
import os,hashlib,subprocess,tempfile
from pathlib import Path
H=Path(__file__).resolve().parents[1];ROOT=H.parent
f=ROOT/'data/stage2/case_021.txt'
if not f.exists():raise RuntimeError('Need true Stage 2 case_021.txt')
with tempfile.TemporaryDirectory(prefix='r84_iso_') as t:
    hashes=[]
    for i in range(2):
        dst=Path(t)/f'{i}.net';env=os.environ.copy()
        for k in list(env):
            if k.startswith('UFUG_R') or k.startswith('UFUG_ROUND'):env.pop(k)
        env.update(UFUG_R84_POLICY='topq_dual',UFUG_R84_PROFILE='1')
        if i:env.update(UFUG_R8_POLICY='iterate',UFUG_R81_POLICY='reverse',UFUG_R82_POLICY='dual_area',UFUG_R83_POLICY='stable_dual_area')
        z=subprocess.run([str(H/'build/synth_round84'),str(f),str(dst)],env=env,text=True,capture_output=True,timeout=90)
        assert z.returncode==0 and 'R84_STAGE' in z.stderr,z.stderr[-500:]
        hashes.append(hashlib.sha256(dst.read_bytes()).hexdigest())
    assert hashes[0]==hashes[1],hashes
print('PASS policy_isolation: R8/R81/R82/R83 cannot contaminate R84')

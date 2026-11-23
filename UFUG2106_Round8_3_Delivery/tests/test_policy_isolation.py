#!/usr/bin/env python3
"""Cross-policy guards: legacy modes cannot accidentally run in R8.3."""
import hashlib,os,subprocess,tempfile
from pathlib import Path
H=Path(__file__).resolve().parents[1];ROOT=H.parent
p=ROOT/'data/stage2/case_021.txt'
if not p.is_file():raise RuntimeError('Expected true Stage2 case_021.txt for policy isolation check')
with tempfile.TemporaryDirectory(prefix='r83_iso_') as t:
    hashes=[]
    for i in range(2):
        dst=Path(t)/f'{i}.net';env=os.environ.copy()
        for k in list(env):
            if k.startswith('UFUG_R') or k.startswith('UFUG_ROUND'):env.pop(k)
        env['UFUG_R83_POLICY']='stable_dual_area';env['UFUG_R83_PROFILE']='1'
        if i:env.update(UFUG_R8_POLICY='iterate',UFUG_R81_POLICY='reverse',UFUG_R82_POLICY='dual_area')
        q=subprocess.run([str(H/'build/synth_round83'),str(p),str(dst)],env=env,capture_output=True,text=True)
        if q.returncode!=0 or 'R83_STAGE' not in q.stderr:raise AssertionError(q.stderr[-600:])
        hashes.append(hashlib.sha256(dst.read_bytes()).hexdigest())
    assert hashes[0]==hashes[1],hashes
print('PASS policy_isolation: R8/R81/R82 conflicts cannot contaminate R8.3',flush=True)

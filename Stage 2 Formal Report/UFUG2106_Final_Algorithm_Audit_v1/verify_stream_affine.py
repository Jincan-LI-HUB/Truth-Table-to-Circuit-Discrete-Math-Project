"""Exhaustively verify generated 18-input affine case output; local only."""
from pathlib import Path
import numpy as np
D=Path(__file__).resolve().parent
n=18;rows=np.arange(1<<n,dtype=np.uint32)
sig=[np.zeros(1<<n,dtype=np.uint8)]+[((rows>>(n-1-j))&1).astype(np.uint8) for j in range(n)]
lines=(D/'stream_affine_n18_limit250.netlist').read_text().splitlines()
for id,line in enumerate(lines[:-1],n+1):
 x=line.split();assert int(x[0])==id
 a=int(x[2]);b=int(x[3]) if len(x)==4 else None
 assert a<id and (b is None or b<id)
 sig.append((1-sig[a]) if x[1]=='NOT' else (sig[a]&sig[b] if x[1]=='AND2' else sig[a]|sig[b]))
output=list(map(int,lines[-1].split()));assert len(output)==1
expected=np.zeros(1<<n,dtype=np.uint8)
for j in range(n):expected^=(rows>>(n-1-j)).astype(np.uint8)&1
assert np.array_equal(sig[output[0]],expected)
print('PASS: 2^18 complete assignments; netlist gates',len(lines)-1)

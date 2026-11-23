#!/usr/bin/env python3
"""Produce the Issue #2 resource-limit test; no special-case content in the solver."""
from pathlib import Path
import sys
p=Path(sys.argv[1] if len(sys.argv)>1 else 'issue2_case_20input_wire_ram9000.txt')
with p.open('w',encoding='utf-8') as f:
    f.write('20\n1\n')
    for i in range(1<<20):
        f.write(str(i&1)+'\n')
    f.write('1 1\n1 1\n1 1\n10\n0\n9000\n')
print(p, p.stat().st_size, 'bytes')

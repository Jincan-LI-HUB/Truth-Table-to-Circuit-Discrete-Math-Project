#!/usr/bin/env python3
"""Verify all R7.1 injection anchors and generated patch invariants.
Full project C++ compilation runs during `make` on the user's frozen source.
"""
import ast,importlib.util
from pathlib import Path
P=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('r71',P/'bootstrap_round71.py')
r71=importlib.util.module_from_spec(spec);spec.loader.exec_module(r71)
source=(P/'bootstrap_round71.py').read_text()
tree=ast.parse(source)
patch=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='patch71')
needles=[]
for n in ast.walk(patch):
 if isinstance(n,ast.Call) and isinstance(n.func,ast.Name) and n.func.id=='replace_one':
  if len(n.args)>1 and isinstance(n.args[1],ast.Constant):
   needles.append(n.args[1].value)
assert len(needles)==10, f'Unexpected patch anchor count {len(needles)}'
# Construct a strict artificial reference where each expected source anchor occurs once.
# This checks anchor substitutions, non-overlapping matching and intended signatures.
fixture='\n// PART_BOUNDARY\n'.join(needles)
output=r71.patch71(fixture)
assert 'R71_TRACE event=legacy_skipped' in output
assert 'R71_TRACE event=primary index=' in output
assert 'const bool r71_skip_legacy' in output
assert 'const bool r71_guard=' in output
assert 'r71_search_cap*1000.0' in output
assert 'start=r71_launch' in output
assert output.count('R71_TRACE event=finish')==1
print('PASS Round 7.1: 10 exact source anchors; guard, policy-off and diagnostic substitutions present')

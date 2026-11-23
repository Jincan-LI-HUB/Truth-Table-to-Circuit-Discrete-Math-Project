#!/usr/bin/env python3
"""Unconditional archive of research evidence (even on failure)."""
from pathlib import Path
import argparse,json,datetime,platform,zipfile
H=Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser();p.add_argument('--exit-code',type=int,default=0);a=p.parse_args()
found=None;ptr=H/'latest_run.txt'
if ptr.is_file():
 t=Path(ptr.read_text().strip()).resolve()
 if t.is_dir() and t.parent==(H/'results').resolve():found=t
stamp=found.name if found else datetime.datetime.now().strftime('%Y%m%d_%H%M%S_%f')
out=H/'feedback'/f'Round8_Prototype_Feedback_{stamp}.zip';out.parent.mkdir(parents=True,exist_ok=True)
files=[]
if found: files.extend((f,'local_results/'+f.relative_to(found).as_posix()) for f in found.rglob('*') if f.is_file())
for q in ('results/latest_test.log','README.md','Makefile','run_round8.sh','bootstrap_round8.py','SOURCE_MANIFEST.json','src/synth_round8.cpp','src/r8_structural.hpp','src/typed_netgraph.hpp','src/optimize_netlist.cpp','tests/verify_exhaustive.cpp','tools/run_benchmarks.py','tools/export_feedback.py'):
 f=H/q
 if f.is_file():files.append((f,'source_snapshot/'+q))
files.extend((f,'research_docs/'+f.name) for f in (H/'docs').glob('*.md'))
with zipfile.ZipFile(out,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=6) as z:
 z.writestr('FEEDBACK_METADATA.json',json.dumps({'milestone':'Round8.0','exit_code':a.exit_code,'host':platform.platform(),'results_available':bool(found),'frozen_parent':'Round7.2'},indent=2))
 for path,name in files:z.write(path,name)
with zipfile.ZipFile(out) as z:assert z.testzip() is None
print('\nFEEDBACK ZIP CREATED:',out,flush=True)
print('Upload this ONE ZIP for Round 8 research analysis.',flush=True)

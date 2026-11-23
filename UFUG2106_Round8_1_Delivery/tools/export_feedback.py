#!/usr/bin/env python3
"""Archive official evidence and exact source snapshot, even upon failure."""
from pathlib import Path
import argparse,datetime,hashlib,json,platform,zipfile
H=Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser();p.add_argument('--exit-code',type=int,default=0);a=p.parse_args()
ptr=H/'latest_run.txt';run=None
if ptr.exists():
 t=Path(ptr.read_text().strip()).resolve()
 if t.is_dir() and t.parent==(H/'results').resolve():run=t
stamp=run.name if run else datetime.datetime.now().strftime('%Y%m%d_%H%M%S_%f')
out=H/'feedback'/f'Round8.1_Feedback_{stamp}.zip';out.parent.mkdir(parents=True,exist_ok=True)
files=[]
if run:files.extend((x,'official_run/'+x.relative_to(run).as_posix()) for x in run.rglob('*') if x.is_file())
for rel in ['README.md','Makefile','bootstrap_round81.py','run_round81.sh','SOURCE_MANIFEST.json',
 'src/synth_round81.cpp','src/r81_cut.hpp','src/r8_structural.hpp','src/typed_netgraph.hpp',
 'src/optimize_cut.cpp','tests/verify_exhaustive.cpp','tests/test_cut_random.py',
 'tools/run_benchmarks.py','tools/export_feedback.py','results/latest_test.log']:
 f=H/rel
 if f.exists():files.append((f,'source_snapshot/'+rel))
for x in (H/'docs').glob('*'):
 if x.is_file():files.append((x,'research_docs/'+x.name))
with zipfile.ZipFile(out,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=6) as zip:
 zip.writestr('FEEDBACK_METADATA.json',json.dumps({'milestone':'Round8.1','exit_code':a.exit_code,
   'host':platform.platform(),'results_available':run is not None,'official_grade_unknown':True},indent=2))
 for f,name in files:zip.write(f,name)
with zipfile.ZipFile(out) as zip:assert zip.testzip() is None
print('FEEDBACK ZIP CREATED:',out,flush=True)
print('Upload this one feedback ZIP for the next analysis.',flush=True)

#!/usr/bin/env python3
"""Export experiment, frozen source and ALL failure diagnostics as a single ZIP."""
from pathlib import Path
import argparse,datetime,hashlib,json,platform,zipfile
H=Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser();p.add_argument('--exit-code',type=int,default=0);a=p.parse_args()
file=H/'latest_run.txt';run=None
if file.exists():
    q=Path(file.read_text().strip()).resolve()
    if q.is_dir() and q.parent==(H/'results').resolve():run=q
stamp=run.name if run else datetime.datetime.now().strftime('%Y%m%d_%H%M%S_%f')
output=H/'feedback'/f'Round8.3_Feedback_{stamp}.zip';output.parent.mkdir(exist_ok=True)
files=[]
if run:files.extend((f,'experiment/'+f.relative_to(run).as_posix()) for f in run.rglob('*') if f.is_file())
for d in ('src','tools','tests','docs','evidence'):
    for f in (H/d).rglob('*'):
        if f.is_file() and '__pycache__' not in str(f):files.append((f,'source/'+f.relative_to(H).as_posix()))
for name in ('README.md','RELEASE_NOTES.md','Makefile','run_round83.sh','SOURCE_MANIFEST.json'):
    f=H/name
    if f.exists():files.append((f,'source/'+name))
log=H/'results/latest_test.log'
if log.is_file():files.append((log,'latest_test.log'))
with zipfile.ZipFile(output,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=6) as z:
    z.writestr('FEEDBACK_METADATA.json',json.dumps({'milestone':'Round8.3','exit_code':a.exit_code,
      'official_results_present':bool(run and (run/'official/summary.json').exists()),
      'ram_evaluator_gate_not_claimed':True,'host':platform.platform()},indent=2))
    for f,arc in files:z.write(f,arc)
with zipfile.ZipFile(output) as z:assert z.testzip() is None
print('FEEDBACK ZIP CREATED:',output,flush=True)
print('Upload this single ZIP for Round 8.3 analysis.',flush=True)

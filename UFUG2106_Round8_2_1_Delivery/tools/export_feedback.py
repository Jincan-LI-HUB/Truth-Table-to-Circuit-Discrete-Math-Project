#!/usr/bin/env python3
"""Feedback ZIP on success OR failure, without any fabricated official results."""
from pathlib import Path
import argparse,datetime,hashlib,json,platform,zipfile
H=Path(__file__).resolve().parents[1]
a=argparse.ArgumentParser();a.add_argument('--exit-code',type=int,default=0);x=a.parse_args()
p=H/'latest_run.txt';run=None
if p.exists():
    q=Path(p.read_text().strip()).resolve()
    if q.is_dir() and q.parent==(H/'results').resolve():run=q
name=run.name if run else datetime.datetime.now().strftime('%Y%m%d_%H%M%S_%f')
out=H/'feedback'/f'Round8.2.1_Feedback_{name}.zip';out.parent.mkdir(exist_ok=True)
files=[]
if run:files.extend((f,'experiment/'+f.relative_to(run).as_posix()) for f in run.rglob('*') if f.is_file())
for directory in ('src','tests','tools','docs'):
    for f in (H/directory).rglob('*'):
        if f.is_file() and '__pycache__' not in str(f):files.append((f,'source/'+f.relative_to(H).as_posix()))
for name in ('README.md','RELEASE_NOTES.md','Makefile','run_round821.sh','SOURCE_MANIFEST.json','evidence/holdout_structured_regression.json'):
    f=H/name
    if f.is_file():files.append((f,'source/'+name))
if (H/'results/latest_test.log').exists():files.append((H/'results/latest_test.log','latest_test.log'))
with zipfile.ZipFile(out,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=6) as z:
    z.writestr('FEEDBACK_METADATA.json',json.dumps({'milestone':'Round8.2.1','script_exit_code':x.exit_code,
      'official_results_present':bool(run and (run/'official/summary.json').exists()),
      'memory_evidence_present':bool(run and (run/'resource_tests/direct_summary.json').exists()),
      'official_grading_formula_known':False,'host':platform.platform()},indent=2))
    for f,name in files:z.write(f,name)
with zipfile.ZipFile(out) as z:assert z.testzip() is None
print('FEEDBACK ZIP CREATED:',out,flush=True)
print('Upload this ZIP for Round 8.2.1 analysis.',flush=True)

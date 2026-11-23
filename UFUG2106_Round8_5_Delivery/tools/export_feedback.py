#!/usr/bin/env python3
"""Record experiment, source, logs and exact evaluator output; never invent success."""
from pathlib import Path
import argparse,datetime,json,platform,zipfile
H=Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser();p.add_argument('--exit-code',type=int,default=0);a=p.parse_args()
file=H/'latest_run.txt';run=None
if file.is_file():
 q=Path(file.read_text().strip()).resolve()
 if q.is_dir() and q.parent==(H/'results').resolve():run=q
stamp=run.name if run else datetime.datetime.now().strftime('%Y%m%d_%H%M%S_%f')
out=H/'feedback'/f'Round8.5_Feedback_{stamp}.zip';out.parent.mkdir(exist_ok=True)
files=[]
if run:files.extend((f,'experiment/'+f.relative_to(run).as_posix()) for f in run.rglob('*') if f.is_file())
for folder in ('src','tools','tests','docs','evidence','integration'):
 for f in (H/folder).rglob('*'):
  if f.is_file() and '__pycache__' not in str(f):files.append((f,'source/'+f.relative_to(H).as_posix()))
for name in ('README.md','RELEASE_NOTES.md','Makefile','run_round85.sh','SOURCE_MANIFEST.json','STAGE2_SUBMISSION_README.md'):
 f=H/name
 if f.exists():files.append((f,'source/'+name))
log=H/'results/latest_test.log'
if log.is_file():files.append((log,'latest_test.log'))
with zipfile.ZipFile(out,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=6) as z:
 z.writestr('FEEDBACK_METADATA.json',json.dumps({'milestone':'Round8.5','exit_code':a.exit_code,
  'official_results_present':bool(run and (run/'official/summary.json').exists()),
  'course_ram_limit_not_assessed':True,'host':platform.platform()},indent=2))
 for f,arc in files:z.write(f,arc)
with zipfile.ZipFile(out) as z:assert z.testzip() is None
print('FEEDBACK ZIP CREATED:',out,flush=True)
print('Upload this ZIP for Round8.5 postmortem.',flush=True)

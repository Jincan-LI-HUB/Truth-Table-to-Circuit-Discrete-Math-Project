#!/usr/bin/env python3
import argparse,datetime,json,platform,zipfile
from pathlib import Path
H=Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser();p.add_argument('--exit-code',type=int,default=0);a=p.parse_args()
latest=H/'latest_run.txt';run=None
if latest.exists():
 try:
  r=Path(latest.read_text().strip()).resolve()
  if r.is_dir() and r.parent==(H/'results').resolve():run=r
 except Exception:pass
stamp=run.name if run else datetime.datetime.now().strftime('%Y%m%d_%H%M%S_%f')
out=H/'feedback'/f'Round8.7_Feedback_{stamp}.zip';out.parent.mkdir(exist_ok=True)
with zipfile.ZipFile(out,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=6) as z:
 z.writestr('FEEDBACK_METADATA.json',json.dumps({'milestone':'8.7','exit_code':a.exit_code,
     'true_course_evaluator_present':bool(run and (run/'official/summary.json').exists()),
     'no_hidden_case_claim':True,'platform':platform.platform()},indent=2))
 if run:
  for f in sorted(run.rglob('*')):
   if f.is_file():z.write(f,'experiment/'+f.relative_to(run).as_posix())
 for prefix in ('src','tools','tests','docs','evidence','stress_v2'):
  for f in sorted((H/prefix).rglob('*')):
   if f.is_file() and f.suffix not in ('.pyc',):z.write(f,'source/'+f.relative_to(H).as_posix())
 for f in sorted((H/'holdouts').rglob('*')):
  if f.is_file():z.write(f,'source/'+f.relative_to(H).as_posix())
 for name in ('Makefile','README.md','RELEASE_NOTES.md','SOURCE_MANIFEST.json','run_round87.sh'):
  f=H/name
  if f.exists():z.write(f,'source/'+name)
with zipfile.ZipFile(out) as z:assert z.testzip() is None
print('R87_FEEDBACK_ZIP:',out,flush=True)

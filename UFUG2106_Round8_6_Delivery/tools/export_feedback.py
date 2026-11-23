#!/usr/bin/env python3
from pathlib import Path
import argparse,datetime,json,platform,zipfile
H=Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser();p.add_argument('--exit-code',type=int,default=0);a=p.parse_args()
run=None;f=H/'latest_run.txt'
if f.exists():
 q=Path(f.read_text().strip()).resolve()
 if q.is_dir() and q.parent==(H/'results').resolve():run=q
stamp=run.name if run else datetime.datetime.now().strftime('%Y%m%d_%H%M%S_%f')
out=H/'feedback'/f'Round8.6_Feedback_{stamp}.zip';out.parent.mkdir(exist_ok=True)
files=[]
if run:files.extend((x,'experiment/'+x.relative_to(run).as_posix()) for x in run.rglob('*') if x.is_file())
for folder in ('src','tools','tests','docs','evidence','integration'):
 for x in (H/folder).rglob('*'):
  if x.is_file() and '__pycache__' not in str(x):files.append((x,'source/'+x.relative_to(H).as_posix()))
for name in ('README.md','RELEASE_NOTES.md','Makefile','run_round86.sh','SOURCE_MANIFEST.json','STAGE2_SUBMISSION_README.md'):
 f=H/name
 if f.exists():files.append((f,'source/'+name))
log=H/'results/latest_test.log'
if log.exists():files.append((log,'latest_test.log'))
with zipfile.ZipFile(out,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=6) as z:
 z.writestr('FEEDBACK_METADATA.json',json.dumps({'milestone':'Round8.6','exit_code':a.exit_code,'official_results_present':bool(run and (run/'official/summary.json').exists()),'no_hidden_or_RAM_claim':True,'host':platform.platform()},indent=2))
 for f,arc in files:z.write(f,arc)
with zipfile.ZipFile(out) as z:assert z.testzip() is None
print('FEEDBACK ZIP CREATED:',out,flush=True)

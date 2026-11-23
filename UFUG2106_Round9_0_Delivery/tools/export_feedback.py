#!/usr/bin/env python3
"""Archive success/failure evidence plus exact submitted C++ source."""
import argparse,datetime,json,platform,zipfile
from pathlib import Path
H=Path(__file__).resolve().parents[1]
q=argparse.ArgumentParser();q.add_argument('--exit-code',type=int,default=0);args=q.parse_args()
latest=H/'latest_run.txt';run=None
if latest.exists():
 try:
  x=Path(latest.read_text().strip()).resolve()
  if x.is_dir() and x.parent==(H/'results').resolve():run=x
 except Exception:pass
name=run.name if run else datetime.datetime.now().strftime('%Y%m%d_%H%M%S_%f')
target=H/'feedback'/f'Round9.0_Feedback_{name}.zip';target.parent.mkdir(exist_ok=True)
with zipfile.ZipFile(target,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=3) as z:
 z.writestr('FEEDBACK_METADATA.json',json.dumps(dict(round='9.0',exit_code=args.exit_code,
   genuine_official_attempt=bool(run and (run/'official').exists()),
   hidden_cases=False,platform=platform.platform()),indent=2))
 if run:
  for f in sorted(run.rglob('*')):
   if f.is_file():z.write(f,'experiment/'+f.relative_to(run).as_posix())
 for prefix in ('src','submission','tools','tests','docs','evidence'):
  for f in sorted((H/prefix).rglob('*')):
   if f.is_file() and f.suffix!='.pyc':z.write(f,'source/'+f.relative_to(H).as_posix())
 # Feedback is a compact, reproducible run audit, not a second full distribution.
 # Full frozen input banks already exist in the versioned delivery ZIP.
 for f in sorted((H/'canonical_bank/stress_v2').glob('stress_*.txt')):
  z.write(f,'source/'+f.relative_to(H).as_posix())
 for name in ('holdouts','stress_v2'):
  for f in sorted((H/'original_bank'/name).glob('*MANIFEST*.json')):
   z.write(f,'source/'+f.relative_to(H).as_posix())
 for f in sorted((H/'hard_bank').rglob('*.json')):
  z.write(f,'source/'+f.relative_to(H).as_posix())
 for fn in ('Makefile','run_round90.sh','SOURCE_MANIFEST.json','README.md','RELEASE_NOTES.md'):
  f=H/fn
  if f.is_file():z.write(f,'source/'+fn)
with zipfile.ZipFile(target) as z:assert z.testzip() is None
print('R90_FEEDBACK_ZIP:',target,flush=True)

#!/usr/bin/env python3
"""Compact feedback ZIP produced even on a failed gate."""
import os,zipfile,hashlib,json,sys,argparse
from pathlib import Path
H=Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser();p.add_argument('--exit-code',type=int,required=True);a=p.parse_args()
runpath=(H/'latest_run.txt').read_text().strip() if (H/'latest_run.txt').is_file() else ''
run=Path(runpath) if runpath else H/'results'
import datetime
stamp=datetime.datetime.utcnow().strftime('%Y%m%d_%H%M%S_%f')
zipname=H/'feedback'/f'Round9.1_Feedback_{stamp}.zip';zipname.parent.mkdir(parents=True,exist_ok=True)
with zipfile.ZipFile(zipname,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=6) as z:
 meta=dict(exit_code=a.exit_code,candidate_sha256=hashlib.sha256((H/'src/synth_round91.cpp').read_bytes()).hexdigest(),genuine_evaluator_claim=False,run_dir=str(run),hidden_test_claim=False)
 z.writestr('FEEDBACK_METADATA.json',json.dumps(meta,indent=2))
 for folder in ('src','submission','tools','tests','docs','evidence'):
  for f in (H/folder).rglob('*'):
   if not f.is_file() or f.name.endswith(('.pyc','.o','.a')) or '__pycache__' in f.parts:continue
   # Keep aggregate CSV and diagnostics, not millions of bytes of derived .net files.
   if f.suffix in ('.net',):continue
   if f.stat().st_size>1_000_000:continue
   z.write(f,'source/'+str(f.relative_to(H)))
 for f in [H/'SOURCE_MANIFEST.json',H/'Makefile',H/'run_round91.sh',H/'README.md',H/'RELEASE_NOTES.md',H/'hard_bank/FROZEN_MANIFEST.json']:
  if f.is_file():z.write(f,'source/'+str(f.relative_to(H)))
 if run.is_dir():
  for f in run.rglob('*'):
   if not f.is_file() or f.suffix=='.net' or f.stat().st_size>1_000_000:continue
   z.write(f,'experiment/'+str(f.relative_to(run)))
print('R91_FEEDBACK_ZIP:',zipname,flush=True)

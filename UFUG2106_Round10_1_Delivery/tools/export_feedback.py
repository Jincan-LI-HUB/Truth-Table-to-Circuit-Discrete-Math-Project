#!/usr/bin/env python3
import argparse,hashlib,json,zipfile
from pathlib import Path
from datetime import datetime,timezone
H=Path(__file__).resolve().parents[1]
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--exit-code',type=int,required=True);ap.add_argument('--run',type=Path,required=True);a=ap.parse_args()
 (H/'feedback').mkdir(exist_ok=True)
 stamp=datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S_%f')
 path=H/'feedback'/f'Round10.1_Feedback_{stamp}.zip'
 files=list(sorted((H/'src').glob('*')))+list(sorted((H/'trial_submission').glob('*')))+[H/'SOURCE_MANIFEST.json',H/'README.md',H/'RELEASE_NOTES.md']
 files+=[x for sub in ('docs','evidence') for x in sorted((H/sub).rglob('*')) if x.is_file()]
 if a.run.is_dir():
  files += [x for x in sorted(a.run.rglob('*')) if x.is_file() and (x.suffix in ('.csv','.json','.log','.txt'))]
 files=list(dict.fromkeys(x for x in files if x.is_file()))
 with zipfile.ZipFile(path,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=6) as z:
  z.writestr('FEEDBACK_METADATA.json',json.dumps({'exit_code':a.exit_code,'created_utc':stamp,'source_sha256':hashlib.sha256((H/'src/synth_round101.cpp').read_bytes()).hexdigest(),'hidden_tested':False},indent=2))
  for x in files:z.write(x,'bundle/'+str(x.relative_to(H))) if x.is_relative_to(H) else None
 assert zipfile.ZipFile(path).testzip() is None
 print('R101_FEEDBACK_ZIP:',path,flush=True)
if __name__=='__main__':main()

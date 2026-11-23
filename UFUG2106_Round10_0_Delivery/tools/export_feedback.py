#!/usr/bin/env python3
"""Always export evidence ZIP, including on nonzero exit."""
from pathlib import Path
import argparse,hashlib,json,zipfile,datetime
H=Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser();p.add_argument('--exit-code',type=int,required=True);a=p.parse_args()
runpath=H/'latest_run.txt'
run=Path(runpath.read_text().strip()) if runpath.is_file() else H/'results'
stamp=datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%d_%H%M%S_%f')
file=H/'feedback'/('Round10.0_Feedback_'+stamp+'.zip');file.parent.mkdir(parents=True,exist_ok=True)
with zipfile.ZipFile(file,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=6) as z:
    sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
    z.writestr('FEEDBACK_METADATA.json',json.dumps(dict(exit_code=a.exit_code,run_dir=str(run),source_sha256=sha(H/'src/synth_round100.cpp'),submission_sha256=sha(H/'submission/synth.cpp'),claims_hidden_testing=False),indent=2))
    for folder in ('src','submission','tests','tools','docs'):
        for f in (H/folder).rglob('*'):
            if not f.is_file() or f.suffix in ('.pyc','.o','.a') or '__pycache__' in f.parts or f.stat().st_size>1_000_000:continue
            z.write(f,'source/'+str(f.relative_to(H)))
    for f in (H/'SOURCE_MANIFEST.json',H/'Makefile',H/'run_round100.sh',H/'README.md',H/'RELEASE_NOTES.md'):
        z.write(f,'source/'+str(f.relative_to(H)))
    if run.is_dir():
        for f in run.rglob('*'):
            if not f.is_file() or f.suffix=='.net' or f.stat().st_size>1_000_000:continue
            z.write(f,'experiment/'+str(f.relative_to(run)))
print('R100_FEEDBACK_ZIP:',file,flush=True)

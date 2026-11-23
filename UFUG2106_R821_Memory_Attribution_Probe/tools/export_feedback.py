#!/usr/bin/env python3
"""Exports completed and incomplete experiment records, including failure logs."""
import argparse,time,hashlib,zipfile,json
from pathlib import Path
HOME=Path(__file__).resolve().parents[1]
def main():
    p=argparse.ArgumentParser();p.add_argument('--exit-code',type=int,default=0);a=p.parse_args()
    out=HOME/'feedback';out.mkdir(parents=True,exist_ok=True)
    target=out/f'R821_Memory_Attribution_Feedback_{time.strftime("%Y%m%d_%H%M%S")}.zip'
    manifest={'exit_code':a.exit_code,'diagnostic_only':True}
    with zipfile.ZipFile(target,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=7) as z:
        z.writestr('FEEDBACK_METADATA.json',json.dumps(manifest,indent=2))
        for dirname in ('src','tools','docs','logs','results'):
            for f in sorted((HOME/dirname).rglob('*')):
                if not f.is_file():continue
                if '__pycache__' in f.parts or f.suffix=='.pyc':continue
                if f.name.endswith('.netlist') and f.stat().st_size>5_000_000:continue
                z.write(f,f.relative_to(HOME))
        for f in ('README.md','run_probe.sh','MANIFEST.json'):
            if (HOME/f).is_file():z.write(HOME/f,f)
    print('MEMORY_ATTRIBUTION_FEEDBACK_ZIP:',target,flush=True)
if __name__=='__main__':main()

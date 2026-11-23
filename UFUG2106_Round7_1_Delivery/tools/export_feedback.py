#!/usr/bin/env python3
"""Always packages the latest full result directory, even on failed evaluations.
No private input data, evaluator executable, or compiled binaries are archived.
"""
from __future__ import annotations
import argparse,datetime,hashlib,json,os,platform,sys,zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]

def main():
    p=argparse.ArgumentParser();p.add_argument('--exit-code',type=int,default=0);args=p.parse_args()
    result=None;pointer=ROOT/'latest_run.txt'
    if pointer.is_file():
        maybe=Path(pointer.read_text().strip())
        if maybe.is_dir() and maybe.parent==(ROOT/'results').resolve():result=maybe
    stamp=result.name if result else datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    archive_dir=ROOT/'feedback';archive_dir.mkdir(parents=True,exist_ok=True)
    filename=archive_dir/f'Round7.1_Feedback_{stamp}.zip'
    selected=[]
    if result:
        selected += [(q,f'local_results/{q.relative_to(result).as_posix()}') for q in result.rglob('*') if q.is_file()]
    for f in ['SOURCE_MANIFEST.json','bootstrap_round71.py','bootstrap_round7.py','Makefile','README.md','run_round71.sh',
          'tests/test_exact_cover.py','tests/test_round71_patch.py','src/synth_round71.cpp',
          'src/typed_netgraph.hpp','src/polarity_mapper.hpp','src/algebraic_mapper.hpp',
          'docs/ROUND7_1_MATHEMATICAL_DESIGN.md','docs/ROUND7_TO_7_1_EVIDENCE.md',
          'docs/EXPERIMENT_PROTOCOL.md','docs/PAPER_RESEARCH_NOTES.md', 'docs/CHANGELOG.md']:
        q=ROOT/f
        if q.is_file():selected.append((q,'release_snapshot/'+f))
    f=ROOT/'results'/'latest_test.log'
    if f.is_file():selected.append((f,'local_results/test_log.txt'))
    metadata={'milestone':'7.1','exit_code':args.exit_code,'run_found':result is not None,
      'host_platform':platform.platform(),'python':platform.python_version(),
      'timestamp':datetime.datetime.now().isoformat(),
      'note':'Includes official evaluator CSVs if produced; never stores input truth tables.'}
    with zipfile.ZipFile(filename,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=6) as z:
        z.writestr('feedback_metadata.json',json.dumps(metadata,indent=2))
        for source,dest in selected:z.write(source,dest)
    with zipfile.ZipFile(filename) as z:assert z.testzip() is None
    print(f'\nFEEDBACK ZIP CREATED: {filename}',flush=True)
    print('Upload this single ZIP for the next analysis.',flush=True)
    return 0
if __name__=='__main__':raise SystemExit(main())

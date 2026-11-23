#!/usr/bin/env python3
"""Archive complete research feedback, including failures and source fingerprints.
Never puts input truth tables, evaluator executables, compiled binaries in ZIP.
"""
from __future__ import annotations
import argparse,datetime,json,platform,sys,zipfile
from pathlib import Path
HERE=Path(__file__).resolve().parents[1]

def main():
    p=argparse.ArgumentParser();p.add_argument('--exit-code',type=int,default=0)
    args=p.parse_args()
    found=None;pointer=HERE/'latest_run.txt'
    if pointer.is_file():
        possible=Path(pointer.read_text().strip()).resolve()
        if possible.is_dir() and possible.parent==(HERE/'results').resolve():found=possible
    stamp=found.name if found else datetime.datetime.now().strftime('%Y%m%d_%H%M%S_%f')
    archive=HERE/'feedback'/f'Round7.2_Feedback_{stamp}.zip';archive.parent.mkdir(parents=True,exist_ok=True)
    manifest={'milestone':'7.2','script_exit_code':args.exit_code,'results_available':found is not None,
       'host':platform.platform(),'python':platform.python_version(),
       'disclaimer':'Contains original official evaluator outputs, not an official score formula.',
       'contains_private_input_data':False}
    selected=[]
    if found:
        selected.extend((q,'local_results/'+q.relative_to(found).as_posix()) for q in found.rglob('*') if q.is_file())
    lastlog=HERE/'results'/'latest_test.log'
    if lastlog.is_file():selected.append((lastlog,'local_results/test_log.txt'))
    files=['README.md','Makefile','run_round72.sh','bootstrap_round72.py',
      'bootstrap_round71.py','bootstrap_round7.py','SOURCE_MANIFEST.json',
      'src/synth_round72.cpp','src/typed_netgraph.hpp','src/polarity_mapper.hpp',
      'src/algebraic_mapper.hpp','tests/test_exact_cover.py','tests/test_round72_patch.py',
      'tests/test_critical_cases.py','tests/verify_netlist.py',
      'tools/run_benchmarks.py','tools/profile_critical.py','tools/export_feedback.py']
    selected.extend((HERE/q,'release_snapshot/'+q) for q in files if (HERE/q).is_file())
    selected.extend((q,'research_docs/'+q.name) for q in (HERE/'docs').glob('*.md'))
    with zipfile.ZipFile(archive,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=6) as z:
        z.writestr('feedback_metadata.json',json.dumps(manifest,indent=2))
        for file,arc in selected:z.write(file,arc)
    with zipfile.ZipFile(archive) as z:assert z.testzip() is None
    print('\nFEEDBACK ZIP CREATED:',archive,flush=True)
    print('Upload this single ZIP for the next Round 7.2 analysis.',flush=True)
    return 0
if __name__=='__main__':raise SystemExit(main())

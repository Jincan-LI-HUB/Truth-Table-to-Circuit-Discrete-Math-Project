#!/usr/bin/env python3
"""Fast independent two-case structural smoke test; not official runtime evidence."""
from pathlib import Path
import subprocess,sys,os,tempfile
HERE=Path(__file__).resolve().parents[1];ROOT=HERE.parent
sys.path.insert(0,str(HERE/'tests'))
from verify_netlist import run

def one(exe,case,env,tmp,name):
    out=tmp/(name+'.net')
    e=os.environ.copy()
    for k in ('UFUG_R71_POLICY','UFUG_R72_POLICY','UFUG_R71_TRACE','UFUG_R7_LEGACY_MERGE','UFUG_R7_LEGACY_COVER'):e.pop(k,None)
    e.update(env)
    p=subprocess.run([str(exe),str(case),str(out)],capture_output=True,text=True,env=e,timeout=15)
    assert p.returncode==0,(name,p.returncode,p.stderr)
    stats=run(case,out)
    assert stats['exhaustive'] and stats['matched']
    return stats

def main():
    old=ROOT/'UFUG2106_Round7_1_Delivery/build/synth_round71'
    new=HERE/'build/synth_round72'
    assert old.is_file() and new.is_file(),'Missing R7.1 or R7.2 executable'
    cases=[('stage1','case_020.txt'),('stage2','case_016.txt')]
    with tempfile.TemporaryDirectory(prefix='ufug_r72_critical_') as d:
        for st,file in cases:
            case=ROOT/'data'/st/file
            assert case.is_file(),case
            old_stats=one(old,case,{},Path(d),'r71_'+st)
            guard_stats=one(new,case,{'UFUG_R72_POLICY':'guard'},Path(d),'guard_'+st)
            short_stats=one(new,case,{'UFUG_R72_POLICY':'shortlist'},Path(d),'shortlist_'+st)
            assert old_stats['area']==guard_stats['area'] and old_stats['delay']==guard_stats['delay'],(st,old_stats,guard_stats)
            assert short_stats['area']<=old_stats['area'],(st,'area regression',old_stats,short_stats)
            assert short_stats['delay']<=old_stats['delay'],(st,'delay regression',old_stats,short_stats)
            print(f'PASS {st}/{file}: R71={old_stats["area"]}/{old_stats["delay"]}, '
                  f'R72 shortlist={short_stats["area"]}/{short_stats["delay"]}, exhaustive assignments={short_stats["assignments"]}',flush=True)
    return 0
if __name__=='__main__':raise SystemExit(main())

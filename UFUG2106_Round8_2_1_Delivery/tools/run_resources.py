#!/usr/bin/env python3
"""Direct OS-memory checks + exhaustive verification. Official evaluator remains authoritative."""
import argparse,csv,json,os,re,subprocess,sys,time
from pathlib import Path
H=Path(__file__).resolve().parents[1]

def run_cmd(args,log,timeout=120):
    z=subprocess.run(args,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True,errors='replace',timeout=timeout)
    log.write_text(z.stdout,encoding='utf8')
    return z

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--results',type=Path,required=True)
    ap.add_argument('--quick',action='store_true');ap.add_argument('--official',action='store_true')
    a=ap.parse_args();out=a.results/'resource_tests';out.mkdir(parents=True,exist_ok=True)
    program=H/'build/synth_round821';verifier=H/'build/verify_exhaustive'
    gen=H/'tests/generate_resource_cases.py'
    kinds=['wire','xor2','and_all'] if a.quick else ['wire','not_wire','constant_one','xor2','majority3','multi','four_var','parity_all','and_all','or_all']
    records=[]
    for kind in kinds:
        testdir=out/kind;testdir.mkdir(exist_ok=True)
        test=testdir/'case_001.txt';net=testdir/'case_001.netlist'
        target=40 if kind=='parity_all' else 10
        cp=run_cmd([sys.executable,str(gen),str(test),'--n','20','--kind',kind,'--ram','9000','--limit','0','--target',str(target)],testdir/'generate.log')
        if cp.returncode:raise RuntimeError(f'failed to generate {kind}')
        peakfile=testdir/'peak_rss.log'
        started=time.monotonic()
        # The C++ wrapper forks from a small process. Python wait4 may report
        # Python's high pre-exec RSS as the peak due to fork copy-on-write.
        runner=H/'build/peak_runner'
        child=run_cmd([str(runner),str(program),str(test),str(net)],
                      testdir/'synthesis.log')
        match=re.search(r'R821_PEAK_RSS_KIB=(\d+)',child.stdout)
        peak=int(match.group(1)) if match else None
        peakfile.write_text(f'R821_PEAK_RSS_KIB={peak} R821_WALL_S={time.monotonic()-started:.6f} EXIT={child.returncode}\n')
        veri=None
        if child.returncode==0 and net.exists():
            check=run_cmd([str(verifier),str(test),str(net)],testdir/'verify.log')
            veri=check.returncode==0
        item={'kind':kind,'target':target,'ram_limit_kib':9000,'peak_rss_kib':peak,
              'synth_exit':child.returncode,'exhaustive':veri,'compliant':child.returncode==0 and peak is not None and peak<=9000 and veri is True}
        records.append(item)
        print('RESOURCE',kind,'PASS' if item['compliant'] else 'FAIL','peak_kib=',peak,flush=True)
        if not item['compliant']:
            (out/'direct_summary.json').write_text(json.dumps(records,indent=2)+'\n')
            raise RuntimeError(f'Resource check failed for {kind}: {item}')
        if a.official and kind in {'wire','xor2','multi','and_all'}:
            evaluator=H.parent/'evaluator'
            if not evaluator.exists():raise RuntimeError('Missing official evaluator for resource tests')
            report=testdir/'official.csv'
            if report.exists():report.unlink()
            z=run_cmd([str(evaluator),str(program),str(testdir),'--report',str(report)],testdir/'official.log',timeout=360)
            # The evaluator will see only the .txt input (not the .netlist or logs).
            if z.returncode!=0 or not report.exists():raise RuntimeError(f'Official resource evaluator failed for {kind}')
            with report.open() as f:rows=list(csv.DictReader(f))
            if len(rows)!=1 or rows[0]['status']!='PASS' or rows[0]['target_met']!='yes':
                raise RuntimeError(f'Official memory case not PASS: {kind}: {rows}')
            item['official_pass']=True
            print('RESOURCE_OFFICIAL',kind,'PASS',flush=True)
    (out/'direct_summary.json').write_text(json.dumps(records,indent=2)+'\n')
    return 0
if __name__=='__main__':
    try:raise SystemExit(main())
    except Exception as e:print('RESOURCE_TEST_ERROR:',repr(e),flush=True);raise

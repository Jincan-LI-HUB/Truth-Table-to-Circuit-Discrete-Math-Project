#!/usr/bin/env python3
"""Stage 1 writing-package provenance audit (Python stdlib only).

With --source-dir: reconstruct published CSVs from the frozen nine local-results ZIPs
and compare them exactly to the CSVs shipped in the manuscript.
Without --source-dir: validate the shipped CSVs and source/raw checksum manifests.
Optional --freeze-dir confirms the separately stored frozen C++ source snapshot.
Outputs one read-only JSON report at --report. Never changes benchmark data.
"""
from __future__ import annotations
import argparse, csv, hashlib, json, pathlib, subprocess, sys, tempfile, collections

p=argparse.ArgumentParser()
p.add_argument('--source-dir',type=pathlib.Path,default=None)
p.add_argument('--freeze-dir',type=pathlib.Path,default=None)
p.add_argument('--report',type=pathlib.Path,default=None)
args=p.parse_args()
ROOT=pathlib.Path(__file__).resolve().parents[2]
DATA=ROOT/'shared'/'data'
failures=[];checks=[]
def check(name, passed, detail=None):
    checks.append({'check':name,'passed':bool(passed),'detail':detail})
    if not passed: failures.append(name)

def digest(p: pathlib.Path): return hashlib.sha256(p.read_bytes()).hexdigest()

def read_rows(p: pathlib.Path):
    with p.open(encoding='utf-8-sig',newline='') as f: return list(csv.DictReader(f))

# Canonical released set: 25 case IDs, one unique row per case.
expected={f'case_{i:03d}.txt' for i in range(1,26)}
official=list(DATA.glob('official_round_*.csv'))
check('9 separately archived selected official CSVs present',len(official)==9,len(official))
for f in sorted(official):
    try:
        rows=read_rows(f)
        case_ids=[r['case'] for r in rows]
        ok=(len(rows)==25 and set(case_ids)==expected and len(set(case_ids))==25
            and all(r['status'].strip()=='PASS' for r in rows)
            and all(r['target_met'].strip().lower()=='true' or r['target_met'].strip().lower()=='false' for r in rows)
            and all(int(r['area'])>=0 and int(r['delay'])>=0 and float(r['runtime_ms'])>=0 for r in rows))
        check('official file schema + complete case set: '+f.name,ok)
    except Exception as e:check('official file schema + complete case set: '+f.name,False,str(e))
try:
    r=read_rows(DATA/'official_round_5_1.csv')
    check('R5.1 selected area = 529014',sum(int(x['area']) for x in r)==529014)
    check('R5.1 25 target met',sum(x['target_met'].strip().lower()=='true' for x in r)==25)
except Exception as e:check('R5.1 numeric results',False,str(e))

# Raw evidence records: explicit original bytes and declared origins.
raw=json.loads((DATA/'raw_evidence'/'RAW_EVIDENCE_CHECKSUMS.json').read_text())
for name,m in raw.items():
    f=ROOT/m['package_path']
    check('raw evidence SHA-256: '+name,f.is_file() and digest(f)==m['sha256'])

freeze=json.loads((DATA/'raw_evidence'/'stage1_round51_research_freeze_manifest.json').read_text())
check('freeze identity', freeze['source_sha256']=='cf90d0b110e6f45d1d508db351c95f10e7d704824fc34e17e6a5f5b783e20759')
if args.freeze_dir:
    for record in freeze['files']:
        f=args.freeze_dir/record['path']
        check('frozen source file SHA-256: '+record['path'],f.is_file() and digest(f)==record['sha256'])

if args.source_dir:
    manifest=read_rows(DATA/'source_manifest.csv')
    for m in manifest:
        f=args.source_dir/m['source_zip']
        check('original run archive SHA-256: '+m['round'],f.is_file() and digest(f)==m['sha256'])
    if not failures:
        with tempfile.TemporaryDirectory(prefix='stage1_evidence_audit_') as td:
            cmd=[sys.executable,str(ROOT/'shared'/'scripts'/'extract_evidence.py'),
                 '--source-dir',str(args.source_dir),'--out-dir',td]
            proc=subprocess.run(cmd,capture_output=True,text=True,timeout=180)
            check('extraction script completed',proc.returncode==0,proc.stderr[:800] if proc.returncode else None)
            if proc.returncode==0:
                for candidate in sorted(pathlib.Path(td).glob('*.csv')):
                    target=DATA/candidate.name
                    check('re-extracted CSV byte-identical: '+candidate.name,
                          target.is_file() and candidate.read_bytes()==target.read_bytes())

report={'status':'PASS' if not failures else 'FAIL', 'checks':len(checks),
        'passed':sum(x['passed'] for x in checks), 'failed':failures,
        'source_dir':str(args.source_dir) if args.source_dir else 'not supplied (historical run ZIP reproduction not attempted)',
        'freeze_dir':str(args.freeze_dir) if args.freeze_dir else 'not supplied (frozen source hash check not attempted)',
        'details':checks}
if args.report:
    args.report.parent.mkdir(parents=True,exist_ok=True)
    args.report.write_text(json.dumps(report,indent=2,ensure_ascii=False)+'\n')
print(f"{report['status']}: {report['passed']}/{report['checks']} checks; failed={len(failures)}")
if failures:print('\n'.join(failures))
sys.exit(1 if failures else 0)

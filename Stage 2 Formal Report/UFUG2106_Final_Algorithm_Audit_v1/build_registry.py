#!/usr/bin/env python3
import csv,hashlib,json,pathlib,zipfile
D=pathlib.Path(__file__).resolve().parent
sources=[]
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for part in iter(lambda:f.read(1048576),b''):h.update(part)
 return h.hexdigest()
def add(path,version,role,verification,origin):
 p=D/path
 if not p.exists(): print('MISSING',p);return
 sources.append({'version':version,'role':role,'relative_path':str(path),'sha256':sha(p),'size_bytes':p.stat().st_size,'verification':verification,'origin':origin})
add(pathlib.Path('stage1_zeyun/UFUG2106_Stage1/src/synth.cpp'),'Z1 submitted','formal Stage 1 implementation','extracted original RAR; SHA-256 verified; compiled + smoke tested','UFUG2106_Stage1_submitted_by_Zeyun_DU.rar')
add(pathlib.Path('stage1_zeyun/UFUG2106_Stage1/README.md'),'Z1 submitted','submitted source README','extracted original RAR','UFUG2106_Stage1_submitted_by_Zeyun_DU.rar')
for p in sorted((D/'primary/03_frozen_candidate/submission').iterdir()):
 if p.is_file():add(p.relative_to(D),'R10.0 frozen independent candidate','final candidate implementation / include', 'verified against official-feedback archived source; R10 synth.cpp compiled', 'Stage2_Final_Evidence_20261122T135755Z.zip')
add(pathlib.Path('primary/03_frozen_candidate/README.md'),'R10.0 frozen independent candidate','candidate release status and testing notes','extracted primary evidence archive','Stage2_Final_Evidence_20261122T135755Z.zip')
add(pathlib.Path('primary/00_specification/Final_Project.pdf'),'assignment','authoritative requirements','direct content inspected','Stage2_Final_Evidence_20261122T135755Z.zip')
with (D/'SOURCE_REGISTRY.csv').open('w',newline='') as f:
 w=csv.DictWriter(f,fieldnames=list(sources[0].keys()));w.writeheader();w.writerows(sources)
# archive SHA vs original collector manifest
manifest=json.loads((D/'primary/MANIFEST.json').read_text())
registry=[]; mismatches=[]
for record in manifest['files']:
 p=D/'primary'/record['archive_path']
 status='VERIFIED' if p.is_file() and sha(p)==record['sha256'] else 'MISMATCH_OR_MISSING'
 if status!='VERIFIED':mismatches.append(record['archive_path'])
 registry.append({'archive_path':record['archive_path'],'original_path':record['source_path'],'expected_sha256':record['sha256'],'observed_sha256':sha(p) if p.is_file() else None,'status':status})
with (D/'EVIDENCE_REGISTER.csv').open('w',newline='') as f:
 w=csv.DictWriter(f,fieldnames=list(registry[0].keys()));w.writeheader();w.writerows(registry)
(D/'PROVENANCE_CHECK.json').write_text(json.dumps({'primary_manifest_entries':len(registry),'verified':len(registry)-len(mismatches),'mismatches':mismatches,'r100_source_sha256':sha(D/'primary/03_frozen_candidate/submission/synth.cpp'),'zeyun_stage1_source_sha256':sha(D/'stage1_zeyun/UFUG2106_Stage1/src/synth.cpp')},indent=2))
# official feedback r100 default: recompute from original csv rows
zpath=D/'primary/02_official_feedback/r100/Round10.0_Feedback_20261122_121200_917768.zip'
import statistics
out=[]
with zipfile.ZipFile(zpath) as z:
 for stage in [1,2]:
  for run in [1,2]:
   nm=f'experiment/official/stage{stage}_run{run}_r100_default.csv'
   rows=list(csv.DictReader(z.read(nm).decode().splitlines()))
   out.append({'stage':stage,'run':run,'source_member':nm,'case_count':len(rows),'PASS':sum(x['status']=='PASS' for x in rows),'target_met':sum(x['target_met']=='yes' for x in rows),'area_sum':sum(int(x['area']) for x in rows),'delay_sum':sum(int(x['delay']) for x in rows),'median_runtime_ms':statistics.median(float(x['runtime_ms']) for x in rows)})
with (D/'R100_FEEDBACK_RECOUNT.csv').open('w',newline='') as f:
 w=csv.DictWriter(f,fieldnames=list(out[0].keys()));w.writeheader();w.writerows(out)
print('SOURCE_COUNT',len(sources),'MANIFEST_VERIFIED',len(registry)-len(mismatches),'/',len(registry),'R100_FEEDBACK',out)

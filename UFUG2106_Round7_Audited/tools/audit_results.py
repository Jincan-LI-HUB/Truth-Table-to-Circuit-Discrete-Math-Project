#!/usr/bin/env python3
"""Post-process the user's official evaluator reports without inventing scores.

Produces a per-case comparison, an ablation summary, and a reproducible audit report.
Does not run an evaluator or assume missing cases are zero-area circuits.
"""
from __future__ import annotations
import argparse,csv,json,math,statistics
from pathlib import Path

DELIVERY=Path(__file__).resolve().parents[1]
EXPECTED=('default','legacy_merge','legacy_cover','legacy_both')

def readcsv(p:Path):
    with p.open(newline='',encoding='utf-8') as f:return {r['case']:r for r in csv.DictReader(f)}

def number(s):
    try:return float(s)
    except (ValueError,TypeError):return None

def output_csv(path,records,fields):
    with path.open('w',newline='',encoding='utf-8') as f:
        writer=csv.DictWriter(f,fieldnames=fields,extrasaction='ignore')
        writer.writeheader();writer.writerows(records)

def getlatest(root):
    candidates=sorted(p for p in (root/'results'/'round7').glob('*/summary.json'))
    if not candidates:raise SystemExit('No results/*/summary.json. Run the official paired evaluator first.')
    return candidates[-1].parent

def main():
    a=argparse.ArgumentParser()
    a.add_argument('--result-dir',type=Path)
    opt=a.parse_args()
    folder=opt.result_dir or getlatest(DELIVERY)
    folder=folder.resolve()
    meta=json.loads((folder/'summary.json').read_text())
    indexed={};
    for entry in meta['runs']:
        case_csv=folder/Path(entry['csv']).name
        if not case_csv.is_file():raise SystemExit(f'Missing expected official CSV: {case_csv}')
        key=(entry['iteration'],entry['stage'],entry['variant'])
        indexed[key]=readcsv(case_csv)
    comparison=[];aggregate=[]
    for (iteration,stage,variant),data in sorted(indexed.items()):
        if variant=='round51':continue
        reference=indexed.get((iteration,stage,'round51'))
        if reference is None: reference=readcsv(DELIVERY/'results'/'baseline'/f'round51_{stage}.csv')
        common=[]
        failures=[]
        n_better=n_worse=n_equal=0
        for case in sorted(set(reference)|set(data)):
            old=reference.get(case,{})
            new=data.get(case,{})
            status_old=old.get('status','MISSING');status_new=new.get('status','MISSING')
            area_old=number(old.get('area'));area_new=number(new.get('area'))
            delay_old=number(old.get('delay'));delay_new=number(new.get('delay'))
            time_old=number(old.get('runtime_ms'));time_new=number(new.get('runtime_ms'))
            valid=status_old=='PASS' and status_new=='PASS'
            ratio=(time_new/time_old if valid and time_old and time_new is not None else None)
            area_ratio=(area_new/area_old if valid and area_old and area_new is not None else None)
            comparison.append({'run':iteration,'stage':stage,'variant':variant,'case':case,
              'r51_status':status_old,'variant_status':status_new,'r51_area':area_old,
              'variant_area':area_new,'area_delta':area_new-area_old if valid else '',
              'r51_delay':delay_old,'variant_delay':delay_new,
              'r51_runtime_ms':time_old,'variant_runtime_ms':time_new,
              'runtime_ratio':round(ratio,6) if ratio is not None else '',
              'area_ratio':round(area_ratio,8) if area_ratio is not None else ''})
            if valid:
                common.append((case,area_old,area_new,delay_old,delay_new,time_old,time_new))
                if area_new<area_old:n_better+=1
                elif area_new>area_old:n_worse+=1
                else:n_equal+=1
            if status_new!='PASS':failures.append(case)
        ratios=[new/old for _,_,_,_,_,old,new in common if old and new]
        meanratio=math.exp(statistics.mean(map(math.log,ratios))) if ratios else None
        aggregate.append({'run':iteration,'stage':stage,'variant':variant,
          'pass':sum(x.get('status')=='PASS' for x in data.values()),
          'cases':len(data),'targets':sum(x.get('target_met')=='yes' for x in data.values()),
          'paired_pass':len(common),'area_sum_valid':sum(int(x['area']) for x in data.values() if x.get('status')=='PASS'),
          'area_sum_complete':sum(x.get('status')=='PASS' for x in data.values())==len(data),
          'area_improved':n_better,'area_equal':n_equal,'area_regressed':n_worse,
          'runtime_geomean_ratio_common_pass':round(meanratio,6) if meanratio is not None else '',
          'failures':';'.join(failures)})
    summary_fields=['run','stage','variant','pass','cases','targets','paired_pass','area_sum_valid','area_sum_complete','area_improved','area_equal','area_regressed','runtime_geomean_ratio_common_pass','failures']
    case_fields=['run','stage','variant','case','r51_status','variant_status','r51_area','variant_area','area_delta','r51_delay','variant_delay','r51_runtime_ms','variant_runtime_ms','runtime_ratio','area_ratio']
    output_csv(folder/'ablation_summary.csv',aggregate,summary_fields)
    output_csv(folder/'casewise_comparison.csv',comparison,case_fields)
    default=[row for row in aggregate if row['variant']=='default']
    pass_gate=bool(default) and all(r['pass']==25 and r['targets']==25 for r in default)
    complete_ablation=all((i,s,v) in indexed for i in sorted({key[0] for key in indexed}) for s in ('stage1','stage2') for v in EXPECTED)
    lines=['# Round 7 — Official Result Audit', '',f'- Result folder: `{folder.name}`',
      f'- Complete 4-mode official ablation: **{complete_ablation}**',
      f'- Default Round 7 meets 50/50 PASS and all targets in each available run: **{pass_gate}**','',
      '## Official per-stage comparisons','','| Run | Stage | Variant | PASS | Area Sum of PASS | Common PASS | Area improved/equal/regressed | Runtime G-mean ratio |',
      '|---:|---|---|---:|---:|---:|---|---:|']
    for r in aggregate:
        lines.append(f"| {r['run']} | {r['stage']} | {r['variant']} | {r['pass']}/{r['cases']} | {r['area_sum_valid']}{'' if r['area_sum_complete'] else ' (partial)'} | {r['paired_pass']} | {r['area_improved']}/{r['area_equal']}/{r['area_regressed']} | {r['runtime_geomean_ratio_common_pass']} |")
    lines+=['','## Notes','','- Missing runtime or area for a FAIL is kept missing, **not zero**.',
      '- Runtime is measured by the official evaluator. Ratios use only cases PASS in both programs.',
      '- Two repeats are insufficient to establish statistical stability near a 100ms deadline.',
      '- Equal area and delay do not prove identical gate-by-gate netlists.','']
    if not complete_ablation:lines.append('**Official ablations are incomplete. Rerun `bash UFUG2106_Round7_Delivery/run_round7.sh` with this audited package, or explicitly use `--ablate`.**')
    (folder/'AUDIT_REPORT.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
    print('Wrote',folder/'ablation_summary.csv',folder/'casewise_comparison.csv',folder/'AUDIT_REPORT.md',sep='\n  ')
    print('Complete ablation:',complete_ablation,'Release gate:',pass_gate)

if __name__=='__main__':main()

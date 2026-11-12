#!/usr/bin/env python3
"""Summarize an actual paired Round 4.1 / Round 5 official-evaluator reproduction."""
import csv, json, statistics, sys
from pathlib import Path


def load(path):
    with path.open(newline='', encoding='utf-8') as f:
        rows=list(csv.DictReader(f))
    if not rows or len(rows)!=len(set(x['case'] for x in rows)):
        raise ValueError('missing or duplicate case IDs: '+str(path))
    return {x['case']:x for x in rows}


def summary(rows):
    vals=list(rows.values())
    return dict(count=len(vals),pass_count=sum(x['status']=='PASS' for x in vals),
        target_met=sum(x['target_met'].lower()=='yes' for x in vals),
        area_sum=sum(int(x['area']) for x in vals),
        median_runtime_ms=round(statistics.median(float(x['runtime_ms']) for x in vals),3),
        max_runtime_ms=round(max(float(x['runtime_ms']) for x in vals),3),
        sum_runtime_ms=round(sum(float(x['runtime_ms']) for x in vals),3))


def main():
    run=Path(sys.argv[1]).resolve();n=25
    a=load(run/'reference'/'official.csv');b=load(run/'round5'/'official.csv')
    if len(a)!=n or set(a)!=set(b):
        raise ValueError('case sets differ or not exactly 25')
    pair=[];matches=0;metric_changes=[]
    for case in sorted(a):
        x,y=a[case],b[case]
        f1=run/'reference'/'outputs'/case.replace('.txt','.output.txt')
        f2=run/'round5'/'outputs'/case.replace('.txt','.output.txt')
        equal=f1.read_bytes()==f2.read_bytes()
        matches+=equal
        if (x['area'],x['delay'])!=(y['area'],y['delay']):metric_changes.append(case)
        tx,ty=float(x['runtime_ms']),float(y['runtime_ms'])
        pair.append(dict(case=case,baseline_area=x['area'],round5_area=y['area'],
            baseline_delay=x['delay'],round5_delay=y['delay'],
            baseline_runtime_ms=x['runtime_ms'],round5_runtime_ms=y['runtime_ms'],
            saved_ms=f'{tx-ty:.3f}',runtime_reduction_pct=f'{100*(tx-ty)/tx:.2f}' if tx else '0',
            netlist_byte_identical=str(equal)))
    with (run/'per_case_comparison.csv').open('w',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f,fieldnames=pair[0].keys());w.writeheader();w.writerows(pair)
    s1,s2=summary(a),summary(b)
    result={'round4_1_reference':s1,'round5':s2,'byte_identical':matches,
            'metric_changes':metric_changes,'all_pass':s1['pass_count']==25 and s2['pass_count']==25,
            'all_targets':s1['target_met']==25 and s2['target_met']==25,
            'same_area_delay':not metric_changes,'same_netlists':matches==25,
            'median_runtime_reduction_pct':round(100*(1-s2['median_runtime_ms']/s1['median_runtime_ms']),2)}
    (run/'summary.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    ready=run/'report_ready';ready.mkdir(exist_ok=True)
    md=[ '# Round 5 — Local Reproduction Results', '',
         '> Local results, not historical/container results. Both executables were compiled in this run.', '',
         '| Metric | Frozen Round 4.1 Balanced | Round 5 |','|---|---:|---:|']
    for key,title in [('pass_count','Official PASS'),('target_met','Target Delay Met'),('area_sum','Area sum'),
                    ('median_runtime_ms','Median runtime (ms)'),('max_runtime_ms','Maximum runtime (ms)'),
                    ('sum_runtime_ms','Total runtime over cases (ms)')]:
        md.append(f'| {title} | {s1[key]} | {s2[key]} |')
    md += ['',f'- **Identical Netlists:** {matches}/25 files (byte-for-byte).',
           f'- **Area / Delay Changed Cases:** {metric_changes or "none"}.',
           f'- **Median Runtime Reduction:** {result["median_runtime_reduction_pct"]}%.',
           '- Runtime numbers are separate wall-clock measurements performed by the official evaluator; CPU and filesystem conditions can influence them.',
           '- **Search-time caveat:** faster synthesis can complete a different number of candidates before a time-based cutoff. Byte identity is an empirical check, not a guaranteed invariant of the whole executable.',
           '- The netlist checker is exhaustive only for small input counts (n≤13), otherwise deterministically sampled; the official evaluator separately checks all published cases.',
           '', '## Per-case timing', '',
           '| Case | Round 4.1 (ms) | Round 5 (ms) | Reduction |','|---|---:|---:|---:|']
    for z in pair:md.append(f'| {z["case"]} | {z["baseline_runtime_ms"]} | {z["round5_runtime_ms"]} | {z["runtime_reduction_pct"]}% |')
    md += ['', '## Evidence', '',
           '- `../reference/` and `../round5/`: official CSVs, evaluator logs, saved Netlists.',
           '- `../round5/independent_verification.log`: independent verifier output.',
           '- `../source_snapshot/`: compiled C++ and headers, Makefile, and scripts.',
           '- `../profiles/`: optional stage timings on representative cases.',
           '- `../environment.txt` and `../case_sha256.txt`: environment, sources, inputs, evaluator provenance.',
           '- `../per_case_comparison.csv`, `../summary.json`: machine-readable local comparison.',
           '- `mathematical_design.md`: the formal invariance argument and cache conditions.', '']
    (ready/'local_reproduction_report.md').write_text('\n'.join(md),encoding='utf-8')
    print('Round 4.1:',s1)
    print('Round 5:',s2)
    print('Byte-identical netlists:',matches,'of 25')
    if not (result['all_pass'] and result['all_targets']):
        raise RuntimeError('Official correctness or Target Delay check failed; inspect report and CSV')
    if not result['same_netlists']:
        print('NOTE: Netlists differ on', metric_changes or f'{25-matches} case(s)',
              '— wall-clock search cutoff can change completed candidate set.')

if __name__=='__main__':main()

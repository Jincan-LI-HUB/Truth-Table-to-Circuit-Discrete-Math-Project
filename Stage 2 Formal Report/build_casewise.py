"""Regenerate the canonical 50-case Z1/R10 appendix from matched evidence."""
from pathlib import Path
import pandas as pd
R=Path(__file__).resolve().parent
D=pd.read_csv(R/'data/matched_case_metrics.csv')
D=D[(D['repeat']==1)&D['method_id'].isin(['Z1','S100'])].copy()
assert len(D)==100 and D[['case_id','method_id']].duplicated().sum()==0
assert set(D.method_id)=={'Z1','S100'}
assert D['passed'].eq(1).all() and D['target_met'].eq(1).all()
assert sorted(D['case_id'].unique())==[f'{bank}/case_{i:03d}.txt' for bank in ('stage1','stage2') for i in range(1,26)]
lines=[r'\\begin{longtable}{@{}llcrrrrrr@{}}',
 r'\\caption{All 50 released cases: first matched repeat. P/P denotes Z1 PASS / R10 PASS; both also meet each case\\textquotesingle s delay target. $A$ is charged gate area, $D$ is circuit delay, and $T$ is synthesis runtime in milliseconds.}\\label{tab:casewise}\\',
 r'\\toprule',
 r'Bank & Case & Status & $A_{\\mathrm{Z1}}$ & $D_{\\mathrm{Z1}}$ & $T_{\\mathrm{Z1}}$ & $A_{\\mathrm{R10}}$ & $D_{\\mathrm{R10}}$ & $T_{\\mathrm{R10}}$\\\\',
 r'\\midrule',r'\\endfirsthead',r'\\toprule',
 r'Bank & Case & Status & $A_{\\mathrm{Z1}}$ & $D_{\\mathrm{Z1}}$ & $T_{\\mathrm{Z1}}$ & $A_{\\mathrm{R10}}$ & $D_{\\mathrm{R10}}$ & $T_{\\mathrm{R10}}$\\\\',
 r'\\midrule',r'\\endhead']
for bank in ('stage1','stage2'):
 for i in range(1,26):
  key=f'{bank}/case_{i:03d}.txt'
  z=D[(D.case_id==key)&(D.method_id=='Z1')].iloc[0]
  r=D[(D.case_id==key)&(D.method_id=='S100')].iloc[0]
  area=lambda row:f'{int(row.area):,}'
  line=f'{"S1" if bank=="stage1" else "S2"} & {i:03d} & P/P & {area(z)} & {int(z.delay)} & {z.synth_runtime_ms:.1f} & {area(r)} & {int(r.delay)} & {r.synth_runtime_ms:.1f} '+r'\\'
  lines.append(line)
 if bank=='stage1':lines.append(r'\\midrule')
lines.extend([r'\\bottomrule',r'\\end{longtable}'])
# Escape the Python raw source's double-backslash delimiters into TeX literals.
result='\n'.join(lines)+'\n'
result=result.replace('\\\\', '\\')
# The last per-row TeX newline must be two slashes; lines above doubled deliberately.
# Rebuild delimiters by line type.
fixed=[]
for line in result.splitlines():
 if line.startswith('Bank &') or line.startswith('S1 &') or line.startswith('S2 &') or line.startswith('\\caption'):
  if line.endswith('\\') and not line.endswith('\\\\'):
   line += '\\'
 fixed.append(line)
result='\n'.join(fixed)+'\n'
# Avoid relying on textquotesingle / newer quote macros for this caption.
result=result.replace(r'\textquotesingle s', "'s")
assert result.count('P/P &')==50 and 'Status &' in result
(R/'casewise.tex').write_text(result)
print('Rebuilt 50 first-repeat cases, 100 PASS and 100 target-met statuses.')

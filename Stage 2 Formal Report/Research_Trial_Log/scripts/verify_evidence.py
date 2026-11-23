"""Recompute selected displayed values from bundled evidence CSVs.
Does not rerun the original algorithms. Fails loudly on changed inputs.
"""
from pathlib import Path
import pandas as pd
R=Path(__file__).resolve().parents[1]
d=R/'data'
a=pd.read_csv(d/'all_runs_reverified.csv')
m=pd.read_csv(d/'selected_round_milestones.csv')
r=pd.read_csv(d/'raw_feedback_verified.csv')
p=pd.read_csv(d/'raw_controlled_pairs_verified.csv')
c=pd.read_csv(d/'matched_case_metrics.csv')
assert len(a)==1706 and a['recomputed_match'].all() and a['sha256_match'].all()
assert len(m)==32 and len(r)==196 and len(p)==56 and len(c)==300
q=m[m.bank=='stage2'].set_index('round')
assert int(q.loc['R7.2','area_pass'])==508535 and int(q.loc['R10.0','area_pass'])==493965
assert int(q.loc['R7','pass_count'])==24 # do not equate passing-case area with a full-25 result
x=p[(p.group=='r86')&(p.bank.isin(['stage1','stage2']))&(p.repeat==1)].groupby('candidate').area_saved.sum()
for name,val in {'r86_extra_sop':2844,'r86_combined':2844,'r86_time_reclaim':0,'r86_reverse':20}.items():
    assert x[name]==val,(name,x[name])
rr=p[(p.group=='r91')&(p.bank.isin(['stage1','stage2']))&(p.repeat==1)].groupby('candidate')[['wins','area_saved']].sum()
assert list(rr.loc['r91_library'])==[15,663]
assert list(rr.loc['r91_repeat_sop'])==[8,1587]
assert list(rr.loc['r91_repeat_shannon'])==[5,879]
z=p[(p.group=='r100')&(p.bank.isin(['stage1','stage2']))&(p.repeat==1)&(p.candidate=='r100_default')]
assert int(z.area_saved.sum())==1587 and int(z.wins.sum())==8
first=c[c.repeat==1].pivot(index='case_id',columns='method_id',values='area').dropna(subset=['Z1','S100'])
diff=first.Z1-first.S100
assert int(diff.sum())==124697
assert int(diff[diff>0].sum())==160696
assert int(diff[diff<0].sum())==-35999
assert (diff>0).sum()==18 and (diff<0).sum()==32
assert round(((first.S100/first.Z1-1).median())*100,4)==3.6944
assert len(pd.read_csv(d/'casewise_milestone_relative_area.csv'))==25
print('VERIFIED: historical index, native feedback, factorial, R9.1 policy, R10.0 sparse gains, matched ranking and 25-case longitudinal matrix')

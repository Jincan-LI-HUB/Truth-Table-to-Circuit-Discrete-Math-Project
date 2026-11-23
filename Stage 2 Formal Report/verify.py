"""Fail-fast numerical checks for the figures and main manuscript, using only bundled CSVs."""
from pathlib import Path
import pandas as pd
R=Path(__file__).resolve().parent
D=pd.read_csv(R/'data/matched_case_metrics.csv')
for rep in [1,2]:
 p=D[D.repeat==rep].pivot(index='case_id',columns='method_id',values=['area','passed','target_met'])
 assert len(p)==50 and int(p['passed'].Z1.sum())==50 and int(p['passed'].S100.sum())==50
 assert int(p['target_met'].Z1.sum())==50 and int(p['target_met'].S100.sum())==50
 assert int(p['passed'].J51.sum())==49
 z=p['area'].Z1.sum(); s=p['area'].S100.sum()
 assert (int(z),int(s))==({1:(1144244,1019547),2:(1145191,1019883)}[rep])
 print(f'matched repeat {rep}: Z1={int(z):,}, R10={int(s):,}, saved={int(z-s):,}')
P=D.query('repeat==1').pivot(index='case_id',columns='method_id',values=['area','synth_runtime_ms'])
d=P['area'].Z1-P['area'].S100
assert int((d>0).sum())==18 and int((d<0).sum())==32
assert int(d.clip(lower=0).sum())==160696 and int(-d.clip(upper=0).sum())==35999
assert int((P['synth_runtime_ms'].S100<P['synth_runtime_ms'].Z1).sum())==49
assert float(d.median())==-54.5
for bank in ('stage1','stage2'):
    z=d[d.index.str.startswith(bank+'/')]
    assert (int((z>0).sum()),int((z<0).sum()))==(9,16)
    area_split={
        'stage1':(81805,18364,63441),
        'stage2':(78891,17635,61256),
    }[bank]
    assert (int(z.clip(lower=0).sum()),int(-z.clip(upper=0).sum()),int(z.sum()))==area_split
assert int(d.max())==39516 and int(d.min())==-8003
assert int(d.nlargest(3).sum())==94004  # Three largest gains = 58.5% of gross wins.
print('first repeat: benefits=18, regressions=32, positive=160,696, negative=35,999')
Q=pd.read_csv(R/'data/quota_factorial.csv').query('repeat==1')
assert (int(Q.extra_roots.sum()),int(Q.reclaim.sum()),int(Q.both.sum()),int(Q.reverse.sum()))==(2844,0,2844,20)
R90=pd.read_csv(R/'data/official_r90_r100_casewise.csv').query('run==1')
R90['id']=R90.bank+'/'+R90.case
A=R90.pivot(index='id',columns='method',values='area')
q=A.r90_frozen-A.r100_default
assert len(q)==50 and int(q.sum())==1587 and int((q>0).sum())==8 and int((q<0).sum())==0
print('official R9/R10 paired first repeat: eight improvements; saved=1,587')
print('ALL VERIFIED')

# Verify the two explicitly documented truth-mask conventions against all rows.
for a in (0, 1):
 for b in (0, 1):
  for c in (0, 1):
   f = int(bool(b or ((not a) and c)))
   if a == b == c == 0:
    mask_stage1 = mask_r10 = 0
   mask_stage1 |= f << (4*a + 2*b + c)
   mask_r10 |= f << (a + 2*b + 4*c)
assert mask_stage1 == 0xCE and mask_r10 == 0xDC
print('truth-mask conventions: MSB-first=0xCE, source LSB-first=0xDC')

# Both matched repeats preserve the same per-case area-gain sign pattern.
A = D.pivot(index='case_id', columns=['repeat','method_id'], values='area')
d1 = A[(1,'Z1')] - A[(1,'S100')]
d2 = A[(2,'Z1')] - A[(2,'S100')]
assert int(((d1 > 0) == (d2 > 0)).sum()) == 50
assert int((d2 > 0).sum()) == 18 and int((d2 < 0).sum()) == 32
assert int(d2.sum()) == 125308
print('two-repeat area-difference signs: 50/50 unchanged')

# Recompute the final policy comparison directly from archived native
# matched-case summaries, expressed per original 50 cases (100 / 2).
P=pd.read_csv(R/'data/final_policy_tradeoff.csv')
assert len(P)==6 and P.policy.nunique()==6 and (P.paired==100).all()
assert (P.penalty50 == -P.area_saved_total/2).all()
saved=P.set_index('policy')['penalty50'].to_dict()
assert (saved['r101_off'],saved['r101_cap40'],saved['r101_cap80'],saved['r101_budget45'])==(1587,1008,602,241)
ratios=P.set_index('policy')['runtime_median_ratio']
assert ratios['r101_off']<ratios['r101_cap40']<1 and ratios['r101_budget45']>1
print('paired final-policy trade-off: validated from 100 observations per policy')

# Keep the actual appendix headings and all 50 PASS rows aligned with its source.
A=(R/'casewise.tex').read_text()
assert A.count('Status &')==2 and A.count(' & P/P & ')==50
assert A.count('\\mathrm{Z1}')==6 and A.count('\\mathrm{R10}')==6
print('50-case appendix: headings and paired PASS rows checked')

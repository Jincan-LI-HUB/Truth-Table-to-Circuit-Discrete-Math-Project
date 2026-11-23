"""Complete cross-round evidence atlas (source-backed). Rebuild in-place.

Reads Stage 1 reference and Stage 2 audited historical run index; late R10.1
paired data come from ORIGINAL native feedback zip nested in the submitted
Stage2_Final_Evidence archive. Never substitute an incomplete 25-case
aggregate for a completed 25-case result.
"""
from pathlib import Path
import zipfile,io,json,re
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.ticker import FuncFormatter,MaxNLocator
R=Path(__file__).resolve().parents[1]
DATA=R/'data'; FIG=R/'figures'; FIG.mkdir(exist_ok=True)
PAL=json.loads((R/'palette.json').read_text())['colors']
INK='#293039';MUTED='#505964';GRID='#E6E7E8'
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10.5,'axes.titlesize':11.5,'axes.labelsize':10,'xtick.labelsize':9.3,'ytick.labelsize':9.1,'axes.edgecolor':INK,'axes.labelcolor':INK,'text.color':INK,'xtick.color':INK,'ytick.color':INK,'pdf.fonttype':42,'ps.fonttype':42,'savefig.facecolor':'white'})
def clean(ax,which='y'):
 ax.spines[['top','right']].set_visible(False);ax.grid(axis=which,color=GRID,lw=.6,zorder=0);ax.set_axisbelow(True)
def save(fig,name):
 fig.savefig(FIG/f'{name}.pdf',bbox_inches='tight',pad_inches=.17)
 fig.savefig(FIG/f'{name}.png',bbox_inches='tight',pad_inches=.17,dpi=175)
 plt.close(fig)

# The nine values below are taken directly from the supplied Stage 1 Final
# Research Trial Log's Table 3, p.17, with explicitly noted archival runs.
stage1=pd.DataFrame([
 ('R1',12,1103455),('R2',25,790243),('R3',25,533705),('R4',25,528910),
 ('R4.1 B',25,529014),('R5',25,529014),('R5.1',25,529014),
 ('R6.0',25,528738),('R6.1',25,528854)],columns=['version','target_met','area'])
stage1['pass']=25;stage1['bank']='stage1';stage1['provenance']='Stage 1 Research Trial Log v1.0, Table 3, archived designated run'
stage1.to_csv(DATA/'stage1_archival_area_milestones.csv',index=False)
fig,ax=plt.subplots(figsize=(10.1,3.5),layout='constrained')
x=np.arange(len(stage1)); y=stage1.area/1000
colors=[PAL['slate'],PAL['sage'],PAL['blue'],PAL['blue'],PAL['mint'],PAL['mint'],PAL['sage'],PAL['peach'],PAL['rose']]
for i,(a,c) in enumerate(zip(y,colors)):
 ax.bar(i,a,color=c,edgecolor=INK,lw=.65,width=.67,zorder=3)
 ax.text(i,a+12,f'{a:,.1f}',ha='center',va='bottom',fontsize=8.8,weight='medium')
ax.set_xticks(x,stage1.version);ax.set_ylim(0,1240);ax.set_ylabel('Stage 1 total weighted area (25 cases, thousands)');clean(ax)
ax.text(.02,.96,'R1: 12/25 delay targets met',transform=ax.transAxes,ha='left',va='top',fontsize=9.2,
 bbox=dict(fc='white',ec=PAL['stone'],pad=4))
ax.text(.98,.96,'All other selected versions: 25/25 PASS and target-met',transform=ax.transAxes,ha='right',va='top',fontsize=8.8,
 bbox=dict(fc='white',ec=PAL['stone'],pad=4))
save(fig,'09_stage1_complete_area_history')

# Stage2 16 chronological milestones (the complete source-backed selected
# checkpoint path; R7 fails one case and is excluded from full-bank curves).
m=pd.read_csv(DATA/'selected_round_milestones.csv'); s=m[m.bank=='stage2'].copy()
order=['R7','R7.1','R7.2','R8','R8.1','R8.2','R8.2.1','R8.3','R8.4','R8.5','R8.6','R8.7','R9.0','R9.1','R10.0','R10.1']
s['round']=pd.Categorical(s['round'],order,ordered=True);s=s.sort_values('round')
assert list(s['round'].astype(str))==order,(list(s['round']),order)
s[['round','policy','pass_count','target_count','area_pass','delay_pass','median_synth_ms','source_path']].to_csv(DATA/'stage2_full_milestone_trace.csv',index=False)
fig,axs=plt.subplots(3,1,figsize=(12.2,8.1),sharex=True,gridspec_kw={'height_ratios':[1.3,1.0,1.05]},layout='constrained')
xx=np.arange(len(s));full=s.pass_count.eq(25)&s.target_count.eq(25)
ax=axs[0];ax.plot(xx[full],s.loc[full,'area_pass']/1000,color=INK,lw=1.4,zorder=2)
ax.scatter(xx[full],s.loc[full,'area_pass']/1000,c=[PAL['blue'] if 4<=i<12 else PAL['sage'] for i in xx[full]],s=45,edgecolors=INK,lw=.7,zorder=3)
for nm in ['R7.2','R8.1','R8.2.1','R8.6','R9.0','R10.0']:
 i=order.index(nm); row=s.iloc[i]; shift= -1.3 if nm in ['R8.1','R8.2.1'] else 1.6
 ax.annotate(f'{int(row.area_pass):,}',(i,row.area_pass/1000),xytext=(0,13 if shift>0 else -15),textcoords='offset points',ha='center',fontsize=8)
ax.set_ylabel('Area / 1,000 (25-case total)');ax.set_ylim(490,516);clean(ax)
ax.annotate('R7: 24/25 PASS\nno full-bank area',xy=(0,507),xytext=(.3,512),arrowprops=dict(arrowstyle='-',color=INK),fontsize=9)
ax=axs[1];ax.plot(xx,s.delay_pass.values,marker='o',color=INK,lw=1.25,markersize=4.2,markerfacecolor=PAL['blue']);ax.scatter([0],[s.iloc[0].delay_pass],s=90,facecolors='white',edgecolors=INK,marker='x',zorder=6)
ax.set_ylabel('Sum circuit delay\n(PASS cases only)');clean(ax)
ax=axs[2];ax.plot(xx,s.median_synth_ms,marker='s',color=INK,lw=1.25,markersize=4.5,markerfacecolor=PAL['rose']);ax.set_ylabel('Median synthesis runtime\n(ms; archival)');clean(ax)
ax.set_xticks(xx,order,rotation=35,ha='right');ax.set_xlim(-.5,15.5);ax.set_xlabel('Selected historical candidate at each recorded Round (not a paired runtime experiment)')
fig.suptitle('Stage 2: quality, delay and search cost moved on different trajectories',fontsize=12.5,y=1.015)
save(fig,'10_stage2_complete_metric_trajectory')

# All tested configurations rather than selected winners: per (round,variant)
# aggregate all source-distinct archived reports. Complete 25/25 PASS and
# target 25/25 cases only receive valid area statistics. For incomplete
# records, counts are retained but area is missing, not coerced to 0.
d=pd.read_csv(DATA/'all_runs_reverified.csv');d=d[(d.bank=='stage2')&(d.cases==25)&d['round'].isin(order)].copy()
rows=[]
for (rnd,variant),g in d.groupby(['round','variant']):
 h=g[(g['pass']==25)&(g['target']==25)].copy()
 # Stable first observed *valid* report for diagram and provenance; all other
 # valid reports remain in the exported index as ranges and counts.
 h=h.sort_values(['original','run_id'])
 chosen=h.iloc[0] if len(h) else None
 rows.append(dict(round=rnd,variant=variant,archived_rows=len(g),distinct_reports=g.report_hash.nunique(),
  complete_rows=len(h), observed_fail_rows=int((g['pass']<25).sum()), observed_target_miss_rows=int(((g['pass']==25)&(g['target']<25)).sum()),
  area=np.nan if chosen is None else int(chosen.area),delay=np.nan if chosen is None else int(chosen.delay),
  median_ms=np.nan if chosen is None else float(chosen.median_ms),
  area_min=np.nan if not len(h) else int(h.area.min()),area_max=np.nan if not len(h) else int(h.area.max()),
  origin='' if chosen is None else chosen.original,report_hash='' if chosen is None else chosen.report_hash))
v=pd.DataFrame(rows);v['round']=pd.Categorical(v['round'],order,ordered=True);v=v.sort_values(['round','variant']);v.to_csv(DATA/'stage2_all_variant_index.csv',index=False)
assert len(v)>=100,len(v)
# The complete variant atlas is rendered as eight legible two-round pages,
# not as two unreadably dense pages. Its source is the audited CSV generated
# above, and it can also be rebuilt independently.
import subprocess,sys
subprocess.run([sys.executable,str(R/'scripts/build_variant_atlas.py')],check=True)

# Paired R10.1 native feedback: medians of matched runtime ratios and deltas
outer=R.parent/'Stage2_Final_Evidence_20261122T135755Z.zip'
if outer.exists():
 with zipfile.ZipFile(outer) as oz:
  native=next(t for t in oz.namelist() if '/r101/' in t and t.endswith('.zip'))
  with zipfile.ZipFile(io.BytesIO(oz.read(native))) as iz:
   summary=pd.read_csv(io.BytesIO(iz.read(next(t for t in iz.namelist() if t.endswith('paired_policy_summary.csv')))))
   pairs=pd.read_csv(io.BytesIO(iz.read(next(t for t in iz.namelist() if t.endswith('paired_runtime_area_delay.csv')))))
   # Recalculate from true 100 matched comparisons, don't trust display labels.
   chk=pairs.groupby('policy').agg(pair_count=('area_saved','size'),saved=('area_saved','sum'),median_ratio=('runtime_ratio','median')).reset_index()
   ss=summary.merge(chk,on='policy',validate='one_to_one')
   assert (ss['paired']==ss['pair_count']).all() and (ss['area_saved_total']==ss['saved']).all()
   assert np.allclose(ss.runtime_median_ratio,ss.median_ratio)
   summary.to_csv(DATA/'r101_native_paired_policy_summary.csv',index=False)
   pairs.to_csv(DATA/'r101_native_100_paired_case_observations.csv',index=False)
else:
 summary=pd.read_csv(DATA/'r101_native_paired_policy_summary.csv')
 pairs=pd.read_csv(DATA/'r101_native_100_paired_case_observations.csv')
 chk=pairs.groupby('policy').agg(pair_count=('area_saved','size'),saved=('area_saved','sum'),median_ratio=('runtime_ratio','median')).reset_index()
 ss=summary.merge(chk,on='policy',validate='one_to_one')
 assert (ss.paired==ss.pair_count).all() and (ss.area_saved_total==ss.saved).all()
 assert np.allclose(ss.runtime_median_ratio,ss.median_ratio)
# The repaired final-policy graphic uses two aligned axes with distinct
# area and paired runtime units, removing overlapping annotation near (1,0).
subprocess.run([sys.executable,str(R/'scripts/build_final_policy_chart.py')],check=True)
print('Stage 1 milestones',len(stage1),'Stage 2 rounds',len(s),'all variants',len(v),'R10.1 pairs',len(pairs))

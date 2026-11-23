"""Multiscale evidence plots for the combined Stage 1 + Stage 2 trial log.
Figures are exact descriptive transformations of archived summary CSVs. They
are not causal one-feature experiments and must not be described as such.
"""
from pathlib import Path
import json
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
ROOT=Path(__file__).resolve().parents[1]; OUT=ROOT/'figures';DATA=ROOT/'data'
COL=json.loads((ROOT/'palette.json').read_text())['colors']
DARK='#252B30'; GRID='#E8E2DB'
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':9,'axes.labelsize':9.5,'axes.titlesize':11,'xtick.labelsize':8.5,'ytick.labelsize':8.5,'axes.edgecolor':DARK,'axes.labelcolor':DARK,'text.color':DARK,'xtick.color':DARK,'ytick.color':DARK,'savefig.facecolor':'white','pdf.fonttype':42})
def save(fig,name):
    fig.savefig(OUT/name,bbox_inches='tight',pad_inches=.11)
    fig.savefig(OUT/name.replace('.pdf','.png'),dpi=190,bbox_inches='tight',pad_inches=.11)
    plt.close(fig)
def clean(ax):
    ax.grid(axis='y',color=GRID,linewidth=.75,zorder=0)
    for p in ('top','right'):ax.spines[p].set_visible(False)
# I. Stage 1 full history with an explicit late-resolution panel
s1=pd.read_csv(DATA/'stage1_archival_area_milestones.csv');labels=s1.version.tolist();a=s1.area.to_numpy()
fig,(ax,bx)=plt.subplots(1,2,figsize=(9.2,3.25),gridspec_kw={'width_ratios':[1.24,1.1]},layout='constrained')
x=np.arange(len(labels));bars=ax.bar(x,a/1000,color=[COL['slate'] if i<4 else COL['sage'] for i in range(len(a))],edgecolor=DARK,lw=.7,zorder=3,width=.74)
ax.set_xticks(x,labels,rotation=38,ha='right');ax.set_ylim(0,1220);ax.set_ylabel('Stage 1 archived total area (thousands)');ax.set_title('Full scale: representation and recovery');clean(ax)
for i in (0,1,2,3):ax.annotate(f'{a[i]:,}',(x[i],a[i]/1000),xytext=(0,4),textcoords='offset points',ha='center',fontsize=8)
late=s1.iloc[3:].copy();lx=np.arange(len(late));delta=late.area-529014
bx.axhline(0,color=DARK,lw=.9,zorder=2)
for j,row in late.reset_index(drop=True).iterrows():
    d=int(row.area-529014);bx.plot([j,j],[0,d],color=COL['slate'],lw=4,solid_capstyle='round',zorder=2)
    bx.scatter(j,d,s=53,color=COL['sage'] if d<=0 else COL['rose'],edgecolor=DARK,lw=.75,zorder=4)
    bx.annotate(f'{d:+d}',(j,d),xytext=(0,7 if d>=0 else -13),textcoords='offset points',ha='center',fontsize=8)
bx.set_xticks(lx,late.version,rotation=38,ha='right');bx.set_title('Late zoom: difference from R5.1');bx.set_ylabel(r'$A(\mathrm{round})-A(\mathrm{R5.1})$');bx.set_ylim(-430,240);bx.grid(axis='y',color=GRID,lw=.8);bx.spines[['top','right']].set_visible(False)
fig.suptitle('Stage 1: the large early convergence and small late trade-offs are different scales',fontsize=11.5)
save(fig,'13_stage1_multiscale_history.pdf')
# II. Stage 2 named milestones with deltas and actual delays; exclude incomplete R7 from numeric trajectory
s2=pd.read_csv(DATA/'stage2_full_milestone_trace.csv');ok=s2[s2.pass_count.eq(25)&s2.target_count.eq(25)].copy(); xs=np.arange(len(ok)); labels=ok['round'].tolist();delta=508535-ok.area_pass; delay=ok.delay_pass-1101
fig,(ax,bx)=plt.subplots(2,1,figsize=(9.1,5.5),sharex=True,layout='constrained',gridspec_kw={'height_ratios':[1.1,.8]})
ax.plot(xs,delta,color=DARK,lw=1.7,zorder=1);ax.scatter(xs,delta,color=COL['blue'],edgecolor=DARK,lw=.75,s=55,zorder=3)
ax.set_ylabel('Stage 2 area saved vs R7.2');ax.set_title('Area improvement: historical chosen candidate at each complete checkpoint');clean(ax)
for r in ('R7.2','R8.1','R8.5','R9.1','R10.0'):
 k=labels.index(r);ax.annotate(f'{int(delta.iloc[k]):+,}',(k,float(delta.iloc[k])),textcoords='offset points',xytext=(0,8),ha='center',fontsize=8)
bx.axhline(0,color=DARK,lw=.9,zorder=2);bx.plot(xs,delay,color=COL['rose'],lw=1.5,zorder=1)
bx.scatter(xs,delay,color=COL['rose'],edgecolor=DARK,s=52,lw=.7,zorder=3)
bx.set_ylabel('Sum of delay changes vs R7.2');bx.set_xticks(xs,labels,rotation=48,ha='right');clean(bx)
fig.suptitle('Stage 2: area decreased while the chosen delay operating point changed',fontsize=11.5)
fig.text(.5,-.005,'R7 (24/25 PASS) excluded. Historical runs describe development, not isolated effects.',ha='center',fontsize=8,color=DARK)
save(fig,'14_stage2_area_delay_trajectory.pdf')
# III. Late-stage magnified, the only way to see 1,034 area units on 495k background
late=ok[ok['round'].isin(['R8.5','R8.6','R8.7','R9.0','R9.1','R10.0','R10.1'])];xx=np.arange(len(late));late_v=late.area_pass.to_numpy()
fig,ax=plt.subplots(figsize=(7.6,3.4),layout='constrained'); ax.axhline(494999,color=COL['slate'],ls='--',lw=1.4,label='R9.0 reference = 494,999')
ax.plot(xx,late_v,color=DARK,lw=1.4,marker='o',ms=7,mec=DARK,mfc=COL['sage'])
ax.set_xticks(xx,late['round']);ax.set_ylim(493680,495280);ax.yaxis.set_major_formatter(FuncFormatter(lambda x,_:f'{x:,.0f}'));ax.set_ylabel('Stage 2 archived total area (25 cases)');ax.set_title('Late-stage magnification: the 1,034-unit improvement is visible');clean(ax)
for i,(rr,area) in enumerate(zip(late['round'],late_v)):
 if i in [0,3,4,5,6]:ax.annotate(f'{area:,}',(i,area),xytext=(0,8 if area<494900 else -16),textcoords='offset points',ha='center',fontsize=8.5)
ax.legend(loc='upper left',frameon=False,fontsize=8.5)
save(fig,'15_stage2_late_zoom.pdf')
# IV. All 111 names summarized as within-round range, no visual zero-precision overplotting
v=pd.read_csv(DATA/'stage2_all_variant_index.csv');order=list(s2['round']); agg=v.groupby('round',sort=False).agg(total=('variant','size'),complete=('complete_rows',lambda q:int((q>0).sum())),lo=('area','min'),hi=('area','max')).reindex(order).reset_index()
agg['spread']=agg.hi-agg.lo
fig,ax=plt.subplots(figsize=(9.1,5.9),layout='constrained')
y=np.arange(len(agg));bars=ax.barh(y,agg['spread'],color=COL['blue'],edgecolor=DARK,lw=.6,height=.67,zorder=3)
ax.set_yticks(y, [f"{r['round']}  ({int(r['complete'])}/{int(r['total'])} complete)" for _,r in agg.iterrows()]);ax.invert_yaxis()
ax.set_xscale('symlog',linthresh=30,linscale=1.2);ax.set_xlim(-1,18500)
ax.set_xticks([0,20,100,500,2000,10000],['0','20','100','500','2,000','10,000']);ax.grid(axis='x',color=GRID,lw=.75);ax.spines[['top','right']].set_visible(False)
ax.set_xlabel('Within-round archived area spread: max(valid) - min(valid)')
ax.set_title('How much configurations within each Round differed (111 named variants)',fontsize=11.2)
for j,r in agg.iterrows():
 val=int(r['spread'])
 ax.annotate(f'{val:,}',(max(val,0),j),xytext=(5,0),textcoords='offset points',va='center',fontsize=8)
fig.text(.01,-.01,'Symlog x-axis: 0-30 linear, then logarithmic. Complete = at least one full 25/25 target-met archive.',fontsize=8)
save(fig,'16_all_variant_spread.pdf')
# V. Fine-grained case-level views: same across method data on submitted Z1 vs R10
m=pd.read_csv(DATA/'matched_case_metrics.csv');d=m[(m.repeat==1)&m.method_id.isin(['Z1','R10'])]
if len(d)==100:
 pivot=d.pivot_table(index='case_id',columns='method_id',values='area',aggfunc='first').dropna()
 pivot['saving']=pivot['Z1']-pivot['R10']; gg=pivot['saving'].sort_values()
 fig,ax=plt.subplots(figsize=(9.5,3.8),layout='constrained');x=np.arange(len(gg))
 colors=[COL['rose'] if z<0 else COL['sage'] for z in gg]
 ax.bar(x,gg,color=colors,edgecolor=DARK,lw=.25,width=.95);ax.axhline(0,color=DARK,lw=.8);ax.set_xlim(-1,50)
 ax.set_xticks([0,9,19,29,39,49],['1','10','20','30','40','50']);ax.set_xlabel('Case rank, ordered by R10 minus Z1 savings')
 ax.set_ylabel('Z1 area - R10 area');ax.set_title('50-case heterogeneity: 18 improvements, 32 regressions; totals are magnitude-weighted')
 ax.yaxis.set_major_formatter(FuncFormatter(lambda z,p:f'{z:,.0f}'));ax.spines[['top','right']].set_visible(False)
 save(fig,'17_cross_stage_ranked_area.pdf')
print('Generated multiscale charts in',OUT)

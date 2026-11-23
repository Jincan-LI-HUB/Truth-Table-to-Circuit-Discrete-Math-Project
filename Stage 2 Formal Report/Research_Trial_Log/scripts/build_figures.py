"""Evidence-locked figures for UFUG2106 Stage 2 trial log.
Execute: python scripts/build_figures.py
Inputs are bundled evidence CSVs (original hash-checked index and 300-row matched trial).
No new synthesis runs are performed; archived cross-round runs are not presented as randomized controls.
"""
from pathlib import Path
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patheffects as pe
from matplotlib.colors import TwoSlopeNorm, ListedColormap, Normalize
from matplotlib.ticker import FuncFormatter

ROOT=Path(__file__).resolve().parents[1]
DATA=ROOT/'data'
FIG=ROOT/'figures'
FIG.mkdir(exist_ok=True)
N='#1D394B'     # ink
BLUE='#36728A'
TEAL='#247B75'
RUST='#BC6E58'
SAND='#CF9C59'
GRAY='#7E8C92'
MIST='#D5DFE0'
BG='#FBFCFB'
plt.rcParams.update({'figure.facecolor':'white','axes.facecolor':'white','text.color':N,'axes.labelcolor':N,'xtick.color':'#43545D','ytick.color':'#43545D','font.family':'DejaVu Sans','font.size':11,'axes.titlesize':13,'axes.titleweight':'bold','axes.linewidth':0.8,'savefig.facecolor':'white','pdf.fonttype':42,'svg.fonttype':'none'})

def style(ax,xgrid=False,ygrid=True):
    for s in ('top','right','left'): ax.spines[s].set_visible(False)
    ax.spines['bottom'].set_color(MIST)
    ax.tick_params(axis='both',length=0,pad=6)
    if ygrid: ax.grid(axis='y',color='#E4EAEB',linewidth=.75,zorder=0)
    if xgrid: ax.grid(axis='x',color='#E4EAEB',linewidth=.75,zorder=0)
    ax.set_axisbelow(True)

def save(fig,name):
    fig.savefig(FIG/(name+'.pdf'),bbox_inches='tight',pad_inches=.18)
    fig.savefig(FIG/(name+'.png'),dpi=190,bbox_inches='tight',pad_inches=.18)
    plt.close(fig)

m=pd.read_csv(DATA/'selected_round_milestones.csv')
r=pd.read_csv(DATA/'all_runs_reverified.csv')
c=pd.read_csv(DATA/'case_metrics.csv')
match=pd.read_csv(DATA/'matched_case_metrics.csv')
raw=pd.read_csv(DATA/'raw_feedback_verified.csv')
pairs=pd.read_csv(DATA/'raw_controlled_pairs_verified.csv')

# 1. Archival area history—explicitly not a controlled single-factor effect.
x=m[m.bank=='stage2'].copy().reset_index(drop=True)
x=x[x['round']!='R7'].reset_index(drop=True) # invalid comparison on failed case
base=float(x.loc[x['round']=='R7.2','area_pass'].iloc[0])
xx=np.arange(len(x)); delta=x['area_pass'].astype(float)-base
fig,ax=plt.subplots(figsize=(10.2,3.5))
ax.axhline(0,color='#7A888F',linewidth=1)
ax.plot(xx,delta/1000,color=BLUE,lw=2,zorder=3)
ax.scatter(xx,delta/1000,s=46,c=np.where(x['round'].isin(['R7.2','R9.0','R10.0']),TEAL,BLUE),edgecolor='white',lw=1.4,zorder=4)
ax.set_xticks(xx,x['round'].tolist(),rotation=40,ha='right',fontsize=9)
ax.set_ylabel('Area difference from R7.2 (thousands)')
ax.set_title('Stage 2 circuit-area development: large search effects precede small final gains',loc='left',pad=16)
ax.text(xx[0],1.6,'Baseline = 508,535',fontsize=10,color=GRAY)
ax.annotate('R8.1: aggressive cut search',xy=(x.index[x['round']=='R8.1'][0],(x.loc[x['round']=='R8.1','area_pass'].iloc[0]-base)/1000),xytext=(3,-4),textcoords='offset points',fontsize=9,color=RUST)
ax.annotate('R10.0 = 493,965',xy=(x.index[x['round']=='R10.0'][0],(x.loc[x['round']=='R10.0','area_pass'].iloc[0]-base)/1000),xytext=(-95,-28),textcoords='offset points',fontsize=10,color=TEAL)
ax.set_ylim(-19,3.2);style(ax)
save(fig,'01_archival_area_evolution')

# 2. Historical Stage2 area-runtime landscape. Observational context, not randomized optimization frontier.
x=m[(m.bank=='stage2')&(m['round']!='R7')&(m['round']!='R10.1')].copy()
x['saving']=base-x.area_pass
fig,ax=plt.subplots(figsize=(8.0,4.7))
phases=[('R7.1','R7.2','R8'),('R8.1','R8.2','R8.2.1','R8.3','R8.4','R8.5','R8.6','R8.7'),('R9.0','R9.1','R10.0')]
for _,rr in x.iterrows():
    co=TEAL if rr['round'] in phases[2] else (RUST if rr['round'] in phases[1] else GRAY)
    ax.scatter(rr.median_synth_ms,rr.saving/1000,s=95,facecolor=co,edgecolor='white',linewidth=1.4,zorder=4)
    offset={'R7.1':(5,-14),'R7.2':(5,7),'R8':(6,1),'R8.1':(5,-16),'R8.2':(5,2),'R8.2.1':(5,4),'R8.3':(6,2),'R8.4':(5,4),'R8.5':(-38,-14),'R8.6':(5,-16),'R8.7':(-25,6),'R9.0':(5,11),'R9.1':(6,14),'R10.0':(6,-13)}.get(rr['round'],(6,4))
    ax.annotate(rr['round'],(rr.median_synth_ms,rr.saving/1000),xytext=offset,textcoords='offset points',fontsize=9,color=N)
ax.set_xlim(10,230);ax.set_ylim(-1.5,17)
ax.set_xlabel('Median synthesis runtime (ms), archived run')
ax.set_ylabel('Area saved versus R7.2 (thousands)')
ax.set_title('A larger candidate search can improve circuit quality while consuming more time',loc='left',pad=14)
style(ax);save(fig,'02_archival_area_runtime')

# 3. Cross-round case-level matrix with *independently chosen* archived run per round.
choose=['R7.2','R8','R8.1','R8.2.1','R8.3','R8.4','R8.5','R9.0','R9.1','R10.0']
cols={}
for k in choose:
    rec=m[(m['round']==k)&(m.bank=='stage2')].iloc[0]
    vals=r[(r.report_hash==rec.evidence_sha256)&(r.bank=='stage2')]
    assert len(vals)>0,k
    cid=vals.iloc[0].run_id
    q=c[(c.run_id==cid)&(c.passed==1)].set_index('case_id')['area']
    assert len(q)==25,k
    cols[k]=q
pivot=pd.DataFrame(cols).sort_index()
assert pivot.shape==(25,len(choose))
rel=(pivot.div(pivot['R7.2'],axis=0)-1)*100
rel.to_csv(DATA/'casewise_milestone_relative_area.csv',float_format='%.9g')
fig,ax=plt.subplots(figsize=(11.0,4.65))
# Color encodes monotonically improving area relative to R7.2; one zero cell is light gray.
vals=(-rel.T).to_numpy(dtype=float)
from matplotlib.colors import PowerNorm
cm=plt.get_cmap('YlGnBu').copy();cm.set_under('#F2F4F4')
mat=ax.imshow(vals,aspect='auto',cmap=cm,vmin=.008,vmax=38,interpolation='nearest')
ax.set_yticks(np.arange(len(choose)),choose,fontsize=10)
ax.set_xticks(np.arange(25),[f'{i:02}' for i in range(1,26)],fontsize=8)
ax.tick_params(length=0,pad=6)
for s in ax.spines.values():s.set_visible(False)
ax.set_xlabel('Stage 2 case index (01–25)')
ax.set_title('Which functions changed? A case-by-round map of area reduction',loc='left',pad=14)
ax.set_xticks(np.arange(-.5,25,1),minor=True);ax.set_yticks(np.arange(-.5,len(choose),1),minor=True)
ax.grid(which='minor',color='white',linewidth=1.2);ax.tick_params(which='minor',bottom=False,left=False)
cb=fig.colorbar(mat,ax=ax,fraction=.027,pad=.016)
cb.set_label('Area reduction vs R7.2 (%)',fontsize=10);cb.ax.tick_params(labelsize=9,length=0)
ax.text(0.01,-.23,'Gray = unchanged; colors encode the relative reduction within each case, not comparable raw area totals.',fontsize=9,color=GRAY,transform=ax.transAxes)
save(fig,'03_case_round_area_matrix')

# 4. R8.6 controlled factorial: run1 and run2, 50 cases.
f=pairs[(pairs.group=='r86')&(pairs.bank.isin(['stage1','stage2']))]
def factor(v):
    a=f[(f.candidate==v)].groupby('repeat')['area_saved'].sum()
    return [int(a.loc[i]) if i in a.index else np.nan for i in [1,2]]
variants=['r86_baseline','r86_time_reclaim','r86_extra_sop','r86_combined','r86_reverse']
labels=['Baseline','Extra time','Extra SOP roots','Roots + time','Reverse allocation']
savings=[([0,0] if v=='r86_baseline' else factor(v)) for v in variants]
fig,ax=plt.subplots(figsize=(9.5,3.9))
xx=np.arange(5)
for i,(label,row) in enumerate(zip(labels,savings)):
    col=TEAL if i in (2,3) else (RUST if i==4 else GRAY)
    ax.scatter([i-.09,i+.09],row,s=[72,72],c=col,edgecolors='white',linewidth=1.2,zorder=4)
    ax.plot([i-.09,i+.09],row,lw=2,color=col,zorder=3,alpha=.6)
    ax.text(i,max(row)+130,str(int(row[0])) if row[0]==row[1] else f'{row[0]} / {row[1]}',ha='center',fontsize=10,color=col,weight='bold')
ax.set_xticks(xx,labels,fontsize=10)
ax.set_ylim(-130,3420)
ax.set_ylabel('Area saved relative to baseline (50 cases)')
ax.set_title('R8.6 factorial: useful root allocation, not more wall time, explains the gains',loc='left',pad=12)
style(ax);save(fig,'04_r86_factorial')

# 5. R9.1: plot wins versus actual aggregate saving on 50 cases, same pair batch.
f=pairs[(pairs.group=='r91')&(pairs.bank.isin(['stage1','stage2']))&(pairs.repeat==1)]
print('R91',f[['baseline','candidate','bank','wins','area_saved']].to_string(index=False))
basevar='r91_off';options=['r91_library','r91_repeat_sop','r91_repeat_shannon']
opts=[]
for k in options:
    y=f[f.candidate==k]
    if y.empty: continue
    opts.append((k,int(y.wins.sum()),int(y.area_saved.sum())))
if len(opts)<2:
    # CSV inspect fallback and leave safe note
    print('WARNING R91 exact variant names may differ; available:',sorted(f.candidate.unique()))
else:
    fig,ax=plt.subplots(figsize=(7.5,4.4))
    for (k,wins,saving),col in zip(opts,[GRAY,TEAL,RUST]):
        ax.scatter([wins],[saving],s=155,c=col,edgecolors='white',linewidth=1.4,zorder=4)
        ax.annotate(k.replace('r91_','').replace('_',' ').title()+f'  ({saving:+,})',(wins,saving),xytext=(9,5),textcoords='offset points',fontsize=10,color=col,weight='medium')
    ax.set_xlim(0,max([o[1] for o in opts])+6);ax.set_ylim(min([0]+[o[2] for o in opts])-170,max(o[2] for o in opts)+250)
    ax.set_xlabel('Cases with strictly lower area (out of 50)')
    ax.set_ylabel('Net area saved versus off control')
    ax.set_title('R9.1: hit frequency and area benefit are different objectives',loc='left',pad=14)
    style(ax);save(fig,'05_r91_frequency_vs_magnitude')

# 6. R10.0 isolated gain distribution, strictly matched within package.
f=pairs[(pairs.group=='r100')&(pairs.repeat==1)&(pairs.candidate=='r100_default')]
print('R100 rows', f[['baseline','candidate','bank','area_saved','case_savings']].to_string(index=False))
gains={}
for _,q in f.iterrows():
  for term in str(q.case_savings or '').split(';'):
    if ':' not in term:continue
    name,amt=term.split(':')
    gains[q.bank+'/'+name.strip()]=int(float(amt))
assert sum(gains.values())==1587,(gains,sum(gains.values()))
sortedg=sorted(gains.items(),key=lambda kv:kv[1],reverse=True)
fig,ax=plt.subplots(figsize=(9.6,3.75))
xv=np.arange(len(sortedg));Y=np.array([v for _,v in sortedg]);names=[x.replace('stage','S').replace('/case_','/').replace('.txt','') for x,_ in sortedg]
ax.vlines(xv,0,Y,color=MIST,linewidth=5,zorder=1);ax.scatter(xv,Y,c=[TEAL]+[BLUE]*(len(Y)-1),s=80,zorder=3,edgecolors='white',lw=1.5)
for i,y in enumerate(Y): ax.text(i,y+16,str(y),fontsize=9,ha='center',color=TEAL if i==0 else BLUE,weight='bold')
ax.set_xticks(xv,names,fontsize=9)
ax.set_ylabel('Absolute area saved in this case')
ax.set_title('R10.0: eight cases carry all 1,587 units of incremental gain',loc='left',pad=12)
ax.text(0.98,0.83,f'Largest gain: {100*Y[0]/Y.sum():.1f}% of total',ha='right',transform=ax.transAxes,color=TEAL,fontsize=11)
ax.set_ylim(0,max(Y)*1.18);style(ax);save(fig,'06_r100_sparse_case_gains')

# 7. Matched direct policy comparison: rank inversion in gains.
mt=match[match.repeat==1].pivot(index='case_id',columns='method_id',values='area').dropna(subset=['Z1','S100'])
impact=(mt.Z1-mt.S100).sort_values(ascending=False)
assert (impact>0).sum()==18 and (impact<0).sum()==32
fig,ax=plt.subplots(figsize=(10.0,4.6))
pos=impact.to_numpy()
colors=[TEAL if v>0 else RUST for v in pos]
ax.bar(np.arange(len(pos)),pos/1000,color=colors,width=.82,zorder=3)
ax.axhline(0,color=N,linewidth=.9)
ax.set_xticks([0,9,19,29,39,49],[1,10,20,30,40,50])
ax.set_xlabel('Case rank by contribution to Zeyun Stage 1 → Stage 2 area saving')
ax.set_ylabel('Area saved per case (thousands; negative = regression)')
ax.set_title('A ranking reversal: 18 wins, 32 regressions, yet net area falls by 124,697',loc='left',pad=14)
ax.annotate('Stage 2/005\n+39,516',xy=(0,pos[0]/1000),xytext=(15,-28),textcoords='offset points',fontsize=10,color=TEAL,weight='bold')
ax.annotate(
    'Stage 2/002\n-8,003',
    xy=(49, pos[-1] / 1000),
    xytext=(-68, 10),
    textcoords='offset points',
    fontsize=10,
    color=RUST,
    weight='bold',
    ha='right',
    va='bottom'
)
ax.text(0.985,.78,'Median relative area change: +3.69%\n(unweighted median across cases)',transform=ax.transAxes,ha='right',fontsize=10,color=GRAY)
style(ax);save(fig,'07_matched_area_rank_reversal')

# 8. Cumulative concentration curve—the observed tradeoff in weighted total.
idx=np.arange(1,len(impact)+1)
cum=impact.cumsum().to_numpy()
fig,ax=plt.subplots(figsize=(8.3,4.1))
ax.plot(idx,cum/1000,lw=2.4,color=BLUE)
ax.scatter([18,50],[cum[17]/1000,cum[-1]/1000],color=[TEAL,RUST],s=90,zorder=4,edgecolor='white',lw=1.5)
ax.axhline(0,lw=.8,color=GRAY)
ax.axvline(18,ls=':',lw=1,color=GRAY)
ax.text(18,cum[17]/1000+9,f'18 positive contributors: +{int(cum[17]):,}',ha='center',fontsize=10,color=TEAL)
ax.annotate(f'After 32 regressions:\n+{int(cum[-1]):,}',(50,cum[-1]/1000),xytext=(-145,-38),textcoords='offset points',color=RUST,fontsize=10,weight='bold')
ax.set_xlim(1,52);ax.set_ylim(0,cum.max()/1000+35)
ax.set_xlabel('Number of cases, ordered from largest area saving to greatest regression')
ax.set_ylabel('Cumulative area saving (thousands)')
ax.set_title('Large gains on a few instances outweigh many smaller losses',loc='left',pad=13)
style(ax);save(fig,'08_matched_cumulative_contribution')

# print checked chart stats
print('Saved eight chart pairs; cross-round count',len(pivot),'stage2 cases, rounds',len(choose))
print('factor data:',dict(zip(labels,savings)))
print('R10 gain structure:',sortedg)
print('matched distribution: sum',impact.sum(),'positive',impact[impact>0].sum(),'negative',impact[impact<0].sum(),'median relative area %',(mt.S100.div(mt.Z1).sub(1).median()*100))

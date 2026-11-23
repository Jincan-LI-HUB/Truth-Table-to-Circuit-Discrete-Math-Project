"""Reproduce report figures from the archived case-level evidence. Palette is user-provided."""
from pathlib import Path
import json
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
from matplotlib.ticker import FuncFormatter

ROOT=Path(__file__).resolve().parent
P={**json.loads((ROOT/'palette.json').read_text())['colors'], 'ink':'#252B30','muted':'#58616A','bg':'#FFFFFF'}
F=ROOT/'figures'; F.mkdir(exist_ok=True)
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10.5,'axes.titlesize':12,'axes.labelsize':10.5,
 'xtick.labelsize':9.5,'ytick.labelsize':9.5,'axes.edgecolor':P['ink'],'axes.labelcolor':P['ink'],
 'text.color':P['ink'],'xtick.color':P['ink'],'ytick.color':P['ink'],
 'pdf.fonttype':42,'ps.fonttype':42,'savefig.facecolor':'white'})

def save(fig,name):
    fig.savefig(F/f'{name}.pdf',bbox_inches='tight',pad_inches=.10)
    plt.close(fig)

def light(ax,axis='y'):
    ax.spines[['top','right']].set_visible(False)
    ax.grid(axis=axis,color='#DEE2E4',linewidth=.65,zorder=0)
    ax.set_axisbelow(True)

raw=pd.read_csv(ROOT/'data/matched_case_metrics.csv'); r=raw.query('repeat == 1')
a=r.pivot(index='case_id',columns='method_id',values='area')
d=(a['Z1']-a['S100']).sort_values(ascending=False); wins=d[d>0].sum(); losses=-d[d<0].sum()
assert int(wins)==160696 and int(losses)==35999 and int(d.sum())==124697

fig,axes=plt.subplots(1,2,figsize=(7.25,3.30),gridspec_kw={'width_ratios':[1.56,1]},layout='constrained')
ax=axes[0]; n=len(d); xx=np.arange(1,n+1)
for bank,marker in [('stage1','o'),('stage2','s')]:
    mask=np.array([s.startswith(bank) for s in d.index]); sub=d.to_numpy()[mask]
    ax.scatter(xx[mask],sub/1000,s=30,marker=marker,edgecolors=P['ink'],linewidths=.55,
               color=[P['sage'] if k>0 else P['rose'] for k in sub],zorder=3,
               label='Stage 1' if bank=='stage1' else 'Stage 2')
ax.axhline(0,color=P['ink'],lw=1.05)
ax.set_yscale('symlog',linthresh=1,linscale=.8)
ax.set_ylim(-15,90);ax.set_xlim(0,51)
ax.set_xticks([1,10,20,30,40,50]);ax.set_xlabel('Cases ordered by signed area difference')
ax.set_ylabel(r'$A_{\mathrm{Z1}}-A_{\mathrm{R10}}$ (thousands)')
ax.yaxis.set_major_formatter(FuncFormatter(lambda x,pos:f'{x:g}'))
light(ax)
ax.legend(handles=[Line2D([0],[0],marker='o',color='none',markerfacecolor=P['sage'],markeredgecolor=P['ink'],label='Stage 1'),
 Line2D([0],[0],marker='s',color='none',markerfacecolor=P['sage'],markeredgecolor=P['ink'],label='Stage 2')],
 loc='upper right',frameon=False,fontsize=9)
ax=axes[1];values=[wins/1000,-losses/1000,(wins-losses)/1000]; labels=['18 benefits','32 regressions','Net change']
colors=[P['sage'],P['rose'],P['blue']]
for i,(v,c) in enumerate(zip(values,colors)):
 ax.barh(i,v,color=c,height=.55,edgecolor=P['ink'],linewidth=.7,zorder=3)
 ax.text(v+3 if v>=0 else -17,i,f'{v:+,.1f}k',ha='left' if v>=0 else 'center',va='center',fontsize=10,weight='bold')
ax.axvline(0,color=P['ink'],lw=1);ax.set_xlim(-70,185)
ax.set_yticks(range(3),labels);ax.invert_yaxis();ax.set_xlabel('Signed total area contribution')
light(ax,'x')
save(fig,'area_case_heterogeneity')

# Compact 2x2 factorial design: each measured cell occupies a restrained box.
# Data determine all labels; text sizes were selected for the final IEEE physical scale.
q=pd.read_csv(ROOT/'data/quota_factorial.csv').query('repeat == 1')
quota=int(q.extra_roots.sum()); reclaim=int(q.reclaim.sum())
both=int(q.both.sum()); rev=int(q.reverse.sum())
assert (quota,reclaim,both,rev)==(2844,0,2844,20)
fig,ax=plt.subplots(figsize=(6.4,1.95));ax.set_xlim(0,6.4);ax.set_ylim(0,1.95);ax.axis('off')
cell_x=[1.43,3.88]; cell_y=[.94,.15]; w,h=2.26,.64
for j,label in enumerate(['No time reclaim','Reclaim unused time']):
    ax.text(cell_x[j]+w/2,1.75,label,fontsize=8.7,ha='center',va='center',weight='semibold')
for i,(label,vals) in enumerate([('Base SOP\nquota',[0,reclaim]),('Extra SOP\nroots',[quota,both])]):
    ax.text(.73,cell_y[i]+h/2,label,fontsize=8.2,ha='center',va='center')
    for j,val in enumerate(vals):
        fill=P['sage'] if val else P['stone']
        rect=FancyBboxPatch((cell_x[j],cell_y[i]),w,h,boxstyle='round,pad=.009,rounding_size=.045',
                            facecolor=fill,edgecolor=P['ink'],linewidth=.85)
        ax.add_patch(rect)
        ax.text(cell_x[j]+w/2,cell_y[i]+h/2, f'{val:+,} area saved',
                fontsize=8.8,weight='semibold',ha='center',va='center')
        # Marker redundantly identifies quota treatment in grayscale, without
        # putting high-contrast hatch strokes through the numeric labels.
        ax.scatter([cell_x[j]+w-.17],[cell_y[i]+h-.16],s=21,
                   marker='s' if val else 'o',facecolor=P['ink'] if val else 'white',
                   edgecolor=P['ink'],linewidth=.65,zorder=4)
save(fig,'r86_factorial_design')

# R9 vs R10 same archived run and each input.
off=pd.read_csv(ROOT/'data/official_r90_r100_casewise.csv').query('run == 1')
off['case_id']=off['bank']+'/'+off['case']; x=off.pivot(index='case_id',columns='method',values='area'); diff=(x['r90_frozen']-x['r100_default']).sort_values(ascending=False)
positive=diff[diff>0]; assert int(diff.sum())==1587 and len(positive)==8 and (diff<0).sum()==0
fig,ax=plt.subplots(figsize=(3.62,2.55)); vals=positive.iloc[::-1]; y=np.arange(len(vals));
ax.barh(y,vals,facecolor=P['blue'],edgecolor=P['ink'],lw=.65,height=.60)
ax.set_yticks(y,[s.replace('stage1/','S1/').replace('stage2/','S2/').replace('case_','').replace('.txt','') for s in vals.index]);
for i,v in enumerate(vals):ax.text(v+12,i,str(int(v)),va='center',fontsize=8.7,weight='semibold')
ax.set_xlim(0,max(vals)*1.25);ax.set_xlabel('Area saved by R10.0 vs R9.0 (weighted units)',fontsize=8.4);ax.tick_params(labelsize=8.5);light(ax,'x')
ax.text(.97,.075,'8 improved / 42 unchanged\nNo regression; same delay',transform=ax.transAxes,
 ha='right',va='bottom',fontsize=7.6, bbox=dict(boxstyle='round,pad=.22',fc=P['ivory'],ec=P['stone']))
save(fig,'last_pass_sparse_benefit')

# Runtime distribution: strict same-run common data, samples = 50 methods.
fig,ax=plt.subplots(figsize=(3.57,2.66))
for meth,col,ls,mk,lab in [('Z1',P['slate'],'-','o','Submitted Z1'),('J51',P['blue'],'--','s','Research J51'),('S100',P['sage'],'-.','D','Final R10')]:
 vals=np.sort(r.query('method_id==@meth')['synth_runtime_ms'].dropna().to_numpy());n=len(vals); yy=np.arange(1,n+1)/n
 ax.step(vals,yy,where='post',lw=1.6,ls=ls,color=P['ink'],label=lab)
 sel=np.linspace(0,n-1,7,dtype=int)
 ax.scatter(vals[sel],yy[sel],s=15,marker=mk,color=col,edgecolor=P['ink'],lw=.55,zorder=4)
ax.set_xscale('log');ax.set_xlim(1,5000);ax.set_ylim(0,1.03);ax.set_xticks([1,10,100,1000],['1','10','100','1000']);ax.set_ylabel('Fraction of cases (ECDF)')
ax.set_xlabel('Synthesis runtime (ms; log scale)',fontsize=8.7);ax.set_ylabel('Fraction of cases (ECDF)',fontsize=8.7);ax.tick_params(labelsize=8.3);ax.legend(loc='lower right',fontsize=7.8,frameon=True,facecolor='white',edgecolor=P['stone']);light(ax)
save(fig,'matched_runtime_ecdf')

# Restrained source-aligned, six-step flow. Use three wide cells per row so
# that titles remain strictly inside nodes at the actual IEEE print size.
fig,ax=plt.subplots(figsize=(7.45,2.55))
ax.set_xlim(0,7.45);ax.set_ylim(0,2.55);ax.axis('off')
X=[.13,2.65,5.17]; Y=[1.45,.28]; W,H=2.12,.78

def flowbox(x,y,title,sub,fill):
    p=FancyBboxPatch((x,y),W,H,boxstyle='round,pad=0.012,rounding_size=.043',
                     facecolor=fill,edgecolor=P['ink'],linewidth=.80)
    ax.add_patch(p)
    ax.text(x+W/2,y+.51,title,fontsize=8.8,weight='semibold',ha='center',va='center')
    ax.text(x+W/2,y+.23,sub,fontsize=7.2,ha='center',va='center')

def flowarrow(a,b):
    ax.add_patch(FancyArrowPatch(a,b,arrowstyle='-|>',mutation_scale=8.3,
                                 lw=.8,color=P['ink'],shrinkA=0,shrinkB=0))

top=[('Input and guards','Truth table; cost/limits','ivory'),
     ('Construct candidates','BDD, covers, gate DAG','blue'),
     ('Select incumbent','Prune, area and delay','mint')]
bottom=[('Emit final netlist','AND2 / OR2 / NOT','sage'),
        ('R10 repeat-SOP','Optional; strict area gain','blue'),
        ('R8.6 alternatives','Shannon + SOP from same G','peach')]
for j,(title,sub,fill) in enumerate(top):flowbox(X[j],Y[0],title,sub,P[fill])
for j,(title,sub,fill) in enumerate(bottom):flowbox(X[j],Y[1],title,sub,P[fill])
for j in range(2):
    cy=Y[0]+H/2
    flowarrow((X[j]+W+.04,cy),(X[j+1]-.04,cy))
    cy=Y[1]+H/2
    flowarrow((X[j+1]-.04,cy),(X[j]+W+.04,cy))
flowarrow((X[2]+W/2,Y[0]-.04),(X[2]+W/2,Y[1]+H+.04))
save(fig,'solver_execution_architecture')

# R10.0 frozen-policy alternatives: controlled 100-pair evidence, not a
# historical cross-version runtime comparison. Both axes are measured against
# exactly the same R10.0 frozen comparator.
pol=pd.read_csv(ROOT/'data/final_policy_tradeoff.csv')
order=['r101_off','r101_cap40','r101_cap80','r101_budget45','r101_default','trial_submission']
assert set(order)==set(pol.policy) and (pol.paired==100).all()
pol=pol.set_index('policy').loc[order].reset_index()
lab={'r101_off':'Disable extra SOP','r101_cap40':'Limit to 40 roots','r101_cap80':'Limit to 80 roots','r101_budget45':'45-ms allowance','r101_default':'R10.1 default','trial_submission':'Submission trial'}
plt.rcParams.update({'font.size':12.3,'axes.titlesize':12.3,'axes.labelsize':11.8,'xtick.labelsize':11,'ytick.labelsize':11.4})
fig,axes=plt.subplots(1,2,figsize=(7.45,3.75),gridspec_kw={'width_ratios':[1.02,1.0],'wspace':.16})
y=np.arange(6)
for ax in axes:
 ax.spines[['right','top']].set_visible(False);ax.grid(axis='x',color='#EAE8E4',lw=.75,zorder=0)
 ax.set_axisbelow(True);ax.set_ylim(5.6,-.6)
axes[0].barh(y,pol.penalty50,color=[P['rose'] if k not in ['r101_default','trial_submission'] else P['sage'] for k in order],edgecolor=P['ink'],height=.56,lw=.75,zorder=3)
axes[0].set_yticks(y,[lab[k] for k in order]);axes[0].tick_params(axis='y',length=0,pad=6)
for yi,v in zip(y,pol.penalty50):axes[0].text(v+34,yi,f'+{v:,.0f}' if v>0 else '0',va='center',ha='left',fontsize=11)
axes[0].set_xlim(0,1850);axes[0].set_xticks([0,500,1000,1500]);axes[0].set_xlabel('Extra weighted area vs frozen R10.0')
axes[0].set_title('Circuit-quality cost',loc='left',fontweight='semibold',pad=13)
axes[1].axvline(1,ls='--',lw=1,color=P['ink'],zorder=2)
axes[1].scatter(pol.runtime_median_ratio,y,s=100,edgecolor=P['ink'],lw=1.0,marker='D',c=[P['rose'] if k in ['r101_budget45','trial_submission'] else P['sage'] for k in order],zorder=4)
axes[1].set_yticks(y,[]);axes[1].set_xlim(.923,1.04);axes[1].set_xticks([.94,.97,1.00,1.03]);axes[1].set_xlabel('Median paired runtime / frozen R10.0')
axes[1].set_title('Synthesis-time ratio',loc='left',fontweight='semibold',pad=13)
for yy,val in enumerate(pol.runtime_median_ratio):axes[1].annotate(f'{val:.3f}',(val,yy),xytext=(7,0),textcoords='offset points',va='center',ha='left',fontsize=9.9)
fig.subplots_adjust(left=.275,right=.975,bottom=.23,top=.85)
fig.savefig(F/'final_policy_tradeoff.pdf',bbox_inches='tight',pad_inches=.16)
plt.close(fig)

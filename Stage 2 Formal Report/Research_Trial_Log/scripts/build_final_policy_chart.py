"""Reproduce exact R10.1 matched policy analysis as legible vector chart."""
from pathlib import Path
import numpy as np,pandas as pd,matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt,json
R=Path(__file__).resolve().parents[1];PAL=json.loads((R/'palette.json').read_text())['colors'];INK='#293039'
s=pd.read_csv(R/'data/r101_native_paired_policy_summary.csv')
keys=['r101_off','r101_cap40','r101_cap80','r101_budget45','r101_default','trial_submission']
assert set(s.policy)==set(keys) and set(s.paired)=={100}
s=s.set_index('policy').loc[keys].reset_index();s['penalty50']=-s.area_saved_total/2
lab={'r101_off':'Disable extra SOP','r101_cap40':'Limit to 40 roots','r101_cap80':'Limit to 80 roots','r101_budget45':'45-ms allowance','r101_default':'R10.1 default','trial_submission':'Submission trial'}
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':12.3,'axes.titlesize':12.3,'axes.labelsize':11.8,'xtick.labelsize':11,'ytick.labelsize':11.4,'pdf.fonttype':42,'text.color':INK,'axes.labelcolor':INK,'xtick.color':INK,'ytick.color':INK,'axes.edgecolor':INK})
fig,axes=plt.subplots(1,2,figsize=(9.5,4.15),gridspec_kw={'width_ratios':[1.02,1.0],'wspace':.12});y=np.arange(6)
for ax in axes:
 ax.spines[['right','top']].set_visible(False);ax.grid(axis='x',color='#EAE8E4',lw=.75,zorder=0)
 ax.set_axisbelow(True);ax.set_ylim(5.6,-.6)
axes[0].barh(y,s.penalty50,color=[PAL['rose'] if k not in ['r101_default','trial_submission'] else PAL['sage'] for k in keys],edgecolor=INK,height=.56,lw=.75,zorder=3)
axes[0].set_yticks(y,[lab[k] for k in keys]);axes[0].tick_params(axis='y',length=0,pad=6)
for yi,v in zip(y,s.penalty50):axes[0].text(v+34,yi,f'+{v:,.0f}' if v>0 else '0',va='center',ha='left',fontsize=11)
axes[0].set_xlim(0,1850);axes[0].set_xticks([0,500,1000,1500]);axes[0].set_xlabel('Extra weighted area vs frozen R10.0')
axes[0].set_title('Circuit-quality cost',loc='left',fontweight='semibold',pad=13)
axes[1].axvline(1,ls='--',lw=1,color=INK,zorder=2)
axes[1].scatter(s.runtime_median_ratio,y,s=100,edgecolor=INK,lw=1,marker='D',c=[PAL['rose'] if k in ['r101_budget45','trial_submission'] else PAL['sage'] for k in keys],zorder=4)
axes[1].set_yticks(y,[]);axes[1].set_xlim(.923,1.04);axes[1].set_xticks([.94,.97,1.0,1.03]);axes[1].set_xlabel('Median paired runtime / frozen R10.0')
axes[1].set_title('Synthesis-time ratio',loc='left',fontweight='semibold',pad=13)
for yy,val in enumerate(s.runtime_median_ratio):axes[1].annotate(f'{val:.3f}',(val,yy),xytext=(7,0),textcoords='offset points',va='center',ha='left',fontsize=9.9)
fig.subplots_adjust(left=.235,right=.985,bottom=.22,top=.86)
fig.savefig(R/'figures/12_r101_native_pareto.pdf',bbox_inches='tight',pad_inches=.16)
fig.savefig(R/'figures/12_r101_native_pareto.png',bbox_inches='tight',pad_inches=.16,dpi=190)
plt.close(fig)
print('verified R10.1 paired policy view: 100 observations per configuration')

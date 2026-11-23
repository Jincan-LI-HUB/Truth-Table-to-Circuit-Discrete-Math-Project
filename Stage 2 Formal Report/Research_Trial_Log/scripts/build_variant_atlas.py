"""Generate complete, legible two-round-per-page Stage 2 variant atlas.
Each plotted point is one archive-designated complete 25-case observation.
For all raw report rows and observed failures consult stage2_all_variant_index.csv.
"""
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import json
ROOT=Path(__file__).resolve().parents[1]
FIG=ROOT/'figures'
D=ROOT/'data'
PAL=json.loads((ROOT/'palette.json').read_text())['colors']
INK='#293039'; GRID='#ECE9E5'; BASE=508535
order=['R7','R7.1','R7.2','R8','R8.1','R8.2','R8.2.1','R8.3','R8.4','R8.5','R8.6','R8.7','R9.0','R9.1','R10.0','R10.1']
frame=pd.read_csv(D/'stage2_all_variant_index.csv')
assert set(frame['round'])==set(order) and len(frame)==111
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':11.8,'axes.labelsize':11.5,'axes.titlesize':12.5,'ytick.labelsize':10.6,'xtick.labelsize':10.8,'pdf.fonttype':42,'text.color':INK,'axes.labelcolor':INK,'xtick.color':INK,'ytick.color':INK})
for part,first in enumerate(range(0,16,2),1):
    fig,axs=plt.subplots(2,1,figsize=(8.4,7.0),layout='constrained',gridspec_kw={'hspace':.23})
    for j,ax in enumerate(axs):
        rnd=order[first+j];g=frame.loc[frame['round']==rnd].copy()
        g['gain']=BASE-g.area
        g=g.sort_values(['area','variant'],na_position='last')
        ypos=np.arange(len(g))
        good=g.area.notna().to_numpy()
        gain=g['gain'].to_numpy()
        ax.axvline(0,ls=':',lw=1,color=INK)
        ax.grid(axis='x',color=GRID,lw=.7,zorder=0);ax.set_axisbelow(True)
        ax.spines[['right','top']].set_visible(False)
        for y,(ok,v) in enumerate(zip(good,gain)):
            if not ok:
                ax.scatter([0],[y],s=85,c='white',edgecolors=INK,marker='x',lw=1.5,zorder=4)
                ax.annotate('no complete record',(0,y),xytext=(7,0),textcoords='offset points',fontsize=9.6,va='center')
                continue
            color=PAL['sage'] if v>0 else PAL['rose'] if v<0 else PAL['slate']
            marker='D' if v>0 else 's' if v<0 else 'o'
            ax.scatter([v/1000],[y],s=64,c=[color],edgecolors=INK,marker=marker,lw=.8,zorder=4)
        ax.set_yticks(ypos,g.variant.astype(str))
        ax.invert_yaxis();ax.tick_params(axis='y',length=0,pad=6)
        ax.set_title(f'{rnd}: {len(g)} archived configurations ({int(good.sum())} with at least one complete 25-case run)',loc='left',weight='semibold',pad=8)
        ax.set_xlim(-1.1,16.8)
        ax.set_xticks([0,4,8,12,16])
        ax.set_xlabel('Weighted area saved relative to R7.2 (25 Stage 2 cases, thousands)')
    fig.suptitle(f'Historical alternatives — rounds {order[first]} and {order[first+1]}',fontweight='semibold',fontsize=13.5)
    out=FIG/f'11_stage2_variant_atlas_part_{part:02d}'
    fig.savefig(str(out)+'.pdf',bbox_inches='tight',pad_inches=.17)
    fig.savefig(str(out)+'.png',bbox_inches='tight',pad_inches=.17,dpi=190)
    plt.close(fig)
print('complete archive: 111 variant names, 105 with complete observations, eight two-round pages')

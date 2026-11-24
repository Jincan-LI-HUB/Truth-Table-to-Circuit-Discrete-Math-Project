"""Upstream development evidence for Trial Log Part III."""
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.patches import Rectangle
import numpy as np
import pandas as pd

from phase_c_data import ARCHIVE, BANKS
from phase_c_plot_style import BLUE, GRID, INK, LINE, MINT, PEACH, RUST, TEAL, export


REPORTS = ARCHIVE.parent/'reports'
TIMING = REPORTS/'stage2-timing-20261124'


def pass_evidence(out):
    cuts = pd.read_csv(REPORTS/'stage2-cuts-20261124/paired.csv')
    factors = pd.read_csv(REPORTS/'stage2-factors-20261124/paired.csv')
    cuts['gain'] = cuts.area_before-cuts.area_after
    factors['gain'] = factors.area_before-factors.area_after
    ranked = cuts.sort_values('gain',ascending=False)
    fig,(a,b) = plt.subplots(1,2,figsize=(6.86,2.70))
    x = np.arange(1,len(ranked)+1)
    for bank,color in zip(BANKS,[BLUE,TEAL]):
        choose = ranked.bank.eq(bank)
        a.scatter(x[choose],ranked.loc[choose,'gain'],color=color,s=14,label=bank.replace('stage','Stage '))
    for i,(_,row) in enumerate(ranked.head(3).iterrows(),1):
        a.annotate(f'{row.bank[-1]}/{row.case[5:8]}',(i,row.gain),xytext=(5,3),
                   textcoords='offset points',fontsize=7.4)
    a.text(.98,.99,f'{ranked.gain.sum():,} units saved\n{ranked.gain.gt(0).sum()} wins, {ranked.gain.eq(0).sum()} ties',
           ha='right',va='top',transform=a.transAxes,fontsize=7.6)
    a.legend(loc='center right',frameon=False,fontsize=7.3)
    a.set(xlabel='Public case rank by area saved',ylabel='Weighted area saved',ylim=(-85,1690))
    family = factors.bank.replace(dict.fromkeys(BANKS,'public'))
    labels=[]
    for i,(name,color) in enumerate([('public',TEAL),('diagnostic',RUST),('holdout','#516E8A')]):
        gains = factors.loc[family.eq(name),'gain']
        positive=gains[gains>0].to_numpy()
        b.scatter(positive,i+np.linspace(-.13,.13,len(positive)),s=25,color=color,
                  marker=['o','D','s'][i],alpha=.78)
        labels.append(f'{name.title()}\n{len(positive)}/{len(gains)} wins')
        b.text(.19,i,f'{gains.sum():,} total',transform=b.get_yaxis_transform(),va='center',
               fontsize=7.5,bbox=dict(facecolor='white',edgecolor='none',alpha=.85,pad=1))
    b.set_xscale('log')
    b.set(xlim=(.83,1200),xticks=[1,2,5,10,50,100,500,1000],
          xticklabels=['1','2','5','10','50','100','500','1k'],yticks=range(3),yticklabels=labels,
          ylim=(2.56,-.56),xlabel='Area saved on improved cases (log scale)')
    for ax,title in zip((a,b),['A  ·  Fixed-incumbent cut polishing','B  ·  Shared-factor gains by family']):
        ax.set_title(title,loc='left',fontsize=8.7,weight='bold',pad=7)
        ax.tick_params(length=0,labelsize=7.2)
    a.grid(axis='y',color=GRID,lw=.55)
    b.grid(axis='x',color=GRID,lw=.55)
    fig.subplots_adjust(left=.105,right=.98,bottom=.20,top=.87,wspace=.43)
    export(fig,'integration_passes',out)


def policy_evidence(out):
    reserve=pd.read_csv(REPORTS/'stage2-headroom-20261124/development.csv').set_index('trial')
    earlier=pd.read_csv(TIMING/'earlier-budget.csv').set_index('earlier_run').combined_area
    frozen=pd.read_csv(TIMING/'public-runs.csv').groupby('run').area.sum()
    fig,(a,b) = plt.subplots(1,2,figsize=(6.86,2.63))
    for trial,offset in [
        ('strict',(5,-2)),('strict32',(5,4)),('weighted',(5,10)),('repair',None),
        ('one',(4,-10)),('dual',(5,-12)),('dual1',(5,3)),('recover',(3,5)),('cuts',(-5,5)),
    ]:
        row=reserve.loc[trial]
        xy=row.area/1000,row.min_slack
        accepted=row.area<900000 and row.min_slack>=1
        a.scatter(*xy,marker='D' if accepted else 'o',color=TEAL if accepted else LINE,s=18)
        if offset is not None:
            label = 'weighted, repair' if trial == 'weighted' else trial
            a.annotate(label,xy,xytext=offset,ha='left' if offset[0]>0 else 'right',
                       textcoords='offset points',fontsize=7.3)
    a.axvline(900,color=RUST,lw=.75,ls='--')
    a.axhline(1,color=LINE,lw=.6,ls=':')
    a.set(xlabel='Weighted area (thousands)',ylabel='Minimum slack (units)',
          xlim=(855,977),ylim=(-.31,2.35),yticks=[0,1,2])
    for color,marker,series,label in [(RUST,'s',earlier,'Old-cap records'),(TEAL,'D',frozen,'Frozen ZIP runs')]:
        b.scatter(series.index,series/1000,marker=marker,color=color,s=28,label=label)
        for i,value in series.items():
            above = label=='Old-cap records'
            b.annotate(f'{value/1000:.1f}',(i,value/1000),xytext=(0,6 if above else -12),
                       textcoords='offset points',ha='center',fontsize=7.3)
    b.axhline(900,color=RUST,lw=.75,ls='--')
    b.set(xlabel='Run index within batch',ylabel='Weighted area (thousands)',xticks=[1,2,3],
          xlim=(.68,3.32),ylim=(866,918))
    b.legend(loc='upper right',frameon=False,fontsize=7.0)
    for ax,title in zip((a,b),['A  ·  Headroom policy trials','B  ·  Public area under recorded caps']):
        ax.set_title(title,loc='left',fontsize=8.7,weight='bold',pad=7)
        ax.grid(color=GRID,lw=.6)
        ax.tick_params(length=0,labelsize=7.4)
    fig.subplots_adjust(left=.11,right=.98,bottom=.21,top=.88,wspace=.41)
    export(fig,'integration_policy',out)


def recovery_evidence(out):
    frame=pd.read_csv(TIMING/'development.csv',dtype={'bank':str})
    versions=frame.version.unique().tolist()
    banks=frame.bank.unique().tolist()
    row_labels=['Previous delivery','Pair cofactors','Bidecomposition','Cover and grouped cofactors',
                'Reclaim scratch gates','Support up to 14 inputs','Remap reconstructed paths',
                'Balanced small-cone splits','Extended generous window']
    fig,ax=plt.subplots(figsize=(6.86,3.45))
    for row in frame.itertuples():
        i,j=versions.index(row.version),banks.index(row.bank)
        miss=row.valid-row.targets_met
        prospective=row.role=='prospective'
        ax.add_patch(Rectangle((j-.43,i-.36),.86,.72,
                     facecolor=PEACH if miss else 'white' if prospective else MINT,
                     edgecolor=RUST if miss else TEAL,linewidth=.65,
                     linestyle='--' if miss and prospective else '-'))
        if miss:
            ax.text(j,i,str(miss),ha='center',va='center',fontsize=7,color=RUST,weight='bold')
    ax.set(xlim=(-.56,len(banks)-.44),ylim=(len(versions)-.45,-.65),
           xticks=range(len(banks)),xticklabels=banks,yticks=range(len(versions)),yticklabels=row_labels)
    ax.tick_params(length=0,labelsize=7.25)
    plt.setp(ax.get_xticklabels(),rotation=57,ha='right')
    fig.legend(handles=[Line2D([],[],marker='s',ms=6,ls='',mfc=MINT,mec=TEAL,label='Development: 14/14'),
                        Line2D([],[],marker='s',ms=6,ls='',mfc='white',mec=TEAL,label='Prospective: 14/14'),
                        Line2D([],[],marker='s',ms=6,ls='',mfc=PEACH,mec=RUST,label='Number of misses shown')],
               loc='upper right',bbox_to_anchor=(.985,1),ncol=3,frameon=False,fontsize=7.4)
    fig.subplots_adjust(left=.309,right=.99,top=.87,bottom=.23)
    export(fig,'integration_recovery',out)

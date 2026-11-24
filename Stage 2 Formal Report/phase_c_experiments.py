"""Distributional and controlled-study figures from archived Phase C inputs."""
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
import numpy as np
import pandas as pd

from phase_c_data import BANKS, FINAL, REPORT, paired
from phase_c_plot_style import BLUE, GRID, INK, LINE, MINT, PEACH, RUST, SLATE, TEAL, export


COMPARATOR = 'R10.0'
EXAMPLE_CASES = [('stage2', 'case_005.txt'), ('stage2', 'case_013.txt'),
                 ('stage2', 'case_011.txt'), ('stage1', 'case_023.txt')]


def area_savings(frame):
    areas = paired(frame, 'area')
    return areas[COMPARATOR] - areas[FINAL]


def contributions(frame, repeat, out):
    savings = area_savings(frame).sort_values(ascending=False)
    order = np.arange(1, len(savings)+1)
    colors = [RUST if value < 0 else TEAL if bank == BANKS[1] else BLUE
              for (bank, _), value in savings.items()]
    top = savings.iloc[:3].sum()
    gross = savings.clip(lower=0).sum()
    penalty = -savings.clip(upper=0).sum()
    split = savings.groupby(level='bank').sum().reindex(BANKS)
    fig = plt.figure(figsize=(7.15, 3.14))
    grid = fig.add_gridspec(2, 2, width_ratios=[1.33,1], height_ratios=[1.12,1],
                           left=.095,right=.974,bottom=.16,top=.86,wspace=.30,hspace=.83)
    bars = fig.add_subplot(grid[:,0])
    cumulative = fig.add_subplot(grid[0,1])
    by_stage = fig.add_subplot(grid[1,1])
    bars.bar(order, savings, color=colors, width=.85, zorder=3)
    bars.axhline(0, color=LINE, lw=.65)
    losses = savings < 0
    bars.scatter(order[losses], savings[losses], s=10, marker='v', color=RUST, zorder=4)
    for i, value in enumerate(savings.iloc[:3],1):
        short = savings.index[i-1][1][5:8]
        bars.annotate(short, (i,value), xytext=(4,4), textcoords='offset points', fontsize=7.1)
    bars.set(title='A  ·  Signed case contributions', ylabel='Weighted area saved', xlabel='Case rank by savings')
    bars.set_ylim(-3500,savings.max()*1.18)
    bars.text(.97,.83, f'Gross {gross:,}\nRegressions −{penalty:,}', ha='right', va='top',
              transform=bars.transAxes, fontsize=8)
    bars.yaxis.set_major_formatter(lambda x,pos: f'{x/1000:g}k' if x else '0')
    cumulative.plot(order, savings.cumsum(), color=TEAL, lw=1.4)
    cumulative.scatter([3],[top],color=INK,s=16,zorder=4)
    cumulative.annotate(f'Top 3: {top:,}', xy=(3,top), xytext=(9,.47*gross),
                        arrowprops=dict(arrowstyle='-',lw=.6,color=LINE),fontsize=7.6)
    cumulative.set(title='B  ·  Cumulative net savings', xlabel='Case rank by savings', ylim=(0,1.10*gross))
    cumulative.yaxis.set_major_formatter(lambda x,pos: f'{x/1000:g}k' if x else '0')
    for i,(bank,value) in enumerate(split.items()):
        by_stage.barh(i,value,color=[BLUE,TEAL][i],height=.51)
        by_stage.text(value+.027*gross,i,f'{value:,}',va='center',fontsize=7.8,weight='bold')
    by_stage.set(title='C  ·  Net savings by bank', xlim=(0,1.06*gross),
                 xticks=[], yticks=[0,1], yticklabels=['Stage 1','Stage 2'])
    by_stage.invert_yaxis()
    for ax in [bars,cumulative,by_stage]:
        ax.title.set_fontsize(8.7)
        ax.title.set_weight('bold')
        ax.title.set_ha('left')
        ax.title.set_position((0,1))
        ax.tick_params(length=0,labelsize=7.3)
        if ax is not by_stage:
            ax.grid(axis='y',color=GRID,lw=.55)
    fig.text(.095,.955,f'Matched repeat {repeat} · Integrated Final versus R10.0',fontsize=8)
    export(fig,'contributions',out)


def tradeoffs(frame, repeat, out):
    area = paired(frame,'area').loc[EXAMPLE_CASES]
    delay = paired(frame,'delay').loc[EXAMPLE_CASES]
    runtime = paired(frame,'runtime_ms').loc[EXAMPLE_CASES]
    values = [100*(area[FINAL]/area[COMPARATOR]-1), delay[FINAL]-delay[COMPARATOR],
              runtime[FINAL]/runtime[COMPARATOR]]
    fig, ax = plt.subplots(figsize=(3.46,1.80))
    fig.subplots_adjust(left=.04,right=.98,top=.94,bottom=.12)
    ax.set(xlim=(0,10),ylim=(0,5))
    ax.axis('off')
    starts = [2.75,5.20,7.65]
    for x,title in zip(starts,['Area (%)','Delay','Time ratio']):
        ax.text(x+1.07,4.48,title,ha='center',va='center',weight='bold',fontsize=7.7)
    names = [f'S{i[-1]} / {case[5:8]}' for i,case in EXAMPLE_CASES]
    for j,name in enumerate(names):
        y=3.68-.85*j
        ax.text(.13,y,name,ha='left',va='center',fontsize=8)
        for k,(x,series,base) in enumerate(zip(starts,values,[0,0,1])):
            value=series.iloc[j]
            color=MINT if value < base else PEACH if value > base else GRID
            value_text=f'{value:.2f}×' if k == 2 else f'{value:+.0f}' if value else '0'
            ax.add_patch(Rectangle((x,y-.34),2.14,.68,facecolor=color,edgecolor='none'))
            ax.text(x+1.07,y,value_text,ha='center',va='center',fontsize=8)
    fig.text(.052,.046,f'Matched repeat {repeat} · Integrated Final versus R10.0',fontsize=7.1)
    export(fig,'tradeoffs',out)


def ablations(out):
    factorial = pd.read_csv(REPORT/'data/quota_factorial.csv').query('repeat == 1')
    totals = factorial[['extra_roots','reclaim','both','reverse']].sum()
    pairs = pd.read_csv(REPORT/'Research_Trial_Log/data/raw_controlled_pairs_verified.csv')
    order = ['r91_library','r91_repeat_shannon','r91_repeat_sop']
    r91 = (pairs.query('group == "r91" and repeat == 1 and bank in @BANKS')
           .groupby('candidate')[['area_saved','wins']].sum().loc[order])
    order = ['r101_off','r101_cap40','r101_cap80','r101_budget45']
    r101 = pd.read_csv(REPORT/'data/final_policy_tradeoff.csv').set_index('policy').loc[order]
    fig,axs = plt.subplots(1,3,figsize=(7.15,2.58),gridspec_kw={'width_ratios':[1,1.15,1.26]})
    a,b,c = axs
    for i,row in enumerate([[0,totals.extra_roots],[totals.reclaim,totals.both]]):
        for j,value in enumerate(row):
            a.add_patch(Rectangle((j-.5,i-.5),1,1,facecolor=MINT if value else GRID,
                                  edgecolor='white',linewidth=.9))
            a.text(j,i,f'{value:,}',ha='center',va='center',weight='bold')
    a.set(xlim=(-.5,1.5),ylim=(1.5,-.5),xticks=[0,1],xticklabels=['Original','Extra SOP'],
          yticks=[0,1],yticklabels=['No','Yes'])
    a.set_xlabel('Root quota',labelpad=2)
    a.set_ylabel('Reclaim time',labelpad=2)
    a.text(.5,-.43,f'Extra Shannon: {totals.reverse:,} saved',ha='center',transform=a.transAxes,fontsize=7.3)
    b.barh(range(3),r91.area_saved,color=[SLATE,BLUE,TEAL],height=.48)
    for j,area in enumerate(r91.area_saved):
        b.text(area+27,j,f'{area:,}',va='center',fontsize=7.4)
    b.set(yticks=range(3),yticklabels=[f'{name}\n{wins} wins' for name,wins in
                                     zip(['Library','Shannon','SOP'],r91.wins)],
          xlim=(0,r91.area_saved.max()*1.27),xticks=[0,500,1000,1500])
    b.set_xlabel('Weighted area saved',labelpad=2)
    b.invert_yaxis()
    c.scatter(r101.runtime_median_ratio,range(4),marker='D',s=21,color=TEAL,zorder=3)
    c.axvline(1,color=LINE,ls='--',lw=.65)
    for i,(ratio,penalty) in enumerate(zip(r101.runtime_median_ratio,r101.penalty50)):
        c.annotate(f'+{penalty:,.0f}',(ratio,i),xytext=(4,0),textcoords='offset points',
                   va='center',fontsize=7.4)
    c.set(yticks=range(4),yticklabels=['Off','40 roots','80 roots','45 ms'],
          xlim=(.936,1.032),xticks=[.94,.97,1.0,1.03],ylim=(3.55,-.55))
    c.set_xlabel('Median paired time ratio',labelpad=2)
    c.text(.5,-.43,'Labels: area penalty per 50 cases',ha='center',transform=c.transAxes,fontsize=7.3)
    for ax,title in zip(axs,['A  ·  R8.6 factorial','B  ·  R9.1 follow-up','C  ·  R10.1 policy']):
        ax.set_title(title,loc='left',fontsize=8.6,weight='bold',pad=6)
        ax.tick_params(length=0,labelsize=7.1)
    b.grid(axis='x',color=GRID,lw=.5)
    c.grid(axis='y',color=GRID,lw=.5)
    fig.text(.5,.955,'Independent studies · area differences within each study',ha='center',fontsize=8)
    fig.subplots_adjust(left=.109,right=.985,top=.80,bottom=.32,wspace=.68)
    export(fig,'ablations',out)

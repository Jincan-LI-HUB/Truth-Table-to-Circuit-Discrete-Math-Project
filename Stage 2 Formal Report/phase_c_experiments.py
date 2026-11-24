"""Distributional and controlled-study figures from archived Phase C inputs."""
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
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


def systems(frame, repeat, out):
    totals = frame.groupby('method')[['runtime_ms', 'area']].sum()
    methods = ['Z1', 'J51', COMPARATOR, FINAL]
    colors = [LINE, '#516E8A', RUST, TEAL]
    patterns = [':', '--', '-.', '-']
    fig, (a,b) = plt.subplots(1, 2, figsize=(7.15,2.58))
    slack_end = frame.delay_slack.max()+1
    frontier = []
    for method, row in totals.iterrows():
        if not ((totals.le(row).all(axis=1)) & (totals.lt(row).any(axis=1))).any():
            frontier.append((row.runtime_ms/1000,row.area/1000))
    a.plot(*zip(*sorted(frontier)), color=LINE, lw=.85, ls='--', zorder=1)
    for method, color, pattern in zip(methods,colors,patterns):
        row = totals.loc[method]
        x,y = row.runtime_ms/1000,row.area/1000
        a.scatter(x,y,marker='D' if method == FINAL else 'o',color=color,s=24,zorder=3)
        a.annotate(method,(x,y),xytext=(-5 if method == 'Z1' else 4,5),
                   textcoords='offset points',ha='right' if method == 'Z1' else 'left',
                   fontsize=7.7,color=color)
        slack = np.sort(frame.loc[frame.method.eq(method),'delay_slack'].to_numpy())
        x = np.r_[-1,slack,slack_end]
        y = np.r_[0,np.arange(1,len(slack)+1)*100/len(slack),100]
        b.step(x,y,where='post',color=color,ls=pattern,lw=1.45,label=method)
    a.set(xlabel='Summed synthesis time (s)',ylabel='Summed weighted area (thousands)',
          xlim=(5,42),ylim=(840,1165))
    b.set(xlabel='Slack: case target − circuit delay',ylabel='Cases at or below slack (%)',
          xlim=(-1,slack_end),ylim=(0,104),xticks=[0,5,10,15,20,25,30],yticks=[0,20,40,60,80,100])
    b.axvline(1,color=GRID,lw=.8,zorder=0)
    b.legend(loc='lower right',fontsize=7,frameon=False,handlelength=2.4)
    for ax,title in zip((a,b),['A  ·  Whole-system operating points','B  ·  Timing-slack distribution']):
        ax.set_title(title,loc='left',weight='bold',fontsize=8.8)
        ax.grid(color=GRID,lw=.6)
        ax.tick_params(length=0,labelsize=7.4)
    fig.text(.108,.977,f'Matched repeat {repeat} · 50 released cases per solver',va='top',fontsize=7.7)
    fig.subplots_adjust(left=.108,right=.987,top=.83,bottom=.205,wspace=.39)
    export(fig,'systems',out)


def tradeoffs(frame, repeat, out):
    area = paired(frame,'area')
    delay = paired(frame,'delay')
    absolute = area[FINAL]-area[COMPARATOR]
    relative = 100*absolute/area[COMPARATOR]
    y = delay[FINAL]-delay[COMPARATOR]
    fig, axs = plt.subplots(1,2,figsize=(7.15,2.65),sharey=True)
    labels = ['2/005','2/013','2/011','1/023']
    offsets = [[(6,-14),(6,6),(-8,7),(7,-12)],
               [(6,-14),(-3,9),(-4,7),(-7,-12)]]
    for ax,x,title,xlabel,offset in zip(
        axs, [absolute/1000,relative], ['A  ·  Absolute weighted area','B  ·  Relative to R10.0'],
        ['Area change (thousands)','Area change (%)'],offsets,
    ):
        ax.axhline(0,color=LINE,lw=.7)
        ax.axvline(0,color=LINE,lw=.7)
        for bank,marker,color in [('stage1','o',BLUE),('stage2','^',TEAL)]:
            ax.scatter(x.loc[bank],y.loc[bank],marker=marker,facecolor='none',edgecolor=color,
                       linewidth=.82,s=20,zorder=2)
        for key,name,move in zip(EXAMPLE_CASES,labels,offset):
            ax.scatter(x.loc[key],y.loc[key],marker='D',color=INK,s=18,zorder=4)
            ax.annotate(name,(x.loc[key],y.loc[key]),xytext=move,textcoords='offset points',
                        ha='right' if move[0]<0 else 'left',fontsize=7.3,color=INK)
        ax.set_title(title,loc='left',weight='bold',fontsize=8.6)
        ax.set_xlabel(xlabel)
        ax.set_ylim(min(-15,y.min()-3),max(20,y.max()+3))
        ax.grid(color=GRID,lw=.6,zorder=0)
        ax.tick_params(length=0,labelsize=7.4)
    axs[0].set_ylabel('Circuit delay change (units)')
    axs[0].set_xlim(min(absolute/1000)-6, max(absolute/1000)+10)
    axs[1].set_xlim(relative.min()-9,relative.max()+10)
    handles=[Line2D([],[],marker=m,ls='',mfc='none',mec=c,label=name,ms=5)
             for m,c,name in [('o',BLUE,'Stage 1'),('^',TEAL,'Stage 2')]]
    fig.legend(handles=handles,loc='upper right',bbox_to_anchor=(.985,.997),
               frameon=False,ncol=2,fontsize=7.6)
    fig.text(.10,.968,f'Matched repeat {repeat} · Integrated Final minus R10.0',va='top',fontsize=7.7)
    fig.subplots_adjust(left=.10,right=.98,top=.83,bottom=.21,wspace=.18)
    export(fig,'tradeoffs',out)


def ablations(out):
    factorial = pd.read_csv(REPORT/'data/quota_factorial.csv').query('repeat == 1')
    totals = factorial[['extra_roots','reclaim','both']].sum()
    pairs = pd.read_csv(REPORT/'Research_Trial_Log/data/raw_controlled_pairs_verified.csv')
    names = ['r91_library','r91_repeat_shannon','r91_repeat_sop']
    r91 = (pairs.query('group == "r91" and repeat == 1 and bank in @BANKS')
           .groupby('candidate')[['area_saved','wins']].sum().loc[names])
    names = ['r101_off','r101_cap40','r101_cap80','r101_budget45','r101_default']
    r101 = pd.read_csv(REPORT/'data/final_policy_tradeoff.csv').set_index('policy').loc[names]
    fig,(a,b,c) = plt.subplots(1,3,figsize=(7.15,2.56))
    a.plot([0,1],[0,totals.extra_roots],color=TEAL,lw=2.6,marker='o',ms=6)
    a.plot([0,1],[totals.reclaim,totals.both],color=INK,lw=.9,ls='--',
           marker='o',mfc='none',ms=8)
    a.text(.05,.94,'Solid: no reclaim\nDashed: reclaim',va='top',transform=a.transAxes,fontsize=7)
    a.set(xticks=[0,1],xticklabels=['Original','Extra SOP'],xlim=(-.10,1.14),
          ylim=(-160,3400),yticks=[0,1000,2000,3000],ylabel='Weighted area saved')
    for (_,row),name,offset in zip(r91.iterrows(),['Library','Shannon','SOP'],[(-5,5),(4,-1),(4,-1)]):
        b.scatter(row.wins,row.area_saved,color=TEAL if name=='SOP' else LINE,s=20)
        b.annotate(name,(row.wins,row.area_saved),xytext=offset,textcoords='offset points',
                   ha='right' if name=='Library' else 'left',fontsize=7.5)
    b.set(xlabel='Cases with lower area',ylabel='Net weighted area saved',
          xlim=(2,17),ylim=(400,1830),xticks=[5,8,11,15],yticks=[500,900,1300,1700])
    for (_,row),name,offset in zip(r101.iloc[:-1].iterrows(),['Off','40 roots','80 roots','45 ms'],
                                  [(4,3),(3,4),(-5,-2),(-5,6)]):
        x,y = row.runtime_median_ratio,row.penalty50
        c.scatter(x,y,color=TEAL,s=22,marker='D')
        c.annotate(name,(x,y),xytext=offset,textcoords='offset points',ha='left' if offset[0]>0 else 'right',
                   fontsize=7.4)
    c.axvline(1,color=LINE,ls='--',lw=.65)
    c.scatter(1,0,color=INK,marker='o',s=14)
    c.annotate('R10.0',(1,0),xytext=(-6,3),textcoords='offset points',ha='right',fontsize=7.1)
    c.set(xlabel='Median paired time ratio',ylabel='Area penalty per 50 cases',
          xlim=(.931,1.021),ylim=(-140,1850),xticks=[.94,.97,1.0],yticks=[0,500,1000,1500])
    for ax,title in zip((a,b,c),['A  ·  R8.6 factorial','B  ·  R9.1 follow-up','C  ·  R10.1 policy']):
        ax.set_title(title,loc='left',fontsize=8.6,weight='bold',pad=6)
        ax.tick_params(length=0,labelsize=7.1)
        ax.grid(axis='y',color=GRID,lw=.6)
    fig.subplots_adjust(left=.09,right=.981,top=.88,bottom=.22,wspace=.55)
    export(fig,'ablations',out)

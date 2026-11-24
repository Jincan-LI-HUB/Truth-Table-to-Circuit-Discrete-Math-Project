"""Phase C figures, adapted from the UFUG2106 Figure Reuse Kit.

Run from any directory. The default output is this report's figures directory.
Conceptual panels use constructed examples. All empirical marks use archived CSVs.
"""
import argparse
from pathlib import Path

from phase_c_plot_style import GRID, INK, LINE, RUST, SLATE, TEAL, export
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
import numpy as np
import pandas as pd

from phase_c_data import BANKS, DATA, FINAL, METHODS, REPORT, direct_memory, matched, paired
from phase_c_diagrams import architecture, bidecomposition, budgets, cofactors, cones, critical, framework, sop_cut
from phase_c_experiments import ablations, contributions, systems, tradeoffs
from phase_c_integration_trials import pass_evidence, policy_evidence, recovery_evidence


def area_comparison(repeat, out):
    summary = pd.read_csv(DATA / 'public_summary.csv')
    rows = summary.query('family == "matched" and repeat == @repeat').set_index(['bank', 'method'])
    fig = plt.figure(figsize=(3.46, 1.78))
    ax = fig.add_axes([.25, .31, .72, .62])
    values = rows.loc[('both', METHODS), 'full_area'].to_numpy()
    y = np.arange(len(values))
    ax.barh(y, values, color=[SLATE]*3 + [TEAL], height=.59)
    for i, value in enumerate(values):
        ax.text(value + 16000, i, f'{value:,}', va='center',
                weight='bold' if i == 3 else 'normal', fontsize=7.6)
    ax.set_yticks(y, ['Z1', 'J51', 'R10.0', 'Integrated\nFinal'])
    ax.invert_yaxis()
    ax.set(xlim=(0, max(values)*1.33), xticks=[0, 500000, 1000000],
           xticklabels=['0', '500k', '1M'])
    ax.tick_params(length=0, pad=3)
    ax.set_xlabel('Total weighted area', labelpad=4)
    fig.text(.25, .035, f'50 released cases · matched repeat {repeat}', fontsize=7)
    ax.set_axisbelow(True)
    ax.grid(axis='x', color=GRID, lw=.6)
    export(fig, 'area_comparison', out)


def casewise(frame, repeat, out):
    areas = paired(frame, 'area')
    fig, axes = plt.subplots(2, 1, figsize=(7.15, 2.58), sharex=True, sharey=True)
    baselines = ['Z1', 'R10.0']
    for ax, bank, title in zip(axes, BANKS, ['Stage 1', 'Stage 2']):
        a = areas.loc[bank]
        x = np.arange(1, len(a)+1)
        for baseline, offset, color, marker in [('Z1', -.15, INK, 'o'), ('R10.0', .15, TEAL, 's')]:
            change = 100*(a[FINAL]/a[baseline]-1)
            ax.scatter(x+offset, change, marker=marker, s=12, facecolor=color if offset > 0 else 'white',
                       edgecolor=color, linewidth=.8, zorder=3)
        decrease = [100*(1-a[FINAL].sum()/a[b].sum()) for b in baselines]
        ax.set_title(f'{title} · total area ↓ {decrease[0]:.1f}% vs Z1; ↓ {decrease[1]:.1f}% vs R10.0',
                     loc='left', fontsize=8.1, weight='bold', pad=3)
        ax.axhline(0, color=LINE, lw=.7)
        ax.grid(axis='y', color=GRID, lw=.6)
        ax.tick_params(length=0)
    axes[-1].set_xticks(range(1, 26))
    axes[-1].set_xlabel('Released case number', labelpad=3)
    fig.supylabel('Integrated area change (%)', fontsize=8, x=.016)
    fig.text(.093, .944, f'Matched repeat {repeat} · 25 cases per bank', fontsize=7.3)
    handles = [Line2D([], [], ls='', marker='o', ms=4, mfc='white', mec=INK, label='vs Z1'),
               Line2D([], [], ls='', marker='s', ms=4, color=TEAL, label='vs R10.0')]
    fig.legend(handles=handles, loc='upper right', bbox_to_anchor=(.991, .998), frameon=False, ncol=2)
    fig.subplots_adjust(left=.093, right=.987, top=.85, bottom=.205, hspace=.34)
    export(fig, 'casewise', out)


def resources(frame, repeat, out):
    times = paired(frame, 'runtime_ms')
    ram = paired(direct_memory(), 'peak_rss_kib')
    fig, axes = plt.subplots(1, 3, figsize=(7.15, 2.13), gridspec_kw={'width_ratios': [1, 1, 1.18]})
    for ax, dataset, title, ticks, bounds in [
        (axes[0], times, 'Paired synthesis time', [.2, .5, 1, 2, 5, 10], (.13, 21)),
        (axes[1], ram, 'Paired direct peak RSS', [.25, .5, 1, 2, 4], (.19, 7)),
    ]:
        for i, baseline in enumerate(METHODS[:-1]):
            ratios = dataset[FINAL] / dataset[baseline]
            jitter = np.linspace(-.17, .17, len(ratios))
            ax.scatter(ratios, i+jitter, s=6, alpha=.46, color=TEAL, linewidth=0)
            ax.scatter(ratios.median(), i, marker='D', facecolor='white', s=22, edgecolor=INK, linewidth=.8, zorder=4)
        ax.axvline(1, color=LINE, lw=.8, linestyle='--')
        ax.set_xscale('log')
        ax.set_xticks(ticks, [f'{tick:g}' for tick in ticks])
        ax.set_xlim(bounds)
        ax.set_yticks(range(3), METHODS[:-1])
        ax.set_ylim(2.45, -.45)
        ax.set_title(title, loc='left', fontsize=8.6, weight='bold', pad=7)
        ax.set_xlabel('Integrated / comparator', labelpad=3)
        ax.grid(axis='x', color=GRID, lw=.55)
        ax.tick_params(axis='both', length=0, labelsize=7)
        ax.tick_params(which='minor', length=0)
    ax = axes[2]
    for i, method in enumerate(METHODS):
        f = frame[frame.method.eq(method)]
        percent = 100*f.runtime_ms/f.time_limit_ms
        ax.scatter(percent, i+np.linspace(-.16,.16,len(f)), s=6, alpha=.45,
                   color=TEAL if method == FINAL else INK, linewidth=0)
        ax.scatter(percent.max(), i, marker='D', facecolor='white', s=22, edgecolor=INK, linewidth=.8, zorder=4)
    ax.axvline(100, color=RUST, lw=.8, linestyle='--')
    ax.set(xlim=(-3, 105), xticks=[0, 25, 50, 75, 100])
    ax.set_yticks(range(4), ['Z1', 'J51', 'R10.0', 'Integrated\nFinal'])
    ax.set_ylim(3.45, -.45)
    ax.set_title('Input time limit used', loc='left', fontsize=8.6, weight='bold', pad=7)
    ax.set_xlabel('Runtime / limit (%)', labelpad=3)
    ax.grid(axis='x', color=GRID, lw=.55)
    ax.tick_params(length=0, labelsize=7)
    fig.text(.077, .03, f'50 released cases per method · time uses matched repeat {repeat} · RSS uses separate process runs',
             fontsize=7.3)
    fig.subplots_adjust(left=.075, right=.985, bottom=.27, top=.8, wspace=.53)
    export(fig, 'resources', out)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repeat', type=int, choices=[1, 2], default=1)
    parser.add_argument('--out', type=Path, default=REPORT / 'figures')
    diagrams = {
        build.__name__: build for build in
        (framework, architecture, budgets, cones, sop_cut, critical, cofactors, bidecomposition,
         ablations, pass_evidence, policy_evidence, recovery_evidence)
    }
    observed = {
        'area_comparison': lambda frame, repeat, out: area_comparison(repeat, out),
        'casewise': casewise, 'resources': resources,
        'contributions': contributions, 'tradeoffs': tradeoffs, 'systems': systems,
    }
    parser.add_argument('--only', nargs='+', choices=[*diagrams, *observed],
                        help='regenerate only named figures')
    args = parser.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)
    selected = args.only or [*diagrams, *observed]
    frame = matched(args.repeat) if any(name in observed for name in selected) else None
    for name in selected:
        if name in diagrams:
            diagrams[name](args.out)
        else:
            observed[name](frame, args.repeat, args.out)
    print(f'Exported {len(selected)} Phase C figures for matched repeat {args.repeat} to {args.out}')


if __name__ == '__main__':
    main()

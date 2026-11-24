"""Phase C figures, adapted from the UFUG2106 Figure Reuse Kit.

Run from any directory. The default output is this report's figures directory.
Conceptual panels use constructed examples. All empirical marks use archived CSVs.
"""
import argparse
import json
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.patches import Ellipse, FancyArrowPatch, FancyBboxPatch
import numpy as np
import pandas as pd

from phase_c_data import BANKS, DATA, FINAL, METHODS, REPORT, direct_memory, matched, paired


PALETTE = json.loads((REPORT / 'palette.json').read_text())['colors']
INK, LINE, GRID = '#253746', '#637481', '#E4EAEB'
TEAL, RUST = '#226D65', '#934C3A'
BLUE, MINT, STONE, PEACH, SLATE = (
    PALETTE[key] for key in ('blue', 'mint', 'stone', 'peach', 'slate')
)
plt.rcParams.update({
    'font.family': 'DejaVu Sans', 'font.size': 8, 'axes.labelcolor': INK,
    'text.color': INK, 'xtick.color': INK, 'ytick.color': INK,
    'axes.spines.top': False, 'axes.spines.right': False,
    'axes.spines.left': False, 'axes.spines.bottom': False,
    'pdf.fonttype': 42, 'svg.fonttype': 'none',
})


def export(fig, name, out):
    # Fixed page widths match the manuscript. Tight cropping would change scale.
    for ext in ('pdf', 'svg', 'png'):
        fig.savefig(out / f'phase_c_{name}.{ext}', dpi=240, facecolor='white')
    plt.close(fig)


def schematic(width, height, xmax=10, ymax=10):
    fig = plt.figure(figsize=(width, height))
    ax = fig.add_axes([.01, .02, .98, .96], xlim=(0, xmax), ylim=(0, ymax))
    ax.axis('off')
    return fig, ax


def box(ax, x, y, w, h, label, fill=STONE, fs=8):
    ax.add_patch(FancyBboxPatch(
        (x-w/2, y-h/2), w, h, boxstyle='round,pad=.025,rounding_size=.10',
        facecolor=fill, edgecolor=LINE, linewidth=.65,
    ))
    ax.text(x, y, label, ha='center', va='center', fontsize=fs, linespacing=1.2)


def arrow(ax, start, end, style='-', bend=0):
    ax.add_patch(FancyArrowPatch(
        start, end, arrowstyle='-|>', mutation_scale=8, color=LINE, lw=.85,
        linestyle=style, shrinkA=0, shrinkB=0, connectionstyle=f'arc3,rad={bend}',
    ))


def architecture(out):
    fig, ax = schematic(7.15, 3.05, xmax=16, ymax=10)
    stages = [
        (9.35, .8, 'Parse packed truth table · set working target', STONE),
        (8.10, .82, 'Natural-order BDD → plain map → optional balance', BLUE),
        (6.84, .82, 'BDD probes, node screening and mapped refinement', BLUE),
        (5.59, .88, 'J51 portfolio and cone mixing (typed-cost guard)', BLUE),
        (4.30, .88, 'Guarded SOP polish → shared factors → compact reconsideration', MINT),
        (3.05, .82, 'Critical cuts if late to working target · compact mixing if eligible', PEACH),
        (1.82, .82, 'Late-output cofactor rescue if late to stated target', PEACH),
        (.57, .72, 'Write surviving netlist', STONE),
    ]
    for y, h, label, fill in stages:
        box(ax, 7.09, y, 9.35, h, label, fill)
    for (y, h, *_), (z, j, *__) in zip(stages, stages[1:]):
        arrow(ax, (7.09, y-h/2), (7.09, z+j/2))
    box(ax, 13.95, 8.10, 3.52, 1.02, 'Stream natural Shannon\nand return', STONE, 7.7)
    arrow(ax, (11.8, 8.10), (12.17, 8.10), '--')
    ax.text(13.95, 8.89, 'No complete incumbent', ha='center', fontsize=7.4)
    box(ax, 13.95, 6.55, 3.52, .95, 'Write incumbent\nand return', STONE, 7.7)
    arrow(ax, (11.8, 7.82), (12.18, 6.80), '--')
    ax.text(13.95, 7.22, 'Zero area and delay', ha='center', fontsize=7.4)
    ax.plot([12.08, 12.08], [1.66, 5.9], color=LINE, lw=.65)
    ax.text(12.42, 3.76, 'Optional steps can be\nskipped; completed\nincumbent survives.', va='center', fontsize=7.7)
    export(fig, 'architecture', out)


def budgets(out):
    fig, ax = schematic(7.15, 2.32, xmax=100, ymax=10)
    ax.text(1, 9.15, 'Main window', weight='bold', va='center')
    ax.text(23, 9.15, 'B = min(3300 ms, 0.45 L); 1800 ms without a positive limit', va='center')
    box(ax, 27, 7.46, 50, 1.04, 'Fallback and BDD portfolio (through B/2)', BLUE)
    box(ax, 76, 7.46, 45, 1.04, 'J51 through B, when supported', BLUE)
    ax.text(2, 6.33, 'Split when the typed-cost guard passes. BDD can use the full main window otherwise.', fontsize=7.8)
    ax.text(2, 5.18, 'BDD remainder: screening ≤ 35% of time left at entry; probes share ⅔ of the next remainder.', fontsize=7.8)
    ax.text(2, 4.14, 'Rank measured orders, then refine within the BDD deadline.', fontsize=7.8)
    ax.plot([2, 98], [3.53, 3.53], color=GRID, lw=1)
    ax.text(2, 2.82, 'Later steps', weight='bold')
    ax.text(23, 2.82, 'Elapsed-time admission guards for positive input limit L', va='center')
    for x, label, fill in [
        (13, 'SOP polish\n90 ms / 0.82 L', MINT),
        (37.5, 'Shared factors\n15 ms / ~0.80 L', MINT),
        (62, 'Critical repair\n100 ms / 0.72 L', PEACH),
        (86.5, 'Late-output rescue\n160 ms / 0.78 L', PEACH),
    ]:
        box(ax, x, 1.45, 22.7, 1.27, label, fill, 7.8)
    ax.text(2, .18, 'Caps and elapsed cutoffs are cooperative. Fallback construction and final writing can extend past them.', fontsize=7.6)
    export(fig, 'budgets', out)


def cones(out):
    fig, ax = schematic(3.46, 2.38, ymax=8)
    for x, color in [(3.18, TEAL), (6.78, INK)]:
        ax.add_patch(Ellipse((x, 4), 5.8, 4.62, facecolor=MINT if x < 5 else BLUE, edgecolor='none', alpha=.42))
        ax.add_patch(Ellipse((x, 4), 5.8, 4.62, facecolor='none', edgecolor=color, linestyle='--', lw=.65))
    for a, b in [((4, 7.03), (4.65, 5.65)), ((6, 7.03), (5.35, 5.65)),
                 ((1.9, 7.03), (2.7, 3.93)), ((8.1, 7.03), (7.3, 3.93)),
                 ((4.4, 4.92), (3.2, 3.93)), ((5.6, 4.92), (6.8, 3.93)),
                 ((2.7, 3.18), (2.7, 2.47)), ((7.3, 3.18), (7.3, 2.47))]:
        arrow(ax, a, b)
    for x, name in [(1.9, '$x_3$'), (4, '$x_1$'), (6, '$x_2$'), (8.1, '$x_4$')]:
        box(ax, x, 7.4, .9, .65, name)
    box(ax, 5, 5.28, 2.22, .7, '$g_s$ · AND', SLATE)
    for x, gate, root in [(2.7, '$g_1$ · OR', '$f_1$'), (7.3, '$g_2$ · OR', '$f_2$')]:
        box(ax, x, 3.55, 2.1, .7, gate, MINT)
        box(ax, x, 2.11, 1.0, .65, root)
    ax.text(5, .96, '$g_s$ has two live parent references.', ha='center')
    ax.text(5, .28, 'Remove cone 1: reclaim only the OR.', ha='center', weight='bold', color=TEAL)
    export(fig, 'cones', out)


def cofactors(out):
    fig, ax = schematic(3.46, 2.22, ymax=8)
    ax.text(1.64, 7.64, '$ab$', ha='center', weight='bold')
    ax.text(5.95, 7.64, 'Cofactor over $cd$', ha='center', weight='bold')
    groups = [('00', '$q_0=c$', MINT), ('01', '$q_0=c$', MINT),
              ('10', '$q_0=c$', MINT), ('11', '$q_1=c\\vee d$', BLUE)]
    for i, (bits, label, color) in enumerate(groups):
        y = 6.77 - i*.93
        box(ax, 1.64, y, 1.36, .64, bits)
        arrow(ax, (2.36, y), (3.37, y))
        box(ax, 5.95, y, 5.0, .64, label, color)
    ax.text(5, 2.66, '$h(a,b)=a\\wedge b$', ha='center', weight='bold', color=TEAL)
    ax.text(5, 1.63, '$f=(\\neg h\\wedge q_0)\\vee(h\\wedge q_1)$', ha='center', fontsize=9)
    ax.text(5, .55, '$f=c\\vee(a\\wedge b\\wedge d)$', ha='center', fontsize=9)
    export(fig, 'cofactors', out)


def critical(out):
    fig, ax = schematic(3.46, 2.40, ymax=9)
    ax.text(2.48, 8.61, 'Original', ha='center', weight='bold', color=RUST)
    ax.text(7.51, 8.61, 'Equivalent cut', ha='center', weight='bold', color=TEAL)
    for x, labels, color in [
        (2.48, [(r'$g_1=p\wedge a$', r'$t=3,\ R=2$'), (r'$g_2=g_1\wedge b$', r'$t=4,\ R=3$'),
                (r'$g_3=g_2\wedge c$', r'$t=5,\ R=4$')], PEACH),
        (7.51, [(r'$h_1=a\wedge b$', '$t=1$'), (r'$h_2=h_1\wedge c$', '$t=2$'),
                (r'$h_3=p\wedge h_2$', r'$t=3,\ R=4$')], MINT),
    ]:
        for i, (expr, timing) in enumerate(labels):
            y = 7.38 - i*1.7
            box(ax, x, y, 4.15, 1.03, f'{expr}\n{timing}', color)
            if i < 2:
                arrow(ax, (x, y-.53), (x, y-1.17))
    ax.text(5, 2.56, '$t(p)=2$; $t(a)=t(b)=t(c)=0$', ha='center')
    ax.text(5, 1.58, 'Unit AND delay · target 4', ha='center')
    ax.text(5, .57, 'Root slack changes from −1 to +1.', ha='center', weight='bold')
    export(fig, 'critical', out)


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
    args = parser.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)
    for build in [architecture, budgets, cones, cofactors, critical]:
        build(args.out)
    frame = matched(args.repeat)
    area_comparison(args.repeat, args.out)
    casewise(frame, args.repeat, args.out)
    resources(frame, args.repeat, args.out)
    print(f'Exported eight Phase C figures for matched repeat {args.repeat} to {args.out}')


if __name__ == '__main__':
    main()

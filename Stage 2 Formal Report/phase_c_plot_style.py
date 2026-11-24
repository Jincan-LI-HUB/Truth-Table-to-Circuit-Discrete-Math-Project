"""Established palette and vector export for Phase C."""
import json

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch

from phase_c_data import REPORT


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

"""Constructed examples and source schematics for Phase C."""
import matplotlib.pyplot as plt
from matplotlib.patches import Ellipse, FancyBboxPatch, Rectangle

from phase_c_plot_style import BLUE, GRID, INK, LINE, MINT, PEACH, RUST, SLATE, STONE, TEAL
from phase_c_plot_style import arrow, box, export, schematic


def label(ax, x, y, value, **kwargs):
    ax.text(x, y, value, **(dict(ha='center', va='center', fontsize=8) | kwargs))


def framework(out):
    fig, ax = schematic(3.46, 1.91, xmax=10, ymax=7)
    box(ax, 5, 6.12, 9.15, .92, 'Function $F$ fixes the equivalence class', STONE)
    box(ax, 2.54, 4.11, 4.2, 1.35, 'Generate equivalent\nstructures', BLUE)
    box(ax, 7.45, 4.11, 4.2, 1.35, 'Evaluate live area\nand arrival times', MINT)
    arrow(ax, (5, 5.64), (2.54, 4.82))
    arrow(ax, (4.68, 4.11), (5.32, 4.11))
    box(ax, 2.54, 1.94, 4.2, 1.30, 'Time and memory\nlimit exploration', PEACH)
    box(ax, 7.45, 1.94, 4.2, 1.30, 'Retain a completed\ncandidate', MINT)
    arrow(ax, (2.54, 2.62), (2.54, 3.41), '--')
    arrow(ax, (7.45, 3.41), (7.45, 2.62))
    label(ax, 5, .42, 'Timing feasibility is tested on the whole network.', fontsize=7.5)
    export(fig, 'framework', out)


def architecture(out):
    fig, ax = schematic(7.15, 2.76, xmax=100, ymax=30)
    label(ax, 2, 28.5, 'Candidate and state relationships', ha='left', weight='bold')
    box(ax, 15.5, 23, 26.4, 5.7, 'Construct and map\nBDD orders and J51 portfolio', BLUE)
    box(ax, 49.7, 23, 28.5, 5.7, 'Global evaluation\nWhole-network area and delay', MINT)
    box(ax, 83.7, 23, 26.1, 5.7, 'Incumbent $G$\nWorking-target choice', MINT)
    box(ax, 83.7, 14.6, 26.1, 5.7, 'Compact candidate $C$\nBest designated legal area', STONE)
    box(ax, 15.5, 14.6, 26.4, 5.7, 'Change structure\nMix roots · SOP · shared factors', BLUE)
    box(ax, 49.7, 14.6, 28.5, 5.7, 'Recover timing\nCritical cuts · late-output rescue', PEACH)
    for start, end, style in [
        ((29,23),(35.3,23),'-'), ((64.2,23),(70.4,23),'-'),
        ((63.3,21.4),(70.4,16.2),'--'), ((29,15.9),(35.3,20.3),'-'),
        ((49.7,17.52),(49.7,20.05),'-'), ((70.4,14.6),(64.1,14.6),'--'),
    ]:
        arrow(ax, start, end, style)
    ax.plot([96.95,98.5,98.5,15.5],[23,23,10.35,10.35],color=LINE,lw=.75,ls='--')
    for x in [15.5,49.7]:
        arrow(ax,(x,10.35),(x,11.68),'--')
    label(ax, 55, 8.95, 'Incumbent feeds eligible rewrites and repairs', fontsize=7.2)
    ax.plot([2,97], [7.65,7.65], color=GRID, lw=.8)
    label(ax, 2, 6.55, 'Sequential execution', ha='left', weight='bold')
    steps = ['Complete fallback', 'BDD probes\nthen J51', 'SOP polish\nthen shared factors',
             'Reconsider compact\nthen critical repair', 'Stated-target rescue\nthen write']
    positions = [10.3,29.7,49.3,69,89]
    for x, item in zip(positions, steps):
        box(ax, x, 3.96, 17.3, 3.1, item)
    for a, b in zip(positions, positions[1:]):
        arrow(ax, (a+8.8,3.96), (b-8.8,3.96))
    label(ax, 2, .8, 'Guarded stages may be skipped. No complete fallback → stream and return. Zero cost and delay → write and return.',
          ha='left', fontsize=7.5)
    export(fig, 'architecture', out)


def budgets(out):
    fig, ax = schematic(7.15, 2.43, xmax=100, ymax=31)
    label(ax, 2, 29.7, 'Main search window', ha='left', weight='bold')
    label(ax, 98, 29.7, r'$B=\min(3300\,\mathrm{ms},0.45L)$; 1800 ms without positive $L$',
          ha='right', fontsize=7.7)
    for y, entries, descriptor in [
        (24.9, [(37,34,'Fallback and BDD',BLUE), (71,34,'J51',MINT)], 'Typed guard passes'),
        (20.7, [(54,68,'Fallback and BDD',BLUE)], 'Typed guard fails'),
    ]:
        label(ax, 2, y, descriptor, ha='left', fontsize=7.6)
        for x, w, text, fill in entries:
            box(ax, x, y, w-1, 2.5, text, fill)
    for x, tick in [(20,'$0$'),(54,'$B/2$'),(88,'$B$')]:
        label(ax, x, 17.8, tick, fontsize=7.6)
    label(ax, 2, 15.8, 'Screen → map shortlisted orders → refine measured candidates',
          ha='left', fontsize=7.7)
    ax.plot([2,98], [14.05,14.05], color=GRID, lw=.8)
    label(ax, 2, 12.5, 'Later optional steps', ha='left', weight='bold')
    label(ax, 98, 12.5, r'At entry $e$, room before elapsed cutoff $cL$ is $cL-e$', ha='right', fontsize=7.7)
    for x, title, cap, cutoff, fill in [
        (13.5,'SOP polish','90 ms and 0.06 L','0.82 L',MINT),
        (37.8,'Shared factors','15 ms','~0.80 L',MINT),
        (62.2,'Critical repair','100 ms','0.72 L',PEACH),
        (86.5,'Late-output rescue','160 ms','0.78 L',PEACH),
    ]:
        box(ax, x, 8.25, 22.5, 5.6, f'{title}\ncap {cap}\ncutoff {cutoff}', fill, 7.5)
    label(ax, 2, 3.56, 'Admitted allowance: min(cap, remaining room).', ha='left', fontsize=7.7)
    arrow(ax, (66,3.75), (96,3.75))
    ax.plot([70,91], [3.75,3.75], color=TEAL, lw=3, solid_capstyle='butt')
    for x,tick in [(70,'entry $e$'),(91,'cutoff $cL$')]:
        ax.plot([x,x],[3.18,4.32],color=INK,lw=.7)
        label(ax, x, 2.1, tick, fontsize=7.3)
    label(ax, 2, 1.27, 'Cooperative checks. Nominal optional windows can overlap.', ha='left', fontsize=7.7)
    export(fig, 'budgets', out)


def cones(out):
    fig, ax = schematic(7.15, 2.46, xmax=100, ymax=27)
    label(ax, 23.7, 25.65, 'Live references charge shared gates once', weight='bold')
    label(ax, 75.7, 25.65, 'A joint switch can cross a local area barrier', weight='bold')
    ax.plot([49,49], [2.9,26.2], color=GRID, lw=.9)
    for center in [14.5,33]:
        ax.add_patch(Ellipse((center,17.3),25.5,11.5, facecolor='none', edgecolor=LINE,
                             linestyle='--', linewidth=.6, alpha=.55))
    box(ax, 23.6, 21.5, 11.2, 2.9, '$g_s$ · AND', MINT)
    for x, title, root, fill in [(13.2,'$g_1$ · OR','$f_1$',PEACH),(33.8,'$g_2$ · OR','$f_2$',STONE)]:
        box(ax, x, 16.6, 10.5, 2.7, title, fill)
        box(ax, x, 12.1, 6.5, 2.5, root)
        arrow(ax, (23.6,19.95), (x,18.02))
        arrow(ax, (x,15.16), (x,13.45))
    label(ax, 23.7, 7.85, r'Drop $f_1$: $g_1$ 1 → 0, $g_s$ 2 → 1')
    label(ax, 23.7, 4.65, r'Restore $f_1$: $g_1$ 0 → 1, $g_s$ 1 → 2')
    label(ax, 23.7, 1.55, 'Shared AND stays · OR charge changes ±3', color=TEAL, weight='bold')
    label(ax, 75.6, 22.65, r'$P=(x\vee y)\wedge(x\vee z)$,  $Q=x\vee(y\wedge z)$', fontsize=8.4)
    label(ax, 75.6, 20.28, r'Each output chooses $P$ or $Q$ before its final AND.', fontsize=7.6)
    for x, y, text, fill in [(61,15.7,'$(0,0)$ · 5',STONE),(89.6,15.7,'$(1,0)$ · 7',PEACH),
                             (61,8.2,'$(0,1)$ · 7',PEACH),(89.6,8.2,'$(1,1)$ · 4',MINT)]:
        box(ax, x, y, 15.1, 3.25, text, fill)
    arrow(ax, (68.8,15.7), (81.8,15.7))
    arrow(ax, (61,14), (61,9.95))
    arrow(ax, (68.5,14.47), (81.8,9), '--')
    label(ax, 75.2, 17.7, 'reject', color=RUST, fontsize=7.1)
    label(ax, 58.8, 11.9, 'reject', ha='right', color=RUST, fontsize=7.1)
    label(ax, 76, 9.7, 'joint', va='top', color=TEAL, fontsize=7.1)
    label(ax, 75.4, 3.65, 'Each label gives state and area. All delays are 3.', fontsize=7.5)
    label(ax, 75.4, 1.35, 'Dashed: complete-trial comparison.', fontsize=7.5)
    export(fig, 'cones', out)


def draw_dag(ax, inputs, gates, links, outputs):
    ports = {name: (x,y,.051,.036) for name,(x,y,_) in (inputs | outputs).items()}
    ports.update({name: (x,y,.090,.046) for name,(x,y,*_) in gates.items()})

    def edge(port, toward):
        x,y,w,h = port
        dx,dy = toward[0]-x,toward[1]-y
        extent = 1/max(abs(dx)/w,abs(dy)/h)
        return x+extent*dx,y+extent*dy

    for source, sink, *routing in links:
        start,end = ports[source],ports[sink]
        route = routing[0] if routing else 0
        if isinstance(route, tuple):
            path = [edge(start,route[0]),*route,edge(end,route[-1])]
            ax.plot(*zip(*path[:-1]),color=LINE,lw=.85)
            arrow(ax,path[-2],path[-1])
        else:
            arrow(ax,edge(start,end),edge(end,start),bend=route)
    for name,(x,y,text) in inputs.items():
        label(ax, x, y, text, fontsize=7.6, color=RUST if name == 'p' else INK,
              weight='bold' if name == 'p' else 'normal')
    for x,y,text,*fill in gates.values():
        ax.add_patch(FancyBboxPatch((x-.081,y-.039),.162,.078,
                     boxstyle='round,pad=.004,rounding_size=.014',
                     facecolor=fill[0] if fill else STONE, edgecolor=LINE, linewidth=.65))
        label(ax, x, y, text, fontsize=7.25)
    for x,y,text in outputs.values():
        label(ax, x, y, text, weight='bold')


def dag_panels(n, width, height, left=.025, right=.975, bottom=.12, top=.90):
    fig, axs = plt.subplots(1, n, figsize=(width,height))
    fig.subplots_adjust(left=left, right=right, top=top, bottom=bottom, wspace=.14)
    for ax in axs:
        ax.set(xlim=(0,1),ylim=(0,1))
        ax.axis('off')
    return fig, axs


def sop_cut(out):
    fig, axs = dag_panels(3, 7.15, 2.77, bottom=.15)
    inputs = {'a':(.17,.88,'$a$'),'b':(.46,.88,'$b$'),'c':(.82,.88,'$c$')}
    shared = {'ab':(.28,.63,'AND',MINT)}
    common = [('a','ab'),('b','ab'),('ab','s')]
    panels = [
        ('Original · area 10', shared | {'nb':(.59,.67,'NOT',PEACH),'mid':(.74,.51,'AND',PEACH),
                                        'long':(.74,.35,'AND',PEACH),'r_gate':(.57,.18,'OR',PEACH)},
         common+[('b','nb'),('nb','mid'),('c','mid'),('mid','long'),
                 ('a','long',((.07,.78),(.07,.34))),
                 ('ab','r_gate'),('long','r_gate')]),
        ('SOP · area 7', shared | {'ac':(.70,.61,'AND',BLUE),'r_gate':(.57,.18,'OR',BLUE)},
         common+[('a','ac',-.12),('c','ac'),('ab','r_gate'),('ac','r_gate')]),
        ('Inverted SOP · area 11', shared | {'na':(.12,.44,'NOT'),'nb':(.53,.67,'NOT'),
                                            'nc':(.83,.67,'NOT'),'both':(.71,.51,'AND'),
                                            'off':(.57,.35,'OR'),'r_gate':(.57,.18,'NOT')},
         common+[('a','na'),('b','nb'),('c','nc'),('nb','both'),('nc','both'),
                 ('na','off'),('both','off'),('off','r_gate')]),
    ]
    for ax,(title,nodes,links) in zip(axs,panels):
        label(ax, .5, 1, title, weight='bold')
        draw_dag(ax, inputs, nodes, links+[('r_gate','r')], {'s':(.28,.45,'$s$'),'r':(.57,.015,'$r$')})
    fig.text(.5, .112, 'Old → SOP: green shared 2 · peach removed 8 · blue constructed 5',
             ha='center', fontsize=8)
    fig.text(.5, .066, 'Gate prices: AND 2 · OR 3 · NOT 1',
             ha='center', fontsize=7.7)
    fig.text(.5, .020, 'Mask 0xA8 · arrivals (r, s) = (7, 5) · SOP area change: local −1, global −3',
             ha='center', fontsize=8, weight='bold')
    export(fig, 'sop_cut', out)


def critical(out):
    fig, axs = dag_panels(2, 3.46, 2.72, left=.06, right=.94, bottom=.17, top=.90)
    for ax,title,order,times,fill in [
        (axs[0],'Original',['p','a','b','c'],[3,4,5],PEACH),
        (axs[1],'Reassociated',['a','b','c','p'],[1,2,3],MINT),
    ]:
        ink = RUST if ax is axs[0] else TEAL
        label(ax, .52, 1.02, title, weight='bold', color=ink)
        inputs = {name:(x,y,'$'+name+'$  '+str(2 if name == 'p' else 0))
                  for name,(x,y) in zip(order,[(.21,.87),(.52,.87),(.21,.61),(.21,.36)])}
        gates = {f'g{i}':(.52,y,'AND',fill) for i,y in enumerate([.71,.46,.21])}
        links = [(order[0],'g0'),(order[1],'g0'),(order[2],'g1'),('g0','g1'),
                 (order[3],'g2'),('g1','g2'),('g2','r')]
        draw_dag(ax, inputs, gates, links, {'r':(.52,.035,'$r$')})
        for y,t,r in zip([.71,.46,.21],times,[2,3,4]):
            label(ax, .67, y, f'({t}, {r})', ha='left', fontsize=7.4)
        label(ax, .52, -.106, f'Root slack {4-times[-1]:+}'.replace('-', '−'),
              weight='bold', color=ink, fontsize=7.7)
    fig.text(.50, .022, 'Leaf: arrival · Gate: (arrival, required)', ha='center', fontsize=7.4)
    export(fig, 'critical', out)


def truth_matrix(ax, rows, columns, values, x, y, width, height, colors):
    dx,dy = width/len(columns),height/len(rows)
    for j,val in enumerate(columns):
        label(ax, x+(j+.5)*dx, y+.42*dy, val, weight='bold', fontsize=7.4)
    for i,row in enumerate(rows):
        label(ax, x-.44*dx, y-(i+.5)*dy, row, weight='bold', fontsize=7.4)
        for j,val in enumerate(values[i]):
            ax.add_patch(Rectangle((x+j*dx,y-(i+1)*dy),dx,dy,
                         facecolor=colors[i][j],edgecolor='white',linewidth=.9))
            label(ax, x+(j+.5)*dx, y-(i+.5)*dy, str(val), fontsize=8.2)


def cofactors(out):
    fig, ax = schematic(3.46, 2.38, xmax=13, ymax=12)
    bits = [(0,0),(0,1),(1,0),(1,1)]
    names = [f'{a}{b}' for a,b in bits]
    values = [[c | (a & b & d) for c,d in bits] for a,b in bits]
    label(ax, 4.9, 11.27, 'Free variables $cd$', weight='bold')
    label(ax, 1.1, 9.6, '$ab$', fontsize=7.5)
    truth_matrix(ax, names, names, values, 2.4, 9, 5, 5.3, [[MINT]*4]*3+[[BLUE]*4])
    label(ax, 9, 10.16, 'Residual', weight='bold')
    label(ax, 11.5, 10.16, 'Selector', weight='bold')
    for i,(row,select) in enumerate([('$q_0=c$','0')]*3+[(r'$q_1=c\vee d$','1')]):
        y = 9-(i+.5)*1.325
        label(ax, 9, y, row)
        label(ax, 11.5, y, select, color=TEAL, weight='bold')
    label(ax, 6.5, 2.55, r'$h(a,b)=a\wedge b$', weight='bold', color=TEAL)
    label(ax, 6.5, 1, r'$f=(\neg h\wedge q_0)\vee(h\wedge q_1)=c\vee(h\wedge d)$', fontsize=8.5)
    export(fig, 'cofactors', out)


def bidecomposition(out):
    fig, axs = dag_panels(3, 3.46, 2.11, left=.055, right=.98, bottom=.18, top=.82)
    assignments = [(0,0),(0,1),(1,0),(1,1)]
    names = [f'{a}{b}' for a,b in assignments]
    u = [a | b for a,b in assignments]
    v = [a & b for a,b in assignments]
    for ax,title,combine,highlight,text in [
        (axs[0],'AND',lambda a,b:a&b,1,'One rectangle'),
        (axs[1],'OR',lambda a,b:a|b,0,'Zero rectangle'),
        (axs[2],'XOR',lambda a,b:a^b,1,'Even on every\n2-by-2 slice'),
    ]:
        label(ax, .53, 1.13, title, weight='bold')
        values = [[combine(a,b) for b in v] for a in u]
        colors = [[MINT if bit == highlight else STONE for bit in row] for row in values]
        truth_matrix(ax, names, names, values, .25, .83, .71, .69, colors)
        label(ax, .59, -.02, text, fontsize=7.0)
    fig.text(.5, .025, r'Rows $x_1x_2$: $g=x_1\vee x_2$ · columns $y_1y_2$: $h=y_1\wedge y_2$',
             ha='center', fontsize=7.1)
    export(fig, 'bidecomposition', out)

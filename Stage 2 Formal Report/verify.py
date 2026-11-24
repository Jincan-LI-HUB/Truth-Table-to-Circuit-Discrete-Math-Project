"""Verify the archived evidence and constructed examples used by the report."""
from itertools import product
from pathlib import Path
import pandas as pd

from build_casewise import OUTPUT, render
from phase_c_data import ARCHIVE, BANKS, DATA, FINAL, METHODS, direct_memory, matched, paired

R=Path(__file__).resolve().parent
D=pd.read_csv(R/'data/matched_case_metrics.csv')
for rep in [1,2]:
 p=D[D.repeat==rep].pivot(index='case_id',columns='method_id',values=['area','passed','target_met'])
 assert len(p)==50 and int(p['passed'].Z1.sum())==50 and int(p['passed'].S100.sum())==50
 assert int(p['target_met'].Z1.sum())==50 and int(p['target_met'].S100.sum())==50
 assert int(p['passed'].J51.sum())==49
 z=p['area'].Z1.sum(); s=p['area'].S100.sum()
 assert (int(z),int(s))==({1:(1144244,1019547),2:(1145191,1019883)}[rep])
 print(f'historical matched repeat {rep}: Z1={int(z):,}, R10={int(s):,}, saved={int(z-s):,}')
P=D.query('repeat==1').pivot(index='case_id',columns='method_id',values=['area','synth_runtime_ms'])
d=P['area'].Z1-P['area'].S100
assert int((d>0).sum())==18 and int((d<0).sum())==32
assert int(d.clip(lower=0).sum())==160696 and int(-d.clip(upper=0).sum())==35999
assert int((P['synth_runtime_ms'].S100<P['synth_runtime_ms'].Z1).sum())==49
assert float(d.median())==-54.5
for bank in ('stage1','stage2'):
    z=d[d.index.str.startswith(bank+'/')]
    assert (int((z>0).sum()),int((z<0).sum()))==(9,16)
    area_split={
        'stage1':(81805,18364,63441),
        'stage2':(78891,17635,61256),
    }[bank]
    assert (int(z.clip(lower=0).sum()),int(-z.clip(upper=0).sum()),int(z.sum()))==area_split
assert int(d.max())==39516 and int(d.min())==-8003
assert int(d.nlargest(3).sum())==94004  # Three largest gains = 58.5% of gross wins.
print('historical repeat 1: benefits=18, regressions=32, positive=160,696, negative=35,999')
Q=pd.read_csv(R/'data/quota_factorial.csv').query('repeat==1')
assert (int(Q.extra_roots.sum()),int(Q.reclaim.sum()),int(Q.both.sum()),int(Q.reverse.sum()))==(2844,0,2844,20)
assert Q.interaction.eq(Q.both - Q.extra_roots - Q.reclaim).all()
assert Q.interaction.sum() == 0
R90=pd.read_csv(R/'data/official_r90_r100_casewise.csv').query('run==1')
R90['id']=R90.bank+'/'+R90.case
A=R90.pivot(index='id',columns='method',values='area')
q=A.r90_frozen-A.r100_default
assert len(q)==50 and int(q.sum())==1587 and int((q>0).sum())==8 and int((q<0).sum())==0
print('official R9/R10 paired first repeat: eight improvements; saved=1,587')

# Verify the two explicitly documented truth-mask conventions against all rows.
for a in (0, 1):
 for b in (0, 1):
  for c in (0, 1):
   f = int(bool(b or ((not a) and c)))
   if a == b == c == 0:
    mask_stage1 = mask_r10 = 0
   mask_stage1 |= f << (4*a + 2*b + c)
   mask_r10 |= f << (a + 2*b + 4*c)
assert mask_stage1 == 0xCE and mask_r10 == 0xDC
print('truth-mask conventions: MSB-first=0xCE, source LSB-first=0xDC')

# Both matched repeats preserve the same per-case area-gain sign pattern.
A = D.pivot(index='case_id', columns=['repeat','method_id'], values='area')
d1 = A[(1,'Z1')] - A[(1,'S100')]
d2 = A[(2,'Z1')] - A[(2,'S100')]
assert int(((d1 > 0) == (d2 > 0)).sum()) == 50
assert int((d2 > 0).sum()) == 18 and int((d2 < 0).sum()) == 32
assert int(d2.sum()) == 125308
print('two-repeat area-difference signs: 50/50 unchanged')

# Recompute the final policy comparison directly from archived native
# matched-case summaries, expressed per original 50 cases (100 / 2).
P=pd.read_csv(R/'data/final_policy_tradeoff.csv')
assert len(P)==6 and P.policy.nunique()==6 and (P.paired==100).all()
assert (P.penalty50 == -P.area_saved_total/2).all()
saved=P.set_index('policy')['penalty50'].to_dict()
assert (saved['r101_off'],saved['r101_cap40'],saved['r101_cap80'],saved['r101_budget45'])==(1587,1008,602,241)
ratios=P.set_index('policy')['runtime_median_ratio']
assert ratios['r101_off']<ratios['r101_cap40']<1 and ratios['r101_budget45']>1
assert [round(ratios[k], 3) for k in ('r101_off', 'r101_cap40', 'r101_cap80', 'r101_budget45')] == [
    .942, .987, .988, 1.009,
]
print('paired final-policy trade-off: validated from 100 observations per policy')

assert OUTPUT.read_text(encoding='utf-8') == render(), 'Regenerate casewise.tex'

summary = pd.read_csv(DATA/'public_summary.csv').query('family == "matched"')
pair_summary = pd.read_csv(DATA/'matched_pairs.csv').set_index(['repeat', 'baseline'])
expected_area = {
    1: (1127450, 1037549, 1019547, 872813),
    2: (1127196, 1037549, 1019547, 872919),
}
for repeat in (1, 2):
    frame = matched(repeat)
    integrated = frame[frame.method.eq(FINAL)]
    assert integrated.independent_replay.eq(1).all()
    assert tuple(frame.groupby('method').area.sum()[METHODS]) == expected_area[repeat]
    assert (integrated.delay.median(), integrated.delay.max(), integrated.delay_slack.min()) == (50, 85, 1)
    assert frame.delay_slack.eq(frame.target - frame.delay).all()
    assert (frame.time_limit_ms > 0).all()
    assert frame.ram_limit_kib.eq(0).all()
    for row in summary[summary.repeat.eq(repeat)].itertuples():
        sample = frame[frame.method.eq(row.method)]
        if row.bank != 'both':
            sample = sample[sample.bank.eq(row.bank)]
        assert len(sample) == row.count == row.targets_met == row.evaluator_pass == row.runtime_count
        assert sample.area.sum() == row.full_area
        assert abs(sample.runtime_ms.sum()/1000 - row.runtime_sum_s) < 1e-6
        assert abs(100*(sample.runtime_ms/sample.time_limit_ms).max() - row.max_budget_pct) < 0.0001
        assert sample.delay_slack.min() == row.min_target_slack
    area = paired(frame, 'area')
    delay = paired(frame, 'delay')
    runtime = paired(frame, 'runtime_ms')
    for baseline in METHODS[:-1]:
        row = pair_summary.loc[repeat, baseline]
        area_diff = area[FINAL] - area[baseline]
        delay_diff = delay[FINAL] - delay[baseline]
        assert len(area) == row.jointly_passing_cases == row.runtime_ratio_count
        assert area_diff.sum() == row.final_minus_base_area
        assert (area_diff.lt(0).sum(), area_diff.eq(0).sum(), area_diff.gt(0).sum()) == (
            row.final_area_lower, row.final_area_equal, row.final_area_higher,
        )
        assert (delay_diff.lt(0).sum(), delay_diff.eq(0).sum(), delay_diff.gt(0).sum()) == (
            row.final_delay_lower, row.final_delay_equal, row.final_delay_higher,
        )
        assert abs((runtime[FINAL]/runtime[baseline]).median() - row.median_case_runtime_ratio) < 1e-6
        assert abs(runtime[FINAL].sum()/runtime[baseline].sum() - row.sum_runtime_ratio_common_cases) < 1e-6
    j51 = frame[frame.method.eq('J51')].set_index(['bank', 'case'])
    assert (j51.runtime_ms/j51.time_limit_ms).idxmax() == ('stage2', 'case_016.txt')
    assert round(100*(j51.runtime_ms/j51.time_limit_ms).max(), 2) == (97.92 if repeat == 1 else 96.93)
    assert round(100*(1-area[FINAL].sum()/area.Z1.sum()), 1) == 22.6
    assert round(100*(1-area[FINAL].sum()/area['R10.0'].sum()), 1) == 14.4
    savings = area['R10.0'] - area[FINAL]
    gross = savings[savings > 0].sum()
    penalty = -savings[savings < 0].sum()
    top = savings.nlargest(3)
    by_bank = savings.groupby(level='bank').sum()
    expected_savings = (147385, 651, 146734, 32358, 114376) if repeat == 1 else (
        147279, 651, 146628, 32358, 114270,
    )
    assert (gross, penalty, savings.sum(), *by_bank.reindex(BANKS)) == expected_savings
    assert (sum(savings > 0), sum(savings == 0), sum(savings < 0)) == (43, 1, 6)
    assert list(top.index) == [('stage2', f'case_{i:03}.txt') for i in (5, 13, 11)]
    assert top.sum() == 89530
    assert round(100 * top.sum()/gross, 2) == (60.75 if repeat == 1 else 60.79)
    if repeat == 1:
        assert round(100 * by_bank.stage2/savings.sum(), 2) == 77.95
    for key, (old_a, new_a, old_d, new_d, target) in {
        ('stage2','case_005.txt'): (102889, 60744, 68, 68, 69),
        ('stage2','case_013.txt'): (115706, 82364, 66, 68, 78),
        ('stage2','case_011.txt'): (52463, 38420, 62, 78, 79),
        ('stage1','case_023.txt'): (125, 202, 22, 15, 24),
    }.items():
        assert tuple(area.loc[key, ['R10.0', FINAL]]) == (old_a, new_a)
        assert tuple(delay.loc[key, ['R10.0', FINAL]]) == (old_d, new_d)
        assert tuple(paired(frame, 'target').loc[key, ['R10.0', FINAL]]) == (target, target)
        assert runtime.at[key, FINAL] > runtime.at[key, 'R10.0']
    if repeat == 1:
        for bank, expected in zip(BANKS, [(493224, 16.2, 6.2), (379589, 29.5, 23.2)]):
            bank_area = area.loc[bank].sum()
            assert (bank_area[FINAL], round(100*(1-bank_area[FINAL]/bank_area.Z1), 1),
                    round(100*(1-bank_area[FINAL]/bank_area['R10.0']), 1)) == expected

rss = paired(direct_memory(), 'peak_rss_kib')
assert len(rss) == 50 and not rss.isna().any().any()
assert (rss[FINAL].median(), rss[FINAL].max()) == (7742, 58912)
assert (rss['R10.0'].median(), rss['R10.0'].max()) == (12124, 75564)
interrupted = pd.read_csv(DATA/'diagnostic/interrupted-J51-stage2.csv')
assert len(interrupted) == 25 and interrupted.status.eq('PASS').sum() == 24
assert interrupted.loc[interrupted.status.eq('FAIL'), 'case'].tolist() == ['case_016.txt']
print('Integrated Final: checked bank/solver aggregates, 100 replay records, matched ratios and direct RSS')

historical = pd.read_csv(R/'Research_Trial_Log/data/raw_feedback_verified.csv')
r91 = historical.query('archive_group == "r91" and repeat == 1').groupby('variant').area_pass.sum()
assert r91.r90_frozen-r91.r91_repeat_sop == 1587
assert r91.r90_frozen-r91.r91_library == 663
assert r91.r90_frozen-r91.r91_repeat_shannon == 879
historical_pairs = pd.read_csv(R/'Research_Trial_Log/data/raw_controlled_pairs_verified.csv')
r91_pairs = historical_pairs.query('group == "r91" and repeat == 1')
r91_pairs = r91_pairs[r91_pairs.bank.isin(BANKS)]
for policy, expected in {
    'r91_library': (50, 15, 663), 'r91_repeat_sop': (50, 8, 1587),
    'r91_repeat_shannon': (50, 5, 879),
}.items():
    rows = r91_pairs[r91_pairs.candidate.eq(policy)]
    assert set(rows.bank) == set(BANKS)
    assert tuple(rows[['joint_pass', 'wins', 'area_saved']].sum()) == expected

timing = ARCHIVE.parent/'reports/stage2-timing-20261124'
headroom = pd.read_csv(timing.parent/'stage2-headroom-20261124/development.csv').set_index('trial')
for trial, expected in {'strict': (960177,2,0), 'weighted': (869636,0,9),
                        'one': (898282,1,0), 'cuts': (880546,1,0)}.items():
    assert tuple(headroom.loc[trial, ['area','min_slack','at_target']]) == expected
earlier = pd.read_csv(timing/'earlier-budget.csv')
assert earlier.stage1_bank_area.add(earlier.stage2_bank_area).eq(earlier.combined_area).all()
assert earlier.combined_area.tolist() == [910462, 880987, 883002]
cuts = pd.read_csv(timing.parent/'stage2-cuts-20261124/paired.csv')
assert len(cuts) == 50 and cuts.delay_after.le(cuts.target).all()
assert cuts.area_before.sub(cuts.area_after).eq(cuts.area_saved).all()
assert (cuts.area_saved.sum(), cuts.area_saved.gt(0).sum(), cuts.area_saved.eq(0).sum()) == (3165, 17, 33)
factors = pd.read_csv(timing.parent/'stage2-factors-20261124/paired.csv')
factor_public = factors[factors.bank.isin(BANKS)]
gain = factor_public.area_before.sub(factor_public.area_after)
assert (len(factor_public), gain.sum(), gain.gt(0).sum()) == (50, 5, 2)
stress = pd.read_csv(timing/'stress.csv')
development = ['limits', 'fresh', '732751', '410931', '851039', '647251',
               '332809', '173391', '659237', '899911', '521021', '937129']
validation = ['112431', '357139', '711413', '338111', '829543', '526633']
dev = stress[stress.bank.isin(development)]
val = stress[stress.bank.isin(validation)]
assert (len(dev), dev.target_met.eq('yes').sum()) == (168, 168)
assert (len(val), val.target_met.eq('yes').sum()) == (84, 83)
assert val.loc[val.target_met.eq('no'), ['bank', 'case']].values.tolist() == [['711413', 'case_003.txt']]
residual = pd.read_csv(timing/'residual.csv').set_index('variant')
assert tuple(residual.loc['Released candidate', ['area', 'delay', 'target']]) == (2105, 28, 27)
assert tuple(residual.loc['Generating witness', ['area', 'delay', 'target']]) == (550, 27, 27)
assert len(residual) == 8 and residual.valid.all()
assert residual.drop('Generating witness').delay.eq(28).all()

# Check the BDD cofactor example and two alternative physical realizations.
for x in (0, 1):
    assert tuple(x & y for y in (0, 1)) == ((0, 0) if x == 0 else (0, 1))
    assert tuple(x ^ y for y in (0, 1)) == ((0, 1) if x == 0 else (1, 0))
    for y in (0, 1):
        assert (x ^ y) == ((x | y) & (1 - (x & y)))


def example_metrics(gates, roots, input_arrivals, prices, delays):
    """Evaluate area and arrival of the output-reachable gates in an example."""
    live = set()
    pending = list(roots)
    while pending:
        gate = pending.pop()
        if gate in live or gate in input_arrivals:
            continue
        live.add(gate)
        pending.extend(gates[gate][1:])
    arrivals = dict(input_arrivals)
    for gate, (op, *fanins) in gates.items():
        if gate in live:
            arrivals[gate] = delays[op] + max(arrivals[pin] for pin in fanins)
    return sum(prices[gates[gate][0]] for gate in live), tuple(arrivals[root] for root in roots)


# Unit costs: each new cone is cheaper alone, while either individual switch costs two extra.
mix = {
    'xy': ('or', 'x', 'y'), 'xz': ('or', 'x', 'z'),
    'p': ('and', 'xy', 'xz'), 'yz': ('and', 'y', 'z'), 'q': ('or', 'x', 'yz'),
    'p_u': ('and', 'p', 'u'), 'p_v': ('and', 'p', 'v'),
    'q_u': ('and', 'q', 'u'), 'q_v': ('and', 'q', 'v'),
}
unit = {'or': 1, 'and': 1, 'not': 1}
mix_arrivals = dict.fromkeys('xyzuv', 0)
for x, y, z, u, v in product((0, 1), repeat=5):
    p = (x | y) & (x | z)
    q = x | (y & z)
    assert (p & u, p & v) == (q & u, q & v)
for roots, area in [
    (('p_u', 'p_v'), 5), (('q_u', 'p_v'), 7), (('p_u', 'q_v'), 7), (('q_u', 'q_v'), 4),
]:
    assert example_metrics(mix, roots, mix_arrivals, unit, unit) == (area, (3, 3))
for root in ('p_u', 'p_v', 'q_u', 'q_v'):
    assert example_metrics(mix, (root,), mix_arrivals, unit, unit) == (4 if root.startswith('p') else 3, (3,))

# Cut masks, maximal cubes, exact cone areas and the local versus global gain.
cut = {
    'ab': ('and', 'a', 'b'), 'nb': ('not', 'b'), 'nbc': ('and', 'nb', 'c'),
    'long': ('and', 'a', 'nbc'), 'old': ('or', 'ab', 'long'),
    'ac': ('and', 'a', 'c'), 'sop': ('or', 'ab', 'ac'),
    'na': ('not', 'a'), 'nc': ('not', 'c'), 'neither': ('and', 'nb', 'nc'),
    'off': ('or', 'na', 'neither'), 'dual': ('not', 'off'),
}
cut_arrivals = {'a': 3, 'b': 0, 'c': 1}
prices = {'and': 2, 'or': 3, 'not': 1}
delays = {'and': 2, 'or': 2, 'not': 1}
mask = 0
for a, b, c in product((0, 1), repeat=3):
    old = (a & b) | (a & ((1-b) & c))
    assert old == ((a & b) | (a & c)) == (1 - ((1-a) | ((1-b) & (1-c))))
    mask |= old << (a + 2*b + 4*c)
assert mask == 0xA8 and (0xFF ^ mask) == 0x57
cubes = {}
for cube in product((0, 1, '*'), repeat=3):
    cubes[cube] = {
        i for i in range(8)
        if all(bit == '*' or bit == ((i >> j) & 1) for j, bit in enumerate(cube))
    }
for on_set, expected_cube_patterns in [
    ({3, 5, 7}, {(1, 1, '*'), (1, '*', 1)}),
    ({0, 1, 2, 4, 6}, {(0, '*', '*'), ('*', 0, 0)}),
]:
    valid = {cube: covered for cube, covered in cubes.items() if covered <= on_set}
    maximal = {cube for cube, covered in valid.items() if not any(covered < other for other in valid.values())}
    assert maximal == expected_cube_patterns
    assert set.union(*(valid[cube] for cube in maximal)) == on_set
for root, area in [('old', 10), ('sop', 7), ('dual', 11)]:
    assert example_metrics(cut, (root, 'ab'), cut_arrivals, prices, delays) == (area, (7, 5))
assert example_metrics(cut, ('ab',), cut_arrivals, prices, delays) == (2, (5,))
assert example_metrics(cut, ('sop',), cut_arrivals, prices, delays) == (7, (7,))
reclaim = 10-2
assert (reclaim, 7-reclaim, 7-10) == (8, -1, -3)

# Grouped cofactor reconstruction, anchored XOR and four-leaf timing.
for a, b, c, d in product((0, 1), repeat=4):
    h = a & b
    selected = ((1-h) & c) | (h & (c | d))
    assert selected == (c | (a & b & d))
for shared in (0, 1):
    table = [[x ^ y ^ shared for y in (0, 1)] for x in (0, 1)]
    for x, y in product((0, 1), repeat=2):
        g = table[x][0]
        h = table[0][y] ^ table[0][0]
        assert (g ^ h) == table[x][y]
    assert (table[0][0] & table[1][1]) != (table[0][1] & table[1][0])
    assert (table[0][0] | table[1][1]) != (table[0][1] | table[1][0])
# Exhaust all two-by-two matrices to test the screen and projection equivalence.
for bits in product((0, 1), repeat=4):
    a, b, c, d = bits
    rows = (bits[:2], bits[2:])
    cols = (bits[::2], bits[1::2])
    reconstructed_and = tuple(int(any(r) and any(s)) for r,s in product(rows, cols))
    reconstructed_or = tuple(int(all(r) or all(s)) for r,s in product(rows, cols))
    reconstructed_xor = tuple(rows[x][0] ^ rows[0][y] ^ a for x,y in product((0, 1), repeat=2))
    assert (reconstructed_and == bits) == ((a & d) == (b & c))
    assert (reconstructed_or == bits) == ((a | d) == (b | c))
    assert (reconstructed_xor == bits) == ((a ^ b ^ c ^ d) == 0)
for p, a, b, c in product((0, 1), repeat=4):
    assert ((p & a) & b) & c == p & ((a & b) & c)
arrival = lambda u, v: 1 + max(u, v)
assert arrival(arrival(arrival(2, 0), 0), 0) == 5
assert arrival(2, arrival(arrival(0, 0), 0)) == 3
assert tuple(r-t for r, t in zip((2, 3, 4), (3, 4, 5))) == (-1, -1, -1)
assert 4-3 == 1
assert (2+3+3, 2+3, (2+3+3)-(2+3)) == (8, 5, 3)
print('ALL VERIFIED: manuscript data, appendix and constructed examples')

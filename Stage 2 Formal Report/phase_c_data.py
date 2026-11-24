"""Shared readers for the archived Phase C measurements."""
from pathlib import Path

import pandas as pd


REPORT = Path(__file__).resolve().parent
ARCHIVE = REPORT.parent / 'Final_Submission_by_Zeyun_DU' / 'integration'
DATA = ARCHIVE / 'data'
METHODS = ['Z1', 'J51', 'R10.0', 'Integrated Final']
BANKS = ['stage1', 'stage2']
FINAL = METHODS[-1]
KEY = ['bank', 'case']


def matched(repeat):
    frame = pd.read_csv(DATA / 'matched_case_metrics.csv').query('repeat == @repeat')
    expected = pd.MultiIndex.from_product(
        [BANKS, [f'case_{i:03}.txt' for i in range(1, 26)], METHODS],
        names=KEY + ['method'],
    )
    actual = frame.set_index(KEY + ['method']).index
    if not actual.is_unique or set(actual) != set(expected):
        raise ValueError(f'Incomplete or duplicate matched observations in repeat {repeat}')
    if not (frame.status.eq('PASS') & frame.target_met.eq(1)).all():
        raise ValueError(f'Matched repeat {repeat} includes failures')
    return frame


def paired(frame, metric):
    return frame.pivot(index=KEY, columns='method', values=metric)[METHODS]


def direct_memory():
    frame = pd.read_csv(DATA / 'matched' / 'direct_memory.csv')
    if len(frame) != 200 or not frame.exit_code.eq(0).all():
        raise ValueError('Incomplete direct RSS observations')
    return frame

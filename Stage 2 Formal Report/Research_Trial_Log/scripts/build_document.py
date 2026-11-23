"""Backwards-compatible entry point for the unified Stage 1+Stage 2 log.
Never regenerate a Stage-2-only main.tex; the combined document is canonical.
"""
from pathlib import Path
import runpy
runpy.run_path(str(Path(__file__).with_name('merge_full_trial.py')), run_name='__main__')

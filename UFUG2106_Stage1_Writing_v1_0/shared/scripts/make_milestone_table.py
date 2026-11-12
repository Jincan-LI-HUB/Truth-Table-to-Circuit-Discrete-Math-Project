#!/usr/bin/env python3
"""Generate LaTeX milestone table from shared/data/round_history.csv only."""
from pathlib import Path
import csv
p=Path(__file__).resolve().parents[1]
rows=list(csv.DictReader((p/'data/round_history.csv').open(newline='')))
assert len(rows)==9
name={'Round 1':'R1 baseline','Round 2':'R2 hybrid','Round 3':'R3 timed map','Round 4':'R4 polarity','Round 4.1 B':'R4.1 Balanced','Round 5':'R5 caching','Round 5.1':'R5.1 typed DAG','Round 6.0':'R6.0 cut proto.','Round 6.1':'R6.1 budgeted'}
output=[r'\begin{table*}[!t]',r'\centering\caption{Stage 1 milestones from individually archived WSL official-evaluator results}\label{tab:milestones}',r'\small\setlength{\tabcolsep}{11pt}',r'\begin{tabular}{@{}lccrr@{}}\toprule',r'Version & PASS & Target met & Area sum & Median synthesis runtime (ms) \\ \midrule']
for row in rows:
 v=name[row['round']]; area=f"{int(row['area_sum']):,}"; t=f"{float(row['median_runtime_ms']):.3f}"; is_r51=row['round']=='Round 5.1'
 fields=[v, str(row['pass'])+'/25',str(row['target_met'])+'/25', area,t]
 if is_r51:fields=[r'\textbf{'+x+'}' for x in fields]
 output.append(' & '.join(fields)+r' \\')
output += [r'\bottomrule\end{tabular}',r'\par\vspace{2pt}',r'\parbox{0.92\textwidth}{\footnotesize\emph{Comparability:} each row is one designated historical WSL run, not a randomized same-run comparison of every round. Runtime is the median of 25 official \texttt{runtime\_ms} values for that one archive; use Fig.~\ref{fig:paired} for directly paired runtime evidence. Values were not normalized across CPU loads.}',r'\end{table*}']
(p/'data/milestones_with_runtime.tex').write_text('\n'.join(output)+'\n')
print('Generated 9-row milestone table')

#!/usr/bin/env python3
"""Reproduce all empirical figures using only included ./data/*.csv.
Run: python shared/scripts/make_figures.py [--out-dir shared/figures]
References: data/source_manifest.csv and data/paired_benchmarks.csv.
"""
import csv,json,pathlib,argparse
import matplotlib;matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
A=argparse.ArgumentParser();A.add_argument('--out-dir',default=None);args=A.parse_args()
P=pathlib.Path(__file__).resolve().parents[1];D=P/'data';F=pathlib.Path(args.out_dir or P/'figures');F.mkdir(exist_ok=True,parents=True)
C=json.loads((P/'palette.json').read_text())['colors']
def read(name):
 with (D/name).open(newline='') as file:return list(csv.DictReader(file))
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':9.3,'axes.spines.top':False,'axes.spines.right':False,'pdf.fonttype':42,'axes.labelcolor':'#27343A','text.color':'#27343A','xtick.color':'#27343A','ytick.color':'#27343A','savefig.facecolor':'white','figure.facecolor':'white'})
def save(name):
 plt.tight_layout(pad=1.3)
 plt.savefig(F/(name+'.pdf'),bbox_inches='tight')
 plt.savefig(F/(name+'.png'),dpi=220,bbox_inches='tight')
 plt.close()
rows=read('round_history.csv')
labels=[r['round'].replace('Round ','R') for r in rows]
vals=np.array([float(r['area_sum']) for r in rows])
fig,ax=plt.subplots(figsize=(8.4,3.5))
barcolors=[C['slate'],C['sage'],C['blue'],C['blue'],C['mint'],C['mint'],C['sage'],C['peach'],C['rose']]
bars=ax.bar(np.arange(len(vals)),vals/1000, color=barcolors,edgecolor='#48545C',linewidth=.55,width=.72)
for i,v in enumerate(vals):ax.text(i,v/1000+13,f'{v/1000:,.1f}k',ha='center',va='bottom',fontsize=7.7)
ax.set_xticks(range(len(vals)),labels);ax.set_ylim(0,max(vals/1000)*1.14);ax.set_ylabel('Sum of reported gate areas (thousands)');ax.set_title('Archived Stage 1 area history (selected local runs)')
ax.text(.01,-.29,'Different versions were not jointly randomized; bars compare area, not synthesis speed.',transform=ax.transAxes,fontsize=7.5)
save('area_evolution')
# Paired runtime, grouped families
pairs=read('paired_benchmarks.csv'); d={r['pair']:r for r in pairs}
group=[('R4.1 B → R5', ['5 vs 4.1 B']),('R5 → R5.1',['5.1 vs 5 #1','5.1 vs 5 #2']),('R5.1 → R6.0',['6.0 vs 5.1 #1','6.0 vs 5.1 #2']),('R5.1 → R6.1',['6.1 vs 5.1 #1','6.1 vs 5.1 #2'])]
fig,ax=plt.subplots(figsize=(7.8,3.5)); x=np.arange(len(group));base=[];cand=[]
for _,runs in group:
 base.append(np.mean([float(d[k]['baseline_median_ms']) for k in runs]));cand.append(np.mean([float(d[k]['candidate_median_ms']) for k in runs]))
ax.bar(x-.17,base,width=.33,color=C['slate'],edgecolor='#48545C',lw=.5,label='Frozen comparator')
ax.bar(x+.17,cand,width=.33,color=C['blue'],edgecolor='#48545C',lw=.5,label='Candidate')
for i,(a,b) in enumerate(zip(base,cand)):
 ax.text(i-.17,a+2,f'{a:.1f}',ha='center',fontsize=7.8)
 ax.text(i+.17,b+2,f'{b:.1f}',ha='center',fontsize=7.8)
ax.set_xticks(x,[g[0] for g in group]);ax.set_ylim(0,max(base+cand)*1.17);ax.set_ylabel('Median synthesis runtime (ms)');ax.legend(frameon=False,loc='upper left',ncol=2);ax.set_title('Same-run paired runtime comparisons on WSL')
save('paired_runtime')
# 25 per-case area reduction of R6.1 vs R5.1, run1
pc=read('stage1_per_case.csv'); c=[int(r['case'].split('_')[1].split('.')[0]) for r in pc]; gain=[int(r['round61_saving']) for r in pc]
fig,ax=plt.subplots(figsize=(8.6,3.0));ax.bar(c,gain,color=C['sage'],edgecolor='#48545C',lw=.5)
ax.axhline(0,color='#48545C',lw=.8);ax.set_xticks(c,[f'{i:02}' for i in c],rotation=0,fontsize=7);ax.set_xlabel('Public case number');ax.set_ylabel('Area saved (R5.1 - R6.1)');ax.set_title('Cut rewriting saves area only on a subset of public cases');save('cut_case_savings')
# holdout bar values
r=read('cut_holdout.csv');labels=[a['set'] for a in r];a=[int(x['base_area']) for x in r];b=[int(x['cut_area']) for x in r]
fig,ax=plt.subplots(figsize=(6.6,3.4));x=np.arange(len(a))
ax.bar(x-.18,a,.34,label='R5.1',color=C['slate'],edgecolor='#48545C',lw=.5)
ax.bar(x+.18,b,.34,label='R6.1',color=C['sage'],edgecolor='#48545C',lw=.5)
for i,(aa,bb) in enumerate(zip(a,b)):
 ax.text(i-.18,aa+900,f'{aa:,}',ha='center',fontsize=8)
 ax.text(i+.18,bb+900,f'{bb:,}',ha='center',fontsize=8)
ax.set_xticks(x,['Mixed functions (40)','Large functions (8)']);ax.set_ylabel('Summed area');ax.set_title('Fresh, frozen Round 6.1 holdout results');ax.legend(frameon=False);ax.set_ylim(0,max(a)*1.2)
save('holdout_area')
print('Generated figures in',F)

# Round 3 chronological development ablation; separate implication branch excluded.
r=read('round3_ablation_path.csv');r=[q for q in r if q['source_row_type']=='sequential_development_snapshot']
lab=['Portfolio','Comp. BDD','Affine','Balance','Slack recovery','Reverse order','Fallback']
vals=[int(q['area_sum']) for q in r]
fig,ax=plt.subplots(figsize=(8.4,3.6)); x=np.arange(len(vals))
ax.plot(x, np.array(vals)/1000,marker='o',linewidth=1.9,color=C['blue'],markersize=6)
for i,v in enumerate(vals): ax.annotate(f'{v/1000:,.1f}k',(i,v/1000),xytext=(0,10),textcoords='offset points',ha='center',fontsize=7.8)
ax.set_xticks(x,lab,rotation=18,ha='right');ax.set_ylim(460,890);ax.set_ylabel('Aggregate Area (thousands)')
ax.set_title('Round 3 sequential development snapshots (not isolated effects)')
save('round3_ablation_path')
# Round 4 postprocessor comparison: all 25 cases; best-per-case is an oracle over the tested strategies.
r=read('round4_postprocess_aggregate.csv'); labels=[q['strategy'] for q in r];vals=[int(q['area_sum']) for q in r]
fig,ax=plt.subplots(figsize=(8,3.65)); x=np.arange(len(vals))
ax.bar(x,np.array(vals)/1000,color=[C['slate'],C['sage'],C['blue'],C['mint'],C['rose'],C['peach']],edgecolor='#48545C',lw=.6)
for i,v in enumerate(vals):ax.text(i,v/1000+1.5,f'{v:,}',ha='center',fontsize=7.4)
ax.set_ylim(525,536.5);ax.set_xticks(x,labels,rotation=16,ha='right');ax.set_ylabel('Aggregate Area (thousands)')
ax.set_title('Round 4: postprocessor-only area ablation, not full R4 search')
save('round4_postprocess_ablation')
# Round 6.1 local search-budget tradeoff on 16 development cases (NOT Stage 1 official metric).
r=read('round61_budget_development.csv'); r=[q for q in r if q['dataset']=='larger_development']
bud=[int(q['budget_ms']) for q in r];a=[int(q['area_saved']) for q in r];tt=[float(q['median_wall_ms']) for q in r]
fig,ax=plt.subplots(figsize=(5.4,3.6));ax.plot(bud,a,marker='o',markersize=7,linewidth=2,color=C['blue'],label='Area saved')
for x,y,t in zip(bud,a,tt): ax.annotate(f'{y} saved\n{t:.2f} ms median',(x,y),xytext=(0,12),textcoords='offset points',ha='center',fontsize=8)
ax.set_xticks(bud);ax.set_xlim(19,51);ax.set_ylim(295,610);ax.set_xlabel('Cut search budget (ms)');ax.set_ylabel('Local Area saved (16 development cases)')
ax.set_title('Round 6.1 budget tradeoff, local postprocessing only')
save('round61_budget_tradeoff')

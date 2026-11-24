from pathlib import Path
import re,fitz
base=Path(__file__).resolve().parents[1]; tex=base/'tex';fig=base/'figures'
stage1=(base/'source_stage1_main.tex').read_text(encoding='utf-8')
stage2=(tex/'source_stage2_full.tex').read_text(encoding='utf-8')
assert '\\section{1. Reading contract:' in stage2
# Crop original vector figures from exact user-supplied finalized Stage 1 PDF
src=fitz.open(base/'references/Stage1_Research_Trial_Log_v1.pdf')
clips=[('stage1_round3_ablation_path.pdf',8,(68,381,548,584)),('stage1_round4_postprocess_ablation.pdf',9,(68,509,548,712)),('stage1_paired_runtime.pdf',12,(68,397,548,607)),('stage1_holdout_area.pdf',15,(68,62,548,265)),('stage1_round61_budget_tradeoff.pdf',15,(68,391,548,648)),('stage1_area_evolution.pdf',17,(68,218,548,410))]
for name,page,region in clips:
    out=fitz.open();r=fitz.Rect(*region);p=out.new_page(width=r.width,height=r.height);p.show_pdf_page(p.rect,src,page,clip=r);out.save(fig/name,garbage=4,deflate=True);out.close()
# Isolate faithful source: no change to mathematical prose
start1=stage1.index('\\section{How to read this record}')
end1=stage1.index('\\bibliographystyle{IEEEtran}',start1)
b1=stage1[start1:end1]
replace={
'round3_ablation_path.pdf':'stage1_round3_ablation_path.pdf',
'round4_postprocess_ablation.pdf':'stage1_round4_postprocess_ablation.pdf',
'paired_runtime.pdf':'stage1_paired_runtime.pdf',
'holdout_area.pdf':'stage1_holdout_area.pdf',
'round61_budget_tradeoff.pdf':'stage1_round61_budget_tradeoff.pdf',
'area_evolution.pdf':'stage1_area_evolution.pdf'
}
for o,n in replace.items():b1=b1.replace('../shared/figures/'+o,'../figures/'+n)
b1=b1.replace('../figures/stage1_area_evolution.pdf','../figures/13_stage1_multiscale_history.pdf')
b1=b1.replace('Selected archived local area totals. This is a non-paired development history; area totals are directly tabulated but runtime is not compared across archives.', 'Multiscale Stage 1 area history. The left panel preserves the entire archived 25-case trajectory; the right panel magnifies small late differences against R5.1. These are historical observations, not a controlled causal contrast.')
(tex/'stage1_body.tex').write_text(b1,encoding='utf-8')
start2=stage2.index('\\section{1. Reading contract:')
end2=stage2.index('\\section*{References and primary research sources}',start2)
b2=stage2[start2:end2]
# Removing repeated Stage 1 synopsis, keeping provenance distinction and a precise bridge
b2=re.sub(r'\\section\{3\. The Stage 1 ancestry that Stage 2 actually inherits\}.*?(?=\\section\{4\. Round 7:)',lambda m:r'''\section{Transition: from Stage 1 evidence to Stage 2 constraints}
The preceding Stage 1 study already established a complete progression: exact Shannon/ROBDD construction, diversified mappings, slack-aware global recovery, typed DAG execution, and exploratory four-leaf cut rewriting. Its crucial unresolved problem was not whether cut rewriting \emph{could} save area---Rounds 6.0 and 6.1 measured real savings---but whether a function-level local search could be made valuable within the synthesizer's deadline and memory constraints. Stage 2 resumes precisely at this engineering question rather than starting the mathematical argument anew.

The separate actually submitted Stage 1 program (Z1) and Jincan's frozen R5.1 research program (J51) remain distinct. Z1 provides the assignment's formal submitted-stage comparator; J51 is the implementation-research lineage feeding into the R7--R10 development. Later matched evaluations of both programs are reported as distinct observations, not as a fabricated single lineage. The course specification, exact source snapshots, and raw results remain the authority for each claim.

''',b2,flags=re.S)
# Remove literal section prefix numbers; full merged LaTeX will number sections across both stages
b2=re.sub(r'(\\(?:sub)?section(?:\[[^]]*\])?\{)(?:\d+(?:\.\d+)?[a-z]?\.?\s+)([^}]*)\}',lambda m:m.group(1)+m.group(2)+'}',b2)
b2=re.sub(r'(\\section\{)Appendix ([AB])\.\s+',lambda m:m.group(1)+'Research appendix '+m.group(2)+': ',b2)
# Stage 2 label with backreference of Stage1 intro remain unique
b2=b2.replace('../figures/01_archival_area_evolution.pdf','../figures/14_stage2_area_delay_trajectory.pdf')
(tex/'stage2_body.tex').write_text(b2,encoding='utf-8')
# Keep original Stage1 preamble, consistent font and muted palette
preamble=stage1[:stage1.index('\\begin{document}')]
preamble=preamble.replace('\\newcommand{\\documentshorttitle}{Stage 1 Research Trial Log}', '\\newcommand{\\documentshorttitle}{Complete Research Trial Log}')
# Pandoc longtable output needs a real length scale; TeX handles numeric values
preamble+='\n\\providecommand{\\real}[1]{#1}\n\\setlength{\\emergencystretch}{2em}\n'
# Exact sources preserved and explicit difference between study and final report
intro=r'''\begin{document}
\input{cover.tex}
\setcounter{tocdepth}{1}
\setcounter{secnumdepth}{2}
\tableofcontents
\clearpage
\part*{Part I. Stage 1 --- Exact construction, mapping quality and implementation efficiency}
\addcontentsline{toc}{part}{Part I. Stage 1 --- Complete historical investigation}
\input{stage1_body.tex}
\clearpage
\part*{Part II. Stage 2 --- Bounded resynthesis, search economics and final selection}
\addcontentsline{toc}{part}{Part II. Stage 2 --- Complete historical investigation}
\input{stage2_body.tex}
\input{final_integration.tex}
'''
bib=r'''
\clearpage
\begin{thebibliography}{99}
\bibitem{coursehandout} UFUG2106 Course Staff, \emph{Final Project: Truth Table to Circuit}, 2026, instructor-provided course specification.
\bibitem{shannon1949} C. E. Shannon, ``The synthesis of two-terminal switching circuits,'' \emph{Bell System Technical Journal}, 1949.
\bibitem{bryant1986} R. E. Bryant, ``Graph-based algorithms for Boolean function manipulation,'' \emph{IEEE Transactions on Computers}, vol. C-35, no. 8, pp. 677--691, 1986.
\bibitem{brayton1984} R. K. Brayton et al., \emph{Logic Minimization Algorithms for VLSI Synthesis}, Kluwer, 1984.
\bibitem{mishchenko2006} A. Mishchenko, S. Chatterjee, and R. K. Brayton, ``DAG-Aware AIG Rewriting,'' \emph{Proc. DAC}, pp. 532--535, 2006.
\bibitem{abc} Berkeley Logic Synthesis and Verification Group, \emph{ABC: A System for Sequential Synthesis and Verification}, software project, accessed 2026.
\bibitem{course} UFUG2106 Course Staff, \emph{Final Project: Truth Table to Circuit}, 2026.
\bibitem{stage1} J. Li and Z. Du, \emph{Stage 1 Research Trial Log}, finalized 11 Nov. 2026, full text reproduced in Part I.
\bibitem{shannon} C. E. Shannon, ``The synthesis of two-terminal switching circuits,'' 1949.
\bibitem{bryant} R. E. Bryant, ``Graph-based algorithms for Boolean function manipulation,'' 1986.
\bibitem{mishchenko} A. Mishchenko et al., ``DAG-aware AIG rewriting,'' 2006.
\end{thebibliography}
\end{document}
'''
(tex/'main.tex').write_text(preamble+intro+bib,encoding='utf-8')
print('generated combined',len(preamble+intro+bib),'stage1 body',len(b1),'stage2 body',len(b2))

# Manuscript Review — Round 7: v0.9 references, figure hierarchy and test protocol

This revision implements the eight explicit author requests and the agreed structural improvements, preserving Round 5.1 frozen source and all original numeric official/paired CSVs.

| Request | Actual file change | Verification / limitation |
|---|---|---|
| Supplementary test-generation rationale | New technical-report subsection; new standalone Trial Log chapter preceding overfitting discussion | Source scripts and fixed-seed manifests archived; 144/144 synthetic case hashes matched original developer ZIPs. Historical 110-case generator not asserted fully available; not hidden Stage 2. |
| Standards-based references | Both documents now use `\bibliographystyle{IEEEtran}` and `\bibliography{../shared/bibliography/references}`; inline `thebibliography` removed | Original BibTeX engine ran for both; `.bbl` produced by IEEEtran.bst; six bibliography entries in each PDF with working DOI/GitHub links where appropriate. |
| First-page acknowledgment | Removed `\thanks{...}` from Technical Report author; Trial title page retains only version identity | Pending contribution / AI statement retained in internal review notes; no attribution invented. |
| Figure 1 poor arrows | Added overview as Fig. 1 and redrew cofactor/MUX as Fig. 2 with clean symmetric fanout | TikZ source retained, no crossing edges; worked example was previously exhaustively verified. |
| Small Fig. 2/3 charts | Round 3 and Round 4 main ablation figures converted to full-width `figure*`, enlarged to 91% of text width | Both remain grounded in existing CSVs; captions retain causal limitations. |
| Table I lacks runtime | Added Median synthesis runtime (ms) derived from 9 official CSVs and a non-paired caveat | `shared/scripts/make_milestone_table.py` regenerates the table directly from round_history.csv, no manual numbers. |
| Remaining academic refinements | Reordered test suite methodology, added evidence-role clarification and reference metadata audit | No new benchmark claimed; existing claims and source hash unchanged. |
| Research overview requested | Editable full-width TikZ Figure 1 distinguishes adopted Round 5.1 and rejected exploratory cut branch | Conceptual figure is not a data plot; diagram source included. |

## Citation checks
- `main.tex` in both outputs calls standard BibTeX; `.bib` contains full metadata and DOI fields.
- IEEEtran.bst does not print `doi` fields by default, so clickable DOI resolver links are retained through the corresponding `.bib` `note` fields as well; the machine-readable `doi` fields remain present.
- An internal handout is properly cited without inventing a public URL.
- Publisher DOI records were checked for Bryant (1986), Mishchenko et al. (2006), and Brayton et al. (1984), and the ABC GitHub repository resolves. Not all sources need a PDF download URL.

## Remaining items intentionally deferred
- P0: individual contributions and final AI-use disclosure require confirmed author statements.
- Research freeze Round 5.1 is not evidence of actual Canvas submission.
- Additional generated cases are known, limited structural families, not random samples from future Stage 2.

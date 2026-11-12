#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
python3 "$ROOT/shared/scripts/make_milestone_table.py"
# Install texlive-bibtex-extra (IEEEtran.bst), texlive-latex-extra, texlive-fonts-recommended where needed.
if command -v bibtex >/dev/null 2>&1; then BIBTEX=bibtex; elif command -v bibtex.original >/dev/null 2>&1; then BIBTEX=bibtex.original; else echo 'BibTeX executable is required' >&2; exit 2; fi
for part in technical_report trial_log_record; do
  (cd "$ROOT/$part"; pdflatex -interaction=nonstopmode -halt-on-error main.tex >/dev/null; "$BIBTEX" main >/dev/null; pdflatex -interaction=nonstopmode -halt-on-error main.tex >/dev/null; pdflatex -interaction=nonstopmode -halt-on-error main.tex >/dev/null)
done
echo 'Built technical_report/main.pdf and trial_log_record/main.pdf using BibTeX.'

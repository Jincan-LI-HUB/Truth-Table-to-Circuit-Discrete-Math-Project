#!/usr/bin/env bash
# Local WSL reproduction for Round 4.1 speed-optimized variants. No sudo/zip package required.
# Usage: bash run_round4_1_local.sh /tmp/ufug2106_evaluator "$CASES" [all|strict|balanced|fast]
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT"
if [[ $# -lt 2 || $# -gt 3 ]];then echo 'Usage: run_round4_1_local.sh EVALUATOR STAGE1_DIR [all|strict|balanced|fast]' >&2;exit 2;fi
EVAL="$(realpath "$1")"; CASES="$(realpath "$2")"; PICK="${3:-all}"
[[ -x "$EVAL" && -d "$CASES" ]] || { echo 'Missing executable evaluator or case directory' >&2;exit 2; }
[[ "$PICK" =~ ^(all|strict|balanced|fast)$ ]] || { echo 'Unknown variant' >&2;exit 2; }
for t in g++ make python3 sha256sum;do command -v "$t" >/dev/null || { echo "Missing $t" >&2;exit 2; };done
[[ "$(find "$CASES" -maxdepth 1 -type f -name 'case_*.txt' | wc -l)" == 25 ]] || { echo 'Expected 25 cases' >&2;exit 2; }
STAMP="$(date +'%Y%m%d_%H%M%S')"
RUN="$ROOT/local_runs/${STAMP}_Round4.1"
[[ ! -e "$RUN" ]] || RUN="${RUN}_$$"
mkdir -p "$RUN/report_ready" "$RUN/source_snapshot"
cp -a src Makefile summarize_round4_1.py run_round4_1_local.sh "$RUN/source_snapshot/"
cp docs/ROUND4_1_MATHEMATICAL_AND_EXPERIMENT.md "$RUN/report_ready/mathematical_design_and_experiment.md"
{
 echo 'Round 4.1 variant study'
 echo "timestamp=$(date -Is)"
 echo "computer=$(uname -srm)"
 echo "compiler=$(g++ --version | head -1)"
 echo "python=$(python3 --version)"
 echo "cases=$CASES"
 echo "evaluator=$EVAL"
 echo '--- CPU ---'
 command -v lscpu >/dev/null && lscpu | head -30 || true
 echo '--- Digests ---'
 sha256sum "$EVAL" Makefile src/synth_*.cpp src/*.hpp
} > "$RUN/environment.txt" 2>&1
find "$CASES" -maxdepth 1 -type f -name 'case_*.txt' -print0 | sort -z | xargs -0 sha256sum > "$RUN/case_sha256.txt"
make clean > "$RUN/build.log" 2>&1
make -j1 >> "$RUN/build.log" 2>&1
MODES=(strict balanced fast)
[[ "$PICK" == all ]] || MODES=("$PICK")
ERR=0
for v in "${MODES[@]}";do
 mkdir -p "$RUN/$v/outputs"
 echo "[Run] $v"
 set +e
 "$EVAL" "$ROOT/build/synth_$v" "$CASES" --report "$RUN/$v/official.csv" --save-outputs "$RUN/$v/outputs" > "$RUN/$v/evaluator.log" 2>&1
 RC=$?
 set -e
 ((RC==0)) || ERR=1
 tail -n 2 "$RUN/$v/evaluator.log" || true
 echo "evaluator_exit_code=$RC" > "$RUN/$v/verification_summary.txt"
 FAILED=0
 : > "$RUN/$v/independent_verification.log"
 for casefile in "$CASES"/case_*.txt;do
  stem="$(basename "${casefile%.txt}")"
  net="$RUN/$v/outputs/${stem}.output.txt"
  if [[ ! -f "$net" ]] || ! python3 tools/verify_netlist.py "$casefile" "$net" >> "$RUN/$v/independent_verification.log" 2>&1;then
    echo "INDEPENDENT_CHECK_FAIL: $stem" >> "$RUN/$v/independent_verification.log"
    FAILED=$((FAILED+1))
  fi
 done
 echo "independent_verification_failed=$FAILED" >> "$RUN/$v/verification_summary.txt"
 ((FAILED==0)) || ERR=1
done
python3 summarize_round4_1.py "$RUN" "$ROOT/results/round4_user_wsl_reference.csv" > "$RUN/summary_console.txt" 2>&1 || ERR=1
cat "$RUN/summary_console.txt"
cat > "$RUN/report_ready/README.md" <<'MD'
# Round 4.1 — report_ready

This is a *local reproduction evidence directory*.

- `mathematical_design_and_experiment.md` documents algorithm motivation and proofs.
- `local_runtime_summary.md` is computed from actual local official CSVs.
- `../per_case_runtime_comparison.csv` contains paired WSL results against frozen Round 4.
- `../strict`, `../balanced`, `../fast` contain evaluator outputs and independent verification logs.
- `../source_snapshot` records the exact sources compiled for this run.

Keep the original Round 4 local run unchanged. Do not call a gain against different hardware a controlled benchmark.
MD
python3 - "$RUN" <<'PY'
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED
import sys
run=Path(sys.argv[1]);out=run.parent/(run.name+'_local_results.zip')
with ZipFile(out,'w',compression=ZIP_DEFLATED,compresslevel=5) as z:
 for f in sorted(run.rglob('*')):
  if f.is_file():z.write(f,arcname=str(Path(run.name)/f.relative_to(run)))
print('Evidence package:',out)
PY
((ERR==0)) || { echo 'WARNING: at least one validation failed; inspect logs before claiming success.' >&2;exit 1; }

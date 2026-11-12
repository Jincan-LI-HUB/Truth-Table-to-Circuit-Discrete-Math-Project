#!/usr/bin/env bash
# Usage: bash run_round5_1_local.sh /path/to/evaluator /path/to/stage1
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT"
if [[ $# -ne 2 ]];then echo 'Usage: run_round5_1_local.sh EVALUATOR STAGE1_DIR' >&2;exit 2;fi
EVAL="$(realpath "$1")"; CASES="$(realpath "$2")"
[[ -x "$EVAL" && -d "$CASES" ]] || { echo 'Cannot access evaluator or stage1 directory' >&2;exit 2; }
for tool in python3 g++ make sha256sum;do command -v "$tool" >/dev/null || { echo "Missing tool $tool" >&2;exit 2; };done
[[ "$(find "$CASES" -maxdepth 1 -name 'case_*.txt' -type f | wc -l)" -eq 25 ]] || { echo 'Expected 25 official cases' >&2;exit 2; }
STAMP="$(date +'%Y%m%d_%H%M%S')"
RUN="$ROOT/local_runs/${STAMP}_Round5.1"
[[ ! -e "$RUN" ]] || RUN="${RUN}_$$"
mkdir -p "$RUN"/{source_snapshot,benchmark,holdout,report_ready}
cp -a src Makefile summarize_round51.py run_round5_1_local.sh tools "$RUN/source_snapshot/"
cp docs/ROUND5_1_MATHEMATICAL_DESIGN.md "$RUN/report_ready/mathematical_design.md"
cp docs/ROUND5_1_REFERENCE_EXPERIMENT.md "$RUN/report_ready/reference_experiment.md"
{
 echo "date=$(date -Is)";uname -srm;g++ --version | head -1;python3 --version
 echo '--- hashes ---';sha256sum "$EVAL" src/* Makefile
} > "$RUN/environment.txt" 2>&1
find "$CASES" -maxdepth 1 -name 'case_*.txt' -type f -print0 | sort -z | xargs -0 sha256sum > "$RUN/cases_sha256.txt"
sha256sum tests/holdout_v1/case_*.txt tests/holdout_large_v1/case_*.txt > "$RUN/holdouts_sha256.txt"
make clean > "$RUN/build.log" 2>&1;make -j1 >> "$RUN/build.log" 2>&1
# Reverse order on the second full official benchmark, reducing order bias.
for pair in 1 2;do
 if [[ "$pair" == 1 ]];then seq="reference round51";else seq="round51 reference";fi
 for mode in $seq;do
  echo "[Official pair=$pair mode=$mode]"
  opts=()
  if [[ "$pair" == 1 ]];then opts=(--save-outputs "$RUN/benchmark/run1_${mode}_outputs");fi
  "$EVAL" "$ROOT/build/synth_${mode}" "$CASES" --report "$RUN/benchmark/run${pair}_${mode}.csv" "${opts[@]}" > "$RUN/benchmark/run${pair}_${mode}.log" 2>&1
  tail -n 1 "$RUN/benchmark/run${pair}_${mode}.log"
 done
done
: > "$RUN/benchmark/independent_verification.log"
errors=0
for case in "$CASES"/case_*.txt;do
 stem="$(basename "${case%.txt}")"
 if ! python3 tools/verify_netlist.py "$case" "$RUN/benchmark/run1_round51_outputs/${stem}.output.txt" >> "$RUN/benchmark/independent_verification.log" 2>&1;then
  echo "FAIL $stem" >> "$RUN/benchmark/independent_verification.log"
  errors=$((errors+1))
 fi
done
[[ "$errors" == 0 ]] || { echo "Independent verification failed on $errors cases" >&2;exit 1; }
# Reuse the separate, pre-committed holdout suite. No area/runtime tuning is done using them.
for subset in generated_110 holdout_v1 holdout_large_v1 stress;do
 [[ -d "$ROOT/tests/$subset" ]] || continue
 for mode in reference round51;do
  echo "[Generalization subset=$subset mode=$mode]"
  "$EVAL" "$ROOT/build/synth_${mode}" "$ROOT/tests/$subset" --report "$RUN/holdout/${subset}_${mode}.csv" > "$RUN/holdout/${subset}_${mode}.log" 2>&1
  tail -n 1 "$RUN/holdout/${subset}_${mode}.log"
 done
done
python3 summarize_round51.py "$RUN" | tee "$RUN/summary_console.txt"
cat > "$RUN/report_ready/README.md" <<'EOF'
# Round 5.1 report_ready

Keep this directory alongside official evaluator CSVs, compiler/source fingerprints,
Netlists, independent verification logs and held-out test results in the same
`local_runs/YYYYMMDD_HHMMSS_Round5.1/` folder. Do not replace Round 5 or Round 4.1 files.
EOF
python3 - "$RUN" <<'PY'
from pathlib import Path
from zipfile import ZipFile,ZIP_DEFLATED
import sys
run=Path(sys.argv[1]);out=run.parent/(run.name+'_local_results.zip')
with ZipFile(out,'w',ZIP_DEFLATED,compresslevel=5) as z:
 for p in sorted(run.rglob('*')):
  if p.is_file():z.write(p,arcname=str(Path(run.name)/p.relative_to(run)))
print('Archive:',out)
PY

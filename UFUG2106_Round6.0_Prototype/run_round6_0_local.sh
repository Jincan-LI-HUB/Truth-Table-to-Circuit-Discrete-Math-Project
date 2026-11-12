#!/usr/bin/env bash
# Usage: bash run_round6_0_local.sh /path/to/evaluator /path/to/stage1
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT"
if [[ $# -ne 2 ]];then echo 'Usage: bash run_round6_0_local.sh EVALUATOR STAGE1_DIR' >&2;exit 2;fi
EVAL="$(realpath "$1")";CASES="$(realpath "$2")"
[[ -x "$EVAL" && -d "$CASES" ]] || { echo 'Missing evaluator or cases directory' >&2;exit 2; }
for t in python3 g++ make sha256sum;do command -v "$t" >/dev/null || { echo "Missing dependency: $t" >&2; exit 2; };done
[[ "$(find "$CASES" -maxdepth 1 -name 'case_*.txt' -type f | wc -l)" -eq 25 ]] || { echo 'Expected 25 Stage 1 cases' >&2; exit 2; }
STAMP="$(date +'%Y%m%d_%H%M%S')"
RUN="$ROOT/local_runs/${STAMP}_Round6.0"
[[ ! -e "$RUN" ]] || RUN="${RUN}_$$"
mkdir -p "$RUN"/{source_snapshot,benchmark,holdout,report_ready}
cp -a src Makefile summarize_round60.py run_round6_0_local.sh tools "$RUN/source_snapshot/"
cp docs/ROUND6_0_MATHEMATICAL_DESIGN.md "$RUN/report_ready/mathematical_design.md"
cp docs/ROUND6_0_REFERENCE_EXPERIMENT.md "$RUN/report_ready/reference_experiment.md"
{
 echo "date=$(date -Is)";uname -srm;g++ --version|head -1;python3 --version
 echo '--- hashes ---';sha256sum "$EVAL" src/* Makefile
} > "$RUN/environment.txt" 2>&1
find "$CASES" -maxdepth 1 -name 'case_*.txt' -type f -print0 | sort -z | xargs -0 sha256sum > "$RUN/cases_sha256.txt"
find tests -name 'case_*.txt' -type f -print0 | sort -z | xargs -0 sha256sum > "$RUN/holdout_cases_sha256.txt"
make clean > "$RUN/build.log" 2>&1;make -j1 >> "$RUN/build.log" 2>&1
for pair in 1 2;do
 if [[ "$pair" == 1 ]];then SEQ='reference round60';else SEQ='round60 reference';fi
 for mode in $SEQ;do
  echo "[Official pair=$pair mode=$mode]"
  opts=();if [[ "$pair" == 1 ]];then opts=(--save-outputs "$RUN/benchmark/run1_${mode}_outputs");fi
  "$EVAL" "$ROOT/build/synth_${mode}" "$CASES" --report "$RUN/benchmark/run${pair}_${mode}.csv" "${opts[@]}" > "$RUN/benchmark/run${pair}_${mode}.log" 2>&1
  tail -1 "$RUN/benchmark/run${pair}_${mode}.log"
 done
done
# New precommitted test set and previously frozen Round 5.1 holdouts.
for group in holdout_round60_v1 previous_holdout_v1 previous_holdout_large_v1;do
 for mode in reference round60;do
  echo "[Holdout $group $mode]"
  opts=();if [[ "$mode" == 'round60' ]];then opts=(--save-outputs "$RUN/holdout/${group}_${mode}_outputs");fi
  "$EVAL" "$ROOT/build/synth_${mode}" "$ROOT/tests/$group" --report "$RUN/holdout/${group}_${mode}.csv" "${opts[@]}" > "$RUN/holdout/${group}_${mode}.log" 2>&1
  tail -1 "$RUN/holdout/${group}_${mode}.log"
 done
done
# Single Python process for all independent verification; avoids launching 161
# interpreters and leaves the synthesizer runtime numbers untouched.
python3 - "$CASES" "$RUN" "$ROOT" > "$RUN/benchmark/independent_verification.log" 2>&1 <<'PYVERIFY'
import importlib.util,sys
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
cases,run,root=map(Path,sys.argv[1:4])
spec=importlib.util.spec_from_file_location('independent',root/'tools/verify_netlist.py')
mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
items=[]
for p in sorted(cases.glob('case_*.txt')):
 items.append(('official',p,run/'benchmark/run1_round60_outputs'/(p.stem+'.output.txt')))
for group in ('holdout_round60_v1','previous_holdout_v1','previous_holdout_large_v1'):
 for p in sorted((root/'tests'/group).glob('case_*.txt')):
  items.append((group,p,run/'holdout'/(group+'_round60_outputs')/(p.stem+'.output.txt')))
def check(t):
 group,case,net=t
 try:
  x=mod.run(case,net)
  return group+' '+case.name+' PASS '+str(x), True
 except Exception as exc:return group+' '+case.name+' FAIL '+str(exc),False
with ThreadPoolExecutor(max_workers=4) as pool:
 results=list(pool.map(check,items))
for line,good in results:print(line)
failures=sum(not good for _,good in results)
print('Verified',len(results),'cases; failures',failures)
if failures:raise SystemExit(1)
PYVERIFY
python3 summarize_round60.py "$RUN" | tee "$RUN/summary_console.txt"
cat > "$RUN/report_ready/README.md" <<'NOTE'
# Round 6.0 report_ready

Keep these reports inside `local_runs/YYYYMMDD_HHMMSS_Round6.0/report_ready/`.
Original evaluator CSVs, saved netlists, input/source hashes, independent checks,
and compiler environment remain in the parent run directory.
The prototype is not a frozen final solver unless the performance/area trade-off is accepted.
NOTE
python3 - "$RUN" <<'PY'
from pathlib import Path
from zipfile import ZipFile,ZIP_DEFLATED
import sys
run=Path(sys.argv[1]);output=run.parent/(run.name+'_local_results.zip')
with ZipFile(output,'w',ZIP_DEFLATED,compresslevel=5) as z:
 for p in sorted(run.rglob('*')):
  if p.is_file():z.write(p,arcname=str(Path(run.name)/p.relative_to(run)))
print('Archive:',output)
PY

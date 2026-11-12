#!/usr/bin/env bash
# Round 6.1: two alternating matched reference/6.1 runs + fresh independent holdouts.
# Usage: bash run_round6_1_local.sh /path/to/evaluator /path/to/stage1
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT"
if [[ $# -ne 2 ]];then echo 'Usage: bash run_round6_1_local.sh EVALUATOR STAGE1_DIR' >&2;exit 2;fi
EVAL="$(realpath "$1")";CASES="$(realpath "$2")"
[[ -x "$EVAL" && -d "$CASES" ]] || { echo 'Missing executable evaluator or Stage 1 input folder' >&2;exit 2; }
for t in python3 g++ make sha256sum;do command -v "$t" >/dev/null || { echo "Missing tool: $t" >&2;exit 2; };done
[[ "$(find "$CASES" -maxdepth 1 -name 'case_*.txt' -type f | wc -l)" -eq 25 ]] || { echo 'Expected 25 official Stage 1 cases' >&2;exit 2; }
STAMP="$(date +'%Y%m%d_%H%M%S')"
RUN="$ROOT/local_runs/${STAMP}_Round6.1"
[[ ! -e "$RUN" ]] || RUN="${RUN}_$$"
mkdir -p "$RUN"/{source_snapshot,benchmark,holdout,report_ready}
cp -a src tools Makefile README.md summarize_round61.py run_round6_1_local.sh "$RUN/source_snapshot/"
cp docs/ROUND6_1_MATHEMATICAL_DESIGN.md "$RUN/report_ready/mathematical_design.md"
cp docs/ROUND6_1_REFERENCE_EXPERIMENT.md "$RUN/report_ready/reference_experiment.md"
{
 date -Is;uname -srm;g++ --version | head -1;python3 --version
 echo '--- evaluator and source hashes ---';sha256sum "$EVAL" src/* Makefile
} > "$RUN/environment.txt" 2>&1
find "$CASES" -maxdepth 1 -name 'case_*.txt' -type f -print0 | sort -z | xargs -0 sha256sum > "$RUN/cases_sha256.txt"
find tests/holdout_round61* -name 'case_*.txt' -type f -print0 | sort -z | xargs -0 sha256sum > "$RUN/holdout_cases_sha256.txt"
sha256sum tests/holdout_round61*manifest.json > "$RUN/holdout_manifest_sha256.txt"
make clean > "$RUN/build.log" 2>&1
make -j1 >> "$RUN/build.log" 2>&1
for pair in 1 2;do
 if [[ "$pair" == 1 ]];then SEQ='reference round61';else SEQ='round61 reference';fi
 for mode in $SEQ;do
  echo "[Stage1 pair=$pair mode=$mode]"
  opts=();if [[ "$pair" == 1 ]];then opts=(--save-outputs "$RUN/benchmark/run1_${mode}_outputs");fi
  "$EVAL" "$ROOT/build/synth_${mode}" "$CASES" --report "$RUN/benchmark/run${pair}_${mode}.csv" "${opts[@]}" > "$RUN/benchmark/run${pair}_${mode}.log" 2>&1
  tail -1 "$RUN/benchmark/run${pair}_${mode}.log"
 done
done
for group in holdout_round61_fresh_v1 holdout_round61_large_v1;do
 for mode in reference round61;do
  echo "[New holdout group=$group mode=$mode]"
  "$EVAL" "$ROOT/build/synth_${mode}" "$ROOT/tests/$group" --report "$RUN/holdout/${group}_${mode}.csv" \
   --save-outputs "$RUN/holdout/${group}_${mode}_outputs" > "$RUN/holdout/${group}_${mode}.log" 2>&1
  tail -1 "$RUN/holdout/${group}_${mode}.log"
 done
done
# Independently recompute circuit functionality and actual Area/Delay (not merely exit status).
python3 - "$CASES" "$RUN" "$ROOT" > "$RUN/benchmark/independent_verification.log" 2>&1 <<'PYVERIFY'
import csv,sys,importlib.util
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
case_dir,run,root=map(Path,sys.argv[1:4])
spec=importlib.util.spec_from_file_location('independent',root/'tools/verify_netlist.py')
mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
items=[]
for tag,source,outputs,report in [
 ('official',case_dir,run/'benchmark/run1_round61_outputs',run/'benchmark/run1_round61.csv'),
 ('fresh',root/'tests/holdout_round61_fresh_v1',run/'holdout/holdout_round61_fresh_v1_round61_outputs',run/'holdout/holdout_round61_fresh_v1_round61.csv'),
 ('large',root/'tests/holdout_round61_large_v1',run/'holdout/holdout_round61_large_v1_round61_outputs',run/'holdout/holdout_round61_large_v1_round61.csv')]:
 metrics={r['case']:r for r in csv.DictReader(report.open())}
 for case in sorted(source.glob('case_*.txt')):items.append((tag,case,outputs/(case.stem+'.output.txt'),metrics[case.name]))
def check(item):
 tag,case,out,metric=item
 try:
  v=mod.run(case,out)
  assert v['area']==int(metric['area']) and v['delay']==int(metric['delay']), 'Area/Delay mismatch'
  return f'{tag} {case.name} PASS exhaustive={v["exhaustive"]} assignments={v["assignments"]}',True
 except Exception as e:return f'{tag} {case.name} FAIL {e}',False
with ThreadPoolExecutor(max_workers=3) as ex:result=list(ex.map(check,items))
for msg,ok in result:print(msg)
fail=sum(not good for _,good in result)
print('verified=',len(result),'failures=',fail)
if fail:raise SystemExit(1)
PYVERIFY
python3 summarize_round61.py "$RUN" | tee "$RUN/summary_console.txt"
cat > "$RUN/report_ready/README.md" <<'EOF'
# Round 6.1 report_ready
This folder belongs in `local_runs/YYYYMMDD_HHMMSS_Round6.1/report_ready/`.
Keep raw official reports, netlists, independent verification, source hashes and
compiler environment in the parent local-run folder. No sudo/network/zip needed.
EOF
python3 - "$RUN" <<'PYZIP'
from pathlib import Path
from zipfile import ZipFile,ZIP_DEFLATED
import sys
run=Path(sys.argv[1]);out=run.parent/(run.name+'_local_results.zip')
with ZipFile(out,'w',ZIP_DEFLATED,compresslevel=6) as z:
 for p in sorted(run.rglob('*')):
  if p.is_file():z.write(p,arcname=str(Path(run.name)/p.relative_to(run)))
print('Completed:',out)
PYZIP

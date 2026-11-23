#!/usr/bin/env bash
set -Eeuo pipefail
HERE="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(dirname "$HERE")"
mkdir -p "$HERE/results" "$HERE/feedback"
STAMP="$(date +%Y%m%d_%H%M%S_%N)";RUN="$HERE/results/$STAMP"
mkdir -p "$RUN";printf '%s\n' "$RUN" > "$HERE/latest_run.txt"
mode="${1:-}"
case "$mode" in ''|--quick|--local-only) ;; *) echo "usage: bash run_round85.sh [--quick|--local-only]";exit 2;; esac
on_exit(){
 local rc=$?
 trap - EXIT
 python3 "$HERE/tools/export_feedback.py" --exit-code "$rc" || true
 if ((rc));then echo "ROUND8.5 FAILED exit=$rc; feedback retained.";fi
 exit "$rc"
}
trap on_exit EXIT
{
 echo '[1/5] Freeze provenance and independent compilation'
 python3 "$HERE/tools/verify_source.py"
 make -C "$HERE" -j1
 "$HERE/build/test_budget_ledger"
 echo '[2/5] Policy isolation and exhaustive preflight'
 python3 "$HERE/tests/test_policy_isolation.py"
 if [[ "$mode" == '--quick' ]];then python3 "$HERE/tests/test_preflight.py" --results "$RUN/preflight" --quick
 else python3 "$HERE/tests/test_preflight.py" --results "$RUN/preflight";fi
 echo '[3/5] Standalone build manifest and submission smoke checks'
 python3 "$HERE/tests/test_clean_build.py" --results "$RUN/clean_build" 
 if [[ "$mode" == '--local-only' ]];then
  echo 'LOCAL_GATE PASS (independent exhaustive and clean build only)'
  exit 0
 fi
 echo '[4/5] Course evaluator availability and frozen comparator'
 if [[ ! -f "$ROOT/evaluator" ]];then
  echo 'NO_GENUINE_EVALUATOR: cannot claim official release gate.'
  exit 17
 fi
 if [[ ! -d "$ROOT/data/stage1" || ! -d "$ROOT/data/stage2" ]];then
  echo 'NO_OFFICIAL_DATA: both public banks must exist for official evaluation.'
  exit 18
 fi
 echo '[5/5] Two-stage paired official evaluator: embedded Round8.4 vs Round8.5'
 if [[ "$mode" == '--quick' ]];then
  python3 "$HERE/tools/run_official.py" --results "$RUN" --runs 1 --quick
 else
  python3 "$HERE/tools/run_official.py" --results "$RUN" --runs 2
 fi
 echo 'ROUND8.5 RELEASE_GATE PASS (public stage 1+2 only)'
} 2>&1 | tee "$HERE/results/latest_test.log" "$RUN/main.log"

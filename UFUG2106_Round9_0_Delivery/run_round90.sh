#!/usr/bin/env bash
set -Eeuo pipefail
HERE="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(dirname "$HERE")"
mode="${1:-}"
case "$mode" in ''|--quick|--local-only|--stress-only) ;; *) echo 'usage: bash run_round90.sh [--quick|--local-only|--stress-only]';exit 2;; esac
mkdir -p "$HERE/results" "$HERE/feedback"
STAMP="$(date +%Y%m%d_%H%M%S_%N)";RUN="$HERE/results/$STAMP";mkdir -p "$RUN"
printf '%s\n' "$RUN" > "$HERE/latest_run.txt"
on_exit(){
 local rc=$?;trap - EXIT
 python3 "$HERE/tools/export_feedback.py" --exit-code "$rc" || true
 if ((rc));then echo "ROUND9.0 FAILED exit=$rc; logs retained";fi
 exit "$rc"
}
trap on_exit EXIT
{
 echo '[1/5] Verify source provenance and 39 canonical case pairs'
 python3 "$HERE/tools/verify_package.py"
 python3 "$HERE/tools/check_banks.py"
 python3 "$HERE/tools/check_hard_bank.py"
 echo '[2/5] Compile frozen reference and no-environment submission'
 make -C "$HERE" -j2
 if [[ "$mode" != '--quick' && "$mode" != '--stress-only' ]];then
  python3 "$HERE/tests/test_cold_build.py" --results "$RUN/cold_build"
 else
  echo "SKIP cold rebuild in fast mode; full/default mode validates cold build"
 fi
 echo '[3/5] Exhaustive correctness, unconfigured default and isolated submission'
 if [[ "$mode" == '--quick' || "$mode" == '--stress-only' ]];then
  python3 "$HERE/tools/run_local.py" --results "$RUN" --quick
 else
  python3 "$HERE/tools/run_local.py" --results "$RUN"
 fi
 if [[ "$mode" == '--local-only' ]];then
  echo 'R90_LOCAL_GATE_PASS; genuine evaluator not invoked';exit 0
 fi
 if [[ "$mode" == '--stress-only' ]];then
  echo '[4/5] 100 ms sensitivity: direct, affine and non-affine n=18-20'
  python3 "$HERE/tools/run_stress.py" --results "$RUN"
  echo 'R90_STRESS_COMPLETE; sensitivity only';exit 0
 fi
 echo '[4/5] Genuine course evaluator + unmodified 50 public cases'
 if [[ ! -f "$ROOT/evaluator" ]];then echo 'NO_GENUINE_EVALUATOR';exit 17;fi
 if [[ ! -d "$ROOT/data/stage1" || ! -d "$ROOT/data/stage2" ]];then echo 'NO_PUBLIC_BANKS';exit 18;fi
 echo '[5/5] Two-stage official paired regression; explicit vs implicit default'
 if [[ "$mode" == '--quick' ]];then
  python3 "$HERE/tools/run_public.py" --results "$RUN" --runs 1
 else
  python3 "$HERE/tools/run_public.py" --results "$RUN" --runs 2
 fi
 echo 'ROUND9.0 PUBLIC RELEASE_GATE PASS (no hidden-test or grading score claim)'
} 2>&1 | tee "$HERE/results/latest_test.log" "$RUN/main.log"

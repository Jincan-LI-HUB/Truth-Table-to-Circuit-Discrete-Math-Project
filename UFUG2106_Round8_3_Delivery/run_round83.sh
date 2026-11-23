#!/usr/bin/env bash
set -Eeuo pipefail
HERE="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(dirname "$HERE")"
cd "$ROOT"
mkdir -p "$HERE/results" "$HERE/feedback"
STAMP="$(date +%Y%m%d_%H%M%S_%N)"
RUN="$HERE/results/$STAMP";mkdir -p "$RUN"
printf '%s\n' "$RUN" > "$HERE/latest_run.txt"
on_exit(){
  local rc=$?
  trap - EXIT
  python3 "$HERE/tools/export_feedback.py" --exit-code "$rc" || true
  if ((rc));then echo "ROUND8.3 FAILED (exit=$rc); logs and feedback retained.";fi
  exit "$rc"
}
trap on_exit EXIT
{
 echo '[1/5] Verify frozen source and compile Round8.3'
 python3 "$HERE/tools/verify_source.py"
 make -C "$HERE" -j1
 echo '[2/5] Validate strategy isolation and critical exhaustive truth tables'
 python3 "$HERE/tests/test_policy_isolation.py"
 QUICK=()
 if [[ "${1:-}" == '--quick' ]];then QUICK=(--quick);fi
 python3 "$HERE/tests/test_preflight.py" --results "$RUN/preflight" "${QUICK[@]}"
 echo '[3/5] Check genuine official evaluator and frozen Round8.2.1 comparator'
 if [[ ! -f "$ROOT/evaluator" ]];then
   echo 'OFFICIAL GATE NOT RUN: real course evaluator missing; this is not a PASS.'
   exit 17
 fi
 if [[ ! -x "$ROOT/UFUG2106_Round8_2_1_Delivery/build/synth_round821" ]];then
   make -C "$ROOT/UFUG2106_Round8_2_1_Delivery" build/synth_round821 -j1
 fi
 echo '[4/5] Paired evaluator: both stages, reversed order, stable vs dense budgets'
 RUNS=2
 if ((${#QUICK[@]}));then RUNS=1;fi
 python3 "$HERE/tools/run_official.py" --results "$RUN" --runs "$RUNS" "${QUICK[@]}"
 echo '[5/5] Official Stage1/2 complete (positive-RAM evaluator issue remains separate)'
 echo 'ROUND8.3 RELEASE_GATE: PASS (public Stage1/2 only)'
} 2>&1 | tee "$HERE/results/latest_test.log" "$RUN/main.log"

#!/usr/bin/env bash
set -Eeuo pipefail
HERE="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(dirname "$HERE")"
cd "$ROOT"
mkdir -p "$HERE/results" "$HERE/feedback"
STAMP="$(date +%Y%m%d_%H%M%S_%N)"
RUN="$HERE/results/$STAMP"
mkdir -p "$RUN"
printf '%s\n' "$RUN" > "$HERE/latest_run.txt"
on_exit(){
  local rc=$?
  trap - EXIT
  python3 "$HERE/tools/export_feedback.py" --exit-code "$rc" || true
  if ((rc));then echo "ROUND8.2.1 FAILED (exit=$rc); logs and feedback retained.";fi
  exit "$rc"
}
trap on_exit EXIT
{
 echo '[1/4] Verify frozen Round8.2 source / build patched standalone'
 python3 "$HERE/tools/verify_source.py"
 make -C "$HERE" -j1
 echo '[2/4] Direct RAM-cap and exhaustive resource tests'
 quick=()
 if [[ "${1:-}" == '--quick' ]];then quick=(--quick);fi
 python3 "$HERE/tools/run_resources.py" --results "$RUN" "${quick[@]}"
 echo '[3/4] Check official evaluator, then build Round8.2 comparator if needed'
 if [[ ! -f "$ROOT/evaluator" ]];then
   echo 'RELEASE_GATE: NOT RUN — genuine course evaluator missing; no official result is claimed.'
   exit 17
 fi
 if [[ ! -x "$ROOT/UFUG2106_Round8_2_Delivery/build/synth_round82" ]];then
   make -C "$ROOT/UFUG2106_Round8_2_Delivery" build/synth_round82 -j1
 fi
 echo '[4/4] Official resource-limit + paired Stage 1 / Stage 2 evaluations'
 # Resource evaluator is authoritative for the RAM cases; it is deliberately
 # separate from the local peak-RSS and truth-table proof.
 python3 "$HERE/tools/run_resources.py" --results "$RUN" "${quick[@]}" --official
 runs=2
 if ((${#quick[@]}));then runs=1;fi
 python3 "$HERE/tools/run_official.py" --results "$RUN" --runs "$runs" "${quick[@]}"
 echo 'RELEASE_GATE: PASS'
} 2>&1 | tee "$HERE/results/latest_test.log" "$RUN/main.log"

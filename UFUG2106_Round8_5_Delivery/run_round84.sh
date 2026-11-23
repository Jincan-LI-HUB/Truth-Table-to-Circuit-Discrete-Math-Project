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
  if ((rc));then echo "ROUND8.4 FAILED (exit=$rc); feedback retained.";fi
  exit "$rc"
}
trap on_exit EXIT
{
  echo '[1/5] Verify source provenance; compile Round8.4'
  python3 "$HERE/tools/verify_source.py"
  make -C "$HERE" -j1
  echo '[2/5] Exhaustive critical-case correctness and policy isolation'
  QUICK=();if [[ "${1:-}" == '--quick' ]];then QUICK=(--quick);fi
  python3 "$HERE/tests/test_policy_isolation.py"
  python3 "$HERE/tests/test_preflight.py" --results "$RUN/preflight" "${QUICK[@]}"
  echo '[3/5] Verify actual course evaluator and frozen comparators'
  if [[ ! -f "$ROOT/evaluator" ]];then
    echo 'OFFICIAL EVALUATOR MISSING. No official PASS claimed.'
    exit 17
  fi
  if [[ ! -x "$ROOT/UFUG2106_Round8_2_1_Delivery/build/synth_round821" ]];then
    make -C "$ROOT/UFUG2106_Round8_2_1_Delivery" build/synth_round821 -j1
  fi
  if [[ ! -x "$ROOT/UFUG2106_Round8_3_Delivery/build/synth_round83" ]];then
    make -C "$ROOT/UFUG2106_Round8_3_Delivery" build/synth_round83 -j1
  fi
  echo '[4/5] Two-stage paired genuine evaluator with 8 independent configurations'
  RUNS=2;if ((${#QUICK[@]}));then RUNS=1;fi
  python3 "$HERE/tools/run_official.py" --results "$RUN" --runs "$RUNS" "${QUICK[@]}"
  echo '[5/5] Public release gate passed; positive-RAM evaluator discrepancy separately unresolved'
  echo 'ROUND8.4 RELEASE_GATE: PASS (public data only)'
} 2>&1 | tee "$HERE/results/latest_test.log" "$RUN/main.log"

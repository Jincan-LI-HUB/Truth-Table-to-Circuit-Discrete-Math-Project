#!/usr/bin/env bash
# Always return a feedback ZIP, even if compilation, correctness tests or evaluation fail.
set -Eeuo pipefail
DELIVERY="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(dirname "$DELIVERY")"
cd "$ROOT"
mkdir -p "$DELIVERY/results" "$DELIVERY/feedback"
rm -f "$DELIVERY/latest_run.txt"
status=0
on_exit(){
  status=$?
  trap - EXIT
  python3 "$DELIVERY/tools/export_feedback.py" --exit-code "$status" || true
  if [[ "$status" != 0 ]]; then echo "ROUND 7.2 EXIT CODE: $status (feedback preserved)";fi
  exit "$status"
}
trap on_exit EXIT
{
  echo '[1/5] Generate and compile reproducible Round 7.2'
  python3 "$DELIVERY/bootstrap_round72.py"
  make -C "$DELIVERY" -j1
  echo '[2/5] Ensure the frozen Round 7.1 comparator is built'
  make -C "$ROOT/UFUG2106_Round7_1_Delivery" -j1
  echo '[3/5] Source and Cover-kernel correctness checks'
  python3 "$DELIVERY/tests/test_round72_patch.py"
  python3 "$DELIVERY/tests/test_exact_cover.py"
  echo '[4/5] Two essential exhaustive regression checks'
  python3 "$DELIVERY/tests/test_critical_cases.py"
  echo '[5/5] Two-stage paired official evaluator and candidate diagnostics'
  python3 "$DELIVERY/tools/run_benchmarks.py" "$@"
} > >(tee "$DELIVERY/results/latest_test.log") 2>&1

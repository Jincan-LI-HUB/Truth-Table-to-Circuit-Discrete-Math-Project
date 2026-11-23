#!/usr/bin/env bash
# All stages, paired and ablated, feedback always packaged even after error.
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
  if [[ "$status" != 0 ]]; then echo "ROUND 7.1 EXPERIMENT EXIT CODE: $status (feedback saved)"; fi
  exit "$status"
}
trap on_exit EXIT
{
  echo '[1/4] Compile frozen-source-derived R7.1'
  make -C "$DELIVERY" -j1
  echo '[2/4] Validate source patch and exact cover ablations'
  python3 "$DELIVERY/tests/test_round71_patch.py"
  python3 "$DELIVERY/tests/test_exact_cover.py"
  echo '[3/4] Paired official evaluation on BOTH stages, plus ablations and case_016 profiling'
  python3 "$DELIVERY/tools/run_benchmarks.py" "$@"
  echo '[4/4] Experiment finished; feedback packager will run automatically.'
} > >(tee "$DELIVERY/results/latest_test.log") 2>&1

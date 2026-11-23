#!/usr/bin/env bash
# Always create the feedback ZIP, even if build/evaluator/verification fails.
set -Eeuo pipefail
HERE="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(dirname "$HERE")"
cd "$ROOT"
mkdir -p "$HERE/results" "$HERE/feedback"
rm -f "$HERE/latest_run.txt"
on_exit(){
 local status=$?;trap - EXIT
 python3 "$HERE/tools/export_feedback.py" --exit-code "$status" || true
 if ((status));then echo "Round 8 experiment failed (exit=$status); feedback ZIP preserved.";fi
 exit "$status"
}
trap on_exit EXIT
{
 echo '[1/4] Materialize and compile from frozen Round7.2 source'
 python3 "$HERE/bootstrap_round8.py"
 make -C "$HERE" -j1
 echo '[2/4] Check frozen Round7.2 comparator'
 if [[ ! -x "$ROOT/UFUG2106_Round7_2_Delivery/build/synth_round72" ]]; then
  make -C "$ROOT/UFUG2106_Round7_2_Delivery" -j1
 else
  echo 'Using existing frozen Round7.2 executable; no upstream rebuild.'
 fi
 echo '[3/4] Preflight: exact truth-table equivalence for two structural probes'
 for item in 'stage2 case_016' 'stage2 case_021' 'stage1 case_020'; do
  read -r stage case <<< "$item"
  casefile="$ROOT/data/$stage/$case.txt"
  if [[ -f "$casefile" ]];then
   out="$HERE/results/preflight_${stage}_${case}.netlist"
   UFUG_R8_POLICY=iterate "$HERE/build/synth_round8" "$casefile" "$out" 2>"$HERE/results/preflight_${stage}_${case}.log"
   "$HERE/build/verify_exhaustive" "$casefile" "$out"
  fi
 done
 echo '[4/4] Official paired Stage 1 + Stage 2 runs and ablations'
 python3 "$HERE/tools/run_benchmarks.py" --case-profiles "$@"
} > >(tee "$HERE/results/latest_test.log") 2>&1

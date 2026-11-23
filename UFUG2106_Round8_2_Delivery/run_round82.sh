#!/usr/bin/env bash
set -Eeuo pipefail
HERE="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(dirname "$HERE")"
cd "$ROOT"
mkdir -p "$HERE/results" "$HERE/feedback"
rm -f "$HERE/latest_run.txt"
on_exit(){
 local rc=$?;trap - EXIT
 python3 "$HERE/tools/export_feedback.py" --exit-code "$rc" || true
 if ((rc));then echo "ROUND8.2 EXPERIMENT FAILED (exit=$rc); feedback preserved.";fi
 exit "$rc"
}
trap on_exit EXIT
{
 echo '[1/5] Verify parent SHA, materialize and compile Round8.2'
 python3 "$HERE/bootstrap_round82.py"
 make -C "$HERE" -j1
 echo '[2/5] Verify frozen Round 7.2 and 8.1 comparison binaries'
 if [[ ! -x "$ROOT/UFUG2106_Round7_2_Delivery/build/synth_round72" ]];then make -C "$ROOT/UFUG2106_Round7_2_Delivery" -j1;fi
 if [[ ! -x "$ROOT/UFUG2106_Round8_1_Delivery/build/synth_round81" ]];then make -C "$ROOT/UFUG2106_Round8_1_Delivery" -j1;fi
 echo '[3/5] Mathematical objectives and randomized Boolean equivalence'
 "$HERE/build/test_objectives"
 python3 "$HERE/tests/test_cut_random.py"
 echo '[4/5] Critical-case full truth table independent verification'
 for spec in 'stage2 case_003' 'stage2 case_005' 'stage2 case_021' 'stage2 case_016' 'stage2 case_023' 'stage1 case_020';do
   read -r stage case <<< "$spec"
   input="$ROOT/data/$stage/$case.txt"
   if [[ -f "$input" ]];then
     output="$HERE/results/preflight_${stage}_${case}.netlist"
     UFUG_R82_POLICY=fast_area UFUG_R82_SAMPLING=priority UFUG_R8_POLICY=off "$HERE/build/synth_round82" "$input" "$output" 2>"$HERE/results/preflight_${stage}_${case}.log"
     "$HERE/build/verify_exhaustive" "$input" "$output"
   fi
 done
 echo '[5/5] Official same-host two-stage paired tests (full ablation)'
 python3 "$HERE/tools/run_benchmarks.py" --profiles "$@"
} > >(tee "$HERE/results/latest_test.log") 2>&1

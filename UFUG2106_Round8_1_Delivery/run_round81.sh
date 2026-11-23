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
 if ((rc));then echo "ROUND8.1 FAILED (exit=$rc); feedback archive preserved.";fi
 exit "$rc"
}
trap on_exit EXIT
{
 echo '[1/5] Verify frozen Round 8.0 source; materialize Round 8.1'
 python3 "$HERE/bootstrap_round81.py"
 make -C "$HERE" -j1
 echo '[2/5] Check frozen Round 7.2 / Round 8.0 comparator binaries'
 if [[ ! -x "$ROOT/UFUG2106_Round7_2_Delivery/build/synth_round72" ]];then
    make -C "$ROOT/UFUG2106_Round7_2_Delivery" -j1
 fi
 if [[ ! -x "$ROOT/UFUG2106_Round8_Prototype/build/synth_round8" ]];then
    make -C "$ROOT/UFUG2106_Round8_Prototype" -j1
 fi
 echo '[3/5] Independent randomized small-DAG exhaustive correctness tests'
 python3 "$HERE/tests/test_cut_random.py"
 echo '[4/5] Critical-case exhaustive truth table verification (direct, not official timing)'
 for spec in 'stage2 case_003' 'stage2 case_005' 'stage2 case_021' 'stage2 case_016' 'stage1 case_020';do
   read -r stage case <<< "$spec"
   input="$ROOT/data/$stage/$case.txt"
   if [[ -f "$input" ]];then
     output="$HERE/results/preflight_${stage}_${case}.netlist"
     UFUG_R81_POLICY=branch UFUG_R8_POLICY=iterate "$HERE/build/synth_round81" "$input" "$output" 2>"$HERE/results/preflight_${stage}_${case}.log"
     "$HERE/build/verify_exhaustive" "$input" "$output"
   fi
 done
 echo '[5/5] Official same-host paired benchmark, both stages, ablations'
 python3 "$HERE/tools/run_benchmarks.py" --profiles "$@"
} > >(tee "$HERE/results/latest_test.log") 2>&1

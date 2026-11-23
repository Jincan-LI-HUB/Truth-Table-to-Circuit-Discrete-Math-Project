#!/usr/bin/env bash
set -Eeuo pipefail
HERE="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(dirname "$HERE")"
mode="${1:-}"
case "$mode" in ''|--quick|--local-only|--stress-only) ;; *) echo 'usage: bash run_round87.sh [--quick|--local-only|--stress-only]';exit 2;; esac
mkdir -p "$HERE/results" "$HERE/feedback"
STAMP="$(date +%Y%m%d_%H%M%S_%N)";RUN="$HERE/results/$STAMP";mkdir -p "$RUN"
printf '%s\n' "$RUN" > "$HERE/latest_run.txt"
on_exit(){
 local rc=$?
 trap - EXIT
 python3 "$HERE/tools/export_feedback.py" --exit-code "$rc" || true
 if ((rc));then echo "ROUND8.7 FAILED exit=$rc; diagnosis saved";fi
 exit "$rc"
}
trap on_exit EXIT
{
 echo '[1/4] Immutable source & frozen generalization bank; compile independent controls'
 python3 "$HERE/tools/verify_release.py"
 python3 "$HERE/tools/generate_holdouts.py" --verify
 python3 "$HERE/tools/generate_stress.py" --verify
 make -C "$HERE" -j2
 if [[ "$mode" == '--stress-only' ]];then
   echo 'ADVERSARIAL_ONLY: genuine evaluator if available; no release PASS assertion'
   python3 "$HERE/tools/run_stress.py" --results "$RUN"
   exit 0
 fi
 echo '[2/4] 36 unseen cases × 3 strategies × 2 runs (quick: 12 × 3 × 1)'
 if [[ "$mode" == '--quick' ]];then
   python3 "$HERE/tools/run_holdouts.py" --results "$RUN" --quick --runs 1
 else
   python3 "$HERE/tools/run_holdouts.py" --results "$RUN" --runs 2
 fi
 if [[ "$mode" == '--local-only' ]];then echo 'R87 LOCAL ROBUSTNESS GATE COMPLETE; no official claims';exit 0;fi
 echo '[3/5] Isolated source-only cold checkout and compilation'
 python3 "$HERE/tests/test_cold_build.py" --results "$RUN/cold_build"
 echo '[4/5] Genuine evaluator and public banks availability'
 if [[ ! -f "$ROOT/evaluator" ]];then echo 'NO_GENUINE_EVALUATOR';exit 17;fi
 if [[ ! -d "$ROOT/data/stage1" || ! -d "$ROOT/data/stage2" ]];then echo 'NO_PUBLIC_BANKS';exit 18;fi
 echo '[5/5] Genuine 50 public case paired regression'
 if [[ "$mode" == '--quick' ]];then
   python3 "$HERE/tools/run_public.py" --results "$RUN" --runs 1
 else
   python3 "$HERE/tools/run_public.py" --results "$RUN" --runs 2
 fi
 echo 'ROUND8.7 ROBUSTNESS GATE COMPLETE. No grading-hidden test claim.'
} 2>&1 | tee "$HERE/results/latest_test.log" "$RUN/main.log"

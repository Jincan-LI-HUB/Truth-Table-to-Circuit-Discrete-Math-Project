#!/usr/bin/env bash
set -Eeuo pipefail
HERE="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(dirname "$HERE")"
mode="${1:-}"
case "$mode" in ''|--quick|--local-only) ;; *) echo 'Usage: bash run_round91.sh [--quick|--local-only]';exit 2;; esac
mkdir -p "$HERE/results" "$HERE/feedback"
STAMP="$(date +%Y%m%d_%H%M%S_%N)"; RUN="$HERE/results/$STAMP";mkdir -p "$RUN"
printf '%s\n' "$RUN" > "$HERE/latest_run.txt"
on_exit(){
 local rc=$?;trap - EXIT
 python3 "$HERE/tools/export_feedback.py" --exit-code "$rc" || true
 if ((rc));then echo "ROUND9.1 INCOMPLETE exit=$rc; feedback preserved";fi
 exit "$rc"
}
trap on_exit EXIT
{
 echo '[1/5] Frozen parent SHA, candidate SHA, sealed lockbox hashes'
 python3 "$HERE/tools/verify_package.py"
 echo '[2/5] Build and independently check 13,956 library template instances'
 make -C "$HERE" -j2
 "$HERE/build/test_library"
 if [[ "$mode" != '--quick' ]];then
  echo '[3/5] Cold isolated submission compile and exact verification'
  python3 "$HERE/tests/test_cold_build.py"
 else echo '[3/5] Cold build skipped in quick mode';fi
 echo '[4/5] Independent exhaustive local development/stress checks'
 if [[ "$mode" == '--quick' ]];then
  python3 "$HERE/tools/run_preflight.py" --results "$RUN" --quick
 else python3 "$HERE/tools/run_preflight.py" --results "$RUN";fi
 if [[ "$mode" == '--local-only' ]];then
  echo 'R91_LOCAL_ONLY_COMPLETE; course evaluator not invoked';exit 0
 fi
 echo '[5/5] Genuine public Stage1/Stage2 evaluator with matched-control ablations'
 if [[ ! -f "$ROOT/evaluator" ]];then echo 'NO_GENUINE_EVALUATOR';exit 17;fi
 if [[ ! -d "$ROOT/data/stage1" || ! -d "$ROOT/data/stage2" ]];then echo 'MISSING_PUBLIC_BANKS';exit 18;fi
 if [[ "$mode" == '--quick' ]];then
  python3 "$HERE/tools/run_public.py" --results "$RUN" --runs 1
 else python3 "$HERE/tools/run_public.py" --results "$RUN" --runs 2;fi
 echo 'R91_PUBLIC_RELEASE_GATE PASS (public cases only; hidden cases untested)'
} 2>&1 | tee "$RUN/main.log" "$HERE/results/latest_test.log"

#!/usr/bin/env bash
set -Eeuo pipefail
HERE="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(dirname "$HERE")"
mode="${1:-}"
case "$mode" in ''|--quick|--local-only) ;; *) echo 'Usage: bash run_round100.sh [--quick|--local-only]' ; exit 2;; esac
mkdir -p "$HERE/results" "$HERE/feedback"
STAMP="$(date +%Y%m%d_%H%M%S_%N)";RUN="$HERE/results/$STAMP";mkdir -p "$RUN"
printf '%s\n' "$RUN" > "$HERE/latest_run.txt"
on_exit(){
 local rc=$?;trap - EXIT
 python3 "$HERE/tools/export_feedback.py" --exit-code "$rc" || true
 if ((rc));then echo "ROUND10.0 INCOMPLETE exit=$rc; feedback preserved";fi
 exit "$rc"
}
trap on_exit EXIT
{
 echo '[1/5] Source lineage, frozen parent, submission identity and independent fixtures'
 python3 "$HERE/tools/verify_package.py"
 echo '[2/5] Compile frozen controls, new default, and independent submission'
 make -C "$HERE" -j2
 echo '[3/5] Isolated cold submission build (source-only)'
 if [[ "$mode" == '--quick' ]];then echo 'SKIP cold build in quick mode';else python3 "$HERE/tests/test_cold_build.py";fi
 echo '[4/5] Exhaustive correctness and opt-in/opt-out comparison'
 if [[ "$mode" == '--quick' ]];then python3 "$HERE/tools/run_preflight.py" --results "$RUN" --quick
 else python3 "$HERE/tools/run_preflight.py" --results "$RUN";fi
 if [[ "$mode" == '--local-only' ]];then echo 'R100_LOCAL_ONLY_COMPLETE; official evaluator not invoked';exit 0;fi
 echo '[5/5] Genuine course evaluator, Stage 1/2, paired reverse-order tests'
 if [[ ! -f "$ROOT/evaluator" ]];then echo 'NO_GENUINE_EVALUATOR';exit 17;fi
 if [[ ! -d "$ROOT/data/stage1" || ! -d "$ROOT/data/stage2" ]];then echo 'MISSING_PUBLIC_BANK';exit 18;fi
 if [[ "$mode" == '--quick' ]];then python3 "$HERE/tools/run_public.py" --results "$RUN" --runs 1 --quick
 else python3 "$HERE/tools/run_public.py" --results "$RUN" --runs 2;fi
 echo 'ROUND10.0 PUBLIC_RELEASE_GATE PASS (public only, not integrated, hidden untested)'
} 2>&1 | tee "$RUN/main.log" "$HERE/results/latest_test.log"

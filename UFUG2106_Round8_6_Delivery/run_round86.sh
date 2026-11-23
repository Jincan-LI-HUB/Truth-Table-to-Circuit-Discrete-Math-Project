#!/usr/bin/env bash
set -Eeuo pipefail
HERE="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(dirname "$HERE")"
mkdir -p "$HERE/results" "$HERE/feedback"
STAMP="$(date +%Y%m%d_%H%M%S_%N)";RUN="$HERE/results/$STAMP";mkdir -p "$RUN"
printf '%s\n' "$RUN" > "$HERE/latest_run.txt"
mode="${1:-}"
case "$mode" in ''|--quick|--local-only) ;; *) echo 'usage: bash run_round86.sh [--quick|--local-only]';exit 2;; esac
on_exit(){
 local rc=$?
 trap - EXIT
 python3 "$HERE/tools/export_feedback.py" --exit-code "$rc" || true
 if ((rc));then echo "ROUND8.6 FAILED exit=$rc; feedback retained.";fi
 exit "$rc"
}
trap on_exit EXIT
{
 echo '[1/5] Verify frozen source and compile self-contained R86 and R85 comparator'
 python3 "$HERE/tools/verify_source.py"
 make -C "$HERE" -j1
 "$HERE/build/test_budget_ledger"
 echo '[2/5] Policy isolation and exact correctness preflight'
 python3 "$HERE/tests/test_policy_isolation.py"
 if [[ "$mode" == '--quick' ]];then python3 "$HERE/tests/test_preflight.py" --results "$RUN/preflight" --quick
 else python3 "$HERE/tests/test_preflight.py" --results "$RUN/preflight";fi
 echo '[3/5] Cold source-only compile + independent truth check'
 python3 "$HERE/tests/test_clean_build.py" --results "$RUN/cold_build"
 if [[ "$mode" == '--local-only' ]];then echo 'R86_LOCAL_GATE PASS, no official evaluator claim';exit 0;fi
 echo '[4/5] Verify course evaluator and complete Stage 1/2 banks'
 if [[ ! -f "$ROOT/evaluator" ]];then echo 'NO_GENUINE_EVALUATOR; official release gate unavailable';exit 17;fi
 if [[ ! -d "$ROOT/data/stage1" || ! -d "$ROOT/data/stage2" ]];then echo 'MISSING_OFFICIAL_BANKS';exit 18;fi
 echo '[5/5] True paired official evaluator: 7 policies / 2 stages / 2 runs'
 if [[ "$mode" == '--quick' ]];then python3 "$HERE/tools/run_official.py" --results "$RUN" --runs 1 --quick
 else python3 "$HERE/tools/run_official.py" --results "$RUN" --runs 2;fi
 echo 'ROUND8.6 PUBLIC RELEASE_GATE PASS; hidden cases and positive RAM limit not assessed'
} 2>&1 | tee "$HERE/results/latest_test.log" "$RUN/main.log"

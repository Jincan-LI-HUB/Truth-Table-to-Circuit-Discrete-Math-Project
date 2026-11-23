#!/usr/bin/env bash
set -Eeuo pipefail
HERE="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(dirname "$HERE")"
MODE="${1:-}"
case "$MODE" in ''|--quick|--local-only) ;; *) echo 'Usage: bash run_round101.sh [--quick|--local-only]' ; exit 2;; esac
mkdir -p "$HERE/results" "$HERE/feedback"
RUN="$HERE/results/$(date -u +%Y%m%d_%H%M%S_%N)"
mkdir -p "$RUN"
printf '%s\n' "$RUN" > "$HERE/latest_run.txt"
on_exit(){
 local rc=$?;trap - EXIT
 python3 "$HERE/tools/export_feedback.py" --exit-code "$rc" --run "$RUN" || true
 if ((rc)); then echo "R101_INCOMPLETE exit=$rc; partial feedback preserved"; fi
 exit "$rc"
}
trap on_exit EXIT
{
 echo '[1/5] Frozen R10.0 provenance, manifest, and experimental isolation'
 python3 "$HERE/tools/verify_package.py"
 echo '[2/5] Compile original frozen solver, controlled trial and exact verifier'
 make -C "$HERE" -j2
 echo '[3/5] Source-only cold-build and independent truth-table checks'
 if [[ "$MODE" == '--quick' ]];then
   echo 'SKIP full cold-build in quick mode'
   python3 "$HERE/tools/run_preflight.py" --out "$RUN/preflight" --quick
 else
   python3 "$HERE/tests/test_cold_build.py"
   python3 "$HERE/tools/run_preflight.py" --out "$RUN/preflight"
 fi
 if [[ "$MODE" == '--local-only' ]]; then echo 'R101_LOCAL_ONLY_COMPLETE';exit 0;fi
 echo '[4/5] Check genuine evaluator and untouched public banks'
 if [[ ! -f "$ROOT/evaluator" ]];then echo 'NO_GENUINE_EVALUATOR';exit 17;fi
 if [[ ! -d "$ROOT/data/stage1" || ! -d "$ROOT/data/stage2" ]];then echo 'MISSING_PUBLIC_BANK';exit 18;fi
 echo '[5/5] Genuine 2-stage reverse-order paired official performance evaluation'
 if [[ "$MODE" == '--quick' ]];then
   python3 "$HERE/tools/run_official.py" --out "$RUN" --quick
 else
   python3 "$HERE/tools/run_official.py" --out "$RUN"
 fi
 python3 "$HERE/tools/analyze_official.py" --official-dir "$RUN/official"
 echo 'R101_PUBLIC_GATE_PASS; experimental variants are NOT automatically promoted'
} 2>&1 | tee "$RUN/main.log" "$HERE/results/latest_test.log"

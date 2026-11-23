#!/usr/bin/env bash
set -Eeuo pipefail
HERE="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
mkdir -p "$HERE/build" "$HERE/results" "$HERE/feedback" "$HERE/logs"
LOG="$HERE/logs/latest.log"
cleanup(){
  rc=$?
  trap - EXIT
  python3 "$HERE/tools/export_feedback.py" --exit-code "$rc" || true
  if ((rc));then echo "ATTRIBUTION PROBE HAD ERROR (exit=$rc), feedback ZIP created";fi
  exit "$rc"
}
trap cleanup EXIT
{
 echo '[1/2] Compile diagnostic-only low-footprint programs'
 cc -O2 -std=c11 -Wall -Wextra -o "$HERE/build/tiny_wire" "$HERE/src/tiny_wire.c"
 cc -O2 -std=c11 -Wall -Wextra -o "$HERE/build/lightweight_mem_runner" "$HERE/src/lightweight_mem_runner.c"
 echo '[2/2] Compare minimal C vs patched C++ across RAM caps and evaluator invocation modes'
 python3 "$HERE/tools/attribution.py" "$@"
} 2>&1 | tee "$LOG"

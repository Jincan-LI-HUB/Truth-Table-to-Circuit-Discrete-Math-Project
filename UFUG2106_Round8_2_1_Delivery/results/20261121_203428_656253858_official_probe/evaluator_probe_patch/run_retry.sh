#!/usr/bin/env bash
# Non-invasive retry: freezes R8.2.1 source, only repairs evaluator invocation.
set -Eeuo pipefail
PROBE="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
PROJECT="$(dirname "$PROBE")"
ORIGINAL="$PROJECT/UFUG2106_Round8_2_1_Delivery"
cd "$PROJECT"
for needed in "$ORIGINAL/tools/export_feedback.py" "$ORIGINAL/tools/run_official.py" "$ORIGINAL/src/synth_round821.cpp"; do
  [[ -f "$needed" ]] || { echo "Missing frozen Round 8.2.1 dependency: $needed"; exit 2; }
done
mkdir -p "$ORIGINAL/results" "$ORIGINAL/feedback"
STAMP="$(date +%Y%m%d_%H%M%S_%N)_official_probe"
RUN="$ORIGINAL/results/$STAMP"
mkdir -p "$RUN/evaluator_probe_patch"
cp "$PROBE/tools/resources_clean_probe.py" "$PROBE/run_retry.sh" "$PROBE/README.md" "$RUN/evaluator_probe_patch/"
printf '%s\n' "$RUN" > "$ORIGINAL/latest_run.txt"
on_exit(){
 local rc=$?
 trap - EXIT
 python3 "$ORIGINAL/tools/export_feedback.py" --exit-code "$rc" || true
 if (( rc )); then echo "ROUND8.2.1 OFFICIAL PROBE FAILED (exit=$rc); upload feedback ZIP with official logs."; fi
 exit "$rc"
}
trap on_exit EXIT
{
  echo '[1/3] Verify frozen sources and obtain existing binaries'
  [[ -x "$PROJECT/evaluator" ]] || { echo "Missing executable official evaluator: $PROJECT/evaluator"; exit 17; }
  python3 "$ORIGINAL/tools/verify_source.py"
  if [[ ! -x "$ORIGINAL/build/synth_round821" ]]; then make -C "$ORIGINAL" -j1; fi
  echo '[2/3] Isolated resource evaluation (real evaluator; logs and reports outside input directory)'
  flags=()
  bench_flags=()
  for arg in "$@"; do
    case "$arg" in
      --quick) flags+=(--quick); bench_flags+=(--quick);;
      --resources-only) ;;
      --single-file-only) flags+=(--single-file-only);;
      *) echo "Unknown option $arg"; exit 2;;
    esac
  done
  python3 "$PROBE/tools/resources_clean_probe.py" --results "$RUN" "${flags[@]}"
  if [[ " $* " == *' --resources-only '* ]]; then
    echo 'RESOURCE_PROBE_ONLY: PASS; Stage 1/2 not run.'
  else
    echo '[3/3] Paired official Stage 1+2 regression (frozen synthesis code)'
    if [[ ! -x "$PROJECT/UFUG2106_Round8_2_Delivery/build/synth_round82" ]]; then
      make -C "$PROJECT/UFUG2106_Round8_2_Delivery" build/synth_round82 -j1
    fi
    runs=2
    if [[ " $* " == *' --quick '* ]]; then runs=1; fi
    python3 "$ORIGINAL/tools/run_official.py" --results "$RUN" --runs "$runs" "${bench_flags[@]}"
    echo 'ROUND8.2.1_OFFICIAL_PROBE: PASS'
  fi
} 2>&1 | tee "$ORIGINAL/results/latest_test.log" "$RUN/main.log"

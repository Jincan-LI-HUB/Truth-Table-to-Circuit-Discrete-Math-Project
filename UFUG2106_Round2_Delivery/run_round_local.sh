#!/usr/bin/env bash
# Round 1 / Round 2 reproducible WSL runner. Original solver source is not modified.
# usage: bash run_round_local.sh /tmp/ufug2106_evaluator '/mnt/e/.../Final Project/data/stage1'
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT"
ROUND_NAME="Round2"
if [[ $# -ne 2 ]]; then echo 'Usage: bash run_round_local.sh EVALUATOR_FILE STAGE1_DIRECTORY' >&2; exit 2; fi
EVALUATOR="$(realpath "$1")"
CASES="$(realpath "$2")"
for c in g++ make python3 sha256sum; do
  if ! command -v "$c" >/dev/null 2>&1; then echo "Missing tool: $c" >&2; exit 2; fi
done
if [[ ! -f "$EVALUATOR" || ! -d "$CASES" ]]; then
  echo 'Evaluator or Stage1 directory missing.' >&2; exit 2
fi
if [[ ! -x "$EVALUATOR" ]]; then echo 'Evaluator lacks execute permission; copy to /tmp and chmod +x.' >&2; exit 2; fi
[[ -f src/synth.cpp && -f results/reference.csv && -f tools/verify_netlist.py ]] || { echo 'Incomplete Round package.' >&2; exit 2; }
CASE_COUNT="$(find "$CASES" -maxdepth 1 -type f -name 'case_*.txt' | wc -l)"
[[ "$CASE_COUNT" == 25 ]] || { echo "Expected 25 cases but got $CASE_COUNT" >&2; exit 2; }
STAMP="$(date +'%Y%m%d_%H%M%S')"
RUN="$ROOT/local_runs/${STAMP}_${ROUND_NAME}"
if [[ -e "$RUN" ]]; then RUN="${RUN}_$$"; fi
mkdir -p "$RUN/outputs"
cp src/synth.cpp "$RUN/synth_source_snapshot.cpp"
cp Makefile "$RUN/Makefile_snapshot"
cp results/reference.csv "$RUN/reference.csv"
find "$CASES" -maxdepth 1 -type f -name 'case_*.txt' -print0 | sort -z | xargs -0 -r sha256sum > "$RUN/case_sha256.txt"
{
  echo "round=$ROUND_NAME"; echo "timestamp=$(date -Is)"
  echo "project=$ROOT"; echo "evaluator=$EVALUATOR"; echo "cases=$CASES"
  echo "uname=$(uname -srm)"; echo "compiler=$(g++ --version | head -1)"
  echo "python=$(python3 --version)"; echo "case_count=$CASE_COUNT"
  echo '--- OS ---'; [[ ! -e /etc/os-release ]] || cat /etc/os-release
  echo '--- CPU ---'; if command -v lscpu >/dev/null; then lscpu | head -35; fi
  echo '--- Source SHA256 ---'; sha256sum src/synth.cpp
  echo '--- Evaluator SHA256 ---'; sha256sum "$EVALUATOR"
} > "$RUN/environment.txt" 2>&1
printf '\n[1/5] Compile from source (%s) ...\n' "$ROUND_NAME"
{ make clean; make; } > "$RUN/build.log" 2>&1 || { cat "$RUN/build.log"; exit 1; }
sha256sum ./synth > "$RUN/executable_sha256.txt"
printf '[2/5] Evaluate all Stage1 cases ...\n'
set +e
"$EVALUATOR" "$ROOT/synth" "$CASES" --report "$RUN/official.csv" --save-outputs "$RUN/outputs" > "$RUN/evaluator.log" 2>&1
EVALUATOR_RC=$?
set -e
printf 'evaluator_exit_code=%s\n' "$EVALUATOR_RC" >> "$RUN/environment.txt"
tail -n 4 "$RUN/evaluator.log" || true
printf '[3/5] Independently verify (exhaustive n<=13, sampled n>13) ...\n'
VERIFY_RC=0
: > "$RUN/independent_verification.log"
for casefile in "$CASES"/case_*.txt; do
  caseid="$(basename "${casefile%.txt}")"
  net="$RUN/outputs/${caseid}.output.txt"
  if [[ -f "$net" ]]; then
    if ! python3 "$ROOT/tools/verify_netlist.py" "$casefile" "$net" >> "$RUN/independent_verification.log" 2>&1; then
      echo "FAILED: $caseid" | tee -a "$RUN/independent_verification.log"; VERIFY_RC=1
    fi
  else
    echo "MISSING: $net" | tee -a "$RUN/independent_verification.log"; VERIFY_RC=1
  fi
done
printf 'independent_verifier_failed=%s\n' "$VERIFY_RC" >> "$RUN/environment.txt"
printf '[4/5] Compare local run with historical reference ...\n'
SUMMARY_RC=0
if [[ -f "$RUN/official.csv" ]]; then
  python3 "$ROOT/summarize_round.py" "$ROUND_NAME" "$RUN/official.csv" "$ROOT/results/reference.csv" "$RUN/summary.txt" "$RUN/per_case_comparison.csv" > "$RUN/summary_console.txt" 2>&1 || SUMMARY_RC=1
  cat "$RUN/summary_console.txt"
else
  echo 'Official CSV missing' > "$RUN/summary_console.txt"; SUMMARY_RC=1
fi
printf 'summary_failed=%s\n' "$SUMMARY_RC" >> "$RUN/environment.txt"
# Cross-check the independent simulator's area/delay against the official CSV.
if ! python3 "$ROOT/tools/audit_verification.py" "$RUN" "$CASES" > "$RUN/verification_audit.log" 2>&1; then
  echo 'Independent/official area-delay crosscheck FAILED.' >&2
  VERIFY_RC=1
fi
cat "$RUN/verification_audit.log"
printf 'crosscheck_failed=%s\n' "$VERIFY_RC" >> "$RUN/environment.txt"
printf '[5/5] Create shareable evidence ZIP ...\n'
ARCHIVE="$ROOT/local_runs/$(basename "$RUN")_local_results.zip"
(
  cd "$(dirname "$RUN")"
  python3 -m zipfile -c "$(basename "$ARCHIVE")" "$(basename "$RUN")"
)
printf '\nEvidence: %s\n' "$ARCHIVE"
if (( EVALUATOR_RC != 0 || VERIFY_RC != 0 || SUMMARY_RC != 0 )); then
 echo 'WARNING: one or more steps failed. Preserve and share the evidence ZIP.' >&2
 exit 1
fi

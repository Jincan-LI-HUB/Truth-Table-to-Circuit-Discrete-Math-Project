#!/usr/bin/env bash
# Rebuild and evaluate UFUG2106 Round 3 locally; preserve logs and results.
# Place this file and summarize_round3.py in the UFUG2106_Round3_Delivery root.
# Usage: bash run_round3_local.sh [EVALUATOR_FILE] [STAGE1_DIRECTORY]
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT"
if [[ ! -f src/synth.cpp || ! -f Makefile || ! -f results/final_release.csv ]]; then
  echo 'ERROR: place this script in the UFUG2106_Round3_Delivery root.' >&2; exit 2
fi
for cmd in g++ make python3; do
  if ! command -v "$cmd" >/dev/null 2>&1; then
    echo "ERROR: missing $cmd; install build-essential / python3 in Ubuntu." >&2; exit 2
  fi
done

pick_unique() {
  local type="$1" name="$2"
  local -a found=()
  mapfile -t found < <(find "$(dirname "$ROOT")" -maxdepth 5 -type "$type" -name "$name" -print | sort)
  if (( ${#found[@]} != 1 )); then
    echo "ERROR: found ${#found[@]} matches for $name. Specify its path manually:" >&2
    printf '  %s\n' "${found[@]}" >&2
    exit 2
  fi
  printf '%s\n' "${found[0]}"
}

EVAL_PATH="${1:-}"
CASES_PATH="${2:-}"
[[ -n "$EVAL_PATH" ]] || EVAL_PATH="$(pick_unique f evaluator)"
[[ -n "$CASES_PATH" ]] || CASES_PATH="$(pick_unique d stage1)"
EVAL_PATH="$(realpath "$EVAL_PATH")"
CASES_PATH="$(realpath "$CASES_PATH")"
if [[ ! -f "$EVAL_PATH" || ! -d "$CASES_PATH" ]]; then
  echo 'ERROR: evaluator file or stage1 directory not found.' >&2; exit 2
fi
if [[ ! -x "$EVAL_PATH" ]]; then
  echo "ERROR: evaluator is not executable. Try: chmod +x \"$EVAL_PATH\"" >&2; exit 2
fi
if (( $(find "$CASES_PATH" -maxdepth 1 -type f -name 'case_*.txt' | wc -l) != 25 )); then
  echo 'WARNING: test directory does not contain exactly 25 case_*.txt files.' >&2
fi

STAMP="$(date +'%Y%m%d_%H%M%S')"
RUN="$ROOT/local_runs/$STAMP"
mkdir -p "$RUN/outputs"
# Keep the exact source/build recipe that produced this experiment.
cp "$ROOT/src/synth.cpp" "$RUN/synth_source_snapshot.cpp"
cp "$ROOT/Makefile" "$RUN/Makefile_snapshot"
# Input fingerprints allow later checking without redistributing the instructor cases.
find "$CASES_PATH" -maxdepth 1 -type f -name "case_*.txt" -print0 | sort -z | xargs -0 -r sha256sum > "$RUN/case_sha256.txt"
{
  echo "timestamp=$(date -Is)"
  echo "project=$ROOT"
  echo "evaluator=$EVAL_PATH"
  echo "cases=$CASES_PATH"
  echo "uname=$(uname -srm)"
  echo "g++=$(g++ --version | head -1)"
  echo "python=$(python3 --version)"
  echo '--- OS ---'
  if [[ -f /etc/os-release ]]; then cat /etc/os-release; fi
  echo '--- CPU ---'
  if command -v lscpu >/dev/null 2>&1; then lscpu | head -35; fi
  echo '--- Source hash ---'
  sha256sum src/synth.cpp
  echo '--- Evaluator hash ---'
  sha256sum "$EVAL_PATH"
  echo '--- Case count ---'
  find "$CASES_PATH" -maxdepth 1 -name 'case_*.txt' -type f | wc -l
} > "$RUN/environment.txt" 2>&1

printf '\n[1/5] Fresh compilation...\n'
{
  make clean
  make
} > "$RUN/build.log" 2>&1 || { cat "$RUN/build.log"; exit 1; }
sha256sum ./synth > "$RUN/executable_sha256.txt"

printf '[2/5] Running official evaluator on %s ...\n' "$CASES_PATH"
set +e
"$EVAL_PATH" "$ROOT/synth" "$CASES_PATH" \
  --report "$RUN/official.csv" \
  --save-outputs "$RUN/outputs" \
  > "$RUN/evaluator.log" 2>&1
EV_RC=$?
set -e
printf 'evaluator_exit_code=%s\n' "$EV_RC" >> "$RUN/environment.txt"
tail -n 3 "$RUN/evaluator.log" || true

printf '[3/5] Independent netlist verification (exhaustive for n<=13, sampled otherwise)...\n'
VERIFY_FAILED=0
if [[ -f "$ROOT/tools/verify_netlist.py" ]]; then
  : > "$RUN/independent_verification.log"
  for file in "$CASES_PATH"/case_*.txt; do
    [[ -f "$file" ]] || continue
    stem="$(basename "${file%.txt}")"
    net="$RUN/outputs/${stem}.output.txt"
    if [[ -f "$net" ]]; then
      if ! python3 "$ROOT/tools/verify_netlist.py" "$file" "$net" \
          >> "$RUN/independent_verification.log" 2>&1; then
        echo "Independent verifier FAILED: $stem" | tee -a "$RUN/independent_verification.log"
        VERIFY_FAILED=1
      fi
    else
      echo "Missing netlist: $net" | tee -a "$RUN/independent_verification.log"
      VERIFY_FAILED=1
    fi
  done
else
  echo 'Independent checker missing from tools directory.' > "$RUN/independent_verification.log"
  VERIFY_FAILED=1
fi
printf 'independent_verifier_failed=%s\n' "$VERIFY_FAILED" >> "$RUN/environment.txt"

printf '[4/5] Summarizing and comparing with packaged historical results...\n'
if [[ -f "$RUN/official.csv" && -f "$ROOT/summarize_round3.py" ]]; then
  python3 "$ROOT/summarize_round3.py" \
    "$RUN/official.csv" "$ROOT/results/final_release.csv" \
    "$RUN/summary.txt" "$RUN/per_case_comparison.csv" \
    | tee "$RUN/summary_console.txt" || true
else
  echo 'Cannot create summary (missing report or summarize_round3.py). See evaluator.log.'
fi

printf '[5/5] Packaging evidence...\n'
python3 - "$RUN" <<'PY'
import sys, zipfile
from pathlib import Path
run = Path(sys.argv[1]); archive = run.parent / (run.name + '_Round3_local_results.zip')
with zipfile.ZipFile(archive, 'w', compression=zipfile.ZIP_DEFLATED, compresslevel=6) as z:
    for f in sorted(run.rglob('*')):
        if f.is_file():
            z.write(f, arcname=str(Path(run.name) / f.relative_to(run)))
print('Evidence ZIP:', archive)
PY
printf '\nCompleted. Local run: %s\n' "$RUN"
if (( EV_RC != 0 || VERIFY_FAILED != 0 )); then
  echo 'WARNING: evaluator or independent verification failed; keep logs and share them for diagnosis.' >&2
  exit 1
fi

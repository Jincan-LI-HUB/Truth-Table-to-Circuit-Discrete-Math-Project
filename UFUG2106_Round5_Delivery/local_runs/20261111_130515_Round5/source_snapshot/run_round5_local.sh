#!/usr/bin/env bash
# Usage: bash run_round5_local.sh EVALUATOR STAGE1_CASES_DIR
# Builds and evaluates frozen Round 4.1 Balanced vs Round 5 in the same WSL run.
# No sudo, zip executable, or network access required.
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT"
if [[ $# -ne 2 ]]; then echo 'Usage: run_round5_local.sh EVALUATOR STAGE1_DIR' >&2; exit 2; fi
EVAL="$(realpath "$1")"; CASES="$(realpath "$2")"
[[ -x "$EVAL" && -d "$CASES" ]] || { echo 'Invalid evaluator or cases directory' >&2; exit 2; }
for t in python3 g++ make sha256sum; do command -v "$t" >/dev/null || { echo "Missing tool: $t" >&2; exit 2; }; done
[[ "$(find "$CASES" -maxdepth 1 -name 'case_*.txt' -type f | wc -l)" == 25 ]] || { echo 'Expected exactly 25 stage1 case files' >&2; exit 2; }
STAMP="$(date +'%Y%m%d_%H%M%S')"
RUN="$ROOT/local_runs/${STAMP}_Round5"
[[ ! -e "$RUN" ]] || RUN="${RUN}_$$"
mkdir -p "$RUN"/source_snapshot "$RUN"/report_ready "$RUN"/reference/outputs "$RUN"/round5/outputs "$RUN"/profiles
cp -a src Makefile summarize_round5.py run_round5_local.sh tools "$RUN/source_snapshot/"
sha256sum tests/generated_110/case_*.txt tests/stress/case_*.txt > "$RUN/generated_stress_sha256.txt"
cp docs/ROUND5_MATHEMATICAL_DESIGN.md "$RUN/report_ready/mathematical_design.md"
cp docs/ROUND5_REFERENCE_EXPERIMENT.md "$RUN/report_ready/reference_experiment.md"
{
 echo 'UFUG2106 Round 5 - reproducible paired benchmark'
 echo "timestamp=$(date -Is)"
 echo "uname=$(uname -srm)"
 echo "compiler=$(g++ --version | head -1)"
 echo "python=$(python3 --version)"
 echo "cases=$CASES"
 echo "evaluator=$EVAL"
 echo '--- CPU ---'
 (command -v lscpu >/dev/null && lscpu | head -30) || true
 echo '--- Source/evaluator hashes ---'
 sha256sum "$EVAL" src/*.cpp src/*.hpp Makefile
} > "$RUN/environment.txt" 2>&1
find "$CASES" -maxdepth 1 -type f -name 'case_*.txt' -print0 | sort -z | xargs -0 sha256sum > "$RUN/case_sha256.txt"
make clean > "$RUN/build.log" 2>&1
make -j1 >> "$RUN/build.log" 2>&1
for variant in reference round5; do
 echo "[Official evaluator] $variant"
 "$EVAL" "$ROOT/build/synth_$variant" "$CASES" \
     --report "$RUN/$variant/official.csv" \
     --save-outputs "$RUN/$variant/outputs" > "$RUN/$variant/evaluator.log" 2>&1
 tail -n 1 "$RUN/$variant/evaluator.log"
done
: > "$RUN/round5/independent_verification.log"
FAILED=0
for case in "$CASES"/case_*.txt; do
 stem="$(basename "${case%.txt}")"
 out="$RUN/round5/outputs/${stem}.output.txt"
 if ! python3 tools/verify_netlist.py "$case" "$out" >> "$RUN/round5/independent_verification.log" 2>&1; then
  echo "FAILED $stem" >> "$RUN/round5/independent_verification.log"
  FAILED=$((FAILED+1))
 fi
done
echo "independent_failures=$FAILED" > "$RUN/round5/verification_summary.txt"
[[ "$FAILED" -eq 0 ]] || { echo 'Independent verification failed; retain logs' >&2; exit 1; }
python3 summarize_round5.py "$RUN" > "$RUN/summary_console.txt" 2>&1
cat "$RUN/summary_console.txt"
# Additional reproducible regression sets. Their target delays are synthetic.
if [[ -d "$ROOT/tests/generated_110" ]]; then
 echo '[Regression] 110 generated Truth Tables'
 "$EVAL" "$ROOT/build/synth_round5" "$ROOT/tests/generated_110" \
   --report "$RUN/round5/generated_110.csv" > "$RUN/round5/generated_110.log" 2>&1
 tail -n 1 "$RUN/round5/generated_110.log"
fi
if [[ -d "$ROOT/tests/stress" ]]; then
 echo '[Regression] 2 structured stress Truth Tables'
 "$EVAL" "$ROOT/build/synth_round5" "$ROOT/tests/stress" \
   --report "$RUN/round5/stress.csv" > "$RUN/round5/stress.log" 2>&1
 tail -n 1 "$RUN/round5/stress.log"
fi
for c in case_001 case_005 case_024; do
 casefile="$CASES/$c.txt"
 if [[ -f "$casefile" ]]; then
    UFUG_ROUND5_PROFILE=1 "$ROOT/build/synth_round5" "$casefile" \
      "$RUN/profiles/$c.output.txt" > "$RUN/profiles/$c.stdout" \
      2> "$RUN/profiles/$c.stages.log"
 fi
done
cat > "$RUN/report_ready/README.md" <<'MD'
# Round 5 report_ready

The local comparison is `local_reproduction_report.md`. The algorithm design
and proofs are in `mathematical_design.md`, and `reference_experiment.md` is
**historical container evidence** distinct from this new local run.

The actual official CSV, output circuits, compiler/source fingerprints,
independent checker log and stage profiler logs are retained one directory up.
Keep the frozen Round 4.1 source and historical logs unchanged.
MD
python3 - "$RUN" <<'PY'
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED
import sys
run=Path(sys.argv[1]);out=run.parent/(run.name+'_local_results.zip')
with ZipFile(out,'w',compression=ZIP_DEFLATED,compresslevel=5) as z:
 for f in sorted(run.rglob('*')):
  if f.is_file(): z.write(f,arcname=str(Path(run.name)/f.relative_to(run)))
print('Evidence package:',out)
PY

#!/usr/bin/env bash
# Round 4 local WSL reproduction with no system zip dependency.
# Usage: bash run_round4_local.sh /tmp/ufug2106_evaluator '/mnt/e/.../data/stage1'
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT"
if [[ $# -ne 2 ]]; then
  echo 'Usage: bash run_round4_local.sh EVALUATOR_FILE STAGE1_DIRECTORY' >&2; exit 2
fi
EVAL="$(realpath "$1")"
CASES="$(realpath "$2")"
for c in g++ make python3 sha256sum;do
  if ! command -v "$c" >/dev/null;then echo "Missing tool: $c" >&2;exit 2;fi
done
if [[ ! -f "$EVAL" || ! -x "$EVAL" || ! -d "$CASES" ]];then
 echo 'Evaluator must be an executable file; Stage1 must be a directory.' >&2;exit 2
fi
[[ "$(find "$CASES" -maxdepth 1 -name 'case_*.txt' -type f | wc -l)" -eq 25 ]] || { echo 'Expected 25 published cases.' >&2;exit 2; }
for file in src/synth.cpp src/polarity_mapper.hpp src/algebraic_mapper.hpp results/reference_round3.csv results/reference_round4.csv tools/verify_netlist.py tools/audit_verification.py;do
 [[ -f "$file" ]] || { echo "Missing $file" >&2;exit 2; }
done
STAMP="$(date +'%Y%m%d_%H%M%S')"
RUN="$ROOT/local_runs/${STAMP}_Round4"
[[ ! -e "$RUN" ]] || RUN="${RUN}_$$"
mkdir -p "$RUN/outputs" "$RUN/report_ready" "$RUN/source_snapshot"
cp src/synth.cpp src/polarity_mapper.hpp src/algebraic_mapper.hpp "$RUN/source_snapshot/"
cp Makefile "$RUN/source_snapshot/"
cp docs/ROUND4_MATHEMATICAL_DESIGN.md "$RUN/report_ready/mathematical_design.md"
cp docs/ROUND4_EXPERIMENT_LOG.md "$RUN/report_ready/round4_reference_experiment.md"
find "$CASES" -maxdepth 1 -name 'case_*.txt' -type f -print0 | sort -z | xargs -0 -r sha256sum > "$RUN/case_sha256.txt"
{
 echo 'round=Round4'
 echo "timestamp=$(date -Is)"
 echo "project=$ROOT"
 echo "evaluator=$EVAL"
 echo "cases=$CASES"
 echo "uname=$(uname -srm)"
 echo "compiler=$(g++ --version | head -1)"
 echo "python=$(python3 --version)"
 echo '--- system ---'
 [[ ! -f /etc/os-release ]] || cat /etc/os-release
 echo '--- cpu ---'
 if command -v lscpu >/dev/null; then lscpu | head -35;fi
 echo '--- source / evaluator SHA256 ---'
 sha256sum src/synth.cpp src/polarity_mapper.hpp src/algebraic_mapper.hpp Makefile "$EVAL"
} > "$RUN/environment.txt" 2>&1
printf '\n[1/6] Build C++ from source...\n'
{ make clean; make; } > "$RUN/build.log" 2>&1 || { cat "$RUN/build.log";exit 1; }
sha256sum ./synth > "$RUN/executable_sha256.txt"
printf '[2/6] Official 25-case evaluator...\n'
set +e
"$EVAL" "$ROOT/synth" "$CASES" --report "$RUN/official.csv" --save-outputs "$RUN/outputs" > "$RUN/evaluator.log" 2>&1
EV_RC=$?
set -e
printf 'evaluator_exit_code=%s\n' "$EV_RC" >> "$RUN/environment.txt"
tail -n 3 "$RUN/evaluator.log" || true
printf '[3/6] Independent bit-parallel verification...\n'
VERIFY_RC=0
: > "$RUN/independent_verification.log"
for casefile in "$CASES"/case_*.txt;do
 stem="$(basename "${casefile%.txt}")"
 net="$RUN/outputs/${stem}.output.txt"
 if [[ ! -f "$net" ]];then echo "MISSING: $stem" >> "$RUN/independent_verification.log"; VERIFY_RC=1; continue;fi
 if ! python3 tools/verify_netlist.py "$casefile" "$net" >> "$RUN/independent_verification.log" 2>&1;then
  echo "FAILED: $stem" | tee -a "$RUN/independent_verification.log";VERIFY_RC=1
 fi
done
printf 'independent_verifier_failed=%s\n' "$VERIFY_RC" >> "$RUN/environment.txt"
printf '[4/6] Independently cross-check official area and delay...\n'
AUDIT_RC=0
python3 tools/audit_verification.py "$RUN" "$CASES" > "$RUN/verification_audit.log" 2>&1 || AUDIT_RC=1
cat "$RUN/verification_audit.log"
printf '[5/6] Compare local results with Round 4 and Round 3 references...\n'
SUMMARY_RC=0
python3 summarize_round4.py "$RUN/official.csv" results/reference_round4.csv results/reference_round3.csv \
 "$RUN/summary.txt" "$RUN/per_case_comparison.csv" > "$RUN/summary_console.txt" 2>&1 || SUMMARY_RC=1
cat "$RUN/summary_console.txt"
if [[ -f "$RUN/summary.txt" ]];then
 cp "$RUN/summary.txt" "$RUN/report_ready/local_metrics.md"
fi
cat > "$RUN/report_ready/README.md" <<'MD'
# Round 4 Report-ready directory

Keep the final Round 4 stage report in this directory after local review.

- `mathematical_design.md`: implementation-grounded mathematical design and proofs.
- `round4_reference_experiment.md`: previous container measurement, NOT the local result.
- `local_metrics.md`: your machine's measured results from this local run.
- `../official.csv`, `../per_case_comparison.csv`: measured per-case evidence.
- `../independent_crosscheck.csv`: independent verification evidence.

Do not overwrite the Round 3/previous-round evidence. Distinguish official PASS from target delay success, and keep the frozen source snapshot.
MD
printf '[6/6] ZIP evidence (Python standard library; no apt/sudo/zip needed)...\n'
python3 - "$RUN" <<'PY'
from pathlib import Path
import sys,zipfile
p=Path(sys.argv[1]);zpath=p.parent/(p.name+'_local_results.zip')
with zipfile.ZipFile(zpath,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=6) as z:
    for file in sorted(p.rglob('*')):
        if file.is_file():z.write(file,arcname=str(Path(p.name)/file.relative_to(p)))
print('Evidence archive:',zpath)
PY
printf '\nReport-ready directory: %s/report_ready\n' "$RUN"
printf 'Share the *_Round4_local_results.zip file after completion.\n'
if (( EV_RC != 0 || VERIFY_RC != 0 || AUDIT_RC != 0 || SUMMARY_RC != 0 ));then
 echo 'WARNING: some validation steps failed. Preserve the generated logs.' >&2
 exit 1
fi

#!/usr/bin/env bash
# Verify the WSL-local Stage 1 Round 5.1 source, gather publication evidence,
# and produce a self-contained private evidence ZIP. Does not modify old rounds.
set -euo pipefail
BASE="${1:-/mnt/e/canfiles/Common courses study/大学通识/26-27 Fall/UFUG 2106 Discrete Math/assignment/Final Project}"
RUN="$BASE/UFUG2106_Round5.1_Delivery/local_runs/20261111_134547_Round5.1"
CASES="$BASE/data/stage1"
EVALUATOR="$BASE/evaluator"
EXPECTED="cf90d0b110e6f45d1d508db351c95f10e7d704824fc34e17e6a5f5b783e20759"

if [[ ! -f "$RUN/source_snapshot/src/synth_round51.cpp" ]]; then
  echo "[ERROR] Cannot find the expected WSL-local Round 5.1 run directory:" >&2
  echo "  $RUN" >&2
  echo "Look for it with:" >&2
  echo "  find \"$BASE\" -type f -name synth_round51.cpp" >&2
  exit 2
fi
if [[ ! -f "$EVALUATOR" ]]; then
  echo "[ERROR] Official evaluator not found: $EVALUATOR" >&2
  exit 2
fi
if [[ ! -d "$CASES" ]]; then
  echo "[ERROR] Official cases not found: $CASES" >&2
  exit 2
fi
if [[ ! -f "$RUN/benchmark/run1_round51.csv" ]]; then
  echo "[ERROR] Official evaluation record missing" >&2
  exit 2
fi

ACTUAL="$(sha256sum "$RUN/source_snapshot/src/synth_round51.cpp" | awk '{print $1}')"
echo "Expected Round 5.1 source SHA-256: $EXPECTED"
echo "Current  Round 5.1 source SHA-256: $ACTUAL"
if [[ "$ACTUAL" != "$EXPECTED" ]]; then
  echo "[STOP] Source differs from the previously evaluated snapshot. No freeze was created." >&2
  exit 3
fi

OUT="$BASE/Stage1_Freeze_Round5.1_Verified"
if [[ -e "$OUT" || -e "$OUT.zip" ]]; then
  echo "[STOP] Output already exists. It will not be overwritten: $OUT" >&2
  exit 4
fi
mkdir -p "$OUT/source_snapshot" "$OUT/evidence/benchmark" "$OUT/evidence/holdout" "$OUT/evidence/provenance" "$OUT/evidence/report_ready" "$OUT/evidence/official_outputs_run1"
cp -a "$RUN/source_snapshot/." "$OUT/source_snapshot/"
cp "$RUN/benchmark/"*.csv "$OUT/evidence/benchmark/"
cp "$RUN/benchmark/independent_verification.log" "$OUT/evidence/benchmark/"
cp -a "$RUN/benchmark/run1_round51_outputs/." "$OUT/evidence/official_outputs_run1/"
cp "$RUN/holdout/"*.csv "$OUT/evidence/holdout/"
cp "$RUN/report_ready/"*.md "$OUT/evidence/report_ready/"
for f in environment.txt summary.json build.log cases_sha256.txt holdouts_sha256.txt per_case_comparison.csv; do
  if [[ -f "$RUN/$f" ]]; then cp "$RUN/$f" "$OUT/evidence/provenance/$f"; fi
done
sha256sum "$EVALUATOR" > "$OUT/evidence/provenance/evaluator.sha256"
( cd "$OUT/source_snapshot" && find src -type f \( -name '*.cpp' -o -name '*.hpp' \) -print0 | sort -z | xargs -0 sha256sum ) > "$OUT/evidence/provenance/source_files.sha256"

{
  printf '# Stage 1 case input headers (local inspection only)\n'
  printf '# These are short previews, NOT a robust parser for target_delay.\n'
  for f in "$CASES"/case_*.txt; do
    [[ -f "$f" ]] || continue
    printf '\n===== %s =====\n' "$(basename "$f")"
    sed -n '1,9p' "$f"
  done
} > "$OUT/evidence/provenance/case_header_preview_LOCAL_ONLY.txt"

{
  printf '# Optional ablation / profiling records located under your round folders\n'
  for dir in "$BASE"/UFUG2106_Round*_Delivery "$BASE"/UFUG2106_Round6.0_Prototype; do
    [[ -d "$dir" ]] || continue
    find "$dir" -type f \( -iname '*ablation*.csv' -o -iname '*profil*.csv' -o -iname '*ablation*.json' \) -print
  done
} > "$OUT/evidence/provenance/optional_ablation_files_found.txt"

( cd "$OUT" && find . -type f ! -path './evidence/provenance/collected_files.sha256' -print0 | sort -z | xargs -0 sha256sum ) > "$OUT/evidence/provenance/collected_files.sha256"

cat > "$OUT/README.md" <<'TXT'
# Stage 1 FROZEN Round 5.1 — private research provenance

Canonical course-report source: `source_snapshot/src/synth_round51.cpp`, with all
headers in `source_snapshot/src/`. Exact source SHA-256 is verified by the collector.

This archive preserves the source from the user's 20261111_134547 WSL local run,
together with the official evaluator CSVs, representative outputs, independent
verification, holdout CSVs, compiler/environment facts and input checksums.

The local private evaluator and full course case inputs are intentionally NOT
included. `case_header_preview_LOCAL_ONLY.txt` is only for determining the input
metadata syntax. Do not publish private instructor test material or unredacted
machine paths to a public GitHub repository.

This is a research-source freeze and does not itself prove what was submitted to
Canvas. If the actual submission later differs, keep its exact independent hash.
TXT

# No external zip package required; Python standard library handles packaging.
python3 - "$OUT" <<'PY'
import pathlib, sys, zipfile
root=pathlib.Path(sys.argv[1]); zip_path=root.parent / (root.name + '.zip')
with zipfile.ZipFile(zip_path,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=6) as z:
    for p in sorted(root.rglob('*')):
        if p.is_file(): z.write(p,p.relative_to(root.parent))
with zipfile.ZipFile(zip_path) as z:
    assert z.testzip() is None
print('[OK] Freeze evidence ZIP:',zip_path)
PY
printf '[OK] Source freeze verified, not modified original rounds.\n'

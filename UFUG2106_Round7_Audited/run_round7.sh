#!/usr/bin/env bash
# Audited Round 7 runner: default execution includes all 4 official ablation modes.
set -euo pipefail
DELIVERY="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(dirname "$DELIVERY")"
cd "$ROOT"
echo '[1/5] Materialize and compile Round 7 from frozen Round 5.1'
make -C "$DELIVERY" -j1
echo '[2/5] Verify bootstrap patch'
python3 "$DELIVERY/tests/test_bootstrap.py"
echo '[3/5] Verify cover kernel A/B and persist log'
mkdir -p "$DELIVERY/results/ablation"
python3 "$DELIVERY/tests/test_exact_cover.py" 2>&1 | tee "$DELIVERY/results/ablation/cover_unit_test.log"
echo '[4/5] Official paired evaluations: Round5.1 + Round7 + 3 independent ablations'
# The old script required an undocumented-looking extra --ablate invocation.
# We run that by default, and still allow overriding --runs N from the CLI.
set +e
python3 "$DELIVERY/tools/run_benchmarks.py" --root "$ROOT" --paired --ablate --runs 2 "$@"
STATUS=$?
set -e
echo '[5/5] Produce casewise CSV and audit summary'
python3 "$DELIVERY/tools/audit_results.py"
if [ "$STATUS" -ne 0 ]; then exit "$STATUS"; fi

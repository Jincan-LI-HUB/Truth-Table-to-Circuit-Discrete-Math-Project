#!/usr/bin/env bash
# One-shot WSL runner. No modifications to the frozen Round 5.1 source tree.
set -euo pipefail
DELIVERY="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(dirname "$DELIVERY")"
cd "$ROOT"
echo '[1/4] Materialize and compile Round 7 from the frozen Round 5.1 source'
make -C "$DELIVERY" -j1
echo '[2/4] Test bootstrap patch correctness'
python3 "$DELIVERY/tests/test_bootstrap.py"
echo '[3/4] Run exact-cover A/B correctness tests'
python3 "$DELIVERY/tests/test_exact_cover.py"
echo '[4/4] Official paired evaluation of Stage 1 and Stage 2'
python3 "$DELIVERY/tools/run_benchmarks.py" --root "$ROOT" --paired --runs 2 "$@"

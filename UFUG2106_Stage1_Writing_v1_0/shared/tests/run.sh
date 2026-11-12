#!/usr/bin/env bash
set -euo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
mkdir -p "$HERE/build"
g++ -O2 -std=c++17 -pipe -DNDEBUG -I "$HERE/frozen_src" \
 "$HERE/test_typed_dag_invariants.cpp" -o "$HERE/build/test_typed_dag_invariants"
"$HERE/build/test_typed_dag_invariants"

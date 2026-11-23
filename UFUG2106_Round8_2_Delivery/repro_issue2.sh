#!/usr/bin/env bash
# This does NOT enforce RAM=9000 KiB, it measures actual peak RSS using /usr/bin/time.
set -euo pipefail
BIN="${1:?Usage: bash repro_issue2.sh PATH_TO_EXECUTABLE}"
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$DIR"
python3 generate_issue2_case.py issue2_case_20input_wire_ram9000.txt
/usr/bin/time -f 'PEAK_RSS_KB=%M WALL_S=%e EXIT_CODE=%x' \
  "$BIN" issue2_case_20input_wire_ram9000.txt issue2_out.netlist
head -3 issue2_out.netlist
printf '\nThe official evaluator is still required to test RAM-limit compliance.\n'

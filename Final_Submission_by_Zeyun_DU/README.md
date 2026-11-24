# UFUG2106 Group 2 · Integrated Stage 2 archive

This directory holds the final team version planned for submission. It pins Zeyun Du's integration to commit [`59e33505616d127fc06a63580ca3ae3c34d1da72`](https://github.com/zdu881/UFUG2106-Project/commit/59e33505616d127fc06a63580ca3ae3c34d1da72). The [integration audit](integration/AUDIT.md) records public verification. The course submission status is unverified.

Zeyun Du authored the submitted Z1 solver, coordinated the Stage 2 integration and set its area and timing objectives. Jincan Li developed the independent J51 and R10.0 research lineage. The integrated solver adapts Round 5.1 synthesis and the R10.0 four-leaf cut mapper, credited in the upstream [origin note](src/round51/ORIGIN.md). The upstream Stage 2 report also credits Codex for implementing timing rescue and assisting with verification and packaging. [Upstream release report](reports/stage2-timing-20261124/UFUG2106_Group2_Stage2_Report.pdf)

## Build and verify

From this directory in Linux or WSL, use GCC with C++17 support, GNU Make and Python with NumPy for the independent check.

```bash
make stage2
out=$(mktemp -d)
./build/synth_stage2 examples/shared_outputs.txt "$out/example.net"
python3 tools/check_circuit.py examples/shared_outputs.txt "$out/example.net"
python3 -m unittest discover -s tests -p 'test_*.py'
```

`make stage2-source` creates the upstream source ZIP. Its entry point is `synth_stage2.cpp` at the ZIP root alongside `round51/`. Compile the extracted package with `g++ -O2 -std=c++17 synth_stage2.cpp -o synth`. The [release instructions](releases/stage2/README.md) use that layout.

To evaluate with the existing course materials, run this from the archive directory:

```bash
out=$(mktemp -d)
install -m755 ../evaluator "$out/evaluator"
for bank in stage1 stage2; do
  "$out/evaluator" "$PWD/build/synth_stage2" "../data/$bank" \
    --report "$out/$bank.csv" --save-outputs "$out/$bank-netlists"
  python3 tools/verify_all.py "../data/$bank" "$out/$bank-netlists" \
    "$out/$bank.csv" "$out/$bank-independent.json"
done
```

Some upstream reproduction notes use the original `official/` layout and cite temporary results from the upstream machine. Use the paths above for this archive. The existing course files match the evaluator and input blobs at the pinned commit. [Course attribution and redistribution notice](official/README.md)

## Evidence and attribution

- [Provenance manifest](PROVENANCE.json) lists the imported files, upstream Git blobs, archival hashes and build entry points. The solver and tests preserve upstream bytes. Four upstream reports and their HTML sources retain the authors' names and omit student numbers in these local copies.
- [Earlier four-method comparison](reports/stage2-cuts-20261124/casewise.csv) and [pinned release acceptance runs](reports/stage2-timing-20261124/public-runs.csv) record different Stage 2 snapshots.
- [Matched integration audit](integration/AUDIT.md) documents the local comparison, independent replays, RSS measurement and limits of attribution.

The repository owner confirmed that team members authorized public GitHub archiving of their contributions. No general redistribution license was identified at the pinned commit. Third-party redistribution rights for instructor-provided materials remain unconfirmed. [Course-material notice](official/README.md)

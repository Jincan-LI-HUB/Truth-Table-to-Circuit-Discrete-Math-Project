# Independent Stage 2 Source Build (Round 8.5 Candidate)

This folder is self-contained. It depends on **no previous Round delivery directory** for compilation, linking or the input/output contract. Standard C++17 compiler only.

```bash
cd UFUG2106_Round8_5_Delivery
make
./build/synth_round85 /absolute/path/to/case_001.txt /tmp/out.net
```

Or compile directly:

```bash
g++ -O2 -std=c++17 -pipe -DNDEBUG src/synth_round85.cpp -o synth
./synth input_path output_path
```

The submission should include `src/synth_round85.cpp` and all `src/*.hpp` dependencies (not just a C++ file with unresolved local includes), plus this README or equivalent. `src/synth_round84_frozen.cpp` is included solely for research comparison and is **not needed to compile Round 8.5**. The actual final submission executable must be chosen after paired evaluator results, and source must match the chosen variant. The default `UFUG_R85_POLICY` is `dual_sop_first` until the team explicitly chooses otherwise; export `UFUG_R85_POLICY=dual_sop_first` to select the SOP-first research variant. Do not submit with inconsistent settings.

The grading server environment and hidden tests are not available in this workspace; this is a locally verifiable delivery rather than a guarantee of grading success.

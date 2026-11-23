# Candidate Submission Readiness — R8.6

- Main C++17 source: `src/synth_round86.cpp`. Headers in `src/*.hpp` must be present for compilation.
- Build: `g++ -O2 -std=c++17 -pipe -DNDEBUG -o synth_round86 src/synth_round86.cpp` (working directory root of this delivery).
- Execute: `./synth_round86 input_path output_path`.
- Default policy if none is specified: `UFUG_R86_POLICY=baseline` (factor ablation baseline). This is NOT necessarily the best-scoring final policy.
- Explicit modes: `baseline`, `extra_sop`, `time_reclaim`, `combined`, `reverse_allocation`.
- Reported Area, Delay, and Peak RSS on development cases are not official hidden-case scores.
- Do not directly submit a folder dependent on environment variables or earlier Round packages without checking course submission format, merged teammate code, public and fresh holdout verification, and the final chosen default.

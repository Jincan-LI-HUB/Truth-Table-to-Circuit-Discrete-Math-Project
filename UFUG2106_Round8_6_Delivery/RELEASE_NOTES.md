# Round 8.6 — Release Notes

- Added **orthogonal Root Quota × Time Allowance** experiments with five R86 policies.
- Kept a byte-identical frozen Round 8.5 source to support same-environment comparisons.
- Prevented legacy Round 8–8.5 flags from activating earlier postprocessors while R86 is selected.
- Added runtime budget diagnostics: nominal allowance, current global remainder, actual visited roots, time hit, objective, output area/delay.
- Completed offline 25-case Stage2 × six policies exhaustive equivalence campaign (150 correct netlists; unmodified target delays satisfied); see casewise CSV.
- Packaged cold C++17 compilation and real evaluator replay with two reversed-order paired runs.
- **Not released as final submission:** cannot claim hidden-case performance, official 50-case acceptance, perfect cross-machine determinism, or positive-RAM acceptance without WSL and/or grading results.

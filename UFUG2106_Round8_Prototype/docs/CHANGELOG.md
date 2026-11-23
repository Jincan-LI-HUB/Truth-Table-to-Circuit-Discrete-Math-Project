# Change log

## 2026-11-21 — Round 8.0 prototype

- Froze Round7.2 parent SHA; source-generation patch adds new `r8_structural.hpp` and final global candidate comparison.
- Added structural hashing, absorption, conditional factoring, cost-aware De Morgan, and limited divisor reuse by distributive expansion.
- Added per-node required time propagation and final global delay guard.
- Added `off`, `factor`, `phase`, `reuse`, `all`, `iterate`, `iterate_strict` policies. Default iterate to five passes maximum, stop on no improvement.
- Added C++ exact checker for full n<=20 truth tables, random function tests, one-pass/iterated offline ablations.
- Added official evaluator paired script, per-case provenance, failure-safe feedback ZIP, frozen control and transparent release gate.
- Preserved negative results and the unresolved scoring/holdout constraints in detailed docs.

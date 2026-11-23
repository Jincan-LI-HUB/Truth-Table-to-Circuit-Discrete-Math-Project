# Handoff to R9.1 library-based rewriting

**Before changing the algorithm**, require the official R9.0 public gate and short-limit stress findings. Do not mistake the four `hard_bank/dev` files for a generalization estimate: they were constructed to *activate* Cut Search. Keep the four `hard_bank/lockbox` cases sealed until candidate selection and parameters are frozen.

R9.1 should enumerate local 3- and 4-leaf cut Boolean functions, evaluate a bounded library of AND/OR/NOT alternatives, and accept replacements based on actual DAG removability and target delay, not raw gate counts. Control extra CPU time per candidate. Use the R9.0 standalone source as the fallback. Track discovered cuts, accepted rewrites, runtime, global area/delay and rejected paths. If no reproducible improvement on independent circuits, do not integrate the new mechanism solely for a new Round number.

R9.2 resubstitution is conditional: for divisors depending on more than the current cut leaves, a local cut signature is insufficient proof; require a global Boolean equivalence argument or restrict to provably leaf-expressible nodes.

R10 remains reserved for teammate-integrated Stage2 solver, open Issue #2 BDD budget reallocation, clean source-only build and final report. Follow TA direction: 50 public + 50 hidden grade cases, no positive RAM limit.

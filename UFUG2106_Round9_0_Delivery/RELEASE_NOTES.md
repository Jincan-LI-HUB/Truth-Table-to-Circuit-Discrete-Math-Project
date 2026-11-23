# Round 9.0 release notes

- P0 fixed: unconfigured executable defaults to the researched R8.6 `extra_sop` policy.
- P0 mitigation: bounded-memory streaming semantic signatures on `n>=18, 0<runtime_limit<=250`; full truth table read and mathematical equivalence required before early return.
- P1 fixed: strict per-line canonicalization of 39 existing independent test functions, without changing their mathematical data.
- P1 improved: new, frozen development and sealed-lockbox banks designed to activate root-work quotas, with full reproducibility hashes.
- P1 diagnostics: distinguish input-reading time, search phase, offline wall-clock, original official evaluator status.
- Source-only cold build: no previous delivery folder, no custom grader environment variables.
- Frozen parent source: SHA256 `6d21a7d3cf80a8662f4f42a965e84c50d6cffcef7766a4d2dccf282c204078d8`.
- Limit: official public regressions and adversarial stress evaluator must run on the user's WSL. No hidden-test or RAM-cap pass claim.

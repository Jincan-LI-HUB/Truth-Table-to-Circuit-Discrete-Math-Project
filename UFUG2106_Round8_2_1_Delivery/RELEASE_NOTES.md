# Round 8.2.1 — Release Notes

- **Severity:** correctness/resource compliance, GitHub Issue #2; not a guaranteed new Area improvement.
- **Upstream freeze:** `synth_round82.cpp` SHA-256 `07ca91581854fe3802ae0165674a3352771f1745ea85beee6608ee720f9a1caa`.
- **Changes:** read ninth-line RAM cap independently of runtime; low-RAM preflight; compact affine and per-output support synthesis; bounded packed BDD fallback; conservative eager-BDD admission; zero-Area early stop and tight-cap optional candidate skip.
- **Local gates:** compile PASS; 10 direct 20-input 9,000-KiB cases PASS + exhaustive equality; 24 frozen structured holdouts netlists byte-identical.
- **Official gates:** pending user WSL; never claim official PASS based on the direct local tests.
- **Known limitation:** rare/sufficiently complex functions may return exit 14 if neither a bounded construction nor an admitted eager BDD is available. A conservative size guard does not prove OS peak-RSS compliance for all admitted cases. Official memory-sensitive evaluation remains required.
- **Issue workflow:** do not close Issue #2 until both memory tests and full Stage1/2 official regression are verified, and teammate integration is separately checked. Keep README checkout/reproducibility and budget reallocation as distinct follow-ups.

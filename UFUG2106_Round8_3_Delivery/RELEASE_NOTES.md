# Round 8.3 Release Notes

- **Parent:** frozen `Round 8.2.1`, SHA256 of bundled parent source `7de901424217ad0258e0cfae15f87e8c1a36f40f3c471fe44e7d0e20814200d0`.
- **New:** `r83cut::rewrite(..., work_roots)` deterministic selected-root quota and workload/end-reason statistics (`work_limit_hit`, `budget_hit`).
- **New:** standalone policy multiplexer for area, strict and area-delay product; independent Shannon/SOP branch evaluations.
- **Critical fix:** `R83` activation forcibly disables old R8/R81/R82 postprocessors, preventing configuration contamination.
- **Default:** 900 roots per branch; 600 for `limit<=2000` and `m>=20`. Safety watchdog is retained and can still lead to variation.
- **Public correctness:** 25 Stage2 cases exhaustively checked locally; 24 already-used structured synthetic cases exhaustively checked.
- **Negative evidence:** local same-host total area 500072 for stable vs 499793 for old dual; 1100-root ablation occasionally interrupts on wall time.
- **Validation boundary:** Official Stage1/2 evaluator only on user WSL. Positive RAM evaluator issue remains open. Do not claim hidden-case guarantees.

# Round 8.2 Official Audit + GitHub Issue #2 Risk Triage

Data origin:
- Round8.2_Feedback_20261121_191537_181833.zip, uploaded user feedback (20 official CSV files; 1,000 rows)
- GitHub Issue #2: https://github.com/Jincan-LI-HUB/Truth-Table-to-Circuit-Discrete-Math-Project/issues/2
- Final_Project.pdf (RAM line 9; nonzero limit is enforceable; runtime line 8)
- Round 8.2 source SHA-256 `07ca91581854fe3802ae0165674a3352771f1745ea85beee6608ee720f9a1caa`

The Issue reproducer was compiled from the exact source bytes contained in both the uploaded feedback source snapshot and the supplied Round 8.2 delivery, then executed on local Linux **without the official evaluator's memory enforcement**:

- Input: n=20, m=1, y=x19, AND2/OR2/NOT each area=1 delay=1, target=10, runtime limit=0, RAM limit=9,000 KiB.
- Raw output: `20` (no gates; area=0, delay=0).
- Measured Linux `/usr/bin/time` peak RSS: **34,132 KiB**.
- Teammate reported **13,952 KiB** for a different integrated executable; these numbers are not directly comparable.

The source only reads the optional runtime limit, not the optional RAM limit. The main BDD builder has `orig(N)` and `cur(N)` allocations in addition to eager BDD node and hash reservations. A zero-area early stop *after* the first synthesis candidate cannot guarantee the first candidate was within the memory cap.

These diagnostics establish the existence of a memory overrun risk. Confirmation using the **official evaluator with RAM=9,000 KiB** must be performed on the user's WSL.

## Recommended scheduling

**Round 8.2.1 — resource safety hotfix (before any further quality-focused Round 8.3):** parse both optional limits; implement correct, low-memory detection of constant/literal/simple outputs prior to the BDD; terminate immediately when a zero-area zero-delay incumbent is certified; enforce conservative memory-aware candidate admission; avoid unconditional memory-heavy reserves under RAM constraints; include hard memory-limit stress cases and full Stage1+Stage2 regression. Failure must not be hidden by a correct output circuit.

**Round 8.3 — synthesis efficiency and score sensitivity:** address integrated solver's separate budget inheritance / complementary method selection, as documented by Issue #2, *after* RAM fix is independently validated. Reported `99,068 → 93,786` Area on an artificial large target is an **integrated controlled observation**, not a standalone Round8.2 result.

**Final submission hardening:** README fresh checkout and reproducible single-thread build; actual compilation of delivery from clean checkout, archiving full scripts and env.

## Evidence files

- `Round8_2_Official_Summary_20261121.csv`: by-variant/run aggregate metrics
- `Round8_2_Official_Casewise_Audit_20261121.csv`: all 1,000 official rows plus reference ratios
- `generate_issue2_case.py`: deterministic minimal reproducer generator (truth table size = 2^20)
- `repro_issue2.sh`: compile and measure memory without altering the user's source
- `Round8_2_Official_Postmortem_Issue2.md`: long-form audit and research decisions

None of these files modifies the GitHub issue, source repository, or existing frozen milestones.

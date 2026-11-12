# Round 4 Local Reproduction — Windows 11 + WSL Ubuntu

Extract `UFUG2106_Round4_Delivery.zip` inside your original **Final Project** folder. Use Windows Terminal / PowerShell to start WSL:

```powershell
wsl
```

Copy the following commands directly into your Ubuntu terminal:

```bash
BASE="/mnt/e/canfiles/Common courses study/大学通识/26-27 Fall/UFUG 2106 Discrete Math/assignment/Final Project"
CASES="$BASE/data/stage1"
cp "$BASE/evaluator" /tmp/ufug2106_evaluator
chmod +x /tmp/ufug2106_evaluator
cd "$BASE/UFUG2106_Round4_Delivery"
bash run_round4_local.sh /tmp/ufug2106_evaluator "$CASES"
```

If you already have an executable `/tmp/ufug2106_evaluator` and the `BASE`/`CASES` variables set in the current terminal, the last two lines are sufficient.

No `sudo`, APT networking, or system `zip` installation is necessary. A C++17 compiler, `make`, Python 3, and `sha256sum` must already exist.

The script automatically compiles the Round 4 source, evaluates the teacher's 25 cases, independently simulates the emitted netlists, cross-checks exact Area/Delay, compares with the frozen Round 3 and Round 4 reference CSVs, and stores source snapshots and environment data.

A successful reference reproduces:

- `25/25 PASS`
- `25/25 Target Delay Met`
- `Area Sum: 528,910`

Runtime can differ across computers. Extra search is budget-limited and might select a different candidate on a different CPU; such differences must be recorded rather than silently replaced.

Send the generated file from:

`UFUG2106_Round4_Delivery/local_runs/YYYYMMDD_HHMMSS_Round4_local_results.zip`

Store the finalized Round 4 report under:

`UFUG2106_Round4_Delivery/local_runs/YYYYMMDD_HHMMSS_Round4/report_ready/`

If the test fails, upload the generated ZIP (if created) along with the terminal error. Preserve the run directory for debugging.

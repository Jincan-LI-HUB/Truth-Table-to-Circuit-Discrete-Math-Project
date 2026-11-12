# Reproducible supplementary test generators (source-only archive)

Scripts are retained unchanged from the archived Round 5.1 and Round 6.1 delivery packages. Each writes complete truth-table cases and/or manifests into its own project-relative `tests/` directory. The writing bundle deliberately includes **no generated truth tables**. To regenerate a suite, copy its generator into the original project layout (`tools/` alongside `tests/`) and execute with Python 3, then compare SHA-256 values against the supplied manifests.

- Round5.1 mixed: `round51_generate_holdout_v1.py`, seed `0x51A17C0DE`, 80 functions, 8 families.
- Round5.1 large: `round51_generate_holdout_large_v1.py`, seed `0x515A7E11`, 16 functions, 4 families.
- Round6.1 mixed fresh: `generate_round61_fresh.py`, seed 661061, 40 cases, 5 families.
- Round6.1 large fresh: `generate_round61_large.py`, seed `0x615A7E11`, 8 cases, 4 families.
- Round6.0 40-case development generator included for historical context; do not count its used development data as an untouched holdout.

**Important**: deterministic generator scripts and manifest SHA-256 enable data provenance checks; they do not imply that the case distribution represents unreleased Stage 2. The 110 preexisting regression cases and the two stress cases have metrics in the original freeze archives, but a complete generator provenance for that older suite is not bundled here.

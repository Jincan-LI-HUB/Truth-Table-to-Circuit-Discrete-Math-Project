# Excluded experiment — DO NOT USE

In a preliminary, unshipped stress bank, a script accidentally replaced the **target delay** line with 100, instead of the **runtime limit** line, resulting in an unconstrained or missing time limit. Preliminary measured runtimes were not evidence of violating a 100-ms limit. They were removed from the evidence narrative. The corrected `stress_v2/` has explicit assertions preserving target and setting runtime=100. This incident is recorded for research audit and is NOT part of the ordinary Round 8.7 bank.

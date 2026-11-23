# Round 10.0 Release Notes — candidate, NOT final team integration

## Source change

Single controlled policy-default patch in R9.1 `synth_round91.cpp`:

```diff
- if(const char* r91env=std::getenv("UFUG_R91_POLICY")){
-  const std::string kind=r91env;
+ const char* r91env=std::getenv("UFUG_R91_POLICY");
+ const std::string kind=r91env?r91env:"repeat_sop";
+ {
```

The remaining code, including optional Library and Shannon controls, is bitwise unchanged. The new source and `submission/synth.cpp` are identical by SHA-256; headers also match.

## Pre-release acceptance criteria

1. Source SHA, frozen R9.0 and R9.1 parent SHA, independent submission SHA all pass.
2. No prior Round directories required to compile the submission; entire truth table equivalence on fresh fixture functions.
3. Default, explicit SOP, explicit off, independent submission, frozen R9.0, and frozen R9.1 SOP controls generate valid netlists on all local cases.
4. WSL official Stage1+Stage2 600/600 PASS, 600/600 Target Met (not available locally).
5. Paired Area/Delay/Runtime reported casewise; report wall-clock sensitivity, not just sums.
6. Team integrated code and Issue#2 remain separate Round10.1 tasks.

## Known research limitations

- `repeat_sop` is nominally bounded by 90ms and root cap160, but work/deadline checks are not hard real-time preemption. Real evaluator Runtime is authoritative.
- Explicit opt-in `library` remains available only for diagnostic experiments, and is NOT chosen by default.
- No positive `ram_limit` or hidden-grader performance claim.
- Previous official public improvements may be concentrated in a small number of cases, so no generalization claim.

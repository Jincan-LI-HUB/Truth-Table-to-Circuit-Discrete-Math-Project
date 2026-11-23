# Round 8.1 Delivery Status

- **Revision:** Round 8.1 research prototype (no official score claim)
- **Parent:** Frozen Round 8.0 `synth_round8.cpp` SHA-256 `9ec7dc97161d3dc906dfad7960e0fc232b8e2cf0399908c6c4e99b756d8bacd8`
- **Generated source:** Round 8.1 `synth_round81.cpp` SHA-256 `a12ed21f9d48862be0771d0d15801c81bb280bbff908d8d90932cf43a53d4181`
- **Local build:** C++17 `-O2 -DNDEBUG` PASS.
- **Local functional verification:** 25 Stage 2 cases × 2 integrated configurations (50 exhaustive original-truth-table validations) PASS; 180 random DAGs × 4 resynthesis modes (720 exhaustive validations) PASS; critical Stage1 case020 verified.
- **Local quality:** Stage2 area-priority sum 500,696 vs frozen 508,535; strict-no-delay-regression sum 508,352. Target delay 25/25 in each configuration.
- **User WSL official evaluator:** NOT RUN in this environment; full Stage1 regression also requires user test.
- **Next step:** run `run_round81.sh`, upload auto-created feedback ZIP. Interpret official Area/Delay/Runtime before freezing a release candidate.

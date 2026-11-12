# Round 4.1 — Runtime Optimization — Local WSL Measurements

Reference is the **original frozen Round 4 run on the same WSL machine**, not another host.

| Variant | PASS | Target Met | Area total | Median Runtime (ms) | Max Runtime (ms) |
|---|---:|---:|---:|---:|---:|
| Original Round 4 | 25/25 | 25/25 | 528,910 | 127.568 | 3535.952 |
| strict | 25/25 | 25/25 | 528,910 | 117.527 | 3084.013 |
| balanced | 25/25 | 25/25 | 529,014 | 102.615 | 2699.425 |
| fast | 25/25 | 25/25 | 530,822 | 63.035 | 2273.646 |

Area and Runtime are distinct quality dimensions. All runtimes depend on machine load and filesystem; a single evaluation does not establish a statistical speedup.


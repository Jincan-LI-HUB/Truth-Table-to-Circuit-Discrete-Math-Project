# Round 4.1 — Runtime Optimization — Local WSL Measurements

Reference is the **original frozen Round 4 run on the same WSL machine**, not another host.

| Variant | PASS | Target Met | Area total | Median Runtime (ms) | Max Runtime (ms) |
|---|---:|---:|---:|---:|---:|
| Original Round 4 | 25/25 | 25/25 | 528,910 | 127.568 | 3535.952 |
| strict | 25/25 | 25/25 | 528,910 | 111.149 | 3337.741 |
| balanced | 25/25 | 25/25 | 529,014 | 96.048 | 2697.434 |
| fast | 25/25 | 25/25 | 530,822 | 67.605 | 2299.251 |

Area and Runtime are distinct quality dimensions. All runtimes depend on machine load and filesystem; a single evaluation does not establish a statistical speedup.


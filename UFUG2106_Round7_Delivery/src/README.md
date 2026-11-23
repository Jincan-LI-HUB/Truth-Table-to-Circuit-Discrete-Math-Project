# Generated source directory

`make -C UFUG2106_Round7_Delivery` automatically copies the frozen local
Round 5.1 source and three headers into this folder before compiling.

The ZIP is deliberately a hash-checked offline **source-derived release**:
`src/synth_round7.cpp` is materialized by `bootstrap_round7.py` on your
machine. No file in the existing Round 5.1 directory is modified.

To generate and inspect the complete C++ implementation without compiling:

```bash
python3 UFUG2106_Round7_Delivery/bootstrap_round7.py
```

After generation, the folder contains `synth_round7.cpp`, the required
headers, and `../SOURCE_MANIFEST.json` with source hashes.

# Reproduction Commands

1. Extract package next to `evaluator`, `data/stage1`, `data/stage2`.
2. Run `bash UFUG2106_Round8_6_Delivery/run_round86.sh`.
3. Upload `feedback/Round8.6_Feedback_<timestamp>.zip`.
4. For local research on a separate Stage2 directory:

```bash
python3 UFUG2106_Round8_6_Delivery/tools/run_local_ablation.py \
  --bank data/stage2 \
  --results UFUG2106_Round8_6_Delivery/results/manual_local \
  --cases 25
```

This generates 150 netlists, their independent exhaustive validations, per-policy logs, hashes, timing and a CSV. Use `--resume` to continue without duplicating successful records. The `run_round86.sh` automatic script instead runs a compact essential exhaustive preflight before the genuine 700-case official comparison.

At the end of each official case collection, inspect `results/<timestamp>/official/summary.json`. A release gate covers **public** stages only. No claim about hidden-test performance or positive `ram_limit` is permitted.

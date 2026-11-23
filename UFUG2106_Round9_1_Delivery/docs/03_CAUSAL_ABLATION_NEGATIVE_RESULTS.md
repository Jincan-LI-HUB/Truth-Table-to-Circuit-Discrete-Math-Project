# Round 9.1 controlled ablation and negative findings

## Controls and provenance

The source SHA of the frozen Round 9.0 comparator is exactly `f846b2c055bfd5ad8d252dd1dcaa6770040b290bff6dc2bddc0ab27ff77e4010`. Experimental source SHA at the first sealed-lockbox access is `345982dc0c27bd9862e03bf4b8e14a4741eeaba756212e2ccda114f040f4fb9f`. Test logic was extended after algorithm freeze, but the algorithm source was not changed.

The ablation uses the same Round 9.0 input, costs, target and time limit, then compares optional postprocessors `off`, `library`, `repeat_sop`, `repeat_shannon`. Three active modes have identical policy of at most 160 selected roots and a nominal deadline of `min(90ms, 0.06*limit, remaining safe wall time)` (non-preemptive root work can overrun). This controls the *allowed search resources*, not the exact completed number of roots or number of candidate materializations.

## Local results (NOT official Round 9.1 scores)

| Dataset | Off | Library | Repeat SOP | Repeat Shannon | Delay sum off/library |
|---|---:|---:|---:|---:|---:|
| Four development cases | 38,903 | 38,894 | 38,896 | 38,890 | 138 / 138 |
| 25 Stage 2 public cases | 501,133 | 501,708 | **500,436** | 501,445 | 1,170 / 1,171 |
| Four sealed Lockbox cases | 25,307 | 25,307 | 25,302 | **25,293** | 146 / 146 |

Every output was checked by complete truth-table enumeration. Stage 2: **100/100 exact**. Development: **16/16 exact**. Lockbox: **16/16 exact**. The algorithm's own safety gate only accepts strict full-area improvement on its own parent. Nevertheless, the separately launched programs can start from different parent circuits because the upstream portfolio is wall-time sensitive. This explains cases where a different policy's final Area is worse even though that optional postprocessor did not accept a worse graph.

The library materialized 13,956 independently verified template instances in its dedicated unit test. For `hard_003` it found three successful local substitutions, reducing Area `1933 -> 1924` without Delay change. The library's independent lockbox benefit was **zero** across four cases; old Shannon improved a held-out case. Thus there is **insufficient evidence to claim that the new expression library outperforms additional SOP/Shannon search time**.

## Research decision

The new library is correctly gated and fully reversible, but it is **off by default**. Official WSL evaluation against the user-provided evaluator is pending. Keep frozen R9.0 as the submission-quality fallback. Only promote after a casewise paired improvement in official Stage 1/2 with acceptable Runtime/Delay tradeoffs; otherwise archive the library as a negative experimental result and move to integration.

Notes: one early developmental version mistakenly returned exit code 27 for short-budget inputs; it was fixed before this package and verified using 100ms stress cases. This defect is NOT present in the shipped source.

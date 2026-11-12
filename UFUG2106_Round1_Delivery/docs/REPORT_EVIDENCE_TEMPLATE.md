# Round 1 · 最终 Report 中建议保留的内容

## Methodology（数学）

- **Formal input model**：定义 \(F:\{0,1\}^n\to\{0,1\}^m\)，澄清 MSB-first 行索引。
- **Correctness baseline**：Shannon Expansion 与 cofactors，证明 \(f=\neg x f_0\lor xf_1\)。
- **ROBDD representation**：固定顺序、`(variable, lo, hi)` 唯一化、相等 Cofactor 的直接删除、不同输出共享子图；严格说明正确性保持。
- **Gate mapping**：常量化简、Structural Hashing、只保留最终输出可达门，按拓扑顺序编号。
- **Cost model**：Area、Delay、Runtime 三种指标及 Gate Costs 按案例变化。
- **Complexity**：至少读取 \(m2^n\) 位输入；期望 \(O(m2^n)\) 的 BDD 构造上界（固定顺序、Hash 期望均摊常数），最坏可能指数级。

## Experiments（运行结束后填入）

| Field | Evidence file | Recorded value |
|---|---|---|
| Source SHA-256 | `environment.txt`, `SOURCE_PROVENANCE.txt` | 待本地复现 |
| Compiler/CPU/OS | `environment.txt` | 待本地复现 |
| Official PASS | `official.csv` | 待本地复现 |
| Target Delay Met | `official.csv`, `summary.txt` | 待本地复现 |
| Area total | `summary.txt` | 待本地复现 |
| Median/maximum runtime | `summary.txt` | 待本地复现 |
| Per-case Area/Delay | `official.csv`, `per_case_comparison.csv` | 待本地复现 |
| Independent verification | `independent_verification.log` | 待本地复现 |

历史参考为 25/25 PASS、12/25 Target Met、Area 1,103,455。**不要直接抄写历史 Runtime 作为用户的本地测量。**

## Discussion（不要遗漏）

- 13 个未达标的案例为什么仍然被判 PASS？
- 固定变量顺序如何影响 BDD 节点数和最后的 Gate 数量？
- BDD 是高效共享表示，不意味着 Gate-level 电路在 Area/Delay 上最优。
- Round 1 为什么要为 Round 2 的变量排序、多层展开和多候选映射提供 Baseline？

本报告需要标明 AI 辅助与学生真实实施和理解过程，不应凭空追加贡献记录。

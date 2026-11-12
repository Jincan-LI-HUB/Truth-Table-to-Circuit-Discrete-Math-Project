# Round 2 · 最终 Report 中建议保留的内容

## Methodology（数学）

- **Evolution from Round 1**：固定自然顺序 ROBDD 基线的局限；为何引入变量影响度和多个映射候选。
- **Variable influence**：明确定义两行只在目标变量不同的 Hamming 邻接对；说明按差异数重排不改变 Truth Table。
- **Two-level Shannon**：从 \(f=\neg x f_0\lor xf_1\) 严格代入 \(f_0,f_1\) 的二次 Shannon Expansion；注明 \(u,v\) 可以不同。
- **Gate rewriting**：De Morgan 的符号成本模型与局部 Arrival Time 约束，不声称所有替换都能全局省面积。
- **Implicant Cover**：Essential Support、ON/OFF Sets、Cube 合并、Greedy Cover 和 SOP/POS 功能正确性证明；不承诺贪心最优。
- **Global candidate selection**：完整 Netlist 的 Area/Delay、优先 Target 的候选排序准则、运行预算（仅候选之间检查）。
- **Synthesis invariant**：每一个候选均计算原函数；Portfolio 不修改语义；Hash Sharing 与 Dead-gate Elimination 维护正确性。

## Experiments（运行后填入）

| Field | Evidence file | Recorded value |
|---|---|---|
| Source SHA-256 | `environment.txt`, `SOURCE_PROVENANCE.txt` | 待本地复现 |
| Compiler/CPU/OS | `environment.txt` | 待本地复现 |
| Official PASS and Target Met | `official.csv`, `summary.txt` | 待本地复现 |
| Area total | `summary.txt` | 待本地复现 |
| Median/maximum runtime | `summary.txt` | 待本地复现 |
| Compared to Round 1 | 两轮本地 `official.csv` | 待同机比较 |
| Independent validation | `independent_verification.log` | 待本地复现 |

历史归档结果：25/25 PASS、25/25 Target Met、Area 总和 790,243。另一个历史中间版本为 21/25 Target Met、Area 904,009；不要将中间版本叫作 Round 2 最终版。

## Discussion

- 比较 Round 1 → Round 2 的 **Area 与 Delay**，同时报告 Runtime 增加。
- 哪些 Cases 的 Target Delay 从未达标变为达标？
- Two-level Shannon 带来的收益是结构并行化，而不等同于某条 De Morgan 等价律。
- 为什么不能依赖已知 25 个文件名选算法？
- 算法搜索只在候选之间做时间检查；单个候选依然可能超时。
- Round 3 的 Complemented Edges、Affine、Required-time Slack Recovery 属于后续改进，不能回写到 Round 2 的设计步骤中。

保留每轮成功和失败的实验记录。最终 Source ZIP 与 Report 要确保属于同一个可复现的代码版本，明确披露 AI 参与及真实团队分工。

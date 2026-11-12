# Round 2 内部迭代：不要混淆 21/25 与 25/25

本仓库将 Round 2 的**最终归档版本**定义为 `src/synth.cpp`，对应 25/25 官方 PASS、25/25 Target Delay Met、Area 总和 790,243。用户此前谈论的 21/25 则是 Round 2 研究过程中的一个中间版本。

## 版本链

1. `Round1`: 固定变量顺序的基础 ROBDD，Area 1,103,455，Target 12/25。
2. `Round2-Intermediate`: BDD + 小 Support Cube + 变量顺序 Portfolio（`src/intermediate_portfolio_21target.cpp`）；Area 904,009，Target 21/25。
3. `Round2-Final`: Two-level Shannon Expansion 与五候选全电路级选择，Area 790,243，Target 25/25。
4. `Round3`: 后续补全 complemented edges、Affine、slack-based recovery 等，属于独立轮次，**不应写进 Round 2 已完成的方法**。

Round 2 中间版本的历史官方评测在 `results/intermediate_21target.csv`，保存的是**独立可追溯证据**，不是最终综合器运行时会自动输出的结果。

正式阶段记录需要注明：Round 2 的算法变更不是单一手段，而是 `Variable Influence + Two-level Shannon + Small-support Implicant + Global Portfolio` 的协同作用。不能从最终成绩直接推断其中某个改进的单独收益；单项归因需要禁用/开启对应特性后在同环境重测（Ablation）。

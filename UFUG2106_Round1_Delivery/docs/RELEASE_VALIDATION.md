# Round1 · 发布前自检（模型实验环境，非用户本地结果）

- C++ 源码已使用 `g++ -O2 -std=c++17` 从头重新编译，官方 Evaluator 对 25 个 Stage 1 发布案例测得 **25/25 PASS**、**12/25 Target Met**。
- 本次 Area 总和 **1,103,455**；Median Runtime **6.855 ms**（仅表示本次实验容器，不是用户 WSL 的测量）。
- 与归档历史参考 `results/reference.csv` 对比：所有 25 个 Case 的 `status, area, delay, target_met` 完全一致：**True**。
- 独立 Bit-parallel Checker：Independent entries: 25/25; Exhaustive cases: 13; Sampled cases: 12; Area/delay agreement: 25/25; Problems: none。
- 本 Round 默认编译的是 `src/synth.cpp`，没有将中间原型替换成正式版。
- 本文档不是 Stage 1 教师评分，也不声称 Runtime 在用户电脑上可重复得到相同数值。

**源码 SHA-256:** `3989b677ba6ff7b533de4179c8b3fc1612878bc1b8fc8c1ae10e0627a5cd4b8b`

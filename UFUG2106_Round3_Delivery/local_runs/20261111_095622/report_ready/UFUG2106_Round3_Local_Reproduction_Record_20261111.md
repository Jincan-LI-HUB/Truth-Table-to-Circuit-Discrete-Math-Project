# UFUG2106 — Stage 1 / Round 3 本地复现实验记录

**Record ID:** UFUG2106-R3-LOCAL-20261111-095622  
**Status:** REPRODUCED — 25/25 Official PASS, 25/25 Target Delay Met  
**实验时间:** 2026-11-11 09:56:22 (UTC+08:00)  
**资料来源:** 用户上传 `20261111_095622_Round3_local_results.zip`；同时与已存档的 Round 3 最终源码、25 个 Netlist 比对。  
**性质:** 本地复现实验记录；不是对未发布测试集的性能保证，也不是算法全局最优证明。

## 1. 目的与设置

将 Round 3 最终单进程 C++17 逻辑综合器移至用户的 Windows 11 + WSL2 环境，用同一批 25 个 Stage 1 官方案例及原始 Evaluator 进行干净编译、完整官方评测、独立电路验证、与历史成绩的逐案例对比，并保留源码与产物的可追溯证据。

**本地环境（由 `environment.txt` 记录）：**

- OS：Ubuntu 24.04.4 LTS under WSL2；kernel `Linux 6.6.87.2-microsoft-standard-WSL2`；x86_64。
- CPU：Intel Core Ultra 9 275HX；WSL 向系统报告 24 个逻辑 CPU；综合程序为单线程，不能把 CPU 数目解释为使用了 24 核。
- Compiler：GCC / g++ 13.3.0，C++17，`-O2 -Wall -Wextra`；Python 3.12.3。
- 代码和测试案例位于 WSL 的 `/mnt/e/` 挂载目录；Evaluator 被复制到 `/tmp/ufug2106_evaluator` 后运行。
- 源码 SHA-256：`2f101e9fc320d5feb78d5539d9d9ddbf131b9805c6ffd6265db37f76b89f0135`。
- Evaluator SHA-256：`142361d7ce18bc47dea6a07538db79a588b3afbf446526c1d1246f4968b3d0ca`。
- 用户上传证据 ZIP SHA-256：`70012533c4909cae0ae7601ebe4a5fe37d2e984e7d9293f5a0950a35f6f423fb`。
- 编译与官方测评退出正常；Evaluator exit code = 0；独立验证失败计数 = 0。

## 2. 实验结果及复现判定

| 统计量 | 参考测评 | 本地复现 | 判定 |
|---|---:|---:|---|
| Official PASS | 25/25 | **25/25** | 完全一致 |
| Target Delay Met | 25/25 | **25/25** | 完全一致 |
| Total Area（25 个案例求和） | 533,705 | **533,705** | 完全一致 |
| Median Runtime (ms) | 104.064 | **68.486** | 本地减少 34.19% |
| Maximum Runtime (ms) | 2404.124 | **1497.046** | 本地减少 37.73% |

**强一致性证据：**

1. 本地编译的 `synth_source_snapshot.cpp` 与 Round 3 最终存档 `src/synth.cpp` 的**文件内容完全一致**，哈希匹配。
2. 对 25 个案例，`area`、`delay`、`status`、`target_met` 在本地与参考 CSV **逐行一致**。
3. 本地上传的 25 份输出电路 Netlist 与 Round 3 存档 `verification_outputs_final/` 中相应文件**逐字节一致**。说明电路拓扑与 Gate ID 的写出结果也得到复现，不仅是统计值相等。
4. 官方 Evaluator 报告全部 PASS；独立验证日志中 13 个案例采用穷举输入赋值，12 个较大案例采用确定性抽样，全部 `matched=True`。独立验证的抽样不应描述为对大案例的穷举证明。

**不应推断：** 两次运行环境不同，测到的 Runtime 变化不能直接归因为 CPU 的纯计算速度；Area 和 Delay 相等不意味着获得了全局最优或通过了隐藏案例。

## 3. 全部案例逐行记录

`Slack = Target Delay - Actual Delay`。`Runtime` 为官方 Evaluator 记录的单案例综合程序运行时间；所有时间单位均为 ms。

| Case | n | m | Area | Delay | Target | Slack | Local Runtime | Ref Runtime |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 001 | 15 | 14 | 61,952 | 62 | 77 | 15 | 578.072 | 888.980 |
| 002 | 14 | 14 | 18,918 | 60 | 61 | 1 | 219.538 | 357.466 |
| 003 | 14 | 14 | 24,463 | 55 | 64 | 9 | 228.839 | 359.125 |
| 004 | 13 | 10 | 4,550 | 47 | 57 | 10 | 27.271 | 35.920 |
| 005 | 8 | 5 | 700 | 31 | 36 | 5 | 39.378 | 53.387 |
| 006 | 12 | 12 | 5,962 | 46 | 60 | 14 | 33.268 | 48.066 |
| 007 | 20 | 15 | 78,042 | 71 | 89 | 18 | 1152.072 | 1898.316 |
| 008 | 12 | 12 | 8,637 | 50 | 62 | 12 | 43.810 | 64.104 |
| 009 | 12 | 6 | 14,584 | 46 | 59 | 13 | 68.486 | 104.064 |
| 010 | 19 | 8 | 4,712 | 32 | 61 | 29 | 201.909 | 313.889 |
| 011 | 10 | 5 | 474 | 33 | 40 | 7 | 44.909 | 59.177 |
| 012 | 10 | 10 | 5,359 | 25 | 40 | 15 | 34.761 | 72.569 |
| 013 | 14 | 14 | 12,014 | 60 | 70 | 10 | 112.767 | 160.457 |
| 014 | 20 | 8 | 11,760 | 61 | 72 | 11 | 481.284 | 722.647 |
| 015 | 16 | 16 | 36,345 | 62 | 81 | 19 | 414.866 | 637.419 |
| 016 | 10 | 5 | 2,149 | 40 | 47 | 7 | 22.305 | 24.454 |
| 017 | 13 | 12 | 440 | 22 | 25 | 3 | 11.403 | 11.224 |
| 018 | 12 | 12 | 1,350 | 29 | 32 | 3 | 15.460 | 22.124 |
| 019 | 18 | 8 | 5,319 | 57 | 73 | 16 | 150.659 | 241.181 |
| 020 | 8 | 8 | 776 | 30 | 35 | 5 | 42.604 | 55.601 |
| 021 | 15 | 14 | 28,134 | 60 | 72 | 12 | 427.984 | 642.817 |
| 022 | 8 | 16 | 1,334 | 32 | 34 | 2 | 52.699 | 69.876 |
| 023 | 8 | 4 | 215 | 21 | 24 | 3 | 8.731 | 11.478 |
| 024 | 18 | 8 | 124,830 | 72 | 83 | 11 | 1497.046 | 2404.124 |
| 025 | 15 | 15 | 80,686 | 60 | 76 | 16 | 796.582 | 1338.471 |

### 重点观察

- **最严格的 Delay Slack：** `case_002` 只有 **1** 个时间单位；`case_022` 为 **2**；`case_017`、`case_018`、`case_023` 各为 **3**。全体 Slack 中位数为 **11**。
- **面积集中度：** `case_024`（124,830）、`case_025`（80,686）、`case_007`（78,042）贡献 **283,558 / 533,705 = 53.13%** 的跨案例 Area 总和。可以优先用它们做实验，但该求和并非官方评分公式。
- **运行耗时：** `case_024` 最大（1497.046 ms），随后是 `case_007`（1,152.072 ms）、`case_025`（796.582 ms）。提升最坏情况下的搜索稳定性时应优先分析这些案例。
- **环境差异：** 24/25 个案例在本地测得更短 Runtime；只有 `case_017` 小幅变慢（+0.179 ms），属于毫秒量级变化。
- **精确复现：** 所有 Area/Delay 数值及 Netlist 内容完全相同，表明本次没有发生因超时截断搜索产生不同候选的现象。

## 4. 验证覆盖范围与可信度边界

**直接由本次上传的日志支持：** 官方 25/25 PASS；25/25 Target Met；源代码、输出电路逐字节与前次归档相同；13 个小规模案例被独立穷举、12 个大规模案例被独立抽样；所有独立检验报告 `matched=True`。

**本次并未证明：** 对任何未知 Truth Table 的正确性及性能；所有大规模案例的第二套独立穷举；算法在更严格或不同机器上的 Runtime/Memory 最坏情况；相对最优电路的近似比；课程评分。

这份 ZIP 含有 `case_sha256.txt` 以便后续确认输入案例版本，但本次未重新从课程发布源获取数据并逐项核对，因此输入版本的结论以本地文件清单、官方 Evaluator 和已有归档为证据。

## 5. 下一轮优化研究的建议

**P0 — 冻结 Round 3 复现基线。** 保存本 ZIP、源代码 SHA、Evaluator SHA、该 Markdown 和逐案例 CSV。后续版本所有比较都应以该固定基线的 25 个案例为对照，保持相同编译参数及相同机器环境。

**P1 — Timing-aware Area Recovery 精炼。** 重点研究拥有较大 Timing Slack、Area 又很大的函数，例如 `case_024`、`case_025`、`case_007`，尝试多候选局部替换、跨输出共享与极性选择。对于 `case_002` 的 1 个单位 Slack，任何延迟退化都有较高风险，不能只按 Area 作贪心替换。

**P2 — 搜索预算与可中断性。** 分析 `case_024`、`case_007`、`case_025` 的变量顺序搜索，记录尝试候选数、每次综合时间、是否命中临界预算；应保证单个候选可超时回滚，且始终保留已经完成的合法 Netlist。不能只依赖候选间的时间检查。

**P3 — 完整同机消融和跨方法比较。** 将 complemented edges、affine detection、balanced mapping、timing-slack recovery、reverse ordering、legacy fallback 分别关掉重测，保留单项改进的净效益与相互作用。对比其他公开实现时，要在同一硬件和编译条件下重跑，避免将不同环境的 Runtime 当成严格排名。

**P4 — 泛化与极限情形。** 用独立生成的结构化/随机函数、不同 Gate Cost 组合、多个输出共享、高熵大输入以及更紧 RAM/Runtime 限制做专项实验。记载 PASS、Target Met、Area、Delay、Runtime 和失败类型；避免根据公开 Case ID 硬编码实现。

## 6. 复现命令与档案位置

脚本与源文件所在目录：

```text
/mnt/e/canfiles/Common courses study/大学通识/26-27 Fall/UFUG 2106 Discrete Math/assignment/Final Project/UFUG2106_Round3_Delivery
```

核心命令（在该目录执行）：

```bash
make clean && make
bash run_round3_local.sh /tmp/ufug2106_evaluator "/mnt/e/canfiles/Common courses study/大学通识/26-27 Fall/UFUG 2106 Discrete Math/assignment/Final Project/data/stage1"
```

本次原始材料：`20261111_095622_Round3_local_results.zip`，包含 `official.csv`、`evaluator.log`、`independent_verification.log`、`environment.txt`、`build.log`、`synth_source_snapshot.cpp`、`case_sha256.txt`、`executable_sha256.txt`、`per_case_comparison.csv` 和 25 个 Netlist。

**建议归档状态：** Round 3 local reproduction verified; implementation baseline frozen; Stage 1 technical evidence sufficient for this released dataset; hidden-case and final scoring still pending.

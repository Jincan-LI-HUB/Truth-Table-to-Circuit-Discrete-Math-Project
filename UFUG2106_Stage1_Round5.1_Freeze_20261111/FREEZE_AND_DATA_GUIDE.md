# UFUG2106 Stage 1 — 源码冻结与数据定位操作指南

> 当前指定冻结版本：**Round 5.1 (Stage 1 Research Freeze)**。它是两篇文稿的主要算法实现，不代表已经在 Canvas 提交的版本。最终提交后，另行保存实际提交 ZIP 的 SHA-256。
>
> 来源：用户于 2026-11-11 上传的本地运行证据 `20261111_134547_Round5.1_local_results.zip`。已核对 C++ 主源码 SHA-256 为 `cf90d0b110e6f45d1d508db351c95f10e7d704824fc34e17e6a5f5b783e20759`，Run 1 官方 Evaluator 为 25/25 PASS，25/25 达 Target Delay，Area 总和 529014。该源码也已从冻结包独立编译成功。

## 0. 先解释四个路径

在 **WSL Ubuntu** 的 Terminal 执行（**不是** Windows PowerShell）：

```bash
BASE="/mnt/e/canfiles/Common courses study/大学通识/26-27 Fall/UFUG 2106 Discrete Math/assignment/Final Project"
RUN="$BASE/UFUG2106_Round5.1_Delivery/local_runs/20261111_134547_Round5.1"
CASES="$BASE/data/stage1"
EVAL="$BASE/evaluator"
```

- `BASE`：项目总目录。
- `RUN`：本人 WSL 第一次成功复现 Round 5.1 的**实际运行记录**。
- `CASES`：老师公布的 Stage 1 的 25 个输入文件。
- `EVAL`：老师的 Linux x86 Evaluator。

检查目录存在性：

```bash
ls -ld "$BASE" "$RUN" "$CASES"
ls -l "$EVAL" "$RUN/source_snapshot/src/synth_round51.cpp"
```

如果报 `No such file or directory`，先在 WSL 运行：

```bash
find "$BASE" -type f -name synth_round51.cpp
find "$BASE" -type f -name run1_round51.csv
```

如果实际 Round 5.1 的 `local_runs` 路径有所不同，按照搜索结果在自动脚本中调整 `RUN` 那一行；**不要修改旧源码或旧实验数据**。

## 1. 最简单：校验你本地的源码与论文主版本相同

```bash
sha256sum "$RUN/source_snapshot/src/synth_round51.cpp"
```

应显示：

```text
cf90d0b110e6f45d1d508db351c95f10e7d704824fc34e17e6a5f5b783e20759
```

检查官方结果原始数据：

```bash
head -n 5 "$RUN/benchmark/run1_round51.csv"
cat "$RUN/summary.json" | head -n 60
```

此主文件与其依赖的 `.hpp`、Makefile、Python 复现程序必须**作为一个源码快照一起保存**，不能只拿走单独 `synth_round51.cpp`。

## 2. 一键冻结与收集证据（推荐）

从聊天中下载 `verify_and_collect_stage1_round51.sh`，将文件放到 Windows 的 `Final Project` 目录（与 `evaluator`、`data` 同级）。然后回到 WSL，运行：

```bash
BASE="/mnt/e/canfiles/Common courses study/大学通识/26-27 Fall/UFUG 2106 Discrete Math/assignment/Final Project"
bash "$BASE/verify_and_collect_stage1_round51.sh" "$BASE"
```

脚本会：核对精确源码 SHA-256；复制冻结源码、两轮官方 CSV、Netlist、独立验证日志、Holdout CSV、环境和原始数据指纹；写出案例输入头部预览和可能存在的 Ablation 文件路径；用 Python 标准库生成 ZIP。**不会更改旧轮次，不需要 `sudo` 或系统 `zip`。**

成功后，你的项目根目录将新增：

```text
Stage1_Freeze_Round5.1_Verified/
├── source_snapshot/
│   ├── src/
│   └── Makefile
├── evidence/
│   ├── benchmark/
│   ├── official_outputs_run1/
│   ├── holdout/
│   ├── report_ready/
│   └── provenance/
└── README.md
Stage1_Freeze_Round5.1_Verified.zip
```

**如果你只打算核对本地一致性，就不必再上传这个 ZIP**；聊天中原有的本地测试结果已足够。只有校验失败、补充了新实验或需再次交叉比对时再上传。

## 3. 可选的额外数据分别在哪里？

### A. 25 个案例的原始目标延迟和资源限制

位置：

```text
Final Project/data/stage1/case_001.txt ... case_025.txt
```

Evaluator 的 CSV `run1_round51.csv` 记录了实测 `delay` 和 `target_met`，但**没有直接给出完整的数值 target-delay 序列**。因此，如果想画 “measured delay vs target delay” 每案例折线图，应回到输入文件。

先确认一个文件的头部格式（不要猜测字段行号）：

```bash
sed -n '1,12p' "$CASES/case_001.txt"
```

再看自动脚本汇总的 25 个文件开头：

```text
Stage1_Freeze_Round5.1_Verified/evidence/provenance/case_header_preview_LOCAL_ONLY.txt
```

如图表确实需要 target-delay、RAM limit 等数字，可把这个**短头部预览**给我，不必上传 25 个完整 Truth Table。脚本不会自动把不确定格式的某一行误标成 target delay。

### B. Round 3 / Round 4 的功能消融结果

可优先查找：

```text
Final Project/UFUG2106_Round3_Delivery/
Final Project/UFUG2106_Round4_Delivery/
Final Project/UFUG2106_Round4.1_Delivery/
```

手动搜索：

```bash
find "$BASE" -type f \( -iname '*ablation*.csv' -o -iname '*profil*.csv' -o -iname '*ablation*.json' \)
```

自动脚本也会生成 `optional_ablation_files_found.txt`。**如果找不到，不需要杜撰每个子模块独立减少多少 Area**；我们已有完整版本间对照，可在报告中明确只归因到联合改动。

### C. 更多重复运行（用于误差棒 / 箱线图）

现有 Round 5.1、6.1 的同机配对测评已经足以写描述性结果。如果要做具有较稳健不确定性区间的 Runtime 图，需额外进行相同硬件、相同命令、**交替顺序**的 5–10 次测试，保留每轮 CSV 和环境信息。

**当前不是必要补充项。** 两篇 v0.1 可以保持原配对图，不绘制没有依据的置信区间。

### D. 峰值内存与 RAM Limit

测试输入中的限制可从 `data/stage1` 文件头部确定。实际峰值 RSS **不在普通 Evaluator CSV 中**，需要重新测量，不能从 Area 或 Runtime 推算。若后续确实要研究，可在 WSL 用：

```bash
cd "$RUN/source_snapshot"
make build/synth_round51
/usr/bin/time -v ./build/synth_round51 "$CASES/case_024.txt" /tmp/r51_case_024.netlist 2> /tmp/r51_case_024_time.log
```

然后查看 `/tmp/r51_case_024_time.log` 的 `Maximum resident set size`。需要先确认本机有 `/usr/bin/time`，没有也不影响写作。

**当前不需要额外做内存实验**，论文可诚实地把它列为尚未系统衡量的限制。

## 4. 对最终论文和 GitHub 的特别说明

- **Technical Report**：以 Round 5.1 为论文主实现，Round 4.1 Strict 和 Round 6.1 等作为研究比较。不要将 `Round 5.1 Research Freeze` 写成“已经提交”。
- **Trial Log**：保留全部版本决策与证据，不将非配对历史 Runtime 混为一组严格控制实验。
- **学术诚信**：团队的具体个人贡献应经两位成员确认；AI 的实际使用范围、课程原文政策及成员验证行为应分开陈述。不能虚构人工作业完成过程或隐瞒实质性 AI 协助。
- **GitHub 公开版**：避免公开学号、未经允许的老师原始测试文件与 evaluator、以及带完整 Windows 用户路径的日志；可公开自己的算法代码、脱敏的统计数据和论文（以课程许可为前提）。
- **Stage 2**：教授公布前不写入任何 Stage 2 实测结论。

## 5. 在 Canvas 最终提交后需要额外冻结什么？

如果最后仍提交 Round 5.1，从真正提交的**源代码 ZIP**再生成：

```bash
sha256sum /path/to/the/actually-submitted-source.zip
```

保留 ZIP、SHA-256、提交日期、程序调用方式。这是一份和论文 Research Freeze 分开的 *Submission Provenance*，因为还没有实际提交之前不能把两者等同。

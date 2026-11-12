# UFUG2106 · Round 2 数学原理、算法协同与迭代记录

> **版本定义**：本文件对应此前 `UFUG2106_Improved_Synthesis_20261111.zip` 中的最终 `synth_portfolio_clean.cpp`。为形成统一的测试接口，其字节内容原样存档为 `src/synth.cpp`。Round 2 的**正式归档版**在历史官方 Evaluator 中为 25/25 PASS、25/25 Target Delay Met、Area 总和 790,243；较早 21/25 的中间版本单独保存在 `src/intermediate_portfolio_21target.cpp` 与 `results/intermediate_21target.csv`。
>
> 这个版本**尚未**实现 Round 3 才有的 complemented-edge BDD、Affine Detection、全图 Required-time Area Recovery、Legacy Fallback；不能将 Round 3 的思想写成 Round 2 已实施的方法。

## 1. 设计目标：从“正确”转变为“多个有效候选中选择”

Round 1 给出了正确性保证，但固定顺序和普通 Shannon MUX 会产生冗余且可能很深的电路。Round 2 不再仅构造唯一结果，而是对每张 Truth Table 建立有限候选集合

\[
\mathcal K(F)=\{C_1,C_2,\ldots,C_K\}\subseteq\mathcal C(F),
\]

其中 \(\mathcal C(F)\) 表示满足 \(C(x)=F(x)\) 的合法电路集合。**每个候选由数学上完全等价的变换构造**；Evaluator 的测试是工程验证，不是依赖已知 Case 的答案查表。

Round 2 的核心组合顺序是：

1. 从输入 Truth Table 构造不同变量排序下的 BDD；
2. 在映射每个 BDD Node 时，尝试普通 Shannon、De Morgan 替换及两层 Shannon 展开；
3. 对 Essential Support 小的输出函数额外尝试 Implicant Cover（SOP / POS）；
4. 对每一候选做 Reachability Pruning，形成完整 Netlist；
5. 用当前案例指定的 Gate Costs 计算完整 \(A(C),D(C)\)，选择候选输出。

这些阶段各有不同的数学作用：**BDD 是函数分解和共享；门级重写是局部结构选择；Implicant Cover 是不同的函数表示；Portfolio 是全电路选择。**

## 2. Variable Influence 与顺序选择

固定其余变量赋值后改变 \(x_i\) 所造成的输出差异，可定义影响度：

\[
I_i(F)=\sum_{j=0}^{m-1}\sum_{z\in\{0,1\}^{n-1}}
\mathbf 1\!\left[f_j(0,z)\ne f_j(1,z)\right].
\]

这里的 \(0,z\) 和 \(1,z\) 指 **仅 \(x_i\) 不同、其余输入完全一致** 的两个赋值；并不是简单把第 0 位设为 0。代码对每个变量枚举所有配对输入行，按输出位计数差异，并将变量以影响度降序排序。

该统计会改变 BDD 决策顺序，但不改变原函数的真值表。源码通过索引映射 `orig[i]` 确保重新排序后的每个叶节点仍读取正确的**原始输入行**。

**局限：** Influence 较高不必然意味着放在 BDD 顶层就面积最小。这是搜索启发式，不是最优性定理。

## 3. BDD 与共享子函数保持 Round 1 的正确性基础

每个节点仍表示 Shannon Identity

\[
f=\neg x\, f_0 \lor x\,f_1.
\]

Unique Table 去重相同 \((x,f_0,f_1)\)；Gate Hash 去重相同 `(op, fanin1, fanin2)`。此外，常量简化、双重取反、死门删除和拓扑编号继续用于减少实际输出的门数。

多输出共享导致“局部省门”与“全局省 Area”并不等价。例如某个 AND Gate 被 \(y_0\) 与 \(y_1\) 共同使用，删除它的一个局部引用不一定降低最终面积。**因此总 Area 必须在最终保留的整张 Netlist 上计算。**

## 4. 两层 Shannon Expansion：缩短串行决策链

单层分解：

\[
f=\neg x\,f_0\lor x\,f_1.
\]

如果两个子 Cofactors 继续按各自 BDD 顶层变量分解：

\[
f_0=\neg u\, f_{00}\lor u\,f_{01},\qquad
f_1=\neg v\, f_{10}\lor v\,f_{11},
\]

那么严格代入可得：

\[
\boxed{
\begin{aligned}
f={}&\neg x\land\neg u\land f_{00}
\;\lor\;\neg x\land u\land f_{01}\\
&\lor x\land\neg v\land f_{10}
\;\lor\;x\land v\land f_{11}.
\end{aligned}}
\]

\(u\) 与 \(v\) **可以不同**，因为不同 Cofactors 的 BDD 可能跳过不同的变量。若某分支为常量，则可以直接化简该项；公式始终是 Boolean 恒等式。

这种结构把原先串行的两个 MUX Level 化为多个并行 Product Terms 再合并，可能降低 Critical Path，却也可能创建更多 Gate。**不能声称两层展开必然降低 Area 或 Delay。**

### 4.1 Arrival-time-aware Tree Building

用两个信号 \(a,b\) 构造 AND2/OR2 时，设其到达时间为 \(T_a,T_b\)，新输出时间：

\[
T_{\mathrm{new}}=\max(T_a,T_b)+d_{\mathrm{gate}}.
\]

代码用 Priority Queue 反复选取较早到达的两个项进行组合，形成相对平衡的合并树。这是一种合理的 Arrival-time Heuristic，但有共享或不同成本时**不是全局最优性的证明**。

两层展开在代码中的接受条件是“新候选的局部 Arrival Time 加指定 Margin，严格小于原候选 Arrival Time”；不同的 Portfolio 变体使用不同 Margin。它不是盲目永远展开。

## 5. De Morgan：根据动态成本选择等价门级结构

\[
a\lor b=\neg(\neg a\land\neg b),
\quad
a\land b=\neg(\neg a\lor\neg b).
\]

对一条单独、全新建造的 OR2 门，右侧 De Morgan 形式所需的 Area 上界为

\[
a_{\mathrm{AND2}}+3a_{\mathrm{NOT}}.
\]

但是在共享电路中可能已有输入取反信号，实际增量 Area 不必等于这个上界。因此代码使用成本条件与 Arrival Time 判据决定是否尝试替换，再由完整候选的最终 Netlist 计算 Area / Delay。

这种局部替换的作用是控制“昂贵 Gate 类型”及部分逻辑层数，但局部收益不保证全局收益，原因是共享结构和其他输出的 Arrival Time 可能随之改变。

## 6. Essential Support、Cube、Implicant 与 SOP/POS

### 6.1 Essential Support

变量 \(x_i\) 对输出 \(f_j\) 是 Essential，当且仅当存在某个固定其余变量的赋值使

\[
f_j\vert_{x_i=0}\neq f_j\vert_{x_i=1}.
\]

集合 \(\operatorname{supp}(f_j)\) 包含所有这样的变量。Round 2 为 \(n\le13\) 的案例检查输出的 Support；若 \(|\operatorname{supp}(f_j)|\le9\)，允许执行附加的 Implicant 枚举。其他输出仍使用 BDD 途径，保证完整通用性。

### 6.2 从 Minterm 到 Cube

将输出为 1 的每个完整赋值转成一个 Minterm，然后合并仅有一位互补的 Product Terms，消去变化的文字。例如

\[
\neg a\land b\land c\quad\lor\quad a\land b\land c
= b\land c.
\]

在 Cube 表示中，一个固定文字集合对应一个满足若干变量取值要求的子立方体。只有当整个 Cube 不覆盖 OFF-set，才能用于覆盖输出为 1 的 ON-set。

代码生成候选 Prime Implicants，使用 Greedy Cover 逐次选择能覆盖最多剩余 ON-set、按文字数量作权衡的 Cube。只要覆盖所有 ON-set 而不覆盖 OFF-set，得到的 SOP 表达式就**严格等价**，无论贪心是否得到最少文字数或最小 Gate Area。

对于 OFF-set（输出为 0 的行）做相同操作得到 \(g=\neg f\) 的 SOP，再对其取反得到 \(f\) 的另一种实现，相当于构造 POS 候选。

### 6.3 严格正确性论证

令选出的 Cubes 为 \(Q_1,\dots,Q_r\)，满足

\[
\bigcup_{k=1}^r Q_k = f^{-1}(1),\qquad
Q_k\subseteq f^{-1}(1).
\]

对任意赋值 \(x\)，若 \(f(x)=1\)，至少落在某个 \(Q_k\) 中，合并电路输出 1；若 \(f(x)=0\)，因为所有 \(Q_k\) 都属于 ON-set，所以没有 Cube 输出 1，合并电路输出 0。因此 \(\bigvee_k Q_k\equiv f\)。

Greedy Cover 只影响效率，不影响正确性；也不承诺得到全局最小表达式。

## 7. 五种完整候选（对应本版源码）

| 变体 | BDD 顺序 | Mapping 选择 | Two-level | Implicant |
|---|---|---|---|---|
| 1 | Influence-desc | Delay-first | 开启 | 小 Support 输出尝试 |
| 2 | Influence-desc | Area-focused rewriting | 开启 | 小 Support 输出尝试 |
| 3 | Influence-desc | Delay-first | 开启 | 关闭 |
| 4 | Natural | Delay-first | 开启 | 小 Support 输出尝试 |
| 5 | Influence-desc | Delay-first | 更保守的展开 Margin=4 | 小 Support 输出尝试 |

这些候选在同一个 C++17 进程中**顺序运行**，每次都生成完整合法的候选 Netlist，不通过读取测试文件名进行分支。

源码对候选的排序准则可用如下词典序写出（仅是我们自定义的工程启发式）：

\[
\operatorname{rank}(C)=\Big(
\max\{0,D(C)-D_{\mathrm{target}}\},\;
\mathbf 1_{D(C)\le D_{\mathrm{target}}}A(C),\;
D(C),\;A(C)\Big).
\]

**为什么不能称为官方评分公式？** 因为老师的 Evaluator CSV 未提供可用于重建最终成绩的完整公式；而且 Area 的跨案例简单相加并不是官方分数。

**时间预算**：读取案例中可选 Runtime Limit；在第一个候选之后、启动下一个候选之前检查耗时是否已超过 \(0.75T_{\mathrm{limit}}\)。这只能限制**候选之间**的搜索，不能强制中断一个耗时过长的候选；对于极端限制，仍存在潜在超时风险。

## 8. “协同使用”的严谨正确性证明

1. 对任意输入函数 \(F\)，每个变量排列仅改变 Shannon Cofactor 的选择顺序；只要叶节点仍正确映射到原始行，BDD 表示始终计算同一函数。
2. De Morgan 与两层 Shannon 展开是恒等式，任意局部替换不改变被映射节点的函数值。
3. 选定 Cubes 时，所有项完全在 ON-set 中，并且覆盖所有 ON-set；补函数版本同理，因此产生的替代表达式准确等价。
4. Structural Hashing 复用同一组门计算；删除不可达门和重编号不会改变任何输出。
5. 最后 Portfolio 只在已经完整构造的候选之间选一个，不改变其语义。因此输出 \(C\) 满足 \(C(x)=F(x)\) 对所有赋值成立。

这是**条件于程序正常完成、输入合法、Netlist 合法**的数学正确性结论。多候选搜索预算、内存和运行时间上界并非由这个归纳证明保证。

## 9. 真实迭代路径和实验结果

| 测试版本 | PASS | 达到 Target Delay | Area 总和 | Median Runtime |
|---|---:|---:|---:|---:|
| Round 1 纯 ROBDD | 25/25 | 12/25 | 1,103,455 | 历史 7.263 ms |
| Round 2 早期 Portfolio | 25/25 | 21/25 | 904,009 | 历史 26.36 ms |
| 加入两层 Shannon 的单候选版本 | 25/25 | 25/25 | 825,125 | 历史 26.40 ms |
| 五候选混合综合器（本归档版） | 25/25 | **25/25** | **790,243** | 历史 55.46 ms |

说明：上表是早期项目记录中保留的官方 Evaluator 实验结果，不是本地用户新测试的结果。Round 2 早期 Portfolio 的源代码单独归档，用户若希望复现这段迭代也可以额外编译并运行，但它不属于当前 Round 2 正式复现脚本的构建目标。

Round 2 相比 Round 1 的主要科学贡献是**突破固定 BDD 逐层 MUX 的结构约束**，引入两层并行展开以及小 Support 的两级逻辑表示，并将多种构造提升为完整电路级别选择。

## 10. Round 2 尚未解决的问题（引出 Round 3）

- 仍没有在 BDD 本身系统共享互补函数的 **Complemented Edges**；
- 对 XOR-rich / Affine 子函数缺少专门的代数结构检测；
- De Morgan 条件主要基于局部 Arrival Time，而非对整个电路向后传播的 **Required Time**；
- 没有用 Timing Slack 恢复大量 Area；
- 搜索预算检查不能中断单个候选；对高熵大规模函数的最坏时间和内存仍需压力测试。

这些不足引出了 Round 3 的 Complemented-edge BDD、Affine Recognition、Balancing、Required-time Area Recovery、受预算约束的变量顺序搜索与 Legacy Fallback。

### 最终 Report 中的披露要求

明确分开**由 AI 完成的实现或实验**和**学生自己完成的理解、验证、决策、协作**；报告中不能凭测评数据推测团队成员做过的工作。将 Stage 1 发布测试、额外生成测试、未发布隐藏测试区分；完整记录每一轮失败结果和局限，避免以“25/25 目标达成”冒充最优性证明。

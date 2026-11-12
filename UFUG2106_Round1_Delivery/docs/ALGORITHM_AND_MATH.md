# UFUG2106 · Round 1 数学原理与算法设计记录

> **版本定义**：原始固定变量顺序 ROBDD Baseline；源码 `src/synth.cpp` 的 SHA-256 见根目录 `SOURCE_PROVENANCE.txt`。本章只描述这份源码实际实现的内容，不把后来才加入的 two-level Shannon、Affine、Implicant 和 Timing Recovery 追溯到 Round 1。
>
> **实验出处**：`results/reference.csv` 为此前运行老师官方 Evaluator 得到的历史记录，不代表用户 Windows/WSL 本地测量。用户自己的记录应取 `local_runs/.../official.csv`。

## 1. 从输入文件到数学对象

设输入有 \(n\) 位，输出有 \(m\) 位，真值表定义映射

\[
F:\{0,1\}^{n}\to\{0,1\}^{m},\qquad
F(x)=(f_0(x),\ldots,f_{m-1}(x)).
\]

第 \(i\) 行对应 \(i\) 的 \(n\) 位二进制表示；\(x_0\) 对应最高有效位（MSB）。以 \(n=3\) 为例，第 5 行（从第 0 行编号）对应 \((x_0,x_1,x_2)=(1,0,1)\)。每一行紧接着是一个长度为 \(m\) 的输出位串。

**本项目不是逆向恢复“原始电路”。** 多个不同的电路可以实现同一个 \(F\)，目标是构造任意正确的允许门级 Netlist，并在后续优化成本。

允许的 Gate 只有 AND2、OR2 和 NOT；输出 Netlist 的信号 0 是常量 0，信号 1 至 \(n\) 分别代表原始输入。每个新 Gate 只可引用更小的信号编号；最后一行给出 \(m\) 个输出 Signal IDs。

## 2. 为什么任何函数都能构造：Shannon Expansion

选取变量 \(x_i\)，定义两个 Cofactors：

\[
f_0=f\vert_{x_i=0},\qquad f_1=f\vert_{x_i=1}.
\]

则恒等式

\[
\boxed{f=\overline{x_i}f_0\lor x_i f_1}
\]

对所有布尔赋值成立。证明直接按 \(x_i=0\) 和 \(x_i=1\) 分情形：前者化为 \(f_0\)，后者化为 \(f_1\)。两种情况穷尽变量取值，故恒等成立。它是**精确恒等式**，不是一个近似模型。

递归地对余下变量使用该恒等式，最终会到达常量函数 0 或 1。因此无需提前知道原电路，也能从任意完整真值表构造正确表达式。

### 2.1 一个 XOR 例子

令 \(f(x_0,x_1)=x_0\oplus x_1\)。按 \(x_0\) 分解：

\[
f_0(x_1)=x_1,\qquad f_1(x_1)=\neg x_1.
\]

于是

\[
f=(\neg x_0\land x_1)\lor(x_0\land\neg x_1).
\]

尽管题目不允许原生 XOR Gate，这个式子仍只需 AND2、OR2、NOT 即可实现。

## 3. 从递归表达式到 Reduced Ordered BDD

普通 Shannon 递归可能重复构造相同子函数。Round 1 使用**固定变量顺序**

\[
x_0\prec x_1\prec\cdots\prec x_{n-1}
\]

构造 Reduced Ordered Binary Decision Diagram（ROBDD）。每个非终端节点表示

\[
\operatorname{ITE}(x_i,\mathrm{hi},\mathrm{lo})
=\neg x_i\land\mathrm{lo}\;\lor\;x_i\land\mathrm{hi}.
\]

其中 ITE 是 if-then-else；`lo` 为 \(x_i=0\) 的子函数，`hi` 为 \(x_i=1\) 的子函数。源码用常量终端节点 0 和 1。

### 3.1 两条关键 Reduction Rules

**Rule A — 删除冗余变量测试。** 若 \(\mathrm{lo}=\mathrm{hi}\)，则

\[
\operatorname{ITE}(x_i,\mathrm{lo},\mathrm{lo})=\mathrm{lo}.
\]

这表示当前函数实际不依赖此位置的变量。

**Rule B — 合并完全相同的三元组。** 对 \((i,\mathrm{lo},\mathrm{hi})\) 建立 Unique Table。第二次出现同一三元组时，返回已有 BDD Node ID，而不是再创建一个新节点。

正确性来自两个事实：Rule A 是 Boolean 恒等式；Rule B 只是让等价的**相同结构**复用同一个节点，没有修改任何子函数值。对固定顺序与这些约简规则，在完整处理下，ROBDD 还具有规范性；规范性依赖于固定变量顺序，而不是声称所有顺序的 BDD 一样大。

### 3.2 代码中为何可以 Bottom-up 构造

源码先读取每个输出的 \(2^n\) 位函数值，再从最末变量向第一个变量两两合并：每次把当前真值序列中相邻的两项当作 `lo` 与 `hi`。在固定 MSB-first 行序下，相邻两项正好只在最后一位（当前被消去变量）上不同。下一层对更高一位变量作同样处理。

**归纳不变式：** 在第 \(i\) 层时，每个 `cur[k]` 表示对应固定前缀下的余变量 Cofactor。合并步骤由 Shannon 恒等式维护此语义，直到 `cur[0]` 成为整个输出函数的 BDD Root。

多个输出共用同一张 Unique Table，因此不同输出中出现相同 Cofactors 时，可以共享 BDD Node。

## 4. BDD → Gate Netlist：两层不同的共享

BDD Unique Table 共享的是**布尔子函数**；Gate Structural Hashing 共享的是具体的**门及其输入信号**。两层 Hash Table 不能相互替代。

对每个 BDD Node，Round 1 映射为允许门级结构：

\[
s_i=\neg x_i\land\mathrm{lo}\lor x_i\land\mathrm{hi}.
\]

代码还直接处理常量 Cofactors：

| 条件 | 精确等价形式 |
|---|---|
| \(\mathrm{lo}=0\) | \(x_i\land\mathrm{hi}\) |
| \(\mathrm{hi}=0\) | \(\neg x_i\land\mathrm{lo}\) |
| \(\mathrm{lo}=1\) | \(\neg x_i\lor\mathrm{hi}\) |
| \(\mathrm{hi}=1\) | \(x_i\lor\mathrm{lo}\) |

对 AND/OR 输入 ID 进行规范排序后，以 `(Gate type, input ID 1, input ID 2)` 为键查找。若完全一致，就复用已有 Gate ID。NOT 的双重否定、\(a\land 0=0\)、\(a\lor 1=1\) 等简化也用于控制冗余门。

为表示常量 1，程序可构造 `NOT 0`。常量、直接输入变量都可作为最终输出；不必强行生成门。

源码构造过程中可能暂时创建后来未使用的门。最后通过输出节点反向标记所有可达门（Reachability / Dead-gate Elimination），只输出这些门，并将 Signal IDs 按拓扑顺序重新连续编号。这个过程不会改变输出函数。

## 5. 面积、延迟与性能指标

设最终实际输出的门集合为 \(G\)，每类门 \(t\) 的成本由**当前测试案例**指定：

\[
\boxed{A(C)=\sum_{g\in G}a_{\operatorname{type}(g)}}.
\]

同一门驱动多个输出只计一次。NOT 与 OR 的成本并非普适固定值。

定义信号到达时间（Arrival Time）：输入和常量 0 的到达时间为 0；NOT 门为其输入到达时间加 NOT 延迟；二输入门为输入的最大到达时间加对应门延迟：

\[
T(v)=\max_{u\in\operatorname{fanin}(v)}T(u)+d(v).
\]

最终电路延迟：

\[
\boxed{D(C)=\max_{0\le j<m}T(y_j)}.
\]

因为每个 Gate 的输入 ID 都比自己小，按 Netlist 顺序计算 \(T\) 就能得到 Critical Path；无需枚举全部路径。**Circuit Delay 与程序 Runtime 是两种不同的量。**

## 6. 严谨的正确性证明结构

1. **输入语义：** 第 \(i\) 行按 MSB-first 转换为赋值，真值表数组的每个条目与定义的 \(f_j\) 一致。
2. **BDD 构造：** 以变量数量作归纳。终端表示常量 Cofactor；内部节点根据 Shannon 恒等式组合两个正确的 Cofactors。删除等值分支及复用相同三元组均不改变函数。
3. **Gate Mapping：** 将每个节点的 Shannon 表达式替换为 AND2、OR2、NOT；所有常量化简是等式恒等变换，结构哈希仅共享相同计算。
4. **Netlist 输出：** 删除不可达门、重新编号不改变每个输出的组合逻辑函数。由 DAG 拓扑编号保证可被 Evaluator 顺序模拟。

所以若程序完成构造、写出合法 Netlist，则对每个 \(x\in\{0,1\}^n\) 都有 \(C(x)=F(x)\)。这一数学结论不等于保证在任意严格时间或内存限制下总能完成计算。

## 7. 复杂度、实验与本轮局限

输入数据本身包含 \(m2^n\) 个输出位，读取至少需要 \(\Omega(m2^n)\) 时间。此固定顺序的底向上 BDD 构造中，各输出涉及的各层配对总数是 \(\sum_{k=1}^n 2^{n-k}=2^n-1\)，因此在 Hash Table 期望常数操作模型下，构造和空间开销的主项为 \(O(m2^n)\)（另有 Hash Table、Netlist 等内存开销）。BDDs 最坏情况仍可能指数级增长。

**已保留历史实验记录：** 25/25 PASS、12/25 满足 Target Delay、Area 总和 1,103,455。13 个未达到 Target Delay 的案例不等于无解；正是后续 Round 2/3 需要改进的对象。

Round 1 **没有**自适应变量顺序，也没有全局面积优化、two-level Shannon、Implicant Cover、Affine Detection、Complemented-edge BDD 或 Slack-aware Recovery。这些内容可以在最终 Report 的 **Limitations and Motivation for Round 2** 小节中说明。

### 需要在最终 Report 中留存的证据

`src/synth.cpp` 源代码与 Hash、`official.csv`（本地生成）、`per_case_comparison.csv`、`build.log`、`evaluator.log`、`independent_verification.log`、机器环境、25 份 Netlist、Runtime Limit 是否满足、不能达标的 13 个 Case 列表。不得将老师的通过/失败判定与我们自己的 `Target Met` 统计混为一谈。

# Truth Table to Circuit — Complete Research Trial Log (Stage 1 + Stage 2)

**Role:** complete archival research record for the UFUG2106 project. It preserves individual design decisions, mathematical arguments, code-grounded implementation narratives, paired and archival experiments, negative results, and their implications. The separate **Formal Report** selects and synthesizes the parts needed to explain the final R10.0 solution. The fully typeset LaTeX and PDF are authoritative for the finished document.

**Evidence policy:** Stage 1 findings come from the finalized R1–R6.1 source; Stage 2 findings from the verified R7–R10.1 source and linked CSVs. Cross-round time series are descriptive, while interleaved matched experiments and controlled candidate comparisons support narrower attributions. A valid Boolean circuit need not meet the delay target, and neither necessarily establishes any unreported numerical course grade.

---

# Part I — Stage 1: Independent Research from R1 to R6.1

# How to read this record

This log is intentionally more explanatory than a conventional technical paper. A reader need not know BDDs, implicants, or logic synthesis in advance. We begin with complete truth tables and the three allowed gates, then explain how each design limitation motivates the next technique. Whenever a mathematical identity is used, we distinguish that *the Boolean function is preserved* from the separate empirical claim that *the resulting circuit is cheaper or faster to synthesize*.

The research was not one straight sequence of uniformly better algorithms. Some changes reduced area at considerable runtime cost; a few optimization proposals were not retained. Consequently, the final architectural choice is not simply “the version with the smallest aggregate area.” Round 5.1 is retained as the principal efficiency candidate, while Round 4.1 Strict and Rounds 6.0/6.1 provide informative alternative points on the engineering tradeoff.

## Two reading routes

Readers who are new to logic synthesis should begin with the synthesis problem and the recurring three-input, two-output example, then follow Rounds 1–3 to see why representation and timing analysis are needed. Readers primarily interested in the engineering decisions can begin with the research map, examine the paired runtime and cut-rewriting results in Rounds 4.1–6.1, and finish with the evidence and reflection sections. Both routes rely on the same definitions and archived measurements; the shorter Technical Report presents the selected method rather than every development turn.

## What the metrics do and do not mean

For a legal netlist $G$ with gate-type areas $a_t$ and delays $d_t$, the output-file area is $$\label{eq:logarea}
 A(G)=\sum_{t\in\{\mathrm{AND2},\mathrm{OR2},\mathrm{NOT}\}}N_t(G)a_t.$$ Every emitted gate is charged exactly once, even if its output fans out to several consumers. The network delay, in contrast, is a *critical-path* quantity: $$\label{eq:logdelay}
 T(v)=\max_{u\in\mathrm{fanin}(v)}T(u)+d_{\operatorname{op}(v)},\quad D(G)=\max_{y\in\mathrm{outputs}}T(y),$$ with source arrival zero (for NOT, the maximum has one argument). Finally, the synthesizer runtime $T_{\rm synth}$ is the wall-clock time of the *program constructing $G$*, not the propagation delay $D(G)$. These are dimensionally and conceptually different. The official evaluator additionally distinguishes the Boolean/format/limit status `PASS` from `target_met`. The provided project instructions and evaluator interface  do not reveal a numerical grading formula, so our totals across cases are engineering diagnostics rather than an official grade.

## A short notation guide

The same symbols recur at different stages of the project. The distinction between the Boolean function and its implementation matters throughout:

<div id="tab:notation">

| **Symbol**      | **Meaning**                                                                            |
|:----------------|:---------------------------------------------------------------------------------------|
| $F$ or $f$      | Desired Boolean output vector or a single Boolean function from the input truth table. |
| $G$             | Concrete, directed acyclic gate network realizing $F$.                                 |
| $A(G)$          | Charged area of all live gates in $G$ (shared gates count once).                       |
| $D(G)$          | Maximum output arrival time; a property of the circuit.                                |
| $T_{\rm synth}$ | Wall-clock runtime of the synthesis *program*, not the circuit delay.                  |
| $T(v),R(v)$     | Arrival time and required arrival time of a node in a fixed network.                   |
| $\rho(G)$       | The program’s internal lexicographic candidate ranking, not an official score.         |

Notation used throughout the trial record. These are definitions, not performance claims.

</div>

## The frozen solver’s ranking is not the evaluator’s score

The Round 5.1 code uses a lexicographic tuple $$\rho(G)=\big(\max(0,D-D_{\rm target}),\ \mathbf1_{D\le D_{\rm target}}A,\ D,\ A\big).$$ A feasible candidate is ranked by area and then delay; an infeasible candidate is first ranked by how badly it misses the target. This tuple is an *internal engineering heuristic*. The evaluator’s public CLI exposes limits and performance metrics, but not a numerical grade formula. A clock-dependent search also means improving runtime can change which candidates finish before the cutoff; identical fixed-candidate semantics do not logically force identical final output bytes.

## The narrative contract

Each iteration answers six questions: (1) What observable problem remained? (2) Which mathematical property suggested an answer? (3) What was implemented, rather than merely proposed? (4) What independent check supports correctness? (5) What happened to area, delay and runtime under measured conditions? (6) How did this evidence change the next decision? Formal results are statements about functions or algorithms under assumptions; benchmark claims are observations of frozen implementations.

## The research map: decisions, not just versions

A conventional changelog would list features in implementation order. A research notebook should reveal why an observation made the next experiment reasonable. Table <a href="#tab:decisionmap" data-reference-type="ref" data-reference="tab:decisionmap">2</a> summarizes that logic; each transition will later be examined with its precise mathematical condition and supporting evidence.

<div id="tab:decisionmap">

| **Move**          | **Observation to explain**                                               | **Next hypothesis**                                                   |
|:------------------|:-------------------------------------------------------------------------|:----------------------------------------------------------------------|
| R1 $\to$ R2       | Correct netlists can still miss delay targets.                           | Change decision orders and mapping forms, not the truth function.     |
| R2 $\to$ R3       | Better representations still leave costly shared gates and slack unused. | Optimize the costed DAG under global timing requirements.             |
| R3 $\to$ R4       | A local De Morgan choice ignores shared polarity across consumers.       | Evaluate phase and shallow algebra jointly with real DAG costs.       |
| R4 $\to$ R4.1     | Additional candidates yield small area gains but expensive searches.     | Make Area–Runtime tradeoffs explicit.                                 |
| R4.1 $\to$ R5–5.1 | Repeated structure building and text processing waste search time.       | Preserve candidate semantics while eliminating recomputation.         |
| R5.1 $\to$ R6     | A fast mapping framework need not exhaust local Boolean alternatives.    | Resynthesize bounded cuts under exact full-network costs.             |
| R6.0 $\to$ R6.1   | Valid area gains do not justify the measured runtime.                    | Cache and prioritize cuts with a fixed search budget; accept or stop. |

A question-led map of the Stage 1 research path. “Observation” denotes the development evidence prompting the next question, not a controlled causal effect.

</div>

**What would have counted as failure?** A proposed new mapping would be rejected if it broke functionality, missed required delay targets without a compensating purpose, or exhausted permitted resources. An engineering refactor would not qualify as an area-preserving speedup merely because it was faster on one selected case: it had to retain complete official results and survive paired and additional-function checks. These tests do not prove hidden-case performance, but they make the research decisions falsifiable.

# Starting point: what is the real synthesis problem?

A complete truth table for $F:\{0,1\}^n\to\{0,1\}^m$ contains $2^n$ input assignments and $m$ output bits per row. One can always write a sum of minterms: for each row on which $f=1$, form the conjunction of the required input literals, then OR all such conjunctions. The construction is exact, but it can repeat the same combinations, use many NOT gates, and produce long chains of ANDs and ORs. This shows the central tension: *existence of a legal circuit* is elementary, while finding a good shared circuit is not.

The allowed gate set is not a library of all Boolean operations. A multiplexer, XOR, or majority gate can appear in an abstract derivation but must be lowered to AND2, OR2, and NOT, each priced by the current test case. For example, $$a\oplus b=(a\lor b)\land\neg(a\land b).$$ This identity proves implementability, but not that its right-hand side has optimal area or delay. Gate sharing and heterogeneous prices determine which realization is preferable. A gate appearing in two output expressions should ideally be computed once and reused; however, choosing what to share can affect the critical path.

The frozen Round 5.1 source reads the optional runtime limit but does not explicitly parse or enforce a separately supplied ninth-line RAM limit. The evaluator may enforce memory externally; a successful published run or one Peak RSS sample is not a universal guarantee. The full truth table alone requires reading $\Omega(m2^n)$ input bits, and ROBDD size and heuristic search costs can be exponential in the worst case.

A second early realization is that the optimum is constrained rather than scalar. The natural question is whether we can reduce $A(G)$ while keeping $D(G)\le D_{\rm target}$ and avoiding program limits. We will repeatedly return to this distinction.

<div class="tcolorbox">

The *truth table* is the specification of $F$. A *BDD* is one compact way to represent that function by recursive decisions. A *gate DAG* is the actual implementation with fanout, prices, and timing. Finally, the *synthesizer* is the program searching for such DAGs and consuming CPU time and memory. A theorem about one level must not silently be turned into a performance claim about another.

</div>

# A recurring three-input, two-output example

This running example will distinguish Boolean reasoning, structural representation and priced implementation throughout the log. Let $$f_1=(a\land b)\lor(\neg a\land c),\qquad f_2=f_1\lor b.$$ The complete table, ordered by $(a,b,c)$, is:

<div class="center">

| $a$ | $b$ | $c$ | $f_1$ | $f_2$ |
|:---:|:---:|:---:|:-----:|:-----:|
|  0  |  0  |  0  |   0   |   0   |
|  0  |  0  |  1  |   1   |   1   |
|  0  |  1  |  0  |   0   |   1   |
|  0  |  1  |  1  |   1   |   1   |
|  1  |  0  |  0  |   0   |   0   |
|  1  |  0  |  1  |   0   |   0   |
|  1  |  1  |  0  |   1   |   1   |
|  1  |  1  |  1  |   1   |   1   |

</div>

**Shannon step.** Restriction at $a=0$ gives $f_1=c$ and $f_2=b\lor c$; restriction at $a=1$ gives $f_1=f_2=b$. Therefore the two output BDDs share the $b$ cofactor. Yet a shared *BDD node* is not a physical gate, and shared gate placement must be decided after mapping.

To make the reduction visible, the root decisions can be written as $$\begin{array}{c|cc}
 & a=0 & a=1\\\hline
f_1 & c & b\\
f_2 & b\lor c & b
\end{array}.$$ One decision graph with root $a$ for each output therefore points to the *same* residual subproblem $b$ in both high branches. The equality of two cofactors is a mathematical reason for merging them; no heuristic guess is involved. It does *not* imply that a post-mapping hardware node has to be reused at every possible location.

**A legal netlist.** Using ID $0$ for constant zero and IDs $1,2,3$ for $a,b,c$, take $$\begin{array}{c|l}
\text{ID}&\text{gate and inputs}\\\hline
4&\mathrm{NOT}(1)\\
5&\mathrm{AND2}(1,2)\\
6&\mathrm{AND2}(4,3)\\
7&\mathrm{OR2}(5,6)\\
8&\mathrm{OR2}(7,2)
\end{array}
\qquad(y_1,y_2)=(7,8).$$ For illustrative areas $a_{\mathrm{AND2}}=2$, $a_{\mathrm{OR2}}=3$, $a_{\mathrm{NOT}}=1$, the area is $2(2)+2(3)+1=11$. Let the respective gate delays be $2,2,1$. Forward arrival propagation gives $T(4)=1$, $T(5)=2$, $T(6)=3$, $T(7)=5$ and $T(8)=7$, hence network delay $7$. With target $8$, $R(8)=8$ and $R(7)=\min\{8,8-2\}=6$, so gate $7$ has slack $R(7)-T(7)=1$ along the path to output $8$. Although $7$ is itself the first primary output, it is also a fanin of gate $8$: its required time is therefore *stricter than the nominal output target*. This provides a concrete example of why multi-output sharing matters in the backward timing recurrence.

**A useful surprise.** Absorption changes $f_2$ to $b\lor(\neg a\land c)$. Gate $8$ can therefore use inputs $(2,6)$ without changing any other line, producing the same two Boolean outputs and the same area, but output $f_2$ then arrives at time $5$. This is not a global optimum proof; it is a controlled illustration of why algebra, fanout and timing must be considered jointly.

**What happens to required time after a rewrite?** After absorbing $f_2$ into the direct gate $8=\mathrm{OR2}(2,6)$, gate $7$ no longer feeds gate $8$, although it remains the first primary output. Its *new* required time becomes $R'(7)=8$ rather than $6$. Thus a valid rewrite can change the fanout graph and the required-time constraints even when it preserves both Boolean outputs. This is exactly why old required times are local proof tools for a *fixed-boundary* rewrite, not numbers that may safely be reused after arbitrary restructuring.

# Round 1: obtain an indisputably correct construction

## Observation and motivation

Before comparing elaborate heuristics, we need a constructor that never relies on guessing hidden circuit structure. A complete table does not disclose the network that produced it, and many distinct networks can implement exactly the same function. The logical target should therefore be *equivalence to the table*, not reconstruction of a hypothetical unique original gate diagram.

## The mathematical step: Shannon decomposition

Pick any variable $x_i$ and restrict the function to its two possible values: $f_0=f|_{x_i=0}$ and $f_1=f|_{x_i=1}$. The Shannon identity, a foundation of switching-network synthesis , is $$\label{eq:logshannon}
 f=\neg x_i\land f_0\;\lor\;x_i\land f_1.$$ Why is this true? If $x_i=0$, the first conjunction reduces to $f_0$ and the second to zero; if $x_i=1$, the roles exchange. These two cases exhaust the domain. Repeatedly applying (<a href="#eq:logshannon" data-reference-type="ref" data-reference="eq:logshannon">[eq:logshannon]</a>) reduces every function to constants at the leaves and is therefore a constructive correctness argument.

But a full Shannon *tree* may represent the same cofactor in many branches. Consider a function whose truth values no longer depend on a variable after earlier decisions; continuing to branch on that variable is redundant. Another possibility is that two different branches lead to the identical remaining function. These are representation-level redundancies, not exotic Boolean identities.

## Reduced Ordered Binary Decision Diagrams

Fix a variable order $\pi$. A BDD node stores its decision variable and the references to its low and high cofactors. We apply two exact reductions: (i) if the two child references are equal, skip that decision; (ii) if an identical node with the same variable and child references exists, reuse it from a unique table. The result is a shared DAG, not merely a binary tree. Bryant’s ROBDD framework explains why fixed ordering and reduction give a canonical function representation .

<div class="theorem">

If every terminal has the correct constant value and every decision node computes (<a href="#eq:logshannon" data-reference-type="ref" data-reference="eq:logshannon">[eq:logshannon]</a>), merging nodes of equal triples and deleting nodes with equal children leaves every output function unchanged.

</div>

<div class="proof">

*Proof.* The full decision expansion computes the table by repeated case analysis. Merging two identical triples merges identical decision expressions. When the low and high child coincide, $\neg x f_0\lor xf_0=f_0$, so the parent is redundant. Apply these identities at each reduction step. ◻

</div>

## Implementation and evidence

The baseline lowers decisions to the allowed physical gates, shares equal gate expressions via structural hashing, and outputs topologically ordered IDs. The Round 1 WSL evidence is 25/25 official PASS but only 12/25 cases meeting the target delay; summed area is 1,103,455. The independent checker additionally verified the outputs under its own exhaustive-or-sampled procedure.

<div class="tcolorbox">

**Learning:** the algorithm is correct, but correctness alone says nothing about whether its variable order, sharing pattern and gate depth are good. Next, keep the exact Shannon foundation but widen the space of equivalent realizations.

</div>

# Round 2: representation is an optimization variable

## Why a smaller BDD need not imply a smaller circuit

A BDD is an abstract decision representation; the assignment asks for a priced AND/OR/NOT netlist. Two BDDs encoding the same function can have very different numbers of decision nodes, but even fewer decision nodes need not imply cheaper *mapped* gates. One structure may expose common AND subexpressions, another may induce many NOT gates, and a third may admit more balanced evaluation. Thus variable ordering and mapping must be evaluated *after* lowering into the actual library.

## Influence-based variable ordering

A natural way to choose a decision variable is to ask whether changing it frequently changes the output. For a single Boolean function, $$I_i(f)=\frac{1}{2^{n-1}}\sum_{x_{-i}}\mathbf1\{f(x_{-i},0)\ne f(x_{-i},1)\}.$$ A variable with large influence is frequently decisive. The heuristic places such variables earlier in one candidate order. This is a plausible structural guide, *not* an optimality theorem: sensitivity and BDD node count are different notions, and neither captures weighted gate area by itself.

#### Compute influence instead of taking it on faith.

In the running example, $f_1$ chooses $c$ when $a=0$ and $b$ when $a=1$. Flipping $a$ changes the output precisely when $b\ne c$, which occurs on two of the four $(b,c)$ assignments. Therefore $I_a(f_1)=1/2$. Flipping $b$ changes $f_1$ when $a=1$, while flipping $c$ changes it when $a=0$; so $I_b(f_1)=I_c(f_1)=1/2$ as well. Influence cannot distinguish the selector from either data signal for this function. By contrast, $f_2=b\lor(\neg a\land c)$ has $I_b(f_2)=3/4$ and $I_a(f_2)=I_c(f_2)=1/4$. The combined influence ordering can be useful but is inevitably sensitive to how multiple outputs are aggregated. It does not know the actual gate prices or the quality of downstream sharing.

## Two-level Shannon expansion

One first-level decision may create a long chain of nested multiplexor-like logic. The next idea is to expand two levels at once, possibly choosing different second variables in the two branches. Formally, $$\begin{aligned}
 f={}&\neg x\land(\neg u\land f_{00}\lor u\land f_{01})\\
 &\lor x\land(\neg v\land f_{10}\lor v\land f_{11}).
\end{aligned}$$ The derivation simply substitutes Shannon’s identity into both cofactors. Its advantage is structural: four gated terms can often be computed in parallel and combined with a balanced OR structure, which may shorten the critical path. Its disadvantage is equally important: an expansion can duplicate shared subfunctions and inflate area. It belongs in a *portfolio*, not as an unconditional rewrite.

## Small-support SOP and POS

The next route does not begin with a BDD at all. A variable is *essential* if its two cofactors differ. When a function depends only on a few essential variables, directly enumerate cubes (partial assignments), derive prime implicants, and select a greedy cover of the function’s on-set. An SOP is exact if every selected cube implies the function and their union covers all true minterms. This is worth proving as two inclusions. Every selected cube lies inside the on-set, hence the SOP never outputs $1$ where $f=0$; coverage ensures the SOP never outputs $0$ where $f=1$. Consequently it agrees with $f$ on the entire domain. A POS-like implementation can be obtained by covering the complement and negating its result. The optimization is incomplete because greedy cover is not guaranteed minimal, and prime enumeration can become exponential, so the implementation restricts support size. These are familiar issues in classical two-level logic minimization .

#### A cover on the running example.

Since $f_2=b\lor(\neg a\land c)$, the cube $b$ covers all rows with $b=1$, while $\neg a\land c$ covers the remaining true row with $a=0,b=0,c=1$. Both cubes imply $f_2$, and together they cover its complete on-set: the expression is therefore exact, not merely a plausible simplification. Distributivity also yields the POS $$f_2=(b\lor\neg a)\land(b\lor c).$$ Neither canonical form is guaranteed to be cheapest after mapping: an AND2, OR2, or NOT may have different prices, and some of their subexpressions may already exist in another output’s graph.

<div class="example">

The SOP $(a\land b)\lor(a\land c)$ is logically equal to $a\land(b\lor c)$. The first exposes two independent AND terms; the second shares $a$ and may use fewer gates. Which has lower delay depends on $d_{\land}$, $d_{\lor}$ and the incoming arrivals. Thus algebraic equality is a correctness fact, while its desirability is a cost fact.

</div>

## Portfolio selection and outcome

Round 2 compares a fixed collection of candidates built from alternative decision orders, two-level expansion and small-support implicant forms, then measures their exact final netlist costs. The WSL result has 25/25 PASS and 25/25 target delays, with summed area 790,243, a reduction of roughly 28.4% from Round 1. The search itself costs more runtime: median WSL runtime increases from 5.455 ms to 36.427 ms across those separately archived runs. Since these are not an interleaved pairing, the numbers indicate scale, not an exact causal speed ratio.

<div class="tcolorbox">

**Learning:** representation diversification succeeds at closing the timing-feasibility gap. But much area remains, and an alternative can become more useful when its negated form or downstream slack is exploited. Next, look at the entire shared graph under case-specific prices and deadlines.

</div>

# Round 3: account for complements, shared algebra and timing slack

## Complemented edges: negation is information before it is a gate

If $g=\neg f$, it seems wasteful to store two unrelated Boolean subgraphs representing $f$ and $g$. A complemented-edge BDD reference stores a regular node identity plus one inversion bit. The graph can share the same structural nodes, while the inversion bit carries the semantic complement. To prevent multiple redundant encodings, the unique table normalizes one child-complement convention before interning nodes. This is a representation optimization; when mapped into physical AND2/OR2/NOT, a required inverter must still be emitted or shared and charged.

An affine detector also recognizes functions $c\oplus\bigoplus_{i\in S}x_i$. If the high cofactor equals the negation of the low cofactor, Shannon decomposition reduces to XOR with the decision variable. To check the algebra, write $q=f|_{x=0}$ and $f|_{x=1}=\neg q$; then $$f=(\neg x\land q)\lor(x\land\neg q)=x\oplus q.$$ This recognizes one XOR-shaped decision, not automatically an arbitrary global affine function; full affine recognition requires the appropriate recursive consistency across the remaining variables. It can allow structured balanced XOR constructions, all lowered through legal gates. It can help parity-like truth tables that ordinary BDD mapping handles awkwardly.

## Why timing slack changes the optimization problem

Imagine a network whose target delay is 30 but whose actual delay to an output is 22. A gate-level rewrite that increases an intermediate arrival by 2 is not automatically harmful if every downstream path still finishes by 30. A greedy “never increase any arrival” policy leaves potentially cheaper gates unexplored.

The more principled tool is *required time*. Assign $R(y)=D_{\rm target}$ at each primary output and propagate deadlines backward: $$\label{eq:logrequired}
 R(u)\gets\min\{R(u),R(v)-d(v)\}
 \quad(u\in\mathrm{fanin}(v)).$$ A shared node receives the strictest requirement over its consumers. Its slack is $S(u)=R(u)-T(u)$. We can then consider a cheaper De Morgan mapping even if it slightly increases local delay, provided the new arrival does not exceed $R(u)$. For instance, $$a\lor b=\neg(\neg a\land\neg b)$$ may substitute a cheap AND and shared inversions for an expensive OR. An isolated sufficient area comparison involves $a_{\lor}$ versus $a_{\land}+3a_{\neg}$, but the actual DAG cost depends on which inversions are already present and which gates stay alive due to fanout. Global remeasurement is essential.

<div class="lemma">

Start from a feasible DAG $G$ and compute the old required times $R_G$ backward. Replace an internal cone by an equivalent acyclic cone with the same external boundary. If every replacement root exposed to the unchanged graph has newly computed arrival at most its old required time, and the unchanged gates preserve their old types, delays and dependency edges, the new output delay is at most the target.

</div>

<div class="proof">

*Proof.* Contract each new cone into its exposed root. Each such root meets the old required bound by assumption. For an unchanged gate $v$, each incoming unchanged dependency $u\to v$ obeys $R_G(u)\le R_G(v)-d(v)$. Thus by topological induction $T'(v)\le\max_u R_G(u)+d(v)\le R_G(v)$, including unary NOT with one predecessor. Every output requirement remains at most the original delay target; an output reused internally may have a strictly smaller required time. ◻

</div>

**Why the assumptions matter.** A rewrite that changes fanout, creates a new cross-cone dependency or reuses stale required times after another transformation is outside this lemma. The implementation remeasures the whole candidate DAG, and the accepted-candidate ranking provides a second engineering safeguard. A sufficient condition is not a proof of optimal area or of correctness of arbitrary rewrite code.

## Balancing, bounded search and outcome

Associative AND/OR chains are re-parenthesized when doing so does not break essential sharing, and additional variable orders are attempted under a computation budget. Every candidate is pruned and evaluated as a complete live DAG. The archived Round 3 WSL Area is 533,705 with 25/25 PASS and 25/25 target delay; this is approximately 32.5% below Round 2. The magnitude is a central Stage 1 result, but it is the combined effect of several features. It should not be attributed solely to required-time recovery without the corresponding ablation data.

## What the archived Round 3 ablation actually establishes

We later recovered a development summary that was missing from the first writing draft. Rather than treating the final result as one opaque improvement, it lists concrete snapshots along an algorithmic path. Starting at the $790{,}243$-area portfolio, the successive archived snapshots record $777{,}324$ after complemented-BDD development, $770{,}195$ after affine detection, $762{,}164$ after balancing, $586{,}218$ after slack-aware recovery, $543{,}209$ after an additional reverse-order candidate, and $533{,}705$ after legacy fallback selection. All listed entries have 25 successful target checks in their respective evaluations.

<figure>
<embed src="figures/stage1_round3_ablation_path.pdf" />
<figcaption>The chronological Round 3 <em>development path</em>; the separate implication experiment in the source CSV is deliberately not connected as though it were the next sequential stage.</figcaption>
</figure>

**Why does the distinction matter?** The $175{,}946$ difference between the balanced snapshot and the slack-recovery snapshot is an observation after a sequence of earlier changes. It illustrates why required-time reasoning was so promising, but it does not prove that activating the recovery routine on every possible prior configuration saves exactly that amount. A controlled factorial study would require frozen alternatives differing in only one feature, compiled and evaluated under matched conditions. Our source supports a strong *development narrative*, not that stronger causal claim.

<div class="tcolorbox">

**Learning:** exact Boolean identities can be used more effectively when the optimization considers shared nodes and global deadline slack. Remaining gate-level opportunities may require selecting positive or negative representations across *several* fanouts. Next, explore polarity and algebraic restructuring.

</div>

# Round 4: phase selection and algebraic rewriting

## The missing global choice

A physical inverter can be shared among several consumers. Therefore asking “Should this OR gate be replaced by De Morgan?” independently at each gate misses a global decision: which *phase* of each shared signal should be stored? Define for node $v$ the phase bit $p_v\in\{0,1\}$ and stored function $$g_v=\neg^{p_v}f_v.$$ Changing $p_v$ switches whether its children must be complemented and whether a logical AND is physically realized as an AND or, under De Morgan, as an OR on the opposite phases. For example, if a shared signal $z=u\lor v$ is stored negatively as $\neg z=\neg u\land\neg v$, an AND2 may replace an OR2 but only if the required child polarities can be produced at acceptable cost. No NOT gate is “free” merely because the internal BDD reference has an inversion bit. A shared NOT is paid once per realized source polarity, not once per fanout. We evaluate a surrogate phase objective and use coordinate descent as a heuristic; exact output DAG area and delay still decide whether a candidate wins. This is not a global minimum-area solver.

A second pass applies absorption and factoring across shallow gate patterns. Its gains can be small because the original Boolean structure has already been aggressively simplified. It must also avoid an incorrect inference: if one rewrites a local cone to use fewer gates, the entire netlist may remain the same size when its allegedly removed ancestors are still referenced elsewhere.

## Observed result and the search-cost warning

Round 4 reaches summed Stage 1 area 528,910, down from Round 3 by 4,795 (approximately 0.90%), with all 25 targets still met. But the archived WSL median synthesis time is 127.568 ms, compared with 68.486 ms for Round 3. The comparison is historical rather than same-run paired, yet the cost increase is sufficiently concerning to motivate a dedicated runtime investigation. A separate exploratory variable-order search occasionally expanded the BDD dramatically; candidate limits and fallback are needed to prevent unbounded resource consumption.

## Recovering the missing postprocessor experiment

The newly located `postprocess_comparison.csv` helps answer the question: was it the De Morgan phase pass or algebraic rewriting that mattered more? Applied separately to the archived Round 3 circuits, algebra only reduces total area from $533{,}705$ to $532{,}416$, while phase only reaches $533{,}378$. The two orders of composition are slightly different: phase followed by algebra gives $532{,}078$, and algebra followed by phase gives $532{,}080$. Taking the best strategy for each of the 25 cases produces $532{,}070$.

<figure>
<embed src="figures/stage1_round4_postprocess_ablation.pdf" />
<figcaption>Round 4 postprocessing ablation. These treatments reuse the same original circuits; extra variable-order search is intentionally not included.</figcaption>
</figure>

The important insight is not that one rewriting order always wins. Both the circuit’s shared fanout and the local AND/OR/NOT prices determine which candidate is best. The $532{,}070$ total uses a *per-case selection*, which makes sense for a multi-candidate synthesizer but should not be confused with a single rewrite rule. The fully fledged Round 4 result of $528{,}910$ also contains further variable-order exploration. Thus the difference between $532{,}070$ and $528{,}910$ cannot be counted as a benefit of algebra and phase postprocessing alone.

<div class="tcolorbox">

**Learning:** increasing the candidate pool is not free. A roughly one-percent Area gain can be purchased with disproportionately more computation. Instead of making the Boolean search even more exhaustive, first ask what work the program repeats unnecessarily.

</div>

# Round 4.1: construct the first explicit Area–Runtime Pareto comparison

**Counterfactual considered.** We could continue adding variable orders or polarity restarts and keep every tiny public-case area improvement. But this would spend more of a finite synthesis budget on strategies whose extra benefit had become small. The alternative was not to abandon the improved R4 circuit: it was to ask how much area a faster search would actually sacrifice.

The next experiment varies the amount of polarity postprocessing and variable-order exploration. It retains three executable configurations rather than presenting one parameter setting as universally best: **Strict** minimizes perturbation of the R4 circuit, **Balanced** accepts a tiny area change for runtime reduction, and **Fast** reduces the search further. These are meaningful *Pareto alternatives*: lower runtime can require worse area, and a global criterion is impossible without knowing the actual scoring function.

Two WSL measurements report that the Balanced configuration produces Area 529,014 in both runs; its median runtime is 96.048 and 102.615 ms. Strict preserves Area 528,910, while Fast reaches Area 530,822. In the case-level data, Fast has a conspicuous area regression in `case_018`; the small relative area-sum penalty conceals a large localized change. This demonstrates why we record per-case data and not only aggregate sums.

#### What makes two settings genuinely incomparable?

Say configuration $X$ dominates $Y$ if $A_X\le A_Y$ and $T_X\le T_Y$, with at least one strict inequality, under matched evaluations. If $X$ is smaller but slower, neither dominates the other: there is no single unambiguous winner without a scoring utility or an explicit time constraint. Strict and Balanced illustrate exactly this tension. This is a *Pareto* argument, not a claim that area and milliseconds can be added together in a physically meaningful unit.

**Research decision:** Balanced becomes the candidate for engineering optimization, not because its gate area is absolutely smallest, but because its area sacrifice relative to Strict is 104 out of roughly 529,000 while lowering median runtime. We retain Strict as the area-oriented comparator.

# Round 5: remove recomputation before reducing search quality

**The change of object.** Until now, the algorithm had treated the circuit as the thing being optimized. Here the *synthesis program* becomes the object of analysis. This is not a semantic change to a Boolean function: we are asking whether repeated work inside the compiler can be removed before sacrificing any useful gate mapping candidate.

## A useful conceptual split

There are two ways to accelerate a synthesis engine: *delete candidate searches*, or *implement the same searches more efficiently*. The latter is preferable when we already trust the candidate quality. Profiling revealed three repeated operations: multiple mapping policies rebuild the same ordered BDD; several small-support candidates recompute identical implicant covers; and every candidate’s textual netlist is reparsed for area and timing estimates.

Fix the truth table $F$ and variable order $\pi$. Let $B(F,\pi)$ be its immutable BDD. If policies $\theta_1,\ldots,\theta_k$ share $\pi$, then they can all use the same BDD: $$C_i=\operatorname{Map}(B(F,\pi),\theta_i).$$ The semantic reason is simple: BDD building depends on $(F,\pi)$, not on how a later gate mapper chooses to realize its nodes. The cache key is logically meaningful: it must distinguish different truth functions and different variable orders, and the cached graph must not be modified by downstream candidates. If the mapper mutates the shared structure, reuse becomes a correctness risk rather than a safe speedup. Likewise, cache hits justify avoiding computation, not inventing a better Boolean function. Throughout this log we use $\land$, $\lor$ and $\neg$ for Boolean connectives; $\mathrm{AND2}$, $\mathrm{OR2}$ and $\mathrm{NOT}$ denote gate types in mathematical expressions; and the corresponding monospaced tokens are reserved for literal netlist syntax. In a simplified cost model the repeated build term decreases from $kT_B$ to $T_B$. Crucially, this does *not* imply a $k$-fold overall speedup when mapping or postprocessing dominates. Cached implicant covers follow the same logic: symbolic cube selections depend on the function and deterministic tie-breaking, while physical gate emission remains candidate-specific.

Round 5 also removes one provably duplicate candidate when $n>13$. In the frozen configuration the pair differed only by an implicant mode that is disabled for those dimensions, so the two candidate computations were identical. A lightweight line scanner further reduces repeated netlist-statistic overhead.

## What the paired evidence shows

In the dedicated Round 5 WSL pairing, Round 4.1 Balanced had median synthesis runtime 87.041 ms and Round 5 had 68.861 ms, both with Area 529,014 and 25/25 correct and target-met cases. All 25 emitted netlist files in that local comparison were byte-identical. These observations support a genuine implementation-efficiency gain. However, time-based candidate cutoffs mean the same byte identity is not guaranteed under every possible timing environment; one independent container rerun had a different yet valid candidate near a deadline.

<div class="tcolorbox">

**Learning:** caches remove repeated *Boolean analysis*, but the engine still converts graphs to text and back as it rebalances and recovers area. If gate structure is already available, why throw it away between stages? This directly motivates typed in-memory DAGs.

</div>

# Round 5.1: treat the netlist as a data structure, not repeated text

**Why another implementation round?** Caching helped with BDDs and covers, but the candidates still passed through several text-to-graph and graph-to-text transformations. Those conversions have no Boolean significance; they exist only because of an inconvenient intermediate representation. Round 5.1 therefore tests whether a typed internal graph can retain the same transformation logic while making it cheaper to execute.

## The engineering hypothesis

A text format is a good external interface but a poor internal representation for repeated graph operations. Instead of parsing a netlist for rebalancing, serializing it, then parsing again for area recovery, Round 5.1 stores a typed gate table $v\mapsto(\mathrm{op},a,b)$ and an explicit output list. Structural hashing interns identical immutable gates; reachability pruning discards dead nodes at the final serialization step. For commutative AND2/OR2 nodes the builder sorts input IDs before hash lookup. For rebalancing, a same-operation internal cone is flattened only when the interior nodes have a single consumer, while output references are included in the fanout count. An interior gate used by two consumers cannot simply be dissolved into one of them: the other consumer still needs that signal. In graph terms, only *unshared* associative interiors can be freely re-parenthesized without requiring a separate replacement for the other use. This matters in a multi-output network: reusing an output as someone else’s intermediate result must not cause that shared computation to be silently removed. A topological induction over gate IDs proves the functional equivalence of these associative, commutative and idempotent rewrites; a reverse reachability pass from *all* output roots preserves every live shared gate.

If a new gate is created only after its fanins exist, its arrival can be stored immediately: $$T(v)=\begin{cases}
 T(a)+d_{\neg},&\operatorname{op}(v)=\mathrm{NOT},\\
 \max\{T(a),T(b)\}+d_{\operatorname{op}(v)},&\text{otherwise}.
 \end{cases}$$ Topological induction proves this stored arrival correct. This is a real *incremental arrival-time* computation, but the implementation does **not** claim incremental global area accounting. A replacement may free an entire private cone, but a gate that still serves another output remains live. Exact area is recomputed after reachability pruning to avoid charging errors.

#### Follow one gate through the builder.

The input Netlist assigns every gate an ID greater than its fanin IDs. The in-memory parser stores that ordered graph as nodes $(\mathrm{op},a,b)$; the builder can therefore compute $T(v)$ immediately after a new node is created. When two AND2 nodes receive the same two operands in opposite orders, sorting their IDs makes their hash keys identical, which is legal because $u\land v=v\land u$. The key does *not* unify arbitrary Boolean-equivalent but structurally different expressions: that would require more algebraic reasoning. After transformations, the serializer traces backward from *every* output, discards nodes outside the union of their ancestor sets, and renumbers the rest. Induction over this topological order explains both semantic preservation and why a gate feeding multiple outputs must be counted only once.

**Limits of the proof.** This reasoning assumes each local rewrite implements the intended Boolean identity and that its new dependencies remain acyclic. The actual program still needs parser validation, full-DAG rescoring and independent netlist checks; a correct identity on paper cannot rule out an indexing bug in C++.

## Why this is not just another heuristic

Round 5.1 keeps the same mapping policies and internal cost ranking as Round 5. The typed DAG covers the high-frequency candidate balancing/recovery passes, but the final phase/algebraic alternatives still serialize and reparse netlists; the system is not entirely text-free. The aim is to change the *cost of executing* the optimization, not its mathematical candidate space. Accordingly, functional identity and equal output netlists are strong regression checks. In a first WSL paired run all 25 Round 5 and 5.1 outputs were byte-identical; the second had the same per-case areas and delays. Under a clock-bounded search, this remains an empirical property rather than a cross-platform guarantee. In particular, the source uses elapsed-time checks before later modern and legacy candidates, additional postprocessor eligibility thresholds, and periodic time checks for selected BDD orders; none constitutes a hard preemption mechanism for all stages. Since the candidate set is timing-dependent, two correct executions can output different valid netlists while using the same lexicographic ranking. The comparison to Round 5.1 therefore supports an engineering-efficiency claim, not a deterministic-output or optimality theorem.

## Measured speed and generalization

The WSL paired medians change from 72.188 to 55.488 ms in one run and 60.827 to 55.077 ms in the other. Both versions have 25/25 PASS, 25/25 target delays and total Area 529,014. The average of the two per-run medians improves from 66.508 to 55.283 ms, about 16.9% (a descriptive two-run estimate). A mixed holdout of 80 functions and a 16-case larger set also pass the evaluator and independent checker, but the gains are distribution-dependent: small cases may see little benefit or small overhead, while larger graphs profit more from avoided parsing.

<figure>
<embed src="figures/stage1_paired_runtime.pdf" />
<figcaption>Paired WSL comparisons from distinct recorded experiments. The figure is constructed from authentic CSV records with the bundled plotting script; inter-group medians are not interchangeable experiments.</figcaption>
</figure>

<div class="tcolorbox">

**Learning:** the engineering refactor achieves another measurable runtime gain without sacrificing measured gate quality. The next research question should not be “how many more milliseconds can be shaved?” but “is the chosen function decomposition leaving significant circuit-area opportunities on the table?” Freeze this implementation as the efficiency baseline.

</div>

## A limited memory snapshot: what Peak RSS says

After the source freeze was checked on the student’s own WSL installation, we ran the exact research source on the large `case_024` as a standalone process under GNU `/usr/bin/time -v`. The terminal reported normal exit, wall-clock time $1.66$ s and peak resident memory $69{,}480$ KiB ($67.85$ MiB); the synthesizer itself reported area $124{,}475$ and delay $70$. The raw `/tmp` time log was not uploaded, so this writing archive labels the record as a student-supplied terminal transcription.

The measurement answers a narrow question: *how much memory did one particular process run make resident at its peak?* It does not bound worst-case memory across the 25 official cases, does not measure all virtual-memory allocations, and must not replace the official evaluator’s per-case synthesis runtime. Preserving these distinctions is part of experimental reproducibility, not a cosmetic disclaimer.

# Round 6.0: a change of representation, not merely another BDD order

**Why resume Boolean optimization after engineering speedups?** A faster synthesis engine is valuable only if it gives room to seek better realizations, or if synthesis time itself is a scoring concern. The next experiment deliberately returns to gate quality: a mapped DAG can still contain locally expensive expressions that are not exposed by changing the original BDD order. This is a new hypothesis, not an extension of the caching theorem.

## Motivation: escaped local equivalences

A BDD-derived circuit may already be compact as a BDD yet still contain local multi-gate patterns that another circuit can implement more cheaply. The new idea is to inspect *the final gate DAG itself*, choose a small boundary of signals, recover the exact Boolean subfunction between that boundary and an internal output, and resynthesize the subfunction independently of the original local shape.

## What exactly is a feasible cut?

For a chosen node $v$, a cut $C_v$ is a collection of upstream boundary nodes meeting every path backward from $v$ to a primary input. A $k$-feasible cut has at most $k$ leaves. Round 6.0 fixes $k\le4$. Treat the cut-leaf values as *formal* independent variables solely when enumerating assignments. This is not probabilistic independence: the real leaf signals can be correlated, but any replacement equal on all $2^k$ formal assignments is certainly equal on the subset the surrounding circuit can actually produce.

With $k\le4$, the local truth table uses at most $2^4=16$ bits: $$M_{v,C}=\sum_{s=0}^{2^k-1}f_{v,C}(s)\,2^s.$$ This small mask is the bridge between an arbitrary gate cone and generic Boolean synthesis; classical DAG-aware AIG rewriting offers a related but more comprehensive rewrite-library approach . Candidate realizations include SOP, complemented SOP/POS, shallow factoring and one-variable Shannon decompositions. All use AND2, OR2 and NOT. The search is *not* complete and should not be called an exact minimum-area optimizer.

## Why gate sharing makes local estimates dangerous

#### A cut mask that can be checked by hand.

Return to the example’s second output $f_2=b\lor(\neg a\land c)$. Treat $(a,b,c)$ as formal cut leaves and number assignments by $s=4a+2b+c$. The rows where $f_2=1$ are $s=1,2,3,6,7$, so its 8-bit truth-function mask is $$M_{f_2,\{a,b,c\}}=2^1+2^2+2^3+2^6+2^7=206=\texttt{0xCE}.$$ A local resynthesizer can check candidate expressions against these eight bits *before* considering gate costs. Equality on all formal boundary assignments guarantees equality for the actual boundary signals, even if they are not independently realizable; the guarantee is sufficient, not necessarily a minimal test. It says nothing yet about cycles, the output interface, or area.

#### Count the surviving DAG, not the rewritten text.

Let $L(G)$ be the set of gates reachable from *any* primary output. With prices $a(v)$, the exact area is $A(G)=\sum_{v\in L(G)}a(v)$. If a candidate “eliminates” a gate which still feeds another output, that gate remains in $L(G)$ and its area is not saved. Our running example shows this sharply: after replacing gate $8$, gate $7$ is no longer used by $8$, but must remain because it is still the first output. The original and rewritten circuits both cost $11$; the benefit is delay, not area. A valid local rewrite therefore needs both semantic equality and a complete live-DAG cost check.

Suppose a cut replacement seems to save a gate $g$. If another output still references $g$, deleting one use does not eliminate its physical cost. Conversely, a rewrite can free several upstream private nodes at once. The implementation conservatively estimates removable gates through reference counts and counts the candidate local cone cost without treating speculative gates from rejected alternatives as free. Only after an actual candidate is produced does it prune and measure the complete graph, retaining it when true area drops and the deadline remains met.

## Outcome: a successful hypothesis but costly implementation

In the user’s two WSL paired runs, Round 6.0 area changes from 529,014 to 528,738 and 528,744, with 25/25 PASS and target delays. Median runtime, however, increases from 53.286 to 114.610 ms and from 51.403 to 116.351 ms. In another set of 40 generated functions, area falls from 9,709 to 9,496; in an older 80-case set it falls from 22,821 to 22,579; for 16 larger cases it falls from 157,944 to 157,440. These tests support that additional optimization opportunities exist beyond particular public case IDs, but the synthetic distributions do not prove hidden-case success.

<div class="tcolorbox">

**Learning:** new area savings are real, but the cost of repeatedly enumerating cuts and rebuilding equivalent cover candidates is too high. The next question should be “can the same local search be made cheaper?”, not “can we enlarge $k$?”

</div>

# Round 6.1: a deliberate Go/No-Go experiment

## Predeclared engineering constraint

We froze $k\le4$ and made the optimization budget explicit. The cut postprocessor receives 25 ms wall-clock budget, with a second constraint linked to the per-case runtime allowance, and keeps caps on retained cuts and visited roots. The baseline Round 5.1 candidate remains available as fallback. This is *not* a 25 ms bound on the whole synthesis process.

## Reuse local Boolean work

For a four-leaf cut, a truth mask contains at most 16 bits, but the same function may appear at many locations. We cache symbolic implicant covers under $$K=(k,M,p),$$ where $k$ is the number of formal leaves, $M$ the truth mask, and $p$ the deterministic greedy cover policy. The cache stores no actual DAG gate IDs, no fanout, and no timing data. Thus a hit preserves the symbolic Boolean cover while each candidate is re-emitted against its own physical cut leaves. Canonicalizing arbitrary input permutations would require tracking the permutation; this implementation does not silently identify them.

Cuts are also prioritized using a conservative estimate of removable *private* old gates. Finally, the complete netlist is remeasured before an accepted rewrite can replace the incumbent. The method is designed to reduce wasted search, not to expand the mathematical search space.

## What the local evaluation actually concluded

Two WSL comparisons reported Round 6.1 areas 528,854 and 528,839 versus 529,014, with full official PASS and target delay. Median synthesis runtime increased from 54.572 to 80.731 ms and from 50.224 to 74.083 ms. Averaging paired medians produces a roughly 47.7% increase, exceeding the previously selected 30% tolerance. The small area improvement, about 0.03% on the public case sum, is not enough to justify replacing Round 5.1 as default.

The fresh 40-case mixed and 8-case larger holdouts nonetheless demonstrate valid generalizing area savings: 11,186 to 10,858 and 67,275 to 67,047, respectively; all pass both correctness and target delay, but their synthesis medians rise from 7.852 to 10.762 ms and from 68.093 to 94.327 ms. The positive and negative conclusions must be presented *together*.

<figure>
<embed src="figures/stage1_holdout_area.pdf" />
<figcaption>Fresh Round 6.1 holdout area by function family; source data and rendering script are included.</figcaption>
</figure>

## What the development budgets really measured

We also recovered two intermediate budget sweeps. On the 40-function mixed *development* set, the nominal cut budgets $25$, $35$ and $45$ ms all save the same $213$ local area units. The corresponding median *postprocessor* wall times are $4.84$, $4.59$ and $4.91$ ms, a fluctuation too small to interpret as a monotone speed law. On a different, larger *development* set of 16 functions, increasing the budget produces $358$, $408$ and $501$ area units saved, while median local wall time rises from $31.66$ to $40.89$ to $52.38$ ms.

<figure>
<embed src="figures/stage1_round61_budget_tradeoff.pdf" />
<figcaption>Larger-development-set Cut Budget experiment. “Area saved” measures the local postprocessor; these are not sums from the official Stage 1 evaluation.</figcaption>
</figure>

**Decision logic:** on easy local structures, more budget may buy nothing; on harder structures, it can buy more rewrites but at an increasing cost. That explains why the 25 ms limit was a defensible engineering compromise. It does not imply that 25 ms is optimal for every unknown truth table. These were *development* sets already consulted during budget selection, so we cannot rebrand them as fresh blind holdouts.

<div class="tcolorbox">

**Learning:** the hypothesis “cut rewriting can reduce area” is supported, while the stronger hypothesis “the current bounded rewriting implementation is worth its runtime” is rejected under our predeclared local criterion. The appropriate research response is to preserve the evidence and stop incremental threshold tuning, not to erase the unsuccessful branch.

</div>

# How We Constructed Non-Official Test Cases

**Motivation.** Repeatedly modifying a synthesizer after checking the same 25 Stage 1 inputs risks learning incidental features of those particular Boolean tables. More importantly, the public set alone cannot tell us whether an optimization helps affine parity-like functions, mux-heavy structures, sparse products, shared outputs, or dense random truth tables equally. We therefore constructed additional functions from *generative descriptions* and only then expanded them into complete truth tables. This is not a new scoring system, and these cases are not professor-provided Stage 2 data.

**Construction.** A deterministic generator chooses a function family, a fixed pseudorandom seed, $n$ input variables, $m$ outputs, legal gate prices, and a delay target. For each assignment $x\in\{0,1\}^n$ it evaluates every output and serializes the resulting $m$-bit row. Thus the generator produces a legal complete instance, not a hand-selected Netlist. The mixed family includes affine functions (parity of selected inputs), sparse SOP, threshold functions, selector-based MUX, arithmetic bits, shared intermediate predicates, and dense deterministic truth bits. A separate large-function family composes local lookup tables, XORs, shared ensembles, and cascaded multiplexors. The scripts and case-hash manifests are preserved in `shared/test_generation/`; the original truth tables are retained separately rather than redistributed in a public writing package.

**Evaluation protocol.** The Round 5.1 test record has an 80-case mixed set and a 16-case large structured set, plus 110 older regression cases and two stress cases. Round 6.1 was additionally evaluated on a newly seeded 40-case mixed set and an 8-case large set after its budget was selected. In contrast, the 25/35/45-ms cut-search budget sweep was conducted on development sets; it should not be mislabeled an untouched holdout. Each run checks functionality, legality, target delay, area, and synthesis time against the appropriate frozen comparator. A deterministic seed makes a suite repeatable but does not make it representative of an unknown deployment distribution.

**Research lesson.** A regression suite answers *did this change break previously checked behavior?*; a frozen generated holdout asks *does the promising trend persist on a different specified family?*; only the later official Stage 2 release will answer the separate question of generalization to the next course distribution. These distinctions stop an attractive Stage 1 result from being exaggerated into a universal claim.

# How did we guard against benchmark overfitting?

A public benchmark is a finite development set. Repeatedly adjusting thresholds until its aggregate area decreases risks overfitting the properties of those 25 released functions. We therefore distinguish *development evidence*, *repeated regression tests*, and *fresh generated holdouts* frozen after the candidate choices. Functions were generated from affine, sparse, threshold, multiplexing, arithmetic, dense and structured graph-related families across different sizes. Fresh holdout results were not used for further parameter tuning in the corresponding finalized experiments.

Nevertheless, there are limits. A synthetic generator creates its own distribution. A withheld seed is not equivalent to a future teacher-provided test distribution, and a collection already inspected during earlier iterations is no longer fully blind for later strategy decisions. We therefore claim only “no observed functional regression on the tested families” and, where supported, “area improvement on the fresh holdouts.” We do not claim statistical proof of optimality or of performance on unreleased Stage 2 cases.

Independent correctness verification adds a different kind of reassurance. The official evaluator performs the required truth-table check under its contract, while a separately written checker validates legality and independently simulates circuits. For selected smaller functions the independent checker enumerates all rows; for larger ones it uses deterministic samples. The latter is not a formal universal proof, and the separate mathematical correctness arguments are still important.

# A consolidated evidence narrative

## The useful negative results

Not every valid rewrite should be adopted. In the present study, a large truth-table-derived candidate pool could become impractically expensive; phase/algebra refinements produced diminishing public-case area gains; the smaller generated cases sometimes showed negligible runtime benefit from typed DAGs; and four-feasible cut rewriting reduced area but breached the local runtime-acceptance threshold. These observations are not defects to omit from a research record. Each separates a *correct mathematical transform* from a *justified engineering decision*. They also explain why further tuning of a public 25-case benchmark was stopped.

A particularly important counterfactual is the decision *not* to promote R6.1. Had we selected the default solely by public-case area sum, we would have ignored its roughly 47.7% local median-runtime penalty relative to R5.1. Had we dismissed it solely because of that penalty, we would have missed the independent evidence that cut rewriting can help other generated function families. Preserving the branch as an experimental result is more informative than either extreme.

## Why the version history needs more than one number

<figure>
<embed src="figures/13_stage1_multiscale_history.pdf" />
<figcaption>Multiscale Stage 1 area history. The left panel preserves the entire archived 25-case trajectory; the right panel magnifies small late differences against R5.1. These are historical observations, not a controlled causal contrast.</figcaption>
</figure>

Read the sequence by the *question solved*, not by the ordering of bar heights. R1 proves construction. R2 changes representations and meets the timing targets. R3 integrates the global deadline and reduces area substantially. R4 explores global phase and algebra, revealing expensive diminishing returns. R4.1 makes the Pareto tradeoff explicit. R5 and R5.1 refactor repeated computational work while preserving observed quality. R6.0 discovers an overlooked local area opportunity; R6.1 demonstrates the current technique’s unfavorable cost under a fixed decision rule. These are complementary contributions, not a monotone sequence in all metrics.

| Round             | Target met | Summed area |
|:------------------|-----------:|------------:|
| 1                 |      12/25 |   1,103,455 |
| 2                 |      25/25 |     790,243 |
| 3                 |      25/25 |     533,705 |
| 4                 |      25/25 |     528,910 |
| 4.1 Balanced      |      25/25 |     529,014 |
| 5                 |      25/25 |     529,014 |
| **5.1 (default)** |  **25/25** | **529,014** |
| 6.0 (prototype)   |      25/25 |     528,738 |
| 6.1 (research)    |      25/25 |     528,854 |

Local Stage 1 area milestones; a single designated run per round

## What was not proved

The work does not establish a globally minimum area or delay circuit for each input function. It does not show that lower delay after reaching target has zero score value; the numerical score formula was not published. A local gate-count reduction is not automatically a global area reduction in a shared DAG. BDD memory can be exponential. Synthesis time varies under CPU contention and wall-clock search cutoffs, so two valid runs can choose different candidates. These limitations should remain visible in any professional GitHub presentation.

# How to reconstruct the evidence and figures

This writing archive includes all *intermediate datasets used by its charts*, not only final images. Run `python shared/scripts/make_figures.py` from the writing-package root (or call the script by absolute path); it reads the accompanying CSVs and the user-provided palette JSON. If the original local-results ZIP files are available, `python shared/scripts/extract_evidence.py –source-dir /path/to/zips` rebuilds the normalized data from the official CSV members; `verify_provenance.py` additionally checks exact archive digests and reconstructed output bytes. The SHA-256 archive provenance is retained in `source_manifest.csv`. The student-verified research freeze identifies `synth_round51.cpp`; its complete SHA-256 is in the bundled freeze manifest under `shared/data/raw_evidence/`; this is not an assertion of a final Canvas submission.

A reproducible public repository should preserve each round’s source snapshot, compiler flags, evaluator commands, input manifest/hash, official CSV, independent verification result, candidate outputs, and document with the research decision. Large raw netlists can be archived separately, while the paper still includes enough information for a reader to reproduce its figures. The exact local output paths follow the project’s convention `local_runs/YYYYMMDD_HHMMSS_Round*/report_ready/`.

## A concrete replication exercise: from a saved official run to a plot

A plot is not primary evidence. For example, the historical area timeline was derived from nine selected official CSVs stored in *nine different local-run ZIPs*. Each row in the original CSV is an evaluator observation for one case, not an independently proved universal bound. To reconstruct the timeline properly, use the following sequence:

1.  Identify the exact archive and CSV member in `shared/data/source_manifest.csv`. Check the SHA-256 of the complete original ZIP; an archive with the same filename but different bytes is not automatically the same experiment.

2.  Extract the 25 case rows and require unique case IDs `case_001` through `case_025`, with explicitly parsed `status`, `target_met`, `area`, `delay`, and `runtime_ms`. A functionally valid PASS can have `target_met=no`.

3.  Sum the 25 `area` values for the selected run. Compare the result to `round_history.csv`, then regenerate `area_evolution.pdf` using the packaged plotting script. This reproduces the *displayed result*, not the original synthesis computation.

4.  To reproduce synthesis itself, obtain the separate frozen C++ source, official input truth tables and Linux x86 evaluator, rebuild with the recorded flags, and run a fresh evaluation. Retain the new logs and use the independent checker on the resulting netlists. Because later candidates can be gated by wall-clock time, a new valid run need not produce the identical network bytes.

The manuscript ZIP supplies the intermediate CSVs and plots; it *does not* supply the instructor-restricted truth tables or the complete original local-run ZIPs. The additional `verify_provenance.py` can audit only the first and third layers without original archives; passing that restricted audit is not evidence that the synthesis program itself was rerun.

## How we checked that the evidence was not silently rewritten

For this review we ran the historical extraction program into an independent temporary directory. Fourteen normalized CSVs (nine selected official case tables, one run-history table, one manifest, one paired-benchmark table, one per-case comparison, and one holdout comparison) were byte-identical to the writing package. We also checked the standalone user-verified Round 5.1 source digest against the recorded manifest and the raw Round 3, Round 4 and Round 6.1 ablation input hashes. This verifies the lineage of those *particular files*; it does not prove that a human-entered cutoff was chosen before observing every development result, nor does it establish statistical representativeness of synthetic holdouts.

For public GitHub presentation, we should publish the generic scripts, mathematical explanations, citation records, curated aggregate results (subject to course permission), and exact source provenance. We should *not* assume permission to redistribute course-private full truth tables or the evaluator. These materials remain in private experiment archives, while the paper distinguishes available code from unavailable official inputs.

# Reflection and next steps

**Research lesson.** A mathematical identity can certify equivalence; a cost model determines whether the identity is economically useful; a benchmark reports how a particular implementation behaved; and an adoption rule explains why that behavior warranted changing the default. Treating these as separate levels of reasoning is the central habit this project developed. The largest early improvements came from changing the search representation and acknowledging global timing; the later rounds taught us when *not* to trade a large amount of computation for a tiny area gain.

The same small example clarifies what changes at each layer: a cofactor is a function, a BDD edge is a structural reference, a gate is a charged operation, and a path is a timed dependency. Reusing a reference, eliminating a live gate, and shortening a critical path are not interchangeable. This progression—Boolean function, shared decision graph, priced gate DAG, constrained timing graph, and resource-consuming search program—is the conceptual thread connecting the rounds.

An area-optimization algorithm can be mathematically sound and still be the wrong engineering choice when its marginal improvement is dwarfed by synthesis time. Preserving that negative result demonstrates an appropriate stopping criterion, especially under a rubric that rewards deep understanding and justified conceptual application. We therefore freeze Round 5.1 as the principal Stage 1 engineering baseline and preserve Rounds 6.0/6.1 as exploration branches, subject to the students’ final submission choice.

For the later Stage 2 release, we should not reuse the published Stage 1 cases as though they were new holdouts. The actual submitted Stage 1 source should first be frozen, then both the old and any improved algorithm can be evaluated on the new release and on the original cases under matched conditions. This future work is outside the current Stage 1 record.

# Collaboration, AI-Assisted Development, and Responsibility

## How the two students collaborated

The two named student authors, Jincan LI and Zeyun DU, initially investigated approaches independently. They then compared ideas and integrated selected methods into a common research direction. This process was not divided into a fixed checklist of per-person ownership for BDDs, area recovery, or experimentation. We therefore describe the collaboration as independent exploration followed by mutual review and integration, without claiming that a specific individual authored each C++ module or mathematical derivation.

## What AI actually did

Generative AI tools, principally ChatGPT, played a substantial role throughout the work. In particular, AI produced or substantially revised significant C++ implementation code, developed scripts for case execution, benchmarking, data gathering, verification and result packaging, and assisted in mathematical explanation, design suggestions, interpretation of measurements, and the preparation and iterative editing of these documents. This was not merely grammar correction, boilerplate generation, or occasional syntax help. The research record deliberately retains the generated tools and the results they produced rather than retroactively portraying the workflow as manual-only development.

## What the human review and local evidence contribute

Human participation focused on asking which technical problem was worth solving next, questioning proposed optimizations and their marginal benefits, assessing the area–runtime trade-off, demanding checks against overfitting, and deciding when to keep or stop an approach. A student author independently executed the provided Linux evaluator and the local reproduction workflow in WSL, inspected the resulting summaries, and verified the chosen Round 5.1 source digest. These actions establish a concrete review and reproduction path; they do not support a claim that every line of code was written unaided or individually inspected in full.

Several risks follow directly from extensive AI assistance: an apparently plausible transformation may violate a graph invariant, a generated script may compare unmatched experimental runs, and a polished explanation may overstate what data establish. Our response was to retain source snapshots, evaluator outputs and independent checks, distinguish proofs from empirical findings, and revise claims whenever the evidence was narrower than an initial interpretation. This process improves traceability but cannot guarantee optimality or correctness on every unseen case. The authors remain responsible for the factual claims, appropriate citations, and final research decisions in any submitted or published version.


---

# Part II — Stage 2: Resource-Constrained Cut Resynthesis from R7 to R10.1

# Reading contract: what problem is being solved, and what evidence means

## The actual project problem

An input instance specifies a complete multi-output Boolean function

$$F:\{0,1\}^{n}\to\{0,1\}^{m},\qquad 1\le n\le20,$$

plus per-instance integer areas and propagation delays for `AND2`, `OR2` and `NOT`, a circuit-delay target, and optional program-runtime/RAM limits. The program must emit a legal topologically ordered netlist computing exactly the specified truth-table outputs. The target delay matters to quality, but **a functionally valid circuit above the target need not be a format/functional FAIL**. Conversely a timeout or failed resource check cannot be rescued by showing a low partial gate area. No numerical official grading formula was provided; consequently neither a home-made area–delay product (ADP) nor a sum of areas across diverse cases is called “the official score.”

The legal network is a directed acyclic graph, not a collection of independent formulas. If $L(G)$ is the set of gates reachable from the union of all primary outputs, area is

$$A(G)=\sum_{v\in L(G)} a_{\operatorname{op}(v)},$$

and critical-path delay is computed recursively, with primary inputs and the constant source arriving at zero:

$$T(v)=d_{\operatorname{op}(v)}+\max_{u\in\operatorname{fanin}(v)}T(u),
\qquad D(G)=\max_{y\in\operatorname{outputs}}T(y).$$

Write $T_{\mathrm{synth}}(F,\pi)$ for the *program’s* elapsed synthesis time under policy $\pi$, and $M_{\mathrm{peak}}$ for measured resource consumption when available. These are different physical quantities from the circuit’s gate delay. For every round, preserve four separate fields: **PASS/FAIL; target-met; charged Area; circuit Delay; synthesis Runtime** (and RAM where measured). Note that the report itself uses **five** status/metric fields because PASS and target-met are not synonyms.

## Four levels that must not be conflated

1.  **Function:** the truth table defines $F$; Boolean identities can prove exact equality.

2.  **Intermediate representation:** Shannon DAG, ROBDD, complement reference or a small cut truth signature. A compact representation is not automatically an inexpensive netlist.

3.  **Realized gate DAG:** exact AND2/OR2/NOT gates, fanout, liveness, weighted area and timing. A local syntax reduction need not remove a live gate.

4.  **Search procedure:** how many mappings, cuts and roots the program visits before a wall-clock/resource limit. It is possible to improve level 3 while substantially worsening level 4.

Stage 1’s most useful lesson is the separation of these four objects. Stage 2 repeatedly encounters the *same* distinction under tighter and more varied resource constraints.

## How the experimental records were audited

The research bundle contains `01_normalized_data/runs.csv`, `case_metrics.csv` and a content-addressed database `00_inventory/payloads.sqlite`. For every one of the 1,706 run-index entries, the auditor retrieved the original report bytes using the stored report SHA-256, recomputed successful-case Area, Delay, number of PASS, number of target-met, and median success runtime, and reconciled them with the index. This included translating historical `True`/`False` target flags as well as newer `yes`/`no`. **All 1,706 indexed records matched** their original payloads; 602 unique report hashes were seen. This verifies extraction and arithmetic, **not** that every experiment was independently rerun or that duplicated copies count as new observations.

For the directly supplied late-round ZIP archives (R8.4–R10.1), the auditor read the named `experiment/official/` members for each bank, period and configuration directly and produced a second raw table and matched contrasts. Early R7–R8.3 reports were separately retrieved from the same content-addressed source store; their originating archive/member is stated in `runs.csv`. The R10.0 submitted `synth.cpp` and reproducibility snapshot have an identical SHA-256 beginning `8c863f1a...`; the Jincan R5.1 research source begins `cf90d0b1...`; the Zeyun submitted source begins `cd31f7d2...`. The two Stage 1 programs have different administrative and technical roles.

We classify observations as follows. **Direct matched evidence** uses identical bank, case, period and feedback experiment. **Archival development evidence** uses frozen historical outputs but may not control execution order or machine load. **Mechanism probes** hold one input DAG or a small constructed example fixed; they explain *possibility* or a local intervention but not universal production behavior. **Code inspection** identifies the mechanism present in the frozen program; it does not prove which option fired on an uninstrumented historical run. Every number in a cross-version interpretation must be associated with one of these categories.

## The question-led roadmap — not a changelog

<div class="longtable">

@ \>

p(- 4) \* \>

p(- 4) \* \>

p(- 4) \* @

Development problem

&

Experiment or intervention

&

Consequence for the next step

  
Stage 1 establishes correctness but does not minimize a priced, timed shared graph & R1–R5.1: decomposition, portfolios, slack recovery, efficient typed DAG & Obtain a reliable, reasonably efficient full-circuit incumbent.  
Local equivalences remain, but naive cut search is expensive & Stage 1 R6.0/R6.1 & Treat cut rewriting as a promising **research branch**, not a free default.  
A faster kernel still misses a short-budget example & R7–R7.2 & Preserve a legal incumbent and admit optional search conservatively.  
Pattern-only rewrites produce tiny, localized savings & R8 prototype & Search by small **Boolean function**, not only visible syntax.  
More function choices can improve area at added circuit delay and synthesis time & R8.1–R8.2 & Separate feasibility, area-only policy, timing preference and search cost.  
Wall limits make the set of visited nodes unstable & R8.3–R8.5 & Select/prioritize bounded *work*, then study root allocation.  
More time and more useful roots were confounded & R8.6 factorial study & The observed gains follow extra SOP roots, not nominal extra time.  
Benchmark gains may not hold under fresh test families or tight budgets & R8.7–R9.0 & Freeze a safer runtime-first default plus an early structured bypass.  
A new indexed library may discover more hits but save less area & R9.1 & Retain an ordinary repeat-SOP pass.  
Deliverability needs a default policy rather than an environment switch & R10.0; R10.1 & Freeze R10.0 and reject unproductive reductions in its final budget.  

</div>

This roadmap is a *reading guide*. The evidence below is deliberately not represented as one monotone improvement curve.

# One recurring four-output example: why local rewriting must be tested globally

The Stage 1 document used a three-input, two-output circuit to explain Shannon cofactors, shared timing and cut signatures. Stage 2 additionally needs a **four-output** example because shared outputs defeat naive algebraic cost arguments in an especially direct way. Let

$$p=a\land b,\qquad q=a\land c,\qquad r=p\lor q,\qquad s=\neg r,$$

and output all four signals $(p,q,r,s)$. Give AND2 area 2, OR2 area 3, NOT area 1, and corresponding delays 1, 2 and 1. The original DAG contains two AND gates, one OR gate and one NOT gate, so

$$A(G)=2+2+3+1=8, \qquad D(G)=4.$$

A symbolic optimizer notices $r=(a\land b)\lor(a\land c)=a\land(b\lor c)$. As an isolated expression, factoring has fewer conjunctions. But because $p$ and $q$ are themselves primary outputs, both original AND gates remain live. We must now add the intermediate $b\lor c$, an AND computing the newly factored $r$, and keep the NOT for $s$. Thus

$$A(G')=2+2+3+2+1=10,\qquad D(G')=4.$$

The factorization preserved **all** output truth functions but made the physical circuit **25% more expensive**. This is not hypothetical: `06_reproducibility/scripts/mechanism_test.cpp` was independently compiled against the frozen R10.0 headers. It returned `factored=0 area=8 delay=4` and `factored=1 area=10 delay=4`, with identical root truth mask `168` in both cases; another 768 signature/mapping checks passed. It demonstrates the strict distinction between **Boolean correctness**, **local expression cost**, and **global output-reachable area**.

A second Stage 1 running example has $f_1=(a\land b)\lor(\neg a\land c)$, $f_2=f_1\lor b$. Replacing only the implementation of $f_2$ with $b\lor(\neg a\land c)$ leaves the shared $f_1$ gate alive; its netlist area remains 11 but output delay drops from 7 to 5 under the reference gate costs. This is a **delay gain with zero area gain**. Together the two examples expose the central tension that later rounds must manage: equivalence proves *legality of substitution*, not *worth of substitution*.

For any two realized graphs with the same library costs,

$$\Delta A=A(G')-A(G)
=\sum_{v\in L(G')\setminus L(G)}a_v
 -\sum_{v\in L(G)\setminus L(G')}a_v.$$

This is a useful **exact accounting identity**, not a theorem that a particular candidate will have $\Delta A<0$. It is why Stage 2 distinguishes estimates of *private old cone reclaim* from final full-network acceptance.

# Transition: from Stage 1 evidence to Stage 2 constraints

The preceding Stage 1 study already established a complete progression: exact Shannon/ROBDD construction, diversified mappings, slack-aware global recovery, typed DAG execution, and exploratory four-leaf cut rewriting. Its crucial unresolved problem was not whether cut rewriting *could* save area—Rounds 6.0 and 6.1 measured real savings—but whether a function-level local search could be made valuable within the synthesizer’s deadline and memory constraints. Stage 2 resumes precisely at this engineering question rather than starting the mathematical argument anew.

The separate actually submitted Stage 1 program (Z1) and Jincan’s frozen R5.1 research program (J51) remain distinct. Z1 provides the assignment’s formal submitted-stage comparator; J51 is the implementation-research lineage feeding into the R7–R10 development. Later matched evaluations of both programs are reported as distinct observations, not as a fabricated single lineage. The course specification, exact source snapshots, and raw results remain the authority for each claim.

# Round 7: when compiler optimization first exposed a feasibility cliff

## The motivation was not simply to reduce area

Entering Stage 2, the synthesizer must retain the existing exact representation and mapping portfolio but also survive short end-to-end runtime caps. Stage 1 had demonstrated that a cut search could be expensive; Stage 2 begins one level earlier: even finding the first valid candidate can consume too much time on particular tables. Round 7 starts from the frozen J51 source and experiments with the prime-implicant merge/greedy-cover computational kernels. Source switches `UFUG_R7_LEGACY_MERGE` and `UFUG_R7_LEGACY_COVER` permit restoration of the prior implementation for controlled comparison.

It is important to distinguish **algorithmic coverage** from **execution scheduling**. A faster kernel may reduce the cost of certain implicant operations but can also change which later portfolios reach a time gate; conversely the first candidate can still be too expensive on a short-limit example. There is no automatic theorem that a local kernel speedup guarantees end-to-end success.

## What the historical R7 controls actually showed

In the R7 Audited Stage 2 comparison, the default modernized path had **24/25 PASS** (24/25 target met). Its **partial** area sum over 24 successes was 506,754 and successful-delay sum 1,065. The `legacy_merge`, `legacy_cover` and `legacy_both` paths completed **25/25 PASS** and target-met cases, with complete area 508,535 and delay sum 1,101. The missing case was **Stage 2 / case_016**, which had the short 100-ms cap. A 24-pass sum of 506,754 must not be called “better area” than 508,535 on 25 passes: an unreturned legal network has no comparable reported area.

Case 016 is a particularly useful falsification of the simplistic hypothesis “large $n$ is always the scheduling bottleneck.” Its input dimension is modest, but the cap and specific search path are restrictive. The relevant principle is **time to produce an incumbent**, not input size alone; this log intentionally does not make the input-dimension distribution a separate research topic.

The audit’s five variants and repeated case-specific profiling implicated the dispatch/search schedule, but archived aggregate CSVs are not a full event trace. We can say the default execution **failed under the limit** while legacy controls passed; we cannot infer which specific function call was always responsible without the matching trace.

<div class="tcolorbox">

**Decision after R7.** Prioritize *obtaining a correct output before optional refinements*. Treat emergency guards as part of the algorithm’s feasibility design. This shifts the central question from “which kernel is fastest?” to “which candidate work should be admitted before the deadline?”

</div>

# R7.1 and R7.2: a guard is necessary, but a blind guard throws away circuit quality

## R7.1: the first attempt to protect the incumbent

R7.1 applies a short-budget dispatch guard and tries to avoid late, expensive alternatives. In the frozen descendants, the guard’s *heuristic* admission line is visible: with a positive limit, `r71_search_cap` is 72% of limits at most 250 ms, otherwise 75%; later candidates are skipped when the elapsed launch time reaches this reserve. This is **not** hard preemption of C++ execution. Candidate constructors that ignore cancellation or cross a time check can still finish late.

R7.1’s `r71_guard` recovered the missing Stage 2 case and achieved **25/25 PASS, 25/25 target**, complete Stage 2 area **508,535**, delay sum **1,101** and one recorded median runtime **31.268 ms**. But `r71_policy_off` still had only 24/25. More revealingly, on Stage 1 / case_020 the guarded path cost **777 area and 32 delay** whereas a corresponding legacy path gave **766 and 30**. That example is tiny in aggregate terms, yet conceptually decisive: a guard can preserve execution feasibility by prematurely suppressing useful cheap work. It is a **quality regression**, not a correctness failure.

## R7.2: conditional shortlisting rather than all-or-nothing search

R7.2’s alternative is to keep the incumbent-first guard and selectively admit a **bounded shortlist** where time remains. The frozen descendant exposes `UFUG_R72_POLICY` for `guard`, `shortlist` and `nocancel` behavior, with a stricter admission test and checkpoint/cancellation diagnostics. The intended logical distinction is: do not restart a risky full search, but do not assume that every optional candidate is equally expensive or equally useless.

In the two-bank R7.2 feedback (two periods), Stage 2 `r72_guard`, `r72_nocancel`, `r72_shortlist` and the comparator achieved 25 PASS and target met, with area **508,535** and delay **1,101** under the successful reported runs. The Stage 2 medians in one run were approximately 31.033, 29.846 and 30.489 ms for the three R7.2 policies, compared with 29.985 ms for `r71_guard`; none should be ranked as universally faster on this small difference. The **Stage 1 / case_020** correction, by contrast, separates policies more clearly: `shortlist` and `nocancel` restore the baseline network quality while `guard` retains an 11-area regression.

## The decision that survived

The final scheduling rule learned from R7–7.2 is not “always run less” and not “always run the fastest branch.” It is a two-layer feasibility strategy: (i) establish and preserve a legal incumbent; (ii) spend remaining time on the most plausibly useful extra work, with a conservative admission guard. Later R9 and R10 keep that principle when adding expensive cut passes, so the R7 family is a genuine **architectural prerequisite**, not a disposable preface.

# Round 8 prototype: why algebraic patterns and iterations were a necessary but insufficient probe

## The research question and its origin in R6

Having restored an incumbent-first runtime discipline, the next task was to find lower-area implementations of a circuit that already passed. One could simply revisit the original truth table with a new variable order, but that does not directly change a *particular expensive gate pattern in the emitted DAG*. Stage 1 R6 had shown that local resynthesis was possible, although expensive. Round 8 therefore starts with cheaper, narrower structural interventions: factoring visible shapes, reusing identical algebraic substructures and running a small number of repeat cleanup passes.

The principle is elementary but nontrivial under sharing: Boolean operators are associative, distributive and absorb certain repeated terms, yet a substitution may change a network’s fanout, liveness and critical path. The prototype deliberately tests `off`, `factor`, `reuse`, `strict`, `all` and `iterate` instead of assuming every rewrite can safely be composed. The corresponding code is retained in `r8_structural.hpp` and called by the frozen descendant through the optional `UFUG_R8_POLICY` branch. Later production runs default **away** from this research branch, because the more general cut search supersedes it.

## Interpreting the experiment at the proper unit

On the 25 Stage 1 published cases, the R8 prototype and R7.2 remained at 529,014 area and all 25 met target, across both recorded periods. On Stage 2, R7.2 area was 508,535; `factor` and `strict` also gave 508,535; `reuse` and `all` gave 508,523; and `iterate` gave **508,480**. The gain of 55 comes entirely from a localized opportunity on Stage 2 / case_021. In an offline five-pass trace of that same example, successive extra area savings were 12, 35, 4, 4 and 0. Its delay moved from 69 to 70 while remaining feasible. The complete Stage 2 delay sum consequently moved from 1,101 to 1,102. Both public periods reproduced these area totals.

The fourth and fifth passes are a warning about convergence language. A zero *next-pass* gain is evidence of a local fixed point **under the current rule, order and remaining graph**; it is not proof of minimum-area realization. And the gains cannot be divided into independent treatment effects because each pass changes the input graph of the next one. Formally, if $P$ denotes one cleanup pass, the observed sequence concerns

$$G_0,\quad G_1=P(G_0),\quad G_2=P(G_1),\ldots,$$

not repeatedly applying $P$ to the *same* fixed $G_0$. Thus $A(G_0)-A(G_2)$ contains a path-dependent interaction, not necessarily the sum of two isolated gains.

## What R8 resolved and what it did not

The prototype establishes three narrow facts: a completed legal incumbent can still contain profitable local structure; structural cleanup can expose further opportunities for subsequent passes; and a modest area gain can coexist with a small delay increase while preserving the target. It does **not** establish that factoring is broadly effective or that iteration is worth deploying on all functions. The research question becomes sharper: can a rewrite be driven by the **actual Boolean function of a bounded cone**, independent of the syntactic pattern in which it happens to appear? That is the transition to R8.1.

# Round 8.1: the central change of object — from syntax patterns to 4-leaf truth functions

## A cut is a function boundary, not a substring of the netlist

For a root gate $v$, a cut $C=\{\ell_1,\ldots,\ell_k\}$ is a set of upstream frontier signals that intercepts every backward path from $v$ to a primary source. A *feasible* cut has $k\le4$. After replacing the upstream cone behind that frontier by formal variables $z_1,\ldots,z_k$, the root is a Boolean function $h_{v,C}:\{0,1\}^k\rightarrow\{0,1\}$. Its truth mask is

$$M(v,C)=\sum_{s=0}^{2^k-1} h_{v,C}(s)2^s,
\qquad 0\le M<2^{2^k}\le2^{16}.$$

The maximum 16-bit mask is computationally cheap to enumerate. The mask is a *semantic bridge*: it forgets the particular sequence of AND, OR and NOT gates in the original cone while preserving its function on the cut inputs. This is a qualitatively different search space from identifying only a literal distributive or absorption pattern.

**Why exact equality is sufficient even with correlated leaves.** In a real circuit the leaf signals $(\ell_1(x),\ldots,\ell_k(x))$ need not realize all $2^k$ Boolean assignments. Nevertheless, if a candidate $\tilde h$ matches $h_{v,C}$ on **all** formal assignments, then for every primary input vector $x$,

$$\tilde h\bigl(\ell_1(x),\ldots,\ell_k(x)\bigr)
=h_{v,C}\bigl(\ell_1(x),\ldots,\ell_k(x)\bigr).$$

This proves local functional substitution unconditionally, without making any stochastic-independence assumption about the leaf signals. Equality on all formal assignments is often stronger than necessary when leaves are correlated, but is an easily checked sufficient test. It says *nothing by itself* about new graph cycles, other output uses, exact area or arrival times; those must be checked separately.

## The actual candidate families and mapping costs

The R8.1 family expands each small cut by several choices. One is Shannon decomposition along an ordering $\sigma$:

$$h(z_1,\ldots,z_k)
=\bigl(\neg z_{\sigma(1)}\land h_0\bigr)
 \lor\bigl(z_{\sigma(1)}\land h_1\bigr),$$

recursively reducing cofactors until they are constants. Other choices enumerate exact implicants of the positive truth mask, build an SOP, enumerate the complement mask and invert its SOP (a POS-like realization), and vary the greedy-cover policy. Every XOR-like or multiplexer-like intermediary must eventually be lowered to permitted AND2/OR2/NOT gates. These alternatives are *exact Boolean implementations*, not approximate learned surrogates.

In the frozen descendant `r84_cut.hpp`, `truth()` (lines approximately 132–150) recursively computes the bit mask with `AND`/`OR`/mask complement and throws if a path bypasses the cut frontier; `Env::sop()` (approximately 69–105) enumerates prime cubes for no more than four leaves; `Env::build_shannon()` (approximately 106–129) constructs a mapped decomposition; and `private_reclaim()` (approximately 164–177) accounts conservatively for the old cone by refusing to count multi-fanout predecessors as removable. The source lineage confirms that these are concrete implementations of the R8 family, although a frozen R10 header must not be mistaken for a byte-identical R8.1 executable.

Suppose $\widehat A_{\rm new}$ is the emitted cost of a candidate cone relative to the same mapped frontier, and $\widehat A_{\rm reclaim}$ is the conservative cost of private old gates expected to become dead. The local screening proxy is

$$\widehat{\Delta A}=\widehat A_{\rm new}-\widehat A_{\rm reclaim}.$$

A favorable local proxy merely justifies considering the candidate. Hash-consing may reuse gates that appear outside the cone; original gates may remain live because of other fanouts; and in-place rewriting can alter reachability. The final acceptance test is on a **finished live DAG**, not on this estimate. That distinction was already foreshadowed by Stage 1’s algebra/fanout example and is now encoded in the synthesizer.

## Required time is a feasibility screen, not a score

Let $R(y)$ initially equal the target delay for each output. On an unchanged DAG, backward propagation gives

$$R(u)=\min_{v:\,u\in\mathrm{fanin}(v)}\bigl(R(v)-d_{\operatorname{op}(v)}\bigr),$$

also taking the primary-output target if $u$ itself is an output. A candidate root with new arrival $T'(v)\le R(v)$ can be feasible under a fixed external boundary even if its arrival increases. For the Stage 1 running example, a signal that serves both as output and downstream fanin can have a tighter required time than its own output deadline. The old $R$ values are **not safe to reuse after arbitrary fanout restructuring**; the final full-DAG metric is authoritative.

A formal sufficient condition holds if the rest of the DAG retains its dependencies and gate delays and each new boundary root meets its original required arrival. Topological induction then shows that every unchanged successor meets its old required arrival and all output delays remain within target. But this lemma is not a universal proof for freely restructured graphs. Stage 2’s implementation combines local screening with a final completed-network feasibility check for exactly this reason.

## What R8.1 actually found: area and delay can pull in different directions

The first archived Stage 2 experimental period provides the clearest contrast. All variants below have 25 PASS and 25 target-met cases:

<div class="longtable">

@ \>

p(- 6) \* \>p(- 6) \* \>p(- 6) \* \>p(- 6) \* @

R8.1 policy, Stage 2 period 1

&

Charged area

&

Sum of output delays

&

Median synthesizer runtime (ms)

  
Prior R7.2 reference & 508,535 & 1,101 & approximately 32–35 in its own feedback  
`r81_strict` & 508,326 & 1,101 & 193.074  
`r81_sop` & 498,949 & 1,161 & 95.509  
`r81_shannon` & 498,568 & 1,158 & 95.287  
`r81_reverse` & **497,509** & **1,158** & 189.880  

</div>

The R7.2 runtime is listed only for context from **a separate feedback batch**, so its subtraction from the R8.1 medians is *not* a matched speedup/slowdown measurement. Inside the R8.1 batch, the policies themselves are comparable. The `reverse` policy saves 11,026 charged area units relative to the archived R7.2 area reference, at an increase of 57 in aggregate circuit delay. `strict` saves only 209 yet does not increase the aggregate delay. The former is not “better in every metric”; the latter is not “useless.”

On Stage 2 / case_005, `r81_reverse` yields area **106,770**, `r81_strict` **112,221**; on case_003 the corresponding areas are **15,207** and **19,494**. These are *actual per-case* manifestations of how candidate admission matters. Neither comparison establishes the hidden evaluator’s score, and sum of delays is descriptive rather than a universal quality utility.

## Decision after R8.1

R8.1 validates the central method hypothesis: bounded Boolean-function rewriting exposes substantially more area opportunities than sparse syntax patterns. But a policy that “takes every legal cheaper cone” can consume significant synthesis time and relax non-regression of individual delays as long as the target is still met. The next question is therefore not “does cut rewriting work?” It is **which search and acceptance objective should be used, and how much of the search should be done per instance?** R8.2 turns those choices into controlled alternatives.

# Round 8.2 and 8.2.1: choosing a point in a multi-dimensional engineering problem

## R8.2: area-first, slack-first and ADP-style rankings are different policies

The combinational function must remain exact in every mode; what changes is the ordering and acceptance of legal candidates. An area-oriented policy prioritizes $A(G)$ subject to timing feasibility. A more conservative policy can prefer preserving or reducing $D(G)$, even after the target is met. An internal area–delay-product proxy, $A(G)D(G)$, trades both by multiplying them. It is mathematically a well-defined search heuristic, but it is **not** the published course-score function and should never be presented as such.

For small perturbations,

$$\frac{\Delta(AD)}{AD}\approx\frac{\Delta A}{A}+\frac{\Delta D}{D}.$$

This explains why a candidate offering a small area saving can be rejected by an ADP objective when it increases delay enough. A weighted lexicographic or target-feasible objective can make the opposite decision. The hypotheses are genuinely different; they cannot be evaluated merely by renaming the same area total.

Round 8.2 added fast and dual-branch variants, slack-oriented and ADP choices, and different root sampling/traversal rules. In its own **Stage 2 period-one** records, all 25 cases passed and met target, but outcomes diverged:

| R8.2 Stage 2 policy |        Area | Delay sum | Median runtime (ms) |
|:--------------------|------------:|----------:|--------------------:|
| `r82_dual_area`     | **501,547** |     1,156 |             163.231 |
| `r82_fast_area`     |     503,313 |     1,137 |             163.812 |
| `r82_fast_slack`    |     506,296 |     1,109 |             156.450 |
| `r82_fast_adp`      |     508,380 | **1,101** |             154.480 |

The dual-area policy achieves lower area than fast-area on this bank; it does so at a greater total circuit delay. The ADP variant retains the original delay sum but gains comparatively little area. Thus *target feasibility* and *delay non-regression* induce different feasible choices. The precise optimal choice cannot be deduced from area or ADP alone without the official score and resource distribution.

The independent repeated period reports another area for some dual searches, consistent with wall-clock-dependent candidate trajectories. It is inappropriate to call two totals recorded on different invocations a perfectly stable deterministic cost function when a time gate can change which roots are reached.

<div class="tcolorbox">

**Decision after R8.2:** preserve multiple frozen comparators, rather than prematurely declaring a universal area/delay/runtime winner. Add explicit resource handling and then separate variability in the root-search process from the underlying Boolean opportunities.

</div>

## R8.2.1: program resource limits are not the same as circuit properties

The input format can specify a ninth-line RAM limit. The algorithm therefore must distinguish (i) a correctness-preserving compact alternative, (ii) deciding whether a BDD or truth-table representation is *admissible* under a conservative memory estimate, and (iii) the evaluator’s external memory supervision. The frozen `r821_resource.hpp` and R10.0 entry code parse both optional positive limits; the latter may attempt a compact exact solver or decline an estimated inadmissible BDD route instead of blindly using memory.

The R8.2.1 probe deliberately used a tiny exact-wire C solver as a control. One archived low-RAM experiment returned evaluator `MEMORY_LIMIT` at **9,000 KiB**, while a separate direct process monitor reported only **1,344 KiB** high-water resident memory for the tiny program. The two observations use different measurement layers. They expose a **measurement/interface discrepancy worth investigating**; they do not prove that the evaluator has a bug, reveal its monitoring internals, or establish a universal memory threshold. There are additional patched and clean evaluator probes, which must be identified by their exact run directory when cited.

The code can formally reject an obviously too-large representation *relative to its estimate*, but it cannot guarantee the evaluator will accept every low-memory execution. Likewise passing a small probe does not prove correctness for all 20-input instances. The lasting contribution of R8.2.1 is clearer resource accounting and honest limits on what a memory measurement certifies, not a new Boolean minimization method. Keep this branch proportionate in the Stage 2 paper; preserve the full detail here because it explains why “PASS” includes more than Boolean equivalence.

# Round 8.3: make the amount of search work explicit

## The problem hidden inside an elapsed-time cutoff

Cut rewriting is an *ordered search*. Let $r_1,\ldots,r_N$ be eligible roots and let $C(r_i,G)$ denote the work required to examine the cuts of root $r_i$ in the current mapped network. Under a wall-time limit $B$, the number of roots visited is not fixed. It depends on data structures, CPU load and the changing shape of $G$:

$$K(B,G,\mathrm{machine})=
\max\biggl\{k:\sum_{i=1}^{k}C(r_i,G)\lesssim B\biggr\}.$$

The expression is schematic, not a claim that runtime is a literal sum of independent root costs: caching, graph growth and periodic clock checks couple the terms. Its purpose is to show why the *same* wall allowance need not produce the same visited search set. Because accepted rewrites alter the subsequent graph, missing or gaining a root can produce different final area, even with the same source and input.

Round 8.3 introduces a deterministic **root-work quota** alongside an emergency wall guard. The former controls an algorithmic quantity (number of completed selected roots), while the latter guards end-to-end runtime. This does not produce deterministic total running time, because one root can contain many cuts and candidates; it does make one dimension of the search more reproducible. In the frozen `r84cut::rewrite`, `visited_roots` is checked against `work_roots` at a root boundary; a clock check is performed periodically. Any remaining unprocessed original nodes are copied to finish a legal graph. This last operation is essential: an optimization timeout is allowed to truncate extra research but not to leave an incomplete netlist.

## 9.2 A quota controls effort but also changes *which* root wins

The R8.3 Stage 2 period-one feedback compares a prior `r821_dual_area` with `r83_stable_dual`, `r83_dense_dual` and `r83_fast_area`. All four complete 25/25 cases and their delay targets, but differ materially:

| R8.3 comparison   |    Area | Delay sum | Median runtime (ms) |
|:------------------|--------:|----------:|--------------------:|
| `r821_dual_area`  | 493,922 |     1,169 |             131.044 |
| `r83_dense_dual`  | 497,885 |     1,169 |             126.208 |
| `r83_stable_dual` | 500,072 |     1,169 |              87.518 |
| `r83_fast_area`   | 502,717 |     1,137 |              58.628 |

These within-batch differences are descriptive tradeoffs, not clean estimates of one isolated code change. Stable work reduces some wall variability but can exclude useful roots that an earlier, more opportunistic schedule happened to visit. For example, on Stage 2 / case_003 the selected areas move from 15,318 (`r821_dual_area`) to 17,283 (`stable_dual`), whereas case_005 moves from 102,928 to 106,771. The numerical pattern does not prove that one root-ranking heuristic is universally optimal; it motivates examining **what was selected by the quota**.

<div class="tcolorbox">

**Decision after R8.3:** root-count stability alone is insufficient. A bounded search should spend its fixed work quota on promising roots, where “promising” must be defined by a proxy tied to removable live area and timing slack. That leads to R8.4.

</div>

# Round 8.4: priority ranking, topological traversal and the Top-Q distinction

## Why “rank 1,500, then visit the first 900” is not “visit the best 900”

A DAG can be rewritten safely in a topological pass because mapped predecessors are ready before their consumers. But ranking roots by potential benefit and *visiting them* are two separate operations. One historical scheme retained a high-ranked pool, then visited up to a quota in ascending topological order. The selected set can differ radically from the highest-scored $Q$ roots even though both schemes report the same nominal quota.

Let $s(v)$ be a root priority proxy, and $P_K$ be the best $K$ roots by that proxy. Then the historical policy selects the first $Q$ root IDs in $\mathrm{sort}_{\mathrm{topological}}(P_K)$, while a **Top-Q policy** first chooses $P_Q$ and *then* traverses that selected set topologically. They differ whenever relative topological position and rank disagree:

$$\mathrm{first}_{Q}\bigl(\mathrm{toposort}(P_K)\bigr)
\ne P_Q,\qquad Q<K.$$

The distinction matters because an early low-ID root may be less promising but can be reached before a higher-value later root. Conversely, the chosen root set affects structural opportunities created for downstream replacements. A ranking is only a heuristic; the exact payoff is measured after completing the network.

The frozen `r84_cut.hpp` defines a score whose principal terms are gate area and one-hop private predecessors:

$$s(v)=16a(v)+8\sum_{u\in\mathrm{fanin}(v)\atop u\text{ internal},\ \mathrm{use}(u)=1}a(u)
+\min\{8,\max(0,R(v)-T(v))\}.$$

This is a **selection surrogate**, not the true benefit of rewriting $v$. It approximates reclaimable private gates plus slack; it does not forecast which Boolean candidate will materialize. The root population is first ranked by this proxy, Top-Q membership is fixed where selected, and the actual rewrite remains topological. R8.4 also compares mixed quotas and pilot→focus allocation for the two branch families.

## The R8.4 controlled outcomes resist an easy ranking story

In the first R8.4 Stage 2 period, with 25 PASS/target cases throughout:

| Strategy            |        Area | Delay sum | Median runtime (ms) |
|:--------------------|------------:|----------:|--------------------:|
| `r84_topology_dual` | **501,063** |     1,169 |             206.012 |
| `r84_topq_dual`     |     501,124 |     1,170 |             182.445 |
| `r84_topq_dense`    |     500,027 |     1,170 |             191.486 |
| `r84_adaptive_dual` |     502,266 |     1,172 |             213.674 |

`topq_dense` improves area relative to both `topology_dual` and `topq_dual` in that first invocation, but the second period changes the ranking of some alternatives. Even the simpler `topology_dual`→`topq_dual` comparison illustrates why a theoretically more “faithful” priority ranking does not automatically improve the finished circuit: area moves from 501,063 to 501,124, and delay sum from 1,169 to 1,170. On case_003, by contrast, Top-Q lowers area from 17,283 to 16,213; on case_005, it increases area from 107,754 to 109,084. The mixed population explains the small aggregate reversal.

This is **not** evidence against ranking per se. It is evidence that the priority formula, downstream sharing, order of accepted transformations and finite root quota interact. The right next experiment is to control the scheduling of the **two candidate-generation branches**, not to assume a single root-score formula solves every case.

<div class="tcolorbox">

**Decision after R8.4:** retain Top-Q and dense variants as controlled choices, but study whether SOP and Shannon should be ordered or budgeted differently. R8.5 takes that step.

</div>

# Round 8.5: branch-order search and the confounding of additional work with additional time

## Two passes may be compositional, but comparison must hold the input fixed

The cut optimizer can generate SOP-like and Shannon-like candidates. Two possible full-pass orders are $H\rightarrow P$ (Shannon then SOP) and $P\rightarrow H$ (SOP then Shannon). If the second pass operates on the output of the first, the maps need not commute:

$$P(H(G))\ne H(P(G)).$$

The equality of the *Boolean outputs* does not make their gate DAGs identical. The first pass changes cut frontiers, hashing opportunities, arrival times and which private gates survive. A second pass may discover something newly visible, or lose a formerly available structural match. There is no general theorem that SOP-first always wins.

In R8.5’s first Stage 2 run, `r85_shannon_first`, `r85_sop_first` and `r84_topq_dual` all yielded **area 497,785**, delay **1,170**, with medians 92.541, 90.418 and 93.720 ms respectively. The tie is **conditional on these runs**: it does not prove the order commutes on all graphs. The `r85_budget_reclaim` configuration yielded the stronger **494,999** at the same delay, but it modified not only the traversal order: unused time could be reallocated to the next branch, changing its potential work as well.

## Why the R8.5 result cannot identify its own mechanism

If policy A changes both the SOP root quota and time allowance, an improvement in output area can result from either factor or their interaction. Let $A_{qr}$ denote area with root-quota treatment $q\in\{0,1\}$ and time-reclaim treatment $r\in\{0,1\}$. Observing just $A_{00}$ and $A_{11}$ identifies only the **joint intervention**, not the partial effects $A_{10}-A_{00}$ and $A_{01}-A_{00}$.

The correct response is not to label the total area difference “time reclaim savings.” It is to conduct the missing two arms and analyze the interaction. R8.6 is therefore a methodological improvement in experiment design as much as an algorithmic experiment.

# Round 8.6: the decisive 2×2 root-allocation experiment

## Freeze everything except the proposed explanatory factors

R8.6 is unusually strong evidence because the frozen implementation explicitly documents the experimental invariants: same initial incumbent, same ranked roots, same library costs, same whole-search deadline and same branch order. Only branch-specific root quotas and nominal wall allowance differ. Its source-level dispatch, retained in the R10.0 main function around the `UFUG_R86_POLICY` branch, runs a **Shannon pass followed by an SOP pass** against the *same frozen base* for each policy. It then selects the best completed result. This is not the same as asserting that the two policies are always composed sequentially on each other’s output.

The unmodified basic root cap is typically 900, or 600 when a shorter (but still admissible) time limit and wide output dimension trigger the documented guard. Under the `extra_sop` treatment the SOP branch gets up to 300 additional roots, subject to a cap of 1,500; `reverse_allocation` gives the extra roots to Shannon instead. The time-reclaim flag changes the *maximum allowance* offered to the later branch if unused global budget remains. The two-pass search budget is bounded by $\min(360\text{ ms},0.15L)$, with additional whole-program reserve checks. Neither the nominal allowance nor the root cap is a guarantee that a pass actually visits that many roots or spends that many milliseconds.

Four factorial arms are therefore defined:

- $A_{00}$: baseline root count, no time reclaim;

- $A_{10}$: extra SOP root count, no reclaim;

- $A_{01}$: baseline root count, with reclaim;

- $A_{11}$: extra SOP roots and reclaim.

Define *savings* $S_{qr}=A_{00}-A_{qr}$. The realized interaction on each case/period is

$$I=S_{11}-S_{10}-S_{01}
=A_{10}+A_{01}-A_{11}-A_{00}.$$

A zero interaction on the observed data means the combined treatment produced precisely the sum of the separately observed savings **on those cases and periods**; it does not prove a separable response function for arbitrary unseen truth tables.

## Direct raw ZIP verification of the factorial outcome

The direct `Round8.6_Feedback_20261122_180727_218078298.zip` contains two periods of official evaluator CSVs for both banks and all four factorial arms plus a reverse-allocation control. Independently re-parsing those files gives the following **50-case** area totals, each period separately reproducing the same totals:

<div class="longtable">

@ \>

p(- 10) \* \>p(- 10) \* \>p(- 10) \* \>p(- 10) \* \>p(- 10) \* \>p(- 10) \* @

Treatment

&

Stage 1 area

&

Stage 2 area

&

Combined 50-case area

&

Saved vs baseline

&

Cases improved

  
$A_{00}$: baseline & 526,193 & 497,785 & **1,023,978** & 0 & 0  
$A_{01}$: time reclaim only & 526,193 & 497,785 & **1,023,978** & **0** & 0  
$A_{10}$: extra SOP roots only & 526,135 & 494,999 & **1,021,134** & **2,844** & 10  
$A_{11}$: both factors & 526,135 & 494,999 & **1,021,134** & **2,844** & 10  
Extra roots to Shannon instead & 526,187 & 497,771 & **1,023,958** & **20** & 5  

</div>

All reported cases passed and met their targets; no case saw a larger total output delay relative to the factorial baseline. The independently reconstructed `quota_factorial.csv` also reports **zero observed case-period interaction** for the complete 100 case-period pairs. The 2,844 savings break into **58** on Stage 1 and **2,786** on Stage 2. Giving comparable extra roots to Shannon yields only 20 total savings, not 2,844.

This is far more informative than saying “the reclaim optimization worked.” In the observed released cases, **increased SOP work quota is the explanatory treatment**, while additional nominal time by itself produced no area change. The results still admit several mechanistic possibilities: the SOP pass may have had more profitable root functions, may have reached later ranked roots that Shannon did not, or its candidate realization may exploit this particular gate-price distribution. The factorial design identifies the *policy factor* that mattered in the experiment, not the unique gate-level reason for every improvement.

## Visual test of the factorial hypothesis

The factorial plot in Figure <a href="#fig:r86-factorial" data-reference-type="ref" data-reference="fig:r86-factorial">1</a> is a visual rendering of the **two separately archived periods**, not a regression fitted to five points. The equality of the two marks in every treatment is an observed repeat agreement, not an error bar with zero population variance. The four arms give

$$S_{00}=0,\quad S_{01}=0,\quad S_{10}=2844,\quad S_{11}=2844,
\qquad I=S_{11}-S_{10}-S_{01}+S_{00}=0.$$

The reverse-allocation control produces only 20 units of savings. That difference is larger than a mere choice of plot color: it rules out the simplistic explanation that the tested 2,844-unit saving arose from *any* generic root-count increase. The archive supports the narrower finding that the additional **SOP opportunity set** was valuable on these particular truth tables. It does not reveal the exact accepted cut boundary for each winning case.

<figure id="fig:r86-factorial">
<embed src="figures/04_r86_factorial.pdf" style="width:99.0%" />
<figcaption>R8.6 controlled quota allocation across 50 released cases. Points mark the two evaluator periods; identical area totals overlap in each arm. Each treatment is compared to the within-archive factorial baseline. One factor changes SOP-root quota and the other changes allowed time; the reverse-allocation treatment instead enlarges the Shannon search. This is a controlled configuration comparison, not a statement about arbitrary unseen functions.</figcaption>
</figure>

## The important negative and the stopping decision

The reverse-allocation control is an essential counterfactual. If “more root visits are always better” were the adequate explanation, giving the extra quota to Shannon should have produced a similar area reduction. It did not. The result supports a targeted claim: **additional quota was valuable when given to the SOP branch of this architecture on the observed 50 cases**. It does not establish a general theorem that SOP is better than Shannon, nor guarantee monotonic savings at still larger quotas.

Runtime remains noisy. In the direct feedback, the Stage 2 median for `r86_baseline` is 102.431 ms and for `r86_extra_sop` 107.818 ms in one period; `time_reclaim` shows 95.163 ms despite identical circuit quality. These differences are not a stable law from one invocation. A 2,844-area saving has an observed search cost and should be followed by a separate robustness test, not promoted solely from the public-bank sum.

<div class="tcolorbox">

**Decision after R8.6:** default to the extra-SOP-root family as the promising area-oriented policy; test it on independently generated functions and explicit short-budget stress cases before calling it production-safe. That is the purpose of R8.7.

</div>

# Round 8.7: published-case improvement is not enough to justify a universal production claim

## What the public cases can and cannot tell us

By the end of R8.6, repeated tuning on the released 50 cases had produced a clear candidate. The danger is no longer only a broken Boolean identity; the danger is **policy overfitting**. A root allocation chosen after inspecting a fixed finite set may be tailored to its mix of dense/sparse/cofactor/multi-output functions. Even if every recorded case passes, it does not follow that the policy improves other function families or adverse runtime limits.

R8.7 therefore freezes the candidate policies and evaluates new deterministic generated functions as a separately named data family. The feedback’s records **36 functions**, **two runs** and **three candidate policies**, plus source and executable digests. The generated cases are reproducible and can test the behavior of classes of Boolean functions that are underrepresented in the released set. They are not the evaluator’s hidden cases, and a seed used for later tuning is no longer a clean unseen holdout for subsequent configurations.

## The findings were not a universal extra-SOP victory

The generated-family totals for the three frozen R8.7 policies were tied in the archived comparison. In contrast, the 50 released cases retained the R8.6 extra-SOP advantage. This does **not** refute the public-case gains: it shows that a nonzero improvement on one distribution is not equivalent to broad improvement on all generated families. Most likely, the particular local opportunities and cost profiles of those constructed functions did not exercise the extra SOP work in a beneficial way. That mechanism is plausible, not uniquely established from aggregate output alone.

The tight-budget stress fixtures were an equally important negative result. Some external wall measurements on stress 001/002 ran beyond 100 ms for both baseline and extra-SOP variants, even when particular invocations of the course evaluator reported PASS. An evaluator’s reported synthesis runtime, a supervisory wall stopwatch and process peak memory are **not identical instruments**. It is wrong to claim either that every run violates the official limit or that public PASS makes the implementation hard-real-time safe. The evidence supports a narrower statement: *some execution paths under adverse caps deserve an early, structurally exact bypass or another conservative feasibility mechanism.*

## The next decision is a deployment policy, not a mathematical retraction

The hypothesis that extra-SOP roots create additional realizable area opportunities is supported for the released 50-case bank, and those opportunities were later exploited by R9/R10. But it would be irresponsible to commit a short-limit program to additional cut search before a safe candidate is available. R9.0 retains the area-oriented policy when resources permit while addressing fast production of exact structured circuits in the special short-budget path. **The R8.7 result constrains the domain of the claim; it does not erase the optimization.**

# Round 9.0: a runtime-first fallback and an exact early structured-function bypass

## Why another “faster heuristic” would not solve the observed risk

The R8.7 stress discussion highlighted the end-to-end work incurred before the ordinary BDD and mapping portfolio can emit any legal output. For certain large tables with very short budgets, a function may have a simple *semantic* form even though constructing a general-purpose shared representation is expensive. Examples include constants, single literals/negated literals and affine functions over $\mathrm{GF}(2)$.

Instead of rushing every routine, R9.0 introduces a logically separate **streaming recognition path**: while reading the full input, maintain sufficient consistency state to tell whether each output belongs to one of those restricted families. If a complete exact witness exists, construct it immediately using the three legal gate types and check its actual area and timing. If the witness does not exist or fails the target, return to the ordinary compiler; **never silently approximate the truth table**.

## The actual implementation and its correctness boundary

The frozen `r90_stream.hpp` defines `StreamProbe`. It maintains candidate bitsets for constants and literals, plus a per-output affine mask and validity flag. For an affine Boolean output,

$$f(x)=c\oplus\bigoplus_{i=1}^{n}\alpha_i x_i,
\qquad \alpha_i\in\{0,1\},$$

$c=f(0)$ and $\alpha_i=f(e_i)\oplus f(0)$, where $e_i$ is the $i$th unit-vector input. Those $n+1$ rows *identify* an affine candidate, but do **not** prove that an arbitrary truth table is affine. The streaming verifier checks every other row against the candidate parity relation. Thus the final acceptance test is an exhaustive comparison against **all** $2^n$ rows as they are read, not extrapolation from a handful of unit vectors.

For literals and constants, the running bitset eliminates any candidate inconsistent with a newly seen row. If all outputs are exactly implementable as simple signals or affine combinations, the builder lowers XORs using only supported gates, e.g.

$$u\oplus v=(u\lor v)\land\neg(u\land v),$$

shares identical subexpressions where possible, builds a legal DAG and checks the requested target delay. The code chooses an arrival-aware combination order for multiple XOR terms. The emitter still pays for every AND2, OR2 and NOT, including inversions.

The entry code in `synth.cpp` restricts this exact bypass to **$n\ge18$** and **$0<L\le250$ ms** and does not skip reading the full input: it first observes all $2^n$ truth rows, then may emit the verified exact candidate. The dimension threshold is an **engineering dispatch**, not a changed contract; the legal problem remains up to 20 inputs. The normal released cases follow the general search path, with R8.6 extra-SOP selected as the default area-oriented policy when eligible.

## What the R9.0 experiments support

In a selected tight-budget stress 001 comparison, the evaluator-reported runtime for the original and new paths was **93.927 ms versus 31.581 ms**, with both marked PASS in that controlled invocation. This supports the value of the early structured path on that particular fixture. It does not prove the same benefit on unstructured random truth tables or eliminate the risk of input-reading overhead. In other stress invocations, external wall monitoring still exceeded nominal limits. The two measurement types must remain distinct.

The archived R9.0 frozen reference on the two published banks has **50/50 PASS, 50/50 target-met**, combined charged area **1,021,134** (526,135 on Stage 1 and 494,999 on Stage 2) and sum of circuit delays **2,382**. These are descriptive engineering totals, not a claimed grade. Round 9.0 is a useful *runtime-first fallback*: it preserves R8.6’s promising area policy in normal circumstances while adding a restricted exact path for a particularly risky class of short-budget inputs.

## What remained unsolved

The most valuable late-stage question was no longer whether we could change the initial representation radically. It was whether the *finished* R9.0 network could benefit from one additional, strictly controlled local pass—perhaps a library of precomputed small Boolean realizations, or simply another SOP/Shannon pass—without jeopardizing feasibility. R9.1 performs exactly this comparison instead of altering multiple earlier pipeline stages simultaneously.

# Round 9.1: precomputed Boolean template library versus another ordinary pass

## A library is a different search mechanism, not necessarily a more powerful one

A truth-signature-indexed library pre-enumerates recipes for functions on 2, 3 and 4 leaves. `r91_library.hpp` stores a bounded number of recipes per complete signature, and explicitly includes associative chains, balanced four-input combinations, MUX-like forms, XOR-like forms, majority-like forms and optional output complementation. The frozen source retains **at most 32 recipes per signature**, in a deterministic generation order. This matters: the library is not an exhaustive catalogue of minimum-area realizations under *arbitrary* case-specific prices and arrival times. A recipe that is compact in generic gates need not be cheapest when a particular OR2 is expensive or when useful inversions are already live elsewhere.

A library lookup is allowed only after computing the exact cut mask. Matching that mask guarantees the local Boolean function can be realized by the recipe; actual emitted mapping and complete network cost still depend on context. A signature match by itself does not grant a free physical inverter or bypass the end-to-end timing check.

As a control, R9.1 also runs the already implemented `r84cut::rewrite` a second time in an SOP-only or Shannon-only mode. This is a valuable experimental design: it asks whether the new representation itself earns its implementation complexity, compared with spending a similar additional budget on an existing conventional method.

## Direct paired outcome: more discovered successes, less realized area benefit

The R9.1 native feedback supplies two periods on both banks. Each candidate passed all 50 and met all delay targets. The first and second periods agree in area values. Relative to frozen R9.0 (area 1,021,134):

<div class="longtable">

@ \>

p(- 10) \* \>p(- 10) \* \>p(- 10) \* \>p(- 10) \* \>p(- 10) \* \>p(- 10) \* @

Postpass policy

&

-case total area

&

Total area saved

&

Improved cases

&

Sum of delays

&

Delay increases

  
R9.0 frozen / off & 1,021,134 & 0 & 0 & 2,382 & —  
Signature-indexed library & **1,020,471** & **663** & **15** & 2,384 & 2 cases  
Repeat Shannon & **1,020,255** & **879** & **5** & 2,381 & 0 cases  
**Repeat SOP** & **1,019,547** & **1,587** & **8** & **2,382** & **0 cases**  

</div>

These numbers are derived from matched per-case source CSVs, not from eyeballing a plot. They show why counting successful candidates is the wrong performance target. Library rewriting helps more individual cases than repeat-SOP, but its gains are small in magnitude and it increases the delay of two completed networks (while still meeting their own targets). Repeat-SOP helps fewer cases yet saves **more than twice** the weighted area, with no per-case delay increase on the observed set. Repeat Shannon offers a distinct, smaller benefit and a one-unit aggregate delay improvement.

The four-case lockbox study in the archive found no library area win. Because its cases and construction are narrowly defined, it should not be described as definitive proof that indexed libraries are useless. The appropriate conclusion is narrower and stronger: **under the measured budget and gate library, there is no compelling evidence to replace a simple repeat-SOP step with this particular bounded template library.**

## Why hit count and saved area answer different questions

A library lookup may recognize many reusable Boolean functions, but each winning candidate replaces a different set of *live physical gates* and interacts with different fanout. Counting the number of strict improvements gives

$$H(\pi)=\sum_{i=1}^{50}\mathbf{1}\{A_i(\pi)<A_i(\text{off})\},$$

whereas total measured saving is

$$S(\pi)=\sum_{i=1}^{50}\bigl(A_i(\text{off})-A_i(\pi)\bigr).$$

Neither statistic determines the other: the first discards magnitude and the second can be dominated by a handful of expensive inputs. In the native R9.1 feedback the library wins **15** cases but saves only **663** area units; repeat-SOP wins **8** but saves **1,587**; repeat-Shannon wins **5** and saves **879**. Figure <a href="#fig:r91-freq" data-reference-type="ref" data-reference="fig:r91-freq">2</a> plots the two statistics simultaneously, exposing why adopting the template library simply because it fired more often would be a poor interpretation. This comparison is valid for the same control batch; it does **not** establish that repeating SOP will always outperform an indexed library.

<figure id="fig:r91-freq">
<embed src="figures/05_r91_frequency_vs_magnitude.pdf" style="width:90.0%" />
<figcaption>R9.1 policy comparison on both released case banks, evaluator period 1, each relative to the same frozen off control. More cases improved does not imply more area saved.</figcaption>
</figure>

## How to read the runtime cost correctly

A repeat pass performs real additional search. On the Stage 2 bank in the first R9.1 period, medians were approximately **104.183 ms** for R9.0, **116.551 ms** for library, **117.559 ms** for repeat-SOP and **114.906 ms** for repeat Shannon. These are within-experiment descriptive medians. They do not establish the precise deadline risk on all inputs, but they show that area improvement has a measurable computational price. That price must be restricted by a scheduling guard, rather than assuming the full final-search allowance is always safe.

<div class="tcolorbox">

**Decision after R9.1:** choose repeat-SOP as the final experimental postpass. Do not enable the indexed library by default. The next task is a controlled production freeze: verify that the default actually runs without a special environment variable and that disabling the pass reproduces the original R9.0 behavior.

</div>

# Round 10.0: what was actually frozen, and why it is a defensible default

## The source-level policy is more specific than “use SOP twice”

The final `synth.cpp` first runs the inherited exact construction and its bounded R8.6 extra-SOP policy where eligible, retaining a validated incumbent. The extra **R9.1-derived** postpass is then admitted only under explicit conditions. The current frozen implementation (near lines 1841–1895) reveals the following policy contract:

1.  `UFUG_R91_POLICY` defaults to **`repeat_sop`**, not `library` and not `off`.

2.  The postpass is eligible only if the instance runtime limit is at least **1,000 ms**, a valid incumbent exists, and its delay already meets target.

3.  Let $t_{\rm used}$ be time since program launch. The allowable postpass budget is $$B_{\rm post}=\min\{90\text{ ms},\ 0.06L,\ 0.82L-t_{\rm used}\}.$$ If this is below **8 ms**, no postpass is attempted.

4.  The normal root cap is **160**, with the experimental override constrained to 20–400. The ordinary `repeat_sop` path invokes `r84cut::rewrite` in SOP-only mode using `priority_topq` and the specified cap. Library and repeat-Shannon exist in source for controlled experiments only.

5.  The resulting graph is rebuilt and remeasured. It replaces the incumbent **only if** it is structurally valid, remains within target and has **strictly smaller entire-network charged area**.

6.  Otherwise the original incumbent remains unchanged. The short-limit R9.0 exact streaming path is a separate earlier dispatch and does not pay for this optional postpass.

The 82% launch budget reserve is a heuristic, not an operating-system guaranteed preemption. The 90-ms maximum is an upper allowance to the extra pass; it is not an assertion that the whole program takes 90 ms or that every root visit completes in constant time. In particular, `work_roots=160` is checked only between completed roots. The cutoff can affect the final network, which explains why a frozen source need not emit byte-identical netlists in separate wall-clock environments.

## Six-configuration freeze comparison

The R10.0 native feedback evaluates frozen R9.0, the R9.1 explicit SOP branch, R10.0 `off`, R10.0 `repeat_sop` explicitly requested, R10.0 default, and the submitted copy of R10.0 default, in **two periods** on **both public banks**. This is the correct unit for verifying the release choice. In each native period:

<div class="longtable">

@ \>

p(- 8) \* \>p(- 8) \* \>p(- 8) \* \>p(- 8) \* \>p(- 8) \* @

Candidate

&

Complete cases

&

Target-met

&

Total Area

&

Total circuit Delay

  
Frozen R9.0 & 50/50 & 50/50 & 1,021,134 & 2,382  
R10.0 postpass `off` & 50/50 & 50/50 & 1,021,134 & 2,382  
R9.1 explicit repeat-SOP & 50/50 & 50/50 & 1,019,547 & 2,382  
R10.0 explicit repeat-SOP & 50/50 & 50/50 & 1,019,547 & 2,382  
**R10.0 default** & **50/50** & **50/50** & **1,019,547** & **2,382**  
R10.0 submission default & 50/50 & 50/50 & 1,019,547 & 2,382  

</div>

The `off` arm restoring the R9.0 area/delay is an important **negative control**. The explicit-vs-default comparison establishes the chosen behavior under the evaluation setup; the submission-vs-research comparison checks packaging consistency. The frozen R10.0 source translation unit and the copy used for the reproducibility study have the same complete SHA-256 `8c863f1a1c9555ae571948a0424c25642c29c9a9f98f1f3e5f193c6b20f5b15d`.

## Only eight cases drive the 1,587-area improvement

Per-case, frozen R10.0 improves **8 out of 50** released instances and ties **42 out of 50** relative to R9.0, with **no area regressions** and **no per-case delay changes** in both native periods. The exact improvement cases and charged-area savings are:

| Bank / case   | Area saved |
|:--------------|-----------:|
| Stage 1 / 010 |        298 |
| Stage 1 / 012 |        250 |
| Stage 1 / 016 |          5 |
| Stage 2 / 003 |        150 |
| Stage 2 / 005 |    **752** |
| Stage 2 / 012 |          2 |
| Stage 2 / 023 |        125 |
| Stage 2 / 024 |          5 |
| **Combined**  |  **1,587** |

Stage 2 / 005 contributes **752/1,587 = 47.39%** of the observed saving. This concentration matters in two ways. First, median improvement per case is zero, so a statement such as “the optimizer improves the typical case by 0.155%” is false. The 0.155% is a *weighted area-total comparison*, not a typical-instance outcome. Second, one or two case-sensitive opportunities could dominate future aggregate totals as well. This does not invalidate the improvement, but it makes per-case detail and holdout/generalization discussion indispensable.

The reduction from 1,021,134 to 1,019,547 is about **0.1554%** relative to the R9.0 aggregate; it is deliberately modest. The value of this last round lies in a *verified strict-improvement postpass* plus preserved target feasibility and rollback—not in claiming a radical new Boolean synthesis theory.

## 16.3a What the *size distribution* adds to the R10.0 summary

The eight improvements are not close in magnitude. Their exact contributions are **752, 298, 250, 150, 125, 5, 5, and 2** (sum 1,587), in descending order. Thus a single Stage 2 case supplies **47.39%** of the incremental gain; the five largest supply **1,575 of 1,587**, or **99.24%**. The three smallest wins total only 12 units. They should not be deleted from the record merely because they are small: they verify that the optimization is not logically limited to large step changes, but neither do they justify characterizing the method as a broadly effective optimization on every input.

A measure of the concentration is

$$C_k=\frac{\sum_{j=1}^{k}g_{(j)}}{\sum_{j=1}^{8}g_{(j)}},
\qquad g_{(1)}\ge\cdots\ge g_{(8)}>0,$$

with $C_1=0.4739$ and $C_5=0.9924$. These are descriptive finite-benchmark statistics, not inferred population probabilities. Figure <a href="#fig:r100-sparse" data-reference-type="ref" data-reference="fig:r100-sparse">3</a> uses exact area units so the 2-unit and 5-unit changes remain legible instead of disappearing in a million-unit total.

<figure id="fig:r100-sparse">
<embed src="figures/06_r100_sparse_case_gains.pdf" style="width:98.0%" />
<figcaption>R10.0 final default versus R9.0 frozen in the directly decoded first-period official feedback. All 42 other cases have zero area change, no area regression is observed, and circuit delays are unchanged. S1/S2 designate the two case banks, not two algorithms.</figcaption>
</figure>

## The runtime tradeoff is not monotonically favorable

The direct feedback shows different effects by case and run order. Comparing the geometric per-case runtime ratios for R10.0 to R9.0 on the native pair gives approximately **0.961** in one period and **1.075** in the reverse period. A value below 1 means the R10 candidate was geometrically faster on the observed paired cases despite performing nominally more search; a value above 1 means it was slower. Runtime scheduling, OS contention and a clock-gated portfolio all contribute variability. Without a controlled trace of every candidate’s clock gate, neither number can be generalized as “the SOP postpass is always 3.9% faster” or “always 7.5% slower.”

The source establishes a reserve rule and fallback; the feedback establishes released-case validity and observed tradeoffs. Neither constitutes a formal upper bound on all $T_{\rm synth}$ or RAM on hidden instances. This difference between *observed successful deployability* and *proven bounded runtime* must remain visible in the final project narrative.

<div class="tcolorbox">

**Decision after R10.0:** freeze the complete default and its source hash. Retain R9.0 as the runtime-first comparator/fallback. Do not promote speculative postpass variants without showing an equal-or-better outcome under comparable controls.

</div>

# Round 10.1: a reasonable runtime hypothesis that was not supported by the quality evidence

## The question: can a smaller postpass recover the useful part of a concentrated gain?

Because only eight cases benefit from the repeat-SOP pass, it is tempting to reduce its root cap or nominal allowance and hope to preserve almost all area savings with less synthesis time. This is a sensible *research question*. It is not yet a justified optimization: profitable roots might occur late in the ranked set, and one expensive case may dominate the aggregate payoff. The root cap is a search-space selection rule, not simply a linear throttle on CPU milliseconds.

R10.1 keeps the frozen R10.0 comparator and tests a default identity, root caps **80** and **40**, and an allowance of **45 ms**. The source also retains a trial submission control. Native feedback again covers 50 cases in two periods; all variants pass all released cases and meet their targets.

## Recomputed native results

<div class="longtable">

@ \>

p(- 8) \* \>p(- 8) \* \>p(- 8) \* \>p(- 8) \* \>p(- 8) \* @

Policy

&

Total Area

&

Area *worse* than R10.0

&

Circuit delay difference

&

Cases that lose area vs frozen R10

  
R10.0 frozen & **1,019,547** & 0 & 0 & 0  
R10.1 default identity & 1,019,547 & 0 & 0 & 0  
Root cap 80 & 1,020,149 & **+602** & 0 & 6  
Root cap 40 & 1,020,555 & **+1,008** & 0 & 6  
Nominal budget 45 ms & 1,019,788 & **+241** & 0 & 1  

</div>

The two feedback periods agree on these area totals and number of regressing cases. On the Stage 2 bank, the 45-ms limit loses 241 area units on a single case. Root cap 40 loses 352 area units across two Stage 1 cases and 656 across four Stage 2 cases. Cap 80 loses 212 and 390 respectively. No circuit-delay benefit compensates for these losses.

Measured median runtime also does not offer a clean cross-case dominance result. Shrinking the nominal cap changes some observed medians in either direction depending on the bank and repeat, and the amount of actual local work may already be below the earlier allowance. A smaller *ceiling* is not equivalent to a demonstrated reduced cost on every case. This is precisely the danger that R8.3–R8.6 taught us to distinguish.

<div class="tcolorbox">

**Decision after R10.1: No-Go.** Preserve R10.0 as final. This negative experiment does not prove 160 roots or a 90-ms ceiling globally optimal. It establishes that **these tested reductions did not retain the observed released-case benefit or show a sufficiently robust compensation in runtime**. Having a defensible stopping decision is part of the research, not an embarrassment to hide.

</div>

# 18. The official cross-stage comparison: three *different* questions, not one misleading scoreboard

## Why these three programs must be separated

The final assignment asks for the *actually submitted* Stage 1 method and the proposed Stage 2 method on **both released banks**. We therefore treat **Z1** (Zeyun DU’s submitted Stage 1 implementation) versus **S100** (the frozen R10.0 Stage 2 implementation) as the *officially relevant method comparison*. Independently, **J51** is Jincan LI’s frozen Stage 1 R5.1 research implementation, a technically important alternate research line whose own trial log and R6 extensions contributed the ideas and implementation lineage underlying Stage 2. Treating J51 as non-existent because it was not administratively submitted would falsify the history; treating its output as the submitted Stage 1 method would falsify the project contract.

A new same-directory, same-evaluator study uses an interleaved/reversed order in **two periods**, over both 25-case banks, running all three source-frozen methods: **2 periods × 2 banks × 25 cases × 3 programs = 300 case-program invocations**. The input SHA-256 and source fingerprints are recorded in the reproduction bundle; Z1, J51 and S100 use **different source hashes**, not labels attached to the same executable. The table below is the direct result of `06_reproducibility/matched_batch/stage{1,2}_run{1,2}_{Z1,J51,S100}.csv` and independently cross-checked against `02_analysis/matched_summary.csv`.

<div class="longtable">

@ \>

p(- 12) \* \>

p(- 12) \* \>p(- 12) \* \>p(- 12) \* \>p(- 12) \* \>p(- 12) \* \>p(- 12) \* @

Bank / repeat

&

Method

&

PASS

&

Target-met

&

**Area on PASS rows**

&

**Delay on PASS rows**

&

Median synthesis time (ms)

  
Stage 1 / 1 & Z1 & 25/25 & 25/25 & 589,023 & 1,271 & 605.748  
Stage 1 / 1 & J51 & 25/25 & 25/25 & 529,014 & 1,167 & 61.360  
Stage 1 / 1 & S100 & 25/25 & 25/25 & **525,582** & 1,212 & 193.699  
Stage 2 / 1 & Z1 & 25/25 & 25/25 & 555,221 & 1,128 & 603.776  
Stage 2 / 1 & J51 & **24/25** & **24/25** & 506,754 & 1,065 & 36.929  
Stage 2 / 1 & S100 & 25/25 & 25/25 & **493,965** & 1,170 & 130.707  
Stage 1 / 2 & Z1 & 25/25 & 25/25 & 589,023 & 1,271 & 609.505  
Stage 1 / 2 & J51 & 25/25 & 25/25 & 529,014 & 1,167 & 51.627  
Stage 1 / 2 & S100 & 25/25 & 25/25 & **525,677** & 1,212 & 220.532  
Stage 2 / 2 & Z1 & 25/25 & 25/25 & 556,168 & 1,128 & 604.088  
Stage 2 / 2 & J51 & **24/25** & **24/25** & 506,754 & 1,065 & 36.835  
Stage 2 / 2 & S100 & 25/25 & 25/25 & **494,206** & 1,170 & 123.591  

</div>

**Interpret the denominator, not just the total.** J51’s 506,754 on the second bank covers only **24 passing cases**; it is *not* a 25-case total and cannot be placed in a simple 50-case ranking beside two 50/50-pass methods. The failure is **Stage 2 / case_016** under its short runtime cap, and the observed low median for the 24 successes cannot excuse an invalid result on the excluded case. The default Z1 and S100 have 50/50 PASS and 50/50 target-met in both periods. Their successful-case sums, unlike J51’s, cover identical complete case sets.

In repeat 1, the legitimate Z1–S100 total-area contrast is

$$A_{\mathrm{Z1}}=589{,}023+555{,}221=1{,}144{,}244,
\quad A_{\mathrm{S100}}=525{,}582+493{,}965=1{,}019{,}547,$$

$$A_{\mathrm{Z1}}-A_{\mathrm{S100}}=124{,}697,
\qquad \frac{124{,}697}{1{,}144{,}244}\approx 10.90\%.$$

In repeat 2, the respective sums are **1,145,191 and 1,019,883**, a **125,308** unit difference. These improvements are strong *released-case aggregate* results. The time medians differ substantially, but they represent a different cost dimension, so no single scalar combined winner is asserted without an official utility formula or explicit constraints.

## The key reversal: a lower weighted total despite losing more individual cases

The first period contains an instructive ranking reversal. Relative to Z1, S100 has **lower area on 18 of 50 individual cases and higher area on 32**, with **zero ties**. The Stage 1 split is 9 wins versus 16 losses; the Stage 2 split is also 9 versus 16. Yet S100 saves 124,697 area units across those 50 cases. There is no contradiction:

$$\sum_{i=1}^{50}\bigl(A_i(\mathrm{S100})-A_i(\mathrm{Z1})\bigr)
= \sum_{i:\Delta_i<0}\Delta_i+\sum_{i:\Delta_i>0}\Delta_i,
\quad\Delta_i=A_i(\mathrm{S100})-A_i(\mathrm{Z1}).$$

**Magnitude**, not the sign count, determines this sum. The median relative change across the 50 cases is actually **+3.69%** (S100 area worse for the median case). This fact must accompany the aggregate improvement, not be hidden behind it. Examples make the point concrete:

- **Stage 2 / 005:** Z1 emits area **142,405**, delay **40**. S100 emits area **102,889**, delay **68**. Area improves by **39,516**, while circuit delay increases by **28**. Both meet their *own case’s* reported target. This is a feasible **area-versus-delay trade**, not strict Pareto dominance.

- **Stage 2 / 002:** Z1 has area **50,694**, delay **77**. S100 has area **58,697**, delay **68**. Here the *sign reverses*: S100 pays **8,003 more area** to remove **nine delay units**. The optimization direction depends on the realized network, allowed slack, mapping choices and candidate policy.

- **Stage 1 / 007 and 025:** S100 saves **28,531** and **25,957** area units respectively, explaining why the Stage 1 bank as a whole improves even though 16 of its 25 cases become larger.

Thus the correct finding is: **on the measured 50-case benchmark, the proposed Stage 2 solver finds much cheaper networks for a minority of high-impact inputs while remaining valid across all 50; it is not uniformly area-superior to the submitted Stage 1 solver.** The comparison also concerns **two distinct code lineages**, not a single isolated patch. It cannot attribute all 124,697 units to one SOP pass or to the cut engine alone.

## The magnitude distribution behind the apparent ranking reversal

The paired study has **18 positive per-case savings**, totaling **160,696**, and **32 negative per-case savings**, totaling **-35,999**; their net is **+124,697**. The five largest improvements together save **129,623**, exceeding the final net saving after all the regressions. This is the appropriate explanation for why the average across areas improves while a majority of individual cases become larger. It is also a warning about *which* aggregate is used: summing raw area units weights naturally large circuits more heavily; taking the median relative change instead gives the typical **percentage** change on one benchmark case, which is **+3.69% in Stage 2 area** (worse for S100 versus Z1).

<figure id="fig:ranking-reversal">
<embed src="figures/07_matched_area_rank_reversal.pdf" style="width:98.0%" />
<figcaption>S100 versus Z1: the complete 50-case distribution of area savings from the independently executed first period, sorted by magnitude. Positive bars mean the Stage 2 implementation has smaller area; negative bars are genuine regressions, not invalid cases. Both programs pass all 50.</figcaption>
</figure>

The ranked cumulative sum $C(k)=\sum_{j=1}^{k}(A_{\mathrm{Z1},(j)}-A_{\mathrm{S100},(j)})$ in Figure <a href="#fig:cumulative-contribution" data-reference-type="ref" data-reference="fig:cumulative-contribution">5</a> makes the tension visible from another angle: the positive contributors raise it to **160,696**, and 32 regressions reduce it to **124,697**. The curve does *not* trace chronological training progress; its order is chosen retrospectively by observed contribution. It therefore describes concentration, not a deployable selection policy.

<figure id="fig:cumulative-contribution">
<embed src="figures/08_matched_cumulative_contribution.pdf" style="width:88.0%" />
<figcaption>Cumulative per-case area contributions, ordered from most favorable to least favorable for S100. The two endpoints correspond to the 18 improvements and the full 50 cases respectively.</figcaption>
</figure>

## Where Jincan’s independent Stage 1 line fits

J51 is not dispensable merely because Z1 was submitted. Against Z1 in repeat 1, J51 has lower area on **15 of their 49 jointly passing cases** and still saves **106,829** area units on that matched common-case set. Its complete Stage 1 bank has area 529,014 versus Z1’s 589,023, and its median synthesis runtime there is much shorter. These are substantive algorithmic and implementation contributions, consistent with its independent Stage 1 development record. However, J51’s **Stage 2 / 016 FAIL** exposes the limit that R7 addressed: a capable high-quality synthesis search can still fail the **actual resource contract**. The failure is not cured by excluding the case or replacing it with an estimated area.

The scientifically useful comparison is therefore **triangular**:

1.  **Z1 → S100**: official Stage 1 submitted method versus final Stage 2 method, under the same released case set.

2.  **J51 → S100**: the development pathway from independent Stage 1 research to a new Stage 2 engineering solution, including a failure mode repaired in Stage 2.

3.  **R9.0 → R10.0**: a much narrower frozen-source **within-lineage ablation**, identifying the marginal effect of the final optional SOP pass on released cases.

These answer different questions; none may substitute for another. The final report can emphasize the mandated Z1→S100 comparison without erasing J51’s technical ancestry.

## Same-source changes across periods are an experimental fact

In the matched independent repeat, S100’s total area increases by **95** on Stage 1 / 012 and **241** on Stage 2 / 005; Z1 adds **947** on Stage 2 / 021. The same respective source hashes and input hashes were used. Circuit delay totals are unchanged. This is evidence of **output sensitivity across observed runtime conditions**, not source-version drift. Both engines contain clock-aware candidate stopping/selection, so differing candidate trajectories are plausible. There is no root-by-root production trace demonstrating *exactly which* deadline or branch caused each difference. A correct research log records the observed difference and candidate-clock explanation as **hypothesis**, not as a proved causal trace.

The native R10.0 feedback was a *different controlled batch* in which both periods happened to return area 1,019,547 for the default. That agreement cannot be silently imposed on the independent three-method test. Both observations are valid within their own recorded conditions.

<div class="tcolorbox">

**Decision from the matched study:** maintain two separate Stage 1 accounts; use Z1 versus S100 to satisfy the assignment and J51 versus S100 to explain genuine technical development. Keep per-case area, delay, time and target status together. Never infer program superiority from the area summed only over successes if the success sets differ.

</div>

# Fixed-incumbent experiment: what a two-pass order hypothesis actually predicts

## Why the previous R8.5 evidence did not isolate pass order

R8.5 changed ordering and sometimes reclaimed time and modified quota, so its production comparison could not isolate the algebraic effect of order. A clean diagnostic must hold **the starting network** fixed and also make the amount of work countable. The additional reproduction study `02_analysis/FIXED_GRAPH_EXPERIMENT.md` does this; it must be distinguished from the historical released-case benchmarking because the six test cases were **purposively chosen after inspecting results**, not selected as an untouched random sample.

For each of six selected inputs, R10.0 with its optional final postpass explicitly disabled created and saved **one initial incumbent DAG**. Four experimental arms begin with that exact frozen graph: SOP only (**P**), Shannon only (**H**), SOP then Shannon (**PH**) and Shannon then SOP (**HP**). Both two-pass arms use the same frozen `r84cut::rewrite` code, the same Top-Q/root-ranking policy, and **160 visited roots per pass**. The emergency 60-second ceiling was never triggered, so truncation cannot explain this particular order comparison. Every pass accepts a replacement only if it preserves the function, remains target-feasible and strictly reduces global live-gate area.

## The mathematical reason pass order need not commute

A rewrite operator is state-dependent: its current root set, cut frontiers, future fanouts and canonical hash lookups are functions of its **input graph**, not just the output Boolean function. Therefore, in general,

$$P(H(G))\not\cong H(P(G)),$$

where $\cong$ denotes structural DAG equivalence, although both graphs satisfy $F_{P(H(G))}=F_{H(P(G))}=F_G$ provided all individual substitutions are correct. Moreover, if both operators are strict-area-decreasing when they accept a candidate, then

$$A(P(G))\le A(G),\quad A(H(G))\le A(G),
\quad A(P(H(G)))\le A(H(G)),\quad A(H(P(G)))\le A(P(G)).$$

These inequalities bound the *admitted* output area but do not order the two compositions against each other. The search landscape changes after the first transformation: the same formal Boolean function can be realized with different shared subgraphs, arrival times and feasible cut choices.

## What the verified fixed-graph evidence says

All **24 final arms** and the six seed outputs were independently simulated against the full source truth tables; the experiments have retained input/netlist SHA-256 fingerprints. Among the six selected graphs, **PH wins three**, **HP wins one** and **two tie**. The sign reversal is observable on individual fixed incumbents:

<div class="longtable">

@ \>

p(- 10) \* \>p(- 10) \* \>p(- 10) \* \>p(- 10) \* \>p(- 10) \* \>

p(- 10) \* @

Fixed seed

&

Area before

&

Area after PH

&

Area after HP

&

Delay of compared outputs

&

Interpretation

  
Stage 2 / 005 & 103,641 & **102,471** & 102,716 & 68 & SOP-first better by 245 on this frozen graph.  
Stage 2 / 003 & 15,773 & 15,585 & **15,575** & 65 & Shannon-first better by 10 on this frozen graph.  

</div>

The actual full source is ; the launcher, detailed per-pass metrics and netlist verifications are in and . The contrast demonstrates **path dependence under fixed input DAG and root count**, not an overall superiority of one order across unseen cases. That distinction is important: equal quota controls one dimension of search effort; it does not make every pass have equal numbers of cuts, candidate materializations or CPU instructions.

This mechanism experiment closes an attribution gap in R8.5: it proves by controlled counterexample that the two pass orders can produce different final network areas. It does *not* identify one universally better production order. The conservative source selection of R10.0, rather than speculative composition of every pass family, remains justified.

# Reconstructing the final synthesis algorithm as a complete executable pipeline

A trial log should end with a clear account of **what the frozen solution actually does**, not only how its experiments are named. The following is a source-backed schematic of the frozen R10.0 translation unit and its included headers, with optional research branches separated from the shipped default. Individual candidate selection and timing guards are simplified in notation here; for literal thresholds consult the source-level descriptions in Sections 12, 14 and 16.

    synthesize(instance):
        read n, m, gate areas/delays, delay target, optional resource limits
        read the complete 2^n-row, m-output truth table
        if (n >= 18 and 0 < runtime_limit <= 250 ms):
             verify streaming-identified constant/literal/affine forms on ALL rows
             if a legal, target-feasible exact network is constructed:
                  emit it and finish
        incumbent = Stage-1-derived multi-candidate Boolean/network synthesis
        validate/prune/measure entire output-reachable AND2/OR2/NOT DAG
        if documented R8.6 eligibility and budget guards hold:
             from the SAME frozen incumbent evaluate bounded Shannon and SOP
             cut-resynthesis branches under the selected root-allocation policy
             keep a valid candidate only if its complete cost is preferred
        if runtime_limit >= 1000 ms and incumbent is valid and target-feasible:
             available = min(90 ms, 0.06*runtime_limit,
                             0.82*runtime_limit - elapsed_since_launch)
             if available >= 8 ms:
                  trial = SOP-only priority_topq rewrite on incumbent
                          (normal cap 160 visited roots)
                  if trial valid AND trial delay <= target
                         AND trial entire-DAG area < incumbent area:
                       incumbent = trial
        emit the legal topological netlist of incumbent

This is an **algorithmic summary**, not an assertion of all-source formal verification. Its architecture explains several otherwise scattered research decisions:

- The Stage 1 machinery supplies an exact legal construction and diversified mapping rather than hoping a cut optimizer can reconstruct the entire function from scratch.

- The incumbent-first discipline learned in R7 ensures optional improvements do not replace a valid circuit with a partially built or rejected candidate.

- R8.1’s cut truth signatures ensure local semantic equality while liveness pruning and whole-DAG scoring prevent incorrect area accounting.

- R8.3–R8.6 control which candidate roots are searched, rather than assuming elapsed time alone measures useful work.

- R9.0 recognizes exact cheap structure early on a narrowly specified short-budget branch; ordinary cases remain in the general synthesis path.

- The adopted R10.0 extra postpass is **monotone in admitted area for a fixed incumbent**: if it fires and its result is accepted, area strictly decreases and target feasibility is retained. It is **not** monotone across independent whole-program invocations in clock-dependent search, nor a guarantee of universal runtime dominance.

## The precise logical contracts of the local transforms

Four mathematical properties are sufficient to explain why the proposed operations *can* be sound:

1.  **Shannon reconstruction.** Each decision computes $f=\neg x\land f_0\lor x\land f_1$; structural reuse of identical cofactors does not change outputs.

2.  **Cut equivalence.** If an acyclic replacement realizes the same formal truth signature on the fixed cut frontier, composition with the unchanged external circuit preserves every original primary-output function (including paths shared with other outputs).

3.  **Global area identity.** For two completed DAGs with identical price schedule, $$A(G')-A(G)=\sum_{v\in L(G')\setminus L(G)}a(v)
          -\sum_{v\in L(G)\setminus L(G')}a(v).$$ Here node identities in the intersection must refer to genuinely surviving gates with unchanged operations; a graph isomorphism of independently rebuilt nodes is not enough to justify term-wise cancellation without matching. No merely *hypothetical* removed gate contributes to a saving.

4.  **Fixed-boundary timing sufficiency.** On an original DAG $G$, initialize output required times at $D_{\rm target}$ and propagate $R(u)\le R(v)-d(v)$ backward over every original edge. An acyclic equivalent cone with unchanged external dependency boundary, replacement roots arriving no later than their original required times and unchanged external gate delays preserves the target by induction through the unchanged region. **If a transformation changes fanout, dependencies or boundary signals, stale $R$ values do not justify the same inference**; recompute timing for the completed network.

The actual C++ correctness checks are a second layer beyond these mathematical identities: legal node indices, acyclicity, output mapping, complete truth-table checking and area/delay computation. Independent signature tests (768 cases) and independent evaluator/source-reproduction runs were performed; none converts heuristic minimum-area search into an optimality proof.

## The synthesis and circuit objectives must remain dimensionally separate

A conceptual view of the engineering objective is to find a valid synthesis policy $\pi$ such that the **produced** network $G_{\pi,B}(F)$ has low charged area and meets the desired delay target, while the *program* remains within its runtime and memory allowance:

$$\begin{aligned}
& G_{\pi,B}(F)\equiv F,\qquad D(G_{\pi,B}(F))\le D_{\rm target}\quad\text{(preferred quality condition)},\\
& T_{\rm synth}(F,\pi,B)\le T_{\rm cap},\qquad M_{\rm peak}\le M_{\rm cap}
\quad\text{(when those limits apply)},\\
&\text{seek small } A(G_{\pi,B}(F))\text{ among such outputs.}
\end{aligned}$$

This is **our mathematical model of the design decision**, not the undisclosed official scoring equation. The published feedback evaluates one finite sample of inputs and environments, not a proof of feasibility for all $n\le20$ and all resource schedules. In particular, source-level guards around elapsed-time checks do not provide hard preemption for every intermediate operation.

# 21. Reading the multi-round sample as a *distribution*, not one scalar

## Why a long-term trajectory is necessary and what it cannot prove

Most version tables reduce a search strategy to one summed Area and one median runtime. That is useful for detecting a gross improvement, but it loses two key distinctions: an algorithm can dramatically improve a few large circuits while hardly changing the median instance, and the same circuit can move in different directions as search priorities are revised. Figure <a href="#fig:long-area" data-reference-type="ref" data-reference="fig:long-area">6</a> therefore takes **one designated archived Stage 2 bank result per research milestone** and plots the area difference relative to the fully passing R7.2 baseline (508,535). It excludes the 24/25-PASS R7 Stage 2 result because its passing-case area sum omits a case and is **not comparable to 25-case totals**.

By R10.0 the selected archived area is 493,965, i.e., **14,570 lower** than R7.2 (about **2.87%** of that particular baseline). The largest structural shift is visible around R8.1–R8.2.1, whereas the final R9–R10 changes appear at a much smaller vertical scale. There is, however, no monotone downward path: R8.3 and R8.4 have larger summed areas than R8.2.1 in these selected records. This is precisely why the version history should be a set of *tested policy alternatives* rather than a claim that each implementation patch monotonically improves a fixed optimizer.

<figure id="fig:long-area">
<embed src="figures/14_stage2_area_delay_trajectory.pdf" style="width:98.0%" />
<figcaption>Selected historical Stage 2 area totals expressed as differences from the R7.2 all-passing baseline. Each point is a recorded archived configuration, not a one-factor causal effect. R7’s incomplete successful-case total is intentionally excluded; detailed archived pointers are in the verified milestone table.</figcaption>
</figure>

Figure <a href="#fig:long-aruntime" data-reference-type="ref" data-reference="fig:long-aruntime">7</a> places each selected archived policy in a two-dimensional *description* of area saved and observed synthesis median. The plot exposes that aggressive search around R8.1 can be costly, and that R8.4’s extra search effort did not automatically produce a better point than its neighboring policies. It also shows why a claim that the final frozen algorithm is simply the *fastest* would be inaccurate. Because these medians come from **different historical campaigns**, we do not draw a randomized causal frontier or quote inter-round speedup factors from these points. Matched R8.6 and R10.0 controls carry the stronger identification claims.

<figure id="fig:long-aruntime">
<embed src="figures/02_archival_area_runtime.pdf" style="width:93.0%" />
<figcaption>Area–synthesis-runtime landscape for selected archived Stage 2 runs. The x-axis is program synthesis runtime, not circuit propagation delay. The area baseline is R7.2; scatter locations are descriptive across separately archived experiments and must not be interpreted as a same-run Pareto frontier.</figcaption>
</figure>

## A case-by-round matrix: persistence, reversals and nearly invisible deltas

Figure <a href="#fig:long-matrix" data-reference-type="ref" data-reference="fig:long-matrix">8</a> resolves a question the aggregate trajectory cannot answer: **are the same functions consistently changing, or does each new strategy discover a different set of opportunities?** Each row takes one designated historical Stage 2 run for a named policy; each column is one released Stage 2 case, all identified by the same bank/case designation. Each cell shows the **percentage reduction of that case’s area relative to its own R7.2 area**, rather than raw gates or a total across differently sized circuits. This normalization makes a 0.5% change on a small graph perceptible alongside a 36% change on a structurally different graph. Gray means no reported change.

<figure id="fig:long-matrix">
<embed src="figures/03_case_round_area_matrix.pdf" style="width:99.0%" />
<figcaption>Selected Stage 2 historical policies against the frozen R7.2 case-level area baseline; 25 cases per row. Color encodes relative area reduction within an instance. The source table <code>casewise_milestone_relative_area.csv</code> includes full-precision numbers. No causal attribution is made to any one component between two archived rows.</figcaption>
</figure>

The matrix produces several concrete, checked observations:

- **Persistence and nonuniversality:** R8.1 changes 17/25 case areas relative to R7.2; R10.0 changes 15/25. In the selected R10.0 Stage 2 benchmark, **10 cases are unchanged**. This is a statement about the archived 25 inputs, not all Boolean functions.

- **Nonmonotonic within-case path:** Stage 2 / 003 records approximately **-21.99%** at R8.1, relaxes to **-11.34%** at R8.3, and settles at **-19.86%** at R10.0 relative to R7.2. The historical development does not preserve every early individual win when the runtime and selection policy change.

- **Long-term concentrated advantage:** Stage 2 / 023 reaches **-36.24%** at R10.0, while Stage 2 / 024 reaches only about **-0.535%**. The two are both improvements, yet they differ by orders of magnitude in percentage scale. This makes a one-number mean misleading about a typical case.

- **Small effects are real but must be contextualized:** the R10.0 Stage 2 distribution has a **median relative area change of approximately -0.052%** versus R7.2, even though the summed area decreases by 14,570. Five cases improve by at least 1%, but only two improve by at least 10%. The total is responding chiefly to a concentrated tail of improvements.

These descriptions are *within the same case bank* and hence do not confuse unequal input sets. Still, successive rows are generally **not matched randomized one-factor treatments**: source code and eligibility policies changed. The matrix reveals *where and when* phenomena occurred; explanations of *which internal cut caused them* require fixed-input DAG traces, not a heatmap.

## A protocol for using plots as evidence, not illustrations

For each figure in this record, the data extraction script must expose the exact run or report hash, the denominator of cases, and whether an area figure includes only passing cases. Three common mistakes are specifically forbidden: (i) plotting R7’s 24-case passing-area sum as though it were a 25-case improvement; (ii) combining a run-1 area with a run-2 runtime to place a fictional point on a tradeoff plot; and (iii) equating a cumulative area win with a majority of case-level wins. The visual form is chosen for the question: a case-by-round matrix for persistence, a sparse lollipop for small localized final changes, a factorial dot plot for controlled knobs, and a sorted contribution plot for distributional asymmetry. None of these establishes a population-level theorem by itself.

The larger arc is now explicit. Stage 1 establishes a correct mapping and efficient candidate engine. R7 makes the process valid under the evaluator’s resource envelope. R8 introduces richer function-level cut replacement and exposes the costs of searching it. R8.3–R8.6 distinguish *where* limited work is spent from nominal elapsed allowance. R9.0 protects short-budget execution. R9.1–R10.1 ask whether a narrowly admitted extra SOP pass justifies its time and whether that win survives smaller search caps. This is a **development explanation supported by distinct experiments**, not a statement that every consecutive version differs by exactly one factor.

## Multiscale reading of the late research line

The preceding historical trajectory answers when the candidate-policy regime changed; it cannot resolve a one-thousand-unit gain when the axis spans more than fifteen thousand units. Figure <a href="#fig:late_zoom" data-reference-type="ref" data-reference="fig:late_zoom">9</a> therefore uses a separate narrow vertical range. On the Stage 2 bank, the selected checkpoints R8.5 through R9.0 all report area 494,999, while R9.1, R10.0 and the unchanged R10.1 control report 493,965. This is the exact *1,034-unit Stage 2-bank difference*, not the *1,587-unit two-bank difference* of the R9.0–R10.0 paired comparison. The distinction prevents accidental mixing of two aggregation units. These selected archival checkpoints are a development trajectory, not an isolated experiment proving the causal effect of one code edit.

<figure id="fig:late_zoom">
<embed src="figures/15_stage2_late_zoom.pdf" />
<figcaption>Late-stage Stage 2 area shown at the resolution needed to see a 1,034-unit change on a roughly 495,000-unit baseline. All points use a complete 25-case checkpoint; cross-version runtime is not inferred from this diagram.</figcaption>
</figure>

## All 111 named configurations: retain breadth without losing precision

The experimental inventory contains **111 distinct (round, variant) names**; **105** have at least one archived 25-case PASS-and-target-met record, but this does not mean that every repeat of those variants succeeded. The full configuration-by-source listing, including 25-case qualification, observed failures, complete-run minimum/maximum, original report digest, delay, and synthesis runtime, remains in `data/stage2_all_variant_index.csv`. Rather than presenting eight low-resolution pages of nearly overlapping points, Figure <a href="#fig:variant_spread" data-reference-type="ref" data-reference="fig:variant_spread">10</a> asks a more interpretable question: *how much did the alternatives within each Round actually differ?*

The horizontal length is $\max_v A_v-\min_v A_v$ over qualified archived variants in the same named Round. A symmetric-logarithmic horizontal axis (linear near zero) permits exact zero differences, tens of units, and thousands of units to coexist without making all small differences invisible. The chart thus distinguishes the negligible R7/R7.1/R7.2 variations from broad R8.1–R8.4 exploration, and the more restricted policy changes in R9–R10. It is a *within-Round diversity diagnostic*, not an effect size, confidence interval, or guarantee that the extrema were measured under an interleaved same-executable comparison.

<figure id="fig:variant_spread">
<embed src="figures/16_all_variant_spread.pdf" />
<figcaption>Within-Round archived range over complete Stage 2 bank observations, accompanied by qualified/total configuration counts. The horizontal scale uses a linear region near zero and logarithmic growth thereafter; exact original data and evidence paths are preserved in CSV.</figcaption>
</figure>

## The final policy must be assessed by matched comparison

The narrow question of whether fewer cut roots or a smaller last-pass budget are preferable *can* be tested on genuinely paired observations. Figure <a href="#fig:archive-finalpolicy" data-reference-type="ref" data-reference="fig:archive-finalpolicy">11</a> uses 100 matched observations for each R10.1 policy (50 released cases, two repeats). Disabling the final pass yields median runtime ratio $0.942$ but costs 1,587 weighted area units per 50-case equivalent; caps of 40 and 80 cost 1,008 and 602 units, respectively, while showing only modest median time reductions. A 45-ms allowance costs 241 units and does not improve the observed median runtime (ratio 1.009). Therefore the retained R10.0 policy is a supported *measured operating point*, not a universal optimality theorem or simply the most recent source file.

<figure id="fig:archive-finalpolicy">
<embed src="figures/12_r101_native_pareto.pdf" />
<figcaption>Paired area penalty and synthesis-time ratio relative to frozen R10.0. Positive area penalty is worse; runtime ratios below one are faster. The measurements are converted from 100 paired observations to a 50-case-equivalent area figure.</figcaption>
</figure>

## Part III — Team integration and freeze record

Integrated Final, pinned to `59e3350`, is the planned team delivery. Its entry point keeps a complete natural-order mapped fallback, then budgets BDD screening and the imported J51 portfolio. Mapped candidates compete under a one-unit delay reserve. Incremental live references let the solver measure each output-cone switch on the full shared DAG. The inherited four-leaf SOP library runs once on the integrated incumbent under the integrated scheduler. Shared factors, critical cuts and late-output cofactor synthesis broaden the candidate set. The standalone J51 and R10.0 controllers remain documented in the historical record. [Source](../../Final_Submission_by_Zeyun_DU/src/synth_stage2.cpp) · [Origin note](../../Final_Submission_by_Zeyun_DU/src/round51/ORIGIN.md)

Across the two fresh matched repeats, all four solvers passed and met every target on both 25-case banks. Integrated Final reached areas of 872,813 and 872,919, with roughly 22.6% lower aggregate area than Z1 and 14.4% lower than R10.0. Its summed runtime was 2.14–2.20× R10.0's. In repeat 1 the R10.0-relative area reduction was 6.2% on Stage 1 and 23.2% on Stage 2. Its 100 outputs were independently replayed over their full truth tables, and every circuit had at least one delay unit of slack. J51 approached the time limit on Stage 2 case 016 in both complete repeats and timed out in an earlier interrupted diagnostic. The matched WSL batch, upstream ZIP acceptance and historical research measurements retain separate provenance. [Integration audit](../../Final_Submission_by_Zeyun_DU/integration/AUDIT.md)

Earlier same-incumbent pass measurements identified sparse SOP and shared-factor gains on their own snapshots. The whole-system comparison has no iso-budget control to separate structural and scheduling changes from the larger search window. One generated validation case, seed 711413 case 003, remains at delay 28 against target 27. The generating witness meets 27 on all 16,384 assignments. The team selected the complete measured operating point. [Residual evidence](../../Final_Submission_by_Zeyun_DU/reports/stage2-timing-20261124/residual.csv) · [Formal Report](../main.pdf)

## Final team integration and evidence reconciliation

The research record closes at R10.1, with R10.0 retained as Jincan Li's independent Stage 2 freeze. Zeyun Du authored Z1 and coordinated the team integration and validation. The integrated code adapts J51 mapping and R10.0 four-leaf cut rewriting and adds its own scheduling, shared-output selection and timing recovery. The upstream report credits Codex for implementing timing rescue and assisting with packaging and verification. [Source attribution](../../Final_Submission_by_Zeyun_DU/src/round51/ORIGIN.md)

The earlier upstream cuts snapshot recorded area 869,773. The subsequent pinned release at `59e3350` recorded 884,234, 876,694 and 876,694 over three 50-case public repeats, each with all evaluator passes and target delays met. The integration audit adds a fresh matched comparison of Z1, J51, R10.0 and Integrated Final, with separate RSS measurements and independent replay of the final circuits. The team archive is the planned course delivery. Its course submission status is unverified. [Integration audit and datasets](../../Final_Submission_by_Zeyun_DU/integration/AUDIT.md)

# 22. What the development path has *actually* established

The trial history is best remembered as an ordered set of **resolved design questions**, not as a monotone chart of area totals:

<div class="longtable">

@ \>

p(- 6) \* \>

p(- 6) \* \>

p(- 6) \* \>

p(- 6) \* @

Phase

&

Initial unanswered question

&

Verified evidence / resolution

&

Explicit limit

  
Stage 1 R1–R3 & Can an exact truth-table circuit satisfy a priced timing target? & Shannon/ROBDD correctness, portfolio mappings and required-time recovery bring released-case target success to 25/25. & Combined improvements not all individually causal.  
Stage 1 R4–R5.1 & Can near-final area quality be retained at lower synthesis cost? & Selected caching and typed DAG refactors preserve released-case area 529,014; paired runtime falls. & Elapsed-gated future candidates may still vary.  
Stage 1 R6–Stage 2 R8.1 & Does the mapped DAG contain savings outside original BDD decomposition? & Small-cut semantic resynthesis and direct area/delay controls find additional valid circuits. & Local truth equivalence alone says nothing about whole-DAG area.  
R7–R7.2 & Can extra search jeopardize validity under a short cap? & Stage 2 / 016 FAIL and guard recovery; shortlist improves an overly conservative quality loss. & A cutoff check is not preemptive worst-case execution-time proof.  
R8.1–R8.2 & Do area, delay and runtime agree on a best rewrite? & Area-first and strict-delay policies choose different network qualities. & No official scalar score inferred.  
R8.3–R8.6 & Is effective search work about elapsed wall time or which roots get visited? & Explicit quotas, priorities and factorial contrasts isolate the area benefit of extra SOP roots (2,844) rather than extra nominal time on the released batch. & Not a general theorem about all instance families.  
R8.7–R9.0 & Are the gains safe to deploy on different structures and constrained runtime? & Generated-function negative result and short-cap stress motivate exact streaming bypass and runtime-first fallback. & A few structured stress fixtures do not bound hidden-case resource use.  
R9.1–R10.0 & Is a new function library better than an ordinary additional pass? & Library wins more cases but saves less total area; repeat SOP saves 1,587 on eight published cases; R10 default preserves fallback and verifies strict full-DAG improvement. & 0.155% is an aggregate comparison; typical instance unchanged.  
R10.1 & Can the final pass be made cheaper without losing its important wins? & Caps 40/80 and 45-ms allowance lose area benefits; no robust runtime-dominance offset. & 160 roots is a tested decision, not a proved global optimum.  
Independent matched comparison & Does the final program improve over the **actual submitted** Stage 1 program? & Both methods 50/50 valid; S100 saves 124,697/125,308 area units over the two periods. & S100 loses 32/50 cases by area and is not universally Pareto-superior.  

</div>

Three cross-cutting lessons now have an experimentally grounded status:

**(i) The optimization unit is a whole, priced, timed live DAG.** Shannon and mask equality are function-level guarantees. The four-output counterexample proves that a locally shorter expression can increase full-network area. The R8.1 area–delay results demonstrate why each legal candidate must be rescored, not just locally simplified.

**(ii) Selecting *useful* work matters more than equating a nominal time budget with optimization progress.** R8.4’s rank-vs-topology distinction, R8.6’s 2×2 intervention and R9.1’s frequency-vs-magnitude reversal show that number of visited candidates, number of winning cases, area payoff and runtime are distinct quantities. The final source uses root caps and reserve rules for exactly that reason.

**(iii) A release is a *policy*, not a one-off best benchmark value.** R10.0 combines an exact base, optional bounded improvements, strict acceptance and a special short-budget semantic bypass. R10.1’s negative result is part of why the frozen default is defensible. This is evidence of reasoned engineering selection rather than a claim of global Boolean minimization.

# Reproducing this record and separating what remains unproved

## Reconstructing an archival comparison without inventing a run

1.  Identify a named source snapshot and its compiler/evaluator flags; retain the program’s full SHA-256 and the case-bank hashes. The frozen source hashes are recorded at the start of this log and in the reproduction bundle.

2.  Retrieve the matching feedback ZIP or report payload hash; verify that every listed case row is unique, identify PASS versus `target_met`, and *exclude FAIL from successful-only numeric area sums without silently reducing the denominator in comparative claims*.

3.  To compare two policies, join by **bank, case, period, report experiment and input checksum**. For a genuine one-factor ablation, verify that *all other policy parameters* and the initial incumbent are held fixed. Historical consecutive rounds alone do not establish an isolated treatment effect.

4.  Report PASS count, target-met count, total charged Area (on explicitly specified common cases), sum or distribution of circuit Delay and paired Runtime summaries. Never substitute circuit Delay for synthesis-time milliseconds; do not interchange `time -v` peak RSS with the evaluator’s RAM flag.

5.  Only after completing the numeric checks, interpret why the *actual source implementation* and mathematical transformation could produce the observed outcome; distinguish what the code makes possible from what an uninstrumented benchmark actually recorded.

6.  Preserve negative and non-adopted branches. A zero-gain or timeout result can explain a later architecture decision as strongly as an improvement result.

The audit tools accompanying this document reconstruct the raw late-round feedback (`verify_raw.py`), re-evaluate every hash-addressed indexed report (`reverify_inventory.py`), and retain the detailed normalized outputs. In particular:

- **`ALL_RUNS_REVERIFIED.csv`:** 1,706 recomputed index rows from 602 distinct content-hash-verified original evaluator tables; 1,706 matched historical aggregate records.

- **`RAW_FEEDBACK_VERIFIED.csv`:** 196 directly decoded original late-round feedback CSVs, with 25-case completeness, status/target counts, area/delay sums, and runtime summaries; the earliest rounds instead come through the audited evidence database.

- **`RAW_CONTROLLED_PAIRS_VERIFIED.csv`:** within-batch contrasts from the native feedback tables, not a noncausal across-archive runtime ranking.

- **`RAW_ARCHIVE_SHA256.txt`:** archive-level digests linking the late-round measurements to the supplied ZIP bytes.

- **`06_reproducibility/matched_batch/*.csv`:** 300 newly run/archived three-method invocations covering both banks and both periods. Their figures and hashes originate in the input reproduction package; these files are copied, not secretly rerun during this particular written audit.

- **`06_reproducibility/fixed_batch/fixed_order.csv`:** the 24 fixed-graph pass-order arms plus full per-pass counters, signatures and full-truth-table verification traces; experiment executed before this document was authored.

- **`06_reproducibility/scripts/mechanism_test.cpp`:** source used for the 768 independent small-cut truth checks and the four-output area counterexample, independently compiled and run again for this edition.

## Unproved claims and the exact missing instruments

The following are not defects that can be fixed by more confident prose. They require different evidence or a narrowed claim:

- **No exhaustive optimality result:** even a four-leaf mask is exhaustively *evaluated* as a function, but SOP/Shannon/limited template candidates do not enumerate all minimal shared, timing-constrained gate networks.

- **No measured causal attribution of the production eight R10.0 gains to specific live-node mechanisms:** exact per-case area savings are verified, but an uninstrumented completed-netlist feedback cannot tell how many private nodes died at each particular accepted cut. Required evidence would include frozen incumbent/checkpoint DAGs and per-cut fanout, liveness and arrival logs on a small selected sample. The four-output example demonstrates the mechanism’s possibility, not why a particular production case improved.

- **No full formal runtime/memory guarantee for all allowed tables:** runtime limits restrict performance validity, but periodic guards and exact early recognition do not formally cap every loop or allocator path. Benchmark PASS is an observed property of tested runs.

- **No representative unknown-input guarantee:** 50 released cases and carefully documented generated families test specific distributions; development tuning on them prevents claims of statistical independence for all later parameters.

- **No inferred official numerical score:** sum-of-Area, home-made ADP and runtime geometric ratios are explanatory diagnostics. The hidden course score is not reverse-engineered.

- **No isolated global treatment effect for consecutive multi-change rounds:** where an archived version changes search policy, rooting, cache layout and budget together, a before/after delta is not a one-factor causal estimate. R8.6 and the fixed-incumbent order probe are stronger designs for their narrower questions.

**Research status after this log.** The algorithmic implementation can remain frozen. The full method lineage, successes, negative experiments, feasible tradeoffs and source-backed final policy are now reconstructed for subsequent writing. Only a *limited set of mechanism-level claims* would benefit from additional instrumentation; none should be manufactured to make the existing evidence appear more complete. The next formal Stage 2 paper can be written from this trial record, but its outline is intentionally not precommitted here.

# Research appendix A: A compact numerical locator for the Stage 2 sequence

The table below is deliberately an **index**, not the causal argument. It displays one archived Stage 2 bank, first-period configuration per named round, with the original report SHA-256 and exact source path preserved in `SELECTED_ROUND_MILESTONES.csv`. A multi-version change between two adjacent rows **must not** be called the marginal effect of one optimization: source conditions, caps, candidate choices and sometimes the evaluation campaign changed. The correct *within-batch* controls are the pair tables, the R8.6 factorial and R10.0 off/default tests described above.

<div class="longtable">

@ \>

p(- 12) \* \>

p(- 12) \* \>p(- 12) \* \>p(- 12) \* \>p(- 12) \* \>p(- 12) \* \>p(- 12) \* @

Milestone

&

Selected policy

&

PASS

&

Target-met

&

Area on passing cases

&

Delay sum on passing cases

&

Median synth. ms

  
R7 & default & **24/25** & 24/25 & **506,754**\* & 1,065\* & 33.463\*  
R7.1 & guard & 25/25 & 25/25 & 508,535 & 1,101 & 31.268  
R7.2 & shortlist & 25/25 & 25/25 & 508,535 & 1,101 & 30.489  
R8 & iterate & 25/25 & 25/25 & 508,480 & 1,102 & 32.131  
R8.1 & reverse & 25/25 & 25/25 & 497,509 & 1,158 & 189.880  
R8.2 & dual-area & 25/25 & 25/25 & 501,547 & 1,156 & 163.231  
R8.2.1 & dual-area & 25/25 & 25/25 & 494,618 & 1,169 & 131.585  
R8.3 & stable-dual & 25/25 & 25/25 & 500,072 & 1,169 & 87.518  
R8.4 & Top-Q dense & 25/25 & 25/25 & 500,027 & 1,170 & 191.486  
R8.5 & budget-reclaim & 25/25 & 25/25 & 494,999 & 1,170 & 104.917  
R8.6 & extra-SOP roots & 25/25 & 25/25 & 494,999 & 1,170 & 107.818  
R8.7 & extra-SOP roots & 25/25 & 25/25 & 494,999 & 1,170 & 105.535  
R9.0 & default no flags & 25/25 & 25/25 & 494,999 & 1,170 & 107.471  
R9.1 & repeat SOP & 25/25 & 25/25 & 493,965 & 1,170 & 117.559  
R10.0 & default frozen & 25/25 & 25/25 & 493,965 & 1,170 & 120.158  
R10.1 & unchanged default & 25/25 & 25/25 & 493,965 & 1,170 & 112.909  

</div>

\* **R7’s reported Area, Delay and successful-run median exclude its failed case 016**; they are incomplete metrics and must *not* be treated as a superior 25-case result. R8.1’s `reverse` policy is an area-oriented branch with greater observed delay, **not** a release decision. R10.1’s displayed `default` is the unchanged control, not a successful new improvement. The Stage 1 bank for these same archived checkpoints, plus original paths, is recorded separately in the paired 32-row CSV.

# Research appendix B: Source and experiment map: where each technical claim can be checked

This map names the archived implementation or original evidence relevant to each research transition, rather than treating a prose statement as proof of code behavior. Root paths below refer to the unpacked user’s original `Stage2_Final_Evidence` and `UFUG2106_Stage2_Research_and_Reproduction` material.

<div class="longtable">

@ \>

p(- 4) \* \>

p(- 4) \* \>

p(- 4) \* @

Technical question

&

Primary implementation / verification source

&

Experimental evidence

  
Stage 1 actual submission versus independent research & Z1 submitted `src/synth.cpp`; J51 frozen `src/synth_round51.cpp` and its headers; 21-page Stage 1 Research Trial Log & Stage 1 frozen development feedback and the two-bank matched batch.  
R7–R7.2 runtime guards and fallback quality & `synth.cpp` ancestry; `UFUG_R7_LEGACY_MERGE` and later schedule/guard branches & R7/R7.1/R7.2 archived official per-case CSV and case 016/020 comparisons.  
R8 structural patterns and iteration & `r8_structural.hpp` & R8 prototype `off`, `factor`, `reuse`, `strict`, `all`, `iterate`; case 021 repeat trace.  
R8.1 small-cut substitution and typed live-DAG scoring & `r81_cut.hpp`, `r82_cut.hpp`, `typed_netgraph.hpp`, later `r84_cut.hpp` & R8.1 SOP/Shannon/strict/reverse controls; local truth-signature correctness test.  
R8.2–R8.2.1 objective/resource perturbation & `r82_cut.hpp`, `r821_resource.hpp` & R8.2 dual area/ADP/strict/slack and R8.2.1 restricted-RAM tests.  
R8.3 work quota and R8.4 Top-Q score & `r83_cut.hpp`, `r84_cut.hpp` & R8.3 stable/dense/fast, R8.4 ranked/topological/dense tests.  
R8.5 branch order and R8.6 factorial identification & `r84_cut.hpp`, R8.6 dispatch in frozen `synth.cpp` & R8.5 SOP-first/Shannon-first/budget-reclaim, R8.6 2×2 + reverse control, independently decoded ZIPs.  
R8.7 distribution and short-limit stress & R8.7 frozen program and generated-case provenance files & , two repeats, tight-budget case logs.  
R9.0 exact streaming early path & `r90_stream.hpp` and early dispatch in frozen `synth.cpp` & R9.0 official stress fixtures plus published 50-case regressions.  
R9.1 template versus conventional repeat & `r91_library.hpp`, `r84_cut.hpp` & Library / repeat-SOP / repeat-Shannon / off controls and casewise results.  
R10.0 frozen policy and R10.1 no-go & Final `submission/synth.cpp`, all included headers & R10.0 native `off`/explicit/default/submission; R10.1 caps and allowance ablations.  
Cross-stage comparison and pass-order mechanism & `06_reproducibility/sources`, `scripts/fixed_order.cpp`, `scripts/mechanism_test.cpp` & `matched_batch/*.csv`, , exact independent truth-table verification.  

</div>

The **strongest distinction preserved across the log** is epistemic: a source statement explains what a program *can* do, a formal identity explains why a transformation *could* be sound, and a matched experiment establishes what happened *on the measured cases*. None of these three forms of evidence should silently replace another.


## Multiscale reading of the late research line

The preceding historical trajectory answers when the candidate-policy regime changed; it cannot resolve a one-thousand-unit gain when the axis spans more than fifteen thousand units. Figure <a href="#fig:late_zoom" data-reference-type="ref" data-reference="fig:late_zoom">1</a> therefore uses a separate narrow vertical range. On the Stage 2 bank, the selected checkpoints R8.5 through R9.0 all report area 494,999, while R9.1, R10.0 and the unchanged R10.1 control report 493,965. This is the exact *1,034-unit Stage 2-bank difference*, not the *1,587-unit two-bank difference* of the R9.0–R10.0 paired comparison. The distinction prevents accidental mixing of two aggregation units. These selected archival checkpoints are a development trajectory, not an isolated experiment proving the causal effect of one code edit.

<figure id="fig:late_zoom">
<embed src="figures/15_stage2_late_zoom.pdf" />
<figcaption>Late-stage Stage 2 area shown at the resolution needed to see a 1,034-unit change on a roughly 495,000-unit baseline. All points use a complete 25-case checkpoint; cross-version runtime is not inferred from this diagram.</figcaption>
</figure>

## All 111 named configurations: retain breadth without losing precision

The experimental inventory contains **111 distinct (round, variant) names**; **105** have at least one archived 25-case PASS-and-target-met record, but this does not mean that every repeat of those variants succeeded. The full configuration-by-source listing, including 25-case qualification, observed failures, complete-run minimum/maximum, original report digest, delay, and synthesis runtime, remains in `data/stage2_all_variant_index.csv`. Rather than presenting eight low-resolution pages of nearly overlapping points, Figure <a href="#fig:variant_spread" data-reference-type="ref" data-reference="fig:variant_spread">2</a> asks a more interpretable question: *how much did the alternatives within each Round actually differ?*

The horizontal length is $\max_v A_v-\min_v A_v$ over qualified archived variants in the same named Round. A symmetric-logarithmic horizontal axis (linear near zero) permits exact zero differences, tens of units, and thousands of units to coexist without making all small differences invisible. The chart thus distinguishes the negligible R7/R7.1/R7.2 variations from broad R8.1–R8.4 exploration, and the more restricted policy changes in R9–R10. It is a *within-Round diversity diagnostic*, not an effect size, confidence interval, or guarantee that the extrema were measured under an interleaved same-executable comparison.

<figure id="fig:variant_spread">
<embed src="figures/16_all_variant_spread.pdf" />
<figcaption>Within-Round archived range over complete Stage 2 bank observations, accompanied by qualified/total configuration counts. The horizontal scale uses a linear region near zero and logarithmic growth thereafter; exact original data and evidence paths are preserved in CSV.</figcaption>
</figure>

## The final policy must be assessed by matched comparison

The narrow question of whether fewer cut roots or a smaller last-pass budget are preferable *can* be tested on genuinely paired observations. Figure <a href="#fig:archive-finalpolicy" data-reference-type="ref" data-reference="fig:archive-finalpolicy">3</a> uses 100 matched observations for each R10.1 policy (50 released cases, two repeats). Disabling the final pass yields median runtime ratio $0.942$ but costs 1,587 weighted area units per 50-case equivalent; caps of 40 and 80 cost 1,008 and 602 units, respectively, while showing only modest median time reductions. A 45-ms allowance costs 241 units and does not improve the observed median runtime (ratio 1.009). Therefore the retained R10.0 policy is a supported *measured operating point*, not a universal optimality theorem or simply the most recent source file.

<figure id="fig:archive-finalpolicy">
<embed src="figures/12_r101_native_pareto.pdf" />
<figcaption>Paired area penalty and synthesis-time ratio relative to frozen R10.0. Positive area penalty is worse; runtime ratios below one are faster. The measurements are converted from 100 paired observations to a 50-case-equivalent area figure.</figcaption>
</figure>

### Upstream pass and timing-policy evidence

On the archived paired cut snapshot, SOP polishing saves 3,165 weighted units over 17 public cases, with the other 33 unchanged. The separate factor study saves five public units, from Stage 1 cases 022 and 023. It also has larger individual diagnostic savings and two holdout reductions from 129 to 107 at unchanged delay 11. These are distinct snapshots and families. [Paired cuts](../../Final_Submission_by_Zeyun_DU/reports/stage2-cuts-20261124/paired.csv) · [Paired factors](../../Final_Submission_by_Zeyun_DU/reports/stage2-factors-20261124/paired.csv)

Team public acceptance required area below 900,000 and at least one delay unit of reserve, alongside evaluator verdicts and independent replay. The earlier weighted trial used 869,636 area with nine exact-target cases, and the one-reserve trial used 898,282. On the two initial generated banks, the previous delivery met 11/14 and 10/14 targets. Grouped covers reached 14/14 on both, while later seeds exposed limitations addressed by scratch-gate reclamation, increased supported input count and remapping reconstructed paths. The final archive records 168/168 development observations and 83/84 validation and post-freeze observations, including repeated exact-target controls. [Headroom trials](../../Final_Submission_by_Zeyun_DU/reports/stage2-headroom-20261124/development.csv) · [Timing development](../../Final_Submission_by_Zeyun_DU/reports/stage2-timing-20261124/development.csv)

Under competing load one old-cap public run totaled 910,462, while the other archived old-cap totals were 880,987 and 883,002. This motivated a larger main window without isolating its effect. The three final source-ZIP public repeats passed the ceiling, reserve and replay criteria. On the residual generated case, changing input order, extra XOR forms, XOR phase transfer, broader balanced masks, derivative expansion and factor splits all left delay at 28, while the feasible witness reaches 27. [Old-cap trials](../../Final_Submission_by_Zeyun_DU/reports/stage2-timing-20261124/earlier-budget.csv) · [Public freeze checks](../../Final_Submission_by_Zeyun_DU/reports/stage2-timing-20261124/public-runs.csv) · [Residual comparisons](../../Final_Submission_by_Zeyun_DU/reports/stage2-timing-20261124/residual.csv)

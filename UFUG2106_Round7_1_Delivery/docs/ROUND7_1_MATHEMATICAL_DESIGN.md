# Round 7.1: Budget-Aware Anytime Portfolio — Mathematical and Engineering Design

## 1. Problem definition and motivation

A synthesizer maps a full Boolean truth table \(F:\{0,1\}^{n}\to\{0,1\}^{m}\) into a directed acyclic network \(C\) of AND2, OR2 and NOT gates. All emitted gates must be topologically ordered and produce outputs identical to the truth table.

For a network with live gate sets \(G_{\land},G_{\lor},G_{\neg}\), its weighted area is

\[
A(C)=a_{\land}|G_{\land}|+a_{\lor}|G_{\lor}|+a_{\neg}|G_{\neg}|.
\]

Input arrival times are zero and internal arrivals are recursively calculated:

\[
 t(v)=\begin{cases}
  t(u)+d_{\neg},&v=\neg u,\\
  \max\{t(u),t(w)\}+d_{\circ},&v=u\circ w,
 \end{cases}
 \quad D(C)=\max_{o\in\mathrm{outputs}}t(o).
\]

A valid emitted network must satisfy Boolean equivalence, format rules and the official runtime/memory bounds. The target delay is a high-priority quality criterion but an over-target result is not automatically a functional FAIL. The course's exact numerical grade formula is unknown; do not replace it with an invented area/runtime weighting.

## 2. Why *faster* kernels can cause *slower* synthesis

Let \(C_0,\ldots,C_q\) be candidate circuits created in order. The legacy portfolio dispatches a candidate if the elapsed time \(t\) is below a fraction of the declared limit \(L\). The rule does not reserve for the **time of the next non-interruptible candidate**.

Suppose \(t_0=65\) ms after a fast first candidate, \(\tau_1=45\) ms for a new candidate, and \(L=100\) ms. The old guard \(t_0<0.75L\) authorizes the new candidate, yet \(t_0+\tau_1=110\) ms exceeds the evaluator's limit. A slower candidate that ends at 80 ms may paradoxically finish earlier because the algorithm *does not start* candidate 1.

This is a policy-level pathology: local acceleration decreases \(\tau_0\), but can increase the number \(q\) of attempted candidates. A correct comparison must therefore measure both primitive cost and the **total dispatched work**.

## 3. Existing synthesis strategy intentionally preserved

Round 7.1 builds on Round 7's two exact cover optimizations and on the frozen Round 5.1 portfolio. It preserves:

- cached complemented-edge ROBDD construction and variable-order heuristics;
- Shannon/polarity mapping, SOP/POS covers and affine handling;
- netlist structural hashing, functional gate mapping, rebalance and area recovery;
- five primary candidates, the original candidate ranking and the final output format;
- the original candidate portfolio for long-limit cases by default.

The chosen rank remains the original lexicographic quality order, prioritizing delay-target excess, then area for on-target candidates, then delay and area. The scheduling policy changes which candidates are **attempted**, not the Boolean identities or area/delay evaluation themselves.

## 4. New rule: short-budget incumbent-aware dispatch

Let \(L>0\) be the runtime limit in milliseconds, \(t\) the monotonic elapsed time measured from the beginning of `main`, \(B\) the best fully materialized incumbent, and \(D^*\) the target delay.

Define a conservative short-budget dispatch threshold:

\[
 t_{\mathrm{dispatch}}(L)=0.72L\quad\text{for }0<L\le 250\text{ ms}.
\]

For longer budgets, the primary and legacy thresholds are kept at their historical 75% and 72%, respectively. This is meant to isolate the scheduling experiment and protect Stage 1 performance; it is not a universal optimal threshold.

Primary candidate 0 is always attempted. Before starting any later primary candidate, compare elapsed time against the applicable dispatch cap. For short budgets, give secondary primary candidates a cooperative absolute deadline when invoking `run_synth`. The original `run_synth` checks its deadline periodically within BDD construction and mapping, but the legacy cover routine and some postprocessing paths are not fully interruptible.

For the optional legacy search on short-budget inputs, define

\[
 \mathrm{skipLegacy}(L,B)=
 \bigl(0<L\le250\bigr)\land\mathrm{valid}(B)\land
 \bigl(D(B)\le D^*\bigr).
\]

If this predicate holds, the incumbent is already a legal, on-target circuit and no additional *legacy* candidate is initiated. If no such incumbent exists, legacy search remains potentially available, but a tighter 35%-of-limit dispatch guard prevents starting a long, uninterruptible legacy search late in the budget.

An auxiliary postprocessing dispatch guard limits the *initiation* of optional postprocessing for short-budget cases to the same 72% cap. For longer budgets, old postprocessing thresholds are retained.

This rule is based on **the declared budget and properties of the current incumbent**, not a hardcoded input size, case label or truth-table fingerprint.

## 5. Why correctness is retained

Each candidate netlist is still produced by the same functional transformations as before. The new policy never invents or modifies an output Boolean function; it only prevents certain synthesis attempts or times out an optional candidate.

Assume every candidate returned by the underlying synthesizer is logically equivalent to the input function, and the existing graph parser/validator behaves correctly. At any moment the incumbent \(B\) is one of those completed candidates. If a new candidate is rejected, the incumbent remains the same. Hence by induction over completed candidate evaluations,

\[
\forall k:\quad B_k\equiv F
\]

provided a valid initial incumbent is produced. This is a **conditional correctness argument** for selection policy only; it does not replace the official evaluator's independent checks or prove the other synthesis routines correct. Optional candidate deadlines can reduce solution quality but cannot logically corrupt the incumbent if exceptions are caught and partial candidates are discarded.

## 6. Quality / computational trade-offs

### Benefit

A good valid incumbent becomes available early, allowing immediate output without spending limited time on low-probability legacy improvements. Most importantly, time saved by exact cover processing no longer automatically converts into additional legacy dispatch on the tightest budgets.

### Potential loss

A skipped legacy candidate might have produced a smaller area, a shorter delay or superior cross-output sharing. Thus the policy may lose local quality. This loss must be quantified on both Stage 1 and Stage 2 by comparing paired per-case Area and Delay.

### Remaining timing risk

The first primary candidate is not preempted in order to avoid losing the only known solution. Gate mapping, cover generation, netlist serialization, postprocessing and external evaluator overhead are not all covered by hard deadlines. A threshold of 72% provides *headroom*, not a mathematical guarantee of \(T\le L\).

### Why not simply disable all legacy search?

Some longer-budget cases may benefit from distinct legacy representations and area recovery. The scope of this intervention is deliberately limited to the highest risk class. Eliminating the search globally would confound timeout repair with representation quality regression and undermine the Stage 1/Stage 2 trade-off study.

## 7. Alternative hypotheses and planned ablations

The following comparisons are included in the package:

| Variant | Cover kernels | Portfolio scheduling | What it isolates |
|---|---|---|---|
| `r51` | Frozen old | Frozen old | Original baseline |
| `r71_policy_off` | Both accelerated | Old dispatch | Effect of R7 cover optimization without new scheduler |
| `r71_guard` | Both accelerated | New guarded dispatch | Main Round 7.1 result |
| `r71_legacy_merge` | Old merge / fast greedy | Guarded | Sensitivity to merging optimization |
| `r71_legacy_cover` | Fast merge / old greedy | Guarded | Sensitivity to greedy counting optimization |

The exact-cover A/B unit test is independent from evaluator-level ablations. A nonzero release gate requires inspection; do not treat a partial area sum as a performance gain.

## 8. Limitations and future research

This is a **budget-aware scheduling change**, not a new global Boolean representation or an optimal circuit search algorithm. Subsequent work may extend it using a calibrated estimate \(\widehat{\tau}_j\) of candidate runtime, a measured improvement probability, and a Pareto set for competing area/delay implementations. An eventual objective might select candidates using an expected quality gain per millisecond subject to sufficient remaining budget:

\[
\text{start candidate }j\ \text{only if}\ \widehat{\tau}_j + t + s(L) < L.
\]

The predictive quantities must be learned or estimated on training/development distributions, not fitted to particular public case IDs. Full deadline compliance would require cooperative checks inside *every* long-running subsystem and an early fallback candidate. These are explicitly **not** claimed in Round 7.1.

## 9. Acceptance criterion

A Round 7.1 version becomes a public-data release candidate only if all 50 published cases PASS and meet their delay targets across repeated official runs, with no known Stage 1 functional regression. Official scoring remains unknown and must be evaluated separately when provided. Hidden-case and held-out generalization is still unproven.

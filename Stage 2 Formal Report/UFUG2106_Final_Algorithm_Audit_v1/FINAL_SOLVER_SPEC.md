# UFUG2106 — Final Candidate Algorithm Specification and Source Audit (Phase 1)

**Document type:** source-aligned technical dossier; **not** the final paper and **not** a shortened chronological Trial Log.  
**Inspected implementation:** R10.0 *independent frozen candidate*, `primary/03_frozen_candidate/submission/synth.cpp` plus twelve header files.  
**Primary code SHA-256:** `8c863f1a1c9555ae571948a0424c25642c29c9a9f98f1f3e5f193c6b20f5b15d`.  
**Actually submitted Stage 1 comparator:** `stage1_zeyun/UFUG2106_Stage1/src/synth.cpp`, SHA-256 `cd31f7d2a0540c85dc32277ad97fda0e221e769d323ea4adfec8b69916584550`.  
**Research reference:** Jincan's independent Stage 1 R5.1 and R6.0–6.1 branch, as preserved in the Stage 1 Research Trial Log and GitHub history.  
**Status warning:** the R10.0 delivery README explicitly says **not yet the teammate-integrated final Stage 2 release**. Confirm the actual integrated version before submission.

## 1. What the final candidate actually computes

The program receives a *complete* truth table for a multi-output Boolean function

\[
F=(f_0,\ldots,f_{m-1}):\{0,1\}^{n}\rightarrow\{0,1\}^{m},\qquad 1\le n\le20,
\]

and the case-dependent AND2, OR2 and NOT gate costs. Its output is a topologically ordered, single-threaded netlist using only those gate types. Boolean equivalence is mandatory; circuit delay, synthesis runtime, and positive RAM-limit constraints are separate considerations under the assignment contract.

Write a concrete network as \(G=(V,E,O)\) with ordered outputs \(O=(o_0,\ldots,o_{m-1})\), and let \(a_{\land},a_{\lor},a_{\neg}\) and \(d_{\land},d_{\lor},d_{\neg}\) be the supplied gate areas/delays. Its emitted-gate cost is

\[
A(G)=a_{\land}N_{\land}(G)+a_{\lor}N_{\lor}(G)+a_{\neg}N_{\neg}(G).
\]

If an input or constant has arrival zero, then

\[
T(v)=\begin{cases}T(u)+d_{\neg}, &v=\neg u,\\
\max\{T(u),T(w)\}+d_{\mathrm{op}(v)}, &v=u\land w\text{ or }u\lor w,
\end{cases}\quad
D(G)=\max_{o\in O}T(o).
\]

**Distinguish three optimizations:** Boolean representation changes (Shannon/BDD/covers), gate-DAG mapping changes (sharing, rebalancing and rewriting), and changes to the *search program* (memoization, pruning and budget scheduling). The R10.0 implementation works across all three; they must not be merged into a claim of one universally optimal Boolean algorithm.

### Source anchors

| System layer | Authoritative code (line numbers in frozen copy) | Significance |
|---|---|---|
| Input contract / dispatch | `synth.cpp:948–1033` | Input streaming, resources and default policy resolution |
| Cached truth and influence | `synth.cpp:30–66` | Table materialization and variable-order signal |
| Cached implicants | `synth.cpp:72–235` | R5 symbolic cover cache, gated by support size |
| ROBDD / complemented references | `synth.cpp:237–345` | Immutable cached BDD, variable order, affine signatures |
| Gate mapper | `synth.cpp:349–484` | Structural hashing, Shannon lowering, affine, covers, live pruning |
| Typed DAG / global metrics | `typed_netgraph.hpp:14–214` | Graph parsing, building, rebalancing, De Morgan recovery |
| Candidate competition | `synth.cpp:1032–1120` | Search portfolio, rank, correctness-preserving incumbent |
| Short-budget legacy selection | `synth.cpp:1135–1253` | Optional older representation under guarded budgets |
| Stage 2 structural alternatives | `synth.cpp:1310–1432`, `r8_structural.hpp` | Explicitly selectable exploratory pattern rewrite |
| Cut resynthesis method | `r84_cut.hpp:35–348` | 4-leaf truth signatures, candidate generation and topology-aware root selection |
| R8.2/R8.3/R8.4 policies | `synth.cpp:1434–1688`, `r82_archive.hpp` | Explicit experimental branches; not all active by default |
| **Default R8.6 policy** | **`synth.cpp:1006–1015,1690–1762`** | `extra_sop`: controlled two-branch area-recovery policy |
| R8.5 ablation alternative | `synth.cpp:1765–1842` | Disabled by default when R8.6 is enabled |
| **Default R10.0 follow-up** | **`synth.cpp:1843–1899`** | `repeat_sop` default, replacing R9.1's environment-dependent research setting |
| R9.0 stream bypass | `synth.cpp:950–982`, `r90_stream.hpp` | Exact literals or affine functions for tight large-n cases |
| R8.2.1 RAM fallback | `synth.cpp:989–1004,1113–1131`, `r821_resource.hpp` | Conservative resource admission + low-memory special path |
| Netlist output | `synth.cpp:1896–1901` | Serialize the accepted incumbent; diagnostics to stderr |

## 2. Default execution is a branch graph, not a Round-by-Round pipeline

A recurring source of inaccurate manuscript descriptions is treating the *names* `R8`, `R8.1`, `R8.2`, ..., `R10` as mandatory successive execution stages. The frozen source keeps many historical policies as selectable research branches. **The default path does not execute them all.**

A faithful high-level description for default environment settings is:

```text
read input / limits while probing high-n short-budget structure
 ├─ if n>=18, 0<limit<=250 and complete table is all simple/affine
 │    and a target-feasible circuit is constructed:
 │      emit streaming candidate; return
 ├─ if positive RAM limit fails conservative BDD admission:
 │    try compact low-memory synthesis; if it cannot solve, return error
 └─ standard synthesis
      ├─ build primary ROBDD/mapping candidates with guarded scheduling
      │    ├─ typed-DAG rebalance
      │    └─ timing-aware area recovery, when eligible
      ├─ retain best completed candidate using internal rank
      ├─ skip optional search for zero-area circuit or conservative RAM guard
      ├─ cautiously try a legacy mapping option if allowed
      ├─ selected shallow algebra/phase postprocessing
      ├─ R8.6 area-oriented Shannon + extra-SOP cut search
      │    (R8.3, R8.4, R8.5, R8.1/R8.2 and old R8 are normally off)
      ├─ R10.0 default additional repeat-SOP cut pass
      │    only when admitted and strictly reducing the complete area
      └─ serialize incumbent and exit
```

This overview deliberately does **not** pretend that `R8.6` or `repeat_sop` always runs: both require a sufficiently high *declared* runtime limit, a valid on-target incumbent, and remaining program time. The program may terminate early through other branches. A limit of zero means **no limit in the task specification**, but optional rewrite code uses conditions such as `limit>=1000`; consequently those optional branches do *not* run when that field is zero. This is an implementation policy, not a change to the input contract.

### Dispatch resolution (source-confirmed)

- `UFUG_R86_POLICY` defaults to `extra_sop` and enables R8.6.
- With R8.6 enabled, R8.5, R8.4 and R8.3 are disabled by their early dispatch booleans. The R8/R8.1/R8.2 independent experimental branches are likewise default-off while later policy is active.
- `UFUG_R91_POLICY` defaults to `repeat_sop` in R10.0. `off`, `library`, and `repeat_shannon` remain explicit research modes.
- Other `UFUG_*` environment options exist for ablation. The official evaluator should not be assumed to supply any of them.

## 3. Input and caches: separate semantic information from mapping choices

`main()` initially reads all \(2^n\) truth groups and the case costs. It feeds a lightweight `r90::StreamProbe` during this read if \(n\ge18\), then dispatches fast paths if admissible. On the normal path, `shared_truth()` opens the same file and materializes the \(m2^n\) output bits in a byte vector. This **second file read** is real implementation overhead and must not be hidden in a statement that input is only parsed once.

The code computes a cumulative influence count per variable,

\[
C_i=\sum_{x_{-i}\in\{0,1\}^{n-1}}\ \sum_{j=0}^{m-1}
\mathbf1\left\{f_j(x_{-i},0)\ne f_j(x_{-i},1)\right\}.
\]

`influence-desc` sorts variables by \(C_i\), descending. It is a **representation heuristic**: its score counts cofactor sensitivity, not the weighted gate area and not a mathematically optimal order. Other candidate orders include natural, reverse, rotate, and influence-ascending, subject to dimension and time admissions.

`shared_covers()` computes Quine–McCluskey-like prime implicant data and greedy cover plans for outputs and complements when \(n\le13\). The symbolic plans are independent of the later physical gate mapping and can be cached. They should not be described as exact minimum-cost SOP covers; the greedy gain/(cost proxy) tie-break is only a heuristic, and final gate sharing may alter their physical cost.

## 4. Shannon and complemented ROBDD foundation

For a chosen variable \(x\), define the cofactors \(f_0=f|_{x=0}\), \(f_1=f|_{x=1}\). The exact decomposition is

\[
f=(\neg x\land f_0)\lor(x\land f_1).
\]

If low and high cofactors coincide, the decision vanishes. For a *fixed* variable order, interning the normalized `(variable, low, high)` triple shares identical subfunctions. The frozen code also uses complemented references: a BDD reference carries a node index and a negation bit. Specifically, `flip = hi&1` normalizes the high edge when inserting the node (`synth.cpp:304–311`). This uses a semantic complement in the BDD **without asserting a free physical NOT gate**.

The forward construction stores BDD node and cofactor information in an immutable `FrozenGraph`. When mapping policies share the `influence-desc` order and the cached BDD is within the specified node/dimension cap, a repeated candidate can reuse that BDD. Reusing an immutable function representation avoids duplicate construction work; it does not itself prove a lower physical gate cost.

An affine-function detector carries masks encoding XOR-linear input support and a constant bit. If the two cofactors have opposite parity signatures, recursive composition can recognize an XOR-shaped function. An affine subfunction is realized through a balanced legal-gate XOR construction, never an illegal XOR output gate. One legal formula is

\[
a\oplus b=(a\lor b)\land\neg(a\land b).
\]

The exact equality ensures function preservation, but the best area/delay realization is not fixed by this identity; the mapper also considers structural sharing and arrival times.

**Proof sketch — semantic correctness.** The full recursion is correct by induction on remaining variables: terminals coincide with table values and Shannon selects the proper cofactor. Equal-child elimination and identical-triple merging do not change the represented function. Complement normalization represents \(\neg f\) as an inversion of the same reference. Gate-level emission remains correct provided every local construction uses the stated Boolean identities and every reference is mapped to its intended physical signal.

**Important boundary:** a canonical ROBDD at fixed variable order is a canonical *functional representation*, not a proof of minimum-area AND2/OR2/NOT realization.

## 5. Gate mapping and typed shared DAG

`run_synth()` uses a structural gate intern table keyed by gate operator and fanin IDs. For commutative AND2 and OR2, it sorts the operands. It applies constant folding, idempotence, complement recognition and reused inverters where possible. Only gate outputs that can reach a primary output are serialized; speculative gates from rejected local mappings are pruned.

A `r51::Graph` stores `(op,a,b)` per gate plus the ordered primary output list. Its `Builder` calculates arrival as gates are appended, performs hash-consing, and runs reverse output reachability when `finish()` builds a candidate graph. In particular:

1. **One physical gate, multiple fanouts.** Shared nodes are charged exactly once in output area.
2. **Reassociation is not unrestricted.** `r51::rebalance` flattens same-operator interiors only when fanout accounting (including primary-output references) shows they are private to that use. The resulting associative terms are rebuilt by repeatedly combining the earliest available arrivals.
3. **Timing-aware De Morgan recovery.** `r51::area_recover` computes old required times backward from the deadline and conditionally tests gate-price-motivated dual mappings.
4. **Final accounting.** The actual `Graph::metric()` function counts every gate currently stored in the graph and computes arrival; **it does not prune by itself**. Whole candidate graphs generated by `Builder::finish()` have already been pruned, so scoring them corresponds to the emitted network. Avoid claiming that `metric()` intrinsically re-discovers live nodes.

For a node \(u\), backward required times are initialized at every primary output \(o\) by \(R(o)=\Delta\), then updated along each original edge \(u\to v\):

\[
R(u)\leftarrow\min\{R(u),R(v)-d_{\mathrm{op}(v)}\}.
\]

A shared node inherits the strictest consumer deadline. A De Morgan alternative such as \(u\lor v=\neg(\neg u\land\neg v)\) can trade additional NOTs or delay for a cheaper AND cost under some prices, but local savings may be illusory if an old shared gate remains live. The outer candidate ranking, rather than the local rewrite heuristic, decides whether to retain the transformed entire network.

## 6. Portfolio selection: rank complete realizations, not symbolic expressions

The primary candidate portfolio begins with a delay-oriented `influence-desc` mapping, then selectively tries additional policy combinations, including a natural-order candidate. Extra variable-order diversity is restricted to sufficiently large declared runtime limits and manageable \(n\). When \(n>13\), a pair whose difference only involves a disabled implicant mode is skipped as semantically duplicate.

Every candidate goes through typed rebalance and, when eligible, area recovery. For a valid candidate \(G\), the internal ranking key is essentially

\[
\rho(G)=\big(\max(0,D(G)-\Delta),\ \mathbf1_{D(G)\le\Delta}A(G),\ D(G),\ A(G)\big),
\]

compared lexicographically. (For non-target-feasible circuits the second component is zero in the actual code.) It is an **internal selection heuristic**, not the course's undisclosed numerical grading formula. In particular, a candidate with smaller area but delay above target can lose to an on-target candidate.

The current incumbent is updated only after a candidate is built and a graph metric reports a valid circuit with better rank. A valid completed result is kept even when a later optional search is timed out. The initial candidate itself can consume substantial work; no global hard preemption is proved.

## 7. The central Stage 2 method: bounded, function-based cut resynthesis

The main new structural search is implemented by `r84cut::rewrite`, with policies inherited through the R8.1–R8.6 sequence. It acts on a **mapped gate DAG** rather than only proposing a different order for the original truth-table BDD.

### 7.1 A k-feasible cut is a functional boundary

For a gate root \(r\), choose a set of upstream boundary nodes \(C_r=\{\ell_0,\ldots,\ell_{k-1}\}\) that intercepts every path from \(r\) toward primary inputs. The implemented rewrite fixes \(k\le4\). By treating the cut leaves as *formal* independent Boolean variables, compute the exact local truth signature

\[
M_{r,C}=\sum_{s=0}^{2^k-1}f_{r,C}(s)2^s,\qquad 0\le M_{r,C}<2^{2^k}.
\]

At four leaves the entire signature has 16 bits. In the actual surrounding network the leaf signals may be correlated; checking all \(2^k\) formal assignments is **stronger than necessary but sufficient** to guarantee equality on every realizable combination.

`r84_cut.hpp:132–151` recursively evaluates a cone with the formal leaf masks. It throws an error if a primary input is reached without passing a designated leaf; that is an invalid frontier, not a Boolean guess.

### 7.2 Cut enumeration and candidate mapping

For each DAG node, cuts are formed from the fanin cuts by sorted set union (or propagated through unary NOT), retaining only feasible cardinalities. The engine retains a bounded set of cuts per node (at most nine entries including the trivial cut, under the implemented selection procedure) rather than enumerating all cuts exhaustively. Thus **"four-feasible" does not mean an exhaustive search over all four-leaf cuts**.

Given the local truth signature, the engine constructs several exact **alternative physical expressions**:

- SOP with prime implicants and one of two deterministic cost proxies;
- complemented SOP (equivalently a POS-flavored realization);
- Shannon decompositions with several leaf-order rotations.

All alternatives are lowered to AND2/OR2/NOT using `r51::Builder`, which also structurally hashes identical gates. This candidate portfolio is neither a complete Boolean-expression enumerator nor a guarantee of minimum local cost.

### 7.3 Private cone reclaim and timing filter

A local candidate \(H\) is assessed against an estimated area reclaim \(R_{\text{private}}\): traverse the old root's private cone but do not count subgates with multiple uses as removable. The local score resembles

\[
\widehat{\Delta A}_{\mathrm{local}}(H)
 =A_{\mathrm{candidate\ cone}}(H)-R_{\mathrm{private}}.
\]

If a candidate's newly built arrival exceeds the *old graph's* `needed[root]`, it is rejected locally. Candidates satisfying the time filter compete by negative estimated local area change (except an explicitly selected `choices` ablation that also permits zero-change candidates).

**This is not the actual globally realized area change.** Builder interning can reuse an existing signal, and a locally removed gate may remain referenced by another output. The engine subsequently remaps the remainder of the DAG, invokes `Builder::finish()` to prune unreachable gates, and returns a complete candidate. Its calling policy then recomputes the complete candidate's Area and Delay and decides whether it beats the previous incumbent.

### 7.4 Priority-ranked roots and actual work quota

A search run may face many eligible roots but a fixed work allowance. The frozen R8.4-style engine ranks roots by an explicit heuristic:

\[
P(r)=16a(r)+8\sum_{u\in\mathrm{fanin}(r),\;\mathrm{use}(u)=1}a(u)
     +\min(8,\max(0,R(r)-T(r))).
\]

(Inputs do not contribute private predecessor-gate area.) This combines the root's charged area, privately owned immediate predecessors and bounded timing slack. It is a **priority proxy**, not the exact gain from cut rewriting.

With `priority_topq`, the code first selects the top quota by this priority, **then visits selected IDs in original topological order**. Selecting Top-Q globally is not the same as taking the first Q topologically from a larger ranked pool. This distinction was empirically tested in R8.4 and is part of the final design rationale.

A deterministic `work_roots` budget bounds the number of complete roots explored. A wall-clock deadline is checked periodically as an emergency guard; it is not a precise asynchronous cancellation. If the search stops, remaining nodes are mapped without further optimization so the builder can still produce a complete graph.

## 8. R8.6 default policy: search resource allocation is part of the algorithm

Under ordinary default environment settings, R8.6 is the active structured search. Its policy is `extra_sop`. It is admitted only if the declared runtime limit is at least 1000 ms, the incumbent is valid and already meets delay, and the synthesizer has consumed less than 65% of the declared limit at entry.

Let \(B\) denote the declared program limit in milliseconds. The search-wide time allowance is

\[
B_{\mathrm{search}}=\min(360,0.15B).
\]

The policy tries **two alternatives from the same starting incumbent**:

1. A Shannon-cut alternative using the base root cap.
2. An SOP-cut alternative with an additional 300 root quota (capped at 1500).

The default base root cap is 900, or at most 600 when `limit<=2000 && m>=20` (unless deliberately overridden by an experiment environment variable). Each branch gets a nominal budget no larger than \(\min(180,0.54 B_{\mathrm{search}})\), also subject to the residual global search budget and a whole-program 77% admission guard. The `extra_sop` default does **not** automatically reclaim unused first-branch time: reclaim is a separate policy tested in R8.6.

The two alternatives are **compared to the same pre-search incumbent** rather than automatically chaining Shannon's output into SOP. A candidate must be a valid entire graph, satisfy \(D\le\Delta\), and satisfy `r82::eligible(original, candidate, target,"area")`. This eligibility condition accepts either strict area improvement or unchanged area with lower delay. The best eligible alternative is selected by area, then delay. The method is therefore best described as an **area-priority, target-feasible full-network selection**, not as a theorem that each local rewrite monotonically improves area.

The R8.6 factorial study (see Trial Log v3 and archived raw feedback) found that increasing root quota specifically for SOP helped, whereas time reclaim alone did not improve the studied 50-case area sum. That experiment supports **this resource-allocation decision for the observed workload**; it does not prove that more runtime can never help an unknown function.

## 9. R10.0 final improvement: an additional, guarded SOP resynthesis pass

The R9.1 experiments found that an additional SOP resynthesis pass could yield further area gains on a *completed* candidate; the research-only R9.1 release required `UFUG_R91_POLICY=repeat_sop` to activate it. R10.0 changes the **default** selection so that the standalone executable automatically uses `repeat_sop` with no custom environment variables. The `r91lib` template library is retained as an opt-in research mode, **not** part of the default.

Admission predicates (all required):

- Mode is one of `library`, `repeat_sop`, `repeat_shannon`, and is not `off`;
- declared runtime limit \(B\ge1000\);
- current incumbent has valid graph metrics and \(D\le\Delta\);
- elapsed time \(t\) leaves enough budget under the 82%-of-declared-limit reserve.

The last-pass allowance is exactly

\[
b_{\mathrm{last}}=\min\big(90\ \text{ms},\ 0.06B,\ 0.82B-t\big),
\]

and the pass is skipped when \(b_{\mathrm{last}}<8\) ms. Default `maxroots` is 160 (the research environment may override it to 20–400). For `repeat_sop`, it invokes

```cpp
r84cut::rewrite(source, costs, target,
                "sop", allowance, 1500,
                "priority_topq", cap);
```

with `source` the incumbent **after** the upstream search. Unlike R8.6's parallel alternatives from the same baseline, this is a *sequential follow-up on the selected network*. The proposed output is accepted if and only if

\[
\mathrm{valid}(G')\land D(G')\le\Delta\land A(G')<A(G_{\mathrm{old}}).
\]

This is a **strict full-network area decrease**: equal-area delay improvements from the last pass alone are not accepted. If any predicate fails, retain the previous candidate.

**Crucial conceptual distinction:** R10.0's main innovation relative to R9.1 is the *deployment/default-policy correction*, not a brand-new cut algorithm. The algorithmic method being deployed includes earlier Stage 1 and Stage 2 work; the final release adjustment makes the selected repeat-SOP policy actually run under the plain course interface.

## 10. Two resource-specialized branches (do not overclaim)

### 10.1 R9.0 streaming short-limit bypass

For \(n\ge18\) and \(0<B\le250\), the program scans all \(2^n\) truth-table groups, attempting to recognize whether **every** output is a constant/literal or whether **every** output is affine over \(\mathrm{GF}(2)\). Because every input row is observed, recognition is exact for these families; it is not a random sample or a heuristic partial-table extrapolation.

A literal/constant output can be emitted without a general ROBDD. An affine output of the form

\[
f_j(x)=c_j\oplus\bigoplus_{i\in S_j}x_i
\]

is built using legal-gate XOR subexpressions (with a ready-time priority queue). It returns early **only** when the emitted graph is valid and within target delay. Other functions fall through to normal synthesis, so the bypass does **not** guarantee every large, short-limit input passes.

The fresh local smoke check `stream_affine_n18_limit250.txt` triggered `R90_SHORT_PATH kind=stream_affine`, produced area 136 and delay 25 on a constructed 18-input parity test. This is a **new local synthetic test**, not an official course-case result.

### 10.2 R8.2.1 positive-RAM-limit path

For positive `ram_kb`, `r821::bdd_admitted` compares the cap to a **conservative** memory reservation estimate for the eager BDD implementation. On rejected admission it tries a packed, support-limited alternative. If that alternative cannot produce a valid target-feasible circuit, the program explicitly exits with code 14, rather than launching memory-hungry BDD construction anyway.

After the first feasible candidate, the solver can also skip optional future heavy searches if its conservative memory screening indicates insufficient headroom. This is a resource-risk mitigation strategy; the code comments explicitly deny that it proves the process's actual peak resident memory remains below the limit. A later report must not claim universally RAM-safe behavior.

## 11. Quantitative facts independently reconfirmed in this audit

**Exact archive integrity.** The original evidence collector's `MANIFEST.json` contains 26 files; all 26 extracted files match its recorded SHA-256 values (`PROVENANCE_CHECK.json`). The R10.0 frozen source matches the copy embedded in the independent official feedback ZIP.

**Compilation and independent local checks.** Zeyun's Stage 1 source and the R10.0 frozen candidate both compiled under GCC/C++17 in this container. The independent `run_source_smoke_checks.py` constructed five different complete functions under two runtime-limit settings and checked each solver's netlist across all input assignments: **20/20 source-run equivalence checks passed**. The exercise includes examples on which R10.0 has a larger area than Stage 1. These are small synthetic checks, not a general performance ranking or replacement for official results.

**R10.0 original course evaluator archives.** Independently parsing the official R10 feedback's original case rows produced:

| Bank | Run | PASS | Target met | Area sum | Delay sum | Median program runtime |
|---|---:|---:|---:|---:|---:|---:|
| Stage 1 | 1 | 25/25 | 25/25 | 525,582 | 1,212 | 188.464 ms |
| Stage 2 | 1 | 25/25 | 25/25 | 493,965 | 1,170 | 120.158 ms |
| Stage 1 | 2 | 25/25 | 25/25 | 525,582 | 1,212 | 189.051 ms |
| Stage 2 | 2 | 25/25 | 25/25 | 493,965 | 1,170 | 122.934 ms |

These are original official-feedback measurements **for this frozen candidate**. They do not independently demonstrate the actual integrated team release or hidden cases, and the sum of per-case delays has no direct mathematical interpretation as one circuit delay.

**Three-method matched local batch already available.** `research/01_normalized_data/matched_case_metrics.csv` contains 300 paired observations over 50 public cases, two repeats and three methods (`Z1` actually submitted Stage 1, `J51` independent research, `S100` R10). This is a distinct WSL batch from the R10 official feedback; its time medians are not interchangeable with the table above. In one paired run, Z1 has all 50 PASS and total area \(589{,}023+555{,}221=1{,}144{,}244\); R10 has all 50 PASS and \(525{,}582+493{,}965=1{,}019{,}547\). The difference is **124,697**. J51 has 24/25 PASS on Stage 2 (stage2/case_016.txt fails) and thus must not be compared by summing only its 49 valid areas as if it passed all 50.

These figures provide an experimental starting point for later mandatory comparison; they do not require any new conclusion about method superiority on every input. Recompute every final manuscript number from the selected, clearly identified batch.

## 12. Critical points for the eventual Method section

To explain the final solution completely, a reader must see **all** of the following relations, not merely the names of algorithms:

1. **Boolean representation:** the complete truth table defines the function; complemented ROBDD and implicant plans expose different legal factorizations.
2. **Physical realization:** the mapper lowers all abstract operations to AND2/OR2/NOT, shares identical gates, and measures actual circuit delay and area.
3. **Local optimization:** 4-leaf cut signatures permit completely new equivalent logic around a chosen gate, independent of how the original BDD happened to map that cone.
4. **Global graph economics:** shared fanout, dead-cone pruning and full candidate metric checks separate *local rewrite plausibility* from *accepted physical benefit*.
5. **Search as a finite resource:** root priority, per-branch quota, fallback and runtime headroom determine whether optimizations can be attempted safely enough in practice.
6. **Final deployment policy:** R8.6's extra SOP root allocation followed by a bounded repeat-SOP pass is the chosen ordinary-budget default; alternate policies are retained research options, not stages that always run.
7. **Safe, narrow resource exceptions:** streaming affine/literal recognition and compact memory-admitted synthesis treat particular difficult resource conditions without pretending they solve all inputs under arbitrary caps.
8. **Independent evidence:** official 50-case comparison, actual per-case regressions, R8.6/R9.1/R10.1 ablations and negative cases explain the choice; the trial log remains the full historical source.

The next work phase should turn this *verified specification* into a code-backed mathematical proof/limitation ledger, then compare the actually submitted Stage 1 implementation with this candidate by functional blocks, without assuming they share a direct copy-and-edit lineage.

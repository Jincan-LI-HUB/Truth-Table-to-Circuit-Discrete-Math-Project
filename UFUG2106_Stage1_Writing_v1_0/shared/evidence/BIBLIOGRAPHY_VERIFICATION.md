# Literature attribution and DOI verification — 2026-11-12

The classical sources below were cross-checked against publisher or bibliographic records. These sources motivate established theory; they do not prove that our student implementation matches external algorithms.

| Citation key | Verified facts | Verification URL |
|---|---|---|
| `shannon1949` | C. E. Shannon, *The Synthesis of Two-Terminal Switching Circuits*, Bell System Technical Journal 28(1), 59–98, 1949 | https://ieeecs-media.computer.org/assets/pdf/20_S_chapter.pdf |
| `bryant1986` | R. E. Bryant, *Graph-Based Algorithms for Boolean Function Manipulation*, IEEE Transactions on Computers 35(8), 677–691 (1986), DOI 10.1109/TC.1986.1676819 | https://dblp.org/rec/journals/tc/Bryant86.html |
| `mishchenko2006` | A. Mishchenko, S. Chatterjee, R. K. Brayton, *DAG-aware AIG rewriting: A fresh look at combinational logic synthesis*, DAC 2006, 532–535, DOI 10.1145/1146909.1147048 | https://doi.org/10.1145/1146909.1147048 |
| `brayton1984` | Brayton et al., *Logic Minimization Algorithms for VLSI Synthesis*, Kluwer, 1984 | Original book title and year carried from existing bibliography; no new publisher verification in this round |
| `abc` | Berkeley ABC open-source synthesis and verification software | https://github.com/berkeley-abc/abc |
| `coursehandout` | Instructor-distributed private assignment specification | Private source, not a public literature reference |

## Attribution boundaries

- Shannon expansion and ROBDD canonicality are classic results, not new mathematical inventions here.
- The 2006 DAG-aware AIG-rewriting paper works primarily with AND-Inverter Graphs. Its node-count results cannot directly be equated with this assignment's weighted AND2/OR2/NOT area metric.
- We claim integrated implementation choices, evidence quality and engineering trade-off decisions, not priority over prior synthesis theory.
- Both manuscripts continue to use an inline self-contained bibliography; `references.bib` is supplied as an editable counterpart, not compiled into these drafts.

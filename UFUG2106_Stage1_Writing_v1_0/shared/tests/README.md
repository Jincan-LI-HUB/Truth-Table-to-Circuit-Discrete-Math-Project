# Independent typed-DAG property checks

This auxiliary test is **not part of** the frozen synthesizer, nor does it substitute for the official evaluator. It verifies the implementation imported from the frozen Round 5.1 `typed_netgraph.hpp` using independently computed truth tables on 2,000 pseudorandom DAGs (2–6 inputs, 1–3 outputs). Four transformations are checked for each case: serialize/parse, rebalance, area recover, and rebalance followed by area recover. Each generated input assignment is exhaustively simulated. The seed is fixed in the test source.

`bash run.sh` requires g++ with C++17. See test_results.txt.

Scope: randomized checks strengthen evidence but are not a proof for arbitrary DAGs, and they do not cover the full portfolio, algebraic phase mapper, evaluator, or binary output format.

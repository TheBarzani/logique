# Input datasets

- `graphs/benchmarks/`: original DIMACS benchmark instances.
- `graphs/execution/`: linear graphs extracted from the historical execution directory.
- `graphs/dev_data/` and `graphs/single_benchmark/`: preserved development inputs.
- `graphs/teaching/`: maintained small tutorial inputs.
- `boolean/teaching/`: deterministic structural Verilog examples.

The EPFL manifest is packaged as `logique.benchmarks/epfl.json`; downloaded AIGER, Verilog, and license files belong in the configured cache. Acquisition verifies pinned SHA-256 hashes even when using an existing cache.

Historical input provenance and original locations remain available through the [archive index](../archive/index.json). Generated circuits, tables, and plots are outputs and belong under `results/`.

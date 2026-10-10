# Input datasets

- `graphs/benchmarks/`: original DIMACS benchmark instances.
- `graphs/execution/`: linear graphs extracted from the historical execution directory.
- `graphs/dev_data/` and `graphs/single_benchmark/`: preserved development inputs.
- `graphs/teaching/`: maintained small tutorial inputs.
- `boolean/teaching/`: deterministic structural Verilog examples.

The EPFL manifest is packaged as `logique.benchmarks/epfl.json`; downloaded AIGER, Verilog, and license files belong in the configured cache. Acquisition verifies pinned SHA-256 hashes even when using an existing cache.

Historical inputs and their original locations remain available on [`legacy/vcgc`](https://github.com/TheBarzani/logique/tree/legacy/vcgc). Generated circuits, tables, and plots that are not final belong under ignored `dump/`.

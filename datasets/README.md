# Input datasets

- `graphs/benchmarks/`: original DIMACS benchmark instances.
- `graphs/execution/`: linear graphs extracted from the historical execution directory.
- `graphs/dev_data/` and `graphs/single_benchmark/`: preserved development inputs.
- `graphs/teaching/`: maintained small tutorial inputs.
- `boolean/teaching/`: deterministic structural Verilog examples.
- `graphs/dimacs/`: DIMACS graph-coloring instances of the medium and large tiers, as downloaded from the
  graph-coloring collection with an appended `x colors` record (the known chromatic number).
- `graphs/small/` and `graphs/families/`: generated graphs of the small tier and the planted families (fixed seeds).
- `graphs/tiers.json`: the tier of every graph (small; medium when its colorings can be counted within the study's
  budget; large otherwise), with its source, SHA-256, size, number of colorings and witness status;
  `graphs/witnesses.json` holds one proper coloring per graph where one is known. Both are written by
  `tools/build_graph_tiers.py` (`--fetch` downloads again and checks the upstream SHA-256).

The EPFL manifest is packaged as `logique.benchmarks/epfl.json`; downloaded AIGER, Verilog, and license files belong in the configured cache. Acquisition verifies pinned SHA-256 hashes even when using an existing cache.

Historical inputs and their original locations remain available on [`legacy/vcgc`](https://github.com/TheBarzani/logique/tree/legacy/vcgc). Generated circuits, tables, and plots that are not final belong under ignored `dump/`.

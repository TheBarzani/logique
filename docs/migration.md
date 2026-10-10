# Migration from VCGC to Logique

The project, Python package, and CLI are now named `logique`. Imports, environment variables, and commands have changed. Historical modules and script entry points are preserved on `legacy/vcgc`, without compatibility aliases.

| Previous entry | Maintained replacement |
| --- | --- |
| `VCPNetwork` / `vcgc.network` | `ColoringProblem`, `read_dimacs`, `problem.to_networkx()` |
| `BooleanFunction` / `vcgc.boolean` | `encode_coloring(problem)` and `encoding.verilog()` |
| `Synthesizer` / `vcgc.synthesis.Synthesizer` | `logique.synthesis.synthesize(source, method=...)` |
| `vcgc.benchmark_synthesis` | `synthesis`, `verification`, `workspace`, `benchmarks` |
| `vcgc.boolean_visuals` | `logique.visualization.boolean` |
| Grover glue functions in `vcgc.circuit` | `coloring_preparation()` and `grover_circuit()` |
| Benchmark generation scripts | `logique benchmark run --config FILE` |
| Plotting scripts | `logique plot TABLE --metric METRIC --output FILE` |
| Notebook runner script | `logique notebook run NOTEBOOK` |
| `data/benchmarks/` | `datasets/graphs/benchmarks/` |
| `data/execution/*.col` | `datasets/graphs/execution/` |
| Original VCGC `examples/` and `experiments/` | `legacy/vcgc` branch; maintained notebooks in `experiments/` |
| `data/output/` and historical result directories | `legacy/vcgc` branch |
| Dependency submodules at the root | `external/abc/`, `external/caterpillar/`, `external/mockturtle/`, `external/saha-belletti/`, `external/tweedledum/` |
| `native/boolean_synthesis/` | `external/native/boolean_synthesis/` |
| `notebooks/` | `experiments/` |
| `results/` | `dump/` (ignored non-final results) |
| New generated results | `dump/` |

The original `main` branch is preserved as [`legacy/vcgc`](https://github.com/TheBarzani/logique/tree/legacy/vcgc). The duplicate `archive/` directory and its integrity checker have been removed from this branch. Moving the submodules into `external/` preserves their URLs and checked-out revisions. Run `git submodule sync --recursive` and `git submodule update --init --recursive` after updating an existing checkout. Manuscript files remain local and ignored.

## Scientific behavior changes

The maintained encoding uses `(colors - 1).bit_length()` consistently, with a one-bit representation for one-color problems. It includes isolated vertices, rejects unused color codes, and enforces precolors. Previous paths disagreed on bit widths, omitted isolated inputs, and did not consistently implement the full coloring predicate.

Grover construction now uses an explicit phase oracle with restored workspace, and reflects about the same preparation used for initialization. Multiple iterations share the same circuit contract. The old single- and multi-iteration glue functions differed in phase-kickback initialization.

The DIMACS reader accepts whitespace and blank lines and reports malformed records and mismatched counts. Every read constructs a fresh problem. Input mappings are deterministic and shared with result decoding.

These changes can alter circuits and metrics. New results are identified separately; historical paper data remains unchanged. Compare current methods using the new configurations, not by combining historical and corrected measurements into an unlabeled table.

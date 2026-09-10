# Migration from the original layout

The toolkit keeps the `vcgc` package name but changes its imports and commands. Historical modules and script entry points are archived, without compatibility aliases.

| Previous entry | Maintained replacement |
| --- | --- |
| `VCPNetwork` / `vcgc.network` | `ColoringProblem`, `read_dimacs`, `problem.to_networkx()` |
| `BooleanFunction` / `vcgc.boolean` | `encode_coloring(problem)` and `encoding.verilog()` |
| `Synthesizer` / `vcgc.synthesis.Synthesizer` | `vcgc.synthesis.synthesize(source, method=...)` |
| `vcgc.benchmark_synthesis` | `synthesis`, `verification`, `workspace`, `benchmarks` |
| `vcgc.boolean_visuals` | `vcgc.visualization.boolean` |
| Grover glue functions in `vcgc.circuit` | `coloring_preparation()` and `grover_circuit()` |
| Benchmark generation scripts | `vcgc benchmark run --config FILE` |
| Plotting scripts | `vcgc plot TABLE --metric METRIC --output FILE` |
| Notebook runner script | `vcgc notebook run NOTEBOOK` |
| `data/benchmarks/` | `datasets/graphs/benchmarks/` |
| `data/execution/*.col` | `datasets/graphs/execution/` |
| Original `examples/` and `experiments/` | `archive/research/`; four curated notebooks in `notebooks/` |
| `data/output/` and historical result directories | `archive/research/data/` |
| New generated results | `results/` |

The complete [path and hash inventory](../archive/index.json) covers historical artifacts. Submodule paths and revisions remain unchanged; manuscript files remain local and ignored.

## Scientific behavior changes

The maintained encoding uses `(colors - 1).bit_length()` consistently, with a one-bit representation for one-color problems. It includes isolated vertices, rejects unused color codes, and enforces precolors. Previous paths disagreed on bit widths, omitted isolated inputs, and did not consistently implement the full coloring predicate.

Grover construction now uses an explicit phase oracle with restored workspace, and reflects about the same preparation used for initialization. Multiple iterations share the same circuit contract. The old single- and multi-iteration glue functions differed in phase-kickback initialization.

The DIMACS reader accepts whitespace and blank lines and reports malformed records and mismatched counts. Every read constructs a fresh problem. Input mappings are deterministic and shared with result decoding.

These changes can alter circuits and metrics. New results are identified separately; historical paper data remains unchanged. Compare current methods using the new configurations, not by combining historical and corrected measurements into an unlabeled table.

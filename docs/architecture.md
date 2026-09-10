# Architecture

VCGC has two input paths: a graph-coloring problem is encoded as structural Verilog, while a Boolean benchmark supplies Verilog or combinational AIGER directly. Both use the same synthesis, verification, and export pipeline.

| Package | Responsibility |
| --- | --- |
| `coloring` | Validated graph inputs, DIMACS parsing, deterministic predicate encoding |
| `synthesis` | Native and tweedledum adapters, result objects, optional Saha-Belletti adapter |
| `circuits` | Gate-record conversion, state preparation, oracle and Grover construction |
| `verification` | Independent Boolean evaluation and coherent phase/restoration checks |
| `workspace` | Conditional-state facts and the separately verified borrowing example |
| `benchmarks` | Pinned input acquisition, configurations, runners, metrics, exports, provenance |
| `visualization` | Graph, logic, circuit, and result figures |
| `execution` | Local measurement analysis and optional explicit IBM submission/retrieval |
| `cli` | Argument parsing and thin library calls |

## Contracts

`ColoringProblem` uses sorted integer vertex labels and zero-based colors. DIMACS declares labels 1 through N; programmatic problems may use noncontiguous labels. `ColoringEncoding` assigns consecutive inputs per vertex, least-significant color bit first, including isolated vertices. One-color problems use one input bit constrained to zero. Empty predicates can be synthesized, but Grover search requires at least one input.

The predicate checks edge inequalities, unused color codes, and precolors. `problem.is_valid()` is the independent classical reference. Verilog generation does not import a quantum library.

`SynthesisResult.circuit` is the raw clean-output computation and may retain intermediate workspace or phase. `oracle()` appends arbitrary XOR targets and computes/copies/uncomputes. `phase_oracle(output=0)` marks one output and restores computational workspace. Wire roles and source/mapped networks remain explicit in metadata.

`grover_circuit()` uses the phase wrapper and a reflection about its supplied preparation. `coloring_preparation()` prepares valid colors and fixes precolors. Comparison runs use an all-bitstrings preparation for both VCGC and Saha-Belletti, so initialization is not an uncontrolled difference between methods.

The native protocol remains JSON over stdin/stdout with diagnostics on stderr. C++ input parsing, mapping, serialization, and request handling are separate. Existing Caterpillar compatibility overlays remain limited to the two documented cleanup corrections.

## Dependency boundaries

The core import needs no quantum or plotting stack. Library packages never import scripts or notebooks. Plotting and hardware imports stay inside their optional features. Installed manifests use package resources; native executables and caches use explicit paths rather than positions relative to `__file__`.

The archive is not an importable compatibility layer. There are no old API aliases: use the migration guide when updating external code.

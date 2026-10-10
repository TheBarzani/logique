# Architecture

Logique accepts graph-coloring problems and general Boolean functions. Coloring predicates use structural Verilog; Boolean functions can supply Verilog, combinational AIGER, or an ordered expression. The expression frontend preserves tweedledum's original logic-tree construction for reproducible specialized XAG synthesis.

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

`grover_circuit()` uses the phase wrapper and a reflection about its supplied preparation. `coloring_preparation()` prepares valid colors and fixes precolors. Comparison runs use an all-bitstrings preparation for both Logique and Saha-Belletti, so initialization is not an uncontrolled difference between methods.

Historical paper replay explicitly uses `edge_coloring_expression()` and `synthesize_expression()`, followed by `kickback_grover_circuit()`. This path ignores precolors and unused binary color codes, reproduces the original valid-color initialization and H-based diffusion, and applies the internally cleaned XAG once with an output in `|minus>`. `verify_kickback_oracle()` checks both initial target bits, including phases and workspace restoration. The baseline adapter can explicitly preserve labels and measurements for replay; its default behavior still normalizes labels and omits measurements. The paper runner saves the original measurement accounting separately from a table that measures every method's data register.

The native protocol remains JSON over stdin/stdout with diagnostics on stderr. C++ input parsing, mapping, serialization, and request handling are separate. Existing Caterpillar compatibility overlays remain limited to the two documented cleanup corrections.

## Dependency boundaries

The core import needs no quantum or plotting stack. Library packages never import scripts or notebooks. Plotting and hardware imports stay inside their optional features. Installed manifests use package resources; native executables and caches use explicit paths rather than positions relative to `__file__`.

Dependency checkouts and the C++ bridge live under `external/`; maintained notebooks live under `experiments/`. Non-final generated artifacts go under ignored `dump/`. Historical VCGC code and results live on the `legacy/vcgc` branch. There are no old API aliases: use the migration guide when updating external code.

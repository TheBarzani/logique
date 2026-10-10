# Experiment configurations

`boolean_teaching.json` compares all five methods on three small local functions. `coloring_comparison.json` compares full Grover circuits on an unprecolored graph. `epfl.json` uses the pinned cache populated by `logique datasets fetch --cache .cache/epfl`.

Paths in JSON are relative to the configuration file. Explicit command-line overrides take precedence; an output supplied on the CLI is relative to the current directory. Omit `output` to allocate a unique directory under the working directory's `dump/`.

Fields: `inputs` (required list), `methods`, `parameters` (synthesis keyword arguments), `colors` (optional DIMACS override), `kind` (`synthesis`, `comparison`, or `phase_oracle`), `iterations`, `seed`, `validation` (`auto`, `exhaustive`, `sampled`, or `none`), `samples`, and `output`. Unknown top-level fields are rejected. Saha-Belletti methods use `sb_original`, `sb_simple`, `sb_minimal`, and `sb_balanced` and require `kind: comparison`.

`coloring_phase_oracle_comparison.json` runs all five methods on the nine paper
graphs, preserving file color counts and precolors. `auto` validates exhaustively
through 12 inputs and uses explicitly labeled seeded samples above that limit.
Phase runs check the actual logical circuit's phase and restoration against the
independent graph predicate. They export logical and U/CX QPY circuits and two
metric rows per case. `basis_gates` is `["u", "cx"]` and `optimization_level`
defaults to 1. These fields apply to phase runs; no hardware routing is performed.
Select `--metric-level logical` or `--metric-level decomposed` when plotting a
phase run. Failed runs preserve diagnostics and completed rows.

Saha-Belletti cannot honor precolors; such inputs are rejected for that adapter rather than silently comparing different problems. Historical datasets on `legacy/vcgc` retain their original precolors.

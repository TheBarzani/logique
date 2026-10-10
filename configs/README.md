# Experiment configurations

`boolean_teaching.json` compares all five methods on three small local functions. `coloring_comparison.json` compares full Grover circuits on an unprecolored graph. `epfl.json` uses the pinned cache populated by `logique datasets fetch --cache .cache/epfl`.

Paths in JSON are relative to the configuration file. Explicit command-line overrides take precedence; an output supplied on the CLI is relative to the current directory. Omit `output` to allocate a unique directory under the working directory's `dump/`.

Fields: `inputs` (required list), `methods`, `parameters` (synthesis keyword arguments), `colors` (optional DIMACS override), `kind` (`synthesis` or `comparison`), `iterations`, `seed`, `validation` (`exhaustive`, `sampled`, or `none`), `samples`, and `output`. Unknown top-level fields are rejected. Saha-Belletti methods use `sb_original`, `sb_simple`, `sb_minimal`, and `sb_balanced` and require `kind: comparison`.

Saha-Belletti cannot honor precolors; such inputs are rejected for that adapter rather than silently comparing different problems. Historical datasets on `legacy/vcgc` retain their original precolors.

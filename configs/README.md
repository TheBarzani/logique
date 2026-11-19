# Experiment configurations

`boolean_teaching.json` compares all five methods on three small local functions. `coloring_comparison.json` compares full Grover circuits on an unprecolored graph. `epfl.json` uses the pinned cache populated by `logique datasets fetch --cache .cache/epfl`.

Paths in JSON are relative to the configuration file. Explicit command-line overrides take precedence; an output supplied on the CLI is relative to the current directory. Omit `output` to allocate a unique directory under the working directory's `dump/`, named `MMDDHHMMSS-descriptive-name` using local time. Same-second collisions receive a numeric suffix. Explicit paths are used exactly as supplied; use the same naming convention when specifying a top-level dump path.

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

`corrected_comparison_pilot.json` runs the controlled study (`kind: study`) on
K3, K5 and myciel3, the pilot graphs of the revision protocol. Every method,
including the Saha–Belletti variants, is evaluated under three regimes: `R1`
(Hadamard preparation, complete predicate), `R2` (valid-color preparation,
complete predicate) and `R3` (valid-color preparation without domain checks).
`corrected_comparison.json` applies the same settings to the nine graphs of
the manuscript, with a count budget large enough for myciel4, and adds
Caterpillar's four XAG and eager strategies to the five methods.
`tree_shapes_input.json`, `tree_shapes_rounds.json` and
`tree_shapes_timed.json` run the XAG flow on the same graphs with a balanced
encoder, each shape of its final conjunction and scheduling, and
`scheduled_baselines.json` runs the four baselines with the same scheduling, so
that the T-depth comparison of the shapes is fair. They omit routing.
`repriced_comparison.json` repeats the nine-graph study without routing, to
reprice the measurement-based column after the pair detector was extended.
`best_fit_depths*.json` price the T-depth of the best-fit oracles that exceed the
default pricing limit (myciel3 to myciel5), with a limit of 12 million gates.
`routed_grid_*.json` route a Grover iteration on a square-grid device that grows
with the circuit (`route_backend: grid`, Nighthawk topology): the XAG flow and the
baselines as in the study, the baselines scheduled, and the XAG flow with each
conjunction shape, scheduled.
`balanced_methods.json` and `scheduled_methods.json` run the other Logique
methods with the balanced encoder, without and with scheduling, so that every
method's T-depth is reported before and after optimization (the nine-graph
study gives the unoptimized versions).
Study fields:

- `regimes`: any of `R1`, `R2`, `R3`.
- `mcx_policies`: names from `logique.benchmarks.costs.MCX_DECOMPOSITIONS`;
  `throwaway_tree` applies only to mirrored compute blocks, and gates without a
  mirror use the restoring tree.
- `pricing`: `static` and/or `measurement` (measurement-based uncomputation of
  logical-AND pairs, reported as a separate metric level).
- `optimization_profile`: how Logique predicates are optimized: `none` (the
  encoded network as read, for every method), `refactor` (the native bridge's
  refactoring, which `aig_bennett` skips), `balanced` (balanced conjunction and
  disjunction trees in the encoder), `mc` (tweedledum's multiplicative-complexity
  reduction) or `balanced_mc` (both); the last three also refactor.
  `balanced_rounds` and `balanced_timed` shape the final conjunction of the
  balanced encoder: pairing constraints by the round of an edge colouring, or
  always joining the two expected to be ready first (same gates, other tree).
  Baselines are unaffected.
- `schedule` (default `false`): reorder the commuting gates of every oracle,
  synthesized or baseline, to a lower T-depth with the same gates
  (`logique.benchmarks.scheduling`); rescheduled Logique oracles are verified
  again, and `structure.scheduled` records whether the reordering applied.
  An order is kept only when it prices to a lower T-depth than the original.
- `description` (default `corrected-study`): names the run folder
  `dump/MMDDHHMMSS-<description>`.
- `targets`: any of `logical`, `toffoli`, `fault-tolerant`, `routed`
  (FakeTorino, with the fixed `seeds`).
- `rotation_budget`: whole-algorithm error budget shared by all rotations.
- `iterations`: `"optimal"` (from an exact solution count, when the count
  finishes within `limits.count_budget`), an integer, or a list of integers.
- `relative_phase_mirrored`: give mirrored compute blocks relative-phase
  Toffoli gates, as the XAG flow already has.
- `relative_phase_pairs` (default `true`): after decomposition, replace every
  Toffoli gate and its matching uncomputation by RCCX and its inverse when no
  gate in between changes their three wires, in the oracle and the diffusion
  operator of every method. The unitary is unchanged.
- `drop_precolors`: remove precolors so that every method solves the same
  problem.
- `limits`: `exhaustive_inputs`, `witnesses` (proper colorings added to
  verification inputs beyond the exhaustive limit), `synthesis_timeout_s`,
  `count_budget`, `route_qubits` (defaults to the device size), and
  `route_cx` (CNOTs of an iteration's Clifford+T lowering, 50,000 by default;
  routing five seeds takes about 3 ms per CNOT). Iterations beyond either
  routing limit are recorded as not routed, with the reason. `price_gates`
  (3,000,000 by default) bounds the Clifford+T gates of a component that is
  priced in full; larger components receive exact T, rotation, CNOT and gate
  counts without depths or measurement-assisted pricing, marked
  `priced: counts only`.

A study writes `summary.csv` with one row per measurement: `component` is
`preparation`, `oracle`, `diffusion`, `search` (complete search at the stated
iterations) or `iteration` (routed), and `metric_level` names the cost model.
`run.json` records each case's validation coverage, qubit roles, structural
statistics and stage timings; `<case>.qpy` holds its preparation, oracle and
diffusion circuits.

# Maintained notebooks

| Notebook | Purpose |
| --- | --- |
| [Graph coloring](tutorials/graph_coloring.ipynb) | DIMACS through verified oracle and Grover iteration |
| [Boolean workspace](tutorials/boolean_workspace.ipynb) | Five methods, circuit contracts, and conditional workspace |
| [Coloring comparison](studies/coloring_comparison.ipynb) | Shared configuration for Logique and Saha-Belletti |
| [Coloring phase-oracle comparison](studies/coloring_phase_oracle_comparison.ipynb) | Five K3 walkthroughs and nine-graph logical/U-CX oracle charts |
| [Boolean visual study](studies/boolean_visual_study.ipynb) | Connected logic diagrams, equations, and complete EPFL exports |

Use `logique notebook run PATH --offline` after setup and cache acquisition. The original VCGC notebook versions, including saved outputs, are retained on [`legacy/vcgc`](https://github.com/TheBarzani/logique/tree/legacy/vcgc). Older exploratory notebooks on that branch are not part of the maintained execution suite.

The phase-oracle study uses `configs/coloring_phase_oracle_comparison.json` and
requires the synthesis, benchmarks, visualization, and notebooks extras plus
system Graphviz. Run it with `--offline --timeout 3600`; the timeout is per cell.
Set `LOGIQUE_PHASE_STUDY_SMOKE=1` for the K3-only execution check. Source notebook
outputs stay empty; the runner saves the executed notebook and figures under
`dump/`. The notebook setup documents an explicit build using the local pinned
Caterpillar submodule. Existing environment settings take priority.

# Maintained notebooks

| Notebook | Purpose |
| --- | --- |
| [Graph coloring](tutorials/graph_coloring.ipynb) | DIMACS through verified oracle and Grover iteration |
| [Boolean workspace](tutorials/boolean_workspace.ipynb) | Five methods, circuit contracts, and conditional workspace |
| [Coloring comparison](studies/coloring_comparison.ipynb) | Shared configuration for Logique and Saha-Belletti |
| [Coloring phase-oracle comparison](studies/coloring_phase_oracle_comparison.ipynb) | Five K3 walkthroughs and nine-graph logical/U-CX oracle charts |
| [Boolean visual study](studies/boolean_visual_study.ipynb) | Connected logic diagrams, equations, and complete EPFL exports |
| [Revision walkthrough](tutorials/revision_walkthrough.ipynb) | K3 from predicate to explicitly decomposed circuits and their costs |
| [MCX decompositions](studies/mcx_decompositions.ipynb) | Multi-controlled X constructions for 3 to 20 controls |
| [Corrected comparison](studies/corrected_comparison.ipynb) | Analysis of a controlled study against the strongest baseline |
| [XAG and Belletti-Simple](studies/xag_belletti_equivalence.ipynb) | The XAG oracle and Belletti-Simple as one construction under the edge-only predicate |

Use `logique notebook run PATH --offline` after setup and cache acquisition. The original VCGC notebook versions, including saved outputs, are retained on [`legacy/vcgc`](https://github.com/TheBarzani/logique/tree/legacy/vcgc). Older exploratory notebooks on that branch are not part of the maintained execution suite.

The phase-oracle study uses `configs/coloring_phase_oracle_comparison.json` and
requires the synthesis, benchmarks, visualization, and notebooks extras plus
system Graphviz. Run it with `--offline --timeout 3600`; the timeout is per cell.
Set `LOGIQUE_PHASE_STUDY_SMOKE=1` for the K3-only execution check. Source notebook
outputs stay empty; the runner saves the executed notebook and figures under
`dump/`. The notebook setup documents an explicit build using the local pinned
Caterpillar submodule. Existing environment settings take priority.

The corrected comparison analyses a study run produced separately by
`logique benchmark run --config configs/corrected_comparison.json` (or the
pilot configuration); name its folder in `LOGIQUE_STUDY_RUN`, since the
notebook never selects a run implicitly.

The [manuscript reproduction study](manuscript/README.md) preserves the original
VCGC scripts and reference data and validates regenerated figures and metrics.

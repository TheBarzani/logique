# Logique

Logique is a Python 3.10 research toolkit for compiling graph-coloring predicates and general Boolean functions into quantum circuits. It provides five synthesis methods, verified XOR and phase-oracle wrappers, Grover circuits, conditional-workspace studies, and comparisons with four Saha–Belletti variants.

Inputs include DIMACS graphs, structural Verilog, and combinational AIGER. Coloring predicates account for valid color codes and precolored vertices. Boolean synthesis can select individual output cones; a separate ordered-expression frontend preserves the original XAG construction for historical replay.

The original VCGC version is preserved on the [`legacy/vcgc` branch](https://github.com/TheBarzani/logique/tree/legacy/vcgc). This checkout also contains a [manuscript reproduction study](experiments/manuscript/README.md) with archived inputs, reference results, and replay tools. See the [migration guide](docs/migration.md) for changes to imports, commands, and scientific behavior.

## Start here

| Task | Entry point |
| --- | --- |
| Understand graph coloring | [Graph-coloring tutorial](experiments/tutorials/graph_coloring.ipynb) |
| Rebuild the paper's K3 example | [Illustrative example](experiments/tutorials/illustrative_example_v2.ipynb) |
| Explore Boolean synthesis and workspace | [Boolean workspace tutorial](experiments/tutorials/boolean_workspace.ipynb) |
| Compare synthesis representations | [Boolean visual study](experiments/studies/boolean_visual_study.ipynb) |
| Compare full coloring Grover circuits | [Coloring comparison](experiments/studies/coloring_comparison.ipynb) |
| Compare complete phase-flip oracles | [Coloring phase-oracle comparison](experiments/studies/coloring_phase_oracle_comparison.ipynb) |
| Inspect verified workspace reuse | [Two borrowed inputs](experiments/studies/guarded_phase_oracle_two_ancillas.ipynb) and [int2float workspace](experiments/studies/int2float_conditional_workspace.ipynb) |
| Reproduce historical paper results | [Manuscript reproduction guide](experiments/manuscript/README.md) |
| Repeat an experiment | [Workflow guide](docs/workflows.md) and [configurations](configs/README.md) |
| Change the library | [Architecture](docs/architecture.md) and [development guide](docs/development.md) |
| Find an old file or paper result | [Migration guide](docs/migration.md) and [`legacy/vcgc`](https://github.com/TheBarzani/logique/tree/legacy/vcgc) |

## Install

Install uv and run these commands from the repository root. Python is restricted to 3.10; the locked research environment uses Qiskit 2.1.1. Initialize submodules before syncing either environment.

For the core graph tools and development checks:

```bash
uv python install 3.10
git submodule update --init --recursive
uv sync --locked
uv run --no-sync logique --help
```

For synthesis, benchmarks, and notebooks, install CMake, a C++17 compiler, and pkg-config. Install system Graphviz for logic diagrams, then prepare the research environment:

```bash
python3 tools/sync.py --all-extras
uv run --no-sync logique native build --source external/native/boolean_synthesis
export LOGIQUE_NATIVE_EXECUTABLE="$PWD/external/native/boolean_synthesis/build/boolean_synthesis"
export LOGIQUE_CACHE="$PWD/.cache/epfl"
```

The sync helper runs `uv sync --locked` using tweedledum's bundled C++ headers to avoid incompatible system headers, without modifying dependency sources. Select fewer dependencies with `python3 tools/sync.py --extra synthesis`, `--extra notebooks`, or `--extra comparison`; other extras are `benchmarks`, `visualization`, `simulation`, and `ibm`. Keep `--no-sync` on subsequent uv runs to retain installed extras. The native executable is built explicitly, never at import time. See [setup details](docs/setup.md) for troubleshooting.

## Compile a graph

```bash
uv run --no-sync logique synthesize datasets/graphs/teaching/edge.col --view grover
```

```python
from logique import read_dimacs, encode_coloring
from logique.synthesis import synthesize
from logique.verification import validate, verify_phase_oracle

encoding = encode_coloring(read_dimacs("datasets/graphs/teaching/edge.col"))
result = synthesize(encoding, method="xag")
print(validate(result))
phase_oracle = result.phase_oracle()
print(verify_phase_oracle(result, encoding=encoding, circuit=phase_oracle))
```

Methods are `xag`, `aig_bennett`, `xag_bennett`, `klut_bennett`, and `best_fit`. The raw `result.circuit` may retain workspace or phase; `result.oracle()` implements XOR into separate targets and `result.phase_oracle()` marks an output while restoring computational workspace. The CLI selects these circuits with `--view raw`, `xor`, `phase`, or `grover` and exports the selected view as `circuit.qpy` alongside synthesis metadata.

Exhaustive validation is limited to 12 inputs. For larger inputs, request seeded sampling with `--validation sampled`; sampling is recorded as such. Phase checks can compare the actual oracle against the independent graph predicate without allocating a statevector for every workspace qubit.

## Run a study

```bash
uv run --no-sync logique benchmark run --config configs/boolean_teaching.json
uv run --no-sync logique benchmark run --config configs/coloring_phase_oracle_comparison.json
uv run --no-sync logique datasets fetch --cache .cache/epfl
uv run --no-sync logique notebook run experiments/tutorials/boolean_workspace.ipynb --offline
```

Configurations resolve input paths relative to the JSON file. Benchmark runs save `run.json`, `summary.csv`, and circuit exports. EPFL downloads use a pinned manifest and verify SHA-256 hashes, including the source license; populate the cache before running EPFL notebooks offline. The phase-oracle configuration covers all five methods on nine paper graphs and reports both logical and U/CX-decomposed costs, without hardware routing.

Non-final outputs go to unique directories under ignored `dump/`, named
`MMDDHHMMSS-descriptive-name` in local time (for example,
`1010130405-coloring-phase-oracle`). Sort names descending to browse the newest
runs first within the year. Related artifacts keep stable filenames inside each
run. Execute notebooks through the CLI to save a separate executed copy; keep
source outputs empty when editing. Explicit output directories must be new and
should follow the same naming convention.

## Reproduce the paper

The [manuscript study](experiments/manuscript/README.md) preserves the original VCGC code, nine-graph inputs, reference CSV/JSON, figures, and provenance. `tools/generate_paper_benchmarks.py` rebuilds the paper circuits through the maintained `src/logique/` package. The recorded full replay matches all 135 historical width, depth, and gate-count values; it also exports a separate comparison with measurements on every method's data register.

Use a separate research environment for historical replay: its depth patch changes the installed Qiskit and must not affect corrected studies. After setting up that environment, a small K3 replay is:

```bash
uv run --no-sync python tools/patch_qiskit_depth.py
uv run --no-sync python tools/generate_paper_benchmarks.py --graphs K3
```

The first command patches the active Qiskit 2.1.1 installation to support the manuscript's analytical MCX-depth estimate and preserves a source backup under `dump/`. Omit `--graphs K3` to run all nine graphs. The [K3 walkthrough](experiments/tutorials/illustrative_example_v2.ipynb) compares the historical Hadamard reflection with the reflection about the actual preparation. The reproduction guide covers the archived implementation, figure validation, metric definitions, and remaining evidence gaps.

Historical replay preserves the original edge-only predicate, preparation, diffusion, baseline indexing, and measurement choices. Matching those results establishes reproducibility of that evaluation. Current phase-oracle studies use complete coloring predicates and measure oracle-only costs, so their resource tables describe a different experiment.

## Repository and development

| Folder | Contents |
| --- | --- |
| `src/logique/` | Maintained Python library |
| `experiments/tutorials/`, `experiments/studies/` | Tutorials and research notebooks |
| `experiments/manuscript/` | Archived paper material, provenance, and reproduction reports |
| `configs/` | Reproducible experiment settings |
| `datasets/` | Source inputs |
| `external/` | Dependency submodules and the native synthesis bridge |
| `dump/` | Ignored non-final results, executed notebooks, and local artifacts |
| `docs/`, `examples/`, `tests/`, `tools/` | Documentation, examples, checks, setup and reproduction tools |

See [external dependencies](external/README.md) for the submodule layout. Optional quantum, visualization, and hardware dependencies are loaded only by the features that need them.

Logique reports logical gate counts unless an explicit decomposition is requested; the paper replay retains its separately documented historical accounting. Conditional-state candidates are analysis results, not automatically certified borrowing transformations. The workspace notebooks verify specific reuse constructions, including phase and restoration, rather than providing a general optimizer. Local simulation uses the `simulation` extra. IBM submission is an explicit operation requiring a backend and shot count; see the [workflow guide](docs/workflows.md).

Run the development checks in the prepared environment:

```bash
uv run --no-sync pytest
uv run --no-sync black --check src tests tools examples
uv run --no-sync ruff check src tests tools examples
uv run --no-sync mypy
uv build --no-sources
```

Quantum and native tests require their optional dependencies and executable. See the [development guide](docs/development.md) for test coverage and notebook conventions.

## Research and licensing

Cite the repository and the relevant source publications when using these experiments; the [manuscript study](experiments/manuscript/README.md) documents historical sources and provenance. Earlier packaging claimed an MIT license, but this checkout has no root license text. Dependency licenses and pinned EPFL source-license verification are retained.

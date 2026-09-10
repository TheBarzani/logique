# Logique

Logique is a research toolkit for compiling graph-coloring predicates and Boolean functions into quantum oracles. It includes five synthesis methods, phase and workspace verification, conditional-workspace studies, and reproducible comparisons with Saha-Belletti.

## Start here

| Task | Entry point |
| --- | --- |
| Understand graph coloring | [Graph-coloring tutorial](notebooks/tutorials/graph_coloring.ipynb) |
| Explore Boolean synthesis and workspace | [Boolean workspace tutorial](notebooks/tutorials/boolean_workspace.ipynb) |
| Compare synthesis representations | [Boolean visual study](notebooks/studies/boolean_visual_study.ipynb) |
| Compare coloring circuits | [Coloring comparison](notebooks/studies/coloring_comparison.ipynb) |
| Repeat an experiment | [Workflow guide](docs/workflows.md) and [configurations](configs/README.md) |
| Change the library | [Architecture](docs/architecture.md) and [development guide](docs/development.md) |
| Find an old file or paper result | [Migration guide](docs/migration.md) and [research archive](archive/README.md) |

## Install

Use Python 3.10, uv, CMake, a C++17 compiler, and pkg-config. Install system Graphviz for the visual notebooks. Both submodules must be initialized.

```bash
git submodule update --init --recursive
uv python install 3.10
python3 tools/sync.py --all-extras
uv run --no-sync logique native build --source native/boolean_synthesis
export LOGIQUE_NATIVE_EXECUTABLE="$PWD/native/boolean_synthesis/build/boolean_synthesis"
export LOGIQUE_CACHE="$PWD/.cache/epfl"
```

The sync helper runs `uv sync --locked` using tweedledum's bundled C++ headers. It avoids accidentally selecting an incompatible system fmt installation. It does not modify dependency source files. See [setup details](docs/setup.md) for smaller installations and native-build troubleshooting.

## Compile a graph

```bash
uv run --no-sync logique synthesize datasets/graphs/teaching/edge.col --view grover
```

```python
from logique import read_dimacs, encode_coloring
from logique.synthesis import synthesize
from logique.verification import validate

encoding = encode_coloring(read_dimacs("datasets/graphs/teaching/edge.col"))
result = synthesize(encoding, method="xag")
print(validate(result))
phase_oracle = result.phase_oracle()
```

## Run a study

```bash
uv run --no-sync logique benchmark run --config configs/boolean_teaching.json
uv run --no-sync logique datasets fetch --cache .cache/epfl
uv run --no-sync logique notebook run notebooks/tutorials/boolean_workspace.ipynb --offline
```

New outputs go to unique directories under `results/`. Source notebooks remain unexecuted in Git. Historical results are retained separately and are not overwritten by new experiments.

The library lives in `src/logique/`; inputs in `datasets/`; active notebooks in `notebooks/`; and documentation in `docs/`. Optional quantum, visualization, and hardware dependencies are loaded only by the features that need them.

Logique reports logical gate counts unless an explicit decomposition is requested. Conditional-state candidates are analysis results, not automatically certified borrowing transformations. The small borrowing demonstration has separate phase and restoration checks.

## Research and licensing

The existing paper material is indexed in the [research roadmap](docs/research/README.md). Cite the repository and the relevant source publications when using these experiments. Earlier packaging claimed an MIT license, but no root license text was present; this refactor does not invent a license grant. Dependency licenses and pinned EPFL source-license verification are retained.

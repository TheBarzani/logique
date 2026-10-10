# Logique

Logique is a research toolkit for compiling graph-coloring predicates and Boolean functions into quantum oracles. It includes five synthesis methods, phase and workspace verification, conditional-workspace studies, and reproducible comparisons with Saha-Belletti.

The original VCGC version is preserved on the [`legacy/vcgc` branch](https://github.com/TheBarzani/logique/tree/legacy/vcgc). See the [migration guide](docs/migration.md) for the changes to imports, commands, and scientific behavior.

## Start here

| Task | Entry point |
| --- | --- |
| Understand graph coloring | [Graph-coloring tutorial](experiments/tutorials/graph_coloring.ipynb) |
| Explore Boolean synthesis and workspace | [Boolean workspace tutorial](experiments/tutorials/boolean_workspace.ipynb) |
| Compare synthesis representations | [Boolean visual study](experiments/studies/boolean_visual_study.ipynb) |
| Compare coloring circuits | [Coloring comparison](experiments/studies/coloring_comparison.ipynb) |
| Repeat an experiment | [Workflow guide](docs/workflows.md) and [configurations](configs/README.md) |
| Change the library | [Architecture](docs/architecture.md) and [development guide](docs/development.md) |
| Find an old file or paper result | [Migration guide](docs/migration.md) and [`legacy/vcgc`](https://github.com/TheBarzani/logique/tree/legacy/vcgc) |

## Install

Use Python 3.10, uv, CMake, a C++17 compiler, and pkg-config. Install system Graphviz for the visual notebooks. Initialize all submodules under `external/`.

```bash
git submodule update --init --recursive
uv python install 3.10
python3 tools/sync.py --all-extras
uv run --no-sync logique native build --source external/native/boolean_synthesis
export LOGIQUE_NATIVE_EXECUTABLE="$PWD/external/native/boolean_synthesis/build/boolean_synthesis"
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
uv run --no-sync logique notebook run experiments/tutorials/boolean_workspace.ipynb --offline
```

Non-final outputs go to unique directories under ignored `dump/`. Source notebooks remain unexecuted in Git. Historical VCGC results remain on `legacy/vcgc`.

| Folder | Contents |
| --- | --- |
| `src/logique/` | Maintained Python library |
| `experiments/` | Tutorials and study notebooks |
| `configs/` | Reproducible experiment settings |
| `datasets/` | Source inputs |
| `external/` | Dependency submodules and the native synthesis bridge |
| `dump/` | Ignored non-final results, executed notebooks, and local artifacts |
| `docs/`, `examples/`, `tests/`, `tools/` | Documentation, examples, checks, and setup helpers |

See [external dependencies](external/README.md) for the submodule layout. Optional quantum, visualization, and hardware dependencies are loaded only by the features that need them.

Logique reports logical gate counts unless an explicit decomposition is requested. Conditional-state candidates are analysis results, not automatically certified borrowing transformations. The small borrowing demonstration has separate phase and restoration checks.

## Research and licensing

Historical paper material is available on [`legacy/vcgc`](https://github.com/TheBarzani/logique/tree/legacy/vcgc). Cite the repository and the relevant source publications when using these experiments. Earlier packaging claimed an MIT license, but no root license text was present; this refactor does not invent a license grant. Dependency licenses and pinned EPFL source-license verification are retained.

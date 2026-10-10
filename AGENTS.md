# Repository guidelines

Logique compiles graph-coloring predicates and general Boolean functions into quantum circuits. It is a Python 3.10 research toolkit with optional native synthesis, plotting, notebook, simulation, and IBM dependencies.

## Navigation

- `src/logique/`: maintained library. Follow the package boundaries in `docs/architecture.md`.
- `experiments/tutorials/` and `experiments/studies/`: maintained notebooks; source outputs stay empty.
- `configs/`: JSON experiment configurations; paths resolve relative to the config.
- `datasets/`: source inputs. New generated outputs belong in ignored `dump/`.
- `legacy/vcgc` branch: historical research, tooling, and paper results.
- `external/native/boolean_synthesis/`: C++17 bridge with pinned Caterpillar dependencies.
- `external/`: ABC, Caterpillar, Mockturtle, Saha-Belletti, and tweedledum submodules plus the native bridge. Preserve dependency revisions and keep their changes separate.

## Setup and checks

```bash
python3 tools/sync.py --all-extras
uv run --no-sync logique native build --source external/native/boolean_synthesis
export LOGIQUE_NATIVE_EXECUTABLE="$PWD/external/native/boolean_synthesis/build/boolean_synthesis"
export LOGIQUE_CACHE="$PWD/.cache/epfl"
uv run --no-sync pytest
uv run --no-sync black --check src tests tools examples
uv run --no-sync ruff check src tests tools examples
uv run --no-sync mypy
uv build --no-sources
```

Initialize submodules first. The sync helper chooses bundled C++ headers without changing dependencies. Use `uv sync --locked` for the minimal environment. Avoid plain uv runs that synchronize away optional research extras.

## Changes

Use four-space indentation, snake_case functions, PascalCase classes, descriptive public docstrings and annotations, and Black's 88-column style. Limit formatting to maintained relevant code; never format dependency sources. Library code must not depend on notebooks or legacy scripts. Optional features must not become import-time dependencies of the core package.

Add deterministic regression tests for parsing, encoding, synthesis, phase, or workspace changes. Use small graphs and local execution. Keep correctness changes and any changed research metrics traceable in separate commits; never overwrite historical results.

Use short imperative commit subjects. PR descriptions explain behavior, validation commands, and relevant benchmark inputs, configuration, and dependency versions. Tokens belong only in local environment configuration based on `.env.example`; never include tokens in notebook output or metadata. Hardware submission must be an explicit requested operation with backend and shots specified.

# Repository guidelines

VCGC compiles graph-coloring predicates and general Boolean functions into quantum circuits. It is a Python 3.10 research toolkit with optional native synthesis, plotting, notebook, simulation, and IBM dependencies.

## Navigation

- `src/vcgc/`: maintained library. Follow the package boundaries in `docs/architecture.md`.
- `notebooks/tutorials/` and `notebooks/studies/`: four maintained notebooks; source outputs stay empty.
- `configs/`: JSON experiment configurations; paths resolve relative to the config.
- `datasets/`: source inputs. New generated outputs belong in ignored `results/`.
- `archive/`: historical research and tooling. Preserve indexed files byte-for-byte; use `archive/index.json` to find old paths.
- `native/boolean_synthesis/`: C++17 bridge with pinned Caterpillar dependencies.
- `tweedledum/` and `saha-belletti/`: unchanged dependency submodules. Keep their changes separate.

## Setup and checks

```bash
python3 tools/sync.py --all-extras
uv run --no-sync vcgc native build --source native/boolean_synthesis
export VCGC_NATIVE_EXECUTABLE="$PWD/native/boolean_synthesis/build/boolean_synthesis"
export VCGC_CACHE="$PWD/.cache/epfl"
uv run --no-sync pytest
uv run --no-sync black --check src tests tools examples
uv run --no-sync ruff check src tests tools examples
uv run --no-sync mypy
uv build --no-sources
python3 tools/check_archive.py
```

Initialize submodules first. The sync helper chooses bundled C++ headers without changing dependencies. Use `uv sync --locked` for the minimal environment. Avoid plain uv runs that synchronize away optional research extras.

## Changes

Use four-space indentation, snake_case functions, PascalCase classes, descriptive public docstrings and annotations, and Black's 88-column style. Limit formatting to maintained relevant code; never format archived files. Library code must not depend on notebooks or archived scripts. Optional features must not become import-time dependencies of the core package.

Add deterministic regression tests for parsing, encoding, synthesis, phase, or workspace changes. Use small graphs and local execution. Keep correctness changes and any changed research metrics traceable in separate commits; never overwrite historical results.

Use short imperative commit subjects. PR descriptions explain behavior, validation commands, and relevant benchmark inputs, configuration, and dependency versions. Tokens belong only in local environment configuration based on `.env.example`; never include tokens in notebook output or metadata. Hardware submission must be an explicit requested operation with backend and shots specified.

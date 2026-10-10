# Setup

The supported research environment is Python 3.10, locked in `uv.lock`, with Qiskit 2.1.1. Upgrading the quantum stack is a separate change from this refactor.

## Minimal graph tools

```bash
uv sync --locked
uv run logique --help
```

This installs the core graph package and development tools without quantum synthesis. `uv sync --locked --no-dev` gives a minimal runtime installation.

## Research environment

Install uv, CMake, pkg-config, and a C++17 compiler using your normal system tooling. On macOS use the Xcode command-line tools; on Linux use a C++ development toolchain. Graphviz's `dot` executable is required for connected logic diagrams.

```bash
git submodule update --init --recursive
uv python install 3.10
python3 tools/sync.py --all-extras
uv run --no-sync logique native build --source external/native/boolean_synthesis
export LOGIQUE_NATIVE_EXECUTABLE="$PWD/external/native/boolean_synthesis/build/boolean_synthesis"
export LOGIQUE_CACHE="$PWD/.cache/epfl"
uv run --no-sync logique datasets fetch --cache .cache/epfl
```

`tools/sync.py` forwards arguments to `uv sync --locked`. Select fewer extras with `--extra synthesis`, `--extra notebooks`, or `--extra comparison`. The other extras are `benchmarks`, `visualization`, `simulation`, and `ibm`. Use `--no-sync` when running an already prepared research environment so a plain uv run does not remove optional packages.

The helper sets CMake include paths to the exact fmt, Eigen, JSON, and parallel-hashmap headers already present in tweedledum. The fresh macOS build otherwise selected Homebrew fmt and failed on `fmt::join`. If an existing tweedledum build cache still names its previous source location, the helper preserves it under `dump/relocation/` before rebuilding. Compilation defaults to two parallel jobs; override `CMAKE_BUILD_PARALLEL_LEVEL` if necessary. No submodule source edits are needed.

The native bridge lives in `external/native/boolean_synthesis/` and builds a separate executable. CMake uses the initialized `external/caterpillar/` submodule by default, with its bundled headers; standalone builds fall back to the pinned Caterpillar download. An explicit `FETCHCONTENT_SOURCE_DIR_CATERPILLAR` override still takes priority. Python imports and notebook execution never compile it automatically. An explicit executable argument takes priority over `LOGIQUE_NATIVE_EXECUTABLE`, followed by `boolean_synthesis` on PATH.

Cache selection uses an explicit argument, then `LOGIQUE_CACHE`, then `~/.cache/logique/epfl`. Every cached EPFL file and its license are checked against the packaged SHA-256 manifest. Offline mode reports missing or corrupt inputs without downloading replacements.

uv records local submodule dependencies through [path sources](https://docs.astral.sh/uv/concepts/projects/dependencies/). The lockfile and Git submodule revisions together identify the environment; the C++ bridge pins its independent dependency revision in CMake.

## Existing local research

The original `.venv` and ignored manuscript directory are retained. Downloaded inputs live in `.cache/epfl`. Existing `results/` contents have moved to `dump/`, and ignored files formerly under `archive/local/` are preserved in `dump/legacy-local/`. CMake caches use absolute paths: previous native builds are retained in `dump/relocation/`, and the setup command creates a fresh build at the new location. Update any local `LOGIQUE_NATIVE_EXECUTABLE` setting to the path above. Historical VCGC sources and results are available on `legacy/vcgc`.

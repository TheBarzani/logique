# Setup

The supported research environment is Python 3.10, locked in `uv.lock`, with Qiskit 2.1.1. Upgrading the quantum stack is a separate change from this refactor.

## Minimal graph tools

```bash
uv sync --locked
uv run vcgc --help
```

This installs the core graph package and development tools without quantum synthesis. `uv sync --locked --no-dev` gives a minimal runtime installation.

## Research environment

Install uv, CMake, pkg-config, and a C++17 compiler using your normal system tooling. On macOS use the Xcode command-line tools; on Linux use a C++ development toolchain. Graphviz's `dot` executable is required for connected logic diagrams.

```bash
git submodule update --init --recursive
uv python install 3.10
python3 tools/sync.py --all-extras
uv run --no-sync vcgc native build --source native/boolean_synthesis
export VCGC_NATIVE_EXECUTABLE="$PWD/native/boolean_synthesis/build/boolean_synthesis"
export VCGC_CACHE="$PWD/.cache/epfl"
uv run --no-sync vcgc datasets fetch --cache .cache/epfl
```

`tools/sync.py` forwards arguments to `uv sync --locked`. Select fewer extras with `--extra synthesis`, `--extra notebooks`, or `--extra comparison`. The other extras are `benchmarks`, `visualization`, `simulation`, and `ibm`. Use `--no-sync` when running an already prepared research environment so a plain uv run does not remove optional packages.

The helper sets CMake include paths to the exact fmt, Eigen, JSON, and parallel-hashmap headers already present in tweedledum. The fresh macOS build otherwise selected Homebrew fmt and failed on `fmt::join`. Compilation defaults to two parallel jobs; override `CMAKE_BUILD_PARALLEL_LEVEL` if necessary. No submodule edits are needed.

The native bridge is a separate executable. Its first CMake configuration downloads a pinned Caterpillar revision. Python imports and notebook execution never compile it automatically. An explicit executable argument takes priority over `VCGC_NATIVE_EXECUTABLE`, followed by `boolean_synthesis` on PATH.

Cache selection uses an explicit argument, then `VCGC_CACHE`, then `~/.cache/vcgc/epfl`. Every cached EPFL file and its license are checked against the packaged SHA-256 manifest. Offline mode reports missing or corrupt inputs without downloading replacements.

uv records local submodule dependencies through [path sources](https://docs.astral.sh/uv/concepts/projects/dependencies/). The lockfile and Git submodule revisions together identify the environment; the C++ bridge pins its independent dependency revision in CMake.

## Existing local research

The original `.venv` and ignored manuscript directory are retained. Old downloaded inputs were relocated to `.cache/epfl`; previous ignored Boolean outputs are under `archive/local/boolean-results`. The latter remains ignored by Git.

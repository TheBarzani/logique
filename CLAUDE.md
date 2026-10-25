# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

Logique compiles graph-coloring predicates and general Boolean functions into quantum circuits (five synthesis methods, XOR/phase oracle wrappers, Grover circuits, workspace-borrowing studies, Saha-Belletti comparison). Python 3.10 only, uv-managed, with optional native C++ synthesis.

`AGENTS.md` holds the repository conventions; `docs/architecture.md`, `docs/development.md`, `docs/workflows.md`, `docs/setup.md`, and `docs/migration.md` hold the details referenced below.

## Environments

Two distinct environments. Do not mix them.

- Minimal (core graph tools, lint, type checks): `uv sync --locked`.
- Research (synthesis, benchmarks, notebooks, visualization): `python3 tools/sync.py --all-extras`. This wrapper runs `uv sync --locked` with tweedledum's bundled C++ headers so system headers do not break the build; plain `uv sync` is not a substitute, and it also relocates stale absolute-path tweedledum build caches into `dump/`.

Always `git submodule update --init --recursive` first, and always pass `--no-sync` to `uv run` afterwards — a plain `uv run` synchronizes the optional research extras away.

Native bridge and cache (needed for `*_bennett`/`best_fit` methods and EPFL benchmarks):

```bash
uv run --no-sync logique native build --source external/native/boolean_synthesis
export LOGIQUE_NATIVE_EXECUTABLE="$PWD/external/native/boolean_synthesis/build/boolean_synthesis"
export LOGIQUE_CACHE="$PWD/.cache/epfl"
```

The executable is never built at import time. `LOGIQUE_WORKSPACE`, `LOGIQUE_OUTPUT`, and `LOGIQUE_OFFLINE` are set by the notebook runner for executed notebooks, not by humans.

## Checks

```bash
uv run --no-sync pytest
uv run --no-sync black --check src tests tools examples
uv run --no-sync ruff check src tests tools examples
uv run --no-sync mypy          # files are pinned: src/logique/coloring + paths.py
uv build --no-sources
```

Single test / subset:

```bash
uv run --no-sync pytest tests/test_coloring.py::test_classical_checker_checks_all_constraints
uv run --no-sync pytest -k phase_oracle
uv run --no-sync pytest -m "not integration"
```

Markers: `integration` (compiled native bridge), `workflow` (executes maintained research workflows). Without the quantum extras the quantum modules `importorskip` themselves; import, parser, path, CLI, and classical tests still run, so a green run on the minimal environment does not mean the synthesis paths were exercised. No test submits hardware jobs. CI (`.github/workflows/checks.yml`) runs the core checks and a separate research job that also builds the bridge, fetches EPFL inputs, runs `configs/boolean_teaching.json`, and executes four notebooks `--offline`.

## Common commands

```bash
uv run --no-sync logique synthesize datasets/graphs/teaching/edge.col --view grover
uv run --no-sync logique benchmark run --config configs/coloring_phase_oracle_comparison.json
uv run --no-sync logique plot dump/YOUR_RUN/summary.csv --metric depth --output dump/YOUR_RUN/depth.png
uv run --no-sync logique notebook run experiments/tutorials/boolean_workspace.ipynb --offline
uv run --no-sync logique datasets fetch --cache .cache/epfl
```

Paper replay (patches the installed Qiskit 2.1.1 for the manuscript's analytical MCX depth, backing up the source under `dump/`):

```bash
uv run --no-sync python tools/patch_qiskit_depth.py
uv run --no-sync python tools/generate_paper_benchmarks.py --graphs K3
```

## Architecture

Pipeline: input (`.col` DIMACS, structural Verilog, AIGER, or an ordered expression) → `coloring.encode_coloring` → `synthesis.synthesize` → `SynthesisResult` → oracle/phase/Grover wrapper → `verification` → `benchmarks` export.

Packages under `src/logique/`: `coloring` (parsing, deterministic predicate encoding, classical reference), `synthesis` (native + tweedledum + Saha-Belletti adapters, result object), `circuits` (gate records, preparation, oracle/Grover), `verification` (independent Boolean evaluation, phase and restoration checks), `workspace` (conditional-state analysis plus one verified borrowing example), `benchmarks` (manifest, runner, metrics, export, provenance), `visualization`, `execution` (local analysis, explicit IBM submission), `cli` (argument parsing plus thin library calls).

Key contracts worth knowing before touching synthesis or verification:

- `result.circuit` is the raw clean-output computation and may retain workspace or phase. `result.oracle()` computes/copies/uncomputes into XOR targets; `result.phase_oracle(output=0)` marks one output and restores computational workspace. The CLI's `--view raw|xor|phase|grover` selects which of these reaches `circuit.qpy`.
- `ColoringEncoding` assigns consecutive inputs per vertex, least-significant color bit first, including isolated vertices; the predicate checks edge inequalities, unused color codes, and precolors. `problem.is_valid()` is the independent classical reference, and Verilog generation imports no quantum library.
- Exhaustive validation stops at 12 inputs (`--validation sampled` is seeded and recorded as sampled); statevector checks stop at 16 qubits.
- Historical paper replay is a deliberately different experiment: `edge_coloring_expression()` + `synthesize_expression()` + `kickback_grover_circuit()`, edge-only predicate, original valid-color preparation and H-based diffusion, historical measurement accounting. Never merge its numbers with the current phase-oracle studies, which use complete predicates and oracle-only costs.
- Metrics are logical gate counts unless a decomposition is explicitly requested.
- The native protocol is JSON over stdin/stdout with diagnostics on stderr.

Dependency boundaries are enforced by design, not just style: the core import pulls in no quantum or plotting stack (see the lazy `__getattr__` in `src/logique/synthesis/__init__.py`), library code never imports notebooks or scripts, and installed code resolves manifests through package resources and executables/caches through explicit paths or env vars rather than positions relative to `__file__`.

`external/` holds the ABC, Caterpillar, Mockturtle, Saha-Belletti, and tweedledum submodules plus the C++17 bridge: preserve their pinned revisions, never format them, and keep dependency changes in separate commits.

## Working conventions

- Non-final output goes to ignored `dump/`, in a folder named `MMDDHHMMSS-descriptive-name` in local time (e.g. `1010130405-coloring-phase-oracle`). Create it with `logique.benchmarks.runner.new_run_directory(description=...)` or `logique.paths.new_dump_directory(...)`; explicit output paths must follow the same convention and must not already exist.
- Source notebooks under `experiments/` keep outputs empty; execute them through the CLI and inspect the executed copy in `dump/`. Never overwrite archived results in `experiments/manuscript/`.
- Add deterministic regression tests with small graphs and local execution for parsing, encoding, synthesis, phase, or workspace changes. Keep correctness changes separate from commits that change research metrics.
- Hardware submission (`logique hardware submit`) is only ever an explicitly requested operation with backend and shots given; tokens live only in the ignored local `.env`, never in notebook output or metadata.
- The original VCGC code and paper results live on the `legacy/vcgc` branch. There are no backward-compatible API aliases — use `docs/migration.md`.

# Repository Guidelines

## Project Structure & Module Organization

VCGC compiles vertex-coloring problems into quantum circuits and benchmarks synthesis methods.

- `vcgc/`: library code for DIMACS parsing, graph management, Boolean constraints, synthesis, and circuit utilities.
- `tests/`: pytest import and basic object-construction tests.
- `examples/` and `experiments/`: usage examples, notebooks, and research workflows; `scripts/` contains benchmark and plotting utilities.
- `data/`: graph inputs, generated circuits, benchmark results, and plots. `docs/`, `images/`, and `manuscript/` hold diagrams and publication assets.
- `tweedledum/` and `saha-belletti/`: Git submodules. Keep dependency changes separate from changes to VCGC.

## Build, Test, and Development Commands

Use Python 3.10, as recommended in `README.md` for tweedledum compatibility. Run commands from the repository root.

```bash
git submodule update --init --recursive
python3.10 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m pip install -e '.[dev]'
```

Install the submodule packages following their own installation instructions when using synthesis or comparison workflows.

- `python -m pytest`: run the configured test suite.
- `python -m pytest tests/test_basic.py -v`: run focused basic checks.
- `python -m pytest --cov=vcgc`: collect library coverage; no minimum threshold is configured.
- `python -m black --check vcgc tests`: check formatting.
- `python -m pip wheel . --no-deps -w dist`: build a package wheel.

`build.py` references obsolete root-level scripts; use the direct commands above.

## Coding Style & Naming Conventions

Use four-space indentation, `snake_case` for functions and variables, and `PascalCase` for classes such as `VCPNetwork`. Follow Black's configured 88-character line length. Add descriptive docstrings and type annotations to public interfaces. The development extras include Flake8 and mypy; no repository-specific configuration is provided for them. Limit formatting changes to relevant files.

## Testing Guidelines

Name tests `test_*.py` or `*_test.py`, with functions named `test_<behavior>`. Add focused regression tests for parsing, coloring constraints, and synthesis changes. Prefer small deterministic graphs and local execution; keep hardware experiments outside routine tests.

## Commit & Pull Request Guidelines

History uses short imperative subjects, such as `Improve figures formatting`; follow that style. PRs should explain the change, report validation commands, and link relevant issues. For benchmark changes, identify graph inputs, parameters, and dependency versions; include comparison plots when results change.

## Configuration

Use `.env.example` as the template for local IBM Quantum settings. Keep tokens out of commits and notebook outputs. Review backend and shot settings before running hardware experiments.

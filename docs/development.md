# Development

Use Python 3.10 and the locked uv environment. Follow [setup](setup.md) for optional synthesis dependencies.

```bash
uv run --no-sync pytest
uv run --no-sync black --check src tests tools examples
uv run --no-sync ruff check src tests tools examples
uv run --no-sync mypy
uv build --no-sources
```

Set `LOGIQUE_NATIVE_EXECUTABLE` and `LOGIQUE_CACHE` to run native and cached EPFL regressions. Without quantum extras, quantum test modules skip; the minimal import, parser, path, CLI, and classical decoding tests still run. Native availability is checked explicitly. No tests submit hardware jobs.

The suite tests complete small truth tables, independent graph predicates, phase/oracle restoration, LUT polarity, conditional borrowing with an entangled reference, repeated Grover amplification, notebook source integrity, output paths, and historical result readers using small local fixtures. CI runs core checks separately from a native research environment.

Keep source notebooks free of outputs. Run them through the CLI and inspect executed copies under `dump/`, the ignored home for non-final results. Preserve final scientific inputs and outputs with their provenance. Historical VCGC material remains on `legacy/vcgc`. Keep dependency changes separate from Logique changes.

Public graph interfaces are typed. Black uses 88 columns; Ruff catches import and syntax errors; mypy checks the core graph and path boundary. Extend these checks as new typed interfaces are introduced.

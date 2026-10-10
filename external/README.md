# External dependencies and native tools

All dependency checkouts live here. These five directories remain Git submodules;
their source files, URLs, and pinned revisions are unchanged by the relocation.

| Directory | Purpose |
| --- | --- |
| `abc/` | ABC logic synthesis |
| `caterpillar/` | Reversible synthesis and mapping |
| `mockturtle/` | Logic networks and optimization |
| `saha-belletti/` | Graph-coloring comparison implementation |
| `tweedledum/` | Python quantum synthesis extension |
| `native/boolean_synthesis/` | Logique's maintained C++17 bridge |

From the repository root:

```bash
git submodule sync --recursive
git submodule update --init --recursive
python3 tools/sync.py --all-extras
uv run --no-sync logique native build --source external/native/boolean_synthesis
export LOGIQUE_NATIVE_EXECUTABLE="$PWD/external/native/boolean_synthesis/build/boolean_synthesis"
```

The native bridge uses Caterpillar's bundled dependency headers to preserve its
existing API contracts. The standalone Mockturtle and tweedledum checkouts keep
their independent pins. Compatibility corrections are written to the native
build directory and never applied to submodule sources. See the
[bridge notes](native/boolean_synthesis/README.md) and [setup guide](../docs/setup.md).

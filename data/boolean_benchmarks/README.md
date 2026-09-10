# EPFL Boolean benchmark experiments

Open `examples/boolean_synthesis_workspace.ipynb` for the complete tutorial.
Install `requirements-benchmarks.txt` in the repository's Python 3.10 environment
and build the helper described in `native/boolean_synthesis/README.md`.

The manifest selects the original `ctrl`, `int2float`, and `cavlc` circuits from
[lsils/benchmarks](https://github.com/lsils/benchmarks). `router` is optional.
It pins revision `82d8cc6910419298e713a46644ed59fd3df53038` and SHA-256 hashes for
the AIGER, Verilog, and MIT license files. Downloaded files live in `cache/`;
generated circuits and tables live in `results/`. Both are ignored by Git.
The original source files are never rewritten. Output cones are explicitly
identified by their selected output indices in result metadata.

```bash
.venv/bin/python scripts/run_boolean_notebook.py
.venv/bin/python scripts/run_boolean_notebook.py --offline
.venv/bin/python -m pytest tests/test_benchmark_synthesis.py
```

The notebook runner uses the invoking Python interpreter. The offline check
blocks Python network connections in the notebook kernel; run online once to
populate caches. The default executed notebook is written into `results/`.
Use `--output examples/boolean_synthesis_workspace.ipynb` to update its saved
outputs explicitly.

For the two-benchmark visual study, install system Graphviz (`brew install
graphviz` on macOS, or `sudo apt install graphviz` on Debian/Ubuntu), then run:

```bash
.venv/bin/python scripts/run_boolean_notebook.py --notebook examples/boolean_synthesis_visual_study.ipynb
.venv/bin/python -m pytest tests/test_boolean_visuals.py
```

This notebook includes LaTeX, connected Schemdraw circuits, SVG logic graphs,
and full Qiskit drawings for selected int2float/cavlc output cones. Complete
benchmark exports and comparison tables live in `results/visual_study/`.
Add `--offline` to verify this notebook without network access too.

QPY exports contain the raw circuit followed by its XOR-oracle wrapper. JSON
exports include source hashes, dependency versions, network and gate records,
and correctness reports. Exhaustive checks enumerate inputs for the default
benchmarks and track both output bits and monomial phases. Actual statevector
checks are limited to 16 qubits. Optional router validation uses fixed-seed
sampling and is labeled accordingly.

Workspace candidates are conjunction-derived conditional-state facts, not
automatically certified borrowing transformations. The four-control borrowing
demo is checked separately for phase correctness and restoration, including an
entangled reference. Logical MCX and rotation counts are not T-count estimates.

# Input datasets

## Graphs (`graphs/`)

The graphs of the coloring study are organized by role and by tier. The generated index
[`graphs/README.md`](graphs/README.md) lists every graph with:
- its size, colors, clique number, triangles and number of colorings;
- its origin: who made it, and how.

| Folder | What it holds |
| --- | --- |
| `graphs/discovery/` | The *discovery set*: the nine graphs of the original manuscript (K3, K5, K10, K20, myciel3–5, 2-Insertions_3, zed-city_2019). Every finding up to 26 November 2026 was made on them. Configurations and tests refer to them by these paths. |
| `graphs/small/<class>/` | *Small tier*: structured graphs whose data register has at most 24 qubits, simulated exactly. |
| `graphs/medium/<class>/` | *Medium tier*: graphs whose colorings can be counted within the study's budget, so the complete search is priced exactly. |
| `graphs/large/<class>/` | *Large tier*: graphs whose colorings cannot be counted; they are compared per Grover iteration. |
| `graphs/teaching/` | Small tutorial inputs and the annotated format template `template.col`. |
| `graphs/legacy/` | Historical and development inputs outside the study: `execution/` (linear graphs of the historical execution directory), `development/` (preserved development inputs) and `benchmarks/grid6.col`. |

Every graph in the three tier folders belongs to the *confirmation set*.

**Classes.** Inside a tier, graphs are grouped by class:
- generated structured classes, such as `paths`, `wheels`, `latin-squares`, `sudoku`, `grids` and
  `planar-triangulations`;
- planted families with fixed seeds (`planted-vertices`, `planted-density`, `planted-colors`);
- DIMACS instances, such as `queens`, `mycielski` and `book-characters`.

**Records.** Each file states its number of colors k in an `x colors` line.

| File | What it holds |
| --- | --- |
| `graphs/manifest.json` | For each graph: its path, SHA-256, split (discovery or confirmation), tier, class, structure (density, clique number, triangles, bipartiteness, girth) and number of colorings. It also records the graph's provenance in two fields. `origin` says who made the graph and how: the author named in a downloaded file's header (Michael Trick, the Stanford GraphBase, David Johnson and others), or the construction and seed of a generated graph. `source` gives the download URL, `generated` or `original manuscript`. |
| `graphs/witnesses.json` | One proper coloring per graph, for verification. |
| `graphs/README.md` | The generated index. |

All three files are written by `tools/build_graph_tiers.py`. It generates the structured graphs and the planted
families. It downloads the DIMACS instances once from the graph-coloring collection and checks them against their
recorded SHA-256 (`--fetch` downloads them again). It reuses the counts and witnesses of unchanged files, and stops
if two graphs are isomorphic.

## Boolean functions (`boolean/`)

- `boolean/teaching/`: deterministic structural Verilog examples.
- `boolean/studies/`: inputs of the workspace studies.

## Other datasets

The EPFL manifest is packaged as `logique.benchmarks/epfl.json`; downloaded AIGER, Verilog and license files belong in
the configured cache. Acquisition verifies pinned SHA-256 hashes even when using an existing cache.

Historical inputs and their original locations remain available on
[`legacy/vcgc`](https://github.com/TheBarzani/logique/tree/legacy/vcgc). Generated circuits, tables and plots that are
not final belong under ignored `dump/`.

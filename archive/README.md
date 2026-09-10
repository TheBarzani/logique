# Research archive

This archive preserves the work that preceded the toolkit refactor. It is historical material, not an executable compatibility layer.

- `research/data/`: original generated circuits, benchmark tables, plots, and development assets. DIMACS inputs were moved into `datasets/graphs/`.
- `research/examples/`: original tutorials and comparisons, including saved notebook outputs.
- `research/experiments/`: exploratory graph, Grover, synthesis, and hardware notebooks with their outputs.
- `tooling/`: former scripts, packaging, Nix configuration, and library implementations.
- `local/`: ignored generated output retained from the local checkout; not distributed in Git.

[index.json](index.json) records original paths, current locations, and SHA-256 hashes. The inventory baseline is commit `924a7ac`, which checkpoints the first-party Boolean-synthesis work. The next commit moved the library into `src/`; library entries in the inventory reflect that intermediate path.

Historical files remain byte-for-byte intact. Their internal links and imports may use original locations. Use the index to locate inputs and the [migration guide](../docs/migration.md) for maintained replacements. Original benchmark numbers are not recomputed or updated by this refactor.

A later working-copy revision of the visual-study notebook arrived during relocation. Both the checkpointed notebook and `boolean_synthesis_visual_study_updated.ipynb` are retained; the inventory records the change.

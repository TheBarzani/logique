# VCGC manuscript revision

This study starts by reproducing the original manuscript on
`vcgc-paper-revision`, branched from `main` at `acbbbd5`. Methodology and manuscript
revisions follow the verified historical baseline. The manuscript remains local
in ignored `docs/manuscript/`.

## Run

Use the existing Python 3.10 research environment without synchronizing it:

```bash
.venv/bin/python tools/reproduce_manuscript.py --stage plots
.venv/bin/python tools/reproduce_manuscript.py --stage all --manuscript docs/manuscript
```

Each invocation creates a fresh directory under `dump/manuscript-<timestamp>/`.
It contains `report.json`, regenerated plots, and side-by-side and pixel-difference
images. `--output PATH` accepts only a new directory. Exit status 2 means a
comparison differs or the full evaluation is blocked; inspect the report.
`--stage audit` checks source hashes and dependencies without plotting or synthesis.
`--stage evaluate` runs only the historical benchmark evaluation after the audit.
The optional `--manuscript` check matches the active LaTeX figures to references.

## Recovered inputs

`legacy/` contains 38 unchanged files selected from `legacy/vcgc` at
`86e3025`. `provenance.json` records the full commit, file hashes, original
submodule pins, dependency Python-source hashes, and the nine-benchmark order.
The snapshot includes the original `vcgc` implementation, generation and plotting
scripts, input graphs, CSV/JSON results, four reference result plots, and two
editable diagram sources. It is separate from the maintained `logique` package.

The benchmark CSV is the paper's nine-graph dataset. The archived JSON also has
`grid6`; it is retained as evidence, but must not silently expand the paper's
evaluation. The runner selects graphs in CSV order and rejects failures that the
original generator reports as zero-valued metrics.

Hardware plotting reads the explicit
`legacy/data/execution/20250829_161926/execution_comparison.csv`, never the script's
ctime-based "latest" selection. Other historical CSVs are retained to distinguish
the experiments. The runner does not import or execute `generate_exec_comparison.py`.

## Validated reproduction

All four result plots reproduce the reference **RGBA pixels exactly** using the
original plotting functions, Matplotlib 3.10.5, and `figure.dpi = 200`. The original
functions export benchmark PNGs at 300 DPI and the hardware PNG at 500 DPI; the
figure DPI controls layout before export and is independently necessary.
The references are also byte-identical to the corresponding local manuscript PNGs.

Regenerated file hashes differ because PNG image-data compression differs. The
PNG metadata and decompressed image-data bytes match. No resizing, cropping, or
postprocessing is used to achieve the pixel matches.

`reproduction-status.json` records the checked run, including package versions,
font and native-binary hashes, input hashes, image comparisons, and blockers.
`requirements-plotting.txt` pins the plotting environment that produced these
matches. The repository's `uv.lock` supplies the maintained environment; the
original unpinned requirements are retained as historical evidence, not presented
as an exact historical lockfile.

The per-baseline improvement rows round to the manuscript's reported values:

| Baseline | Width | Depth | Gates |
| --- | ---: | ---: | ---: |
| Saha/original | 35.5% | 71.9% | 52.2% |
| Belletti minimal | 56.1% | 90.5% | 89.6% |
| Belletti simple | 36.8% | -9.5% | 36.7% |
| Belletti balanced | 38.7% | 44.9% | 62.2% |

Unrounded overall means are 41.7864997822%, 49.4611328330%, and 60.1599737446%.
Truncating them to one decimal gives the manuscript's 41.7%, 49.4%, and 60.1%;
ordinary rounding gives 41.8%, 49.5%, and 60.2%. Truncation explains the numbers,
but its use in the original writing process has not been established.

## Remaining work

1. Recover and preserve the original Qiskit `depth(mcx_decomposition=True)` patch.
   The current `.venv` imports Qiskit 2.1.1 without that parameter. Historical
   commit `6c068f74d03dffe6dc1d51a7994317c7e2f99a84` explicitly mentions an
   installed-Qiskit modification but does not contain its implementation.
   Installed tweedledum and Saha–Belletti Python sources match the legacy pins.
2. Run `--stage evaluate` in the recovered environment and compare all 135
   benchmark metrics: nine graphs, five original methods, and three metrics.
   Until then, the plots are reproduced from saved data; the underlying circuit
   evaluation is **not yet reproduced**.
3. Recover raw hardware measurement records if available. The selected CSV
   contains 30 summary rows, 10,000 shots per row, and job identifiers; reproducing
   its plot does not independently verify probabilities from raw counts.
4. Recover the six illustrative figure exports and their exact source settings.
   They have no byte-identical standalone file or embedded notebook PNG on the
   legacy branch. The two Draw.io sources are candidates, not verified exports.
5. Resolve reproduction discrepancies before changing methodology or manuscript
   claims. Preserve historical references and put each changed metric definition
   in its own traceable commit. Additional synthesis workflows are outside this
   reproduction milestone.

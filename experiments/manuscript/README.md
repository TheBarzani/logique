# VCGC manuscript revision

This study starts by reproducing the original manuscript on
`vcgc-paper-revision`, branched from `main` at `acbbbd5`. Methodology and manuscript
revisions follow the verified historical baseline. The manuscript remains local
in ignored `docs/manuscript/`.

## Maintained historical replay

[`tools/generate_paper_benchmarks.py`](../../tools/generate_paper_benchmarks.py)
now reproduces the original methodology through the maintained `src/logique/`
implementation. It imports no historical VCGC code. The archived CSV supplies
benchmark names and expected values; every new value is measured from a freshly
built circuit.

```bash
.venv/bin/python tools/patch_qiskit_depth.py
.venv/bin/python tools/generate_paper_benchmarks.py
.venv/bin/python tools/plot_paper_benchmarks.py dump/MMDDHHMMSS-paper-benchmarks --measured
```

The generator prints its new output directory. Use `--graphs K3` for a small
example. The native bridge must be built at
`external/native/boolean_synthesis/build/boolean_synthesis`, or selected through
`LOGIQUE_NATIVE_EXECUTABLE`. Explicit output directories must not already exist.

The replay restores these original choices:

1. **Encoding:** edge inequalities only, with the original variable order and
   tweedledum expression-tree construction. Precolors and unused binary color
   codes are not constraints in the original Boolean function. The source
   datasets remain unchanged.
2. **Preparation:** VCGC prepares each vertex over its valid colors using the
   original decomposed `UniformSuperpositionGate`. The four baselines retain
   their original Hadamard preparation over all bitstrings.
3. **Oracle:** prepare the XAG output in `|minus>` and apply the synthesized XAG
   once. Internal XAG cleanup restores workspace; there is no additional inverse
   of the whole oracle. The replay verifies raw XOR action, exact phase, and
   restoration for **both** initial output-target bits before building Grover.
4. **Diffusion:** reproduce the original H-based reflection. The old generator
   did not pass its valid-color preparation into its diffusion helper, so the
   replay explicitly preserves that choice.
5. **Indexing:** pass the original one-based graph labels to every baseline.
   This reproduces the historical original-Saha indexing mismatch: that
   dependency loops over zero-based labels and omits edges incident on vertex
   `n` for a one-based graph. Exact replay preserves it; the default maintained
   adapter continues to normalize labels for other studies.

### Measurements and exact comparison

The legacy generator left VCGC unmeasured but measured the data register for all
four baselines. Consistent measurement accounting therefore changes the original
VCGC numbers. The new run saves both evaluations explicitly:

- `benchmark_results.csv`: the original measurement choices, including graph
  metadata. This reproduces **all 135 metrics exactly**, and the CSV is
  **byte-identical** to the historical reference.
- `comparison.csv`: all 135 original/new/delta pairs; every delta is zero.
- `measurement_consistent_results.csv`: all five methods measure every data
  qubit. Baseline metrics are unchanged. VCGC gains one depth layer and
  `input_count + 1` instructions (measurements plus a final barrier); width is
  unchanged. Its K3 width/depth/gates become **11/31/80**, versus **11/30/73** in
  the exact historical replay.
- `<graph>_<method>.qasm`: the 45 historical circuits.
- `<graph>_vcgc_measured.qasm`: nine VCGC circuits with the same measurement step
  as the baselines; reuse the baseline QASM files for the consistent comparison.
- `<graph>.v` and `run.json`: rebuilt encodings, environment/source provenance,
  removed precolors, and verification coverage.

Metric formulas retain the historical MCX width allowance, requested analytical
MCX tree-weighted depth, and `len(circuit)` instruction count. The latter includes
barriers and measurements. These are the original accounting definitions, not
costs of explicitly decomposed hardware circuits.

The full maintained replay is in `dump/1010174305-paper-benchmarks/`.
Its `validation.json` records source/dependency fingerprints and the checks.
All three benchmark figures generated from the fresh CSV match the original
RGBA pixels exactly. The saved-measurement hardware figure also matches; its
measurements were not rerun. All 158 tests passed across the suite and the
notebook rerun outside the sandbox; Black, Ruff, mypy, and the package build pass.
`tools/plot_paper_benchmarks.py --measured` plots the consistent-measurement CSV
through the maintained plotting implementation. Without `--measured`, it plots
historical accounting. The original figure functions can also be applied to the
fresh historical CSV through `tools/reproduce_manuscript.py`'s `plots` function;
this checks the original figure pixels independently of circuit generation.

K3 verification covers all 64 binary assignments and both target bits. Its
edge-only predicate marks 24 assignments across four encoded colors; only six
are supported valid-color solutions under the three-color preparation. Larger
graphs use 256 seeded assignments for both target bits, which is sampling rather
than a proof. Baseline phase semantics are not independently verified by this
replay. Matching historical costs establishes reproducibility of the original
methodology, including its preserved indexing and preparation choices.

### Preserved earlier experiment

[`maintained-status.json`](maintained-status.json) and
[`maintained-comparison.csv`](maintained-comparison.csv) preserve the earlier
methodology experiment with **34/135** matches. That run used complete predicates,
Hadamard preparation, an outer compute–Z–uncompute wrapper, normalized baseline
labels, and removed measurements. It is a separate experiment and has not been
overwritten. The exact historical generator reports below are also unchanged.

## Historical reproduction

Use the existing Python 3.10 research environment without synchronizing it:

```bash
.venv/bin/python tools/patch_qiskit_depth.py
.venv/bin/python tools/reproduce_manuscript.py --stage all --manuscript docs/manuscript
```

Each invocation creates a fresh directory under
`dump/MMDDHHMMSS-manuscript-<stage>/`, using local time.
The `all` stage regenerates circuits and metrics first, compares them against the
archived CSV, and plots the **newly generated CSV**. The run contains:

- `evaluation/benchmark_results.csv` and `.json`: new numerical results.
- `evaluation/<graph>/`: freshly synthesized QASM circuits, Verilog, and DOT.
- `metric-comparison.csv`: all 135 old/new metric pairs and their differences.
- `report.json`: source and environment fingerprints, numerical checks, and figures.
- `plots/` and `comparisons/`: regenerated plots and visual comparisons.

`--output PATH` accepts only a new directory. Exit status 2 means a
comparison differs or the full evaluation is blocked; inspect the report.
`--stage audit` checks source hashes and dependencies without plotting or synthesis.
`--stage evaluate` runs only the historical benchmark evaluation after the audit.
`--stage plots` only replays archived data and is not a benchmark-regeneration run.
The optional `--manuscript` check matches the active LaTeX figures to references.

## Scripts and methodology to inspect

The computation is in the unchanged
[`legacy/scripts/generate_benchmarks.py`](legacy/scripts/generate_benchmarks.py):

1. `process_benchmark` reads each DIMACS graph using the original `VCPNetwork`.
2. `generate_vcgc_circuit` builds the original Boolean function and tweedledum XAG,
   synthesizes the oracle, and combines the original uniform preparation and
   diffusion circuits into a Grover circuit.
3. `generate_saha_belletti_circuits` generates the original, minimal, simple, and
   balanced baselines with one Grover iteration.
4. Each method measures width as circuit qubits plus the original MCX ancilla
   estimate; depth through `depth(mcx_decomposition=True)`; and gates as
   `len(circuit)`. The ancilla helper sums `max(0, n-2)` for operations named `mcx`,
   excluding the last MCX as assumed diffusion. The gate count remains the
   original logical count; the depth weighting does not rewrite the circuit.

[`tools/reproduce_manuscript.py`](../../tools/reproduce_manuscript.py) is the
entry point; run its commands from the repository root.
Its `evaluate` function invokes the original generator on each of the nine
graphs, saves the results, and calls `validate_evaluation`. No archived metric
value is substituted into a newly generated result. The archived CSV supplies
the benchmark selection/order and expected values for validation.

## Reconstructed depth method

[`depth-model.json`](depth-model.json) specifies `logique.mcx_tree_bound.v1`.
The installer overwrites `QuantumCircuit.depth` in the active Qiskit 2.1.1
installation, preserves an original-source backup under `dump/`, and refuses an
unrecognized source version. It is safe to rerun. Reapply it after reinstalling
Qiskit, and restart any already-running notebook kernels.

`depth(mcx_decomposition=True)` assigns an n-controlled X the cost
`ceil(log2(n))` for n >= 2 and other counted instructions cost one. X and CX
therefore retain cost one. The method propagates those costs along Qiskit's
existing critical path; filters, barriers, and classical dependencies retain
their original behavior. Plain `depth()` remains unchanged.

The rule follows the MCX Toffoli-depth bound in
[Dutta et al., Section V](https://arxiv.org/html/2502.01433v2#S5), published as
[Phys. Rev. A 111, 052611](https://doi.org/10.1103/PhysRevA.111.052611).
This is an analytical operation cost: it does not allocate ancillas, construct
the decomposition, or schedule restoration, measurements, or hardware operations.
The resulting mixed depth is not a measured physical depth or a pure T-depth.
The implementation is a reconstruction authorized for this reproduction; the
original edited Qiskit source has not been recovered. The source changes are
recorded in [`qiskit-depth.patch`](qiskit-depth.patch).

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

Rebuilding the original circuits with the reconstructed depth method reproduces
**all 135 benchmark metrics exactly**: nine graphs, five methods, and width,
depth, and gate count. The graph metadata also matches. Installed tweedledum and
Saha–Belletti Python sources match their historical pins.
The regenerated benchmark CSV is byte-identical to the archived reference CSV.

All four result plots reproduce the reference **RGBA pixels exactly** using the
original plotting functions, Matplotlib 3.10.5, and `figure.dpi = 200`. The original
functions export benchmark PNGs at 300 DPI and the hardware PNG at 500 DPI; the
figure DPI controls layout before export and is independently necessary.
The references are also byte-identical to the corresponding local manuscript PNGs.

Regenerated file hashes differ because PNG image-data compression differs. The
PNG metadata and decompressed image-data bytes match. No resizing, cropping, or
postprocessing is used to achieve the pixel matches.

`regeneration-status.json` records the full generation and comparison run, and
`metric-comparison.csv` records all old/new pairs. The three benchmark plots use
the regenerated results. Hardware plotting continues to use saved measurements.
`reproduction-status.json` preserves the earlier archived-data-only run, including
its then-missing depth-patch blocker; it has not been overwritten.
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

1. Recover raw hardware measurement records if available. The selected CSV
   contains 30 summary rows, 10,000 shots per row, and job identifiers; reproducing
   its plot does not independently verify probabilities from raw counts.
2. Recover the six illustrative figure exports and their exact source settings.
   They have no byte-identical standalone file or embedded notebook PNG on the
   legacy branch. The two Draw.io sources are candidates, not verified exports.
3. Use the reproduced numerical baseline to revise methodology and manuscript
   claims. Numerical agreement validates reproduction of the old evaluation;
   it does not establish the scientific validity of each original metric choice.
   Preserve historical references and put changed metric definitions in separate
   commits. Additional synthesis workflows are outside this reproduction milestone.

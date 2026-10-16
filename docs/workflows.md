# Research workflows

Run commands from the checkout after [setup](setup.md), or invoke installed `logique` from another directory with explicit input paths. New experiment output directories must not already exist.

Default runs use `dump/MMDDHHMMSS-descriptive-name/` in local time. Sort names
descending for newest-first browsing within a year. Use
`new_run_directory(description="my-study")` from Python; related figures and data
belong inside that directory. Explicit output paths are used as supplied and
should follow the same convention.

## Synthesize and verify

```bash
uv run --no-sync logique synthesize datasets/boolean/teaching/and4.v --method best_fit
uv run --no-sync logique synthesize datasets/graphs/teaching/edge.col --view grover --iterations 2
uv run --no-sync logique benchmark run --config configs/boolean_teaching.json
uv run --no-sync logique benchmark run --config configs/coloring_comparison.json
```

Methods are `xag`, `aig_bennett`, `xag_bennett`, `klut_bennett`, and `best_fit`. LUT sizes range from 2 to 6. Best-fit supports `outer_cut` and `inner_cut`. Selected output indices are zero-based and retain requested ordering and duplicates.

Use `--validation sampled` explicitly for inputs exceeding the 12-input exhaustive limit; sampled validation is labeled and seeded. `--validation none` records that verification was not run. Statevector checks are separately limited to 16 qubits.

A synthesis export contains JSON metadata and QPY with the raw computation followed by its XOR wrapper. The CLI also writes `circuit.qpy` containing exactly the selected `--view`. Experiment runs include `run.json`, a long-form `summary.csv`, and per-case circuit/metadata exports. Failed runs retain completed cases and record the error; a rerun uses a new directory.

## Inspect results

```bash
uv run --no-sync logique plot dump/YOUR_RUN/summary.csv --metric depth --output dump/YOUR_RUN/depth.png
```

The same reader handles historical wide CSV and nested JSON comparison formats, available on `legacy/vcgc`. Export a historical table into `dump/` to inspect it in this checkout. `--normalize` uses an XAG/Logique baseline; `--log` changes the vertical scale. Timings are individual wall-clock measurements, not statistical speedup claims. Optional `decomposed_metrics()` requires an explicit target basis and reports its counts separately.

## Execute notebooks

```bash
uv run --no-sync logique notebook run experiments/tutorials/graph_coloring.ipynb --offline
uv run --no-sync logique notebook run experiments/tutorials/boolean_workspace.ipynb --offline
uv run --no-sync logique notebook run experiments/tutorials/paper_benchmark_walkthrough.ipynb --offline
uv run --no-sync logique notebook run experiments/studies/coloring_comparison.ipynb --offline
uv run --no-sync logique notebook run experiments/studies/boolean_visual_study.ipynb --offline
```

The runner uses the invoking interpreter, a temporary kernel specification, and a fresh results directory. Use `--workspace /path/to/checkout` when launching elsewhere. The notebook source is never overwritten, including on execution failure. Offline execution blocks Python socket connections in the notebook kernel; this is a reproducibility check, not an operating-system network sandbox.

For interactive use, select the research environment's kernel and launch from the repository root. Source cells call shared library functions; executed notebooks and figures belong in `dump/`.

The [paper benchmark walkthrough](../experiments/tutorials/paper_benchmark_walkthrough.ipynb)
builds K3 step by step, visualizes its graph, Boolean logic, quantum circuits,
and probabilities, then reconciles all five methods with the paper generator.
It requires the comparison and notebook extras, the native bridge, system
Graphviz, and the manuscript MCX-depth patch (`tools/patch_qiskit_depth.py`).
It preserves the historical edge-only predicate, preparation/reflection choices,
and measurement accounting. Generator artifacts and provenance are saved in a
`paper-replay/` subfolder of the notebook run.

## IBM execution

Copy `.env.example` to `.env` and configure your own account, or use an account previously saved through the IBM SDK. Credentials are read only when creating a hardware service and are never recorded in run metadata.

```bash
uv run --no-sync logique hardware submit dump/YOUR_RUN/circuit.qpy --input-qubits 0 1 2 3 --backend YOUR_BACKEND --shots 1024
uv run --no-sync logique hardware retrieve YOUR_JOB_ID --output dump/YOUR_RUN/counts.json
uv run --no-sync logique hardware analyze dump/YOUR_RUN/counts.json --graph datasets/graphs/teaching/edge.col
```

Submission requires a QPY containing one unmeasured circuit. Input-qubit order must match the encoding; only those wires are measured. The CLI returns and saves the job identifier immediately. Retrieval and analysis do not submit new jobs. The adapter uses IBM's [SamplerV2 interface](https://quantum.cloud.ibm.com/docs/en/api/qiskit-ibm-runtime/sampler-v2). Routine tests mock submission; no hardware experiment is part of the refactor validation.

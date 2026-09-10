# Research workflows

Run commands from the checkout after [setup](setup.md), or invoke installed `vcgc` from another directory with explicit input paths. New experiment output directories must not already exist.

## Synthesize and verify

```bash
uv run --no-sync vcgc synthesize datasets/boolean/teaching/and4.v --method best_fit
uv run --no-sync vcgc synthesize datasets/graphs/teaching/edge.col --view grover --iterations 2
uv run --no-sync vcgc benchmark run --config configs/boolean_teaching.json
uv run --no-sync vcgc benchmark run --config configs/coloring_comparison.json
```

Methods are `xag`, `aig_bennett`, `xag_bennett`, `klut_bennett`, and `best_fit`. LUT sizes range from 2 to 6. Best-fit supports `outer_cut` and `inner_cut`. Selected output indices are zero-based and retain requested ordering and duplicates.

Use `--validation sampled` explicitly for inputs exceeding the 12-input exhaustive limit; sampled validation is labeled and seeded. `--validation none` records that verification was not run. Statevector checks are separately limited to 16 qubits.

A synthesis export contains JSON metadata and QPY with the raw computation followed by its XOR wrapper. The CLI also writes `circuit.qpy` containing exactly the selected `--view`. Experiment runs include `run.json`, a long-form `summary.csv`, and per-case circuit/metadata exports. Failed runs retain completed cases and record the error; a rerun uses a new directory.

## Inspect results

```bash
uv run --no-sync vcgc plot results/YOUR_RUN/summary.csv --metric depth --output results/depth.png
uv run --no-sync vcgc plot archive/research/data/output/benchmark_results.json --metric qubits --output results/historical-qubits.png
```

The same reader handles the archived wide CSV and nested JSON comparison formats. `--normalize` uses an XAG/VCGC baseline; `--log` changes the vertical scale. Timings are individual wall-clock measurements, not statistical speedup claims. Optional `decomposed_metrics()` requires an explicit target basis and reports its counts separately.

## Execute notebooks

```bash
uv run --no-sync vcgc notebook run notebooks/tutorials/graph_coloring.ipynb --offline
uv run --no-sync vcgc notebook run notebooks/tutorials/boolean_workspace.ipynb --offline
uv run --no-sync vcgc notebook run notebooks/studies/coloring_comparison.ipynb --offline
uv run --no-sync vcgc notebook run notebooks/studies/boolean_visual_study.ipynb --offline
```

The runner uses the invoking interpreter, a temporary kernel specification, and a fresh results directory. Use `--workspace /path/to/checkout` when launching elsewhere. The notebook source is never overwritten, including on execution failure. Offline execution blocks Python socket connections in the notebook kernel; this is a reproducibility check, not an operating-system network sandbox.

For interactive use, select the research environment's kernel and launch from the repository root. Source cells call shared library functions; executed notebooks and figures belong in `results/`.

## IBM execution

Copy `.env.example` to `.env` and configure your own account, or use an account previously saved through the IBM SDK. Credentials are read only when creating a hardware service and are never recorded in run metadata.

```bash
uv run --no-sync vcgc hardware submit results/YOUR_RUN/circuit.qpy --input-qubits 0 1 2 3 --backend YOUR_BACKEND --shots 1024
uv run --no-sync vcgc hardware retrieve YOUR_JOB_ID --output results/counts.json
uv run --no-sync vcgc hardware analyze results/counts.json --graph datasets/graphs/teaching/edge.col
```

Submission requires a QPY containing one unmeasured circuit. Input-qubit order must match the encoding; only those wires are measured. The CLI returns and saves the job identifier immediately. Retrieval and analysis do not submit new jobs. The adapter uses IBM's [SamplerV2 interface](https://quantum.cloud.ibm.com/docs/en/api/qiskit-ibm-runtime/sampler-v2). Routine tests mock submission; no hardware experiment is part of the refactor validation.

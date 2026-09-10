"""Shared synthesis entry point for coloring predicates and Boolean files."""

import hashlib
from pathlib import Path
import tempfile
import time
from vcgc.coloring import ColoringEncoding
from vcgc.benchmarks.provenance import environment
from vcgc.circuits.records import records_to_qiskit
from .native import METHODS, run_native
from .tweedledum import _xag_records
from .result import SynthesisResult


def synthesize(
    source: str | Path | ColoringEncoding,
    method: str = "xag",
    *,
    k: int = 4,
    outputs=None,
    outer_cut: int = 16,
    inner_cut: int = 4,
    executable=None,
) -> SynthesisResult:
    """Synthesize a raw computation; oracle wrappers explicitly restore workspace."""
    if method not in METHODS:
        raise ValueError(f"method must be one of {METHODS}")
    if isinstance(source, ColoringEncoding):
        with tempfile.TemporaryDirectory(prefix="vcgc-coloring-") as directory:
            path = source.write_verilog(Path(directory) / "coloring.v")
            result = synthesize(
                path,
                method,
                k=k,
                outputs=outputs,
                outer_cut=outer_cut,
                inner_cut=inner_cut,
                executable=executable,
            )
        result.metadata.update(
            source="coloring predicate",
            coloring={
                "vertices": list(source.problem.vertices),
                "edges": list(source.problem.edges),
                "colors": source.problem.colors,
                "precolored": dict(source.problem.precolored),
                "bits_per_color": source.bits_per_color,
                "input_mapping": source.input_mapping,
            },
        )
        if len(result.metadata["input_qubits"]) != source.input_count:
            raise RuntimeError("Backend changed the declared coloring input order")
        return result
    params = {"k": k} if method == "klut_bennett" else {}
    if method == "best_fit":
        params.update(outer_cut=outer_cut, inner_cut=inner_cut)
    if outputs is not None:
        params["outputs"] = list(outputs)
    start = time.perf_counter()
    md = run_native(source, method, executable=executable, **params)
    if method == "xag":
        md["gates"], md["num_qubits"] = _xag_records(md["network"])
        n, m = len(md["network"]["inputs"]), len(md["network"]["outputs"])
        md.update(
            input_qubits=list(range(n)), output_qubits=list(range(n, n + m)), steps=[]
        )
    qc = records_to_qiskit(md["gates"], md["num_qubits"])
    md.update(
        parameters=params,
        seconds=time.perf_counter() - start,
        source=str(Path(source).resolve()),
        source_sha256=hashlib.sha256(Path(source).read_bytes()).hexdigest(),
        versions=environment(),
    )
    return SynthesisResult(qc, md)

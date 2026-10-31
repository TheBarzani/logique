"""Shared synthesis entry point for coloring predicates and Boolean files."""

import hashlib
from pathlib import Path
import tempfile
import time
from logique.coloring import ColoringEncoding
from logique.benchmarks.provenance import environment
from logique.circuits.records import records_to_qiskit
from .native import METHODS, _sat_controls, run_native
from .tweedledum import _network_records, _xag_records
from .result import SynthesisResult


def synthesize(
    source: str | Path | ColoringEncoding,
    method: str = "xag",
    *,
    k: int = 4,
    outputs=None,
    outer_cut: int = 16,
    inner_cut: int = 4,
    preprocessing: str | None = None,
    strategy: str | None = None,
    qubit_budget: int | None = None,
    sat_max_steps: int | None = None,
    sat_conflict_limit: int | None = None,
    sat_time_seconds: int | None = None,
    executable=None,
) -> SynthesisResult:
    """Synthesize a raw computation; oracle wrappers explicitly restore workspace.

    Explicit ``preprocessing='none'`` or ``'refactoring'`` selects a common XAG
    before conversion to each representation. Omission preserves legacy defaults
    (unrefactored AIG Bennett, refactored XAG for the other methods).
    AIG/XAG Bennett additionally accept ``strategy='bennett'``,
    ``'bennett_inplace'``, ``'eager'`` or ``'sat_pebbling'``. SAT requires all
    four explicit budgets and supports only tiny binary AIG/XAGs (<=6 inputs,
    <=32 gates, <=64 nodes, <=16 outputs), with clean initial workspace.
    ``qubit_budget`` includes inputs, constants and output copies; it excludes
    external XOR-wrapper targets. SAT wall time is bounded by the Python process
    timeout; native search checks time between conflict-bounded solver calls.
    Omission retains Bennett mapping.
    """
    if method not in METHODS:
        raise ValueError(f"method must be one of {METHODS}")
    if preprocessing is not None and preprocessing not in ("none", "refactoring"):
        raise ValueError("preprocessing must be none or refactoring")
    if strategy is not None:
        if method not in ("aig_bennett", "xag_bennett"):
            raise ValueError("strategy is supported only for AIG/XAG Bennett methods")
        if strategy not in ("bennett", "bennett_inplace", "eager", "sat_pebbling"):
            raise ValueError(
                "strategy must be bennett, bennett_inplace, eager or sat_pebbling"
            )
    sat = dict(
        qubit_budget=qubit_budget,
        sat_max_steps=sat_max_steps,
        sat_conflict_limit=sat_conflict_limit,
        sat_time_seconds=sat_time_seconds,
    )
    if strategy == "sat_pebbling":
        _sat_controls(sat)
    elif any(value is not None for value in sat.values()):
        raise ValueError("SAT budgets require strategy='sat_pebbling'")
    if isinstance(source, ColoringEncoding):
        with tempfile.TemporaryDirectory(prefix="logique-coloring-") as directory:
            path = source.write_verilog(Path(directory) / "coloring.v")
            result = synthesize(
                path,
                method,
                k=k,
                outputs=outputs,
                outer_cut=outer_cut,
                inner_cut=inner_cut,
                preprocessing=preprocessing,
                strategy=strategy,
                **sat,
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
                "balanced_encoder": source.balanced,
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
    if preprocessing is not None:
        params["preprocessing"] = preprocessing
    if strategy is not None:
        params["strategy"] = strategy
    if strategy == "sat_pebbling":
        params.update(sat)
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
        versions=environment(executable=executable),
    )
    return SynthesisResult(qc, md)


def synthesize_expression(
    expression: str, variable_order: list[str], *, executable=None
) -> SynthesisResult:
    """Preserve expression-tree construction and input order for specialized XAG.

    Compile directly with tweedledum's expression frontend. The native bridge
    exports the Boolean reference for verification; it does not rebuild the XAG
    that is passed to synthesis.
    """
    from tweedledum.bool_function_compiler.bool_function import BoolFunction
    from tweedledum.classical import write_verilog

    start = time.perf_counter()
    function = BoolFunction.from_expression(expression, variable_order)
    network = function.logic_network()
    with tempfile.TemporaryDirectory(prefix="logique-expression-") as directory:
        path = Path(directory) / "expression.v"
        write_verilog(network, str(path))
        md = run_native(path, "xag", executable=executable)
        source_verilog = path.read_text()
    md["gates"], md["num_qubits"] = _network_records(network)
    n, m = network.num_pis(), network.num_pos()
    md.update(
        input_qubits=list(range(n)),
        output_qubits=list(range(n, n + m)),
        steps=[],
        parameters={"variable_order": variable_order},
        seconds=time.perf_counter() - start,
        source="Boolean expression",
        expression=expression,
        source_sha256=hashlib.sha256(source_verilog.encode()).hexdigest(),
        source_verilog=source_verilog,
        versions=environment(executable=executable),
    )
    return SynthesisResult(records_to_qiskit(md["gates"], md["num_qubits"]), md)

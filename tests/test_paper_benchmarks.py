"""Check historical replay, measured comparisons, and raw XAG kickback cleanup."""

import importlib.util
import inspect
import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]


@pytest.mark.integration
def test_paper_pipeline_replays_all_triangle_costs(tmp_path, monkeypatch):
    pd = pytest.importorskip("pandas")
    qiskit = pytest.importorskip("qiskit")
    pytest.importorskip("tweedledum")
    pytest.importorskip("saha_belletti")
    from logique.paths import native_executable

    try:
        executable = native_executable()
    except FileNotFoundError:
        pytest.skip("Configure the native bridge for paper benchmarks")
    if (
        "mcx_decomposition"
        not in inspect.signature(qiskit.QuantumCircuit.depth).parameters
    ):
        pytest.skip("Install the manuscript MCX depth patch")
    monkeypatch.setenv("LOGIQUE_NATIVE_EXECUTABLE", str(executable))
    spec = importlib.util.spec_from_file_location(
        "paper_benchmarks", ROOT / "tools/generate_paper_benchmarks.py"
    )
    paper = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(paper)
    observed = []
    original_adapter = paper.comparison_circuit

    def comparison(problem, variant, *, iterations, preserve_labels, measure):
        assert not problem.precolored
        assert iterations == 1
        assert preserve_labels and measure
        assert problem.vertices == (1, 2, 3)
        observed.append(variant)
        return original_adapter(
            problem,
            variant,
            iterations=iterations,
            preserve_labels=preserve_labels,
            measure=measure,
        )

    monkeypatch.setattr(paper, "comparison_circuit", comparison)
    output = paper.generate(tmp_path / "run", ["K3"])
    manifest = json.loads((output / "run.json").read_text())
    assert manifest["status"] == "complete"
    assert manifest["implementation"] == "src/logique"
    assert observed == ["original", "minimal", "simple", "balanced"]
    phase = manifest["cases"][0]
    assert phase["removed_precolors"] == {"1": 0}
    assert phase["status"] == "exhaustive"
    assert phase["assignments"] == 64 and phase["marked_assignments"] == 24
    assert phase["target_initializations"] == [0, 1]
    assert phase["phase_exact"] and phase["workspace_restored"]
    assert len(list(output.glob("*.qasm"))) == 6
    assert (output / "K3.v").exists()
    current = pd.read_csv(output / "benchmark_results.csv").set_index("benchmark")
    reference = pd.read_csv(paper.REFERENCE).set_index("benchmark")
    comparison = pd.read_csv(output / "comparison.csv")
    assert len(comparison) == 15
    assert comparison.exact.all()
    for row in comparison.itertuples():
        assert row.new == current.loc["K3", row.metric]
        assert row.old == reference.loc["K3", row.metric]
        assert row.delta == row.new - row.old
        assert row.exact == (row.delta == 0)
    measured = pd.read_csv(output / "measurement_consistent_results.csv").set_index(
        "benchmark"
    )
    assert measured.loc["K3", "vcgc_gates"] == current.loc["K3", "vcgc_gates"] + 7
    assert measured.loc["K3", "vcgc_depth"] == current.loc["K3", "vcgc_depth"] + 1
    assert measured.loc["K3", "vcgc_width"] == current.loc["K3", "vcgc_width"]
    for variant in observed:
        for metric in ("width", "depth", "gates"):
            key = f"sb_{variant}_{metric}"
            assert measured.loc["K3", key] == current.loc["K3", key]
    for path in output.glob("*.qasm"):
        text = path.read_text()
        assert text.count("= measure") == (0 if path.name == "K3_vcgc.qasm" else 6)


@pytest.mark.integration
def test_single_xag_kickback_matches_historical_amplitudes(monkeypatch):
    np = pytest.importorskip("numpy")
    pytest.importorskip("qiskit")
    pytest.importorskip("tweedledum")
    from qiskit import QuantumCircuit
    from qiskit.circuit.library.data_preparation.state_preparation import (
        UniformSuperpositionGate,
    )
    from qiskit.quantum_info import Statevector
    from logique.coloring import read_dimacs, edge_coloring_expression, encode_coloring
    from logique.synthesis import synthesize_expression
    from logique.circuits.grover import kickback_grover_circuit
    from logique.paths import native_executable
    from logique.verification import verify_kickback_oracle
    from dataclasses import replace

    try:
        executable = native_executable()
    except FileNotFoundError:
        pytest.skip("Configure the native bridge")
    problem = read_dimacs(ROOT / "datasets/graphs/benchmarks/K3.col")
    expression, variables = edge_coloring_expression(problem)
    result = synthesize_expression(expression, variables, executable=executable)
    encoding = encode_coloring(replace(problem, colors=4, precolored={}))
    assert verify_kickback_oracle(result, encoding=encoding)["workspace_restored"]
    preparation = QuantumCircuit(6)
    uniform = QuantumCircuit(2)
    uniform.append(UniformSuperpositionGate(3), [0, 1])
    for start in (0, 2, 4):
        preparation.compose(uniform.decompose(), [start, start + 1], inplace=True)
    reflection = QuantumCircuit(6)
    reflection.h(range(6))

    def extra_inverse():
        raise AssertionError("The raw XAG must not be inverted again")

    monkeypatch.setattr(result.circuit, "inverse", extra_inverse)
    circuit = kickback_grover_circuit(
        result, preparation=preparation, reflection_preparation=reflection
    )
    expected = np.zeros(64)
    for basis in range(64):
        colors = [(basis >> shift) & 3 for shift in (0, 2, 4)]
        if max(colors) < 3:
            expected[basis] = (-1 if len(set(colors)) == 3 else 1) / np.sqrt(27)
    # The historical H-based reflection is I - 2|s><s|.
    expected -= 2 * expected.mean()
    actual = Statevector.from_instruction(circuit).data
    np.testing.assert_allclose(actual[:64], expected / np.sqrt(2), atol=1e-9)
    np.testing.assert_allclose(actual[64:128], -expected / np.sqrt(2), atol=1e-9)
    np.testing.assert_allclose(actual[128:], 0, atol=1e-9)


def test_kickback_check_rejects_output_borrowing():
    pytest.importorskip("qiskit")
    from qiskit import QuantumCircuit
    from logique.coloring import ColoringProblem, encode_coloring
    from logique.synthesis import SynthesisResult
    from logique.verification import verify_kickback_oracle

    raw = QuantumCircuit(3)
    raw.x(1)
    raw.cx(1, 2)
    raw.x(2)
    # This computes constant true with clean workspace only when target=0.
    result = SynthesisResult(raw, {"input_qubits": [0], "output_qubits": [1]})
    encoding = encode_coloring(ColoringProblem((1,), (), 2))
    with pytest.raises(AssertionError, match="target=1"):
        verify_kickback_oracle(result, encoding=encoding)

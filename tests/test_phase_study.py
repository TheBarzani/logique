"""Phase-oracle semantics, common-basis metrics, and study execution."""

import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture
def native():
    pytest.importorskip("qiskit")
    pytest.importorskip("tweedledum")
    from logique.paths import native_executable

    try:
        return native_executable()
    except FileNotFoundError:
        pytest.skip("Configure the native bridge for phase-oracle tests")


@pytest.mark.integration
@pytest.mark.parametrize(
    "method", ["xag", "aig_bennett", "xag_bennett", "klut_bennett", "best_fit"]
)
def test_k3_complete_phase_action(native, method):
    from logique import read_dimacs, encode_coloring
    from logique.synthesis import synthesize
    from logique.verification import verify_phase_oracle

    encoding = encode_coloring(read_dimacs(ROOT / "datasets/graphs/benchmarks/K3.col"))
    result = synthesize(encoding, method, executable=native)
    report = verify_phase_oracle(result, encoding=encoding)
    assert report["assignments"] == 64
    assert report["marked_assignments"] == 2
    assert report["phase_exact"] and report["workspace_restored"]


@pytest.mark.integration
@pytest.mark.parametrize(
    "method", ["xag", "aig_bennett", "xag_bennett", "klut_bennett", "best_fit"]
)
def test_phase_and_lowering_against_statevector(native, method):
    import numpy as np
    from qiskit import QuantumCircuit
    from qiskit.quantum_info import Statevector
    from logique import ColoringProblem, encode_coloring
    from logique.synthesis import synthesize
    from logique.verification import verify_phase_oracle
    from logique.benchmarks.metrics import lower_circuit

    encoding = encode_coloring(ColoringProblem((1, 2), ((1, 2),), 2))
    result = synthesize(encoding, method, executable=native)
    assert verify_phase_oracle(result, encoding=encoding)["phase_exact"]
    phase = result.phase_oracle()
    lowered = lower_circuit(phase, basis_gates=["u", "cx"])
    assert set(lowered.count_ops()) <= {"u", "cx"}
    # Check every input, not just one superposition.
    for basis in range(4):
        prep = QuantumCircuit(phase.num_qubits)
        index = 0
        for i, q in enumerate(result.metadata["input_qubits"]):
            if (basis >> i) & 1:
                prep.x(q)
                index |= 1 << q
        expected = np.zeros(1 << phase.num_qubits, dtype=complex)
        expected[index] = -1 if encoding.problem.is_valid(encoding.decode(basis)) else 1
        initial = Statevector.from_instruction(prep)
        for circuit in (phase, lowered):
            np.testing.assert_allclose(
                initial.evolve(circuit).data, expected, atol=1e-9
            )


@pytest.mark.integration
def test_phase_verifier_rejects_corrupt_oracles(native):
    import numpy as np
    from logique import read_dimacs, encode_coloring
    from logique.synthesis import synthesize
    from logique.verification import verify_phase_oracle

    encoding = encode_coloring(read_dimacs(ROOT / "datasets/graphs/benchmarks/K3.col"))
    result = synthesize(encoding, "xag", executable=native)
    wrong = result.phase_oracle()
    del wrong.data[len(result.circuit.data)]
    with pytest.raises(AssertionError, match="phase marking"):
        verify_phase_oracle(result, encoding=encoding, circuit=wrong)
    wrong = result.circuit.copy()
    wrong.z(result.metadata["output_qubits"][0])
    with pytest.raises(AssertionError, match="restore"):
        verify_phase_oracle(result, encoding=encoding, circuit=wrong)
    wrong = result.phase_oracle()
    wrong.global_phase += np.pi
    with pytest.raises(AssertionError, match="phase marking"):
        verify_phase_oracle(result, encoding=encoding, circuit=wrong)
    wrong = result.phase_oracle()
    wrong.h(0)
    with pytest.raises(ValueError, match="Cannot track"):
        verify_phase_oracle(result, circuit=wrong)


@pytest.mark.integration
def test_phase_run_exports_actual_oracle_metrics(native, tmp_path):
    from qiskit import qpy
    from logique.benchmarks.runner import load_config, run_benchmarks
    from logique.benchmarks.results import load_results
    from logique.benchmarks.metrics import circuit_metrics
    from logique.visualization.results import plot_results
    import matplotlib.pyplot as plt

    config = load_config(ROOT / "configs/coloring_phase_oracle_comparison.json")
    config.update(inputs=config["inputs"][:1], output=str(tmp_path / "phase"))
    run = run_benchmarks(config, executable=native)
    manifest = json.loads((run / "run.json").read_text())
    frame = load_results(run)
    assert manifest["status"] == "complete"
    assert len(manifest["cases"]) == 5 and len(frame) == 10
    assert set(frame.validation) == {"exhaustive"}
    for case in manifest["cases"]:
        for level, suffix in (("logical", "phase"), ("decomposed", "phase_decomposed")):
            with (run / f"{case['name']}_{suffix}.qpy").open("rb") as stream:
                circuit = qpy.load(stream)[0]
            measured = circuit_metrics(circuit)
            row = frame[
                (frame.method == case["method"]) & (frame.metric_level == level)
            ].iloc[0]
            for metric in ("qubits", "depth", "gates"):
                assert row[metric] == measured[metric]
        assert case["validation"]["marked_assignments"] == 2
    with pytest.raises(ValueError, match="Mixed metric"):
        plot_results(run)
    figure = plot_results(run, metric_level="decomposed")
    plt.close(figure)


@pytest.mark.integration
def test_phase_failure_preserves_diagnostics(native, tmp_path, monkeypatch):
    from logique.benchmarks.runner import load_config, run_benchmarks
    from logique.benchmarks.results import load_results
    import logique.benchmarks.metrics as metrics

    config = load_config(ROOT / "configs/coloring_phase_oracle_comparison.json")
    config.update(
        inputs=config["inputs"][:1], methods=["xag"], output=str(tmp_path / "failed")
    )

    def fail(*args, **kwargs):
        raise RuntimeError("deliberate lowering failure")

    monkeypatch.setattr(metrics, "lower_circuit", fail)
    with pytest.raises(RuntimeError, match="deliberate"):
        run_benchmarks(config, executable=native)
    manifest = json.loads((tmp_path / "failed/run.json").read_text())
    assert manifest["status"] == manifest["cases"][0]["status"] == "failed"
    frame = load_results(tmp_path / "failed")
    assert len(frame) == 1 and frame.iloc[0].metric_level == "logical"
    assert frame.iloc[0].gates > 0


@pytest.mark.workflow
def test_phase_notebook_smoke(native, tmp_path, monkeypatch):
    nbformat = pytest.importorskip("nbformat")
    pytest.importorskip("nbclient")
    from logique.benchmarks.notebooks import execute_notebook

    source = ROOT / "experiments/studies/coloring_phase_oracle_comparison.ipynb"
    original = source.read_bytes()
    notebook = nbformat.read(source, as_version=4)
    assert all(
        not c.get("outputs") and c.get("execution_count") is None
        for c in notebook.cells
    )
    monkeypatch.setenv("LOGIQUE_PHASE_STUDY_SMOKE", "1")
    monkeypatch.delenv("LOGIQUE_PHASE_RESULTS", raising=False)
    monkeypatch.setenv("LOGIQUE_NATIVE_EXECUTABLE", str(native))
    executed = execute_notebook(
        source, output=tmp_path / "notebook", offline=True, workspace=ROOT, timeout=3600
    )
    assert source.read_bytes() == original
    manifest = json.loads((executed.parent / "benchmark/run.json").read_text())
    assert manifest["status"] == "complete" and len(manifest["cases"]) == 5
    assert len(list((executed.parent / "benchmark_charts").glob("*.png"))) == 6
    assert (
        len(list((executed.parent / "illustrations").glob("*_phase_circuit.svg"))) == 5
    )

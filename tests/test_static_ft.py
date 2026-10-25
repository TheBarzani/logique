"""Tiny independent semantic, persistence and failure checks for the FT pilot."""

import json
import math
from pathlib import Path
from unittest.mock import patch

import pytest

np = pytest.importorskip("numpy")
pytest.importorskip("qiskit")

from qiskit import QuantumCircuit  # noqa: E402
from qiskit.circuit.library import StatePreparation  # noqa: E402

from logique.benchmarks import static_ft as ft  # noqa: E402
from logique.benchmarks import rotations  # noqa: E402
from logique.coloring import ColoringEncoding, ColoringProblem  # noqa: E402


@pytest.mark.parametrize("width", [1, 2, 3, 4])
def test_signed_zero_reflection(width):
    expected = -np.eye(1 << width, dtype=complex)
    expected[0, 0] = 1
    actual = ft.numeric_matrix(ft.zero_reflection(width))
    assert np.linalg.norm(actual - expected, 2) < 3e-14


def mapped_components():
    preparation = QuantumCircuit(2, global_phase=0.27)
    preparation.h(0)
    preparation.s(1)
    oracle = QuantumCircuit(4)
    # Logical x=1 on mapping [3,1], independent of zero scratch wires 0,2.
    oracle.x(1)
    oracle.cz(3, 1)
    oracle.x(1)
    return preparation, oracle, ft.zero_reflection(2)


def test_clean_phase_mapping_and_restoration():
    a, o, s = mapped_components()
    contract = ft.validate_contract(a, o, s, [3, 1], lambda x: x == 1)
    assert contract["clean_data_columns"] == 4
    assert contract["phase_operator_error"] == 0
    assert contract["scratch_operator_error"] == 0
    assert ft.clean_indices(4, [3, 1]) == [0, 8, 2, 10]
    with pytest.raises(ValueError, match="contract failed"):
        ft.validate_contract(a, o, s, [1, 3], lambda x: x == 1)


@pytest.mark.parametrize("fault", ["sign", "scratch", "s0"])
def test_contract_rejects_phase_or_scratch_fault(fault):
    a, o, s = mapped_components()
    if fault == "sign":
        o.global_phase += math.pi
    elif fault == "scratch":
        o.cx(3, 0)
    else:
        s.global_phase += math.pi
    with pytest.raises(ValueError, match="contract failed"):
        ft.validate_contract(a, o, s, [3, 1], lambda x: x == 1)


@pytest.mark.parametrize("mapping", [[0, 0], [4, 1], [True, 1], []])
def test_invalid_mapping_rejected(mapping):
    with pytest.raises(ValueError, match="Data mapping"):
        ft.clean_indices(4, mapping)


@pytest.mark.parametrize("iterations", [0, 1])
def test_original_numeric_target_and_actual_inverse(iterations):
    a, o, s = mapped_components()
    # A includes a scalar phase; compare without phase alignment.
    out = rotations.compile_search(a, o, s, data_qubits=[3, 1], iterations=iterations)
    expected = ft.original_search_matrix(a, o, s, [3, 1], iterations)
    assert np.linalg.norm(ft.numeric_matrix(out.circuit) - expected, 2) < 1e-13
    assert out.preparation_inverse == out.preparation.circuit.inverse()
    shifted = out.circuit.copy()
    shifted.global_phase += 0.1
    assert np.linalg.norm(ft.numeric_matrix(shifted) - expected, 2) > 0.09


def test_event_probabilities_distinguish_invalid_from_improper():
    enc = ColoringEncoding(ColoringProblem(vertices=[7, 11], edges=[(7, 11)], colors=3))
    state = np.zeros(16, dtype=complex)
    state[[0, 1, 15]] = 1 / math.sqrt(3)  # equal valid, proper, invalid
    events = ft.event_probabilities(state, enc, [0, 1, 2, 3])
    assert events["proper_coloring_success"] == pytest.approx(1 / 3)
    assert events["invalid_code_leakage"] == pytest.approx(1 / 3)
    assert events["nonzero_scratch_probability"] == 0


def test_source_qpy_expansion_preserves_inverse_statepreparation(tmp_path):
    a = QuantumCircuit(2, global_phase=0.31)
    a.append(StatePreparation([1 / math.sqrt(3)] * 3 + [0]), [0, 1])
    a = a.inverse()
    loaded, record = ft.save_circuit(tmp_path, "inverse", a, emitted=False)
    assert np.linalg.norm(ft.numeric_matrix(loaded) - ft.numeric_matrix(a), 2) < 1e-13
    assert record["source_definitions_expanded"]
    assert all("state_preparation" not in item.operation.name for item in loaded.data)


def test_saved_counts_and_dependency_t_depth(tmp_path):
    circuit = QuantumCircuit(2, global_phase=0.17)
    circuit.t(0)
    circuit.tdg(1)  # same T layer
    circuit.cx(0, 1)
    circuit.t(1)  # dependent second T layer
    loaded, record = ft.save_circuit(tmp_path, "emitted", circuit, emitted=True)
    assert record["counts"] == {"t": 2, "tdg": 1, "cx": 1}
    assert record["metrics"]["t_count"] == 3
    assert record["metrics"]["t_depth"] == 2
    assert ft.sha256(tmp_path / "emitted.qpy") == record["qpy_sha256"]
    assert (
        np.linalg.norm(ft.numeric_matrix(loaded) - ft.numeric_matrix(circuit), 2)
        < 1e-14
    )


def test_qpy_semantic_corruption_rejected(tmp_path):
    circuit = QuantumCircuit(1)
    circuit.h(0)
    damaged = circuit.copy()
    damaged.global_phase = 0.1
    with patch.object(ft.qpy, "load", return_value=[damaged]):
        with pytest.raises(ValueError, match="QPY semantic failure"):
            ft.save_circuit(tmp_path, "bad", circuit, emitted=True)


def test_hash_gate_and_dense_limit():
    root = Path(__file__).resolve().parents[1]
    for name, expected in ft.ADMITTED_HASHES.items():
        assert ft.sha256(root / name) == expected
    with patch.object(ft, "sha256", return_value="changed"):
        with pytest.raises(ValueError, match="reviewed rotation hashes"):
            ft.verify_admission(root, Path("unused"))
    with pytest.raises(ft.ValidationLimitError, match="four qubits"):
        ft.numeric_matrix(QuantumCircuit(5))


def test_real_bounded_synthesis_failure_has_trials():
    a = QuantumCircuit(1)
    a.rz(0.731, 0)
    with pytest.raises(rotations.PrecisionNotReachedError) as caught:
        rotations.compile_search(
            a,
            QuantumCircuit(1),
            ft.zero_reflection(1),
            data_qubits=[0],
            iterations=1,
            options=rotations.SynthesisOptions(
                max_recursion=0, basic_approximation_depth=1
            ),
        )
    assert caught.value.metadata["attempts"][0]["recursion_degree"] == 0
    assert caught.value.metadata["component"] == "preparation"


def test_pilot_records_precision_failures_and_fallback(tmp_path):
    a = QuantumCircuit(2)
    o = QuantumCircuit(2)
    s = ft.zero_reflection(2)
    parts = {
        "preparation": a,
        "oracle": o,
        "zero_reflection": s,
        "mapping": [0, 1],
        "contract": {},
        "native": {},
        "mcx": {},
    }

    def components(problem, regime, executable):
        if len(problem.vertices) == 2:
            raise ft.ValidationLimitError("13 qubits")
        return dict(parts)

    failure = rotations.PrecisionNotReachedError(
        "bounded failure", {"attempts": [0, 1]}
    )
    with (
        patch.object(ft, "verify_admission", return_value=ft.ADMITTED_HASHES),
        patch.object(ft, "_components", side_effect=components),
        patch.object(ft, "_run_case", side_effect=failure),
    ):
        directory = ft.run_pilot(tmp_path, Path("unused"), output_root=tmp_path)
    manifest = json.loads((directory / "manifest.json").read_text())
    assert "NO GRAPH COMPARISON" in manifest["graph_comparison"]
    assert manifest["status"] == "bounded_complete"
    assert len(manifest["rows"]) == 7
    assert [r["error_budget"] for r in manifest["rows"]].count(1e-2) == 1
    for row in manifest["rows"]:
        assert row["status"] == "failed_precision"
        assert row["failure"]["trials"] == {"attempts": [0, 1]}
        assert "saved_metrics" not in row


def test_pilot_timeout_recorded(tmp_path):
    with (
        patch.object(ft, "verify_admission", return_value=ft.ADMITTED_HASHES),
        patch.object(
            ft, "_components", side_effect=ft.PilotTimeoutError("bounded timeout")
        ),
    ):
        directory = ft.run_pilot(
            tmp_path, Path("unused"), output_root=tmp_path, seconds=1
        )
    manifest = json.loads((directory / "manifest.json").read_text())
    assert manifest["status"] == "timeout"
    assert manifest["failure"]["type"] == "PilotTimeoutError"
    assert len(manifest["not_run_cases"]) == 7
    assert manifest["rows"] == []


def test_real_deadline_handler_and_allowance():
    import signal

    with pytest.raises(ft.PilotTimeoutError):
        with ft._deadline(1):
            signal.raise_signal(signal.SIGALRM)
    with pytest.raises(ValueError, match="300"):
        with ft._deadline(301):
            pytest.fail("Over-budget work must not start")


@pytest.mark.integration
def test_native_tiny_complete_search_saved_components(tmp_path):
    import os

    executable = Path(os.environ["LOGIQUE_NATIVE_EXECUTABLE"])
    root = Path(__file__).resolve().parents[1]
    ft.verify_admission(root, executable)
    parts = ft._components(
        ColoringProblem(vertices=[7], edges=[], colors=3), "R1", executable
    )
    parts["regime"] = "R1"
    result = ft._run_case(tmp_path, parts, 1, 1e-3)
    assert result["status"] == "complete"
    assert result["original_target_operator_error"] < 1e-12
    assert result["ideal_target_state_gap"] < 1e-12
    assert result["emitted"]["proper_coloring_success"] == pytest.approx(0)
    assert result["emitted"]["invalid_code_leakage"] == pytest.approx(1)
    assert result["saved_metrics"]["search"]["t_count"] > 0

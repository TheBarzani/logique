"""Regression coverage for the bounded complete-predicate C5 experiment."""

import importlib.util
import json
from pathlib import Path

import pytest


@pytest.fixture
def harness():
    path = Path(__file__).resolve().parents[1] / "tools/check_c5_complete.py"
    spec = importlib.util.spec_from_file_location("c5_complete", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def metadata(width=11, wires=None):
    return {
        "num_qubits": width,
        "input_qubits": list(range(10)) if wires is None else wires,
        "output_qubits": [10],
    }


@pytest.mark.parametrize("width", [19, 22, 9, True, 11.0])
def test_actual_width_rejected_before_quantum_work(harness, width):
    with pytest.raises(ValueError, match="actual native width"):
        harness.preflight(metadata(width))


@pytest.mark.parametrize("cap", [19, True, 0, 18.0])
def test_caller_cannot_raise_statevector_cap(harness, cap):
    with pytest.raises(ValueError, match="cap"):
        harness.preflight(metadata(), cap)


@pytest.mark.parametrize(
    "wires", [list(range(9)), [0] * 10, list(range(1, 11)), [True, *range(1, 10)]]
)
def test_native_mapping_is_validated(harness, wires):
    with pytest.raises(ValueError, match="allocation"):
        harness.preflight(metadata(wires=wires))


def test_noncontiguous_permuted_mapping_is_used(harness):
    wires = [5, 2, 8, 1, 9, 0, 7, 3, 6, 4]
    assert harness.preflight(metadata(wires=wires)) == (11, wires)
    indices = harness.physical_indices(11, wires)
    assert indices[1] == 1 << 5
    assert indices[2] == 1 << 2
    assert indices[513] == (1 << 5) + (1 << 4)
    assert len(set(indices)) == 1024
    assert all(index & (1 << 10) == 0 for index in indices)


def test_independent_classes_include_all_negative_categories(harness):
    from logique.benchmarks.ideal_iterations import count_coloring_support

    good, valid = harness.packed_classes()
    assert sum(good) == 30  # chromatic polynomial (k-1)^5-(k-1)
    assert sum(valid) == 243
    assert sum(not value for value in valid) == 781
    assert sum(code and not marked for code, marked in zip(valid, good)) == 213
    for regime, support, peak, last in (("R1", 1024, 4, 5), ("R2", 243, 2, 3)):
        from logique.benchmarks.ideal_iterations import ideal_iteration_ledger

        count = count_coloring_support(harness.problem(), regime=regime)
        assert (count.marked, count.support) == (30, support)
        ledger = ideal_iteration_ledger(30, support, max_rows=10, max_iterations=10)
        assert ledger.first_peak_iteration == peak
        assert [row.iterations for row in ledger.rows] == list(range(last + 1))


def test_evidence_is_never_overwritten(harness, tmp_path):
    path = tmp_path / "partial.json"
    harness.write_json(path, {"status": "failed"})
    with pytest.raises(FileExistsError):
        harness.write_json(path, {"status": "complete"})
    assert json.loads(path.read_text())["status"] == "failed"


def test_allocation_guard_precedes_circuit_builder(harness, monkeypatch, tmp_path):
    import logique.circuits.records

    harness.write_json(tmp_path / "native-stdout.json", metadata(22))

    def forbidden(*args, **kwargs):
        pytest.fail("wide candidate reached quantum circuit/array construction")

    monkeypatch.setattr(logique.circuits.records, "records_to_qiskit", forbidden)
    with pytest.raises(ValueError, match="actual native width"):
        harness.simulate(tmp_path, "R1")
    assert not (tmp_path / "R1").exists()


def test_absolute_phase_verifier_rejects_opposite_global_sign():
    import math
    from logique.coloring import ColoringProblem, encode_coloring
    from logique.circuits.structure import structure_oracle
    from logique.verification.phase import verify_phase_oracle

    graph = ColoringProblem((0, 1), ((0, 1),), 3)
    result = structure_oracle(graph)
    oracle = result.phase_oracle()
    oracle.global_phase += math.pi
    with pytest.raises(AssertionError, match="phase marking"):
        verify_phase_oracle(result, encoding=encode_coloring(graph), circuit=oracle)


def test_missing_domain_checks_are_detected():
    from logique.coloring import ColoringProblem, encode_coloring
    from logique.circuits.structure import structure_oracle
    from logique.verification.phase import verify_phase_oracle

    graph = ColoringProblem((0, 1), ((0, 1),), 3)
    result = structure_oracle(graph, domain_policy="domain_free")
    with pytest.raises(AssertionError, match="phase marking"):
        verify_phase_oracle(result, encoding=encode_coloring(graph))


def test_reusable_mcx_component_preserves_nonzero_spectator(harness):
    import numpy as np
    from qiskit import QuantumCircuit
    from qiskit.quantum_info import Statevector

    circuit = QuantumCircuit(8)
    circuit.mcx(list(range(6)), 6)
    lowered = harness.flatten_component(circuit)
    rng = np.random.default_rng(37)
    amplitudes = rng.normal(size=256) + 1j * rng.normal(size=256)
    amplitudes /= np.linalg.norm(amplitudes)
    expected = amplitudes.copy()
    # Independent permutation for every control/target/spectator configuration.
    for word in range(256):
        target = word ^ (64 if word & 63 == 63 else 0)
        expected[target] = amplitudes[word]
    actual = Statevector(amplitudes).evolve(lowered).data
    assert np.max(np.abs(actual - expected)) < 1e-10
    assert all(item.operation.num_qubits <= 2 for item in lowered.data)


def test_lowering_disables_zero_input_assumption(harness, monkeypatch):
    from qiskit import QuantumCircuit
    import qiskit

    def inspect(circuit, **kwargs):
        assert kwargs["qubits_initially_zero"] is False
        assert kwargs["num_processes"] == 1
        return circuit

    monkeypatch.setattr(qiskit, "transpile", inspect)
    harness.flatten_component(QuantumCircuit(1))


def test_preparation_inverse_uses_actual_emitted_gates(harness, tmp_path):
    import numpy as np
    from qiskit import qpy
    from qiskit.quantum_info import Statevector
    from logique.coloring import ColoringProblem, encode_coloring
    from logique.circuits.grover import coloring_preparation

    encoding = encode_coloring(ColoringProblem((0,), (), 3))
    forward, inverse = harness.preparation_pair(coloring_preparation(encoding))
    assert all(item.operation.name in ("u", "cx") for item in forward.data)
    path = tmp_path / "pair.qpy"
    with path.open("wb") as stream:
        qpy.dump([forward, inverse], stream)
    with path.open("rb") as stream:
        saved_forward, saved_inverse = qpy.load(stream)
    amplitudes = np.array([1, 2j, 3 - 1j, -4], dtype=complex)
    amplitudes /= np.linalg.norm(amplitudes)
    restored = (
        Statevector(amplitudes.copy()).evolve(saved_forward).evolve(saved_inverse)
    )
    assert np.max(np.abs(restored.data - amplitudes)) < 1e-12
    prepared = Statevector.from_int(0, 4).evolve(saved_forward)
    assert np.max(np.abs(prepared.data - np.array([1 / np.sqrt(3)] * 3 + [0]))) < 1e-12

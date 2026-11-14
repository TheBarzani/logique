"""Bounded synthetic checks for the analysis-only resource candidate."""

import importlib.util
from pathlib import Path

import pytest

spec = importlib.util.spec_from_file_location(
    "noisy_resource_candidate", Path("tools/noisy_resource_candidate.py").resolve()
)
subject = importlib.util.module_from_spec(spec)
spec.loader.exec_module(subject)


def test_current_inherited_imports_are_explicit():
    assert len(subject.source_contract()) == 2


def test_identity_failure_precedes_saved_circuit_load(tmp_path):
    (tmp_path / "manifest.json").write_text("{}")
    with pytest.raises(ValueError, match="identity mismatch"):
        subject.analyze_saved(tmp_path, {"inputs": {"manifest.json": "0" * 64}})


def test_evidence_is_never_overwritten(tmp_path):
    path = tmp_path / "old.json"
    path.write_text("preserve")
    with pytest.raises(FileExistsError):
        subject.write_new(path, {"new": True})
    assert path.read_text() == "preserve"


@pytest.mark.parametrize("width,layers", [(19, 4), (4, 4), (3, 5), (18, 999)])
def test_probe_caps_before_fixture_allocation(width, layers):
    with pytest.raises(ValueError, match="prebounded"):
        subject.synthetic_fixture(width, layers)


def test_inventory_retains_operand_and_readout_order():
    from qiskit import QuantumCircuit

    circuit = QuantumCircuit(3, 1)
    circuit.cx(2, 0)
    circuit.cx(0, 2)
    circuit.measure(2, 0)
    snapshot = {
        "errors": [
            {"type": "qerror", "operations": ["cx"], "gate_qubits": [[2, 0]]},
            {"type": "roerror", "operations": ["measure"], "gate_qubits": [[2]]},
        ]
    }
    inventory = subject.channel_inventory(snapshot, circuit)
    assert inventory["quantum_applications_per_shot"] == 1
    assert inventory["readout_applications_per_shot"] == 1
    assert inventory["entries"][0]["ordered_compact_qargs"] == [2, 0]
    snapshot["errors"].append(snapshot["errors"][0])
    with pytest.raises(ValueError, match="Duplicate"):
        subject.channel_inventory(snapshot, circuit)


def test_serial_decoder_matches_explicit_asymmetric_local_channel():
    """Use direct local Kraus algebra, no full-system density matrix."""
    import numpy as np
    from qiskit.quantum_info import SuperOp

    _, snapshot = subject.synthetic_fixture(3, 4)
    decoded = subject.noise_from_snapshot(snapshot)
    actual = SuperOp(decoded._local_quantum_errors["cx"][(2, 1)]).data

    def damping(gamma):
        return (
            np.diag([1, np.sqrt(1 - gamma)]),
            np.array([[0, np.sqrt(gamma)], [0, 0]]),
        )

    operators = [np.kron(a, b) for a in damping(0.13) for b in damping(0.31)]
    expected = sum(np.kron(k.conj(), k) for k in operators)
    np.testing.assert_allclose(actual, expected, atol=1e-14, rtol=0)
    swapped = [np.kron(a, b) for a in damping(0.31) for b in damping(0.13)]
    assert np.max(abs(expected - sum(np.kron(k.conj(), k) for k in swapped))) > 0.1
    np.testing.assert_array_equal(
        decoded._local_readout_errors[(0,)].probabilities,
        [[0.83, 0.17], [0.09, 0.91]],
    )


@pytest.mark.parametrize("fusion", [False, True])
def test_dense_candidate_preserves_full_complex_fixture_state(fusion):
    """Compare all amplitudes on three wires, not just probabilities."""
    import numpy as np
    from qiskit.quantum_info import Statevector
    from qiskit_aer import AerSimulator

    circuit, _ = subject.synthetic_fixture(3, 4)
    pure = circuit.remove_final_measurements(inplace=False)
    pure.global_phase = 0.37
    expected = Statevector.from_instruction(pure).data.copy()
    pure.save_statevector()
    result = (
        AerSimulator(**subject.trajectory_options(fusion=fusion))
        .run(pure, shots=1, seed_simulator=74730)
        .result()
    )
    assert result.success
    np.testing.assert_allclose(result.get_statevector().data, expected, atol=1e-13)


def test_stages_survive_result_failure(tmp_path, monkeypatch):
    import qiskit_aer

    class FailedJob:
        def result(self):
            raise RuntimeError("synthetic result failure")

    class FakeSimulator:
        def __init__(self, **options):
            assert options["fusion_enable"] is False
            assert options["max_parallel_threads"] == 1

        def run(self, circuit, **options):
            assert options == {"shots": 64, "seed_simulator": 74730}
            return FailedJob()

    monkeypatch.setattr(qiskit_aer, "AerSimulator", FakeSimulator)
    with pytest.raises(RuntimeError, match="synthetic result failure"):
        subject.profile_fixture(tmp_path, 3, False)
    assert len(list(tmp_path.glob("stage-*.json"))) == 5
    assert not (tmp_path / "fixture.json").exists()

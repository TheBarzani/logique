"""Routed NISQ metrics on the recorded FakeTorino snapshot."""

import math

import pytest

np = pytest.importorskip("numpy")
pytest.importorskip("qiskit")
pytest.importorskip("qiskit_ibm_runtime")

from qiskit import QuantumCircuit  # noqa: E402
from qiskit.circuit.library import RXGate  # noqa: E402
from qiskit.quantum_info import Operator  # noqa: E402

from logique.benchmarks import routing  # noqa: E402


@pytest.mark.parametrize("angle", [math.pi, -math.pi])
@pytest.mark.parametrize("ctrl_state", [0, 1, 2, 3])
def test_prelowering_preserves_controlled_rx(angle, ctrl_state):
    circuit = QuantumCircuit(3)
    circuit.append(RXGate(angle).control(2, ctrl_state=ctrl_state), [2, 0, 1])
    lowered = routing.prelower(circuit)
    assert "ccrx" not in "".join(lowered.count_ops())
    np.testing.assert_allclose(
        Operator(lowered).data, Operator(circuit).data, atol=1e-9
    )


def test_prelowering_requires_expanded_mcx():
    circuit = QuantumCircuit(4)
    circuit.mcx([0, 1, 2], 3)
    with pytest.raises(ValueError, match="decompose_mcx"):
        routing.prelower(circuit)


def test_routed_metrics_are_deterministic_for_fixed_seeds():
    circuit = QuantumCircuit(4)
    circuit.ccx(0, 1, 2)
    circuit.append(RXGate(math.pi).control(2), [1, 2, 3])
    first = routing.routed_metrics(circuit, seeds=(11, 23))
    second = routing.routed_metrics(circuit, seeds=(11, 23))
    assert first["routed"] and first == second
    assert first["backend"] == "fake_torino" and first["seeds"] == [11, 23]
    assert first["two_qubit_count"] >= 10
    assert 0 < first["esp"] < 1 and first["duration_s"] > 0
    assert first["active_qubits"] >= 4
    assert first["best_seed"] in (11, 23)


def test_wide_circuits_are_labelled_infeasible():
    circuit = QuantumCircuit(134)
    circuit.cx(0, 133)
    record = routing.routed_metrics(circuit)
    assert record["routed"] is False
    assert "134" in record["reason"]


@pytest.mark.parametrize(
    "qubits, shape", [(120, (10, 12)), (11, (3, 4)), (4, (2, 2)), (1, (1, 2))]
)
def test_grid_backend_follows_the_nighthawk_lattice(qubits, shape):
    backend = routing.grid_backend(qubits)
    rows, columns = shape
    assert backend.num_qubits == rows * columns >= qubits
    assert f"{rows}x{columns}" in backend.name
    degree = {}
    for a, b in backend.coupling_map.get_edges():
        degree[a] = degree.get(a, 0) + 1
    # Each qubit couples to at most four neighbours (edges are listed both ways).
    assert max(degree.values(), default=0) <= 4
    assert "cz" in backend.target.operation_names


def test_routed_metrics_on_an_uncalibrated_grid():
    circuit = QuantumCircuit(5)
    circuit.ccx(0, 1, 4)
    circuit.append(RXGate(math.pi).control(2), [2, 3, 4])
    backend = routing.grid_backend(circuit.num_qubits)
    record = routing.routed_metrics(circuit, backend=backend, seeds=(11, 23))
    assert record["routed"] and record["two_qubit_count"] >= 10
    assert record["esp"] is None and record["duration_s"] is None
    assert record["backend"].startswith("square grid")

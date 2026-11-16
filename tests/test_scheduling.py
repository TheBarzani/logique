"""Reordering commuting gates keeps the unitary and never deepens the circuit."""

import random

import pytest

pytest.importorskip("qiskit")

from qiskit import QuantumCircuit  # noqa: E402
from qiskit.quantum_info import Operator  # noqa: E402

from logique.benchmarks import costs  # noqa: E402
from logique.benchmarks.scheduling import (  # noqa: E402
    mirrored_middle,
    reschedule,
    reschedule_mirrored,
    schedule_order,
)


def t_depth(circuit):
    return costs.ft_metrics(costs.clifford_t(circuit))["t_depth"]


def random_circuit(seed, width=5, gates=24):
    rng = random.Random(seed)
    qc = QuantumCircuit(width)
    for _ in range(gates):
        kind = rng.choice(["cx", "ccx", "x", "z", "t", "h", "s", "ccx", "cx"])
        wires = rng.sample(range(width), {"cx": 2, "ccx": 3}.get(kind, 1))
        getattr(qc, kind)(*wires)
    return qc


@pytest.mark.parametrize("seed", range(12))
def test_reschedule_keeps_the_unitary_and_the_gates(seed):
    circuit = random_circuit(seed)
    scheduled = reschedule(circuit)
    assert Operator(scheduled).equiv(Operator(circuit))
    assert sorted(map(str, scheduled.count_ops().items())) == sorted(
        map(str, circuit.count_ops().items())
    )
    assert t_depth(scheduled) <= t_depth(circuit)


def test_reschedule_runs_commuting_toffolis_in_parallel():
    circuit = QuantumCircuit(9)
    circuit.ccx(0, 1, 5)
    circuit.ccx(0, 2, 6)
    circuit.ccx(1, 3, 7)
    circuit.ccx(2, 4, 8)
    order, bound = schedule_order(circuit)
    scheduled = reschedule(circuit)
    # Sharing only controls, the four gates commute: two rounds instead of three.
    assert t_depth(circuit) == 3 * bound
    assert t_depth(scheduled) == 2 * bound
    assert sorted(order) == [0, 1, 2, 3]


def _mirrored_oracle(block_order):
    """Two in-place comparisons computed, joined onto the output, then undone."""
    qc = QuantumCircuit(8)
    blocks = []
    for (a, b), target in (((0, 2), 4), ((1, 3), 5)):
        block = QuantumCircuit(8)
        block.cx(a, b)
        block.ccx(b, 3 if b == 2 else 2, target)
        block.cx(a, b)
        blocks.append(block)
    for block in blocks:
        qc.compose(block, inplace=True)
    qc.ccx(4, 5, 7)
    for i in block_order:
        qc.compose(blocks[i].inverse(), inplace=True)
    return qc


@pytest.mark.parametrize("block_order", [(1, 0), (0, 1)])
def test_reschedule_mirrored_keeps_the_oracle(block_order):
    circuit = _mirrored_oracle(block_order)
    middle = mirrored_middle(circuit, 7)
    assert middle == len(circuit.data) // 2
    scheduled = reschedule_mirrored(circuit, middle)
    assert Operator(scheduled).equiv(Operator(circuit))
    assert t_depth(scheduled) <= t_depth(circuit)


def test_reschedule_mirrored_rejects_a_second_half_of_other_gates():
    circuit = _mirrored_oracle((1, 0))
    broken = circuit.copy_empty_like()
    for k, inst in enumerate(circuit.data):
        operation = inst.operation
        if k == len(circuit.data) - 1:
            broken.cz(*inst.qubits)  # replaces the last CX
            continue
        broken.append(operation, inst.qubits)
    with pytest.raises(ValueError):
        reschedule_mirrored(broken, len(broken.data) // 2)
    assert mirrored_middle(broken, 0) is None

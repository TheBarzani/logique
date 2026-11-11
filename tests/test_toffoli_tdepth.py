"""T-depth of logique's emitted Toffoli lowering (ledger row C8, TASK-28).

Uses logique's own ``clifford_t`` and ``weighted_depth`` (longest dependency path counting only T/Tdg),
and checks each lowered circuit against the exact unitary so the cost is not of a wrong circuit.
"""

import itertools

import pytest

pytest.importorskip("qiskit")

from qiskit import QuantumCircuit  # noqa: E402
from qiskit.quantum_info import Operator  # noqa: E402

from logique.benchmarks.costs import clifford_t, weighted_depth  # noqa: E402

T_WEIGHTS = {"t": 1, "tdg": 1}


def _t_count(circuit):
    ops = circuit.count_ops()
    return ops.get("t", 0) + ops.get("tdg", 0)


def _lower(source):
    lowered = clifford_t(source)
    assert Operator(lowered).equiv(Operator(source)), "lowering is not equivalent"
    return lowered


def test_single_toffoli_t_count_and_depth():
    source = QuantumCircuit(3)
    source.ccx(0, 1, 2)
    lowered = _lower(source)
    assert _t_count(lowered) == 7
    assert weighted_depth(lowered, T_WEIGHTS) == 3


def test_disjoint_toffolis_depth_is_not_sum_of_isolated_depths():
    parallel = QuantumCircuit(6)
    parallel.ccx(0, 1, 2)
    parallel.ccx(3, 4, 5)
    lowered = _lower(parallel)
    assert _t_count(lowered) == 14
    assert weighted_depth(lowered, T_WEIGHTS) == 3  # not 3 + 3


def test_overlapping_toffoli_pairs_with_this_gadget_add_up():
    """Measured, not assumed: every pair sharing a qubit (5 qubits, all 900 placements) has depth 6 = 3 + 3.

    The gadget puts T gates on all three wires in its first layer and its CNOT network couples them, so any
    shared wire serialises the two gadgets. The manuscript's 'not the sum' therefore holds only for gadgets
    on disjoint qubits (or for other gadgets/compilations).
    """
    triples = [(a, b, c) for a, b, c in itertools.permutations(range(5), 3) if a < b]
    for x in triples:
        for y in triples:
            circuit = QuantumCircuit(5)
            circuit.ccx(*x)
            circuit.ccx(*y)
            assert weighted_depth(clifford_t(circuit), T_WEIGHTS) == 6, (x, y)

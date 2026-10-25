"""Explicit MCX decompositions, Clifford+T gadgets, and cost metrics."""

import math
from pathlib import Path

import pytest

np = pytest.importorskip("numpy")
pytest.importorskip("qiskit")

from qiskit import QuantumCircuit  # noqa: E402
from qiskit.circuit.library import (  # noqa: E402
    CCXGate,
    CHGate,
    MCXGate,
    RCCXGate,
    RXGate,
)
from qiskit.quantum_info import Operator  # noqa: E402

from logique.benchmarks import costs  # noqa: E402

RESTORING = sorted(
    name
    for name, item in costs.MCX_DECOMPOSITIONS.items()
    if item.workspace != "throwaway"
)


def single(gate, width):
    circuit = QuantumCircuit(width)
    circuit.append(gate, range(gate.num_qubits))
    return circuit


def assert_equal_on_clean_ancillas(actual, expected, original_width):
    """Compare columns whose appended ancillas start in |0>."""
    padded = QuantumCircuit(actual.num_qubits)
    padded.compose(expected, qubits=range(expected.num_qubits), inplace=True)
    columns = [i for i in range(2**actual.num_qubits) if i >> original_width == 0]
    np.testing.assert_allclose(
        Operator(actual).data[:, columns],
        Operator(padded).data[:, columns],
        atol=1e-9,
    )


@pytest.mark.parametrize(
    "gate,t_count,t_depth",
    [
        (CCXGate(), 7, 3),
        (CCXGate(ctrl_state=1), 7, 3),
        (RCCXGate(), 4, 2),
        (RCCXGate().inverse(), 4, 2),
        (RXGate(math.pi).control(2), 4, 2),
        (RXGate(-math.pi).control(2, ctrl_state=2), 4, 2),
        (CHGate(ctrl_state=0), 2, 2),
    ],
)
def test_gadgets_are_exact_with_known_t_costs(gate, t_count, t_depth):
    circuit = single(gate, gate.num_qubits)
    lowered = costs.clifford_t(circuit)
    np.testing.assert_allclose(
        Operator(lowered).data, Operator(circuit).data, atol=1e-9
    )
    metrics = costs.ft_metrics(lowered)
    assert (metrics["t_count"], metrics["t_depth"], metrics["rotation_count"]) == (
        t_count,
        t_depth,
        0,
    )


@pytest.mark.parametrize("method", RESTORING)
@pytest.mark.parametrize("controls", [3, 4])
def test_restoring_decompositions_are_exact(method, controls):
    width = controls + 3  # two spare wires that dirty constructions may borrow
    circuit = single(MCXGate(controls, ctrl_state=(1 << controls) - 2), width)
    decomposed, info = costs.decompose_mcx(circuit, method)
    assert info["mcx_gates"] == 1 and info["garbage_ancillas"] == 0
    assert decomposed.num_qubits == width + info["appended_ancillas"]
    if costs.MCX_DECOMPOSITIONS[method].workspace == "dirty":
        # Borrowed wires may hold any state, so the whole unitary must match.
        assert info["appended_ancillas"] == 0
        np.testing.assert_allclose(
            Operator(decomposed).data, Operator(circuit).data, atol=1e-9
        )
    else:
        assert_equal_on_clean_ancillas(decomposed, circuit, width)
    lowered = costs.clifford_t(decomposed)
    assert set(lowered.count_ops()) <= {*costs.CLIFFORD_T_BASIS, "rz"}
    assert_equal_on_clean_ancillas(lowered, circuit, width)


def test_clean_wires_are_used_before_appending_and_reused():
    circuit = QuantumCircuit(7)
    circuit.mcx([0, 1, 2, 3], 4)
    circuit.mcx([0, 1, 2, 4], 3)
    decomposed, info = costs.decompose_mcx(circuit, "clean_tree", clean_wires=[5, 6])
    assert decomposed.num_qubits == 7
    assert info["appended_ancillas"] == 0 and info["clean_wires_used"] == 2
    columns = [i for i in range(2**7) if i >> 5 == 0]
    np.testing.assert_allclose(
        Operator(decomposed).data[:, columns],
        Operator(circuit).data[:, columns],
        atol=1e-9,
    )
    with pytest.raises(ValueError, match="clean_wires"):
        costs.decompose_mcx(circuit, "clean_tree", clean_wires=[4])


def test_dirty_constructions_borrow_before_appending():
    roomy = single(MCXGate(4), 7)
    _, info = costs.decompose_mcx(roomy, "n_dirty_i15")
    assert (info["appended_ancillas"], info["borrowed_dirty_wires"]) == (0, 2)
    tight = single(MCXGate(4), 5)
    decomposed, info = costs.decompose_mcx(tight, "n_dirty_i15")
    assert (info["appended_ancillas"], decomposed.num_qubits) == (2, 7)


def test_throwaway_tree_needs_its_mirror():
    block = single(MCXGate(4), 6)  # computes the AND of wires 0-3 into wire 4
    compute, info = costs.decompose_mcx(block, "throwaway_tree")
    assert info["garbage_ancillas"] == 2 and compute.num_qubits == 8
    alone = Operator(compute).data
    leaked = [i for i in range(2**6) if np.abs(alone[2**6 :, i]).max() > 1e-9]
    assert leaked, "garbage remains on the ancillas without a mirrored gate"
    oracle = compute.copy()
    oracle.z(4)
    oracle.compose(compute.inverse(), inplace=True)
    reference = block.copy()
    reference.z(4)
    reference.compose(block.inverse(), inplace=True)
    assert_equal_on_clean_ancillas(oracle, reference, 6)
    with pytest.raises(ValueError, match="garbage"):
        costs.decompose_mcx(block, "throwaway_tree", clean_wires=[5])


@pytest.mark.parametrize(
    "method,controls,count,depth",
    [
        ("clean_tree", 4, 5, 3),
        ("clean_tree", 5, 7, 5),
        ("throwaway_tree", 4, 3, 2),
        ("throwaway_tree", 5, 4, 3),
    ],
)
def test_tree_toffoli_counts(method, controls, count, depth):
    decomposed, _ = costs.decompose_mcx(single(MCXGate(controls), controls + 1), method)
    metrics = costs.toffoli_metrics(decomposed)
    assert (metrics["toffoli_count"], metrics["toffoli_depth"]) == (count, depth)


def test_rotations_are_counted_and_priced_separately():
    from qiskit.circuit.library.data_preparation.state_preparation import (
        UniformSuperpositionGate,
    )

    preparation = single(UniformSuperpositionGate(3), 2)
    lowered = costs.clifford_t(preparation)
    assert Operator(lowered).equiv(Operator(preparation))
    per_rotation = costs.rotation_t_count(1e-3)
    assert per_rotation == 30
    metrics = costs.ft_metrics(lowered, rotation_t=per_rotation)
    assert (metrics["t_count"], metrics["rotation_count"]) == (2, 1)
    assert metrics["total_t_count"] == 2 + 30
    with pytest.raises(ValueError, match="Clifford"):
        costs.ft_metrics(single(CCXGate(), 3))
    with pytest.raises(ValueError, match="decompose_mcx"):
        costs.clifford_t(single(MCXGate(3), 4))


def test_grover_helpers_match_known_success_probabilities():
    # Unprecolored K3 with three valid codes per vertex: 6 of 27 assignments.
    assert costs.grover_success(6 / 27, 1) == pytest.approx(0.9903978, abs=1e-7)
    assert costs.optimal_iterations(6 / 27) == 1
    # Eight-vertex path, two colors, Hadamard preparation: 2 of 256 assignments.
    assert costs.grover_success(2 / 256, 1) == pytest.approx(0.0689, abs=1e-4)
    assert costs.optimal_iterations(2 / 256) == 8
    assert costs.optimal_iterations(1.0) == 0
    with pytest.raises(ValueError):
        costs.optimal_iterations(0.0)
    with pytest.raises(ValueError):
        costs.rotation_t_count(1.0)


@pytest.mark.integration
def test_xag_oracle_t_count_follows_its_and_gates():
    pytest.importorskip("tweedledum")
    from logique import encode_coloring, read_dimacs
    from logique.paths import native_executable
    from logique.synthesis import synthesize

    try:
        native_executable()
    except FileNotFoundError:
        pytest.skip("Configure the native bridge for synthesis tests")
    root = Path(__file__).resolve().parents[1]
    problem = read_dimacs(root / "datasets/graphs/benchmarks/K3.col")
    result = synthesize(encode_coloring(problem), "xag")
    summary = result.summary()
    assert summary["mcx_3plus"] == 0
    metrics = costs.ft_metrics(costs.clifford_t(result.circuit))
    # Exact Toffoli gates cost 7 T gates; controlled Rx(±pi) gates cost 4.
    assert metrics["rotation_count"] == 0
    assert (
        metrics["t_count"] == 7 * summary["exact_ccx"] + 4 * summary["controlled_rx_pi"]
    )

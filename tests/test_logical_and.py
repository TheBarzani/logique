"""Measurement-based uncomputation of logical-AND pairs."""

import math
from pathlib import Path

import pytest

np = pytest.importorskip("numpy")
pytest.importorskip("qiskit")
pytest.importorskip("qiskit_aer")

from qiskit import QuantumCircuit, transpile  # noqa: E402
from qiskit.circuit.library import MCXGate, RCCXGate, RXGate  # noqa: E402
from qiskit.quantum_info import Statevector  # noqa: E402
from qiskit_aer import AerSimulator  # noqa: E402

from logique.benchmarks import costs, logical_and  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]


def assert_dynamic_matches(original, dynamic, clean, *, seed=7, shots=6):
    """Every shot of the dynamic circuit must reproduce the unitary state."""
    rng = np.random.default_rng(seed)
    preparation = QuantumCircuit(original.num_qubits)
    for q in range(original.num_qubits):
        if q not in clean:
            preparation.ry(rng.uniform(0.2, math.pi - 0.2), q)
            preparation.rz(rng.uniform(0, 2 * math.pi), q)
    expected = Statevector(preparation.compose(original))
    run = dynamic.copy_empty_like()
    run.compose(preparation, qubits=range(original.num_qubits), inplace=True)
    run.compose(dynamic, inplace=True)
    run.save_statevector(pershot=True)
    simulator = AerSimulator(method="statevector")
    result = simulator.run(
        transpile(run, simulator), shots=shots, seed_simulator=seed
    ).result()
    states = result.data()["statevector"]
    assert len(states) == shots
    for state in states:
        overlap = np.vdot(expected.data, np.asarray(state))
        assert abs(overlap) ** 2 == pytest.approx(1, abs=1e-9)


def and_phase_oracle(gate_pair, ctrl_state=3):
    """Compute an AND into clean wire 2, flip its phase, then uncompute it."""
    compute, uncompute = gate_pair
    circuit = QuantumCircuit(3)
    circuit.append(compute, [0, 1, 2])
    circuit.z(2)
    circuit.append(uncompute, [0, 1, 2])
    return circuit


@pytest.mark.parametrize(
    "pair",
    [
        (MCXGate(2), MCXGate(2)),
        (MCXGate(2, ctrl_state=1), MCXGate(2, ctrl_state=1)),
        (RCCXGate(), RCCXGate().inverse()),
        (RXGate(math.pi).control(2), RXGate(-math.pi).control(2)),
        (
            RXGate(math.pi).control(2, ctrl_state=2),
            RXGate(-math.pi).control(2, ctrl_state=2),
        ),
    ],
)
def test_single_pair_is_exact_and_cheaper(pair):
    circuit = and_phase_oracle(pair)
    assert logical_and.find_and_pairs(circuit, clean_wires=[2]) == {0: 2}
    dynamic, skeleton, info = logical_and.measurement_assisted(circuit, clean_wires=[2])
    assert info["and_pairs"] == info["measurements"] == 1
    assert dynamic.count_ops()["measure"] == 1
    assert_dynamic_matches(circuit, dynamic, clean={2})
    metrics = logical_and.measurement_assisted_metrics(circuit, clean_wires=[2])
    assert metrics["t_count"] == 4
    assert metrics["reaction_depth"] == 1


def test_targets_must_start_clean():
    circuit = and_phase_oracle((MCXGate(2), MCXGate(2)))
    assert logical_and.find_and_pairs(circuit) == {}
    _, _, info = logical_and.measurement_assisted(circuit)
    assert info["and_pairs"] == 0


def test_controls_may_change_if_their_and_is_restored():
    circuit = QuantumCircuit(4)
    circuit.ccx(0, 1, 3)
    circuit.cx(2, 0)  # a control changes and is restored before the uncompute
    circuit.z(3)
    circuit.cx(2, 0)
    circuit.ccx(0, 1, 3)
    # Simulation confirms the pair without any restoration guarantee.
    pairs = logical_and.find_and_pairs(circuit, clean_wires=[3], restored_wires=[])
    assert pairs == {0: 4}
    dynamic, _, info = logical_and.measurement_assisted(circuit, clean_wires=[3])
    assert info["pair_check"] == "exhaustive"
    assert_dynamic_matches(circuit, dynamic, clean={3})


def test_a_changed_and_blocks_the_pair():
    circuit = QuantumCircuit(4)
    circuit.ccx(0, 1, 3)
    circuit.cx(2, 0)  # the control is never restored
    circuit.z(3)
    circuit.ccx(0, 1, 3)
    assert logical_and.find_and_pairs(circuit, clean_wires=[3], restored_wires=[]) == {}


def test_unknown_values_block_unconfirmed_pairs():
    circuit = QuantumCircuit(4)
    circuit.ccx(0, 1, 3)
    circuit.h(0)  # leaves the computational basis, so the values are unknown
    circuit.h(0)
    circuit.ccx(0, 1, 3)
    assert logical_and.find_and_pairs(circuit, clean_wires=[3], restored_wires=[]) == {}


def test_reused_wires_pair_each_computation():
    circuit = QuantumCircuit(5)
    for controls in ((0, 1), (2, 3)):
        circuit.ccx(*controls, 4)
        circuit.z(4)
        circuit.ccx(*controls, 4)
    pairs = logical_and.find_and_pairs(circuit, clean_wires=[4])
    assert pairs == {0: 2, 3: 5}
    dynamic, _, info = logical_and.measurement_assisted(circuit, clean_wires=[4])
    assert info["reaction_depth"] == 2
    assert_dynamic_matches(circuit, dynamic, clean={4})


def test_restoring_tree_uncomputes_its_internal_nodes_by_measurement():
    circuit = QuantumCircuit(5)
    circuit.append(MCXGate(4), range(5))
    decomposed, info = costs.decompose_mcx(circuit, "clean_tree")
    ancillas = list(range(5, 5 + info["appended_ancillas"]))
    static = costs.ft_metrics(costs.clifford_t(decomposed))
    assisted = logical_and.measurement_assisted_metrics(
        decomposed, clean_wires=ancillas
    )
    assert static["t_count"] == 8 * 4 - 9
    assert assisted["and_pairs"] == 2
    assert assisted["t_count"] == 4 * 2 + 7
    dynamic, _, _ = logical_and.measurement_assisted(decomposed, clean_wires=ancillas)
    assert_dynamic_matches(decomposed, dynamic, clean=set(ancillas))


def test_mcx_gates_must_be_expanded_first():
    circuit = QuantumCircuit(4)
    circuit.mcx([0, 1, 2], 3)
    with pytest.raises(ValueError, match="decompose_mcx"):
        logical_and.find_and_pairs(circuit)


@pytest.fixture
def k3_xag():
    pytest.importorskip("tweedledum")
    from logique import encode_coloring, read_dimacs
    from logique.paths import native_executable
    from logique.synthesis import synthesize

    try:
        native_executable()
    except FileNotFoundError:
        pytest.skip("Configure the native bridge for synthesis tests")
    problem = read_dimacs(ROOT / "datasets/graphs/benchmarks/K3.col")
    return synthesize(encode_coloring(problem), "xag")


@pytest.mark.integration
def test_k3_xag_kickback_oracle(k3_xag):
    inputs = set(k3_xag.metadata["input_qubits"])
    outputs = set(k3_xag.metadata["output_qubits"])
    workspace = sorted(set(range(k3_xag.circuit.num_qubits)) - inputs - outputs)
    raw = k3_xag.circuit
    assisted = logical_and.measurement_assisted_metrics(raw, clean_wires=workspace)
    summary = k3_xag.summary()
    # Each controlled Rx(±pi) pair becomes a 4-T AND and a measurement; the
    # exact Toffoli on the output target stays static.
    assert assisted["and_pairs"] == summary["controlled_rx_pi"] // 2
    assert assisted["t_count"] == 4 * assisted["and_pairs"] + 7 * summary["exact_ccx"]
    dynamic, _, _ = logical_and.measurement_assisted(raw, clean_wires=workspace)
    assert_dynamic_matches(raw, dynamic, clean=set(workspace), shots=3)


@pytest.mark.integration
def test_k3_xag_phase_oracle(k3_xag):
    inputs = set(k3_xag.metadata["input_qubits"])
    oracle = k3_xag.phase_oracle()
    clean = sorted(set(range(oracle.num_qubits)) - inputs)
    assisted = logical_and.measurement_assisted_metrics(oracle, clean_wires=clean)
    summary = k3_xag.summary()
    # Both halves pair their internal ANDs; the output AND pairs across them.
    expected = summary["controlled_rx_pi"] + summary["exact_ccx"]
    assert assisted["and_pairs"] == expected
    assert assisted["t_count"] == 4 * expected
    dynamic, _, _ = logical_and.measurement_assisted(oracle, clean_wires=clean)
    assert_dynamic_matches(oracle, dynamic, clean=set(clean), shots=3)


@pytest.mark.parametrize("controls", [3, 8])
def test_isolated_restoring_tree_with_measurement(controls):
    row = logical_and.isolated_mcx_assisted_costs("clean_tree", controls)
    # n - 2 internal nodes become 4-T ANDs; the gate on the target stays exact.
    assert row["and_pairs"] == controls - 2
    assert row["t_count"] == 4 * (controls - 2) + 7
    assert row["ancillas"] == controls - 2

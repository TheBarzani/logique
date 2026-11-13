"""Alternative preparations of the valid colors and their costs."""

import math

import pytest

np = pytest.importorskip("numpy")
pytest.importorskip("qiskit")

from qiskit import QuantumCircuit  # noqa: E402
from qiskit.quantum_info import Operator, Statevector  # noqa: E402

from logique.benchmarks import costs  # noqa: E402
from logique.circuits import preparation as prep  # noqa: E402
from logique.coloring.model import ColoringProblem  # noqa: E402


def proportional(a, b):
    """Whether a equals b up to a global phase."""
    index = np.unravel_index(np.argmax(abs(b)), b.shape)
    phase = a[index] / b[index]
    return math.isclose(abs(phase), 1, abs_tol=1e-9) and np.allclose(
        a, phase * b, atol=1e-9
    )


def rz(angle):
    return np.diag([np.exp(-0.5j * angle), np.exp(0.5j * angle)])


def ry(angle):
    return Operator(QuantumCircuit(1).compose(_ry(angle))).data


def _ry(angle):
    qc = QuantumCircuit(1)
    qc.ry(angle, 0)
    return qc


def uniform(colors, width):
    state = np.zeros(1 << width)
    state[:colors] = 1 / math.sqrt(colors)
    return state


@pytest.mark.parametrize("denominator", [3, 5])
def test_exact_rotations_succeed_or_leave_the_target_unchanged(denominator):
    rotation = prep.EXACT_ROTATIONS[denominator]
    unitary = Operator(rotation.attempt).data
    ancillas = rotation.attempt.num_qubits - 1
    total = 0.0
    for outcome in range(1 << ancillas):
        block = unitary[np.ix_([(outcome << 1) | t for t in (0, 1)], [0, 1])]
        probability = float(np.real(np.trace(block.conj().T @ block)) / 2)
        total += probability
        if probability < 1e-12:
            continue
        block = block / math.sqrt(probability)
        if format(outcome, f"0{ancillas}b") == rotation.success:
            assert math.isclose(probability, float(rotation.probability))
            assert proportional(block, rz(rotation.angle))
        else:
            assert proportional(block, np.eye(2))
    assert math.isclose(total, 1)
    counts = costs.ft_metrics(costs.clifford_t(rotation.attempt))
    assert counts["t_count"] == rotation.t_per_attempt * (1 if denominator == 3 else 2)
    assert counts["rotation_count"] == 0


@pytest.mark.parametrize("denominator", [3, 5])
def test_exact_rotation_gates_are_the_shukla_vedula_rotations(denominator):
    angle = prep.EXACT_ROTATIONS[denominator].angle
    gate = prep.ExactRotationGate(denominator)
    assert proportional(Operator(gate).data, ry(angle))
    assert proportional(Operator(gate.inverse()).data, ry(-angle))
    # Ry(angle) = S·H·Rz(angle)·H·S^dagger, so the attempt realizes the gate.
    wrapped = QuantumCircuit(1)
    wrapped.sdg(0)
    wrapped.h(0)
    wrapped.rz(angle, 0)
    wrapped.h(0)
    wrapped.s(0)
    assert proportional(Operator(wrapped).data, ry(angle))


@pytest.mark.parametrize("colors", range(2, 21))
def test_vertex_preparations_are_uniform(colors):
    width = max(1, (colors - 1).bit_length())
    target = uniform(colors, width)
    assert proportional(Statevector(prep.shukla_vedula(colors)).data, target)
    exact = prep.with_exact_rotations(prep.shukla_vedula(colors))
    assert proportional(Statevector(exact).data, target)
    if colors in (3, 5, 6, 10, 12, 20):
        assert "ry" not in exact.count_ops()
    amplified = Statevector(prep.amplitude_amplified(colors)).data.reshape(4, -1)
    assert np.allclose(amplified[1:], 0, atol=1e-9)
    assert proportional(amplified[0], target)


@pytest.mark.parametrize("n", range(1, 8))
def test_hamming_weight_phasing_applies_every_rotation(n):
    circuit = prep.hamming_weight_phasing(n, 0.37)
    assert circuit.num_qubits == n + prep.hamming_weight_ancillas(n)
    assert circuit.count_ops().get("rz", 0) == n.bit_length()
    unitary = Operator(circuit).data
    clean = list(range(1 << n))
    expected = np.array([[1]])
    for _ in range(n):
        expected = np.kron(rz(0.37), expected)
    assert proportional(unitary[np.ix_(clean, clean)], expected)
    # Nothing leaks into the ancillas.
    assert np.allclose(np.abs(unitary[np.ix_(clean, clean)]).sum(axis=0) ** 0, 1)


@pytest.mark.parametrize("colors", [3, 5, 6])
@pytest.mark.parametrize("method", prep.PREPARATIONS)
def test_search_preparations_agree(colors, method):
    problem = ColoringProblem((0, 1, 2), ((0, 1), (1, 2)), colors, {2: 1})
    bits = (colors - 1).bit_length()
    groups = [list(range(i * bits, (i + 1) * bits)) for i in range(3)]
    reference = Statevector(prep.search_preparation(problem, groups, "shukla_vedula"))
    circuit = prep.search_preparation(problem, groups, method)
    state = Statevector(circuit).data.reshape(-1, 1 << (3 * bits))
    assert np.allclose(state[1:], 0, atol=1e-9)
    assert proportional(state[0], reference.data)


def test_costs_count_exact_rotations_by_their_expectation():
    problem = ColoringProblem((0, 1), ((0, 1),), 5)
    groups = [[0, 1, 2], [3, 4, 5]]
    circuit = prep.search_preparation(problem, groups, "exact_rus")
    lowered = costs.clifford_t(circuit)
    metrics = costs.ft_metrics(lowered)
    expected = 2 * prep.EXACT_ROTATIONS[5].expected_t
    assert metrics["rotation_count"] == 0
    assert metrics["rus_count"] == 2
    assert math.isclose(metrics["rus_expected_t"], expected)
    assert costs.ft_counts(circuit)["rus_expected_t"] == pytest.approx(expected)
    assert proportional(Operator(lowered).data, Operator(circuit).data)


def test_rotation_synthesis_models():
    assert costs.rotation_t_count(1e-3) == 30
    assert costs.rotation_t_count(1e-3, "fallback") == math.ceil(
        1.03 * math.log2(1e3) + 5.75
    )
    assert costs.rotation_t_count(1e-9, "mixed_fallback") < costs.rotation_t_count(
        1e-9, "mixed_diagonal"
    )
    with pytest.raises(ValueError):
        costs.rotation_t_count(1e-3, "unknown")


@pytest.mark.parametrize("method", prep.PREPARATIONS)
def test_prepared_diffusion_reflects_about_the_same_state(method):
    from logique.benchmarks.preparations import (
        component_counts,
        prepared_components,
        search_total,
    )
    from logique.circuits.search import baseline_instance

    problem = ColoringProblem((0, 1), ((0, 1),), 3)
    instance = baseline_instance(problem, "simple", "R3")
    preparation, diffusion, ancillas, clean = prepared_components(
        problem, instance, method
    )
    reference = Operator(instance.diffusion).data
    width = instance.diffusion.num_qubits
    unitary = Operator(diffusion).data
    # Columns and rows with every non-data wire clean.
    data = instance.data
    keep = [
        sum(((index >> i) & 1) << q for i, q in enumerate(data))
        for index in range(1 << len(data))
    ]
    assert proportional(unitary[np.ix_(keep, keep)], reference[np.ix_(keep, keep)])
    assert diffusion.num_qubits >= width
    counts = component_counts(diffusion, "clean_tree", clean)
    total = search_total(counts, counts, 10, 2)
    assert total["t_total"] == pytest.approx(
        counts["t_count"] * 3
        + 20
        + total["rotations"] * total["t_per_rotation"]
        + 3 * counts["rus_expected_t"]
    )


def test_measurement_based_choices_are_priced_apart():
    from logique.benchmarks.preparations import pricing

    assert pricing("shukla_vedula", "ross_selinger") == "unitary"
    assert pricing("hamming_weight", "ross_selinger") == "unitary"
    assert pricing("shukla_vedula", "mixed_diagonal") == "mixed"
    assert pricing("shukla_vedula", "fallback") == "measurement-based"
    assert pricing("shukla_vedula", "mixed_fallback") == "measurement-based"
    assert pricing("exact_rus", "ross_selinger") == "measurement-based"

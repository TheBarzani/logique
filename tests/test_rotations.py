"""Small phase-sensitive regressions for bounded static-unitary synthesis."""

import json
import math

import pytest

np = pytest.importorskip("numpy")
pytest.importorskip("qiskit")

from qiskit import QuantumCircuit  # noqa: E402
from qiskit.circuit import Gate, Parameter  # noqa: E402
from qiskit.circuit.library import RXGate, RZGate, XGate  # noqa: E402
from qiskit.quantum_info import Operator  # noqa: E402

from logique.benchmarks import rotations  # noqa: E402
from logique.benchmarks.costs import CLIFFORD_T_BASIS, ft_metrics  # noqa: E402


def operator_error(actual, expected):
    """Tests form search matrices only at widths <= 4; phases are not aligned."""
    assert actual.num_qubits == expected.num_qubits <= 4
    return float(np.linalg.norm(Operator(actual).data - Operator(expected).data, 2))


def reference_search(a, oracle, s0, mapping, iterations):
    result = QuantumCircuit(oracle.num_qubits)
    result.compose(a, qubits=mapping, inplace=True)
    for _ in range(iterations):
        result.compose(oracle, inplace=True)
        result.compose(a.inverse(), qubits=mapping, inplace=True)
        result.compose(s0, qubits=mapping, inplace=True)
        result.compose(a, qubits=mapping, inplace=True)
    return result


@pytest.mark.parametrize("angle", [0, math.pi / 4, -math.pi / 2, 2 * math.pi])
def test_exact_rotations_preserve_scalar_phase(angle):
    result = rotations.approximate_rz(angle, 1e-12)
    assert result.metadata["method"] == "numerical_clifford_t_lowering"
    assert 0 < result.metadata["error_bound"] <= 1e-12
    assert result.metadata["recursion_degree"] is None
    assert result.metadata["attempts"] == []
    assert not result.circuit.count_ops().get("rz", 0)
    target = QuantumCircuit(1)
    target.rz(angle, 0)
    assert operator_error(result.circuit, target) <= result.metadata["error_bound"]


@pytest.mark.parametrize("angle", [0.731, -1.123])
def test_arbitrary_rotations_emit_measured_phase_sensitive_approximations(angle):
    result = rotations.approximate_rz(angle, 1e-4)
    metadata = result.metadata
    error = np.linalg.norm(Operator(result.circuit).data - RZGate(angle).to_matrix(), 2)
    assert error == pytest.approx(metadata["measured_error"], abs=1e-15)
    assert error < metadata["error_bound"] <= 1e-4
    assert metadata["method"] == "qiskit_solovay_kitaev"
    assert metadata["qiskit_version"] == "2.1.1"
    assert metadata["recursion_degree"] <= metadata["max_recursion"] == 5
    assert metadata["metrics"] == ft_metrics(result.circuit)
    assert metadata["metrics"]["t_count"] > 100
    assert set(result.circuit.count_ops()) <= set(CLIFFORD_T_BASIS)
    # Same settings produce the actual same construction, not just the same cost.
    repeat = rotations.approximate_rz(angle, 1e-4)
    assert repeat.circuit == result.circuit
    assert repeat.metadata == metadata
    # A missing scalar phase is visible to this test (Operator.equiv would hide it).
    wrong_phase = result.circuit.copy()
    wrong_phase.global_phase += 0.1
    assert (
        np.linalg.norm(Operator(wrong_phase).data - RZGate(angle).to_matrix(), 2) > 0.09
    )
    json.dumps(metadata)


def test_double_cover_sign_is_repaired_in_emitted_phase(monkeypatch):
    class SignedEngine:
        def run(self, target, recursion_degree):
            circuit = QuantumCircuit(1)
            circuit.global_phase = math.pi
            return circuit

    monkeypatch.setattr(rotations, "_synthesizer", lambda depth: SignedEngine())
    result = rotations.approximate_rz(0.01, 0.01)
    assert result.metadata["sign_correction"]
    assert result.metadata["measured_error"] < 0.006
    assert abs(float(result.circuit.global_phase)) < 1e-14


def test_component_lowering_and_budget_use_emitted_dependency_graph():
    original = QuantumCircuit(3)
    original.global_phase = 0.31
    original.h(0)
    original.rz(0.731, 0)
    original.ccx(0, 1, 2)
    original.rz(-1.123, 2)
    lowered = rotations.lower_component(original)
    assert operator_error(lowered, original) < 1e-13
    result = rotations.synthesize_component(original, error_budget=1e-3)
    metadata = result.metadata
    assert metadata["rotation_count"] == 2
    assert metadata["per_rotation_precision"] == pytest.approx(5e-4)
    assert [row["qubit"] for row in metadata["rotations"]] == [0, 2]
    assert operator_error(result.circuit, original) <= metadata["error_bound"] <= 1e-3
    assert metadata["metrics"] == ft_metrics(result.circuit)
    expected_t = 7 + sum(row["metrics"]["t_count"] for row in metadata["rotations"])
    assert metadata["metrics"]["t_count"] == expected_t
    assert metadata["metrics"]["rotation_count"] == 0


def test_near_clifford_rotation_is_not_silently_snapped():
    original = QuantumCircuit(1)
    original.rz(math.pi / 4 + 1e-10, 0)
    assert rotations.lower_component(original).count_ops() == {"rz": 1}
    # The degree-zero T approximation is measured and charged to the budget.
    result = rotations.synthesize_component(original, error_budget=1e-8)
    assert result.metadata["rotation_count"] == 1
    assert 1e-11 < result.metadata["error_bound"] < 1e-8


def test_complete_search_accounts_for_every_component_and_inverse_reuse(monkeypatch):
    a = QuantumCircuit(2)
    a.global_phase = 0.23
    a.h(0)
    a.rz(0.731, 1)
    a.cx(0, 1)
    oracle = QuantumCircuit(4)
    # A clean compute/phase/uncompute oracle; auxiliary wire 0 starts at zero.
    oracle.rz(-1.123, 3)
    oracle.cx(3, 0)
    oracle.z(0)
    oracle.cx(3, 0)
    oracle.rz(1.123, 3)
    s0 = QuantumCircuit(2)
    # The diagonal dressing commutes with S0 and cancels exactly in the input;
    # each emitted approximation still has to enter the compilation budget.
    s0.rz(0.731, 0)
    s0.x([0, 1])
    s0.cz(0, 1)
    s0.x([0, 1])
    s0.rz(-0.731, 0)
    mapping = [3, 1]
    calls = []
    original_approximation = rotations.approximate_rz

    def tracked_approximation(angle, precision, **kwargs):
        calls.append((angle, precision))
        return original_approximation(angle, precision, **kwargs)

    monkeypatch.setattr(rotations, "approximate_rz", tracked_approximation)
    result = rotations.compile_search(
        a, oracle, s0, data_qubits=mapping, iterations=2, error_budget=1e-2
    )
    metadata = result.metadata
    assert len(calls) == 5  # Each source rotation once; no separate synthesis of A†.
    assert metadata["occurrence_counts"] == {
        "preparation": 5,
        "oracle": 2,
        "zero_reflection": 2,
    }
    assert metadata["rotation_occurrences"] == 13
    assert metadata["per_rotation_precision"] == pytest.approx(1e-2 / 13)
    assert all(p == metadata["per_rotation_precision"] for _, p in calls)
    assert result.preparation_inverse == result.preparation.circuit.inverse()
    product = result.preparation.circuit.compose(result.preparation_inverse)
    assert operator_error(product, QuantumCircuit(2)) < 1e-10
    emitted_reference = reference_search(
        result.preparation.circuit,
        result.oracle.circuit,
        result.zero_reflection.circuit,
        mapping,
        2,
    )
    assert result.circuit == emitted_reference
    expected = reference_search(a, oracle, s0, mapping, 2)
    assert operator_error(result.circuit, expected) <= metadata["error_bound"] <= 1e-2
    weighted = sum(
        metadata["occurrence_counts"][name] * component["error_bound"]
        for name, component in metadata["components"].items()
    )
    assert metadata["error_bound"] == pytest.approx(weighted)
    metrics = metadata["metrics"]
    assert metrics == ft_metrics(result.circuit)
    assert metrics["t_count"] == sum(
        component["occurrences"] * component["metrics"]["t_count"]
        for component in metadata["components"].values()
    )
    # Wire 2 is auxiliary and unused by O; A/S0 must never accidentally touch it.
    assert all(
        result.circuit.qubits[2] not in item.qubits for item in result.circuit.data
    )
    assert metadata["inverse_reused"]
    json.dumps(metadata)


@pytest.mark.parametrize("budget", [1e-2, 1e-3, 1e-4])
def test_zero_iterations_does_not_synthesize_or_charge_unused_rotations(budget):
    a = QuantumCircuit(1)
    a.h(0)
    a.rz(0.731, 0)
    oracle = QuantumCircuit(3)
    oracle.rz(-1.123, 0)
    s0 = QuantumCircuit(1)
    s0.rz(-1.123, 0)
    result = rotations.compile_search(
        a, oracle, s0, data_qubits=[2], iterations=0, error_budget=budget
    )
    metadata = result.metadata
    assert metadata["rotation_occurrences"] == 1
    assert metadata["per_rotation_precision"] == pytest.approx(budget)
    for unused in (result.oracle, result.zero_reflection):
        assert unused.circuit is None
        assert unused.metadata["status"] == "unused"
        assert unused.metadata["rotation_count"] == 1
        assert unused.metadata["rotation_occurrences"] == 0
        assert unused.metadata["occurrences"] == 0
        assert unused.metadata["metrics"] is None
        assert unused.metadata["error_bound"] == 0
    reference = QuantumCircuit(3)
    reference.compose(a, qubits=[2], inplace=True)
    assert (
        operator_error(result.circuit, reference) <= metadata["error_bound"] <= budget
    )
    assert metadata["metrics"] == result.preparation.metadata["metrics"] | {"qubits": 3}


def test_primary_search_budget_weights_repeated_preparation():
    a = QuantumCircuit(1)
    a.h(0)
    a.rz(0.731, 0)
    oracle = QuantumCircuit(2)
    oracle.z(1)
    s0 = QuantumCircuit(1)
    s0.z(0)
    result = rotations.compile_search(a, oracle, s0, data_qubits=[1], iterations=2)
    metadata = result.metadata
    local = result.preparation.metadata
    assert metadata["rotation_occurrences"] == 5
    assert local["per_rotation_precision"] == pytest.approx(2e-4)
    assert 0 < local["error_bound"] < metadata["error_bound"] <= 1e-3
    assert metadata["error_bound"] == pytest.approx(5 * local["error_bound"])
    assert (
        operator_error(result.circuit, reference_search(a, oracle, s0, [1], 2))
        <= metadata["error_bound"]
    )


def test_unused_components_can_exceed_the_available_synthesis_precision():
    a = QuantumCircuit(1)
    a.h(0)
    oracle = QuantumCircuit(2)
    oracle.rz(0.731, 0)
    s0 = QuantumCircuit(1)
    s0.rz(0.731, 0)
    options = rotations.SynthesisOptions(max_recursion=0)
    result = rotations.compile_search(
        a, oracle, s0, data_qubits=[1], iterations=0, options=options
    )
    assert result.metadata["error_bound"] == 0
    assert result.metadata["method"] == "exact_clifford_t"
    with pytest.raises(rotations.PrecisionNotReachedError) as exc:
        rotations.compile_search(
            a, oracle, s0, data_qubits=[1], iterations=1, options=options
        )
    assert exc.value.metadata["component"] == "oracle"
    assert exc.value.metadata["occurrences"] == 1
    assert exc.value.metadata["rotation_occurrences"] == 2
    assert exc.value.metadata["lowered_instruction_index"] == 0


def test_clifford_search_charges_lowering_and_has_actual_parallel_t_depth():
    a = QuantumCircuit(2)
    a.h([0, 1])
    a.t([0, 1])
    oracle = QuantumCircuit(3)
    oracle.cz(2, 0)
    s0 = QuantumCircuit(2)
    s0.x([0, 1])
    s0.cz(0, 1)
    s0.x([0, 1])
    result = rotations.compile_search(a, oracle, s0, data_qubits=[2, 0], iterations=2)
    metadata = result.metadata
    assert metadata["method"] == "numerical_clifford_t_lowering"
    assert 0 < metadata["error_bound"] < 1e-12
    assert metadata["per_rotation_precision"] is None
    assert metadata["rotation_occurrences"] == 0
    assert result.preparation.metadata["metrics"]["t_count"] == 2
    assert result.preparation.metadata["metrics"]["t_depth"] == 1
    assert metadata["metrics"]["t_count"] == 10
    assert metadata["metrics"]["t_depth"] == 5
    assert (
        operator_error(result.circuit, reference_search(a, oracle, s0, [2, 0], 2))
        < 1e-13
    )


def test_bounded_precision_failure_reports_real_trials():
    with pytest.raises(
        rotations.PrecisionNotReachedError, match="best bounded error"
    ) as exc:
        rotations.approximate_rz(
            0.731, 1e-4, options=rotations.SynthesisOptions(max_recursion=0)
        )
    metadata = exc.value.metadata
    assert metadata["max_recursion"] == 0
    assert len(metadata["attempts"]) == 1
    trial = metadata["attempts"][0]
    assert trial["error_bound"] > 0.02
    assert trial["metrics"]["t_count"] == 1
    # Tight default bounds also fail explicitly, rather than return an estimate.
    with pytest.raises(rotations.PrecisionNotReachedError):
        rotations.approximate_rz(0.731, 1e-12)


@pytest.mark.parametrize("value", [0, -0.1, 1, math.inf, math.nan, True, "1e-3"])
def test_invalid_precision(value):
    with pytest.raises(ValueError, match="precision"):
        rotations.approximate_rz(0.731, value)
    with pytest.raises(ValueError, match="error_budget"):
        rotations.synthesize_component(QuantumCircuit(1), error_budget=value)


@pytest.mark.parametrize("angle", [math.inf, -math.inf, math.nan, True, "0.7"])
def test_invalid_angle(angle):
    with pytest.raises(ValueError, match="angle"):
        rotations.approximate_rz(angle, 1e-3)


@pytest.mark.parametrize(
    "kwargs",
    [
        {"max_recursion": -1},
        {"max_recursion": 7},
        {"max_recursion": True},
        {"basic_approximation_depth": 0},
        {"basic_approximation_depth": 13},
    ],
)
def test_invalid_work_limits(kwargs):
    with pytest.raises(ValueError):
        rotations.SynthesisOptions(**kwargs)


@pytest.mark.parametrize("kind", ["measure", "reset", "initialize", "parameter"])
def test_non_static_components_rejected(kind):
    circuit = QuantumCircuit(1)
    if kind == "measure":
        circuit.measure_all()
    elif kind == "reset":
        circuit.reset(0)
    elif kind == "initialize":
        circuit.initialize([1, 0], 0)
    else:
        circuit.rz(Parameter("theta"), 0)
    with pytest.raises(ValueError, match="static"):
        rotations.synthesize_component(circuit)


@pytest.mark.parametrize(
    "mapping", [[0, 0], [0], [0, 3], [-1, 0], [True, 0], [[], []], None]
)
def test_invalid_data_mapping(mapping):
    with pytest.raises(ValueError, match="data_qubits"):
        rotations.compile_search(
            QuantumCircuit(2),
            QuantumCircuit(3),
            QuantumCircuit(2),
            data_qubits=mapping,
            iterations=1,
        )


@pytest.mark.parametrize("iterations", [-1, 1.5, True])
def test_invalid_iteration_count(iterations):
    with pytest.raises(ValueError, match="iterations"):
        rotations.compile_search(
            QuantumCircuit(1),
            QuantumCircuit(2),
            QuantumCircuit(1),
            data_qubits=[1],
            iterations=iterations,
        )


def test_mcx_must_be_explicitly_decomposed():
    circuit = QuantumCircuit(4)
    circuit.mcx([0, 1, 2], 3)
    with pytest.raises(ValueError, match="decompose_mcx"):
        rotations.synthesize_component(circuit)


@pytest.mark.parametrize("angle", [1e6 * 2 * math.pi, 1e16])
def test_astra_large_angles_are_explicitly_unsupported(angle):
    original = QuantumCircuit(1)
    original.rz(angle, 0)
    with pytest.raises(ValueError, match="angle parameters"):
        rotations.synthesize_component(original, error_budget=1e-12)
    with pytest.raises(ValueError, match="angle parameters"):
        rotations.approximate_rz(angle, 1e-12)


@pytest.mark.parametrize("delta", [-1e-9, 1e-9, 3e-9])
def test_astra_near_pi_ccrx_cannot_return_false_zero(delta):
    original = QuantumCircuit(3)
    original.append(RXGate(math.pi + delta).control(2), range(3))
    with pytest.raises(rotations.PrecisionNotReachedError):
        rotations.synthesize_component(original, error_budget=1e-12)
    result = rotations.synthesize_component(original, error_budget=1e-8)
    assert 0 < result.metadata["error_bound"] <= 1e-8
    assert operator_error(result.circuit, original) <= result.metadata["error_bound"]


def test_astra_matrix_translation_is_charged_against_original_matrix():
    original = QuantumCircuit(1)
    original.unitary(RZGate(2 * math.pi + 1e-12).to_matrix(), [0])
    with pytest.raises(rotations.PrecisionNotReachedError, match="precision floor"):
        rotations.synthesize_component(original, error_budget=1e-14)
    with pytest.raises(rotations.PrecisionNotReachedError, match="preprocessing"):
        rotations.synthesize_component(original, error_budget=1e-12)
    result = rotations.synthesize_component(original, error_budget=1e-8)
    error = operator_error(result.circuit, original)
    assert 1e-13 < error <= result.metadata["lowering_error_bound"]
    assert error <= result.metadata["error_bound"] <= 1e-8
    assert result.metadata["status"] == "approximated"
    assert result.metadata["method"] == "numerical_clifford_t_lowering"
    assert result.metadata["rotation_count"] == 0
    json.dumps(result.metadata)


@pytest.mark.parametrize("iterations", [0, 2])
def test_astra_near_pi_search_rejects_tight_whole_search_budget(iterations):
    a = QuantumCircuit(3)
    a.append(RXGate(math.pi + 1e-9).control(2), range(3))
    oracle = QuantumCircuit(3)
    oracle.z(2)
    s0 = QuantumCircuit(3, global_phase=math.pi)
    s0.x(range(3))
    s0.h(2)
    s0.ccx(0, 1, 2)
    s0.h(2)
    s0.x(range(3))
    with pytest.raises(rotations.PrecisionNotReachedError):
        rotations.compile_search(
            a,
            oracle,
            s0,
            data_qubits=[0, 1, 2],
            iterations=iterations,
            error_budget=1e-12,
        )
    result = rotations.compile_search(
        a,
        oracle,
        s0,
        data_qubits=[0, 1, 2],
        iterations=iterations,
        error_budget=1e-7,
    )
    assert (
        operator_error(
            result.circuit, reference_search(a, oracle, s0, [0, 1, 2], iterations)
        )
        <= result.metadata["error_bound"]
        <= 1e-7
    )
    assert result.preparation_inverse == result.preparation.circuit.inverse()


@pytest.mark.parametrize("iterations", [0, 2])
def test_numerical_only_lowering_is_weighted_before_rotation_allocation(iterations):
    a = QuantumCircuit(1)
    a.unitary(RZGate(2 * math.pi + 1e-12).to_matrix(), [0])
    oracle = QuantumCircuit(1)
    oracle.z(0)
    s0 = QuantumCircuit(1)
    s0.z(0)
    result = rotations.compile_search(
        a, oracle, s0, data_qubits=[0], iterations=iterations, error_budget=1e-8
    )
    local = result.preparation.metadata
    assert local["rotation_count"] == 0
    assert local["lowering_error_bound"] > 1e-13
    assert local["weighted_error_bound"] == pytest.approx(
        (1 + 2 * iterations) * local["lowering_error_bound"], rel=1e-12, abs=0
    )
    assert result.metadata["error_bound"] >= local["weighted_error_bound"]
    assert (
        operator_error(result.circuit, reference_search(a, oracle, s0, [0], iterations))
        <= result.metadata["error_bound"]
        <= 1e-8
    )


def test_astra_spoofed_standard_gate_name_is_rejected():
    body = QuantumCircuit(1)
    body.rz(0.731, 0)
    gate = Gate("x", 1, [])
    gate.definition = body
    original = QuantumCircuit(1)
    original.append(gate, [0])
    with pytest.raises(ValueError, match="conflicting standard gate"):
        rotations.synthesize_component(original)


def test_modified_standard_gate_definition_is_rejected():
    gate = XGate().to_mutable()
    gate.definition = QuantumCircuit(1)
    gate.definition.rz(0.731, 0)
    original = QuantumCircuit(1)
    original.append(gate, [0])
    with pytest.raises(ValueError, match="conflicting definition"):
        rotations.synthesize_component(original)


def test_astra_nested_mcx_requires_explicit_policy():
    body = QuantumCircuit(4)
    body.mcx([0, 1, 2], 3)
    wrapped = QuantumCircuit(4)
    wrapped.append(body.to_gate(label="wrapped MCX"), range(4))
    twice = QuantumCircuit(4)
    twice.append(wrapped.to_gate(), range(4))
    with pytest.raises(ValueError, match="decompose_mcx"):
        rotations.synthesize_component(twice)


def test_recursive_custom_definitions_preserve_phase_and_charge_rotations():
    body = QuantumCircuit(1, global_phase=0.37)
    body.rx(0.731, 0)
    middle = QuantumCircuit(1, global_phase=0.13)
    middle.append(body.to_gate(), [0])
    original = QuantumCircuit(1, global_phase=0.21)
    original.append(middle.to_gate(), [0])
    result = rotations.synthesize_component(original, error_budget=1e-3)
    assert result.metadata["rotation_count"] > 0
    assert result.metadata["lowering_error_bound"] > 0
    assert operator_error(result.circuit, original) <= result.metadata["error_bound"]
    assert result.metadata["error_bound"] <= 1e-3
    assert set(result.circuit.count_ops()) <= set(CLIFFORD_T_BASIS)


@pytest.mark.parametrize("kind", ["opaque", "reset", "cycle", "wide_matrix"])
def test_unsupported_recursive_forms_are_rejected(kind):
    gate = Gate("custom", 1, [])
    circuit = QuantumCircuit(1)
    if kind == "wide_matrix":
        circuit = QuantumCircuit(2)
        circuit.unitary(np.eye(4), [0, 1])
    else:
        if kind == "reset":
            gate.definition = QuantumCircuit(1)
            gate.definition.reset(0)
        elif kind == "cycle":
            gate.definition = QuantumCircuit(1)
            gate.definition.append(gate, [0], copy=False)
        circuit.append(gate, [0], copy=False)
    with pytest.raises(ValueError):
        rotations.synthesize_component(circuit)


@pytest.mark.parametrize("precision", [1e-14, 1e-18])
def test_even_canonical_rotations_enforce_numerical_precision_floor(precision):
    with pytest.raises(rotations.PrecisionNotReachedError, match="precision floor"):
        rotations.approximate_rz(math.pi / 4, precision)


def test_standard_valid_color_preparation_remains_supported():
    from logique.circuits.grover import coloring_preparation
    from logique.coloring import ColoringEncoding, ColoringProblem

    encoding = ColoringEncoding(ColoringProblem(vertices=[0], edges=[], colors=3))
    original = coloring_preparation(encoding)
    assert original.num_qubits == 2
    result = rotations.synthesize_component(original, error_budget=1e-2)
    assert result.metadata["rotation_count"] > 0
    assert operator_error(result.circuit, original) <= result.metadata["error_bound"]
    assert result.metadata["error_bound"] <= 1e-2


@pytest.mark.parametrize("angle", [-math.pi, math.pi])
@pytest.mark.parametrize("state", [0, 1, 3])
def test_compiler_controlled_pi_gadgets_preserve_open_controls(angle, state):
    original = QuantumCircuit(3)
    original.append(RXGate(angle).control(2, ctrl_state=state), range(3))
    result = rotations.synthesize_component(original, error_budget=1e-10)
    assert result.metadata["rotation_count"] == 0
    assert result.metadata["metrics"]["t_count"] == 4
    assert operator_error(result.circuit, original) <= result.metadata["error_bound"]
    assert 0 < result.metadata["error_bound"] <= 1e-10


def test_lowering_is_subtracted_from_repeated_rotation_budget():
    a = QuantumCircuit(1)
    a.unitary(RZGate(2 * math.pi + 1e-12).to_matrix(), [0])
    oracle = QuantumCircuit(1)
    oracle.rz(math.pi / 4 + 1e-10, 0)
    s0 = QuantumCircuit(1)
    s0.z(0)
    result = rotations.compile_search(
        a, oracle, s0, data_qubits=[0], iterations=2, error_budget=1e-8
    )
    metadata = result.metadata
    assert metadata["rotation_occurrences"] == 2
    assert metadata["preprocessing_error_bound"] > 5e-12
    assert metadata["per_rotation_precision"] == pytest.approx(
        (
            math.nextafter(1e-8 / metadata["source_norm_product_bound"], 0.0)
            - metadata["unscaled_preprocessing_error_bound"]
        )
        * (1 - 1e-12)
        / 2,
        rel=1e-14,
        abs=0,
    )
    assert (
        operator_error(result.circuit, reference_search(a, oracle, s0, [0], 2))
        <= metadata["error_bound"]
        <= 1e-8
    )


def test_unused_nested_mcx_is_still_rejected():
    body = QuantumCircuit(4)
    body.mcx([0, 1, 2], 3)
    oracle = QuantumCircuit(4)
    oracle.append(body.to_gate(), range(4))
    with pytest.raises(ValueError, match="decompose_mcx"):
        rotations.compile_search(
            QuantumCircuit(1),
            oracle,
            QuantumCircuit(1),
            data_qubits=[0],
            iterations=0,
        )


def nested_matrix(matrix, depth):
    """Use ordinary Qiskit admission, then wrap without changing the input."""
    circuit = QuantumCircuit(1)
    circuit.unitary(matrix, [0])
    for _ in range(depth):
        outer = QuantumCircuit(1, global_phase=0.23)
        outer.append(circuit.to_gate(), [0])
        circuit = outer
    return circuit


@pytest.mark.parametrize("budget", [1e-3, 5.000005e-6])
@pytest.mark.parametrize("iterations", [0, 1, 2])
@pytest.mark.parametrize("delta", [-1e-6, -1e-14, 1e-14, 1e-6])
@pytest.mark.parametrize("depth", [0, 2])
@pytest.mark.parametrize("complex_matrix", [False, True])
def test_nonunitary_matrix_search_rejected(
    budget, iterations, delta, depth, complex_matrix
):
    # Includes the exact reviewed A=(1+1e-6)I, O=S0=Z reproducer at both budgets.
    unitary = (
        np.array([[1, 1j], [1j, 1]]) / math.sqrt(2) if complex_matrix else np.eye(2)
    )
    a = nested_matrix((1 + delta) * unitary, depth)
    oracle = QuantumCircuit(1)
    oracle.z(0)
    s0 = oracle.copy()
    with pytest.raises(ValueError, match="matrix unitarity defect"):
        rotations.synthesize_component(a, error_budget=budget)
    with pytest.raises(ValueError, match="matrix unitarity defect"):
        rotations.compile_search(
            a, oracle, s0, data_qubits=[0], iterations=iterations, error_budget=budget
        )


@pytest.mark.parametrize("component", ["oracle", "zero_reflection"])
def test_unused_nested_nonunitary_matrix_is_still_rejected(component):
    sources = {
        name: QuantumCircuit(1) for name in ("preparation", "oracle", "zero_reflection")
    }
    # Non-scalar complex distortion, with both expanding and contracting axes.
    matrix = np.diag([1 + 1e-6, 1 - 1e-6]) @ np.array([[0, 1j], [1j, 0]])
    sources[component] = nested_matrix(matrix, 3)
    with pytest.raises(ValueError, match="matrix unitarity defect"):
        rotations.compile_search(**sources, data_qubits=[0], iterations=0)


@pytest.mark.parametrize("delta", [-3e-15, 0.0, 3e-15])
@pytest.mark.parametrize("iterations", [0, 1, 2])
def test_roundoff_matrix_targets_keep_norm_growth_and_original_target(
    delta, iterations
):
    matrix = (1 + delta) * np.array([[1, 1j], [1j, 1]]) / math.sqrt(2)
    a = nested_matrix(matrix, 2)
    oracle = QuantumCircuit(3)
    oracle.z(2)
    s0 = QuantumCircuit(1)
    s0.z(0)
    result = rotations.compile_search(
        a, oracle, s0, data_qubits=[2], iterations=iterations, error_budget=1e-8
    )
    metadata = result.metadata
    assert 0 < metadata["matrix_unitarity_tolerance"] == 64 * np.finfo(float).eps
    assert result.preparation.metadata["source_norm_bound"] > 1
    factor = metadata["source_norm_product_bound"]
    assert factor >= result.preparation.metadata["source_norm_bound"] ** (
        1 + 2 * iterations
    )
    assert metadata["error_bound"] >= factor * metadata["unscaled_error_bound"]
    # Multiply ORIGINAL stored matrices and the numeric adjoint, independently
    # of circuit.inverse() and of the compiler's lowered/approximated target.
    embedded = QuantumCircuit(3)
    embedded.compose(a, qubits=[2], inplace=True)
    am = Operator(embedded).data
    om = Operator(oracle).data
    target = np.linalg.matrix_power(am @ om @ am.conj().T @ om, iterations) @ am
    actual_error = float(np.linalg.norm(Operator(result.circuit).data - target, 2))
    assert actual_error <= metadata["error_bound"] <= 1e-8
    assert result.preparation_inverse == result.preparation.circuit.inverse()
    json.dumps(metadata)


@pytest.mark.parametrize("depth", [0, 2])
def test_ordinary_complex_unitary_matrix_with_residual_rotations_remains_supported(
    depth,
):
    original = QuantumCircuit(1, global_phase=0.17)
    original.rx(0.731, 0)
    original.rz(-1.123, 0)
    original = nested_matrix(Operator(original).data, depth)
    result = rotations.synthesize_component(original, error_budget=1e-2)
    assert result.metadata["rotation_count"] > 0
    assert (
        operator_error(result.circuit, original)
        <= result.metadata["error_bound"]
        <= 1e-2
    )

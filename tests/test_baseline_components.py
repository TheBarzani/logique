"""Independent small baseline checks; every simulated circuit has <=12 qubits."""

# ruff: noqa: E402

import sys
from types import SimpleNamespace

import pytest

np = pytest.importorskip("numpy")
pytest.importorskip("qiskit")
pytest.importorskip("saha_belletti")

from qiskit import QuantumCircuit
from qiskit.quantum_info import Operator, Statevector

from logique.coloring import ColoringProblem, encode_coloring
from logique.synthesis import BaselineComponents, baseline_components
from logique.synthesis.saha_belletti import VARIANTS, comparison_circuit


def predicate(problem, domain_policy):
    """Use the classical graph model, never the package's constraint flags."""
    encoding = encode_coloring(problem)
    assignments = [encoding.decode(x) for x in range(1 << encoding.input_count)]
    return np.array(
        [
            (
                problem.is_valid(a)
                if domain_policy == "complete"
                else all(a[u] != a[v] for u, v in problem.edges)
            )
            for a in assignments
        ]
    )


def evolve(vector, circuit):
    assert circuit.num_qubits <= 12, "Keep this suite safe on the 8 GiB server"
    return Statevector(vector).evolve(circuit).data


def check_phase(problem, variant, domain_policy="complete"):
    components = baseline_components(problem, variant, domain_policy=domain_policy)
    width = components.circuit.num_qubits
    n = len(components.metadata["input_qubits"])
    rng = np.random.default_rng(731)
    data = rng.normal(size=1 << n) + 1j * rng.normal(size=1 << n)
    data /= np.linalg.norm(data)
    initial = np.zeros(1 << width, dtype=complex)
    initial[: len(data)] = data
    expected = initial.copy()
    expected[: len(data)] *= 1 - 2 * predicate(problem, domain_policy)
    phase = components.phase_oracle()
    np.testing.assert_allclose(evolve(initial, phase), expected, atol=1e-9)
    np.testing.assert_allclose(evolve(expected, phase), initial, atol=1e-9)

    # decompose alone restores the package initializer state, then the adapter
    # must undo the initializer as well to satisfy its all-zero contract.
    initialized = evolve(initial, components.initializer)
    computed = evolve(initialized, components.compute)
    restored = evolve(computed, components.uncompute)
    np.testing.assert_allclose(restored, initialized, atol=1e-9)
    np.testing.assert_allclose(
        evolve(restored, components.initializer.inverse()), initial, atol=1e-9
    )
    return components


@pytest.mark.parametrize("variant", VARIANTS)
@pytest.mark.parametrize(
    "problem",
    [
        ColoringProblem((-7, 20), ((-7, 20),), 3),
        # k=3's only unused code is symmetric under bit reversal. k=5 is not:
        # code 3 is valid and code 6 is invalid in the maintained LSB convention.
        ColoringProblem((42,), (), 5),
    ],
)
def test_exhaustive_clean_xor_and_coherent_phase(variant, problem):
    components = check_phase(problem, variant)
    marked = predicate(problem, "complete")
    width = components.circuit.num_qubits
    target = components.metadata["kickback_qubit"]
    # Both target initializations verify arbitrary-target XOR, not just a
    # clean-output computation that happens to work for target zero.
    for target_bit in (0, 1):
        for x, valid in enumerate(marked):
            source = x | (target_bit << target)
            destination = x | ((target_bit ^ int(valid)) << target)
            initial = np.zeros(1 << width, dtype=complex)
            initial[source] = 1
            expected = np.zeros_like(initial)
            expected[destination] = 1
            np.testing.assert_allclose(
                evolve(initial, components.oracle()), expected, atol=1e-9
            )


@pytest.mark.parametrize("variant", VARIANTS)
def test_small_uncompute_operator_and_entangled_target(variant):
    problem = ColoringProblem((3, 80), ((3, 80),), 2)
    components = baseline_components(problem, variant)
    block = components.compute.compose(components.uncompute)
    assert block.num_qubits <= 5
    np.testing.assert_allclose(
        Operator(block).data, np.eye(1 << block.num_qubits), atol=1e-9
    )
    # An asymmetric coherent input entangles the target with the data and
    # checks the relative phases between both target sectors.
    width = components.circuit.num_qubits
    target = components.metadata["kickback_qubit"]
    initial = np.zeros(1 << width, dtype=complex)
    initial[:4] = np.array([1, 2j, 3, -4j]) / np.sqrt(60)
    initial[(1 << target) : (1 << target) + 4] = np.array([4j, 3, -2j, 1]) / np.sqrt(60)
    expected = initial.copy()
    for x, valid in enumerate(predicate(problem, "complete")):
        if valid:
            expected[x], expected[x | (1 << target)] = (
                initial[x | (1 << target)],
                initial[x],
            )
    np.testing.assert_allclose(evolve(initial, components.circuit), expected, atol=1e-9)


@pytest.mark.parametrize("variant", VARIANTS)
@pytest.mark.parametrize("colors", (3, 5))
def test_domain_free_edges_use_full_binary_palette(variant, colors):
    problem = ColoringProblem((9, 100), ((9, 100),), colors)
    components = check_phase(problem, variant, "domain_free")
    md = components.metadata
    assert md["effective_colors"] == 1 << md["bits_per_color"]
    assert md["constraint_count"] == 1
    # Binary assignments using unused codes are deliberately admitted in R3.
    assert (
        predicate(problem, "domain_free").sum() > predicate(problem, "complete").sum()
    )


def test_minimal_single_constraint_keeps_initializer_off_target():
    problem = ColoringProblem((12,), (), 3)
    components = check_phase(problem, "minimal")
    md = components.metadata
    assert md["width_adjustment"] == 1
    assert md["initializer_one_qubits"] == [2, 3]
    assert md["workspace_qubits"] == [3]
    assert md["kickback_qubit"] == 4
    for target_bit in (0, 1):
        initial = np.zeros(32, dtype=complex)
        initial[(target_bit << 4) : (target_bit << 4) + 4] = 0.5
        expected = np.zeros_like(initial)
        for x in range(4):
            expected[x | ((target_bit ^ (x < 3)) << 4)] = 0.5
        np.testing.assert_allclose(
            evolve(initial, components.oracle()), expected, atol=1e-9
        )


@pytest.mark.parametrize("variant", ("minimal", "balanced"))
@pytest.mark.parametrize("colors", (9, 12, 17))
def test_larger_constraint_trees_within_simulation_bound(variant, colors):
    # Exercise recursive/tree boundaries through 15 domain constraints without
    # exceeding 12 qubits, using a single vertex and asymmetric color codes.
    check_phase(ColoringProblem((37,), (), colors), variant)


@pytest.mark.parametrize("variant", VARIANTS)
def test_isolated_vertices_and_wire_metadata(variant):
    problem = ColoringProblem((-2, 4, 90), ((-2, 4),), 3)
    components = check_phase(problem, variant)
    assert isinstance(components, BaselineComponents)
    md = components.metadata
    assert md["label_map"] == {-2: 0, 4: 1, 90: 2}
    assert md["input_mapping"] == {-2: [0, 1], 4: [2, 3], 90: [4, 5]}
    assert md["package_to_input_qubits"][:6] == [1, 0, 3, 2, 5, 4]
    roles = [
        md["input_qubits"],
        md["constraint_qubits"],
        md["workspace_qubits"],
        [md["kickback_qubit"]],
    ]
    assert sorted(q for role in roles for q in role) == list(
        range(components.circuit.num_qubits)
    )
    assert list(md["qubit_roles"].values()) == roles
    assert sum(md["qubit_counts"].values()) == components.circuit.num_qubits
    assert set(md["initializer_one_qubits"]) <= set(
        md["constraint_qubits"] + md["workspace_qubits"]
    )
    assert md["output_qubits"] == [md["kickback_qubit"]]
    assert md["dependency"]["compose"].endswith(f"{variant}_compose")
    assert md["dependency"]["version"]
    assert md["metric_level"] == "logical"
    assert md["validation"]["status"] == "not run"


@pytest.mark.parametrize("variant", VARIANTS)
@pytest.mark.parametrize("domain_policy", ("complete", "domain_free"))
@pytest.mark.parametrize(
    "problem",
    [
        ColoringProblem((), (), 3),
        ColoringProblem((11, 30), (), 4),
        ColoringProblem((11, 30), (), 3),
        ColoringProblem((11,), ((11, 11),), 3),
    ],
)
def test_empty_constraints_isolates_and_self_loops(variant, domain_policy, problem):
    check_phase(problem, variant, domain_policy)


@pytest.mark.parametrize("variant", ("simple", "minimal", "balanced"))
def test_unsatisfiable_triangle(variant):
    problem = ColoringProblem((2, 7, 20), ((2, 7), (2, 20), (7, 20)), 2)
    assert not predicate(problem, "complete").any()
    check_phase(problem, variant)


@pytest.mark.parametrize("variant", ("original", "minimal", "balanced"))
def test_asymmetric_complete_edge_predicate(variant):
    # Simple needs 14 qubits here. Its k=5 domain checks and edge comparator
    # are covered separately above; never simulate its larger combined circuit.
    check_phase(ColoringProblem((6, 19), ((6, 19),), 5), variant)


@pytest.mark.parametrize(
    "variant,edges,solutions",
    [
        ("original", ((2, 5), (5, 30)), 12),
        ("simple", ((2, 5), (5, 30)), 12),
        ("minimal", ((2, 5), (2, 30), (5, 30)), 6),
        ("balanced", ((2, 5), (2, 30), (5, 30)), 6),
    ],
)
@pytest.mark.parametrize("domain_policy", ("complete", "domain_free"))
@pytest.mark.parametrize("iterations", (0, 1, 2))
def test_matching_preparation_grover(
    variant, edges, solutions, domain_policy, iterations
):
    from logique.circuits.grover import coloring_preparation, grover_circuit

    problem = ColoringProblem((2, 5, 30), edges, 3)
    encoding = encode_coloring(problem)
    components = baseline_components(problem, variant, domain_policy=domain_policy)
    preparation = coloring_preparation(encoding)
    initial = Statevector.from_instruction(preparation).data
    expected = initial.copy()
    valid = predicate(problem, "complete")
    for _ in range(iterations):
        expected[valid] *= -1
        expected = 2 * initial * np.vdot(initial, expected) - expected
    circuit = grover_circuit(components, preparation=preparation, iterations=iterations)
    actual = evolve(np.eye(1, 1 << circuit.num_qubits, dtype=complex)[0], circuit)
    np.testing.assert_allclose(actual[: len(initial)], expected, atol=1e-9)
    np.testing.assert_allclose(actual[len(initial) :], 0, atol=1e-9)
    assert np.abs(actual[: len(initial)][valid]).dot(
        np.abs(actual[: len(initial)][valid])
    ) == pytest.approx(
        np.sin((2 * iterations + 1) * np.arcsin(np.sqrt(solutions / 27))) ** 2
    )
    invalid_codes = np.array([max(encoding.decode(x).values()) >= 3 for x in range(64)])
    np.testing.assert_allclose(actual[:64][invalid_codes], 0, atol=1e-9)


@pytest.mark.parametrize(
    "problem,kwargs,message",
    [
        (ColoringProblem((1,), (), 3, {1: 0}), {}, "precolored"),
        (ColoringProblem((1,), (), 1), {}, "at least two"),
        (ColoringProblem((1,), (), 2), {"variant": "unknown"}, "Unknown baseline"),
        (ColoringProblem((1,), (), 2), {"domain_policy": "unknown"}, "domain_policy"),
        (
            ColoringProblem((2, 8, 99), ((2, 8), (2, 99)), 3),
            {"variant": "original"},
            "multiple higher-index neighbors",
        ),
    ],
)
def test_unsupported_inputs_raise(problem, kwargs, message):
    with pytest.raises(ValueError, match=message):
        baseline_components(problem, **kwargs)


def test_historical_adapter_still_forwards_replay_options(monkeypatch):
    observed = []
    measured = QuantumCircuit(1, 1)
    measured.measure(0, 0)

    def generate(graph, colors, **kwargs):
        observed.append((list(graph.nodes), colors, kwargs))
        return measured

    # Avoid importing the dependency's heavy historical execution stack.
    monkeypatch.setitem(
        sys.modules, "saha_belletti.core", SimpleNamespace(generate_circuit=generate)
    )
    problem = ColoringProblem((4, 20), ((4, 20),), 3)
    assert (
        comparison_circuit(
            problem, "original", iterations=2, preserve_labels=True, measure=True
        )
        is measured
    )
    default = comparison_circuit(problem)
    assert default.num_clbits == 0
    assert observed == [
        ([4, 20], 3, {"oracle_type": "original", "grover_iterations": 2}),
        ([0, 1], 3, {"oracle_type": "balanced", "grover_iterations": 1}),
    ]

"""Compare every compiled assignment with an independent graph predicate."""

import pytest

np = pytest.importorskip("numpy")
pytest.importorskip("qiskit")
pytest.importorskip("tweedledum")
from logique import ColoringProblem, encode_coloring
from logique.synthesis import synthesize, METHODS
from logique.paths import native_executable
from logique.verification import validate, truth_outputs
from logique.verification.classical import input_assignments

pytestmark = pytest.mark.integration


@pytest.fixture(autouse=True)
def native():
    try:
        native_executable()
    except FileNotFoundError:
        pytest.skip("Native executable not configured")


@pytest.mark.parametrize("method", METHODS)
@pytest.mark.parametrize(
    "problem",
    [
        ColoringProblem((1, 2, 7), ((1, 2),), 2),
        ColoringProblem((1, 2), ((1, 2),), 3),
        ColoringProblem((1, 2), ((1, 2),), 4, {1: 0}),
        ColoringProblem((1,), (), 1),
        ColoringProblem((1, 2), ((1, 2),), 1),
        ColoringProblem((1,), ((1, 1),), 2),
        ColoringProblem((), (), 2),
    ],
)
def test_synthesis_matches_graph_predicate(problem, method):
    encoding = encode_coloring(problem)
    result = synthesize(encoding, method)
    assignments = input_assignments(encoding.input_count)
    actual = truth_outputs(result.metadata["source_network"], assignments)[0]
    expected = [
        problem.is_valid(encoding.decode(i)) for i in range(1 << encoding.input_count)
    ]
    np.testing.assert_array_equal(actual, expected)
    assert len(result.metadata["input_qubits"]) == encoding.input_count
    assert validate(result)["wrapped_restoration"]


@pytest.mark.parametrize("iterations", [0, 1, 2, 3])
def test_grover_matches_independent_amplitude_amplification(iterations):
    from qiskit.quantum_info import Statevector
    from logique.circuits.grover import coloring_preparation, grover_circuit

    encoding = encode_coloring(ColoringProblem((1, 2), ((1, 2),), 3, {1: 0}))
    result = synthesize(encoding)
    preparation = coloring_preparation(encoding)
    initial = Statevector.from_instruction(preparation).data
    expected = initial.copy()
    valid = np.array(
        [encoding.problem.is_valid(encoding.decode(i)) for i in range(len(initial))]
    )
    for _ in range(iterations):
        expected[valid] *= -1
        expected = 2 * initial * np.vdot(initial, expected) - expected
    circuit = grover_circuit(result, preparation=preparation, iterations=iterations)
    actual = Statevector.from_instruction(circuit).data
    np.testing.assert_allclose(actual[: len(initial)], expected, atol=1e-9)
    np.testing.assert_allclose(actual[len(initial) :], 0, atol=1e-9)


@pytest.mark.parametrize("method", METHODS)
@pytest.mark.parametrize(
    "problem",
    [
        ColoringProblem((1, 2, 3), ((1, 2), (2, 3), (1, 3)), 3),
        ColoringProblem((1, 2, 3), ((1, 2), (2, 3)), 5, {3: 1}),
        ColoringProblem((), (), 2),
    ],
)
def test_optimization_profiles_keep_the_predicate(problem, method):
    encoding = encode_coloring(problem, balanced=True)
    result = synthesize(encoding, method, mc_reduction=True)
    assignments = input_assignments(encoding.input_count)
    actual = truth_outputs(result.metadata["source_network"], assignments)[0]
    expected = [
        problem.is_valid(encoding.decode(i)) for i in range(1 << encoding.input_count)
    ]
    np.testing.assert_array_equal(actual, expected)
    assert result.metadata["parameters"]["mc_reduction"]
    assert result.metadata["source"] == "coloring predicate"
    assert validate(result)["wrapped_restoration"]


def test_mc_reduction_removes_and_gates_from_domain_checks():
    # Three colors leave one unused code per vertex, which the comparator rejects.
    encoding = encode_coloring(ColoringProblem((1, 2, 3), ((1, 2), (2, 3), (1, 3)), 3))
    plain = synthesize(encoding).summary()["AND"]
    reduced = synthesize(encoding, mc_reduction=True).summary()["AND"]
    assert reduced < plain

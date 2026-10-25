"""Independent structure-oracle checks, with explicit bounded coverage.

Dense operators use <=4 qubits; statevectors use <=5. Wider circuits are
exhaustively evaluated as monomial maps on their clean-workspace subspace.
Together with exact primitive semantics this establishes coherent action by
linearity, not a wide statevector or an MCX-decomposition validation claim.
"""

# ruff: noqa: E402

import itertools
from collections import Counter

import pytest

np = pytest.importorskip("numpy")
pytest.importorskip("qiskit")

from qiskit import QuantumCircuit
from qiskit.circuit.library import CCXGate, CXGate, MCXGate, XGate, ZGate
from qiskit.quantum_info import Operator, Statevector

from logique.circuits.grover import coloring_preparation
from logique.circuits.structure import (
    disjoint_edge_layers,
    edge_inequality,
    structure_oracle,
)
from logique.coloring import ColoringEncoding, ColoringProblem


def monomial(circuit, source):
    """Scalar gate interpreter, independent of repository record verification."""
    phase = np.exp(1j * float(circuit.global_phase))
    for item in circuit.data:
        gate = item.operation
        qs = [circuit.find_bit(q).index for q in item.qubits]
        if isinstance(gate, ZGate):
            phase *= (-1) ** ((source >> qs[0]) & 1)
        elif isinstance(gate, XGate):
            source ^= 1 << qs[0]
        else:
            assert isinstance(gate, (CXGate, CCXGate, MCXGate)), gate
            assert gate.ctrl_state == (1 << (len(qs) - 1)) - 1
            if all((source >> q) & 1 for q in qs[:-1]):
                source ^= 1 << qs[-1]
    return source, phase


def reference(problem, basis, policy):
    """Decode by integer arithmetic, without encoding.decode or circuit flags."""
    c = max(1, (problem.colors - 1).bit_length())
    values = {
        v: (basis >> (i * c)) & ((1 << c) - 1)
        for i, v in enumerate(sorted(problem.vertices))
    }
    if policy == "complete":
        return problem.is_valid(values)
    return all(values[u] != values[v] for u, v in problem.edges)


def check_exhaustive(problem, policy):
    result = structure_oracle(problem, domain_policy=policy)
    md = result.metadata
    n = len(md["input_qubits"])
    assert n <= 9, "Bound exhaustive monomial enumeration to 512 inputs"
    phase = result.phase_oracle()
    target = md["output_qubits"][0]
    marked = 0
    c = md["bits_per_color"]
    for basis in range(1 << n):
        valid = reference(problem, basis, policy)
        marked += valid
        # Inspect the compute boundary: data preserved, scratch zero, every
        # edge/domain flag independently correct before its later uncompute.
        computed, scalar = monomial(result.compute, basis)
        assert computed & ((1 << n) - 1) == basis
        assert scalar == 1
        assert all(not (computed >> q) & 1 for q in md["workspace_qubits"])
        values = [(basis >> (i * c)) & ((1 << c) - 1) for i in range(n // c)]
        colors = dict(zip(problem.vertices, values))
        flags = [colors[u] != colors[v] for u, v in problem.edges]
        if md["domain_constraint_qubits"]:
            flags += [value < problem.colors for value in values]
        assert [bool((computed >> q) & 1) for q in md["constraint_qubits"]] == flags
        assert not (computed >> target) & 1
        for initial_target in (0, 1):
            source = basis | (initial_target << target)
            final, scalar = monomial(result.circuit, source)
            assert final == basis | ((initial_target ^ valid) << target)
            assert scalar == 1
        final, scalar = monomial(phase, basis)
        assert final == basis  # Every flag, scratch and target is restored.
        assert scalar == (-1 if valid else 1)
    return result, marked


@pytest.mark.parametrize("controls", range(4))
def test_interpreter_matches_small_exact_primitive_operators(controls):
    circuit = QuantumCircuit(controls + 1)
    if controls:
        circuit.mcx(list(range(controls)), controls)
    else:
        circuit.x(0)
    circuit.z(controls)
    assert circuit.num_qubits <= 4
    matrix = Operator(circuit).data
    for source in range(1 << circuit.num_qubits):
        destination, scalar = monomial(circuit, source)
        expected = np.zeros(1 << circuit.num_qubits, dtype=complex)
        expected[destination] = scalar
        np.testing.assert_allclose(matrix[:, source], expected, atol=1e-14)


@pytest.mark.parametrize("c", (1, 2, 3, 4))
def test_comparator_exhaustive_clean_subspace_and_arbitrary_target(c):
    # Up to 12 logical wires, but only integer monomial evaluation; no arrays
    # of size 2**width. This exercises prefix AND length 0,1,2,3.
    circuit = edge_inequality(c)
    assert circuit.num_qubits == 3 * c
    for left, right, target in itertools.product(range(1 << c), range(1 << c), (0, 1)):
        source = left | (right << c) | (target << (2 * c))
        final, phase = monomial(circuit, source)
        expected = left | (right << c) | ((target ^ (left != right)) << (2 * c))
        assert final == expected
        assert phase == 1


PROBLEMS = [
    ColoringProblem((-7, 20), ((-7, 20),), 3),
    ColoringProblem((19, -6), ((19, -6),), 5),
    ColoringProblem((90, -2, 4), ((-2, 4),), 3),
    ColoringProblem((90, -2, 4), ((-2, 4),), 5),
    ColoringProblem((2, 7, 20), ((2, 7), (7, 20)), 3),
    ColoringProblem((2, 7, 20), ((2, 7), (2, 20), (7, 20)), 5),
    ColoringProblem((), (), 3),
    ColoringProblem((11, 30), (), 4),
    ColoringProblem((11, 30), (), 3),
    ColoringProblem((11, 30), (), 5),
    ColoringProblem((11,), ((11, 11),), 3),
    ColoringProblem((11,), ((11, 11),), 5),
    ColoringProblem((1, 2, 3, 4), tuple(itertools.combinations(range(1, 5), 2)), 3),
    ColoringProblem((2, 7, 20), ((2, 7), (2, 20), (7, 20)), 2),
    ColoringProblem((8,), (), 1),
    ColoringProblem((8, 70), ((8, 70),), 1),
]


@pytest.mark.parametrize("problem", PROBLEMS)
@pytest.mark.parametrize("policy", ("complete", "domain_free"))
def test_exhaustive_monomial_predicate_phase_and_restoration(problem, policy):
    result, marked = check_exhaustive(problem, policy)
    if any(u == v for u, v in problem.edges):
        assert marked == 0
    if policy == "complete" and problem == PROBLEMS[12]:
        assert marked == 0  # K4 has no 3-coloring, independently counted.
    if problem == PROBLEMS[13]:
        assert marked == 0  # Odd cycle with two binary colors.
    md = result.metadata
    roles = md["qubit_roles"]
    assert sorted(q for qs in roles.values() for q in qs) == list(
        range(result.circuit.num_qubits)
    )
    assert sum(md["qubit_counts"].values()) == result.circuit.num_qubits
    assert md["sequential_clean_ancillas"] == (
        len(md["constraint_qubits"]) + len(md["workspace_qubits"]) + 1
    )
    assert md["validation"] == {"status": "not run"}
    assert result.oracle() == result.circuit


@pytest.mark.parametrize(
    "problem", [PROBLEMS[0], PROBLEMS[1], PROBLEMS[2], PROBLEMS[3]]
)
def test_explicit_lsb_mapping_and_domain_contract(problem):
    complete, good = check_exhaustive(problem, "complete")
    edge_only, binary = check_exhaustive(problem, "domain_free")
    assert binary > good > 0
    encoding = ColoringEncoding(problem)
    assert complete.metadata["input_mapping"] == {
        v: list(qs) for v, qs in encoding.input_mapping.items()
    }
    assert edge_only.metadata["input_mapping"] == complete.metadata["input_mapping"]
    if problem.colors == 5:
        # Code 3 (011) is valid; code 6 (110) is invalid. A bit reversal would
        # swap these classifications. Make a second vertex a distinct color.
        assert reference(problem, 3, "complete")
        assert not reference(problem, 6, "complete")
        assert reference(problem, 6, "domain_free")


@pytest.mark.parametrize("colors", range(1, 10))
def test_domain_prefix_comparator_all_codes(colors):
    # Up to four data bits; verification is monomial even when total width >5.
    problem = ColoringProblem((42,), (), colors)
    _, count = check_exhaustive(problem, "complete")
    assert count == colors


@pytest.mark.parametrize(
    "problem", [ColoringProblem((3, 80), ((3, 80),), 2), ColoringProblem((42,), (), 5)]
)
def test_bounded_statevector_coherence_with_entangled_target(problem):
    result = structure_oracle(problem)
    width = result.circuit.num_qubits
    assert width <= 5
    n = len(result.metadata["input_qubits"])
    target = result.metadata["output_qubits"][0]
    rng = np.random.default_rng(731)
    amplitudes = rng.normal(size=(2, 1 << n)) + 1j * rng.normal(size=(2, 1 << n))
    amplitudes /= np.linalg.norm(amplitudes)
    source = np.zeros(1 << width, dtype=complex)
    expected = np.zeros_like(source)
    for t, x in itertools.product((0, 1), range(1 << n)):
        source[x | (t << target)] = amplitudes[t, x]
        expected[x | ((t ^ reference(problem, x, "complete")) << target)] = amplitudes[
            t, x
        ]
    np.testing.assert_allclose(
        Statevector(source).evolve(result.oracle()).data, expected, atol=1e-14
    )
    # A nonuniform complex data superposition checks phase and zero leakage to
    # all ancillas, with a separate target-zero initialization.
    source[:] = 0
    source[: 1 << n] = amplitudes[0] / np.linalg.norm(amplitudes[0])
    expected = source.copy()
    for x in range(1 << n):
        expected[x] *= (-1) ** reference(problem, x, "complete")
    np.testing.assert_allclose(
        Statevector(source).evolve(result.phase_oracle()).data, expected, atol=1e-14
    )


@pytest.mark.parametrize("colors", (3, 5))
def test_bounded_valid_preparation_restricts_edge_only_equivalence(colors):
    problem = ColoringProblem((-8,), (), colors)
    encoding = ColoringEncoding(problem)
    preparation = coloring_preparation(encoding)
    assert preparation.num_qubits <= 3
    prepared = Statevector.from_instruction(preparation).data
    np.testing.assert_allclose(prepared[:colors], 1 / np.sqrt(colors), atol=1e-14)
    np.testing.assert_allclose(prepared[colors:], 0, atol=1e-14)
    results = []
    for policy in ("complete", "domain_free"):
        result = structure_oracle(problem, domain_policy=policy)
        assert result.circuit.num_qubits <= 5
        source = np.zeros(1 << result.circuit.num_qubits, dtype=complex)
        source[: len(prepared)] = prepared
        final = Statevector(source).evolve(result.phase_oracle()).data
        np.testing.assert_allclose(final, -source, atol=1e-14)
        results.append(final[: len(prepared)])
    np.testing.assert_allclose(*results, atol=1e-14)


@pytest.mark.parametrize(
    "edges",
    [(), ((1, 1),), ((1, 2), (3, 4)), tuple(itertools.combinations(range(1, 6), 2))],
)
def test_schedule_conflicts_coverage_determinism_and_separate_width(edges):
    problem = ColoringProblem(tuple(range(1, 6)), edges, 5)
    layers = disjoint_edge_layers(problem)
    assert Counter(edge for layer in layers for edge in layer) == Counter(problem.edges)
    assert layers == disjoint_edge_layers(
        ColoringProblem(problem.vertices, edges[::-1], 5)
    )
    for layer in layers:
        for a, b in itertools.combinations(layer, 2):
            assert set(a).isdisjoint(b)
    md = structure_oracle(problem).metadata
    active = max((sum(u != v for u, v in layer) for layer in layers), default=0)
    assert md["sequential_comparator_scratch"] == (2 if active else 0)
    assert md["parallel_comparator_scratch"] == 2 * active
    assert md["parallel_max_active_comparators"] == active
    assert md["parallel_clean_ancillas_requirement"] == (
        len(md["constraint_qubits"]) + 2 * active + 1
    )
    assert md["parallel_logical_width_requirement"] == (
        md["num_qubits"] - md["sequential_comparator_scratch"] + 2 * active
    )
    assert md["parallel_schedule_only"] is True
    if edges == ((1, 2), (3, 4)):
        assert active == 2
        assert md["parallel_comparator_scratch"] > md["sequential_comparator_scratch"]


@pytest.mark.parametrize("c", (0, -1, True, 2.5))
def test_invalid_comparator_width(c):
    with pytest.raises(ValueError, match="positive integer"):
        edge_inequality(c)


def test_reject_unsupported_contracts():
    with pytest.raises(ValueError, match="precolored"):
        structure_oracle(ColoringProblem((1,), (), 3, {1: 0}))
    with pytest.raises(ValueError, match="domain_policy"):
        structure_oracle(ColoringProblem((1,), (), 3), domain_policy="edge-ish")

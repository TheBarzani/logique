"""Exact enumeration and independent <=2-qubit Kraus checks, no simulators."""

import ast
import cmath
import itertools
import math
from fractions import Fraction as F
from pathlib import Path

import pytest

from logique.benchmarks import rus_accounting as rus


def test_unlimited_geometric_moments():
    m = rus.retry_moments()
    assert m.expected_attempts == F(4, 3)
    assert m.variance_attempts == F(4, 9)
    assert m.expected_trial_t == F(8, 3)
    assert m.variance_trial_t == F(16, 9)
    assert m.expected_attempts_given_success == m.expected_attempts
    assert m.variance_attempts_given_success == m.variance_attempts
    assert m.success_probability == 1
    assert m.failure_probability == 0
    one = rus.analytical_ledger(1, 0)
    assert one.unbounded_expected_total_t == F(14, 3)
    assert one.unbounded_variance_vertex_t == F(16, 9)
    assert one.capped_vertex_t_upper_bound is None
    assert one.stop_expected_total_t == one.success_expected_total_t == F(14, 3)


@pytest.mark.parametrize("cap", range(9))
def test_capped_moments_against_exact_distribution(cap):
    # Independently enumerate first-success events and the all-fail event.
    events = [(r, F(3, 4) * F(1, 4) ** (r - 1)) for r in range(1, cap + 1)]
    tail = F(1, 4) ** cap
    unconditional = events + [(cap, tail)]
    mean = sum((r * p for r, p in unconditional), F(0))
    var = sum(((r - mean) ** 2 * p for r, p in unconditional), F(0))
    m = rus.retry_moments(cap)
    assert sum((p for _, p in unconditional), F(0)) == 1
    assert m.expected_attempts == mean
    assert m.variance_attempts == var
    assert m.expected_trial_t == 2 * mean
    assert m.variance_trial_t == 4 * var
    assert m.failure_probability == tail
    assert m.success_probability == 1 - tail
    assert m.expected_attempts == sum((F(1, 4) ** r for r in range(cap)), F(0))
    if cap:
        conditional_mean = sum((r * p for r, p in events), F(0)) / (1 - tail)
        conditional_var = sum(
            ((r - conditional_mean) ** 2 * p for r, p in events), F(0)
        ) / (1 - tail)
        assert m.expected_attempts_given_success == conditional_mean
        assert m.variance_attempts_given_success == conditional_var
    else:
        assert m.expected_attempts_given_success is None
        assert m.variance_attempts_given_success is None


@pytest.mark.parametrize("n,j", [(0, 0), (0, 3), (1, 0), (2, 0), (2, 3), (7, 2)])
@pytest.mark.parametrize("cap", [None, 0, 1, 4])
def test_invocations_and_program_failure(n, j, cap):
    ledger = rus.analytical_ledger(n, j, cap=cap, oracle_t=7, zero_reflection_t=11)
    loops = n * (1 + 2 * j)
    assert ledger.forward_vertex_invocations == n * (1 + j)
    assert ledger.inverse_vertex_invocations == n * j
    assert ledger.unitary_invocations == loops
    assert ledger.oracle_invocations == ledger.zero_reflection_invocations == j
    assert ledger.unbounded_expected_attempts == loops * F(4, 3)
    assert ledger.unbounded_variance_attempts == loops * F(4, 9)
    assert ledger.unbounded_expected_vertex_t == loops * F(14, 3)
    assert ledger.unbounded_variance_vertex_t == loops * F(16, 9)
    assert ledger.unbounded_expected_total_t == loops * F(14, 3) + 18 * j
    tail = F(0) if cap is None else F(1, 4) ** cap
    assert ledger.program_failure_probability == 1 - (1 - tail) ** loops
    assert ledger.program_failure_union_bound == min(1, loops * tail)
    assert ledger.program_failure_probability <= ledger.program_failure_union_bound
    if cap is not None:
        assert ledger.capped_attempts_upper_bound == loops * cap
        assert ledger.capped_vertex_t_upper_bound == loops * (2 * cap + 2)
    if not loops:
        assert ledger.program_failure_probability == 0
        assert ledger.stop_expected_vertex_t == ledger.success_expected_vertex_t == 0
        assert ledger.success_variance_vertex_t == 0
        assert ledger.stop_expected_total_t == ledger.success_expected_total_t == 18 * j
    elif not cap and cap is not None:
        assert ledger.program_failure_probability == 1
        assert ledger.stop_expected_total_t == 0
        assert ledger.success_expected_total_t is None


def _enumerate_program(n, j, cap):
    # Branch over first success (1..cap) or exhaustion, walking the actual
    # serial schedule. Inverse extensions are charged BEFORE the trial.
    schedule = ["forward"] * n
    for _ in range(j):
        schedule += ["O"] + ["inverse"] * n + ["S0"] + ["forward"] * n
    results = []

    def visit(index, probability, attempts, vertex_t, external_t):
        if index == len(schedule):
            results.append((True, probability, attempts, vertex_t, external_t))
            return
        op = schedule[index]
        if op in ("O", "S0"):
            visit(
                index + 1,
                probability,
                attempts,
                vertex_t,
                external_t + (7 if op == "O" else 11),
            )
            return
        before = 2 if op == "inverse" else 0
        after = 2 if op == "forward" else 0
        for r in range(1, cap + 1):
            visit(
                index + 1,
                probability * F(3, 4) * F(1, 4) ** (r - 1),
                attempts + r,
                vertex_t + before + 2 * r + after,
                external_t,
            )
        results.append(
            (
                False,
                probability * F(1, 4) ** cap,
                attempts + cap,
                vertex_t + before + 2 * cap,
                external_t,
            )
        )

    visit(0, F(1), 0, 0, 0)
    return results


@pytest.mark.parametrize("n,j,cap", itertools.product(range(3), range(2), range(3)))
def test_stop_costs_and_success_conditioning_by_enumeration(n, j, cap):
    events = _enumerate_program(n, j, cap)
    ledger = rus.analytical_ledger(n, j, cap=cap, oracle_t=7, zero_reflection_t=11)
    assert sum((p for _, p, *_ in events), F(0)) == 1
    assert ledger.stop_expected_attempts == sum(
        (p * a for _, p, a, _, _ in events), F(0)
    )
    assert ledger.stop_expected_vertex_t == sum(
        (p * t for _, p, _, t, _ in events), F(0)
    )
    assert ledger.stop_expected_total_t == sum(
        (p * (t + e) for _, p, _, t, e in events), F(0)
    )
    good = [event for event in events if event[0]]
    success = sum((event[1] for event in good), F(0))
    assert ledger.program_failure_probability == 1 - success
    if success:
        mean = sum((p * a for _, p, a, _, _ in good), F(0)) / success
        variance = sum((p * (a - mean) ** 2 for _, p, a, _, _ in good), F(0)) / success
        assert ledger.success_expected_attempts == mean
        assert ledger.success_variance_attempts == variance
        assert (
            ledger.success_expected_vertex_t
            == sum((p * t for _, p, _, t, _ in good), F(0)) / success
        )
        assert ledger.success_variance_vertex_t == 4 * variance
        assert (
            ledger.success_expected_total_t
            == sum((p * (t + e) for _, p, _, t, e in good), F(0)) / success
        )


def test_external_counts_unknown_and_explicit_workspace_assumptions():
    assert rus.analytical_ledger(2, 1).unbounded_expected_total_t is None
    assert rus.analytical_ledger(2, 1, oracle_t=0).stop_expected_total_t is None
    assert rus.analytical_ledger(2, 0).unbounded_expected_total_t == F(28, 3)
    assert rus.analytical_ledger(2, 1, cap=0).stop_expected_total_t == 0
    fractional = rus.analytical_ledger(
        1, 2, oracle_t=F(7, 2), zero_reflection_t=F(1, 3)
    )
    assert fractional.unbounded_expected_total_t == F(14, 3) * 5 + F(23, 3)
    shared = rus.analytical_ledger(4, 2)
    parallel = rus.analytical_ledger(4, 2, retry_ancillas="parallel")
    assert shared.retry_ancillas == 1
    assert parallel.retry_ancillas == 4
    assert shared.data_qubits == parallel.data_qubits == 8
    assert shared.stop_expected_attempts == parallel.stop_expected_attempts
    assert rus.analytical_ledger(0, 0).retry_ancillas == 0
    assert rus.analytical_ledger(0, 1, retry_ancillas="parallel").retry_ancillas == 0
    assert set(shared.unpriced) == {
        "measurement",
        "reset/repreparation",
        "classical feed-forward",
        "Clifford gates",
        "runtime",
        "physical QEC",
    }


@pytest.mark.parametrize("name", ["n", "j", "cap", "k"])
@pytest.mark.parametrize("value", [-1, True, 1.0, F(1), "1", None])
def test_invalid_integer_inputs(name, value):
    if name == "cap" and value is None:
        return  # None explicitly denotes unbounded retries.
    args = {"n": 1, "j": 1, name: value}
    with pytest.raises(ValueError, match=name):
        rus.analytical_ledger(**args)


@pytest.mark.parametrize("value", [-1, False, 0.5, float("nan"), float("inf"), "0"])
@pytest.mark.parametrize("name", ["oracle_t", "zero_reflection_t"])
def test_invalid_external_costs(name, value):
    with pytest.raises(ValueError, match=name):
        rus.analytical_ledger(0, 0, **{name: value})


@pytest.mark.parametrize("k", [0, 1, 2, 4, 5])
def test_other_color_counts_are_explicitly_unsupported(k):
    with pytest.raises(NotImplementedError, match="k=3"):
        rus.analytical_ledger(1, 0, k=k)


def test_unsupported_models_and_optional_dependency_boundary():
    with pytest.raises(ValueError, match="retry_ancillas"):
        rus.analytical_ledger(1, 0, retry_ancillas="dirty")
    for unsupported in (
        "quantum_controlled",
        "state_dependent_success",
        "graph",
        "optimal_j",
    ):
        with pytest.raises(TypeError):
            rus.analytical_ledger(1, 0, **{unsupported: True})
    assert Path(rus.__file__).resolve() == (
        Path(__file__).resolve().parents[1] / "src/logique/benchmarks/rus_accounting.py"
    )
    tree = ast.parse(Path(rus.__file__).read_text())
    imports = {
        node.module for node in ast.walk(tree) if isinstance(node, ast.ImportFrom)
    }
    assert imports == {"dataclasses", "fractions", "typing"}
    assert not any(isinstance(node, ast.Import) for node in ast.walk(tree))


# Independent tiny matrix algebra. No Qiskit, NumPy, maintained gates, or RUS
# runtime is used. Dense matrices never exceed 4x4; reference vectors have 8
# amplitudes at most. All comparisons retain complex branch phases.
def _mm(a, b):
    return [[sum(x * y for x, y in zip(row, col)) for col in zip(*b)] for row in a]


def _dagger(a):
    return [[complex(x).conjugate() for x in col] for col in zip(*a)]


def _scale(c, a):
    return [[c * x for x in row] for row in a]


def _kron(a, b):
    return [[x * y for x in row_a for y in row_b] for row_a in a for row_b in b]


def _close(a, b):
    assert len(a) == len(b)
    assert all(len(x) == len(y) for x, y in zip(a, b))
    assert max(abs(x - y) for r, s in zip(a, b) for x, y in zip(r, s)) < 3e-14


IDENTITY = [[1, 0], [0, 1]]
X = [[0, 1], [1, 0]]
Z = [[1, 0], [0, -1]]
H = _scale(1 / math.sqrt(2), [[1, 1], [1, -1]])
T = [[1, 0], [0, cmath.exp(1j * math.pi / 4)]]
U = _scale(1 / math.sqrt(3), [[1, 1j * math.sqrt(2)], [1j * math.sqrt(2), 1]])
ALPHA = cmath.exp(-1j * math.pi / 4) * math.sqrt(3) / 2
BETA = cmath.exp(1j * math.pi / 4) / 2


def _trial_kraus():
    # Basis |h a>, ancilla a is the low bit. CX control a, target h.
    cx = [
        [int(row == (col ^ (2 if col & 1 else 0))) for col in range(4)]
        for row in range(4)
    ]
    trial = _kron(IDENTITY, IDENTITY)
    for gate in (
        _kron(IDENTITY, H),
        _kron(IDENTITY, T),
        cx,
        _kron(IDENTITY, H),
        cx,
        _kron(IDENTITY, T),
        _kron(IDENTITY, H),
    ):
        trial = _mm(gate, trial)
    _close(_mm(_dagger(trial), trial), _kron(IDENTITY, IDENTITY))
    return tuple(
        [[trial[2 * h + b][2 * g] for g in range(2)] for h in range(2)]
        for b in range(2)
    )


def _apply_with_reference(matrix, vector):
    # Data-major tensor order, one untouched reference bit; no 8x8 operator.
    return [
        sum(matrix[row][col] * vector[2 * col + ref] for col in range(len(matrix)))
        for row in range(len(matrix))
        for ref in range(2)
    ]


def test_trial_kraus_completeness_and_arbitrary_input_actions():
    k0, k1 = _trial_kraus()
    _close(k0, _scale(ALPHA, U))
    _close(k1, _scale(BETA, IDENTITY))
    _close(_mm(_dagger(k0), k0), _scale(0.75, IDENTITY))
    _close(_mm(_dagger(k1), k1), _scale(0.25, IDENTITY))
    # Matrix identities prove all inputs. Complex asymmetric and entangled
    # inputs additionally detect state-only verification or phase fitting.
    for raw in ([1, 0, 0, 0], [1, 0, 0, 1j], [1, 2j, 3 - 1j, -2]):
        norm = math.sqrt(sum(abs(x) ** 2 for x in raw))
        psi = [x / norm for x in raw]
        for kraus, target, phase, probability in (
            (k0, U, ALPHA, 0.75),
            (k1, IDENTITY, BETA, 0.25),
        ):
            branch = _apply_with_reference(kraus, psi)
            expected = [phase * x for x in _apply_with_reference(target, psi)]
            assert branch == pytest.approx(expected, abs=2e-15)
            assert sum(abs(x) ** 2 for x in branch) == pytest.approx(
                probability, abs=2e-15
            )


def _vertex_parts():
    ch = [[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, *H[0]], [0, 0, *H[1]]]
    sdg = _kron([[1, 0], [0, -1j]], IDENTITY)
    extension = _mm(_kron(X, IDENTITY), _mm(ch, sdg))
    vertex = _mm(extension, _kron(U, IDENTITY))
    return ch, extension, vertex


def test_two_t_controlled_h_and_vertex_bit_ordering():
    ch, _, vertex = _vertex_parts()
    c, s = math.cos(math.pi / 8), math.sin(math.pi / 8)
    ry = [[c, -s], [s, c]]
    cz = [[int(i == j) * (-1 if i == 3 else 1) for j in range(4)] for i in range(4)]
    _close(_mm(_kron(IDENTITY, ry), _mm(cz, _kron(IDENTITY, _dagger(ry)))), ch)
    # Ry(pi/4)=Rx(-pi/2) Rz(pi/4) Rx(pi/2); Rz differs from T
    # by exp(-i*pi/8), whose inverse partner cancels in CH.
    rx = _scale(1 / math.sqrt(2), [[1, 1j], [1j, 1]])
    _close(ry, _scale(cmath.exp(-1j * math.pi / 8), _mm(rx, _mm(T, _dagger(rx)))))
    assert [row[0] for row in vertex] == pytest.approx(
        [1 / math.sqrt(3)] * 3 + [0], abs=2e-15
    )
    # |h l> columns other than zero distinguish the high/low bit assignment.
    expected = _scale(
        1 / math.sqrt(3),
        [
            [1, 1, -1j / math.sqrt(2), -1j / math.sqrt(2)],
            [1, -1, -1j / math.sqrt(2), 1j / math.sqrt(2)],
            [1, 0, 1j * math.sqrt(2), 0],
            [0, 1, 0, 1j * math.sqrt(2)],
        ],
    )
    _close(vertex, expected)


@pytest.mark.parametrize("attempts", [1, 2, 4])
def test_vertex_data_channel_inverse_with_branch_phases_and_entangled_reference(
    attempts,
):
    k0, k1 = _trial_kraus()
    ch, extension, vertex = _vertex_parts()
    # Actual deterministic inverse time order X(h), CH(h,l), S(h).
    inverse_extension = _mm(
        _kron([[1, 0], [0, 1j]], IDENTITY), _mm(ch, _kron(X, IDENTITY))
    )
    _close(inverse_extension, _dagger(extension))
    _close(_mm(Z, _mm(U, Z)), _dagger(U))
    forward = _mm(extension, _kron(k0, IDENTITY))
    inverse_trial = _mm(Z, _mm(k0, Z))
    inverse_failure = _mm(Z, _mm(k1, Z))
    inverse = _mm(_kron(inverse_trial, IDENTITY), inverse_extension)
    _close(forward, _scale(ALPHA, vertex))
    _close(inverse, _scale(ALPHA, _dagger(vertex)))
    _close(inverse_failure, _scale(BETA, IDENTITY))
    # E† is done once before the loop, so a failed attempt leaves beta*E†,
    # not beta*IDENTITY on the original vertex. Retrying must act after this prefix.
    inv_path = inverse_extension
    fwd_path = _kron(IDENTITY, IDENTITY)
    for _ in range(attempts - 1):
        inv_path = _mm(_kron(inverse_failure, IDENTITY), inv_path)
        fwd_path = _mm(_kron(k1, IDENTITY), fwd_path)
    inv_path = _mm(_kron(inverse_trial, IDENTITY), inv_path)
    fwd_path = _mm(extension, _mm(_kron(k0, IDENTITY), fwd_path))
    phase = BETA ** (attempts - 1) * ALPHA
    _close(inv_path, _scale(phase, _dagger(vertex)))
    _close(fwd_path, _scale(phase, vertex))
    # alpha, NOT alpha.conjugate(): inverse channel is a fresh instrument.
    _close(_mm(inv_path, fwd_path), _scale(phase**2, _kron(IDENTITY, IDENTITY)))
    psi = [1, 2j, -3, 1j, 2 - 1j, -1, 0.5j, 3j]
    norm = math.sqrt(sum(abs(x) ** 2 for x in psi))
    psi = [x / norm for x in psi]
    branch = _apply_with_reference(fwd_path, psi)
    recovered = _apply_with_reference(inv_path, branch)
    assert recovered == pytest.approx([phase**2 * x for x in psi], abs=2e-15)
    failed_inverse = _mm(_kron(inverse_failure, IDENTITY), inverse_extension)
    _close(failed_inverse, _scale(BETA, inverse_extension))
    failed_state = _apply_with_reference(failed_inverse, psi)
    assert failed_state == pytest.approx(
        [BETA * x for x in _apply_with_reference(inverse_extension, psi)], abs=2e-15
    )
    # The failure branch and completeness retain arbitrary-input semantics.
    _close(_mm(_dagger(forward), forward), _scale(0.75, _kron(IDENTITY, IDENTITY)))
    _close(_mm(_dagger(inverse), inverse), _scale(0.75, _kron(IDENTITY, IDENTITY)))
    _close(
        _mm(_dagger(failed_inverse), failed_inverse),
        _scale(0.25, _kron(IDENTITY, IDENTITY)),
    )

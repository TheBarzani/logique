"""Scalar independent reflections and exhaustive integer coloring fixtures."""

from fractions import Fraction
import math
import subprocess
import sys

import pytest

from logique.benchmarks import ideal_iterations as ideal
from logique.coloring import ColoringProblem


def ledger(m, n, **kwargs):
    return ideal.ideal_iteration_ledger(m, n, max_rows=100, max_iterations=99, **kwargs)


def exact_reflections(m, n, steps):
    """Independent O then signed D via its rational weighted dot product.

    g=sqrt(p)*u and b=sqrt(1-p)*v; return (P_j, v_j). This uses two
    first-order reflections, not the implementation's Chebyshev recurrences.
    """
    p = Fraction(m, n)
    u = v = Fraction(1)
    result = []
    for _ in range(steps + 1):
        result.append((p * u * u, v))
        oracle_u = -u
        dot = p * oracle_u + (1 - p) * v
        u, v = 2 * dot - oracle_u, 2 * dot - v
        assert p * u * u + (1 - p) * v * v == 1
    return result


def assert_exact_peak(m, n, candidates, peak):
    """Check the bracket, exact probability ordering and required sweep extent."""
    out = ledger(m, n)
    assert out.first_peak_candidates == candidates
    assert out.first_peak_iteration == peak
    assert [r.iterations for r in out.rows] == list(range(peak + 2))
    exact = exact_reflections(m, n, max(peak + 1, candidates[1]))
    lower, upper = candidates
    assert all(exact[j][1] > 0 for j in range(upper))
    if lower == upper:
        assert exact[upper][1] == 0
    else:
        assert exact[upper][1] < 0
        if peak == lower:
            assert exact[lower][0] >= exact[upper][0]
        else:
            assert exact[upper][0] > exact[lower][0]
    # Later oscillations are not optimized: only compare first-lobe candidates.
    for row in out.rows:
        assert row.analytical_success_probability == pytest.approx(
            float(exact[row.iterations][0]), abs=2e-14
        )
    return exact


@pytest.mark.parametrize(
    "m,n,candidates,peak",
    [
        (18014398509481983, 36028797018963968, (0, 1), 1),
        (18014398509481985, 36028797018963968, (0, 1), 0),
        (14644660940672623, 10**17, (1, 2), 2),
        (14644660940672624, 10**17, (1, 2), 1),
        (4503599627370495, 18014398509481984, (1, 2), 1),
        (4503599627370497, 18014398509481984, (0, 1), 1),
        (1, 4, (1, 1), 1),
        (1, 2, (0, 1), 0),
        (3, 4, (0, 1), 0),
    ],
)
def test_exact_adversarial_counts(m, n, candidates, peak):
    exact = assert_exact_peak(m, n, candidates, peak)
    if 2 * m == n:
        assert exact[0][0] == exact[1][0] == Fraction(1, 2)
    elif peak > 0:
        assert exact[peak][0] > exact[peak - 1][0]
        assert exact[peak][0] > exact[peak + 1][0]


@pytest.mark.parametrize("j", range(1, 9))
@pytest.mark.parametrize("side", [-1, 1])
def test_both_sides_of_candidate_boundaries(j, side):
    # Float only locates a fixture; exact signs independently prove its side.
    n = 10**17
    m = round(n * math.sin(math.pi / (4 * j + 2)) ** 2) + side * 100
    candidates = (j, j + 1) if side < 0 else (j - 1, j)
    assert_exact_peak(m, n, candidates, j)


@pytest.mark.parametrize("j", range(8))
@pytest.mark.parametrize("side", [-1, 1])
def test_both_sides_of_nearest_peak_boundaries(j, side):
    n = 10**17
    m = round(n * math.sin(math.pi / (4 * j + 4)) ** 2) + side * 100
    peak = j + 1 if side < 0 else j
    exact = assert_exact_peak(m, n, (j, j + 1), peak)
    assert (exact[j + 1][0] > exact[j][0]) == (side < 0)


@pytest.mark.parametrize(
    "m,n,rows,iterations",
    [
        (18014398509481983, 36028797018963968, 2, 1),
        (18014398509481983, 36028797018963968, 2, 2),
        (18014398509481983, 36028797018963968, 3, 1),
        (14644660940672623, 10**17, 3, 3),
        (14644660940672623, 10**17, 4, 2),
        (1, 2**64, 1000, 1000),
        (0, 2**64, 1000, 1000),
        (2**64 - 2, 2**64 - 1, 1000, 1000),
        (1, 100000, 1000, 1000),
        (1, 4, 2, 99),
        (1, 2, 1, 99),
    ],
)
def test_boundary_and_internal_caps_reject_before_rows(
    monkeypatch, m, n, rows, iterations
):
    def forbidden(*args, **kwargs):
        pytest.fail("Unresolved decision or insufficient cap reached row allocation")

    monkeypatch.setattr(ideal, "IterationRow", forbidden)
    with pytest.raises(ValueError, match="cap|float boundary"):
        ideal.ideal_iteration_ledger(m, n, max_rows=rows, max_iterations=iterations)


def test_smallest_nonzero_12_bit_fraction_and_fixed_bracket_bound():
    assert_exact_peak(1, 4096, (49, 50), 50)
    # Enormous caller caps cannot increase bounded scalar work or row count.
    out = ideal.ideal_iteration_ledger(
        1, 4096, max_rows=10**100, max_iterations=10**100
    )
    assert out.first_peak_iteration == 50
    assert len(out.rows) == 52


def test_fixed_degree_and_count_caps_include_their_endpoints():
    out = ideal.ideal_iteration_ledger(1, 26700, max_rows=130, max_iterations=129)
    assert out.first_peak_candidates == (127, 128)
    assert out.first_peak_iteration == 128
    assert len(out.rows) == 130
    exact = exact_reflections(1, 26700, 129)
    assert all(exact[j][1] > 0 for j in range(128))
    assert exact[128][1] < 0
    assert exact[128][0] > exact[127][0]
    assert exact[128][0] > exact[129][0]
    out = ledger(0, 2**64 - 1)
    assert out.first_peak_iteration == 0
    assert [r.analytical_success_probability for r in out.rows] == [0, 0]


@pytest.mark.parametrize("n", range(1, 33))
def test_independent_signed_good_bad_reflections(n):
    for m in range(n + 1):
        result = ledger(m, n)
        p = m / n
        a = (math.sqrt(p), math.sqrt(1 - p))
        g, b = a
        for row in result.rows:
            assert row.analytical_success_probability == pytest.approx(g * g, abs=2e-14)
            assert g * g + b * b == pytest.approx(1, abs=2e-14)
            # O negates good only; D=2|a><a|-I with its correct signed action.
            phase_g, phase_b = -g, b
            projection = a[0] * phase_g + a[1] * phase_b
            g, b = 2 * a[0] * projection - phase_g, 2 * a[1] * projection - phase_b
        if 0 < m < n:
            # Amplitude, not probability, distinguishes D from -D.
            theta = math.asin(math.sqrt(p))
            assert g == pytest.approx(math.sin((2 * len(result.rows) + 1) * theta))
            assert b == pytest.approx(math.cos((2 * len(result.rows) + 1) * theta))


def test_peak_tie_boundaries_and_nonmonotonicity():
    tied = ledger(1, 2)
    assert tied.first_peak_candidates == (0, 1)
    assert tied.first_peak_iteration == 0
    assert [r.iterations for r in tied.rows] == [0, 1]
    for m in (0, 8):
        result = ledger(m, 8)
        assert result.first_peak_candidates == (0, 0)
        assert result.first_peak_iteration == 0
        assert [r.analytical_success_probability for r in result.rows] == [m / 8] * 2
    result = ledger(2, 256)
    probabilities = [r.analytical_success_probability for r in result.rows]
    assert probabilities[1] == pytest.approx(0.06885528564453125)
    assert result.first_peak_iteration == 8
    assert probabilities[9] < probabilities[8]
    assert result.probability_kind.startswith("analytical")
    assert "noise" in result.unavailable
    assert "leakage" in result.unavailable
    assert "t_depth" in result.unavailable


@pytest.mark.parametrize("m,n", [(1, 4), (2, 9), (1, 100), (4, 5)])
def test_peak_candidates_and_exact_sweep_extent(m, n):
    out = ledger(m, n)
    x = math.pi / (4 * math.asin(math.sqrt(m / n))) - 0.5
    expected_candidates = (math.floor(x), math.ceil(x))
    if 4 * m == n:
        expected_candidates = (1, 1)
    assert out.first_peak_candidates == expected_candidates
    assert len(out.rows) == out.first_peak_iteration + 2
    candidates = out.first_peak_candidates
    best = out.rows[out.first_peak_iteration].analytical_success_probability
    for j in candidates:
        assert best >= math.sin((2 * j + 1) * math.asin(math.sqrt(m / n))) ** 2 - 1e-15


@pytest.mark.parametrize("bad", [True, False, 1.0, -1, None, math.inf, math.nan, "1"])
def test_integer_rejection(bad):
    for args in ((bad, 8), (1, bad)):
        with pytest.raises(ValueError):
            ledger(*args)
    for key in ("max_rows", "max_iterations"):
        args = dict(max_rows=10, max_iterations=9)
        args[key] = bad
        with pytest.raises(ValueError):
            ideal.ideal_iteration_ledger(1, 4, **args)
    with pytest.raises(ValueError):
        ideal.random_sampling_reference(1, 8, trials=bad, cost_basis="unpriced trial")


def test_inconsistent_unknown_and_unrepresentable_counts():
    for m, n in [(1, 0), (2, 1), (None, 10), (1, 10**1000), (10**1000 - 1, 10**1000)]:
        with pytest.raises(ValueError):
            ledger(m, n)
    with pytest.raises(TypeError):
        ideal.ideal_iteration_ledger(1, 8)
    with pytest.raises(ValueError):
        ledger(1, 8, costs={})


def test_sweep_rejects_before_row_construction(monkeypatch):
    def forbidden(*args, **kwargs):
        pytest.fail("row construction occurred before cap rejection")

    monkeypatch.setattr(ideal, "IterationRow", forbidden)
    for m, n, rows, iterations in [
        (1, 2**1000, 3, 2),
        (1, 4, 2, 2),
        (0, 1, 1, 1),
        (1, 1, 2, 0),
    ]:
        with pytest.raises(ValueError, match="cap"):
            ideal.ideal_iteration_ledger(m, n, max_rows=rows, max_iterations=iterations)


def test_cost_accounting_and_zero_probability():
    costs = ideal.InvocationCosts(3, 5, 7, "supplied additive gate-count units")
    out = ledger(1, 4, costs=costs)
    for row in out.rows:
        assert row.supplied_program_cost == 3 + row.iterations * 18
        assert row.expected_cost_per_success == pytest.approx(
            row.supplied_program_cost / row.analytical_success_probability
        )
        assert "independent_identical" in row.repeated_cost_status
    assert out.rows[0].supplied_program_cost == 3
    zero = ledger(0, 4, costs=costs)
    assert zero.rows[0].expected_cost_per_success is None
    assert "infinite_expected_runs" in zero.rows[0].repeated_cost_status
    assert ledger(1, 4).rows[0].repeated_cost_status == "unavailable_cost"
    assert ledger(1, 1, costs=costs).rows[0].expected_cost_per_success == 3
    assert (
        ledger(0, 1, costs=ideal.InvocationCosts(0, 0, 0, "units"))
        .rows[0]
        .expected_cost_per_success
        is None
    )
    with pytest.raises(ValueError, match="overflow"):
        ideal.InvocationCosts(1e308, 1e308, 0, "units").program_cost(1)
    assert ideal.InvocationCosts(1e308, 1e308, 0, "units").program_cost(0) == 1e308


@pytest.mark.parametrize("bad", [True, -1, math.inf, math.nan, "3", 10**1000])
def test_cost_rejection(bad):
    for position in range(3):
        values = [1, 2, 3]
        values[position] = bad
        with pytest.raises(ValueError):
            ideal.InvocationCosts(*values, "units")
    with pytest.raises(ValueError):
        ideal.random_sampling_reference(
            1, 4, trials=2, trial_cost=bad, cost_basis="units/trial"
        )


def test_cost_basis_and_float_overflow():
    for basis in ("", "T-depth", None, " dependency depth "):
        with pytest.raises(ValueError):
            ideal.InvocationCosts(1, 2, 3, basis)
    with pytest.raises(ValueError, match="overflow"):
        ledger(1, 100, costs=ideal.InvocationCosts(1e308, 0, 0, "units"))
    for r, cost in [(10, 1e308), (10**1000, 1)]:
        with pytest.raises(ValueError):
            ideal.random_sampling_reference(
                1, 4, trials=r, trial_cost=cost, cost_basis="units/trial"
            )
    for basis in ("", None):
        with pytest.raises(ValueError):
            ideal.random_sampling_reference(1, 4, trials=1, cost_basis=basis)


@pytest.mark.parametrize("m,n", [(0, 4), (4, 4), (1, 4), (2, 27)])
@pytest.mark.parametrize("r", [0, 1, 2, 10])
def test_random_reference_independent_exact_fraction(m, n, r):
    reference = ideal.random_sampling_reference(
        m,
        n,
        trials=r,
        trial_cost=7,
        cost_basis="7 units per independent predicate evaluation",
    )
    assert reference.analytical_success_probability == pytest.approx(
        float(1 - (1 - Fraction(m, n)) ** r)
    )
    assert reference.trials == r
    assert reference.supplied_total_cost == 7 * r
    assert reference.probability_kind == "analytical_independent_uniform_random_trials"


def test_random_small_probability_is_stable():
    result = ideal.random_sampling_reference(
        1, 10**20, trials=1, cost_basis="unpriced uniform trial"
    )
    assert result.analytical_success_probability == 1e-20
    assert result.supplied_total_cost is None


def fixtures():
    for n in range(3, 9):
        yield ColoringProblem(
            tuple(range(n)), tuple((i, i + 1) for i in range(n - 1)), 2
        ), 2
    yield ColoringProblem((4, 11, 29), ((4, 11), (11, 29), (4, 29)), 3), 6
    yield ColoringProblem(
        tuple(range(5)), tuple((i, (i + 1) % 5) for i in range(5)), 3
    ), 30
    yield ColoringProblem(tuple(range(4)), ((0, 1), (1, 2), (2, 3)), 3), 24
    yield ColoringProblem((0, 1, 2), ((0, 1), (1, 2), (0, 2)), 2), 0
    yield ColoringProblem((0,), ((0, 0),), 3), 0
    yield ColoringProblem((3, 9), (), 3), 9
    yield ColoringProblem((), (), 3), 1
    yield ColoringProblem((4, 11, 29), ((4, 29),), 5), 100
    yield ColoringProblem((0, 1), ((0, 1),), 1), 0
    yield ColoringProblem((9,), (), 1), 1
    yield ColoringProblem(tuple(range(6)), (), 3), 729


@pytest.mark.parametrize("regime", ["R1", "R2", "R3"])
@pytest.mark.parametrize("problem,expected", list(fixtures()))
def test_bounded_coloring_fixtures_independent_binary_enumeration(
    problem, expected, regime
):
    result = ideal.count_coloring_support(problem, regime=regime)
    c = max(1, (problem.colors - 1).bit_length())
    assert result.data_bits <= 12
    assert result.support == (
        2 ** (c * len(problem.vertices))
        if regime == "R1"
        else problem.colors ** len(problem.vertices)
    )
    # Independent binary-word decoding and maintained explicit integer checker.
    positives, negatives, invalids, edge_failures = [], [], [], []
    for packed in range(2**result.data_bits):
        word = tuple(
            (packed >> (c * i)) & ((1 << c) - 1) for i in range(len(problem.vertices))
        )
        codes = all(x < problem.colors for x in word)
        if regime != "R1" and not codes:
            continue
        assignment = dict(zip(problem.vertices, word))
        (positives if problem.is_valid(assignment) else negatives).append(word)
        if not codes:
            invalids.append(word)
        elif any(assignment[u] == assignment[v] for u, v in problem.edges):
            edge_failures.append(word)
    assert result.marked == expected == len(positives)
    assert result.rejected == len(negatives)
    assert result.invalid_code_count == len(invalids)
    assert result.edge_violation_count == len(edge_failures)
    for witness, words in [
        (result.positive_witness, positives),
        (result.negative_witness, negatives),
        (result.invalid_code_witness, invalids),
        (result.edge_violation_witness, edge_failures),
    ]:
        assert (witness in words) if words else (witness is None)
    assert result.marked + result.rejected == result.support
    assert result.rejected == result.invalid_code_count + result.edge_violation_count
    assert result.coverage.startswith("exhaustive")
    out = ledger(result.marked, result.support)
    assert out.marked == expected


def test_asymmetric_unused_codes_and_r3_restriction():
    graph = ColoringProblem((4, 11), ((4, 11),), 5)
    r1 = ideal.count_coloring_support(graph, regime="R1")
    r3 = ideal.count_coloring_support(graph, regime="R3")
    assert (r1.marked, r1.support, r3.marked, r3.support) == (20, 64, 20, 25)
    assert r1.invalid_code_count == 39
    assert (0, 4) != (4, 0)
    assert graph.is_valid({4: 0, 11: 4})
    assert not graph.is_valid({4: 0, 11: 5})  # edge-only would accept this
    assert ideal.count_coloring_support(graph, regime="R2").marked == r3.marked


def test_enumeration_rejection_precedes_product(monkeypatch):
    def forbidden(*args, **kwargs):
        pytest.fail("Enumeration started before bound rejection")

    monkeypatch.setattr(ideal, "product", forbidden)
    with pytest.raises(ValueError, match="12 data bits"):
        ideal.count_coloring_support(
            ColoringProblem(tuple(range(13)), (), 2), regime="R1"
        )
    with pytest.raises(ValueError, match="Precolored"):
        ideal.count_coloring_support(ColoringProblem((0,), (), 2, {0: 0}), regime="R2")
    with pytest.raises(ValueError, match="regime"):
        ideal.count_coloring_support(ColoringProblem((), (), 2), regime="unknown")


def test_standard_library_import_boundary():
    code = """
import sys
import logique.benchmarks.ideal_iterations as module
from pathlib import Path
assert Path(module.__file__).resolve() == Path('src/logique/benchmarks/ideal_iterations.py').resolve()
assert not any(name in sys.modules for name in ('qiskit', 'numpy', 'pandas', 'networkx', 'matplotlib'))
"""
    subprocess.run([sys.executable, "-S", "-c", code], check=True, timeout=10)


def test_exact_rational_zero_and_repeated_cost_range():
    costs = ideal.InvocationCosts(1, 2, 3, "units")
    row = ledger(3, 4, costs=costs).rows[1]
    assert row.analytical_success_probability == 0
    assert row.expected_cost_per_success is None
    assert "infinite_expected_runs" in row.repeated_cost_status
    out = ledger(1, 10000, costs=ideal.InvocationCosts(1e305, 0, 0, "units"))
    assert out.rows[0].repeated_cost_status == "infinite_float_cost"
    assert out.rows[0].expected_cost_per_success is None
    assert all(math.isfinite(row.supplied_program_cost) for row in out.rows)


def test_empty_graph_large_palette_needs_no_palette_enumeration():
    out = ideal.count_coloring_support(ColoringProblem((), (), 10**100), regime="R1")
    assert (out.marked, out.support, out.data_bits) == (1, 1, 0)


def test_invalid_edge_integer_and_depth_cost_basis():
    with pytest.raises(ValueError, match="Edges"):
        ideal.count_coloring_support(
            ColoringProblem((0, 1), ((False, 1),), 2), regime="R1"
        )
    with pytest.raises(ValueError, match="Depth"):
        ideal.random_sampling_reference(
            1, 4, trials=2, trial_cost=7, cost_basis="T-depth"
        )

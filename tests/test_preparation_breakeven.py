"""Hypothetical supplied-cost fixtures, not graph-resource measurements."""

from fractions import Fraction as F
from itertools import product
from pathlib import Path

import pytest

from logique.benchmarks import preparation_breakeven as pb


ASSUMPTIONS = pb.RenewalAssumptions(True, True, True, True)
LIMITS = pb.RusLimits(4, 4, 8, 4096)


def static(regime="R2", *, j=1, a=2, o=3, z=5, domain="hypothetical valid domain"):
    return pb.StaticCosts(regime, domain, j, a, o, z)


def h_cost(*, j=2, o=7, z=4):
    return static("R1", j=j, a=0, o=o, z=z, domain="hypothetical binary domain")


def rus(n, j, cap, **kwargs):
    arguments = dict(
        k=3,
        cap=cap,
        limits=LIMITS,
        ideal_instrument_assumptions=True,
        oracle_t=F(7, 3),
        zero_reflection_t=F(11, 2),
    )
    arguments.update(kwargs)
    return pb.rus_cost_summary(n, j, **arguments)


def test_import_is_assigned_source():
    assert Path(pb.__file__).resolve() == (
        Path(__file__).resolve().parents[1]
        / "src/logique/benchmarks/preparation_breakeven.py"
    )


@pytest.mark.parametrize("j_h,j_v,regime", product(range(4), range(4), ("R2", "R3")))
def test_threshold_from_independent_concatenated_schedule(j_h, j_v, regime):
    # Independently sum explicit A / O,A†,S0,A component words, without helpers.
    h = h_cost(j=j_h, o=F(13, 2), z=F(3, 2))
    for a in (F(0), F(1, 3), F(2), F(19, 2)):
        v = static(regime, j=j_v, a=a, o=F(5, 2), z=F(1, 2))
        h_word = [F(0)]
        v_word = [a]
        for _ in range(j_h):
            h_word.extend((F(13, 2), F(0), F(3, 2), F(0)))
        for _ in range(j_v):
            v_word.extend((F(5, 2), a, F(1, 2), a))
        result = pb.compare_preparations(h, v)
        delta = sum(v_word) - sum(h_word)
        assert result.difference_t == delta
        assert result.hadamard.charge.total_t == sum(h_word)
        assert result.valid.charge.total_t == sum(v_word)
        assert result.threshold.limit_t == F(8 * j_h - 3 * j_v, 2 * j_v + 1)
        assert delta == (2 * j_v + 1) * (a - result.threshold.limit_t)
        assert result.relation == (
            "improvement" if delta < 0 else "loss" if delta > 0 else "tie"
        )
        assert result.hadamard.domain != result.valid.domain
        assert result.success is None
        assert result.per_success_relation == "unknown"


@pytest.mark.parametrize("regime", ("R2", "R3"))
def test_positive_exact_boundary_and_neighbours(regime):
    # H costs 26; V's non-A cost is 5, A multiplicity 7 => threshold 3.
    h = h_cost(j=2, o=9, z=4)
    for a, expected in (
        (F(299, 100), "improvement"),
        (3, "tie"),
        (F(301, 100), "loss"),
    ):
        result = pb.compare_preparations(h, static(regime, j=3, a=a, o=1, z=F(2, 3)))
        assert result.threshold.limit_t == 3
        assert result.threshold.coefficient == 7
        assert result.threshold.boundary == "positive"
        assert result.relation == expected


@pytest.mark.parametrize("a", (0, F(1, 1000), 3))
def test_negative_and_zero_threshold(a):
    h = h_cost(j=1, o=1, z=1)
    negative = pb.compare_preparations(h, static(j=1, a=a, o=2, z=1))
    zero = pb.compare_preparations(h, static(j=1, a=a, o=1, z=1))
    assert negative.threshold.limit_t == F(-1, 3)
    assert negative.threshold.boundary == "negative"
    assert negative.relation == "loss"
    assert zero.threshold.limit_t == 0
    assert zero.threshold.boundary == "zero"
    assert zero.relation == ("tie" if a == 0 else "loss")


def test_j_zero_and_explicit_unknown_components():
    h = h_cost(j=0, o=None, z=None)
    v = static(j=0, a=0, o=None, z=None)
    result = pb.compare_preparations(h, v)
    assert result.relation == "tie"
    assert result.threshold.limit_t == 0
    assert result.threshold.coefficient == 1
    assert v.oracle_t is None and v.zero_reflection_t is None
    assert v.charge.unknown_terms == ()
    assert "Clifford operations" in result.unpriced
    assert (
        pb.compare_preparations(
            h_cost(j=2), static(j=0, a=5, o=None, z=None)
        ).threshold.limit_t
        == 22
    )
    assert pb.compare_preparations(h_cost(j=0), static(j=1)).relation == "loss"


def test_unknown_is_symbolic_and_not_assumed_shared():
    v = static(j=2, a=None, o=3, z=None)
    assert v.charge.known_t == 6
    assert v.charge.unknown_terms == (("A", 5), ("S0", 2))
    result = pb.compare_preparations(h_cost(), v)
    assert result.relation == "unknown" and result.threshold.limit_t is None
    threshold_only = pb.compare_preparations(h_cost(), static(j=2, a=None, o=1, z=2))
    assert threshold_only.threshold.limit_t == F(16, 5)
    assert threshold_only.relation == "unknown"
    both_unknown = pb.compare_preparations(h_cost(o=None), static(o=None))
    assert (
        both_unknown.difference_t is None
        and both_unknown.threshold.boundary == "unknown"
    )


def test_success_comparison_requires_external_comparable_event():
    # Hypothetical cheaper V program has worse success; rankings reverse.
    success = pb.ComparableSuccess(
        F(1, 2),
        F(1, 10),
        "same hypothetical verified solution",
        "same success predicate and verification after a completed program",
        ASSUMPTIONS,
    )
    result = pb.compare_preparations(
        h_cost(j=1, o=4, z=6), static(j=0, a=3), success=success
    )
    assert result.relation == "improvement"
    assert result.hadamard_per_success.solution_t == 20
    assert result.valid_per_success.solution_t == 30
    assert result.per_success_relation == "loss"
    assert result.success is success


@pytest.mark.parametrize("hp,vp", ((0, 1), (1, 0), (0, 0)))
def test_zero_success_never_becomes_zero_cost_per_solution(hp, vp):
    success = pb.ComparableSuccess(
        hp, vp, "event", "comparable hypothetical semantics", ASSUMPTIONS
    )
    result = pb.compare_preparations(h_cost(j=0), static(j=0, a=0), success=success)
    assert result.relation == "tie"
    assert result.per_success_relation == "unknown"
    if not hp:
        assert result.hadamard_per_success.solution_t is None
        assert result.hadamard_per_success.solution_status == "undefined_zero_success"
    if not vp:
        assert result.valid_per_success.solution_t is None


@pytest.mark.parametrize(
    "charge,p,q", product((None, 0, F(5, 3)), (0, F(3, 4), 1), (None, 0, F(2, 3), 1))
)
def test_renewal_boundaries(charge, p, q):
    result = pb.renewal_cost(
        charge, p, assumptions=ASSUMPTIONS, solution_success_given_completion=q
    )
    if p == 0:
        assert result.completion_status == "undefined_zero_success"
        assert result.completion_t is None
    elif charge is None:
        assert result.completion_status == "unknown_cost"
    else:
        # Renewal equation counts a full attempt also on failure.
        assert result.completion_t == charge + (1 - p) * result.completion_t
    if q is None:
        assert result.solution_status == "not_supplied"
        assert result.solution_probability is None
    elif p * q == 0:
        assert result.solution_status == "undefined_zero_success"
        assert result.solution_t is None
    elif charge is None:
        assert result.solution_status == "unknown_cost"
    else:
        assert result.solution_probability == p * q
        assert result.solution_t == charge + (1 - p * q) * result.solution_t


def tiny_distribution(n, j, cap):
    """Independent finite probability tree, not a retry runtime or circuit.

    Each tuple is (probability, charged T, completed). Enumerate first-success
    records plus exhausted records and halt the mathematical word there.
    """
    word = ["forward"] * n
    for _ in range(j):
        word += ["oracle"] + ["inverse"] * n + ["zero"] + ["forward"] * n
    records = [(F(1), F(0), True)]
    for operation in word:
        next_records = []
        for probability, cost, live in records:
            if not live:
                next_records.append((probability, cost, False))
            elif operation in ("oracle", "zero"):
                next_records.append(
                    (
                        probability,
                        cost + (F(7, 3) if operation == "oracle" else F(11, 2)),
                        True,
                    )
                )
            else:
                for r in range(1, cap + 1):
                    next_records.append(
                        (
                            probability * F(3, 4) * F(1, 4) ** (r - 1),
                            cost + 2 * r + 2,
                            True,
                        )
                    )
                next_records.append(
                    (
                        probability * F(1, 4) ** cap,
                        cost + 2 * cap + (2 if operation == "inverse" else 0),
                        False,
                    )
                )
        records = next_records
    return records


@pytest.mark.parametrize("n,j,cap", product(range(3), range(2), range(3)))
def test_capped_summary_and_renewal_from_full_tiny_distribution(n, j, cap):
    records = tiny_distribution(n, j, cap)
    assert sum(p for p, _, _ in records) == 1
    completed = sum(p for p, _, live in records if live)
    expectation = sum(p * cost for p, cost, _ in records)
    good_charge = sum(p * cost for p, cost, live in records if live)
    result = rus(
        n,
        j,
        cap,
        renewal_assumptions=ASSUMPTIONS,
        solution_success_given_completion=F(2, 5),
    )
    assert result.exhaustion_probability == 1 - completed
    assert result.unconditional_stop_t == expectation
    assert result.unlimited_expected_t == F(14 * n * (1 + 2 * j), 3) + j * (
        F(7, 3) + F(11, 2)
    )
    if completed:
        assert result.conditional_completed_t == good_charge / completed
        assert result.renewal.completion_t == expectation / completed
        assert result.renewal.solution_t == expectation / (completed * F(2, 5))
        assert (
            result.renewal.completion_t
            == expectation + (1 - completed) * result.renewal.completion_t
        )
    else:
        assert result.conditional_completed_t is None
        assert result.renewal.completion_t is None
        assert result.renewal.solution_status == "undefined_zero_success"


def test_conditional_cost_excludes_failures_and_cannot_be_static_row():
    row = rus(1, 0, 1, renewal_assumptions=ASSUMPTIONS)
    assert row.conditional_completed_t == 4
    assert row.unconditional_stop_t == F(7, 2)
    assert row.exhaustion_probability == F(1, 4)
    assert row.renewal.completion_t == F(14, 3)
    assert row.renewal.completion_t != row.conditional_completed_t
    assert set(row.ledger.unpriced) >= {
        "measurement",
        "reset/repreparation",
        "classical feed-forward",
        "Clifford gates",
    }
    with pytest.raises(ValueError, match="deterministic"):
        pb.compare_preparations(h_cost(), row)


def test_rus_empty_zero_cap_unknown_and_unlimited():
    empty = rus(
        0, 0, 0, oracle_t=None, zero_reflection_t=None, renewal_assumptions=ASSUMPTIONS
    )
    assert empty.exhaustion_probability == 0
    assert empty.renewal.completion_t == 0
    empty_external = rus(
        0, 1, 0, oracle_t=None, zero_reflection_t=None, renewal_assumptions=ASSUMPTIONS
    )
    assert empty_external.exhaustion_probability == 0
    assert empty_external.unconditional_stop_t is None
    assert empty_external.renewal.completion_status == "unknown_cost"
    impossible = rus(
        1, 1, 0, oracle_t=None, zero_reflection_t=None, renewal_assumptions=ASSUMPTIONS
    )
    assert impossible.unconditional_stop_t == 0
    assert impossible.exhaustion_probability == 1
    assert impossible.renewal.completion_t is None
    assert impossible.renewal.completion_status == "undefined_zero_success"
    unknown = rus(1, 1, 2, oracle_t=None)
    assert unknown.unconditional_stop_t is None
    assert unknown.conditional_completed_t is None
    assert unknown.unlimited_expected_t is None
    unlimited = rus(2, 2, None, renewal_assumptions=ASSUMPTIONS)
    assert unlimited.exhaustion_probability == 0
    assert unlimited.unlimited_expected_t == unlimited.unconditional_stop_t
    assert unlimited.renewal.completion_t == unlimited.conditional_completed_t
    assert unlimited.ledger.capped_vertex_t_upper_bound is None


BAD_COSTS = (
    True,
    False,
    -1,
    F(-1, 3),
    1.0,
    float("nan"),
    float("inf"),
    "1",
    complex(1),
)


@pytest.mark.parametrize("field", ("preparation_t", "oracle_t", "zero_reflection_t"))
@pytest.mark.parametrize("bad", BAD_COSTS)
def test_reject_inexact_or_negative_static_costs_even_if_unused(field, bad):
    arguments = dict(
        regime="R2",
        domain="hypothetical",
        j=0,
        preparation_t=1,
        oracle_t=0,
        zero_reflection_t=0,
    )
    arguments[field] = bad
    with pytest.raises(ValueError):
        pb.StaticCosts(**arguments)


@pytest.mark.parametrize("bad", (True, -1, 1.0, F(1), "1", 1_000_001, 10**100))
def test_reject_iteration_counts(bad):
    with pytest.raises(ValueError):
        static(j=bad)


@pytest.mark.parametrize("bad", BAD_COSTS + (None, F(11, 10)))
def test_reject_invalid_probabilities(bad):
    with pytest.raises(ValueError):
        pb.renewal_cost(0, bad, assumptions=ASSUMPTIONS)
    with pytest.raises(ValueError):
        pb.ComparableSuccess(1, bad, "event", "semantics", ASSUMPTIONS)
    if bad is not None:
        with pytest.raises(ValueError):
            pb.renewal_cost(
                0, 1, assumptions=ASSUMPTIONS, solution_success_given_completion=bad
            )
        with pytest.raises(ValueError):
            rus(
                1,
                0,
                1,
                renewal_assumptions=ASSUMPTIONS,
                solution_success_given_completion=bad,
            )


def test_bounds_and_mandatory_assumptions_before_ledger(monkeypatch):
    from logique.benchmarks import rus_accounting

    def forbidden(*args, **kwargs):
        pytest.fail("ledger called before rejecting out-of-scope input")

    monkeypatch.setattr(rus_accounting, "analytical_ledger", forbidden)
    for arguments in (
        dict(n=5, j=0, cap=1),
        dict(n=0, j=5, cap=1),
        dict(n=1, j=0, cap=9),
        dict(n=True, j=0, cap=1),
        dict(n=1, j=F(1), cap=1),
        dict(n=1, j=0, cap=True),
        dict(n=4, j=4, cap=8, limits=pb.RusLimits(4, 4, 8, 64)),
        dict(n=64, j=64, cap=0, limits=pb.RusLimits(64, 64, 64, 4096)),
        dict(n=1, j=0, cap=1, k=2),
        dict(n=1, j=0, cap=1, k=True),
        dict(n=1, j=0, cap=1, ideal_instrument_assumptions=False),
        dict(n=1, j=0, cap=1, ideal_instrument_assumptions=1),
        dict(n=1, j=0, cap=1, limits=None),
        dict(n=1, j=0, cap=1, oracle_t=1.5),
        dict(n=1, j=0, cap=1, solution_success_given_completion=F(1, 2)),
        dict(n=1, j=0, cap=1, renewal_assumptions=True),
    ):
        with pytest.raises(ValueError):
            rus(**arguments)


def test_scalar_size_and_limit_validation():
    huge = 1 << pb.MAX_INPUT_BITS
    for cost in (huge, F(1, huge)):
        with pytest.raises(ValueError, match="bits"):
            static(a=cost)
        with pytest.raises(ValueError, match="bits"):
            pb.renewal_cost(cost, 1, assumptions=ASSUMPTIONS)
    for limits in (
        (65, 1, 1, 4096),
        (1, 65, 1, 4096),
        (1, 1, 65, 4096),
        (1, 1, 1, 4097),
        (True, 1, 1, 4096),
        (1, 1, 1, -1),
    ):
        with pytest.raises(ValueError):
            pb.RusLimits(*limits)
    assert static(j=pb.MAX_ITERATIONS, a=0, o=0, z=0).charge.total_t == 0


def test_reject_missing_or_inconsistent_provenance():
    for a in (None, 1):
        with pytest.raises(ValueError, match="zero logical T"):
            static("R1", a=a)
    for domain in ("", " ", None, "x" * 4097):
        with pytest.raises(ValueError):
            static(domain=domain)
    with pytest.raises(ValueError):
        static("R4")
    with pytest.raises(ValueError):
        pb.compare_preparations(static(), h_cost())
    with pytest.raises(ValueError):
        pb.compare_preparations(h_cost(), static(), success=F(1, 2))
    for field in range(4):
        values = [True] * 4
        values[field] = 1
        with pytest.raises(ValueError):
            pb.RenewalAssumptions(*values)
    with pytest.raises(ValueError):
        pb.renewal_cost(1, 1, assumptions=None)
    with pytest.raises(ValueError):
        pb.ComparableSuccess(1, 1, "event", "semantics", True)
    with pytest.raises(ValueError):
        pb.ComparableSuccess(1, 1, "", "semantics", ASSUMPTIONS)
    with pytest.raises(TypeError):
        pb.StaticCosts("R2", "domain", 1, 1)
    with pytest.raises(TypeError):
        rus(1, 0, 1, quantum_controlled=True)

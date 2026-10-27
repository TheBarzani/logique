"""Hypothetical scalar regressions, not graph or performance evidence."""

from dataclasses import replace
from fractions import Fraction as F
from itertools import product

import pytest

from logique.benchmarks import preparation_breakeven as pb
from logique.benchmarks.preparation_success_threshold import (
    MAX_DERIVED_BITS,
    success_normalized_threshold,
)


def success(ph=F(2, 7), pv=F(3, 5)):
    return pb.ComparableSuccess(
        ph,
        pv,
        "same externally verified hypothetical event",
        "caller asserts comparable verification across independent domains",
        pb.RenewalAssumptions(True, True, True, True),
    )


def compare(h, v, supplied=None):
    return success_normalized_threshold(
        h,
        v,
        success=success() if supplied is None else supplied,
        stationary_attempts=True,
    )


def word(a, o, z, j):
    # Independent literal component word, only used for j<=3 in these tests.
    return [a] + [item for _ in range(j) for item in (o, a, z, a)]


@pytest.mark.parametrize("jh,jv,regime", product((0, 1, 3), (0, 2), ("R2", "R3")))
@pytest.mark.parametrize("ph,pv", [(F(2, 7), F(3, 5)), (F(3, 4), F(1, 9)), (1, 1)])
def test_independent_words_and_cross_multiplication(jh, jv, regime, ph, pv):
    h = pb.StaticCosts("R1", "H full external domain", jh, 0, F(11, 3), F(5, 7))
    ch = sum(word(F(0), F(11, 3), F(5, 7), jh))
    ev = sum(word(F(0), F(2, 5), F(7, 2), jv))
    a_count = word(1, 0, 0, jv).count(1)
    # Derive equality by cross multiplication p_H*C_V=p_V*C_H.
    boundary = (pv * ch - ph * ev) / (ph * a_count)
    for a in (F(0), F(7, 3), max(F(0), boundary)):
        v = pb.StaticCosts(regime, "independent valid domain", jv, a, F(2, 5), F(7, 2))
        cv = sum(word(a, F(2, 5), F(7, 2), jv))
        result = compare(h, v, success(ph, pv))
        cross = ph * cv - pv * ch
        assert result.hadamard_per_success.per_success_t == ch / ph
        assert result.valid_per_success.per_success_t == cv / pv
        assert result.valid_external_charge.total_t == ev
        assert result.threshold.status == "defined"
        assert result.threshold.limit_t == boundary
        assert result.threshold.coefficient == a_count / pv
        assert result.difference_t == cross / (ph * pv)
        assert result.difference_t == result.threshold.coefficient * (a - boundary)
        assert result.relation == (
            "improvement" if cross < 0 else "loss" if cross > 0 else "tie"
        )
        assert result.hadamard is h and result.valid is v
        assert result.success.event == success().event
        assert result.stationary_attempts is True


@pytest.mark.parametrize("p", [F(1, 2), F(1, 1 << 2000), 1])
def test_equal_probabilities_reduce_to_unchanged_raw_threshold(p):
    h = pb.StaticCosts("R1", "H", 2, 0, 10, 1)
    for a in (0, F(17, 3), 100, None):
        v = pb.StaticCosts("R3", "V", 1, a, 2, 3)
        raw = pb.compare_preparations(h, v)
        normalized = compare(h, v, success(p, p))
        assert normalized.threshold.limit_t == raw.threshold.limit_t
        assert normalized.threshold.boundary == raw.threshold.boundary
        assert normalized.relation == raw.relation
        assert normalized.difference_t == (
            None if raw.difference_t is None else raw.difference_t / p
        )


def test_raw_ranking_reversal_is_not_a_success_threshold():
    h = pb.StaticCosts("R1", "H", 1, 0, 3, 5)
    v = pb.StaticCosts("R2", "V", 0, 1, None, None)
    raw = pb.compare_preparations(h, v)
    result = compare(h, v, success(F(1, 2), F(1, 100)))
    assert raw.threshold.limit_t == 8 and raw.relation == "improvement"
    assert result.threshold.limit_t == F(4, 25)
    assert result.difference_t == 84 and result.relation == "loss"


@pytest.mark.parametrize(
    "offset,relation", [(-1, "improvement"), (0, "tie"), (1, "loss")]
)
def test_exact_boundary_neighbours(offset, relation):
    h = pb.StaticCosts("R1", "H", 2, 0, 10, 1)
    a = 13 + offset * F(1, 1 << 2000)
    v = pb.StaticCosts("R2", "V", 1, a, 2, 3)
    result = compare(h, v, success(F(1, 4), F(1, 2)))
    assert result.threshold.limit_t == 13
    assert result.threshold.boundary == "positive"
    assert result.threshold.coefficient == 6
    assert result.difference_t == 6 * offset * F(1, 1 << 2000)
    assert result.relation == relation


def test_negative_threshold_has_no_feasible_nonnegative_tie():
    h = pb.StaticCosts("R1", "H", 0, 0, None, None)
    for a in (0, F(1, 2), 10):
        v = pb.StaticCosts("R3", "V", 1, a, 2, 3)
        result = compare(h, v)
        assert result.threshold.limit_t == -F(5, 3)
        assert result.threshold.boundary == "negative"
        assert result.relation == "loss"


def test_zero_threshold_only_zero_cost_ties():
    h = pb.StaticCosts("R1", "H", 1, 0, 3, 5)
    for a, relation in ((0, "tie"), (F(1, 1 << 2000), "loss")):
        v = pb.StaticCosts("R2", "V", 2, a, 4, 4)
        result = compare(h, v, success(F(1, 4), F(1, 2)))
        assert result.threshold.limit_t == 0
        assert result.threshold.boundary == "zero"
        assert result.relation == relation


def test_unknown_a_keeps_known_threshold_and_unused_zero_weight_terms():
    h = pb.StaticCosts("R1", "H", 1, 0, 3, 5)
    v = pb.StaticCosts("R3", "V", 0, None, None, None)
    result = compare(h, v, success(F(1, 4), F(1, 2)))
    assert result.threshold.limit_t == 16
    assert result.threshold.status == "defined"
    assert result.valid_external_charge.total_t == 0
    assert result.valid_external_charge.unknown_terms == ()
    assert result.valid_per_success.charge.unknown_terms == (("A", 1),)
    assert result.valid_per_success.status == "unknown_cost"
    assert result.difference_t is None and result.relation == "unknown"
    used = compare(h, replace(v, j=2))
    assert used.threshold.limit_t is None
    assert used.threshold.coefficient == F(25, 3)
    assert used.threshold.status == "unknown_cost"
    assert used.valid_external_charge.unknown_terms == (("O", 2), ("S0", 2))
    assert used.valid_per_success.charge.unknown_terms == (
        ("A", 5),
        ("O", 2),
        ("S0", 2),
    )


def test_reached_h_unknown_and_shared_unknown_labels_do_not_cancel():
    h = pb.StaticCosts("R1", "H", 1, 0, None, 2)
    v = pb.StaticCosts("R2", "V", 1, 0, None, 2)
    result = compare(h, v)
    assert result.threshold.limit_t is None
    assert result.threshold.boundary == "unknown"
    assert result.hadamard_per_success.status == "unknown_cost"
    assert result.relation == "unknown"
    unused = compare(replace(h, j=0), replace(v, j=0))
    assert unused.threshold.limit_t == 0
    assert unused.relation == "tie"


@pytest.mark.parametrize(
    "ph,pv,which", [(0, 1, "hadamard"), (1, 0, "valid"), (0, 0, "both")]
)
@pytest.mark.parametrize("unknown", [False, True])
def test_zero_probability_is_undefined_even_with_zero_or_unknown_cost(
    ph, pv, which, unknown
):
    h = pb.StaticCosts("R1", "H", 1, 0, None if unknown else 0, 0)
    v = pb.StaticCosts("R2", "V", 0, None if unknown else 0, None, None)
    result = compare(h, v, success(ph, pv))
    assert result.threshold.status == f"undefined_zero_{which}_success"
    assert result.threshold.boundary == "undefined"
    assert result.threshold.limit_t is None
    assert result.threshold.coefficient is None
    assert result.difference_t is None and result.relation == "undefined"
    for p, normalized in (
        (ph, result.hadamard_per_success),
        (pv, result.valid_per_success),
    ):
        assert normalized.status == (
            "undefined_zero_success"
            if p == 0
            else "unknown_cost" if unknown else "defined"
        )
        assert normalized.per_success_t == (0 if p and not unknown else None)


def test_expanded_outputs_exceed_input_ceiling_without_revalidation(monkeypatch):
    def forbidden(*args, **kwargs):
        pytest.fail("expanded charges passed to a public scalar-input API")

    monkeypatch.setattr(pb, "renewal_cost", forbidden)
    monkeypatch.setattr(pb, "compare_preparations", forbidden)
    large = (1 << 4095) - 1
    tiny = F(1, 1 << 4095)
    h = pb.StaticCosts("R1", "H", 1_000_000, 0, large, large)
    v = pb.StaticCosts("R3", "V", 1_000_000, large, F(1, large), tiny)
    result = compare(h, v, success(tiny, 1))
    ch = 2_000_000 * large
    ev = 1_000_000 * (F(1, large) + tiny)
    cv = 2_000_001 * large + ev
    assert result.threshold.limit_t == (ch / tiny - ev) / 2_000_001
    assert result.difference_t == cv - ch / tiny
    assert result.hadamard_per_success.per_success_t == ch / tiny
    assert (
        result.hadamard_per_success.charge.total_t.numerator.bit_length()
        > pb.MAX_INPUT_BITS
    )
    assert result.threshold.limit_t.numerator.bit_length() > pb.MAX_INPUT_BITS
    for value in (
        ch,
        ev,
        cv,
        result.threshold.limit_t,
        result.threshold.coefficient,
        result.difference_t,
    ):
        assert (
            max(value.numerator.bit_length(), value.denominator.bit_length())
            <= MAX_DERIVED_BITS
        )


BAD_SCALARS = [
    True,
    False,
    -1,
    F(-1, 3),
    1.0,
    float("nan"),
    float("inf"),
    "1",
    1j,
    1 << 4096,
    F(1, 1 << 4096),
]


@pytest.mark.parametrize("bad", BAD_SCALARS)
def test_public_input_types_reject_invalid_scalars_before_accounting(bad):
    for name in ("preparation_t", "oracle_t", "zero_reflection_t"):
        values = dict(
            regime="R2",
            domain="V",
            j=0,
            preparation_t=0,
            oracle_t=0,
            zero_reflection_t=0,
        )
        values[name] = bad
        with pytest.raises(ValueError):
            pb.StaticCosts(**values)
    for ph, pv in ((bad, 1), (1, bad)):
        with pytest.raises(ValueError):
            success(ph, pv)


@pytest.mark.parametrize("bad", [True, -1, 1.0, F(1), 1_000_001, 1 << 4096])
def test_invalid_iteration_counts_reject(bad):
    with pytest.raises(ValueError):
        pb.StaticCosts("R2", "V", bad, 0, 0, 0)


def test_invalid_domains_probabilities_event_and_renewal_assumptions():
    for text in (None, "", " ", "x" * 4097):
        with pytest.raises(ValueError):
            pb.StaticCosts("R1", text, 0, 0, 0, 0)
        for field in ("event", "semantics"):
            with pytest.raises(ValueError):
                replace(success(), **{field: text})
    for p in (F(3, 2), None):
        with pytest.raises(ValueError):
            success(p, 1)
        with pytest.raises(ValueError):
            success(1, p)
    for i, bad in product(range(4), (False, 1, None)):
        flags = [True] * 4
        flags[i] = bad
        with pytest.raises(ValueError):
            pb.RenewalAssumptions(*flags)
    with pytest.raises(ValueError):
        replace(success(), renewal_assumptions=None)


def test_comparison_requires_static_rows_comparability_and_stationarity():
    h = pb.StaticCosts("R1", "H", 0, 0, None, None)
    v = pb.StaticCosts("R2", "V", 0, 0, None, None)
    for a, b in ((v, h), (h, h), (v, v), (object(), v), (h, {"expected_t": F(14, 3)})):
        with pytest.raises(ValueError):
            compare(a, b)
    # Construct an existing RUS result type without evaluating any RUS ledger.
    rus_row = pb.RusCostSummary(None, F(14, 3), F(4), F(7, 2), F(1, 4), None)
    with pytest.raises(ValueError):
        compare(h, rus_row)
    for supplied in (None, True, {"p_H": 1, "p_V": 1}):
        with pytest.raises(ValueError):
            success_normalized_threshold(
                h, v, success=supplied, stationary_attempts=True
            )
    for stationary in (False, 1, None, "True"):
        with pytest.raises(ValueError):
            success_normalized_threshold(
                h, v, success=success(), stationary_attempts=stationary
            )
    with pytest.raises(TypeError):
        success_normalized_threshold(h, v, success=success())
    assert "external verification" in compare(h, v).unpriced
    assert "runtime" in compare(h, v).unpriced

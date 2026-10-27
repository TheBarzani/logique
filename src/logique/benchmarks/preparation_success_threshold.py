"""Exact success-normalized equality thresholds for supplied static charges.

Write D=1+2j_V and E_V=j_V(O_V+S0_V). The unoptimized component word
A,(O,A-inverse,S0,A)^j has charge C=D*A+E. For positive supplied comparable
event probabilities, subtracting C_H/p_H from C_V/p_V gives

    (D/p_V)*(A_V-B),  B=((p_V/p_H)*C_H-E_V)/D.

D/p_V is positive, so exact signs decide improvement/tie/loss. B<0 admits
no nonnegative tie or improvement; B=0 permits a zero-cost tie only. Equal
probabilities recover the raw-charge threshold in preparation_breakeven;
unequal probabilities can reverse its ranking. This module leaves that API
and its raw-charge semantics unchanged.

Inputs are the public validated StaticCosts and ComparableSuccess types.
Their 4096-bit int/Fraction input ceilings and j<=1,000,000 apply before
arithmetic, including unused components. None means unknown; a zero-weight
unknown contributes nothing. Unknown A_V can coexist with a known B. Zero
p_H or p_V makes the threshold and comparison explicitly undefined, even
when the corresponding charge is zero. No zero-probability method is ranked.

C/p has a renewal interpretation only for stationary fresh independent
attempts, with the same unconditional static charge on success and failure:
R=C+(1-p)R. Explicit acknowledgements and comparable event/verification text
are assertions, not certificates of costs, domain support or event equivalence.
Expected RUS charges must never be supplied as deterministic static charges.
Verification, measurement/reset, feed-forward, Clifford operations, runtime
and physical QEC remain unpriced. No circuits or repetitions are executed.

Only a fixed number of scalar rational operations is used, with no j-sized
enumeration, inference of probabilities/solutions/j, optimization or graph
experiment. Expanded results are not fed to public scalar-input validators:
they may exceed the input ceiling. MAX_DERIVED_BITS is a conservative bound
on numerator/denominator bit lengths in this computation, including unreduced
arithmetic temporaries, not an OS memory/time guarantee or an output-admission
rule for other APIs. No FT/RUS, interval, ideal-amplitude or paper admission.
"""

from dataclasses import dataclass
from fractions import Fraction
from typing import Literal

from logique.benchmarks.preparation_breakeven import (
    ComparableSuccess,
    LogicalCharge,
    MAX_INPUT_BITS,
    StaticCosts,
)

# With b input bits and j<2**20, charges use <=3b+24 bits; normalized
# charges <=4b+24; B<=6b+24; the signed difference <=7b+48. Allow extra
# room for products before Fraction reduction. No powers/iteration loops occur.
MAX_DERIVED_BITS = 16 * MAX_INPUT_BITS + 256
UNPRICED = (
    "external verification",
    "measurement/reset/repreparation",
    "feed-forward",
    "Clifford operations",
    "runtime",
    "physical QEC",
)
ChargeStatus = Literal["defined", "unknown_cost", "undefined_zero_success"]
ThresholdStatus = Literal[
    "defined",
    "unknown_cost",
    "undefined_zero_hadamard_success",
    "undefined_zero_valid_success",
    "undefined_zero_both_success",
]


@dataclass(frozen=True)
class SuccessNormalizedCharge:
    """Retain reached unknown terms and the supplied event probability."""

    charge: LogicalCharge
    probability: Fraction
    per_success_t: Fraction | None
    status: ChargeStatus


@dataclass(frozen=True)
class SuccessPreparationThreshold:
    """Equality limit B with slope D/p_V for valid-minus-H charge per event.

    Unknown reached external costs prevent B, but not the positive slope.
    Either zero probability makes both fields None and boundary undefined.
    A negative limit is infeasible for nonnegative A, zero allows only A=0
    to tie, and a positive limit allows strict improvement below it.
    """

    coefficient: Fraction | None
    limit_t: Fraction | None
    boundary: Literal["negative", "zero", "positive", "unknown", "undefined"]
    status: ThresholdStatus


@dataclass(frozen=True)
class SuccessThresholdComparison:
    """Analytical comparison under independent supplied j/domain/cost inputs.

    difference_t and relation concern C_V/p_V-C_H/p_H, never raw C_V-C_H.
    The retained inputs are provenance assertions, not semantic verification.
    """

    hadamard: StaticCosts
    valid: StaticCosts
    success: ComparableSuccess
    stationary_attempts: bool
    hadamard_per_success: SuccessNormalizedCharge
    valid_per_success: SuccessNormalizedCharge
    valid_external_charge: LogicalCharge
    threshold: SuccessPreparationThreshold
    difference_t: Fraction | None
    relation: Literal["improvement", "tie", "loss", "unknown", "undefined"]
    unpriced: tuple[str, ...] = UNPRICED


def _normalize(charge: LogicalCharge, p: Fraction) -> SuccessNormalizedCharge:
    # charge is an expanded output, not a new bounded scalar input.
    if p == 0:
        return SuccessNormalizedCharge(charge, p, None, "undefined_zero_success")
    total = charge.total_t
    if total is None:
        return SuccessNormalizedCharge(charge, p, None, "unknown_cost")
    return SuccessNormalizedCharge(charge, p, total / p, "defined")


def success_normalized_threshold(
    hadamard: StaticCosts,
    valid: StaticCosts,
    *,
    success: ComparableSuccess,
    stationary_attempts: bool,
) -> SuccessThresholdComparison:
    """Solve the supplied static C/p equality, without choosing any inputs.

    Require ordinary constructed public input instances, R1 versus R2/R3,
    explicit comparable-event/renewal assertions, and literal True stationarity.
    Stationarity means the same supplied cost/probability law on every fresh
    independent attempt, including failed attempts. This is not a retry engine
    or a provenance/security validator for forged Python objects.
    """
    if type(hadamard) is not StaticCosts or type(valid) is not StaticCosts:
        raise ValueError("Threshold requires deterministic StaticCosts")
    if hadamard.regime != "R1" or valid.regime not in ("R2", "R3"):
        raise ValueError("Threshold requires R1 versus R2/R3")
    if type(success) is not ComparableSuccess:
        raise ValueError("Explicit ComparableSuccess is required")
    if stationary_attempts is not True:
        raise ValueError("Stationary fresh independent attempts must be explicit")

    ph = Fraction(success.hadamard_probability)
    pv = Fraction(success.valid_probability)
    h = _normalize(hadamard.charge, ph)
    v = _normalize(valid.charge, pv)
    # Preserve labels/multiplicities without constructing a bounded-input row
    # from its expanded external subtotal. At j=0, unknown O/S0 are unused.
    known = Fraction(0)
    unknown = []
    for label, value in (("O", valid.oracle_t), ("S0", valid.zero_reflection_t)):
        if valid.j and value is None:
            unknown.append((label, valid.j))
        elif value is not None:
            known += valid.j * value
    external = LogicalCharge(known, tuple(unknown))

    difference = None
    relation: Literal["improvement", "tie", "loss", "unknown", "undefined"]
    if ph == 0 or pv == 0:
        status: ThresholdStatus = (
            "undefined_zero_both_success"
            if ph == 0 and pv == 0
            else (
                "undefined_zero_hadamard_success"
                if ph == 0
                else "undefined_zero_valid_success"
            )
        )
        threshold = SuccessPreparationThreshold(None, None, "undefined", status)
        relation = "undefined"
    else:
        coefficient = (1 + 2 * valid.j) / pv
        hc, ev = h.charge.total_t, external.total_t
        limit = (
            None
            if hc is None or ev is None
            else (pv / ph * hc - ev) / (1 + 2 * valid.j)
        )
        boundary: Literal["negative", "zero", "positive", "unknown", "undefined"]
        boundary = "unknown"
        if limit is not None:
            boundary = "negative" if limit < 0 else "positive" if limit > 0 else "zero"
        threshold = SuccessPreparationThreshold(
            coefficient, limit, boundary, "unknown_cost" if limit is None else "defined"
        )
        if h.per_success_t is not None and v.per_success_t is not None:
            difference = v.per_success_t - h.per_success_t
        relation = (
            "unknown"
            if difference is None
            else (
                "improvement" if difference < 0 else "loss" if difference > 0 else "tie"
            )
        )
    return SuccessThresholdComparison(
        hadamard,
        valid,
        success,
        stationary_attempts,
        h,
        v,
        external,
        threshold,
        difference,
        relation,
    )

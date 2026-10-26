"""Exact supplied-cost preparation comparisons; no experiment or circuit execution.

For the unoptimized concatenation A, then j copies of O,A†,S0,A, logical
T/T† charge is C=(1+2j)A+j(O+S0). Inversion preserves the supplied A charge.
This is neither optimized T-count, static T-depth, total width nor physical
cost. H preparation has zero logical T but unpriced Clifford operations.

R1 and R2/R3 retain separate external domains, iteration counts and component
costs. No solution count, success probability, iteration choice, domain
equivalence or oracle correctness is inferred. Unknown charges remain symbolic.
The threshold for valid preparation is [C_H-j_V(O_V+S0_V)]/(1+2j_V).
Negative thresholds permit no nonnegative improvement or tie; at zero only
A_V=0 ties. At positive threshold A_V below/equal/above improves/ties/loses.
At j_V=0 the threshold is C_H and unused O/S0 contribute nothing.

The optional k=3 RUS summary delegates ONLY to the admitted analytical ledger,
under explicit ideal, uncontrolled scalar-Kraus instrument assumptions. Its
unlimited expectation, all-loops-completed conditional expectation and serial
stop-at-first-exhaustion expectation are separate quantities. No conditional
cost is compared directly with a deterministic successful program. For fresh
independent repeated attempts, renewal gives E[C]/P_completed, including aborted
costs; further conditional solution probability q gives E[C]/(P_completed*q).
This follows from R=E[C]+(1-P)R and does not require cost/event independence
within an attempt. Zero success is undefined, even for zero cost. Measurement,
reset, feed-forward and verification remain unpriced. No retry runtime, dynamic
execution, quantum control, static substitution or scientific advantage follows.

Only standard-library int/Fraction inputs are accepted, with explicit size
limits. There are no graph enumerations, iteration sweeps or quantum arrays.
"""

from dataclasses import dataclass
from fractions import Fraction
from typing import Literal, TYPE_CHECKING

if TYPE_CHECKING:
    from logique.benchmarks.rus_accounting import RusLedger

Cost = int | Fraction | None
Relation = Literal["improvement", "tie", "loss", "unknown"]
MAX_INPUT_BITS = 4096
MAX_ITERATIONS = 1_000_000
UNPRICED_STATIC = ("Clifford operations", "runtime", "physical QEC")


def _natural(name: str, value: int, maximum: int) -> int:
    if type(value) is not int or not 0 <= value <= maximum:
        raise ValueError(f"{name} must be an integer in [0, {maximum}]")
    return value


def _cost(name: str, value: Cost) -> Fraction | None:
    if value is None:
        return None
    if type(value) not in (int, Fraction):
        raise ValueError(f"{name} must be a nonnegative exact int/Fraction or None")
    # Check sizes before conversion/arithmetic; Fraction is already normalized.
    numerator = value if isinstance(value, int) else value.numerator
    denominator = 1 if isinstance(value, int) else value.denominator
    if (
        numerator < 0
        or max(numerator.bit_length(), denominator.bit_length()) > MAX_INPUT_BITS
    ):
        raise ValueError(
            f"{name} must be nonnegative and at most {MAX_INPUT_BITS} bits"
        )
    return Fraction(value)


def _probability(name: str, value: int | Fraction) -> Fraction:
    p = _cost(name, value)
    if p is None or p > 1:
        raise ValueError(f"{name} must be an exact probability in [0, 1]")
    return p


def _text(name: str, value: str) -> None:
    if not isinstance(value, str) or not value.strip() or len(value) > 4096:
        raise ValueError(f"{name} must be nonempty text of at most 4096 characters")


def _relation(difference: Fraction | None) -> Relation:
    if difference is None:
        return "unknown"
    return "improvement" if difference < 0 else "loss" if difference > 0 else "tie"


@dataclass(frozen=True)
class LogicalCharge:
    """Known subtotal plus unknown (component, multiplicity) terms.

    Fractional charges are supplied analytical quantities, not fractional
    emitted gates. Multiplicities describe the concatenation, without cancellation.
    """

    known_t: Fraction
    unknown_terms: tuple[tuple[str, int], ...]

    @property
    def total_t(self) -> Fraction | None:
        """Return None if any reached component is unpriced."""
        return None if self.unknown_terms else self.known_t


def _charge(terms: tuple[tuple[str, int, Fraction | None], ...]) -> LogicalCharge:
    known = Fraction(0)
    unknown = []
    for name, weight, value in terms:
        if weight and value is None:
            unknown.append((name, weight))
        elif value is not None:
            known += weight * value
    return LogicalCharge(known, tuple(unknown))


@dataclass(frozen=True)
class StaticCosts:
    """Explicit deterministic component charges at a supplied iteration count.

    domain is caller provenance, not a domain-equivalence certificate. R1 must
    explicitly supply A=0; R2/R3 may supply an unknown A. All cost arguments are
    required (None explicitly means unknown), even for unused j=0 O/S0.
    """

    regime: Literal["R1", "R2", "R3"]
    domain: str
    j: int
    preparation_t: Cost
    oracle_t: Cost
    zero_reflection_t: Cost

    def __post_init__(self) -> None:
        if self.regime not in ("R1", "R2", "R3"):
            raise ValueError("regime must be R1, R2 or R3")
        _text("domain", self.domain)
        _natural("j", self.j, MAX_ITERATIONS)
        for name in ("preparation_t", "oracle_t", "zero_reflection_t"):
            object.__setattr__(self, name, _cost(name, getattr(self, name)))
        if self.regime == "R1" and self.preparation_t != 0:
            raise ValueError("R1 H preparation must explicitly have zero logical T")

    @property
    def charge(self) -> LogicalCharge:
        """Retain exact known/unknown concatenated logical T charges."""
        return _charge(
            (
                ("A", 1 + 2 * self.j, _cost("preparation_t", self.preparation_t)),
                ("O", self.j, _cost("oracle_t", self.oracle_t)),
                ("S0", self.j, _cost("zero_reflection_t", self.zero_reflection_t)),
            )
        )


@dataclass(frozen=True)
class PreparationThreshold:
    """Exact equality threshold for A_V, independent of its supplied value.

    The valid-minus-H difference is coefficient*(A_V-limit_t). A negative
    limit has no feasible tie/improvement for A_V>=0; zero permits a zero-cost
    tie only. unknown means reached external costs prevent a numeric threshold.
    """

    coefficient: int
    limit_t: Fraction | None
    boundary: Literal["negative", "zero", "positive", "unknown"]


@dataclass(frozen=True)
class RenewalAssumptions:
    """Explicit assumptions for repeating independent analytical attempts.

    Each attempt uses fresh initialization, abort/reset after exhaustion or
    unsuccessful completion, and an external success verifier. Verification,
    measurement/reset/feed-forward and Clifford costs are unpriced. All four
    acknowledgements must be literal True; this class implements no repetition.
    """

    independent_attempts: bool
    fresh_initialization: bool
    abort_reset: bool
    unpriced_verification: bool

    def __post_init__(self) -> None:
        if any(value is not True for value in vars(self).values()):
            raise ValueError("All renewal assumptions must be explicitly True")


@dataclass(frozen=True)
class RenewalCost:
    """Unconditional attempt charge normalized by the named completion event.

    solution_t additionally includes supplied success conditional on completion.
    None is accompanied by an explicit reason; zero probability takes precedence
    over unknown cost. No conditional completed-cost input is derived here.
    """

    expected_attempt_t: Fraction | None
    completion_probability: Fraction
    solution_probability: Fraction | None
    completion_t: Fraction | None
    solution_t: Fraction | None
    completion_status: str
    solution_status: str
    assumptions: RenewalAssumptions


def _renewal(
    charge: Fraction | None,
    completion: Fraction,
    q: Fraction | None,
    assumptions: RenewalAssumptions,
) -> RenewalCost:
    if not isinstance(assumptions, RenewalAssumptions):
        raise ValueError("Explicit RenewalAssumptions are required")
    solution = None if q is None else completion * q

    def normalized(p: Fraction | None) -> tuple[Fraction | None, str]:
        if p is None:
            return None, "not_supplied"
        if p == 0:
            return None, "undefined_zero_success"
        if charge is None:
            return None, "unknown_cost"
        return charge / p, "defined"

    completion_t, completion_status = normalized(completion)
    solution_t, solution_status = normalized(solution)
    return RenewalCost(
        charge,
        completion,
        solution,
        completion_t,
        solution_t,
        completion_status,
        solution_status,
        assumptions,
    )


def renewal_cost(
    expected_attempt_t: Cost,
    completion_probability: int | Fraction,
    *,
    assumptions: RenewalAssumptions,
    solution_success_given_completion: Cost = None,
) -> RenewalCost:
    """Price renewal from unconditional E[C], never a success-conditional cost.

    Caller supplies the unconditional full attempt charge, including failures.
    q=None requests completion only. q=0 or P=0 makes solution cost undefined,
    including when E[C]=0. Expected values use the same exact cost input type
    as static charges but remain semantically separate.
    """
    q = (
        None
        if solution_success_given_completion is None
        else _probability(
            "solution_success_given_completion", solution_success_given_completion
        )
    )
    return _renewal(
        _cost("expected_attempt_t", expected_attempt_t),
        _probability("completion_probability", completion_probability),
        q,
        assumptions,
    )


@dataclass(frozen=True)
class ComparableSuccess:
    """Supplied probabilities for one explicitly comparable successful event.

    The caller asserts comparable event/verification semantics across domains
    via event and semantics text. Nothing here proves that assertion or infers
    probabilities from M/N. Independent fresh attempts are needed for C/p.
    """

    hadamard_probability: int | Fraction
    valid_probability: int | Fraction
    event: str
    semantics: str
    renewal_assumptions: RenewalAssumptions

    def __post_init__(self) -> None:
        _text("event", self.event)
        _text("semantics", self.semantics)
        if not isinstance(self.renewal_assumptions, RenewalAssumptions):
            raise ValueError("Explicit renewal assumptions are required")
        for name in ("hadamard_probability", "valid_probability"):
            object.__setattr__(self, name, _probability(name, getattr(self, name)))


@dataclass(frozen=True)
class PreparationComparison:
    """Cost-only comparison with optional explicitly comparable C/p results.

    No preparation advantage or achieved graph break-even is established.
    relation compares valid minus H logical T charges at their own supplied j.
    Threshold concerns C, not cost per solution. Unpriced operations remain.
    """

    hadamard: StaticCosts
    valid: StaticCosts
    threshold: PreparationThreshold
    difference_t: Fraction | None
    relation: Relation
    success: ComparableSuccess | None
    hadamard_per_success: RenewalCost | None
    valid_per_success: RenewalCost | None
    per_success_relation: Relation
    unpriced: tuple[str, ...] = UNPRICED_STATIC


def compare_preparations(
    hadamard: StaticCosts,
    valid: StaticCosts,
    *,
    success: ComparableSuccess | None = None,
) -> PreparationComparison:
    """Compare supplied R1 and R2/R3 charges, preserving separate j and domain.

    Solving (1+2j_V)A_V+j_V(O_V+S0_V) < C_H gives A_V < limit_t.
    All iteration counts are nonnegative, so the divisor is strictly positive,
    including at j_V=0. Unknown A_V does not prevent computing the threshold.
    No float probabilities, implicit same-j assumption or RUS rows are accepted.
    """
    if not isinstance(hadamard, StaticCosts) or not isinstance(valid, StaticCosts):
        raise ValueError("Comparison requires deterministic StaticCosts")
    if hadamard.regime != "R1" or valid.regime not in ("R2", "R3"):
        raise ValueError("Comparison requires R1 versus R2/R3")
    if success is not None and not isinstance(success, ComparableSuccess):
        raise ValueError("Success comparison requires ComparableSuccess")
    h, v = hadamard.charge.total_t, valid.charge.total_t
    external = _charge(
        (
            ("O", valid.j, _cost("oracle_t", valid.oracle_t)),
            ("S0", valid.j, _cost("zero_reflection_t", valid.zero_reflection_t)),
        )
    ).total_t
    coefficient = 1 + 2 * valid.j
    limit = None if h is None or external is None else (h - external) / coefficient
    boundary: Literal["negative", "zero", "positive", "unknown"] = "unknown"
    if limit is not None:
        boundary = "negative" if limit < 0 else "positive" if limit > 0 else "zero"
    difference = None if h is None or v is None else v - h
    hp = vp = None
    per_success_difference = None
    if success is not None:
        assumptions = success.renewal_assumptions
        hp = _renewal(
            h, Fraction(1), Fraction(success.hadamard_probability), assumptions
        )
        vp = _renewal(v, Fraction(1), Fraction(success.valid_probability), assumptions)
        if hp.solution_t is not None and vp.solution_t is not None:
            per_success_difference = vp.solution_t - hp.solution_t
    return PreparationComparison(
        hadamard,
        valid,
        PreparationThreshold(coefficient, limit, boundary),
        difference,
        _relation(difference),
        success,
        hp,
        vp,
        _relation(per_success_difference),
    )


@dataclass(frozen=True)
class RusLimits:
    """Caller ceilings checked before ledger exponentiation; no rows generated.

    Hard maxima n/j/cap<=64, L<=4096 and growth budget<=4096 keep this optional
    scalar slice bounded. Finite-cap power-size estimate 2c(L+2n+2)+32 must
    fit max_exponent_bits. This conservatively bounds principal power sizes,
    not every rational intermediate or OS RSS. Costs have separate bit limits.
    """

    max_n: int
    max_j: int
    max_cap: int
    max_exponent_bits: int

    def __post_init__(self) -> None:
        for name in ("max_n", "max_j", "max_cap"):
            _natural(name, getattr(self, name), 64)
        _natural("max_exponent_bits", self.max_exponent_bits, 4096)


@dataclass(frozen=True)
class RusCostSummary:
    """Separate expected costs from an ideal, uncontrolled k=3 instrument.

    conditional_completed_t is diagnostic only: it omits aborted attempts.
    renewal (if requested) uses unconditional_stop_t. ledger contains exhaustion
    and unpriced measurement/reset/feed-forward details, not total width/depth.
    """

    ledger: "RusLedger"
    unlimited_expected_t: Fraction | None
    conditional_completed_t: Fraction | None
    unconditional_stop_t: Fraction | None
    exhaustion_probability: Fraction
    renewal: RenewalCost | None


def rus_cost_summary(
    n: int,
    j: int,
    *,
    k: int,
    cap: int | None,
    limits: RusLimits,
    ideal_instrument_assumptions: bool,
    oracle_t: Cost,
    zero_reflection_t: Cost,
    renewal_assumptions: RenewalAssumptions | None = None,
    solution_success_given_completion: Cost = None,
) -> RusCostSummary:
    """Delegate to analytical_ledger after explicit assumptions and bounds.

    True acknowledges the admitted k=3 arbitrary-input scalar-Kraus ideal
    gates, fresh zero trial ancillas, noiseless measurement/reset/feed-forward,
    completion before progress, actual inverse prefix and no quantum control.
    O/S0 costs and their ideal clean semantics remain caller obligations.
    Nothing is executed or substituted into the static compiler. A supplied
    solution probability requires separate renewal assumptions.
    """
    if type(k) is not int or k != 3:
        raise ValueError("Explicit k=3 is required")
    if ideal_instrument_assumptions is not True:
        raise ValueError("Explicit ideal-instrument assumptions are required")
    if not isinstance(limits, RusLimits):
        raise ValueError("Explicit RusLimits are required")
    _natural("n", n, limits.max_n)
    _natural("j", j, limits.max_j)
    if cap is not None:
        _natural("cap", cap, limits.max_cap)
    loops = n * (1 + 2 * j)
    if loops > 4096:
        raise ValueError("At most 4096 analytical loops are supported")
    growth = 32 if cap is None else 2 * cap * (loops + 2 * n + 2) + 32
    if growth > limits.max_exponent_bits:
        raise ValueError("Exact-power growth exceeds caller budget")
    o, z = _cost("oracle_t", oracle_t), _cost("zero_reflection_t", zero_reflection_t)
    q = (
        None
        if solution_success_given_completion is None
        else _probability(
            "solution_success_given_completion", solution_success_given_completion
        )
    )
    if q is not None and renewal_assumptions is None:
        raise ValueError("Solution normalization requires renewal assumptions")
    if renewal_assumptions is not None and not isinstance(
        renewal_assumptions, RenewalAssumptions
    ):
        raise ValueError("Explicit RenewalAssumptions are required")
    from logique.benchmarks.rus_accounting import analytical_ledger

    ledger = analytical_ledger(n, j, k=k, cap=cap, oracle_t=o, zero_reflection_t=z)
    completion = 1 - ledger.program_failure_probability
    renewal = (
        None
        if renewal_assumptions is None
        else _renewal(ledger.stop_expected_total_t, completion, q, renewal_assumptions)
    )
    return RusCostSummary(
        ledger,
        ledger.unbounded_expected_total_t,
        ledger.success_expected_total_t,
        ledger.stop_expected_total_t,
        ledger.program_failure_probability,
        renewal,
    )

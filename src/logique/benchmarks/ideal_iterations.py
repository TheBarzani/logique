"""Bounded scalar analytical references; no circuit or noise execution.

Assume exact uniform preparation A on a declared support, a clean phase oracle
O marking precisely M of N support words, and D=A(2|0><0|-I)A†. Physical
lowering, signed S0, actual inverse, wire mapping and workspace restoration are
caller obligations. R3 matches coloring only on valid-code support. These
formulae certify neither approximate preparation amplitudes nor saved QPY.
"""

from dataclasses import dataclass
from fractions import Fraction
from itertools import product
import math
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from logique.coloring.model import ColoringProblem


UNAVAILABLE = (
    "leakage",
    "noise",
    "confidence_intervals",
    "routing",
    "actual_circuit_resources",
    "t_depth",
)
ASSUMPTIONS = (
    "Exact uniform A on declared support; clean O marks precisely M words; "
    "D=A(2|0><0|-I)A†; actual inverse, signed S0, mapping and restoring "
    "lowering required. No approximate-amplitude or saved-QPY certification."
)


def _integer(value: int, name: str, minimum: int = 0) -> int:
    if type(value) is not int or value < minimum:
        raise ValueError(f"{name} must be an integer >= {minimum}, excluding bool")
    return value


def _finite_cost(value: float, name: str) -> float:
    if type(value) not in (int, float):
        raise ValueError(f"{name} must be a finite nonnegative number")
    try:
        result = float(value)
    except OverflowError as exc:
        raise ValueError(f"{name} is outside finite float range") from exc
    if not math.isfinite(result) or result < 0:
        raise ValueError(f"{name} must be a finite nonnegative number")
    return result


def _fraction(marked: int, support: int) -> float:
    _integer(support, "support", 1)
    _integer(marked, "marked")
    if marked > support:
        raise ValueError("marked must not exceed support")
    p = marked / support
    if 0 < marked < support and not 0 < p < 1:
        raise ValueError("solution fraction rounds to a float boundary")
    return p


def _exact_first_peak(
    marked: int, support: int, max_iterations: int
) -> tuple[tuple[int, int], int]:
    """Bracket x using exact polynomial signs, with at most 128 scalar steps.

    Write theta=asin(sqrt(M/N)), t=cos(2theta)=1-2M/N. The recurrences
    v_0=1, v_1=2t-1 and v_j=2t*v_(j-1)-v_(j-2) give
    v_j=cos((2j+1)theta)/cos(theta). Stop at the FIRST nonpositive v_j.
    All preceding odd angles are below pi/2; the crossing angle is below
    3pi/2 since 0<2theta<pi. Thus zero means x=j exactly, otherwise
    j-1<x<j. No later oscillation can masquerade as the first crossing.

    Also c_j=T_j(t)=cos(2j*theta). In this bracket 2j*theta lies strictly
    between 0 and pi, so c_j's sign decides x versus j-1/2: positive
    chooses j, negative chooses j-1, and exact zero chooses j-1 (tie).
    Fraction signs resolve every boundary, including irrational roots in p;
    there is no floating-point uncertainty or probability tolerance here.
    The count cap imposed by the caller and degree cap bound integer sizes.
    """
    t = 1 - 2 * Fraction(marked, support)
    previous_v, v = Fraction(1), 2 * t - 1
    previous_c, c = Fraction(1), t
    for j in range(1, min(128, max_iterations) + 1):
        if j > 1:
            previous_v, v = v, 2 * t * v - previous_v
            previous_c, c = c, 2 * t * c - previous_c
        if v <= 0:
            if v == 0:
                return (j, j), j
            return (j - 1, j), j if c > 0 else j - 1
    raise ValueError("First-peak bracket unresolved within 128-step/iteration cap")


@dataclass(frozen=True)
class InvocationCosts:
    """Supplied additive scalar costs in one unit; never a T-depth model.

    A and its actual inverse have the same supplied cost. Values are caller
    inputs, not measured circuit resources. Measurement/check/reset costs are
    excluded unless explicitly included by the caller in the stated basis.
    """

    preparation: float
    oracle: float
    zero_reflection: float
    basis: str

    def __post_init__(self) -> None:
        for name in ("preparation", "oracle", "zero_reflection"):
            object.__setattr__(self, name, _finite_cost(getattr(self, name), name))
        if not isinstance(self.basis, str) or not self.basis.strip():
            raise ValueError("An explicit additive cost basis is required")
        if "depth" in self.basis.lower():
            raise ValueError("Depth requires circuit dependencies, not additive costs")

    def program_cost(self, iterations: int) -> float:
        """Charge A once plus j*(2A+O+S0); fail on finite-range overflow."""
        _integer(iterations, "iterations")
        try:
            cost = self.preparation
            if iterations:
                cost += iterations * (
                    2 * self.preparation + self.oracle + self.zero_reflection
                )
        except OverflowError as exc:
            raise ValueError("Program cost overflow") from exc
        if not math.isfinite(cost):
            raise ValueError("Program cost overflow")
        return cost


def _repeat_cost(cost: float | None, p: float) -> tuple[float | None, str]:
    if p == 0:
        return None, "infinite_expected_runs; cost_per_success_undefined"
    if cost is None:
        return None, "unavailable_cost"
    result = cost / p
    if not math.isfinite(result):
        return None, "infinite_float_cost"
    return result, "C/P_for_independent_identical_program_runs"


@dataclass(frozen=True)
class IterationRow:
    """One analytical ideal row; repeated cost assumes independent program runs."""

    iterations: int
    analytical_success_probability: float
    supplied_program_cost: float | None
    expected_cost_per_success: float | None
    repeated_cost_status: str


@dataclass(frozen=True)
class IdealLedger:
    """First-peak ledger with unavailable physical quantities left unpriced."""

    marked: int
    support: int
    analytical_initial_probability: float
    first_peak_candidates: tuple[int, int]
    first_peak_iteration: int
    rows: tuple[IterationRow, ...]
    cost_basis: str | None
    boundary_convention: str
    probability_kind: str = "analytical_ideal_uniform_support_not_simulation"
    assumptions: str = ASSUMPTIONS
    unavailable: tuple[str, ...] = UNAVAILABLE


def ideal_iteration_ledger(
    marked: int,
    support: int,
    *,
    max_rows: int,
    max_iterations: int,
    costs: InvocationCosts | None = None,
) -> IdealLedger:
    """Return j=0 through first peak +1 for explicitly known M and N.

    For 0<p<1 let x=pi/(4 asin(sqrt(p)))-1/2. The first-peak candidates
    are floor(x), ceil(x), clamped at zero. Choose the nearest integer to x;
    exact half-integer ties choose fewer iterations. Categorical decisions
    use exact rational polynomial signs of M/N, never rounded p or theta.
    This is the first lobe, not a global optimization over later oscillations.
    M=0 or M=N uses peak=0 and rows j=0,1 with exact probabilities 0 or 1.
    Caps are mandatory finite integers and checked before allocating any rows.
    Unknown M rejects; it is never replaced by one or an estimated fraction.

    Bounded input contract: N.bit_length()<=64, representable interior float
    fraction, and ceil(x)<=128. Larger counts or an unresolved first bracket
    reject BEFORE row allocation, even with larger caller caps. This covers
    every known count on <=12-bit graph support (x<50). At most 128 exact
    degree-128 recurrence steps use O(128*64)-bit integers, independent of caps.
    Probabilities/costs remain approximate binary64 analytical values; they
    do not decide ties, candidates, extent or admission. No interval or ideal
    preparation-amplitude certificate is supplied.
    """
    _integer(max_rows, "max_rows", 1)
    _integer(max_iterations, "max_iterations")
    if costs is not None and not isinstance(costs, InvocationCosts):
        raise ValueError("costs must be InvocationCosts or None")
    _integer(support, "support", 1)
    _integer(marked, "marked")
    if support.bit_length() > 64:
        raise ValueError("Count cap requires support.bit_length() <= 64")
    p = _fraction(marked, support)
    if marked in (0, support):
        candidates = (0, 0)
        peak = 0
        convention = "constant_probability; peak=0; include_j=1"
        theta = 0.0
    else:
        candidates, peak = _exact_first_peak(marked, support, max_iterations)
        theta = math.asin(math.sqrt(p))
        convention = "nearest_first_lobe_peak; exact_ties_choose_fewer"
    last = peak + 1
    if last > max_iterations or last + 1 > max_rows:
        raise ValueError("First-peak sweep exceeds row/iteration cap")
    rows = []
    for j in range(last + 1):
        probability = (
            p if marked in (0, support) else math.sin((2 * j + 1) * theta) ** 2
        )
        # Exact rational-angle cases avoid a spurious finite C/P at sin(pi).
        if 2 * marked == support:
            probability = 0.5
        elif 4 * marked == 3 * support and j % 3 == 1:
            probability = 0.0
        elif 4 * marked == support and j % 3 == 1:
            probability = 1.0
        cost = None if costs is None else costs.program_cost(j)
        repeated, status = _repeat_cost(cost, probability)
        rows.append(IterationRow(j, probability, cost, repeated, status))
    return IdealLedger(
        marked,
        support,
        p,
        candidates,
        peak,
        tuple(rows),
        None if costs is None else costs.basis,
        convention,
    )


@dataclass(frozen=True)
class RandomSamplingReference:
    """Independent uniform trials; a trial is not a Grover iteration."""

    marked: int
    support: int
    trials: int
    analytical_success_probability: float
    supplied_trial_cost: float | None
    supplied_total_cost: float | None
    cost_basis: str
    probability_kind: str = "analytical_independent_uniform_random_trials"


def random_sampling_reference(
    marked: int,
    support: int,
    *,
    trials: int,
    trial_cost: float | None = None,
    cost_basis: str,
) -> RandomSamplingReference:
    """Compute 1-(1-M/N)**r; explicitly price each independent uniform trial."""
    _integer(trials, "trials")
    p = _fraction(marked, support)
    if not isinstance(cost_basis, str) or not cost_basis.strip():
        raise ValueError("State random trial cost basis, even if unpriced")
    if "depth" in cost_basis.lower():
        raise ValueError("Depth requires circuit dependencies, not additive costs")
    cost = None if trial_cost is None else _finite_cost(trial_cost, "trial_cost")
    total = None
    if cost is not None:
        try:
            total = trials * cost
        except OverflowError as exc:
            raise ValueError("Random total cost overflow") from exc
        if not math.isfinite(total):
            raise ValueError("Random total cost overflow")
    if trials == 0 or p == 0:
        success = 0.0
    elif p == 1:
        success = 1.0
    else:
        try:
            exponent = trials * math.log1p(-p)
        except OverflowError as exc:
            raise ValueError("Random trial count exceeds float range") from exc
        success = -math.expm1(exponent)
    return RandomSamplingReference(
        marked, support, trials, success, cost, total, cost_basis
    )


@dataclass(frozen=True)
class CountedColoringSupport:
    """Exhaustive integer-predicate coverage on the declared bounded support.

    Witness tuples follow sorted vertex order. None means that class is absent
    on this support, not that it was sampled and missed. R2/R3 contain no unused
    codes; R1 negatives include both unused-code and edge-violation categories.
    """

    regime: str
    vertices: tuple[int, ...]
    colors: int
    data_bits: int
    support: int
    marked: int
    rejected: int
    invalid_code_count: int
    edge_violation_count: int
    positive_witness: tuple[int, ...] | None
    negative_witness: tuple[int, ...] | None
    invalid_code_witness: tuple[int, ...] | None
    edge_violation_witness: tuple[int, ...] | None
    coverage: str = "exhaustive_explicit_integer_predicate; <=12_data_bits"


def count_coloring_support(
    problem: "ColoringProblem", *, regime: str
) -> CountedColoringSupport:
    """Count known M independently of encoding/synthesis; reject >12 bits first.

    Unprecolored instances only. c=max(1,(k-1).bit_length()) matches the
    maintained one-color binary convention. R1: N=2**(c*|V|), complete
    predicate. R2/R3: N=k**|V|, exact uniform valid-code support. R3's edge-only
    oracle is coloring-equivalent only on that support. No quantum arrays.
    """
    if regime not in ("R1", "R2", "R3"):
        raise ValueError("regime must be R1, R2 or R3")
    _integer(problem.colors, "colors", 1)
    if problem.precolored:
        raise ValueError("Precolored instances are outside this reference")
    vertices = tuple(problem.vertices)
    if any(type(v) is not int for v in vertices) or len(set(vertices)) != len(vertices):
        raise ValueError("Vertices must be distinct integer labels")
    if vertices != tuple(sorted(vertices)):
        raise ValueError("Vertices must be sorted")
    bits = max(1, (problem.colors - 1).bit_length()) * len(vertices)
    if bits > 12:
        raise ValueError("Enumeration exceeds 12 data bits; rejected before work")
    positions = {v: i for i, v in enumerate(vertices)}
    edges = tuple(problem.edges)
    if any(
        len(e) != 2 or any(type(v) is not int or v not in positions for v in e)
        for e in edges
    ):
        raise ValueError("Edges must connect declared vertices")
    indexed_edges = tuple((positions[u], positions[v]) for u, v in edges)
    palette = 1 << max(1, (problem.colors - 1).bit_length())
    if regime != "R1":
        palette = problem.colors
    if not vertices:
        palette = 1
    support = palette ** len(vertices)
    marked = invalid = violations = 0
    positive = negative = invalid_witness = edge_witness = None
    for word in product(range(palette), repeat=len(vertices)):
        valid_codes = all(color < problem.colors for color in word)
        proper_edges = all(word[u] != word[v] for u, v in indexed_edges)
        if valid_codes and proper_edges:
            marked += 1
            if positive is None:
                positive = word
        else:
            if negative is None:
                negative = word
        if not valid_codes:
            invalid += 1
            if invalid_witness is None:
                invalid_witness = word
        if valid_codes and not proper_edges:
            violations += 1
            if edge_witness is None:
                edge_witness = word
    return CountedColoringSupport(
        regime,
        vertices,
        problem.colors,
        bits,
        support,
        marked,
        support - marked,
        invalid,
        violations,
        positive,
        negative,
        invalid_witness,
        edge_witness,
    )

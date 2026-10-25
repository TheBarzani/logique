"""Exact analytical accounting for one specific k=3 RUS construction.

This module imports only the standard library. It executes no circuit and is
separate from the static FT compiler and its admission contract.

Provenance: Paetznick and Svore, arXiv:1311.1074v2, section 5 / figure 8,
https://arxiv.org/html/1311.1074v2#S5.F8, supplies the two-T, one-ancilla
primitive U=(I+i*sqrt(2)*X)/sqrt(3). The vertex extension and inverse below
are LOCAL derivations recorded in docs/research/task6_critical_review.md,
not a literature claim of 14/3 T per coloring vertex.

The trial, in time order, is H(a), T(a), CX(a,h), H(a), CX(a,h), T(a), H(a).
With a initially zero and measured in Z, its phase-sensitive Kraus operators
are K0=alpha*U, K1=beta*I, alpha=exp(-i*pi/4)*sqrt(3)/2,
beta=exp(i*pi/4)/2. Thus K0†K0=3I/4 and K1†K1=I/4, on arbitrary data
including an entangled reference. A first success on attempt r has operator
beta**(r-1)*alpha*U. These scalar branches justify independent geometric
attempt counts in this IDEAL analytical model, even between coherent data
operations. No state-dependent success model is supported.

An algebraic check, keeping t=(1+i)/sqrt(2), gives the ancilla-zero block
[(1-t²)I+2tX]/(2sqrt(2)) and the ancilla-one block
[(1+t²)I]/(2sqrt(2)). Substitution yields exactly K0 and K1 above.
Completeness and input-independent branch probabilities follow as operator
identities, rather than from preparing a single test state.

For vertex bits |h l> (l is the least significant bit), time order U(h),
S†(h), CH(h,l), X(h) defines V=E*U(h), E=X(h)*CH(h,l)*S†(h).
It maps |00> to (|00>+|01>+|10>)/sqrt(3). CH costs two T/T† gates:
H=Ry(pi/4)*Z*Ry(-pi/4), and Ry(pi/4) is a Clifford conjugate of T
up to scalar phase; the two conjugate factors' phases cancel in CH.
The arbitrary-input inverse is U†(h)*E†, with U†=ZUZ. First apply
X(h), CH(h,l), S(h), then complete a fresh ZUZ retry loop. Each failure
inside that loop is scalar identity AFTER E†; do not reapply E† on retry.
Its successful operator is alpha*V†, not an inverted measurement path.
The product of successful forward/inverse branches is a scalar identity;
discarding the classical record gives the inverse DATA CHANNEL. Branch
phases are retained here; quantum control of this instrument is unsupported.

Only logical T/T† counts are priced. Measurement, reset/repreparation,
classical feed-forward, Clifford gates, runtime, and physical QEC are unpriced.
No static T-depth, optimal iteration choice, graph cost, break-even, dynamic
implementation, or RUS/paper admission follows from this ledger.
"""

from dataclasses import dataclass
from fractions import Fraction
from typing import Literal


SUCCESS = Fraction(3, 4)
FAILURE = Fraction(1, 4)
TRIAL_T = 2
EXTENSION_T = 2
UNPRICED = (
    "measurement",
    "reset/repreparation",
    "classical feed-forward",
    "Clifford gates",
    "runtime",
    "physical QEC",
)


def _natural(name: str, value: int) -> None:
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise ValueError(f"{name} must be a nonnegative integer")


def _exact_cost(name: str, value: int | Fraction | None) -> Fraction | None:
    if value is None:
        return None
    if isinstance(value, bool) or not isinstance(value, (int, Fraction)) or value < 0:
        raise ValueError(f"{name} must be a nonnegative int or Fraction, or None")
    return Fraction(value)


def _geometric_sum(ratio: Fraction, terms: int) -> Fraction:
    """Sum ratio**i for i in range(terms), without enumerating invocations."""
    return Fraction(terms) if ratio == 1 else (1 - ratio**terms) / (1 - ratio)


@dataclass(frozen=True)
class RetryMoments:
    """Attempts in a single reached loop; cap=0 means immediate exhaustion.

    Unconditional moments describe M=min(N,cap), including the exhausted
    branch; N is geometric on {1,2,...}. Conditional moments describe
    N given N<=cap, and are None if that event is impossible. T moments price
    only the two-T trial, excluding the vertex's deterministic extension.
    Each attempted trial has one measurement; its count equals attempts,
    while its cost and reset/repreparation/feed-forward costs stay unpriced.
    """

    cap: int | None
    success_probability: Fraction
    failure_probability: Fraction
    expected_attempts: Fraction
    variance_attempts: Fraction
    expected_trial_t: Fraction
    variance_trial_t: Fraction
    expected_attempts_given_success: Fraction | None
    variance_attempts_given_success: Fraction | None


def retry_moments(cap: int | None = None) -> RetryMoments:
    """Return exact geometric or truncated-geometric moments for this trial.

    For finite c, E[M]=sum(q**r,r=0..c-1) and
    E[M²]=sum((2r+1)*q**r,r=0..c-1). Remove c*q**c and c²*q**c
    respectively before dividing by 1-q**c for success conditioning.
    Unlimited retries terminate almost surely but have no finite worst case.
    """
    if cap is not None:
        _natural("cap", cap)
    tail = Fraction(0) if cap is None else FAILURE**cap
    success = 1 - tail
    mean = success / SUCCESS
    second = (1 + FAILURE) / SUCCESS**2
    if cap is not None:
        second -= tail * (2 * cap * SUCCESS + 1 + FAILURE) / SUCCESS**2
    variance = second - mean**2
    conditional_mean = None
    conditional_variance = None
    if success:
        conditional_mean = (mean - (cap or 0) * tail) / success
        conditional_second = (second - (cap or 0) ** 2 * tail) / success
        conditional_variance = conditional_second - conditional_mean**2
    return RetryMoments(
        cap,
        success,
        tail,
        mean,
        variance,
        TRIAL_T * mean,
        TRIAL_T**2 * variance,
        conditional_mean,
        conditional_variance,
    )


@dataclass(frozen=True)
class RusLedger:
    """Logical analytical charges, with cost conventions in analytical_ledger.

    A missing total T value means O/S0 charges were not both supplied when
    used. Vertex-only charges remain available. Ancillas count retry ancillas
    only; data_qubits excludes all unknown O/S0 workspace. Parallel means
    one retry ancilla per vertex, reused across sequential A/A† blocks; it
    makes no depth/runtime promise. Stop costs always use the serial schedule.
    """

    n: int
    j: int
    cap: int | None
    retry_ancilla_policy: Literal["shared", "parallel"]
    retry_ancillas: int
    data_qubits: int
    forward_vertex_invocations: int
    inverse_vertex_invocations: int
    unitary_invocations: int
    oracle_invocations: int
    zero_reflection_invocations: int
    loop: RetryMoments
    program_failure_probability: Fraction
    program_failure_union_bound: Fraction
    unbounded_expected_attempts: Fraction
    unbounded_variance_attempts: Fraction
    unbounded_expected_vertex_t: Fraction
    unbounded_variance_vertex_t: Fraction
    unbounded_expected_total_t: Fraction | None
    stop_expected_attempts: Fraction
    stop_expected_vertex_t: Fraction
    stop_expected_total_t: Fraction | None
    success_expected_attempts: Fraction | None
    success_variance_attempts: Fraction | None
    success_expected_vertex_t: Fraction | None
    success_variance_vertex_t: Fraction | None
    success_expected_total_t: Fraction | None
    capped_attempts_upper_bound: int | None
    capped_vertex_t_upper_bound: int | None
    unpriced: tuple[str, ...] = UNPRICED


def analytical_ledger(
    n: int,
    j: int,
    *,
    cap: int | None = None,
    k: int = 3,
    retry_ancillas: Literal["shared", "parallel"] = "shared",
    oracle_t: int | Fraction | None = None,
    zero_reflection_t: int | Fraction | None = None,
) -> RusLedger:
    """Account for n vertices, initialization once, then j O,A†,S0,A blocks.

    There are L=n*(1+2j) vertex-unitary retry loops. In the ideal scalar-Kraus
    model, capped program exhaustion probability is exactly
    1-(1-4**(-cap))**L, bounded by min(1,L*4**(-cap)). This is a retry
    exhaustion event, NOT coloring/search failure or an approximation error.
    Empty n=0 has no loops and zero exhaustion, even when cap=0; O/S0 still
    appear j times symbolically. This is accounting, not an executable search.

    unbounded_* means unlimited retries, unconditional almost-sure completion.
    success_* conditions on ALL capped loops succeeding. stop_* is an
    UNCONDITIONAL expectation including aborted runs, stopping at the first
    exhausted loop. Within each block vertices are processed in order. Forward
    extensions follow successful loops; inverse extensions precede their loops
    and are charged even when that loop exhausts (also at cap=0).

    For stop costs, O at iteration r is reached with probability s**(n*(1+2r))
    and S0 with s**(n*(2+2r)), where s=1-4**(-cap). Supplied O/S0 charges
    are exact external deterministic counts; None means unknown, not zero.
    They do not establish oracle correctness or graph costs. No optimization
    over j or cross-vertex gate cancellation is assumed. The finite capped
    upper bounds are conservative logical counts, never static T-depth.
    """
    _natural("n", n)
    _natural("j", j)
    _natural("k", k)
    if k != 3:
        raise NotImplementedError(
            "Only the reviewed k=3 vertex construction is supported"
        )
    if retry_ancillas not in ("shared", "parallel"):
        raise ValueError("retry_ancillas must be 'shared' or 'parallel'")
    o = _exact_cost("oracle_t", oracle_t)
    z = _exact_cost("zero_reflection_t", zero_reflection_t)
    loop = retry_moments(cap)
    unlimited = retry_moments()
    forward, inverse = n * (1 + j), n * j
    total = forward + inverse
    s = loop.success_probability
    completion = s**total
    reached = _geometric_sum(s, total)
    rounds = _geometric_sum(s ** (2 * n), j)
    block = _geometric_sum(s, n)
    forward_reached = block * (1 + s ** (2 * n) * rounds)
    inverse_reached = block * s**n * rounds
    stop_attempts = reached * loop.expected_attempts
    stop_t = TRIAL_T * stop_attempts + EXTENSION_T * (
        s * forward_reached + inverse_reached
    )
    unbounded_t = total * (unlimited.expected_trial_t + EXTENSION_T)
    success_attempts = success_variance = success_t = success_t_variance = None
    if completion:
        # completion>0 implies a nonempty loop can succeed; empty sums are zero.
        success_attempts = total * (loop.expected_attempts_given_success or Fraction(0))
        success_variance = total * (loop.variance_attempts_given_success or Fraction(0))
        success_t = TRIAL_T * success_attempts + EXTENSION_T * total
        success_t_variance = TRIAL_T**2 * success_variance

    def with_external(
        vertex_t: Fraction | None, o_weight: Fraction, z_weight: Fraction
    ) -> Fraction | None:
        if vertex_t is None or (o is None and o_weight) or (z is None and z_weight):
            return None
        return vertex_t + (o or 0) * o_weight + (z or 0) * z_weight

    return RusLedger(
        n=n,
        j=j,
        cap=cap,
        retry_ancilla_policy=retry_ancillas,
        retry_ancillas=(int(n > 0) if retry_ancillas == "shared" else n),
        data_qubits=2 * n,
        forward_vertex_invocations=forward,
        inverse_vertex_invocations=inverse,
        unitary_invocations=total,
        oracle_invocations=j,
        zero_reflection_invocations=j,
        loop=loop,
        program_failure_probability=1 - completion,
        program_failure_union_bound=min(Fraction(1), total * loop.failure_probability),
        unbounded_expected_attempts=total * unlimited.expected_attempts,
        unbounded_variance_attempts=total * unlimited.variance_attempts,
        unbounded_expected_vertex_t=unbounded_t,
        unbounded_variance_vertex_t=total * unlimited.variance_trial_t,
        unbounded_expected_total_t=with_external(unbounded_t, Fraction(j), Fraction(j)),
        stop_expected_attempts=stop_attempts,
        stop_expected_vertex_t=stop_t,
        stop_expected_total_t=with_external(
            stop_t, s**n * rounds, s ** (2 * n) * rounds
        ),
        success_expected_attempts=success_attempts,
        success_variance_attempts=success_variance,
        success_expected_vertex_t=success_t,
        success_variance_vertex_t=success_t_variance,
        success_expected_total_t=with_external(success_t, Fraction(j), Fraction(j)),
        capped_attempts_upper_bound=(
            0 if not total else None if cap is None else total * cap
        ),
        capped_vertex_t_upper_bound=(
            0
            if not total
            else None if cap is None else total * (TRIAL_T * cap + EXTENSION_T)
        ),
    )

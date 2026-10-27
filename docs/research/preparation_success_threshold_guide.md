# Calling the analytical static preparation success threshold

`success_normalized_threshold` compares supplied deterministic static logical
T/T-dagger charges per occurrence of one comparable successful event. It solves
an exact scalar equality; it does not establish an achieved graph break-even.
The binding scope and exact admitted bytes are in the
[coordinator admission](preparation_success_threshold_admission.md) and
[independent review](preparation_success_threshold_review.md). This guide adds
documentation only. Independent review and coordinator admission of the guide
are separate steps. **The full paper remains unfinished.**

## Supply the accounting model explicitly

Construct ordinary `StaticCosts` rows from
`logique.benchmarks.preparation_breakeven`: one R1 row and one R2 or R3 row.
Each needs its own `domain`, `j`, `preparation_t`, `oracle_t` and
`zero_reflection_t`. R1 means Hadamard preparation with the complete predicate
and must explicitly supply `preparation_t=0` logical T; its Clifford operations
still have unpriced cost. R2 denotes valid-color preparation with the complete
predicate; R3 denotes valid-color preparation with domain checks removed.
Separate rows may have unequal j and different component costs and domains.
No equality between them is implicit.

Supply nonnegative exact built-in `int` or `fractions.Fraction` costs. `None`
explicitly means an unknown cost, including when the component is unused.
Fractional charges are analytical inputs, not fractional emitted gates.
Supply exact probabilities for the named event at each row's supplied j;
probabilities cannot be `None`. No domain size, solution count, probability,
iteration selection, peak or sweep is inferred. Missing evidence for a
probability cannot be replaced by zero.

The static charge counts the unoptimized time-ordered concatenation

```text
A, then j copies of (O, A-inverse, S0, A)
C = (1+2j) A + j(O+S0).
```

The inverse has the same supplied logical T/T-dagger charge as A. Initialization
is charged once even at j=0. This is the full deterministic unconditional charge
of each attempt, including an attempt whose final event fails. It is not a
success-conditioned charge, optimized lower bound, emitted-circuit measurement,
T-depth, workspace count, runtime or physical resource estimate.

Construct `ComparableSuccess` with `hadamard_probability`, `valid_probability`,
nonempty `event` text, nonempty `semantics` text explaining comparable external
verification across both domains, and explicit `RenewalAssumptions`. The latter
requires four literal `True` acknowledgements:

- `independent_attempts`: future attempts are independent of past attempts.
- `fresh_initialization`: each attempt starts afresh.
- `abort_reset`: unsuccessful attempts are discarded/reset before a fresh one.
- `unpriced_verification`: external verification is acknowledged and unpriced.

Also pass literal `stationary_attempts=True` to the threshold function: every
fresh attempt has the same supplied cost/probability law. Under these assumptions,
conditioning on the first attempt gives `R=C+(1-p)R`, hence `R=C/p` for p>0.
Failed attempts incur C too. This identity implements no repeated attempts.
Text and acknowledgements assert the model; they do not verify cost provenance,
event equivalence, stationarity or independence.

## Read the threshold and statuses

For positive supplied `p_H,p_V`, let `C_H` be the R1 charge and put

```text
D = 1+2j_V > 0,          E = j_V(O_V+S0_V),
p_H(D A_V+E) = p_V C_H,
B = (p_V C_H-p_H E)/(p_H D),
Delta = C_V/p_V-C_H/p_H = (D/p_V)(A_V-B).
```

Cross multiplication uses only positive denominators. `threshold.limit_t` is B;
`threshold.coefficient` is the positive slope D/p_V. `difference_t` is Delta,
and `relation` is `improvement`, `tie` or `loss` according to its exact sign.
These concern valid-minus-H charge per the declared event. The older
`compare_preparations(...).threshold` concerns raw C and remains unchanged.
Equal positive probabilities recover its boundary `(C_H-E)/D`; Delta is the
raw difference divided by that common probability.

| Boundary B | Consequence for nonnegative supplied A_V at fixed probabilities |
| --- | --- |
| negative | Every A_V loses; no feasible tie or strict improvement. |
| zero | A_V=0 ties; every positive A_V loses. |
| positive | A_V below/at/above B improves/ties/loses. |
| unknown | Reached unknown H or valid external costs prevent numeric B. |
| undefined | At least one probability is zero; no threshold comparison. |

Hypothetical variation of A_V in this algebra holds both supplied probabilities,
j values and other charges fixed. It says nothing about how an actual change to
preparation would affect its success probability or whether an implementation
attaining B exists. It supplies no cost/probability trade-off inference.

Unknown A_V can coexist with a defined B; the actual comparison then remains
`unknown`, with `difference_t=None`. Reached unknown components retain their
labels and multiplicities, alongside a known subtotal. Identical labels in two
rows neither assert equal unknown values nor cancel. At j=0, unknown O/S0 have
zero weight and contribute nothing; invalid supplied values still reject.

Each method's `hadamard_per_success` or `valid_per_success` reports its own
`status` and `per_success_t`. Positive p with known C is `defined`, including
C=0; positive p with unknown C is `unknown_cost`. Zero p is
`undefined_zero_success`, even if C is zero or unknown, with no finite value.
Zero takes precedence over unknown cost.

| Supplied probability condition | `threshold.status` |
| --- | --- |
| p_H=0, p_V>0 | `undefined_zero_hadamard_success` |
| p_H>0, p_V=0 | `undefined_zero_valid_success` |
| both zero | `undefined_zero_both_success` |
| both positive, B unavailable | `unknown_cost` |
| both positive, B available | `defined` |

For any zero-probability condition, B, slope and Delta are all `None`, boundary
and relation are `undefined`. The other method can still have its own defined
normalization. No zero-success method is ranked, and 0/0 never becomes a tie.

## Twelve hypothetical scalar examples, derived by hand

All twelve are invented scalar records. Their domain/event assertions are
hypothetical assumptions, not support certificates or graph evidence. All
renewal acknowledgements and stationarity are assumed solely to interpret C/p.
Every R1 row has A_H=0. Costs below use `(j; A,O,S0)` and exact fractions;
`?` denotes `None`. Rows reused below retain their stated inputs. No example
uses a graph, an iteration study, a compiler output or an inferred probability.

| No. | Supplied rows and probabilities | Hand-derived charges and result |
| --- | --- | --- |
| 1 | H/R1 `(2; 0,5,1)`, p_H=1/3; V/R2 `(1; 1,2,1)`, p_V=1/2 | C_H=2(5+1)=12; D=3, E=3, C_V=3+3=6. Equality `(3B+3)/3=6` gives B=5. C_H/p_H=36, C_V/p_V=12; Delta=-24=`6(1-5)`: improvement. |
| 2 | H as 1; V/R3 `(3; 1/2,1,1)`, p_V=2/3 | D=7, E=6; C_V=7/2+6=19/2. Equality `(7B+6)/3=8` gives B=18/7. V per event is 57/4; Delta=57/4-36=-87/4=`(21/2)(1/2-18/7)`: improvement. |
| 3 | H/R1 `(2; 0,5,1)`; V/R2 `(1; 2,3,3)`; p_H=p_V=1/4 | C_H=12, E=6, D=3, C_V=12. Cancel equal probabilities in the equality: 3B+6=12, so B=2, exactly the raw boundary. Both per-event charges are 48; Delta=0: tie. |
| 4 | H/R1 `(1; 0,5,5)`, p_H=1/2; V/R2 `(0; 2,?,?)`, p_V=1/20 | C_H=10, C_V=2. Raw charge improves by 8, yet normalized charges are 20 and 40. Equality B/2=10/20 gives B=1; Delta=20=`20(2-1)`: loss. This is a counterexample to substituting the raw threshold for the C/p threshold. |
| 5 | H/R1 `(1; 0,1,1)`, p_H=1/2; V/R3 `(1; 0,1,1)`, p_V=1/4 | C_H=C_V=2, D=3, E=2. Equality `(3B+2)/2=2/4` gives 3B=-1, B=-1/3. Per-event charges are 4 and 8; Delta=4=`12(0+1/3)`: loss even at A_V=0. |
| 6 | Rows as 5, but p_H=p_V=1/2 | Equality 3B+2=2 gives B=0. Both per-event charges are 4; Delta=0: tie at A_V=0. With probabilities fixed, the symbolic difference is 6A_V, positive for every A_V>0. |
| 7 | H as 1; V/R3 `(1; ?,2,1)`, p_V=1/2 | D=3 and E=3 still give B=5, slope6. V's charge has known subtotal3 and unknown term `(A,3)`; V normalization and relation are unknown, Delta=None. B remains defined independently of A_V. |
| 8 | H as 1; V/R2 `(1; 1,?,1)`, p_V=1/2 | V's known subtotal is 3+1=4, with unknown `(O,1)`; E has known subtotal1 and unknown `(O,1)`. Positive probabilities leave slope6 defined, but B=None, boundary unknown, threshold status `unknown_cost`, relation unknown. |
| 9 | H/R1 `(0; 0,?,?)`, p_H=0; V/R2 `(0; 0,?,?)`, p_V=1/2 | Both static charges are zero because O/S0 are unused. H normalization is undefined; V normalization is defined zero. Threshold status `undefined_zero_hadamard_success`; B/slope/Delta=None and relation undefined. |
| 10 | Rows as 9; p_H=1/2, p_V=0 | H normalization is defined zero; V normalization is undefined. Threshold status `undefined_zero_valid_success`; B/slope/Delta=None and relation undefined. |
| 11 | Rows as 9; p_H=p_V=0 | Both normalizations are undefined despite zero charges. Threshold status `undefined_zero_both_success`; B/slope/Delta=None and relation undefined, with no 0/0 tie. |
| 12 | Let x=2^4095. H/R1 `(0; 0,?,?)`; V/R2 `(1; x,0,0)`; p_H=p_V=1 | x has 4096 bits and is an admissible scalar input. C_H=0; C_V=3x lies between 2^4096 and 2^4097, so has 4097 bits. E=0, D=3, B=0; Delta=3x>0: loss. This legal derived charge is too large to reuse as a new scalar cost input. No large integer needs to be materialized to derive this example. |

Examples 1 and 2 retain unequal H/V j values in both R2 and R3. They do not
establish a controlled implementation relationship between those V rows. In
example 1 the cross-product sign is `(1/3)6-(1/2)12=-4`; dividing by
`p_H p_V=1/6` gives Delta=-24. The same positive-denominator argument derives
the other numeric signs; no library output was used as their oracle.

The following is bounded API notation for example 1 only. It performs scalar
accounting, with no circuits or retries. It was read against the admitted
sources and was not executed as part of this documentation slice.

```python
from fractions import Fraction as F
from logique.benchmarks.preparation_breakeven import (
    ComparableSuccess, RenewalAssumptions, StaticCosts,
)
from logique.benchmarks.preparation_success_threshold import (
    success_normalized_threshold,
)

h = StaticCosts("R1", "hypothetical H domain", 2, 0, 5, 1)
v = StaticCosts("R2", "hypothetical V domain", 1, 1, 2, 1)
assumptions = RenewalAssumptions(
    independent_attempts=True,
    fresh_initialization=True,
    abort_reset=True,
    unpriced_verification=True,
)
event = ComparableSuccess(
    hadamard_probability=F(1, 3),
    valid_probability=F(1, 2),
    event="hypothetical common externally verified success",
    semantics="caller asserts the same event and comparable verification",
    renewal_assumptions=assumptions,
)
result = success_normalized_threshold(
    h, v, success=event, stationary_attempts=True,
)
# By the derivation above: limit_t=5, coefficient=6,
# difference_t=-24, relation="improvement".
```

## Keep input bounds separate from derived sizes

Normally constructed public inputs validate costs and probabilities before the
accounting arithmetic: built-in int/Fraction only, not bool or float; costs
nonnegative; probabilities in [0,1]; normalized numerator and denominator each
at most 4096 bits. `j` must be a built-in int in [0,1000000]. Domain, event and
semantics text must be nonempty after stripping and at most 4096 characters.
All supplied components are validated even at j=0. Reject oversized input,
inexact input and missing/false acknowledgements; do not silently round or
truncate. A Fraction's caller-side construction/normalization occurs before
these checks and needs its own size discipline. Forged or mutated Python
instances are outside the ordinary constructed-input contract.

Accounting uses a fixed number of scalar rational operations and a fixed
two-component loop, with no enumeration over j. With b=4096, the admitted
conservative bit bounds for numerator/denominator are C_H<=2b+24,
C_V<=3b+24, normalized charges<=4b+24, B<=6b+24 and Delta<=7b+48.
`MAX_DERIVED_BITS=16b+256=65792` also allows for unreduced intermediates;
it is an analytical bound, not a runtime output validator. Example 12 shows
why the 4096-bit input ceiling must not be imposed on legal expanded outputs.
Conversely, expansion does not authorize feeding an oversized output into a
new input field. None of these bounds is an OS memory/time guarantee or
admission to a different API.

## Establish semantics outside this scalar call

Domain text is no support or equivalence certificate. The caller must establish
the appropriate preparation support, clean phase marking, ordered data mapping,
signed S0, actual preparation inverse and restored workspace for any physical
interpretation. R3's removed domain checks are redundant only on the supported
valid-code subspace, not as a globally equivalent Boolean predicate. Approximate
preparation can leak outside that subspace, and even a reflection matched to its
actual approximation need not preserve the ideal valid-code subspace. An
edge-only R3 oracle can mark leaked invalid codes. Proper-coloring success and
invalid-code leakage need separate evidence; a supplied p must refer to the
same verified event in both rows. This guide supplies no leakage bound,
probability estimate, amplitude certificate or semantic repair.

Verification, measurement/reset/repreparation, feed-forward, Clifford operations,
runtime and physical QEC remain unpriced. Thus C/p is a charge per the declared
event under this restricted model, not total physical cost per solution.
Expected RUS rows are outside the deterministic static contract and must be
rejected. A RUS summary/result is not a `StaticCosts` input; copying its numeric
expectation into that type would also violate the contract even if numeric
validation accepts the scalar. No RUS instrument assumption or ledger is used
here. No retry runtime, dynamic execution, quantum control, static compiler
substitution or FT/RUS extension follows.

The existing [rotation admission](rotation_norm_admission.md) and
[static FT pilot admission](static_ft_pilot_admission.md) retain their exact
hashes and caller obligations. Their restricted numerical contract includes
measured one-qubit matrix defect<=64 float64 epsilon, original numeric/recursive
targets, norm-aware whole-search budgeting, precision floor1e-12 and bounded
SK/recursion/angles. Callers retain clean oracle/mapping/signed S0/restoration,
explicit MCX lowering, actual emitted inverse and scalar phases; precision
failure stays failure. Those admissions supply no interval certificate or
ideal-amplitude guarantee, and the isolated-vertex pilot supplies no meaningful
graph FT comparison. This guide runs none of those tools and broadens none of
those admissions.

This bounded caller guide authorizes no experiment, graph advantage claim,
iteration/probability inference, hardware submission or paper claim. Its next
step is the already queued independent guide review, then the coordinator's
own admission decision. Bounded completion is distinct from scientific
admission and full research acceptance.

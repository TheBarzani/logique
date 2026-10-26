# Analytical preparation break-even: coordinator admission

Coordinator `coordinate-preparation-breakeven-1025175909`, 26 October 2026.
**ADMITTED only for exact supplied-cost analytical accounting under the
assumptions below.** Both predecessors are dispatcher-complete, neither blocked;
no earlier completed own batch existed. Bounded integration is complete once the
batch checkpoint records its validated handoff. **Full paper unfinished.**
No graph break-even, dynamic execution, retry runtime, quantum control, static
compiler substitution, FT/RUS extension, hardware or paper admission is granted.

## Exact integration and independent evidence

Only correctness commit `16d1077f119c479546e8f63b35799ae7e88fa304` was integrated
as `25d5452`. Its two owned paths, actual files and committed blobs match the
independent review. Checkpoint-only `21a53e9` was not integrated. Review commit
`3cdd204` is preserved byte-for-byte in
[preparation_breakeven_review.md](preparation_breakeven_review.md).

| Artifact | Bytes | SHA-256 |
| --- | ---: | --- |
| src/logique/benchmarks/preparation_breakeven.py | 18161 | 774f1a4b8d255a66ffe24d57673f00ae5c0da13aaf6aaf5ea28dd838c2e10afe |
| tests/test_preparation_breakeven.py | 16864 | c3ed791853c16a223ba3e3bb593963ac5d9415109c485b55bbccc72ef3b8d225 |
| Worker checkpoint | 16183 | a745147d62a8c1d17b5499faa981ab3fcc59d3dfe7c6b90055b0a59a28414949 |
| Exact independent review | 29490 | 9d3d3c514ed23172ef5f04f8b5a67cc74ae510535e793244689ac6708f4648dd |
| Unchanged rus_accounting.py | 12683 | c56af0fa743ba6a58e622a7ab5614d983bf4e0eed532256b6ddc967e65fb2b44 |

Evidence is in `dump/1026123642-preparation-coordinator-triage/`: intake,
queue/state/server-manifest snapshots, protected byte/hash map, actual saved
worker/reviewer command events, exact embedded independent verifier, new
coordinator probes, command receipts and full logs. The original worker
checkpoint is copied there without editing. Both original worktrees remain
clean. Their original evidence and prior failures are retained.

## Proof, meaning and assumptions

For the time-ordered unoptimized word A followed by j copies of O,A-inverse,S0,A,
inversion preserves the supplied A logical T charge. Thus
`C=(1+2j)A+j(O+S0)`. This prices a concatenation, not an optimized lower bound,
static T-depth, workspace, physical cost or actual compiler output. Fractional
charges are hypothetical exact analytical inputs, not fractional emitted gates.
R1 requires explicit A=0 logical T; Clifford operations remain unpriced.

Each row retains its own domain, j and O/S0 costs. No same-j, same-domain or
same-oracle assumption is implicit. Caller provenance does not certify oracle
cleanup, domain equivalence or preparation support. In particular, removing
R3 domain checks is justified only on the appropriate valid-code support; this
module does not prove that support for any approximate preparation.

Put `D=1+2j_V>0`, `E_V=j_V(O_V+S0_V)` and
`B=(C_H-E_V)/D`. Then `C_V-C_H=D(A_V-B)` exactly. For B>0,
A_V below/equal/above B improves/ties/loses in raw logical T charge. At B=0
only A_V=0 ties; B<0 permits no nonnegative improvement or tie. At j_V=0,
B=C_H even when unused O/S0 are unknown. Unknown A can retain a known B;
unknown reached H or valid external costs prevent a numeric threshold. Unknown
component labels do not assert cross-row equality or permit cancellation.
All inputs, including unused invalid charges at j=0, are validated.

A raw-charge threshold does not establish a cost-per-solution threshold.
C/p comparisons require explicit exact probabilities for one caller-declared
comparable verified event, semantics text and renewal acknowledgements. They
infer no M/N, graph solution count, optimal j or first peak. Stationary fresh
independent attempts with unconditional attempt charge C satisfy
`R=E[C]+(1-p)R`, so `R=E[C]/p` for p>0. Cost/event dependence inside an attempt
is allowed; future attempts must have the same fresh independent distribution.
Comparable-event assertions are not equivalence certificates. Measurement,
reset/feed-forward, Clifford operations, external verification, runtime and
physical QEC remain unpriced. Zero event probability is explicitly undefined,
even at zero charge. Positive probability and zero charge give zero; unknown
cost remains unknown. No actual repetitions are executed.

Optional RUS results are separate from deterministic StaticCosts. They delegate
only to the exact [admitted analytical RUS ledger](rus_ledger_admission.md), with
explicit k=3 and literal True ideal arbitrary-input scalar-Kraus assumptions.
The underlying proof has K0=alpha U and K1=beta I, input-independent probabilities
3/4 and 1/4, including entangled references. The inverse prefix E-inverse is
applied once before a fresh ZUZ loop; scalar branch phases are retained. This
slice neither repeats quantum checks nor extends that ideal-instrument theorem.

Unlimited expectation, all-loops-completed conditional cost, unconditional
serial stop-at-first-exhaustion cost and exhaustion probability remain distinct.
Reached inverse prefixes and aborted trials are charged. For completion P and
supplied solution probability q conditional on completion, renewal uses
`E[C_stop]/(P*q)`, never the all-completed conditional charge. The product follows
from conditional probability and assumes no extra independence of those events.
For n=1,j=0,c=1, completed conditional charge 4, unconditional charge 7/2 and
P=3/4 yield completion-renewal charge 14/3; using 4 would discard failed trials.
Static comparison rejects RUS rows. n=0 is an empty mathematical product, with
external j charges retained; cap=0,n>0 aborts immediately. None of these cases
asserts executable circuit semantics or achieved preparation advantage.

## Bounded verification and exclusions

Candidate and integrated suites each passed **148 tests**, no skips/deselections.
The exact independent review verifier replay passed **11157 checks**, **88
rejections**, **1776 threshold cases** and **36 finite probability distributions**
(maximum ten loops and 85 aggregated polynomial terms). The verifier bytes are
9782 bytes, SHA-256
`f38401d285cdde45bc2f45d4fea2b1c94dcf37cc44ba27d80774a0f85fd6aac4`.
New seeded coordinator probes independently summed **512 component words**, used
cross multiplication to check success-normalized ranks, and checked high-bit
boundary neighbours, unknown A and maximum j: **2053 exact assertions**. These
are hypothetical correctness probes, not research performance measurements.
Relevant Black/Ruff, focused one-file mypy and whitespace checks pass.

Costs/probabilities accept only built-in int/Fraction, not bool/float, with
4096-bit numerator/denominator input ceilings checked before arithmetic.
Static j<=1000000 uses a constant number of rational operations, no enumeration.
Outputs can exceed the input bit ceiling. RUS requires caller limits with
n,j,cap<=64, L=n(1+2j)<=4096, and principal power-growth estimate
`2c(L+2n+2)+32` within caller budget<=4096 (32 for unlimited cap). This is not an
all-intermediate or general OS resource bound; unlimited retries have no finite
worst case. Preflight rejects before ledger delegation.

All seven validation children ran sequentially using the existing root research
Python, explicit cwd src/cache/private native paths, one BLAS/OpenMP thread,
external timeout60s each. Numerical wall across four numerical children was
**0.697964 seconds**, below 180s; maximum measured child RSS **97452032 bytes**,
below 8 GiB. High-water RSS can carry a previous maximum; it is not aggregate OS
memory enforcement. Native was never called. **No quantum arrays** were used;
dense<=4/statevector<=5 limits are unchanged and unused. No full suite, configured
whole-project mypy, build, static FT/compiler tests, graph experiment, notebook,
routing/noise, historical replay or saved-static-artifact regeneration is claimed.

Explicit operational failures: absent .codex/.agents exploratory discovery;
broad file discovery/combined long reads truncated and were replaced by focused
full-document chunks; initial state summary used nonexistent `tasks` rather than
`jobs` (KeyError, no writes), then corrected. Initial cherry-pick could not create
.git/index.lock; scoped automatic escalation succeeded. No automatic approval
rejection, numerical/assertion/static failure, timeout or scientific counterexample
occurred. Prior worker/reviewer failures remain in their original checkpoints.
No agents/models/API/credits/hardware/push/sync/install/dependency change occurred.

All **2088 protected intake identities** must match at handoff, including README,
source outside owned additions/audit, original worktrees/evidence, prototypes,
archives, nested histories, pins, both binaries and saved static pilot artifacts.
External index/gitlinks also must match. The only existing tracked document
allowed to change is the append-only implementation audit; server manifest and
queue receive the separate validated checkpoint/handoff updates.

Static FT retains exact source/test/harness/artifact hashes and the
[rotation numerical contract](rotation_norm_admission.md): measured one-qubit
unitarity defect<=64 float64 eps, original numeric/recursive targets, norm-aware
whole-search accounting, precision floor1e-12 and bounded SK/recursion/angles.
Caller obligations remain clean oracle, ordered mapping, signed S0, restored
workspace, explicit lowering, actual emitted inverse and scalar phases. The
private common-preprocessing binary remains distinct from the old root build.
No interval certificate, ideal-amplitude guarantee, graph FT or RUS extension.

## One next analytical slice and release

The whole **45-job queue** was inspected, with two blocked native statuses,
this sole running coordinator and six pending jobs for component-width and
ideal-boundary correction/review/coordinators. Those owners retain their scopes.
Append exactly one additive static success-normalized preparation threshold
slice, with isolated review and coordinator: `preparation-success-1026123642`,
`preparation-success-review-1026123642`, and
`coordinate-preparation-success-1026123642`. Worker depends on THIS coordinator;
review/coordinator use finished-predecessor triage. Prior headers, definitions
and prompt bytes remain immutable. Dispatcher alone launches and pushes.

Justification: the admitted threshold B is explicitly raw-charge-only, while
unequal supplied success probabilities can reverse the ranking. The next slice
may derive `B_p=[(p_V/p_H)C_H-E_V]/D` for positive supplied comparable probabilities
and `C_V/p_V-C_H/p_H=(D/p_V)(A_V-B_p)`. It must preserve zero/unknown distinctions,
exact signs, provenance and resource bounds. Own only a new additive source/test
pair and checkpoint; existing admitted modules/tests remain read-only. No RUS
rows, inference/choice of j, graph costs, execution or FT/RUS extension.

Full remaining scope is preserved in the batch/server manifest: controls and
post-pilot freeze; affected old QPY evidence; native mappings/profiles/SAT;
structure common-lowering comparisons; nine-graph/multilevel/strongest-baseline/
ablations/five-seed studies; meaningful graph FT under unchanged exact-hash
contract; achieved preparation break-even and separate dynamic RUS admission;
iteration-boundary corrections and executed ideal/noisy/leakage/confidence/
random-sampling/cost-per-success studies; scaling/DIMACS five repeats and
witnesses/resources; full acceptance/build/provenance/offline notebooks/isolated
135-metric replay; traced manuscript, reviewer responses, evidence gate and
independent final correctness/claim/reproducibility reviews. Full paper unfinished.

On resumption after batch bounded_batch_complete, verify integration/document
commits, exact reviewed/protected/evidence hashes and three unique jobs, then
release this assigned coordinator outcome=complete without repeating tests,
integration or queue appends. Scientific admission and bounded completion are
distinct. Initial outcome=continue reports the unfinished full paper.

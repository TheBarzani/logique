# Independent exact-count boundary review

**Bounded review COMPLETE. Scientific decision: ADMIT the exact bytes below
for the enforced bounded analytical ideal-iteration contract only.**
No remaining categorical counterexample was found. This closes the predecessor's
boundary blocker for these corrected bytes; it does not retroactively admit the
old bytes. Probabilities and supplied costs remain numerical, not interval or
ideal-amplitude certificates. No saved-circuit, noise, FT/RUS, achieved advantage,
or paper admission. The full paper remains unfinished.

## Identity and intake

Task `ideal-boundary-review-1026075259`, 26 October 2026, America/Montreal.
Assigned branch `codex/coloring-ideal-boundary-review-1026075259`.
Review base `e46f643dca6e40c08c629430ab170dabc0c0dd5d`, initially clean.
This file was absent; there was no completed own review to repeat.
Read-only sibling source: `../boundary-fix`, branch
`codex/coloring-ideal-boundary-fix-1026075259`.
Original correctness commit `ed1001b7b32668717f447898503d5d4c3ca6af47`;
correction `a157c602935457ec2c04eee9e022d119faedcb31`;
source HEAD/checkpoint `a6e95928ff6747fe8cbb75782735638d26480b47`.
Both correctness commits contain only the source/test pair. Checkpoint-only
commits must stay outside correctness integration. Source status is clean.

Read AGENTS.md, CLAUDE.md, the full 646-line revision plan, implementation audit
including current root additions, both required rotation/parallel coordinator
batches, server checkpoint manifest, root structure/rotation admission,
historical ideal boundary review/triage, this run's batch and assigned prompt,
original candidate checkpoint and correction checkpoint. Inspected all 399
source lines and 462 test lines, actual commits and committed blobs, not merely
the correction delta or green tests. No required deliverable was missing.

The entire live queue/state was parsed and inspected: 51 queue jobs, 44 state
records at resumption. Correction is complete; this reviewer is the only durable
running job. Its coordinator is queued once with finished-dependency triage.
Unrelated native low-T and alias coordinator remain blocked. Existing native,
MCX/main-runner/QPY/controls, structure, static FT/RUS and preparation scopes
retain ownership. Durable state is not complete OS process visibility.
Initial intake was interrupted before numerical checks; resumption verified Git,
all queue statuses/dependencies, absent own checkpoint and unchanged source
identities. It did not repeat completed numerical work.

| Source-relative file | Review before = after SHA-256, matching HEAD blob |
| --- | --- |
| `src/logique/benchmarks/ideal_iterations.py` | `7724b76624bc07cf3164abf2c76ddb677c21ccc6cdc86991f8cc09b659b53e40` |
| `tests/test_ideal_iterations.py` | `756c2507cd522815ba155c18abb61c26101475ec69df7e87098475dd36fffa0e` |
| `IDEAL_ITERATIONS_CHECKPOINT.md` | `c5e27ef74740b3d2699e2614a7e9899fa8e95921f898a89bceae03a64ff19427` |
| `IDEAL_BOUNDARY_CHECKPOINT.md` | `d517faf194f02dec5093432897c2e6eaf82ddf1d509f60e3e3215b3fb6c4dd76` |

Rejected original source/test hashes remain respectively
`47c4dca00f43ffbf99e9152b6c006ddefbd0df3cf92207dff84fd264b89c9aaf` and
`8f4856a5f497c620578704350552b75379575ec97e60d41632910cab760022ee`.
Historical root review remains
`1865e17f48314d1bf3cd4f446b8bd2d8ee60e3dc1c36b47637fa6f49c0f9ca65`;
triage remains `602282224a50f79e78414e006ee3ec5d51745650aac5fee6f278b885fb673e20`.
Its original failed independent probe and 20 categorical mismatches remain saved.

## Independent proof and exact acceptance boundary

Let p=M/N, theta=asin(sqrt(p)), and x=pi/(4 theta)-1/2 for 0<p<1.
With good/bad reference a=(sqrt(p),sqrt(1-p)), the oracle O=diag(-1,1)
and signed D=2aa^T-I give amplitudes sin((2j+1)theta), cos((2j+1)theta).
Equivalently g=sqrt(p)u, b=sqrt(1-p)v start u=v=1 and obey
u'=(1-2p)u+2(1-p)v, v'=-2pu+(1-2p)v. This follows by applying O then
the weighted-dot reflection; it fixes the sign of D, which probabilities alone
cannot establish. Exact Pj=p*u_j^2 is rational for rational counts.

The implementation's v polynomial equals cos((2j+1)theta)/cos(theta):
v0=1, v1=1-4p, vj=2(1-2p)v(j-1)-v(j-2). Its second polynomial is
cj=cos(2j theta), c0=1, c1=1-2p, with the same second-order recurrence.
Fraction arithmetic evaluates both exactly from accepted integer M,N.

The FIRST nonpositive vj brackets x. Before it, odd angles are below pi/2:
an increment 2theta<pi cannot skip the whole negative-cosine interval.
The crossing angle is strictly below 3pi/2. Thus vj=0 means x=j exactly;
otherwise j-1<x<j. This is a general proof, including irrational boundary roots,
not a repair for named rational landmarks. In the bracket,
0<2j theta<pi because (2j-1)theta<pi/2 and theta<pi/2.
The adjacent probability difference is
Pj-P(j-1)=sin(4j theta)*sin(2theta). Its sign is exactly the sign of cj
since sin(2j theta)>0 and sin(2theta)>0. Consequently positive cj selects j;
negative selects j-1; exact zero selects j-1. Equivalently the nearest integer
to x is chosen, with exact ties choosing fewer iterations. vj=0 selects (j,j).
This concerns the first continuous lobe, not later oscillation or optimal C/P.

All categorical choices use those exact signs, never displayed probabilities,
rounded theta, or a tolerance. Mathematical exactness of integer arithmetic
therefore removes categorical floating uncertainty for every accepted input.
General unresolved/out-of-range inputs reject rather than manufacture a tie:

- Known Python integer M,N excluding bool; N>=1 and 0<=M<=N. Unknown M rejects.
- N.bit_length()<=64 is enforced before float conversion/rational recurrence,
  including constants. Interior fractions rounded to a binary64 endpoint reject.
- The first bracket must be found within min(128,max_iterations) steps.
  User caps cannot extend degree128. Unresolved degree/iteration range rejects.
- Constants M=0,N use peak0, candidates(0,0) and rows0,1. Interior accepted
  sweeps use last=peak+1; last<=max_iterations and last+1<=max_rows are checked
  before the row list or any IterationRow is constructed. No partial sweep
  silently substitutes for an insufficient cap.

The bracket limit cannot reject a sweep whose required last index fits a smaller
caller iteration cap: bracket j is at most peak+1. A nonconstant accepted ledger
has peak<=128 and at most130 rows. At most128 exact recurrence steps, constant
scalar storage and O(128*64)-bit integers bound categorical work independently
of enormous caller caps. All <=12-bit graph supports have N<=4096; their smallest
positive fraction gives x<50, hence bracket<=50. The narrowed contract covers
the intended bounded graph fixtures while explicitly rejecting smaller fractions
such as 1/100000. Binary64 analytical probabilities/costs remain approximations;
near-boundary probabilities may round together or in the opposite numerical
order without changing the exact metadata. No certified uniform float-error
bound or ideal preparation-amplitude guarantee is inferred.

## Source/test and semantic assessment

Support enumeration is separate from circuit/encoder implementations. Sorted
distinct integer labels include isolates; each edge must use declared vertices.
The complete predicate requires valid codes AND every edge inequality. R1 uses
all 2^(c|V|) words, R2/R3 use k^|V| valid-code words, c=max(1,(k-1).bit_length()).
Precolors reject; >12 data bits rejects before product enumeration. Empty graphs,
loops and one-color cases retain their explicit semantics. Rejected support is
partitioned into invalid codes and valid-code edge violations, with real witnesses
or None for absent classes. R3's edge-only oracle is coloring-equivalent only
on valid-code support; unequal words (0,5) for k5 are not a proper coloring.

The caller must independently establish exact uniform A on the declared support,
clean marking O, actual inverse, correct signed S0, mapping and restored workspace
under lowering. The ledger establishes none of these executed implementations.
Ordinary graph support counting does not supply approximate amplitudes or QPY
fidelity. Empty-graph analytical support is meaningful even if a circuit API
requires nonempty data registers.

Costs remain finite nonnegative supplied additive values with an explicit basis:
A+j*(2A+O+S0). A and its inverse have equal stated costs. C/P assumes independent
identical full program restarts, paying A and all j iterations every time; no
early exit, shared preparation, measured resources or achieved break-even.
P=0 gives infinite expected runs and undefined cost per success even at zero
cost. Missing cost stays unavailable; nonfinite program cost rejects; C/P range
overflow is explicitly unavailable/infinite_float_cost. Depth-labelled additive
costs reject. Measurement/check/reset charges require explicit caller inclusion.
Random reference 1-(1-p)^r has its own trial cost/basis and analytical label;
its unchanged float-range contract is separate from the ideal ledger's new
64-bit/degree limits. No trial-to-Grover cost equivalence is assumed.
Leakage, noise, confidence intervals, routing, actual resources and T-depth
remain unavailable. Imports remain standard library only.

The full supplied suite retains floating signed-amplitude checks, exact rational
adversarial checks, cost/range failures, import isolation and support enumeration.
Some old ordinary-case expectations use floating x; those alone cannot establish
boundary correctness. New Fraction reflection checks and this independent probe
supply exact expectations. Source inspection confirms caps precede the list;
constructor sentinels independently check no row is reached on rejection.

## Independent evidence and actual commands

Evidence directory in THIS review worktree:
`dump/1026174027-ideal-boundary-review/`.
`independent.py` was written separately and imports the actual candidate by exact
file path. It does not import worker tests, their recurrence, is_valid, encoder
or a maintained verification interpreter. Own checkout src is on PYTHONPATH
and asserted; the source module is loaded explicitly. Integer weighted-dot
O-then-D numerators over N^j supply independent exact rational probabilities.

Results: **277,950 assertions, 6,442 accepted ledger cases, 50,146 exact rational
probability rows, 1,063 expected rejections, 1,167 graph/regime checks.**
Maximum observed absolute displayed-probability error is
**1.5543122344752192e-15**, a fixture observation, not a certified bound.
Every M for N=1..96 is covered. Both sides of **256 decision boundaries**
(candidate j=1..128 and adjacent-peak j=1..128) use exact integer sign bisection
at N=2^64-1. Floating trig only seeds a broad bracket; integer signs prove its
sides and narrow to adjacent rational numerators. The side needing bracket129
explicitly rejects before rows. Degree128, huge caller caps, endpoint rounding,
count overflow, exact p=1/4 and 1/2 ties, P=0 at p=3/4,j1, and insufficient
row/iteration caps are checked. Thus the test does not merely reuse rounded x.

The original near-half case returns candidates(0,1), peak1, rows0..2;
the irrational case M=14644660940672623,N=10^17 returns (1,2), peak2, rows0..3;
the two near-quarter cases return (1,2)/(0,1), both peak1. Opposite sides are
also tested. Exact rational probabilities establish the strict comparisons.
Insufficient caps now reject before rows. Direct packed-word predicates cover
all simple graphs through four vertices for k1..5, two-color paths3..8, C5/k3,
loops, empty graphs and six k3 isolates. They do not call problem.is_valid.
Signed amplitudes and exact weighted norm are checked separately from probability.
Independent supplied-cost, random-trial, unavailable and overflow checks pass.

The source-worktree focused suite independently passed **183 tests**, zero skips
or deselections. Its import-only -S child performs no numerical work. No numerical
checks were repeated after passing. No broader suite, static rerun, compiler,
native execution, study, notebook or historical replay is claimed. Worker
Black/Ruff/mypy results were inspected and their saved evidence hashes verified.

Actual supervised commands, with argv/cwd/environment/exits/time/RSS retained in
`commands.json` and logs:

```sh
/Users/mar/codex-work/logique/.venv/bin/python dump/1026174027-ideal-boundary-review/run_checks.py
# Supervisor launches these sequentially:
/Users/mar/codex-work/logique/.venv/bin/python /Users/mar/codex-work/logique/dump/1026075259-ideal-iteration-coordinator-triage/worktrees/boundary-review/dump/1026174027-ideal-boundary-review/independent.py
# Source worktree cwd and source worktree src for the supplied import test:
/Users/mar/codex-work/logique/.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_ideal_iterations.py
git diff --check
git diff --cached --check
```

Independent child 14.279797s; supplied child 0.490010s; cumulative **14.769807s**,
each timeout180s, total below300s. Maximum measured child RSS **44,187,648 bytes**,
below8GiB. One sequential scalar numerical child; exact recurrence at most129
iterations in independent post-peak checks, production at most128; graph words
<=4096. No quantum arrays, dense operators, statevectors or compiler. RSS is
per-child/highwater evidence, not an enforced aggregate OS cap.
Both use PYTHONDONTWRITEBYTECODE=1, OMP/OPENBLAS/VECLIB threads=1,
LOGIQUE_CACHE=/Users/mar/codex-work/logique/.cache/epfl and explicit
LOGIQUE_NATIVE_EXECUTABLE=/Users/mar/codex-work/logique/dump/1025024643-coloring-integration-gate/worktrees/native-contract/dump/1025025511-native-contract/build/boolean_synthesis.
This manifest-selected binary was not invoked or rebuilt.

## Preservation, failures and handoff

All 1,007 intake protected identities and all 1,432 correction-worker protected
identities match, including archives, prototypes, nested histories, prior failed
evidence and nonowned sources. All 20 correction evidence receipt hashes match.
Source/test hashes match committed blobs before/after; dependency gitlinks are
unchanged. Root README remains modified user work, hash
`73c3c1acbfa78ee31abce2e4d1e7af369b02c554b8aca7a5bf3d8b6c293f4e4c`.
Private binary remains `6aa7357d2f64202584b14b0a14f8fb183379faf5907723cd24bd838b9be14a9a`;
old root binary remains `ea78b720327f82dd9bbc8c1eb4db63b182c87eaeb7382474ea4d3488457150fa`.
Queue remains unchanged; the existing dispatcher may refresh live state.

No numerical assertion failure, timeout or OOM occurred. Expected ValueError
rejections above are successful fail-closed checks. Preliminary ls reported
this new review absent (exit1); large exploratory combined reads were truncated
and followed by focused ranges/parsed inventories. The intentional intake
interruption is recorded above. Original failed predecessor evidence and blocked
decision remain unchanged. Initial explicit-path git add failed with exit128:
the sandbox denied the shared worktree index.lock. Scoped Git escalation is
used under the existing explicit commit authorization. Git commit outcome and exact
review-file hash are recorded in `final-receipt.json` to avoid self-reference.

Only this new review is tracked/committed. No source edits, root integration,
job append, agents/models/Codex subprocesses, API/credits, hardware, pushes,
publishing, sync/install or dependency changes. Correctness/build/metrics stay
separate. Next action belongs to the already queued
`coordinate-ideal-boundary-1026075259`: verify exact bytes, independently accept
the bounded scope, and integrate original ed1001b plus correction a157c60 only
if its checks support admission. Preserve this review alongside the historical
blocked review; do not overwrite that history. Dispatcher alone launches jobs
and pushes committed integration HEAD. Workers never integrate or push.

Existing rotation admission is unchanged: exact reviewed hashes and numerical
contract in root rotation_norm_admission.md, without interval certification,
ideal-amplitude guarantees or broader FT/RUS acceptance. Executed ideal/noisy
iteration sweeps, leakage/confidence/resource comparisons, all remaining full
research acceptance and the paper evidence gate remain outstanding.
On completed-handoff resumption verify commit, hashes and receipt, then release
outcome=complete without repeated tests, duplicate work or queue edits.

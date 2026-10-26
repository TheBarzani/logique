# Independent ideal-iteration review

**Bounded review: COMPLETE. Scientific admission: BLOCKED for the advertised
supplied-integer-count analytical contract. Full paper: unfinished.**

The exact candidate accepts known integer M,N near floating-point decision
boundaries but can return the wrong first discrete peak and omit its required
post-peak row. It also misreports floor/ceiling candidates near p=1/4. The
ordinary bounded graph fixtures pass; this decision does not allege incorrect
graph counts or a failure of the amplitude-amplification formula. It concerns
discrete metadata and sweep completeness on accepted inputs. Passing supplied
tests does not remove this blocker. No worker files were repaired or integrated.

## Identity and intake

Date: 26 October 2026, America/Montreal.
Task: `ideal-iterations-review-1025173122`.
Review worktree:
`/Users/mar/codex-work/logique/dump/1025173122-parallel-coordinator-triage/worktrees/ideal-review`.
Review branch: `codex/coloring-ideal-iteration-review-1025173122`.
Initial HEAD: `4ab42355841220913d09e8f2e728527835e2d11d`, clean, with this review
file absent. There was no previous completed review handoff to repeat.

Read-only source worktree: sibling `ideal-iterations`.
Source branch: `codex/coloring-ideal-iterations-1025173122`.
Correctness commit: `ed1001b7b32668717f447898503d5d4c3ca6af47`.
Source HEAD/checkpoint commit: `0d14550e66bd94b74aa28773cd5de9f1e8536e12`.
Source status was clean before and after review. These are the final amended
worker bytes, not its superseded `05569c6` correctness commit.

Git and durable dispatcher files were inspected before substantive work. The
entire 42-job queue and state were read, including blocked native jobs and all
pending scopes. The predecessor is complete; this reviewer was the only durable
running job. The ideal coordinator is queued once, with finished-dependency
triage. Queue/state inspection is not complete OS process visibility. No
dispatcher control or queue mutation was performed.

Read AGENTS.md, CLAUDE.md, the full 646-line revision plan, implementation audit,
worker and reviewer prompts, source checkpoint, both required coordinator
batches, server manifest/native selection and current admission gates, root
structure_parallel_admission.md, and the rotation numerical contract. Large
initial combined outputs were truncated; the plan, audit and queue/state were
subsequently inspected in smaller ranges. The manifest was parsed in full and
its state, ownership, selected executable and admission sections inspected.

Exact SHA-256 identities below were equal before/after numerical checks and
equal to source HEAD blobs:

| Source-relative file | Before SHA-256 = after SHA-256 |
| --- | --- |
| `src/logique/benchmarks/ideal_iterations.py` | `47c4dca00f43ffbf99e9152b6c006ddefbd0df3cf92207dff84fd264b89c9aaf` |
| `tests/test_ideal_iterations.py` | `8f4856a5f497c620578704350552b75379575ec97e60d41632910cab760022ee` |
| `IDEAL_ITERATIONS_CHECKPOINT.md` | `c5e27ef74740b3d2699e2614a7e9899fa8e95921f898a89bceae03a64ff19427` |

Only `IDEAL_ITERATIONS_REVIEW.md` is owned/tracked by this slice. Evidence lives
in the fresh local-time run `dump/1026073939-ideal-iteration-review/`. The final
commit and review-file hash are recorded in its `final-receipt.json`, avoiding
a self-referential hash. No generated output is staged.

## Concrete blocker and correction requirement

`_fraction` (lines 52–60) rejects interior fractions rounded to zero or one but
accepts loss of information at interior decision boundaries. Lines 169–185
compute theta/x in binary64 and use their rounded floor/ceiling and distance
for categorical decisions. Exact special cases only repair equalities such as
`2*M == N`; they do not resolve near-boundary inequalities. Lines 186–190 then
derive the sweep cap and extent from that potentially wrong peak.

Minimal peak/extent reproducer, with the source worktree on PYTHONPATH:

```python
from logique.benchmarks.ideal_iterations import ideal_iteration_ledger

out = ideal_iteration_ledger(
    18014398509481983, 36028797018963968,
    max_rows=3, max_iterations=2,
)
assert out.first_peak_iteration == 0       # actual; mathematically must be 1
assert [r.iterations for r in out.rows] == [0, 1]  # must include 2
```

Here p=1/2-2^-55 is strictly below 1/2 but its float conversion is 0.5. Exact
rational reflection recurrence proves P1>P0 and P1>P2. In particular,
`P1-P0 = 8*p*(1-p)*(1-2*p) > 0`; the saved exact difference is
`324518553658426726783156020576255 / 2923003274661805836407369665432566039311865085952`.
This is a tiny probability difference (about 1.11e-16), not a large probability
error. Nevertheless this is not an exact tie, peak 1 is required, and the
advertised sweep needs j=0,1,2. The same input with `max_rows=2,
max_iterations=1` wrongly succeeds instead of rejecting the insufficient cap.

The issue is not confined to exactly representable rational-angle landmarks.
For M=`14644660940672623`, N=`100000000000000000`, caps rows=4/iterations=3,
the candidate returns peak 1, while exact rational probabilities give
P2>P1, P2>P0 and P2>P3: peak 2 and row j=3 are required. This fraction lies
just below `(2-sqrt(2))/4`, the j=1 versus j=2 tie. Decimal arithmetic only
located the fixture; exact Fraction recurrences prove the strict ordering.
An additional N=10^18 fixture reproduces the same error.

Candidate-metadata reproducer: N=`18014398509481984`,
M=`4503599627370495` or `4503599627370497`. Both return candidates `(1,1)`.
Correct pairs are respectively `(1,2)` and `(0,1)`. These p values remain
distinct from 1/4 even in binary64 (`0.24999999999999994` and
`0.25000000000000006`); rounding of theta/x loses the distinction. Since x(p)
is strictly decreasing and x(1/4)=1, the strict integer inequalities prove the
correct candidate pairs. These two examples retain the correct peak 1 and
row extent; their failure is metadata only.

Required correction: preserve the relationship of accepted exact M/N to
candidate and peak boundaries, or explicitly reject numerically unresolved
decisions before constructing rows. A documented bounded input contract with
enforced rejection is acceptable; silently calling a near-tie an exact tie is
not. Resolve the general decision ambiguity, not only the half/quarter examples.
Retain mandatory row/iteration preflight and exact p=0/1 conventions. Add
regressions using independent exact probabilities for both sides of boundaries,
exact ties, complete first-peak-plus-one extent and insufficient caps. Do not
inflate a fixed probability tolerance to redefine the requested tie convention.
Correction and independent review must bind new source/test hashes. This review
does not authorize changing someone else's files or dispatching that work.

## Independent assessment of the remaining contract

For exact uniform support, write a=(sqrt(p),sqrt(1-p)). The good/bad oracle is
O=diag(-1,1) and the correctly signed diffuser is D=2aa^T-I. Applying O then D
gives `(g,b) -> ((1-2p)g+2sqrt(p(1-p))b,
-2sqrt(p(1-p))g+(1-2p)b)`, hence amplitudes
`sin((2j+1)theta), cos((2j+1)theta)` from a. Probability alone would not
distinguish D from -D; the independent tests inspect both signed amplitudes.
For exact rational checking set g=sqrt(p)u, b=sqrt(1-p)v. Starting u=v=1,
update `u'=(1-2p)u+2(1-p)v`, `v'=-2pu+(1-2p)v`; Pj=p*u² is rational.

The first-lobe continuous maximum is x=pi/(4theta)-1/2. Comparing adjacent
integer samples is equivalent to selecting the nearest integer to x, with the
fewer-iteration exact-tie rule; this is not an optimum over later oscillations
or an optimum cost per success. Exact p=1/2 returns peak 0. p=0/1 explicitly
uses peak 0 and rows 0,1, with constant zero/one probability. p=3/4 at j=1 is
set to exact zero, avoiding fabricated finite C/P from sin(pi) roundoff. The
small-count first-peak results and post-peak decreases passed; the blocker above
concerns unrestricted supplied counts and unresolved numerical decisions.

Integer support counting is independent of the encoder/synthesis and rejects
data widths above 12 before Cartesian enumeration. c=max(1,(k-1).bit_length())
retains the maintained one-color convention. R1 counts complete predicates on
N=2^(c|V|); R2/R3 count on N=k^|V|. The same proper-coloring M is obtained in
all three regimes. Invalid-code and valid-code edge-violation counts partition
the rejected support; witnesses are explicit, absent classes are None. Loops,
isolates, empty graphs and noncontiguous integer labels are handled. Precolors
reject. M=None, bool/noninteger counts and inconsistent M,N reject; there is
no fabricated M=1 or unknown-M peak.

Checked counts include two-color paths3..8 (M=2); three-color K3 (M=6,
N=64/27), C5 (M=30,N=1024/243), P4 (M=24,N=256/81); unsatisfiable two-color
triangle and loops (M=0); two isolated k3 vertices (M=9,N=16/9); empty graph
(M=N=1); asymmetric k5 edge plus isolate (M=100,N=512/125); and six k3 isolates
at exactly 12 binary bits (M=729,N=4096/729). The eight-vertex two-color path
has P1=0.06885528564453125 and peak 8, followed by lower success at j=9.

R3's edge-only predicate is coloring-equivalent only on valid-code support:
the k5 edge word (0,5) satisfies inequality but is not a coloring. Exact uniform
A, the full mapped support, a clean phase oracle, actual inverse, correctly
signed S0, and restored lowering/workspace remain caller obligations. Counts
and formulae verify none of those physical implementations or saved QPY files.

Supplied nonnegative finite scalar costs implement A+j*(2A+O+S0), with equal
stated A/inverse costs and an explicit common basis. Independent identical full
program restarts yield C/P for P>0: all j iterations run and A is paid again on
every restart. This is not early termination within a run, shared preparation,
variable schedules, or a proof of achieved break-even. P=0 explicitly reports
infinite expected runs and undefined cost per success, including zero cost;
unpriced costs stay unavailable and range overflow has explicit status/rejection.
Measurement/check/reset costs must be declared in the supplied basis if desired.
Depth-labelled additive costs reject; no T-depth is obtained by summing T counts.

Random reference probabilities are separately labelled analytical independent
uniform trials, `1-(1-p)^r`, with r and its own per-trial cost basis recorded.
Trial cost is not equated to a Grover iteration. Stable log1p/expm1 evaluation
agrees with independent exact rational values in the tested range, including
r=0 and p=0/1. Leakage, noise, confidence intervals, routing, actual circuit
resources and T-depth remain explicitly unavailable. No quantum imports were
introduced in this standard-library reference.

## Evidence, commands and bounds

The independent harness imports the actual candidate module and ColoringProblem,
but no worker tests, model.is_valid checker, encoder or verification interpreter.
It asserts the module path equals the read-only source worktree's src path.
Coverage: 2,144 M,N cases (all M for N=1..64), 5,744 scalar probability/norm
steps, 5,488 signed-amplitude comparisons; 577 exact rational recurrence steps
for N<=20; 396 graph fixtures / 1,188 regime checks, including every simple
graph through four vertices for k=1..5, with direct packed-integer decoding;
4,752 witness checks; 2,800 exact random-trial probability comparisons; supplied
cost/repeat arithmetic, invalid-input rejection and preflight sentinels.

`independent.py` made **38,157 assertions: 38,156 pass and one grouped boundary
assertion fails**, recording 20 concrete peak/candidate mismatches. Its exit code
is **1**, retained in `independent.log` and `independent-results.json`.
The targeted `boundary_reproducer.py` then passed its blocker-confirming
assertions (exit 0), proving the half-boundary ordering/cap failure and retaining
all six additional near-irrational-boundary outcomes (two mismatches).
That green targeted result confirms the blocker; it is not admission.

The supplied focused suite separately passes **129 tests**, no skips or
deselections. It is supporting regression evidence only. No broad suite, build,
lint/type-check rerun, study or historical replay was needed for this review-only
change. `git diff --check` validates the owned document before commit.

Actual supervised commands (source worktree cwd):

```sh
/Users/mar/codex-work/logique/.venv/bin/python /Users/mar/codex-work/logique/dump/1025173122-parallel-coordinator-triage/worktrees/ideal-review/dump/1026073939-ideal-iteration-review/independent.py
/Users/mar/codex-work/logique/.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_ideal_iterations.py
/Users/mar/codex-work/logique/.venv/bin/python /Users/mar/codex-work/logique/dump/1025173122-parallel-coordinator-triage/worktrees/ideal-review/dump/1026073939-ideal-iteration-review/boundary_reproducer.py
```

`commands.json` retains argv, cwd, environment, exits, measured times and RSS;
`run_checks.py` and `run_boundary.py` are the supervisors. Per-child timeout
180 seconds, cumulative preflight budget 300 seconds; measured total
**1.311927 seconds**, maximum child RSS **42,762,240 bytes**, below 8 GiB.
RSS is measured, not an enforced aggregate OS memory guarantee. One sequential
numerical child at a time; the supplied import-only -S child does no numerical
work. No quantum arrays, dense operators, statevectors, compiler or native
invocation. Enumeration <=4096 words per fixture; two scalar amplitudes;
large supplied counts are integers, never allocated support arrays.

Environment: existing research Python, PYTHONDONTWRITEBYTECODE=1,
PYTHONPATH=`/Users/mar/codex-work/logique/dump/1025173122-parallel-coordinator-triage/worktrees/ideal-iterations/src`,
LOGIQUE_CACHE=`/Users/mar/codex-work/logique/.cache/epfl`, OMP/OPENBLAS/VECLIB
thread limits=1. Explicit LOGIQUE_NATIVE_EXECUTABLE is the manifest foundation
binary at `/Users/mar/codex-work/logique/dump/1025024643-coloring-integration-gate/worktrees/native-contract/dump/1025025511-native-contract/build/boolean_synthesis`.
Its SHA-256 remains `6aa7357d2f64202584b14b0a14f8fb183379faf5907723cd24bd838b9be14a9a`.
The old root binary remains `ea78b720327f82dd9bbc8c1eb4db63b182c87eaeb7382474ea4d3488457150fa`.

## Preservation and handoff

All 614 intake protected file hashes match, covering both worktrees' tracked
files, source checkpoint, README and native/admission references. An additional
205 archive/history/prototype baseline hashes match the coordinator inventory.
Dependency gitlinks are recorded and unchanged. Root README remains modified
user work, SHA-256 `73c3c1acbfa78ee31abce2e4d1e7af369b02c554b8aca7a5bf3d8b6c293f4e4c`;
it is never staged. Queue bytes are unchanged; durable state may be refreshed
by its existing dispatcher. No source/worker/root integration, job append,
agents, model/Codex launches, API/credits, hardware, pushes, publication,
sync/install, dependency changes, or historical-output edits occurred.

Failures retained: the substantive independent boundary assertion above;
initial discovery found this review file absent as expected; an ancillary shell
glob for absent root .codex failed without mutation. No numerical timeout or
resource failure occurred. Initial explicit-path Git staging was sandbox-denied
creating the shared worktree index.lock; retry uses scoped Git escalation under
the existing commit authorization. Final Git outcome and the explicit-path
commit receipt are retained in final-receipt.json. No automatic approval
rejection had occurred at this checkpoint.

Next action belongs to already queued `coordinate-ideal-iterations-1025173122`:
preserve this exact-hash BLOCKED decision, do not treat the candidate as
scientifically admitted, and arrange a bounded isolated correction/re-review
of the categorical numerical ambiguity. No missing predecessor deliverable was
substituted. Existing native, restoring-MCX/main-runner/QPY, structure, static
FT/RUS and break-even ownership stays separate.

This assigned independent review and bounded handoff are complete despite
scientific non-admission. On resumption verify commit, hashes and evidence,
then release complete without repeated tests or duplicate jobs. Full ideal/noisy
iteration studies, saved scientific comparisons and the full paper remain
unfinished. Existing rotation admission is unchanged and confined to its exact
reviewed bytes, numerical bounds and caller obligations: no interval certificate,
ideal-amplitude guarantee, executed-circuit, FT/RUS/noise or paper approval is
added by this review.

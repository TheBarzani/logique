# Ideal-iteration categorical boundary triage

Coordinator `coordinate-ideal-iterations-1025173122`, 26 October 2026.
**Scientific admission BLOCKED. No candidate implementation integrated.**
The bounded correction/review handoff is complete only when the batch records
`bounded_batch_complete=true`. Full paper remains unfinished.

Run: `dump/1026075259-ideal-iteration-coordinator-triage/`.
Git, complete 42-job queue/durable state, server manifest and own completion
records were inspected before work. Initial integration HEAD was
`e46f643dca6e40c08c629430ab170dabc0c0dd5d`, with only user README modifications.
No prior completed handoff for THIS coordinator existed. The supplied parallel
coordinator batch belongs to its completed predecessor, not this task.

Both ideal predecessors are dispatcher **complete**, not dispatcher-blocked.
The independent review's scientific decision is **BLOCKED**. Initial commentary
incorrectly described both as blocked; full state inspection corrected that
status distinction. Existing native jobs remain blocked in their original state
and are outside this slice's ownership.

## Identity and decision

The original candidate correctness commit is
`ed1001b7b32668717f447898503d5d4c3ca6af47`; source checkpoint/HEAD is
`0d14550e66bd94b74aa28773cd5de9f1e8536e12`. Independent review commit is
`dc5938b21bd41fd80905329b6545174f61e46c71`.

| File in original source/review worktree | Before = after SHA-256 |
| --- | --- |
| `src/logique/benchmarks/ideal_iterations.py` | `47c4dca00f43ffbf99e9152b6c006ddefbd0df3cf92207dff84fd264b89c9aaf` |
| `tests/test_ideal_iterations.py` | `8f4856a5f497c620578704350552b75379575ec97e60d41632910cab760022ee` |
| `IDEAL_ITERATIONS_CHECKPOINT.md` | `c5e27ef74740b3d2699e2614a7e9899fa8e95921f898a89bceae03a64ff19427` |
| `IDEAL_ITERATIONS_REVIEW.md` | `1865e17f48314d1bf3cd4f446b8bd2d8ee60e3dc1c36b47637fa6f49c0f9ca65` |

Source/test hashes also match their committed blobs. The full independent review
is copied byte-for-byte to [ideal_iteration_boundary_review.md](ideal_iteration_boundary_review.md).
All 45 saved worker/reviewer evidence inventory hashes and both inventory receipts
were verified. Original source/review worktrees are clean. Both candidate source
and tests remain absent in the integration tree; neither correctness nor
checkpoint-only worker commits were cherry-picked. Only triage/review/audit
documents are integrated and committed in this batch. No build/metric change.

## Independent assessment and counterexamples

For exact uniform support, p=M/N, a=(sqrt(p),sqrt(1-p)), O=diag(-1,1), and
D=2aa^T-I, the signed O-then-D recurrence gives
Pj=sin²((2j+1)asin(sqrt(p))). Set g=sqrt(p)u, b=sqrt(1-p)v, initially u=v=1.
Then u'=(1-2p)u+2(1-p)v and v'=-2pu+(1-2p)v, so Pj=p*u² is exactly rational
when p is rational. This supplies an independent scalar check without a circuit
or floating-point trigonometry deciding the expected peak.

The first-lobe continuous maximum is x=pi/(4theta)-1/2, theta=asin(sqrt(p)).
Its candidate indices floor(x),ceil(x) and nearest-integer first peak are
categorical decisions. Exact ties choose fewer iterations. A small numerical
probability error can still make a categorical decision and required sweep
extent false; a probability tolerance does not redefine that tie convention.

The coordinator independently wrote and executed `coordinator_probe.py`, directly
loading the exact candidate file by path with root src on PYTHONPATH. It imports
no worker test/harness or quantum stack. Exact Fraction recurrence confirms:

- M=18014398509481983, N=36028797018963968: p=1/2-2^-55, strictly P1>P0,P2.
  Candidate reports peak0 and rows0,1, omitting required j2. The same input
  incorrectly accepts max_rows2/max_iterations1. In particular
  P1-P0=8p(1-p)(1-2p)>0; rounding p to 0.5 must not declare an exact tie.
- M=14644660940672623, N=10^17: exact P2>P1,P3. Candidate reports peak1,
  omitting j3. This is near an irrational decision boundary, so named
  rational-angle special cases cannot resolve the general issue.
- M=4503599627370495 or 4503599627370497, N=18014398509481984:
  candidates should be (1,2)/(0,1) because x decreases strictly with p and
  x(1/4)=1. Candidate reports (1,1) in both cases. Peak1 itself remains correct.

The source rejects rounded endpoints 0/1, but not unresolved interior
boundaries. Rounded theta/x and distance comparisons control both metadata and
row/cap decisions. This is the concrete blocker; it is not a claim that ordinary
graph counts or the amplification identity are wrong.

The original 129 passing tests were inspected and their saved results verified,
not rerun. Some candidate expectations reuse the same floating-point x that
causes the defect. The independent review retained 38,157 assertions with one
grouped boundary failure (20 mismatches); its passing targeted reproducer
confirms non-admission. Coordinator targeted probes independently confirm the
four cases above, insufficient-cap acceptance, four boundary/path sanity cases
and elementary cost/random-reference arithmetic. A green blocker-confirmation
probe is not admission.

The remaining source semantics were inspected directly: independent complete
integer predicates reject >12 data bits before product enumeration, with sorted
labels, isolates, loops, empty constraints, one-color convention and no precolors.
R1 uses N=2^(c|V|), R2/R3 N=k^|V| with identical proper-coloring M. R3 edge-only
coloring equivalence requires valid-code support. This ledger assumes exact
uniform A, clean phase O, signed matching D, actual inverse, mapping and restored
workspace; it verifies none of those executed implementations. Known integer
M,N are mandatory. Supplied additive costs use A+j*(2A+O+S0) and C/P for
independent identical complete restarts; random trials have their own basis and
1-(1-p)^r. Unavailable leakage/noise/confidence/routing/circuit costs/T-depth
remain explicit. These observations do not partially admit the rejected module.

## Bounds, failures and preservation

One sequential scalar numerical child at a time, timeout60s, two probe attempts
cumulative 0.093275 seconds, maximum measured child RSS 20,283,392 bytes.
The <=300s cumulative and <=180s per-command limits were respected. Two scalar
amplitudes, at most four rational recurrence steps per adversarial input;
no quantum arrays/dense operators/statevectors, compiler or native invocation.
RSS is measured fixture evidence, not an enforced aggregate OS memory guarantee;
durable state inspection is not full OS process visibility.

`commands.json` retains exact argv, cwd, environment, exits, elapsed/RSS and
bounds. Existing research Python, root src/cache and manifest private executable
were explicit; BLAS/OpenMP/Accelerate threads=1. Initial probe incorrectly used
exact float equality for random-sampling sanity (not a peak check); that assertion
failed. Its script/log/command are preserved with `failed-initial-` prefixes.
Changing only this numerical sanity assertion to abs error <1e-15 yielded a
passing probe; the categorical expectations remain exact Fraction inequalities.
No supplied suite, full tests, build, lint/mypy, notebook, study or replay ran.

Other retained failures: initial combined reads were truncated and required
smaller reads/parsed inventories; an absent top-level ideal glob and absent
previous-run append_queue.py/protected-before.json exploratory reads returned
nonzero without mutation. First new worktree Git ref-lock write was sandbox-denied;
scoped automatic Git escalation succeeded. No automatic approval rejection.

All 1,127 intake protected identities must match at finalization, including root
tracked nonowned files, both original worktrees/evidence, 205 archived-output/
prototype/nested-history baseline identities, README, dependency pins and both
native binaries. Private executable remains
`6aa7357d2f64202584b14b0a14f8fb183379faf5907723cd24bd838b9be14a9a`;
old root binary `ea78b720327f82dd9bbc8c1eb4db63b182c87eaeb7382474ea4d3488457150fa`.
README remains `73c3c1acbfa78ee31abce2e4d1e7af369b02c554b8aca7a5bf3d8b6c293f4e4c`
and is never staged. External index entries/pins and prior job prompt bytes remain
unchanged. No agents/model/Codex launches, API/credits, hardware, push/publishing,
sync/install, dependency or historical-output changes.

## Concrete correction and dispatcher handoff

Exactly three unique jobs are atomically appended, 42 ->45, preserving queue
header, every prior definition and existing bytes before the array closing:
`ideal-boundary-fix-1026075259` (experiments,1800s),
`ideal-boundary-review-1026075259` (critical_review,1200s), and
`coordinate-ideal-boundary-1026075259` (coordinator,1200s), four attempts each.
Fix depends on THIS coordinator completing; review/coordinator use finished
predecessor triage. Two isolated codex/coloring- worktrees were created without
launching work. Fix starts at 0d14550; reviewer starts at e46f643.

The narrow correction must preserve exact accepted counts' relationship to ALL
categorical boundaries, or enforce a justified bounded contract rejecting
unresolved decisions before row construction. It must cover both sides of
rational/irrational boundaries, exact ties, complete peak-plus-one extent,
insufficient caps and ordinary bounded graph inputs with independent rational
expectations. Merely special-casing these reproducers or inflating tolerance is
insufficient. New full source/test hashes require independent review.

The next coordinator may integrate original ed1001b plus validated correction
correctness commits only AFTER reviewing final complete bytes and scientific
scope; worker checkpoint-only commits stay out. Existing native, component-width/
controls/QPY, structure, static FT/RUS and symbolic preparation-break-even scopes
retain owners. Dispatcher alone launches jobs and pushes committed integration
HEAD. No circuit/noise/FT/RUS/paper acceptance follows from an analytical ledger.

Remaining full plan: categorical correction/re-review; executed ideal/noisy
iteration through first peak plus one, leakage/confidence/random sampling/cost
per success; native mappings and blocked coordinator, MC reduction/balancing
profiles/common preprocessing/SAT; structure common lowering/workspace/saved
R1-R3 comparisons; other 3..20-control decompositions or infeasibility, complete
workspace/stage/routing/precision/limits controls and post-pilot protocol freeze;
unsafe older QPY/pilot evidence correction; nine-graph five-method/four-baseline
multilevel strongest-baseline comparisons, ablations and five routing seeds;
meaningful graph static FT under existing exact-hash numerical/caller contract;
separate dynamic RUS and achieved preparation break-even; scaling/DIMACS with
five repetitions, time/memory/timeouts and positive/negative witnesses; full
acceptance/build/provenance/offline notebooks/isolated 135-metric replay; traced
manuscript numbers, reviewer responses, evidence gate and independent final
quantum-correctness/claim/reproducibility reviews. Rotation admission is unchanged:
no interval certificate, ideal-amplitude guarantee or blanket RUS/paper approval.

On THIS coordinator's resumption verify committed triage/review/audit, exact hashes,
protected evidence and unique queued jobs; release complete without repeating
checks, integration or job append. Bounded completion and scientific admission
are distinct; full paper unfinished.

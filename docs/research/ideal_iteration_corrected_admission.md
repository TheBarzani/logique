# Exact-count ideal iteration: bounded coordinator admission

Coordinator `coordinate-ideal-boundary-1026075259`, 26 October 2026.
**ADMITTED for the exact bounded analytical contract below only.** The original
categorical blocker is closed by the corrected bytes, not by the old implementation
alone. Bounded completion is separate from scientific admission. The full paper
remains unfinished; no circuit, noise, FT/RUS or paper acceptance follows.

Run: `dump/1026222142-ideal-boundary-coordinator-triage/`.
Git, all 51 queue definitions, all 45 durable task records and the server manifest
were inspected first. Both correction/review tasks are complete. This coordinator
was the sole durable running job and had no completed own handoff in the manifest,
batch inventory or dispatcher results. The supplied 1026075259 batch belongs to
the predecessor coordinator. Its blocked decision, source, saved failures and
checkpoint are preserved. Native low-T and alias coordinator blocked statuses
are unrelated and unchanged. Durable records do not prove OS process visibility.

## Exact identities and integration

The full 399 source lines and 462 test lines, committed blobs, both new checkpoints
and independent scientific decision were inspected. The independent review is
preserved byte-for-byte as [ideal_iteration_corrected_review.md](ideal_iteration_corrected_review.md),
SHA-256 `94ccdea24cbabb0f446abccf6a3d5be8a92c6d85a2d6bcccb9937bc1ade1a14a`.
Review commit: `97fad3448039df03537fbcd09cfa8f21f7e1205a`.

Only source/test correctness commits were cherry-picked, in order:

| Original | Integrated |
| --- | --- |
| `ed1001b7b32668717f447898503d5d4c3ca6af47` | `4a6dcbaa84c1d7f834286e9f313af117a582d662` |
| `a157c602935457ec2c04eee9e022d119faedcb31` | `a6d8387067a365dfed09a6d3bb20c18fdfab0736` |

Neither worker checkpoint-only commit 0d14550/a6e9592 was integrated. No build or
research-metric changes enter these commits. Both files were absent in root at
intake; final integrated bytes and committed blobs equal the new review:

| File | Final SHA-256 |
| --- | --- |
| `src/logique/benchmarks/ideal_iterations.py` | `7724b76624bc07cf3164abf2c76ddb677c21ccc6cdc86991f8cc09b659b53e40` |
| `tests/test_ideal_iterations.py` | `756c2507cd522815ba155c18abb61c26101475ec69df7e87098475dd36fffa0e` |

Original rejected source/test hashes remain
`47c4dca00f43ffbf99e9152b6c006ddefbd0df3cf92207dff84fd264b89c9aaf` /
`8f4856a5f497c620578704350552b75379575ec97e60d41632910cab760022ee`.
The [historical blocked review](ideal_iteration_boundary_review.md) and
[triage](ideal_iteration_boundary_triage.md) are unchanged, not retroactively admitted.

## Independent analytical assessment

For exact uniform support, write p=M/N, theta=asin(sqrt(p)),
x=pi/(4theta)-1/2. Applying O=diag(-1,1) followed by signed D=2aa^T-I,
a=(sqrt(p),sqrt(1-p)), gives signed amplitudes sin((2j+1)theta) and
cos((2j+1)theta). With g=sqrt(p)u, b=sqrt(1-p)v, the exact first-order
reflection is u'=(1-2p)u+2(1-p)v, v'=-2pu+(1-2p)v, initially u=v=1.
Thus Pj=p*u_j^2 is rational for rational supplied counts.

The production second-order polynomial vj equals
cos((2j+1)theta)/cos(theta). Its FIRST nonpositive value brackets x: vj=0
means x=j; otherwise j-1<x<j. The angular step 2theta<pi cannot skip the
whole negative-cosine interval; the first crossing is below 3pi/2. In the
bracket 0<2j*theta<pi, so
Pj-P(j-1)=sin(4j*theta)*sin(2theta) has the sign of cos(2j*theta).
The second exact polynomial cj computes that sign. Positive selects j;
negative selects j-1; exact zero chooses fewer iterations. This proves general
categorical decisions, including irrational boundaries in p, independently of
binary64 theta/probabilities. It does not optimize later lobes or C/P.

Admission enforces known Python integers excluding bool, N>=1, 0<=M<=N,
N.bit_length()<=64 and a representable interior binary64 fraction for 0<M<N.
The first bracket must occur within min(128,max_iterations); unresolved or
out-of-range inputs reject. Constants use peak0/candidates(0,0)/rows0,1.
Row and iteration caps reject before constructing rows; accepted sweeps include
peak+1 and contain at most130 rows. Exact categorical work is bounded by128
steps and O(128*64)-bit integers regardless of huge caller caps. Every support
with <=12 data bits fits the degree limit (smallest positive p=1/4096).

Displayed probabilities and supplied additive costs remain numerical binary64
values. Their rounding does not decide peak, candidates, ties or sweep extent.
No uniform floating error certificate, interval theorem or ideal preparation
amplitude guarantee is admitted. The random-trial helper retains its separately
reviewed numerical/range contract, not the ideal ledger's new count/degree caps.

Support counting independently checks complete integer coloring predicates,
sorted labels, isolates, loops, empty graphs and one-color domains, rejecting
precolors or >12 data bits before enumeration. R1 uses all binary words; R2/R3
use valid-code support. R3's edge-only coloring equivalence requires that support.
Caller obligations remain exact uniform A, clean marking, signed matching
reflection, mapping, actual inverse and restoration under lowering. This ledger
does not validate their executed implementations or saved QPY.

Costs are supplied additive A+j*(2A+O+S0), with equal A/inverse charges.
C/P assumes independent identical complete program restarts; P=0 is undefined
even with zero cost. Missing/overflowed costs remain explicit. Random trials have
their own basis. Leakage, noise, confidence, routing, measured resources and
T-depth remain unavailable. No graph advantage or achieved break-even is inferred.

## Validation, bounds and failures

All 20 correction and 13 reviewer evidence receipt hashes, 1,432 worker protected
identities and 1,007 reviewer protected identities matched before integration.
The coordinator intake protects 1,791 identities; only its owned audit may change.
README, archives, prototype backups, nested histories, dependency pins, both
native binaries, original checkpoints and failure logs remain unchanged.

A separately authored coordinator first-order rational probe passed **630 cases,
1,819 probability rows and five pre-row rejections**, including all four original
counterexamples, constants/ties, the degree endpoint and 64 seeded large-count
fixtures. It uses at most130 scalar reflection updates; no worker tests/helpers.
The integrated focused suite passed **183 tests**, no skips/deselections.
The preserved independent review harness replayed against integrated bytes with
only OWN/SOURCE roots changed: **277,950 assertions, 6,442 accepted cases,
50,146 exact probability rows, 1,063 rejections, 1,167 graph/regime checks and
256 exact decision boundaries**. No assertions were removed or weakened.
Maximum displayed-probability error 1.5543122344752192e-15 is a fixture observation.

Exact commands, environment, exit codes, time and RSS are in `commands.jsonl`;
`review-replay-adaptations.json` records the two path-only changes. Sequential
existing .venv Python children have timeout180s each, cumulative17.322679s,
maximum measured child RSS44,072,960 bytes, below8GiB. PYTHONPATH resolves to
root src; cache and manifest private native executable are explicit, threads=1.
No quantum arrays/dense operators/statevectors, compiler or native invocation.
RSS is per-child evidence, not an enforced aggregate memory limit. Worker static
checks on these exact bytes were inspected; no redundant static/full-suite,
build, notebook, study, noise, routing or historical replay is claimed.

No numerical failure, timeout or OOM occurred. Expected ValueErrors are successful
rejections. Initial cherry-pick failed creating .git/sequencer under sandbox;
scoped automatic Git escalation succeeded. Initial explicit-document staging also
failed on .git/index.lock; scoped staging escalation succeeded. No automatic approval rejection.
Exploratory .agents/.codex discovery and unmatched ideal glob returned nonzero;
large combined reads were truncated and followed by focused ranges/parsed complete
inventories. A temporary dump pointer with an unsuitable name was immediately
removed; all durable new artifacts use this timestamped run. Original predecessor
failed probes and 20 categorical mismatches remain intact.

## Concrete handoff and remaining scope

No new jobs are appended: six existing unique jobs already own preparation-success
and component-instruction acceptance with independent reviews/coordinators.
Dispatcher alone releases those queued workers and pushes committed integration
HEAD; this coordinator launches/pushes nothing and edits no live state. Queue
header, all 51 definitions and prior prompt bytes remain immutable. Native,
controls/QPY, structure and static FT/RUS scopes retain ownership.

Next ideal-study work requires a separate bounded executed-circuit validation
slice: compare actual matching-A oracle/diffusion iterations through peak+1 to
this ledger on declared small fixtures, record resource exclusions before arrays,
and obtain independent review. It is not silently satisfied by this admission or
dispatched here. Leakage/noise/confidence/random-sampling/cost-per-success studies,
meaningful graph FT under unchanged rotation contract, dynamic RUS/achieved
break-even, native mappings/MC reduction/balancing/SAT, structure common lowering/
workspace/comparisons, full controls/post-pilot freeze, affected old QPY review,
nine-graph R1/R2/R3 five-method/four-baseline multilevel strongest-baseline/ablation/
five-routing-seed studies, five-repeat scaling/DIMACS with witnesses/resources,
full acceptance/build/provenance/offline notebooks/isolated 135-metric replay,
traced manuscript numbers/reviewer responses/evidence gate and independent final
correctness/claim/reproducibility reviews remain open.

Rotation admission remains exactly [rotation_norm_admission.md](rotation_norm_admission.md),
with its exact hashes, numerical contract and all caller obligations. No interval,
ideal-amplitude, broader static FT/RUS or blanket paper approval is added.
This bounded handoff is complete when batch.json records bounded_batch_complete
and committed correctness/audit identities. On resumption verify/release complete
without repeated tests, integration, launches or duplicate jobs.

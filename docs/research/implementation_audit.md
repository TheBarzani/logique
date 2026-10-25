# Coloring revision implementation audit

Audited on 25 October 2026 from transferred HEAD `3ec511d` on
`coloring-paper-revamp-codex`. The operating plan is
[the server execution plan](../coloring-paper-revamp-codex-plan.md), including its
26 October–1 November schedule. This audit does not add roadmap work.

## Existing implementation reused

| Task | Current implementation | Evidence and remaining work |
| --- | --- | --- |
| 1 | Notebook reference repairs (`e066c39`); native build provenance (`3a96dff`); existing claim audit | All maintained notebook sources currently have empty outputs and execution counts. Illustrative cells 0, 34, 36, 39–43 already distinguish matching and historical reflections and check zero leakage only for the former. Revision sources and nested histories were transferred. Sources are now tracked after verified history preservation; environment reporting reads the selected bridge build record (`7daf835`, `b34a22b`). |
| 2 | Config loader, synthesis/comparison/phase runners; normalized historical baseline adapter; coherent monomial verification | Controlled R1–R3 assembly, per-input witnesses, iterations/seeds, explicit precolor removal, QPY export and validated baseline components are implemented (`94665c0`, `4fa714c`, `8058826`). Unsupported precision/routing/profile/limit controls are rejected, not silently ignored. Stage timing and qubit-role classification still need extension. |
| 3 | `costs.py` (`2ed650b`, `2848f21`), `routing.py` (`059e865`), `mcx_decompositions.ipynb` (`3ec511d`) | Explicit restoring and throwaway constructions, exact gadgets, dependency-graph T-depth, Dutta analytical reference, leading-order rotation estimate, success/iteration helpers, five-seed routing, and isolated 3–20-control study exist. Quantum smoke tests passed. Paired monomial compute-Z-uncompute lowering now holds scratch and uses the actual expanded inverse (`8f3a08d`). Whole-algorithm emitted rotation synthesis is under implementation/review. Gray-code rows above ten controls still need bounded execution or explicit infeasibility records; the existing notebook caps them at ten. |
| 4 | Existing all-bitstrings comparison and phase-oracle runner | The K3/K5/myciel3 logical pilot completed 144 validated cases with 18 explicit original-baseline exclusions and no failures. Every completed case exercised a marked input. All 720 metric rows were reproduced from saved QPY; per-instance strongest-baseline summaries are saved separately (`ba6b5b8`). Full nine-graph/multilevel evaluation, complete workspace classification and protocol freeze remain open; these pilot results are not headline evidence. |
| 5 | Five maintained synthesis methods, native bridge and standalone balancing tool | Balanced AND/OR encoder association is opt-in and validated against independent predicates (`e6f3b45`). The standalone tool supports XAG, algebraic and ESOP passes with per-pass and serialization equivalence checks (`90df410`). Exhaustive pinned-action serialization and opt-in shared native preprocessing are integrated (`fcc52d4`, `7aeacb6`); omitted controls preserve legacy defaults. Opt-in in-place Bennett/eager mappings are integrated after emitted-action review (`ce93291`); low-T and other mappings, MC reduction/profile integration, SAT pebbling and structure-aware scheduled oracles remain open. Dependency pins remain fixed. |
| 6 | Per-circuit Clifford+T gadgets; hash-bound admitted static rotation compiler (`54c58c3`); independent derivation/RUS review | The independent reviews establish the unitary composition and separate RUS derivation, with explicit limitations. The previously reviewed repair admits a near-unitary matrix that violates its requested search budget. The corrected matrix-admission/norm implementation is now admitted and integrated for the restricted numerical contract in [the independent admission](rotation_norm_admission.md). The root prototype was preserved before replacement. This is not ideal-amplitude certification or RUS admission. FT comparisons, complete-search experiments and preparation break-even results remain open. |
| 7 | Correct matching-reflection Grover wrapper and small independent amplification regression | Complete ideal/noisy iteration sweeps, leakage, confidence intervals and random-sampling/cost-per-success study remain open. |
| 8 | General benchmark runner and fixed 180-second native timeout | The three requested legacy inputs were restored byte-for-byte from `95f6167`, with hashes (`040d420`). Remaining source inputs, controlled families, five repetitions, stage memory/timeouts and larger-instance witnesses remain open. The restored color parameters are historical inputs, not verified chromatic-number claims. |

## Server evidence

The home server has 8 GiB RAM, eight logical CPUs and AC power. The initial
numerical policy is one memory-heavy job and one compiler process. Python 3.10.22,
Qiskit 2.1.1 and the locked research extras were installed through `tools/sync.py`.
CMake 3.31.6 and Ninja 1.11.1.4 are isolated build tools. The bridge built with
AppleClang 21.0.0; its build record includes the declared Caterpillar reference
and source hashes. No dependency revisions were changed.

The initial quantum smoke selection passed 109 tests (coloring, synthesis,
MCX/costs, routing, and notebook-source checks). Two notebook execution checks
initially failed because the sandbox blocked Jupyter socket binding; both passed
on their separate rerun with local socket access.

Execution logs, task/session IDs, tests and next actions are in
`dump/1024235721-coloring-paper-server-checkpoint/manifest.json`. No new comparison
or scalability result should be inferred from a passing toolkit test.

## Source-history preservation

Before source integration, complete nested `main` histories were bundled and
verified in `nested-histories/manuscript.bundle` and `research.bundle` under the
checkpoint. Their original Git metadata was moved alongside those bundles.
Original source files and generated PDFs remain on disk; generated LaTeX outputs
are excluded from parent tracking. Historical `experiments/manuscript/` artifacts
are unchanged.

## Additional execution evidence

- `dump/1024235721-coloring-paper-server-checkpoint/historical-replay/`
  reproduced all 135 archived metrics inside an isolated Qiskit environment.
  The corrected research environment was checked to remain unpatched.
- The full pre-pilot suite passed 333 tests with six explicit skips; Black, Ruff,
  mypy and package build passed. Fetching the pinned EPFL inputs subsequently
  enabled and passed their skipped regressions. The historical patch remains
  intentionally absent from the corrected environment.
- `dump/1025012448-coloring-study/` contains the logical pilot and all 720 saved
  circuit metric rows; `comparison/` has 1,350 per-instance metric comparisons
  and 450 separately matched summaries. Seeds, iteration counts, components and
  metric levels are never combined implicitly.
- Graph and Boolean tutorial notebooks and the existing bounded MCX study ran
  offline with unchanged sources. The illustrative notebook's historical-cost
  section requires the isolated historical interpreter, which was used for its
  successful rerun. Logs retain the initial expected failure in the unpatched
  environment. No hardware or remote circuit jobs were run.
- Results-independent manuscript corrections cover matching diffusion, solution
  fraction, valid codes versus proper colorings, restoration contracts, logical
  Clifford+T accounting and full-search gate-count composition (`62fb1af`).
  The old abstract/evaluation/contribution claims still await the evidence gate;
  no final revised manuscript or superiority claim is asserted.

## Rotation integration gate: 25 October bounded batch

Integration HEAD at intake was `1e1f525`. The two repair files exactly match
the SHA-256 identities in the [independent re-review](task6_rotation_rereview.md):
`rotations.py` = `5a811a35f2f3d6203d68bb441213d521883b8b56235054df7384fd00db679457`,
`test_rotations.py` = `5513b65b67831e9100e76db00fadbbe22890da125f1abe8492d65c026cd924a1`.
The review task completed, but its scientific decision is **blocked**. Neither
repair file was integrated. The different untracked root prototype and the
user's README changes were preserved byte-for-byte.

The independently rerun 37-test review suite reproduces the accepted numeric
matrix counterexample: A = (1 + 1e-6) I, O = S0 = Z, j = 2. Actual error is
`5.000009999589494e-6`, reported bound `5.000000212751493e-6`, and a requested
budget of `5.000005e-6` is exceeded. Two passing review tests deliberately
confirm blockers, so this green suite does not admit the rotation contract.
Unitary-only telescoping does not bound products of admitted nonunitary numeric
targets. The next correction must reject such inputs or account for their norms;
increasing a fixed floating-point margin is not an acceptable resolution.

The manuscript findings in that re-review concern the older repair worktree
(HEAD `90df410`). Integration already contains `eef059d`: zero reflection is
`-X^n MCZ X^n`, A is initialized once with O,D repeated, full data preparation
is specified, p=0 means no prepared marked amplitude, and the first-peak
floor/ceiling candidates and tie convention are explicit. This context difference
was checked directly; a new independent review must inspect the current text.
It does not remove the matrix blocker or grant manuscript approval.

Unblocked balancing exchange, independent graph predicates and dispatcher
regressions passed **100 tests**, with both native tools configured and no skips.
One numerical process ran at a time using the existing research interpreter;
the independent review used the repair source via explicit PYTHONPATH. No new
comparison metrics, historical outputs or dependency pins were changed.

Identity records, the preserved review suite and both test logs are in
`dump/1025024643-coloring-integration-gate/`. The server checkpoint manifest
records the append-only dispatcher handoff. Shared preprocessing/mappings,
MC reduction/balancing integration, SAT/structure scheduling, decomposition,
workspace/routing/precision controls, post-pilot protocol freeze, complete-search
FT and separate RUS accounting, iteration/noise and scaling studies, full
comparisons and evidence-gated manuscript/final reviews all remain in scope.

## Native foundation admission: 25 October bounded batch

Dispatcher task `native-contract-1025024643` finished **complete**, not blocked;
its checkpoint also reports bounded completion. This coordinator inspected the
two owned implementation commits and admitted them as `fcc52d4` (action payload
correctness) and `7aeacb6` (shared preprocessing bridge/API and optional probe
build support). No research metrics or scientific superiority claims changed.
The original [foundation checkpoint](native_contract_foundation.md) records the
private builds, exact contract, test exclusions and outstanding mapping limits.

The independent rerun checked source, executable and pinned-header SHA-256
identities, all **13 exact rows across seven action variants**, **132 Python
tests** (27 deliberately deselected, no skips), and **45/45 intake/new legacy
comparisons**. Integrated-tree regressions then passed **188 tests**, including
native contracts, coloring, balancing and dispatcher behavior, with no skips.
Black, Ruff, configured mypy and diff checks passed. Tests ran sequentially in
the existing research environment; the largest recorded child RSS was below
0.3 GiB. A Darwin address-space-limit attempt failed before execution; bounded
fixtures and measured RSS, rather than that unavailable limit, support the
memory evidence. Logs and command records are in
`dump/1025030802-native-integration/`.

Common preprocessing selects the shared XAG after output projection and before
representation conversion, with explicit ordered before/after evidence. An
explicit request requires native confirmation. Omission keeps the unrefactored
AIG Bennett and refactored other methods; historical expression synthesis stays
on its original construction. The complete action visitor retains optional
leaves, cell truth tables, in-place targets, buffers and ordered level/cone
payloads. This admits serialization and the two preprocessing policies only;
it does not certify additional strategies' emitted circuits. The legacy
`is_nary_xor` shim remains a separate level-mapping concern.

The next bounded dispatcher handoff is in-place Bennett/eager mapping in an
isolated worktree, followed by coordinator triage including blocked status.
Existing rotation correction/review jobs are retained without duplicates;
root prototype files and README stay byte-identical. Static FT remains blocked
until exact reviewed hashes **and explicit scientific admission** match the
declared contract. Native foundation admission does not change that gate.

Remaining full scope: low-T/low-depth and other mappings; MC reduction and
balancing profile integration; SAT pebbling; structure-aware sequential and
parallel schedules; decomposition/workspace/routing/precision controls and
post-pilot protocol freeze; complete-search static FT after review, separate
dynamic/RUS accounting and preparation break-even; ideal/noisy iteration,
leakage, confidence intervals and random-sampling/cost-per-success studies;
scaling families and selected DIMACS with five repeats, time/memory and positive
witnesses; full nine-graph/multilevel strongest-baseline comparisons; manuscript
evidence gate and independent final reviews. The bounded integration is complete;
the full paper remains unfinished.

## Rotation norm correction triage: 25 October bounded batch

Task `rotation-norm-1025024643` completed its assigned implementation. Its
checkpoint and actual candidate bytes agree:
`rotations.py` = `5e8d08c69305100bd892c25deb748415cd7de1f530b4654da4cdb801dea4e595`,
`test_rotations.py` = `88412c34913b160d1ebc857e833646bd5e7a7e527b654f7cb43bf439b776db77`.
No rotation source was integrated or staged. Scientific admission remains
pending in already queued `rotation-norm-review-1025024643`.

The candidate narrows one-qubit numeric matrix admission to measured spectral
unitarity defect at most `64*float64_eps` (`1.4210854715202004e-14`). Original
numeric targets are retained; component and repeated-search norm products scale
the error accounting and reduce the budget before residual-rotation allocation.
These remain floating-point engineering bounds, not interval certificates.
The review must admit this declared restriction and derivation explicitly.

Coordinator reruns passed **255 tests, 2 deliberately deselected**, comprising
187 candidate regressions and 68 adapted review/norm probes. The deselections
are the old acceptance-of-bad-matrix and old-manuscript blocker-confirming
assertions; positive rejection and direct original-target probes cover the
corrected behavior. These adapted tests originate with the implementation
handoff and do not replace independent scientific review. Import resolution was
verified against the candidate worktree. The current integration and candidate
manuscript bytes also match, including `eef059d` corrections. Independent
unblocked balancing, dispatcher and coloring regressions passed **100 tests**,
without skips. Sequential numerical processes used the existing research
environment and explicit native/cache paths, with maximum child RSS
**199,442,432 bytes**. Commands, logs and preservation identities are in
`dump/1025033231-rotation-norm-triage/`.

The existing reviewer prompt reads the actual corrected files and checkpoint,
requires before/after hashes and explicit scientific admission, and can triage a
blocked predecessor through `dependency_policy="finished"`. The already queued
`coordinate-rotation-review-1025024643` must retain the gate if review blocks
and append a bounded isolated correction/re-review with coordinator follow-ups
when justified. Neither queue header nor any job definition was changed; no
duplicate jobs were appended. Native in-place/eager mapping and its coordinator
remain queued independently. README edits, root prototypes, archived manuscript
files, preserved nested histories and dependency pins remain unchanged.

This assigned triage and handoff are complete. Do not repeatedly dispatch this
finished batch. Full scope remains: all additional native mappings and their
emitted-circuit validation; MC reduction/balancing profiles; SAT pebbling;
structure-aware sequential/parallel oracles; decomposition, workspace, routing,
precision and stage-statistics controls; post-pilot protocol freeze; full
nine-graph/multilevel strongest-baseline comparisons; complete-search static FT
after scientific admission, separate RUS accounting and preparation break-even;
ideal/noisy iteration, leakage, confidence intervals and random-sampling costs;
controlled scaling and selected DIMACS with five repeats, time/memory/timeout
records and positive witnesses; all acceptance checks, offline notebooks,
historical replay and evidence-gated manuscript/final independent reviews.
The full paper remains unfinished.

## Rotation norm scientific admission: bounded review integration

Task `rotation-norm-review-1025024643` is complete and explicitly **ADMITTED for
static FT comparison experiments under its declared numerical contract**. Actual
source and integrated bytes match both reviewed identities:
`rotations.py` = `5e8d08c69305100bd892c25deb748415cd7de1f530b4654da4cdb801dea4e595`,
`test_rotations.py` = `88412c34913b160d1ebc857e833646bd5e7a7e527b654f7cb43bf439b776db77`.
Only those two files entered correctness commit `54c58c3`; no build or metric
change is mixed in. The [full independent decision](rotation_norm_admission.md)
is preserved byte-for-byte, including executable probes and caller obligations.

Coordinator replay passed 187 candidate regressions and all 37 previous plus
79 additional independent cases. Integrated regressions passed **425 tests**,
without skips; Black, Ruff, configured mypy and diff checks passed. Sequential
research-interpreter jobs used explicit native/cache paths and at most
253,444,096 bytes recorded child RSS, below 8 GiB. Exact commands and logs are in
`dump/1025034429-rotation-admission/validation.json`. The 37-case replay retains
explicit replacements of obsolete blocker assertions, as recorded by the review.

This closes the old matrix blocker only for one-qubit matrices whose measured
unitarity defect is at most 64*float64_eps, original numeric targets, norm-aware
whole-search budgeting, numerical (not interval-certified) bounds, bounded SK,
precision floor 1e-12 and the reviewed recursive/angle limits. The caller must
prove clean phase-oracle semantics, data mapping, signed zero reflection and
workspace restoration; lower MCX explicitly, preserve scalar phases and use the
actual emitted inverse. Failed precision must remain an explicit failure.
Composite preparation targets are recursive definitions, not certified ideal
amplitude vectors. Static FT admission is separate from RUS/dynamic accounting
and paper acceptance. Broader targets or changed compiler bytes need re-review.

Before replacement both unapproved root prototype files were copied byte-for-byte
to this run's `prototype/` directory and hash-verified. README edits, archived
results, nested histories and dependency pins remain unchanged. The existing
native in-place/eager and coordinator jobs retain their scopes. New isolated
bounded controls/stage-provenance, structure-oracle and static-FT-pilot jobs each
have a coordinator follow-up; queue header and all prior entries stay immutable.
The run checkpoint and server manifest record exact handoff identities.

This assigned integration batch is complete once the recorded handoff is appended.
Do not repeat it on resumption. Full remaining scope: additional native mappings
and emitted-circuit validation; MC reduction/balancing profiles and SAT pebbling;
structure-aware sequential/parallel schedules and workspace trade-offs; full
decomposition/workspace/routing/precision/limits controls and stage statistics;
post-pilot protocol freeze; nine-graph R1/R2/R3 multilevel strongest-baseline
comparisons with saved circuits and five routing seeds; complete-search static
FT comparisons under the admitted contract, separate RUS and preparation
break-even; ideal/noisy iteration through first maximum plus one, leakage,
confidence intervals, random-sampling costs; controlled scaling and selected
DIMACS with five repetitions, time/memory/timeouts and larger positive witnesses;
full research checks, offline notebooks, isolated 135-metric historical replay,
claim-evidence gate, reviewer responses and independent final correctness/claim
reviews. The full paper remains unfinished.

## In-place Bennett and eager admission: bounded mapping integration

Task `native-inplace-eager-1025030802` and its isolated checkpoint both report
**complete**, with no remaining blocker for the declared mapping contract.
Coordinator `coordinate-mapping-1025030802` had no prior completed handoff.
Only the six owned files of implementation `3cd712e` were cherry-picked as
`ce93291`; the original checkpoint is preserved byte-for-byte in
[native_mapping_inplace_eager.md](native_mapping_inplace_eager.md). No build,
dependency or research-metric change was mixed into that correctness commit.

Admission covers opt-in actual pinned Bennett, in-place Bennett and eager
classes on AIG/XAG Bennett methods. Input allocation includes unused PIs and
preserves order through common preprocessing/conversion. In-place targets are
node indices resolved through live qubit stacks; reverse XOR restoration is
required before ancestor uncomputation. The stale in-place stack entry is not
read again in these once-computed, non-recomputing schedules. Eager retains
shared/PO fanout and releases cleaned wires before later output computations.
Actual gates, not just serialized steps, exercise both input and gate-node
in-place targets, nested aliases and early eager reuse. AIG has no XOR in-place
steps. A complemented PI output may change a raw input; arbitrary-target XOR
and selected-output phase wrappers restore inputs/workspace. General mixed or
recomputing schedules and level actions are outside admission.

Independent candidate replay passed **353 tests, 27 explicitly deselected,
no skips**. The exclusions retain the handoff's <=5-qubit dense-check bound;
aliases/constants and larger fixtures receive compositional monomial coverage.
A separately written seeded source-DAG evaluator and scalar circuit interpreter
checked **144 mapping cases / 71,424 coherent checks**, across both common
policies and all three strategies on AIG/XAG: five declared inputs with an
unused PI, asymmetric ordering, shared intermediate POs, complemented PIs,
repeated projections, every joint XOR-target pattern and every selected phase
output. Twelve actual in-place actions and 32 early-cleanup schedules were
exercised. These are bounded correctness fixtures, not performance evidence.
The independent harness initially applied Z unconditionally; that harness bug
was corrected. A retry also used the root's pre-integration API and rejected the
new keyword; the subsequent candidate run used the correct explicit PYTHONPATH.
Both failed logs are retained; neither was a native correctness failure.

All **135 exact omitted-strategy native comparisons** and **three historical
expression comparisons** pass against the hash-verified foundation executable,
excluding only timing and additive mapping evidence. The compiled action probe
passes 13 exact rows across seven variants; it is supporting serialization
coverage only. Integrated-tree replay passed **370 tests, 27 deselected, no
skips**. Relevant Black/Ruff, configured five-file mypy and diff checks pass.
Source, binary, pinned headers, tool and compatibility-overlay identities were
verified before reusing the private executable; root binaries were untouched.
Sequential local research-Python jobs used explicit worktree source, cache and
native paths; maximum child RSS **251,592,704 bytes**. No compiler rebuild or
OS address-space guarantee is claimed. Evidence is in
`dump/1025072819-native-mapping-triage/`.

All 158 original protected root/history/archive identities, plus the two saved
unapproved rotation prototypes, match this batch's intake. README, current
rotation source/tests, prototype backups, archived manuscript outputs, nested
histories, pins and root executable remain byte-identical. The older native
foundation batch's blocked FT statement is historical: the separate exact-hash
scientific admission is recorded in `rotation_norm_admission.md` and the server
manifest. Its gate and all caller obligations are preserved without extension;
this mapping work grants no rotation/FT, RUS or scientific performance admission.

The entire 17-job queue was inspected before appending exactly two unique jobs:
`native-xag-lowt-1025072819` (native profile, 1800 seconds, four attempts) and
`coordinate-xag-lowt-1025072819` (coordinator, 1200 seconds, four attempts,
finished-dependency triage). Existing header and entries are immutable. The
worker starts at `ce93291` in isolated `codex/coloring-xag-lowt-1025072819` and
owns only pinned `caterpillar::xag_mapping_strategy` via opt-in `xag_low_t` on
XAG Bennett, with emitted-action correctness/legacy acceptance. Fast-low-T,
low-depth/level paths, SAT and measurement-assisted free uncomputation are
excluded. Its checkpoint is `XAG_LOWT_CHECKPOINT.md`; the coordinator must
independently admit it or append a concrete correction. Dispatcher exclusively
owns launches. This bounded integration and handoff are complete; release on
resumption without re-integrating or appending duplicates.

Full remaining scope: the queued low-T contract and subsequent fast-low-T,
low-depth and other mapping admission; MC reduction and balancing optimization
profiles; SAT pebbling; queued structure-aware sequential/parallel oracles and
workspace trade-offs; decomposition/workspace/routing/precision/limits controls,
stage statistics and post-pilot protocol freeze; nine-graph R1/R2/R3 multilevel
strongest-baseline comparisons, saved circuits, five routed seeds and ablations;
complete-search static FT under exact-byte scientific admission and caller
obligations (pilot queued), separate dynamic/RUS and preparation break-even;
ideal/noisy iteration through first maximum plus one, leakage, confidence
intervals, random sampling and cost per success; controlled scaling and selected
DIMACS with five repeats, stage memory/timeouts and larger positive witnesses;
full research acceptance, provenance/build checks, offline notebooks and isolated
135-metric replay; traced manuscript numbers, reviewer responses, evidence gate
and independent correctness/claim/final reviews. The full paper remains open.

## Stage controls triage: blocked saved-QPY semantics

The completed worker `stage-controls-1025034429` supplied owned source/tests
in `71ed6a4`, with truthful additive timing/statistics and reserved-wire
provenance. Actual hashes match its checkpoint. Coordinator
`coordinate-stage-controls-1025034429` independently reran **79 tests** (31
bounded deselections, no skips), relevant Black/Ruff, all **240 saved metric
rows**, 24 independent network checks and 18 predicate/restoration cases.
**Neither candidate file is integrated.**

The [independent semantic review](stage_controls_qpy_review.md) blocks admission:
installed Qiskit 2.1.1 QPY readback changes inverse `StatePreparation` into its
forward form. Minimal two-qubit operator distance is `1.9986497753173806`.
Original/saved preparation and diffusion comparisons found **16 failures among
48** bounded operators, maximum distance `1.93829197958024`, in R2/R3 diffusion.
Wider search semantics are not admitted by reproduced counts. This predates
the candidate; earlier pilot artifacts remain preserved and their affected
serialization paths need review before paper evidence admission. Width, gate
and depth totals are unchanged in the 240-row tiny comparison, but 24 gate-type
maps differ; trace representation/metric changes separately from correctness.

Evidence, exact hashes, failures, resource bounds and queue handoff are in
`dump/1025074732-stage-controls-triage/batch.json`. Next is bounded correction
in isolated `codex/coloring-qpy-correction-1025074732`, independent isolated
review and coordinator triage, including blocked status. Queue header and all
prior definitions stay unchanged; existing native, structure and static-FT
jobs retain ownership. Dispatcher exclusively launches the three appended
jobs. This bounded triage is complete; do not repeatedly dispatch its handoff.
The full paper remains unfinished.

After QPY admission, restoring decomposition/fresh-scratch controls are next.
Remaining workspace, routing, precision/limits and instrumentation controls,
post-pilot freeze, nine-graph/multilevel comparisons, separate RUS/break-even,
iteration/noise/scaling, evidence-gated manuscript and independent final reviews
remain in scope. Rotation admission retains the existing exact hashes,
numerical contract and caller semantics; no broader FT, interval,
ideal-amplitude, RUS or paper approval is inferred here.

## Sequential structure admission: bounded coordinator triage

Worker `structure-oracle-1025034429` completed its foundation; this coordinator
had no prior completed batch/handoff. Only its two owned correctness files
were integrated from `ed6f8a3` as `0a56cd2`. The exact-byte contract and
independent proof assessment are in
[structure_oracle_admission.md](structure_oracle_admission.md). Admission covers
logical sequential complete/domain-free predicates, arbitrary-target XOR,
phase/restoration on clean workspace and explicit disjoint workspace roles.
It does not admit emitted parallel depth, lowered MCX resources, saved-study
semantics, research superiority, static FT extensions or paper claims.

Candidate and integrated focused suites each passed **84 tests**, no skips or
deselections, plus relevant Black/Ruff and one-file mypy. Separate seeded direct
predicate/scalar-gate probes each passed **222 graph/policy cases**, **27,756
XOR/phase checks** and **2,728 comparator checks**, including compute boundaries
and independently calculated workspace/schedule requirements. The comparator
and prefix proof establishes coherent clean-subspace action; bounded testing
supplements it. Dense operators remain <=4 qubits, statevectors <=5; wider
checks use integer monomial evaluation. Maximum recorded child RSS upper bound
was **93,077,504 bytes**. Exact commands, logs, hashes, failures and preservation
evidence are in `dump/1025081040-structure-oracle-triage/batch.json`.

All 165 protected identities and external index/gitlinks match intake. Initial
sandbox-denied Git metadata writes succeeded under scoped automatic escalation;
`ps` remained unavailable. No numerical/static failure or model launch occurred.
The whole 22-job queue was inspected and exactly two unique bounded jobs appended
atomically, with immutable header/prior definitions: isolated emitted-parallel
structure implementation and coordinator triage, including blocked status.
These require private concurrent scratch, emitted dependency evidence and exact
restoration. Existing native mapping, QPY/control correction and static FT jobs
retain their scopes. This bounded batch/handoff is complete and must not be
repeated on resumption. Full paper remains unfinished.

Remaining scope: emitted parallel structure and later comparison integration;
additional native mappings, MC reduction/balancing profiles and SAT; blocked
QPY semantics and affected pilot review; all decomposition/workspace/routing/
precision/limits controls and post-pilot protocol freeze; full nine-graph R1/R2/R3
multilevel strongest-baseline comparisons with five routing seeds and ablations;
whole-search static FT under exact admitted hashes/caller obligations, separate
RUS/dynamic and preparation break-even; ideal/noisy iteration through first
maximum plus one, leakage/confidence intervals/random sampling/cost per success;
scaling and selected DIMACS with five repetitions and positive/negative witnesses;
full research/static/build/provenance checks, offline notebooks and isolated
135-metric replay; evidence-gated manuscript, traced numbers, reviewer responses
and independent final correctness/claim/reproducibility reviews. Rotation
admission is unchanged; no interval/ideal-amplitude/RUS/paper approval is added.

## Static FT pilot: bounded coordinator integration

`static-ft-pilot-1025034429` completed; its coordinator had no prior completed
batch/handoff. Only owned source/tests from `daf4b21` were integrated as
`28413d8`, separately from this evidence record. The exact bytes, caller
semantics, failure/status contract and limitations are in
[static_ft_pilot_admission.md](static_ft_pilot_admission.md).

Independent candidate replay passed **211 tests** without skips/deselections;
integrated replay passed all **24 harness tests**. Relevant Black/Ruff and
focused one-file mypy pass. Separately written coordinator readback in both
checkouts verified **61 QPY artifacts / seven rows**, **28 original phase
columns**, ten asymmetric contract fixtures, signed S0, actual emitted inverse,
full assembly, raw T-count/dependency T-depth and direct event probabilities.
Largest assembly error: **1.4763228132311763e-14**. All seven original-target
errors satisfy declared bounds without added tolerance in independent readback.

The edge graph explicitly fails at 13 native wires before dense construction.
All rows use one isolated vertex k=3: **NO GRAPH COMPARISON**. This is numerical
assembly evidence only; no ideal-amplitude certificate, interval theorem,
preparation break-even, protocol freeze, RUS or paper admission. Source QPY
expansion is local to this harness; the separately blocked main-runner QPY
candidate remains held. `bounded_complete` describes finishing the schedule,
not successful rows; consumers must inspect each persisted outcome.

Evidence and exact hashes are in `dump/1025083656-static-ft-pilot-triage/`.
Sequential research-interpreter commands used explicit src/native/cache paths,
180-second supervisors and single BLAS/OpenMP threads. Dense operators <=4,
statevectors <=5; maximum recorded child RSS **222,330,880 bytes**. No rebuild,
sync/install or broader numerical experiment ran. `ps` was sandbox-denied;
scoped Git escalation succeeded after index/ref-write denials.

The whole 24-job queue was reviewed. Next is one separate analytical RUS ledger
slice, with isolated critical review and coordinator triage, including blocked
status. It must distinguish arbitrary-input instruments, inverse semantics,
expected costs and capped failures; no dynamic execution or static substitution.
Existing native, QPY-controls and parallel-structure jobs retain ownership.
Queue header and prior definitions remain immutable. This batch/handoff is
complete and must not be repeated on resumption; dispatcher alone launches work.

Remaining: meaningful static FT graph-domain admission/comparisons; all full
controls and post-pilot freeze; full nine-graph R1/R2/R3 multilevel comparisons
with five routed seeds, strongest-baseline aggregation and ablations; remaining
native mappings, MC reduction/balancing profiles and SAT; parallel structure;
separate RUS and preparation break-even; iteration/noise/leakage/confidence and
random-sampling/cost-per-success; scaling/DIMACS with five repeats and explicit
positive/negative witnesses; full research/static/build/provenance checks,
offline notebooks and isolated historical replay; traced manuscript numbers,
reviewer responses, evidence gate and independent final reviews. Full paper
remains unfinished; rotation admission and its exact hashes are unchanged.

## XAG low-T triage: pinned physical-alias blocker

`native-xag-lowt-1025072819` is dispatcher-blocked after four attempts. Its
isolated `XAG_LOWT_CHECKPOINT.md` and checkpoint-only commit `09020b0` confirm
that the opt-in was not delivered: all maintained source files were restored to
`ce93291`. This assigned coordinator had no previous completed batch; the
supplied `1025072819-native-mapping-triage/batch.json` belongs to its predecessor.
**No implementation or checkpoint-only commit was cherry-picked.**

The [independent blocker review](native_xag_lowt_blocker_review.md) audits the
actual pinned non-template XAG strategy, LHRS node-stack/buffer/in-place payloads
and emitted static gates. Equal XOR cones alias both AND controls to one wire;
common `none` emits invalid `[0,0]` controls with equal or contradictory
polarities. Both are independently reproduced and correctly rejected by Python.
Common `refactoring` passes those fixtures, without discharging `none`.
Independent source/scalar/API-wrapper checks passed **1,760 coherent checks** on
valid candidate and admitted predecessor fixtures, **105 exact omitted-control
comparisons** across all five methods and three policies, and **three historical
expression comparisons**. Two initial harness-only Verilog parse failures and
their corrected passing replay are retained. No dense quantum allocation,
rebuild, broad-suite or scientific-performance claim is made. Maximum measured
child RSS: **72,220,672 bytes**; sequential existing research-Python processes,
explicit src/native/cache, single threads and 180-second supervisor bounds.

The static emitter actually executes inverse ANDs: the nested fixture emits five
Toffolis, not a measurement-assisted zero-T cleanup. Serializer completeness and
passing ordinary fixtures do not prove the alias invariant. Low-T remains
**unadmitted**. Original evidence (93 files), 52 source/build identities and 160
protected root/archive/history/prototype hashes match; README, rotations,
prototype backups, binary/pins and existing research evidence remain unchanged.
Scoped Git escalation created two isolated worktrees after an initial ref-lock
sandbox denial. No models/agents/API/paid fallback/hardware/push/sync ran.

The entire 27-job queue was inspected for scope and IDs. Append only
`native-xag-alias-fix-1025121607` (native, 1800s),
`native-xag-alias-review-1025121607` (critical_review, 1200s), and
`coordinate-xag-alias-1025121607` (coordinator, 1200s), four attempts each.
Review/coordinator use finished-predecessor triage. Existing queue header,
definitions and prompt bytes stay immutable. The narrow correction must derive
explicit physical literal normalization, preserve exact pinned class/defaults,
fail closed on target aliases, exercise both preprocessing policies and coherent
restoration, and receive independent exact-hash review. No next unrelated
mapping/MC/balancing slice is added. Evidence, final preservation and exact
handoff: `dump/1025121607-xag-lowt-coordinator-triage/batch.json`.
This bounded batch/handoff is complete; verify and release on resumption without
repeating tests/integration or appending duplicates. Dispatcher owns launches.

Full remaining scope: correction and independent admission of pinned low-T;
fast-low-T, low-depth/level/other mapping contracts, MC reduction/balancing
profiles, common preprocessing studies and SAT/qubit budgets; parallel structure
schedules and workspace trade-offs; held main-runner QPY correction/review,
decomposition policies through 20 controls or explicit infeasibility, workspace,
stage/routing/precision/resource controls and post-pilot freeze; nine-graph
R1/R2/R3 multilevel saved-circuit comparisons, strongest-baseline aggregation,
ablations and five routing seeds; meaningful graph-domain static FT beyond the
isolated-vertex pilot, separate RUS ledger/review and preparation break-even;
ideal/noisy iterations through first peak plus one, leakage/confidence intervals,
random sampling and cost per success; scaling/DIMACS with five repetitions,
stage time/memory/timeouts and positive/negative witnesses; full acceptance,
static/build/provenance checks, offline notebooks and isolated 135-metric replay;
traced manuscript numbers, reviewer responses, evidence gate and independent
final correctness/claim/reproducibility reviews. The existing restricted exact-hash
rotation admission and every caller obligation remain unchanged. No broader
numeric target, interval/ideal-amplitude, RUS/dynamic or paper approval is added.

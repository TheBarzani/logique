# Independent dynamic k=3 RUS instrument review

**Assigned review COMPLETE. Correctness ADMIT; bounded metric/evidence ADMIT,
with the separate scopes below.** No candidate correctness blocker was found.
This establishes ideal, uncontrolled dynamic instrument execution on one
two-bit vertex register, including capped aborts. It does not establish a
static unitary implementation, quantum-controlled use, a graph search,
preparation break-even, noise performance, or full-paper admission.

Date: 1 November 2026, America/Montreal. Task
`dynamic-rus-review-1030020413`, session
`01a19476-e502-7e81-b933-92d02733a736`, resumed attempt 2 after included-quota
interruption. The interrupted first turn inspected sources; it launched no
numerical checks and wrote no review. Quota interruption is not a scientific
failure. Review branch `codex/coloring-dynamic-rus-review-1030020413`, base
`e90adf3373236ef51a937480febd3cd7d669dce7`. No candidate edits or integration.

## Exact admissions and provenance

Read-only candidate is sibling worktree `dynamic-rus-execute`, branch
`codex/coloring-dynamic-rus-execute-1030020413`. Exact correctness commit
**`849bcc765dd140342d83f181469b4b8f29fa8893`** adds only its dynamic source/tests.
Exact evidence/checkpoint HEAD **`c655f5e905051a51316f33e87dd243cafa2239cf`**
adds `DYNAMIC_RUS_CHECKPOINT.md`. Working bytes equal those Git blobs and the
candidate was clean at intake and after checks.

| Decision | Exact scope |
| --- | --- |
| Correctness **ADMIT** | `src/logique/benchmarks/dynamic_rus.py` and `tests/test_dynamic_rus.py` at `849bcc7`: cap 0..4, at most three serial forward/inverse invocations on the **same vertex register**, up to three untouched reference wires and four operator/purification columns. Fresh zero retry ancilla; ideal primitive gates, Z projection, reset and classical control. All terminal records, including zero-norm and abort records, retained. |
| Build/dependencies | No bridge/build/pin changes in this candidate; no new build admission is needed or granted. The prescribed unchanged native binary was hash-checked and never invoked. Optional NumPy/Qiskit imports remain lazy. |
| Metrics/evidence **ADMIT** | The exact 20 saved finite-cap cases, 220 terminal branches, 10 dynamic QPY circuits, four primitive QPY circuits, saved input/channel/state/event artifacts and restrictions, bound by the 100-entry evidence index below. Counts describe this unoptimized emitted ideal construction. They are neither hardware measurements nor optimized FT costs. |
| Broader claims **BLOCK / outside admission** | Static A/A† substitution, quantum control, executed unlimited retries, graph/search correctness or advantage, runtime/T-depth, noise, physical costs, achieved preparation break-even and paper-wide conclusions. No new evidence here removes those gates. |

| Candidate artifact | SHA256 |
| --- | --- |
| Dynamic source | `4212abaaae4e3bb031ac28baa624c1d88c6ff574aa82701894688458529d44c9` |
| Dynamic tests | `5de0b20abb2fbeb2d655b93fe082536e5ab8e78618ce0386a4fb2933e7ee22e3` |
| Committed checkpoint | `4b723770f363a672dac6a748c67064169eb4692fe996c2052da53aa87eab5d50` |
| Evidence index | `a8f7fc74fdf36cb42f261439bdd8d025723dbe0fe671743a929d116523a362cf` |
| Saved summary | `9eaeb95fe61d2284f19886bdce5783051e3250aa1033106da476bb04253b9d85` |
| Branch/event ledger | `34a332b49a5d6e87e71eff08225d08ec871e0c390e393f0dc6106e49ca561946` |

Candidate evidence root:
`../dynamic-rus-execute/dump/1031201007-dynamic-rus-execution/`.
Every indexed artifact's length and SHA256 was verified, including saved
source, scripts, failures, command receipts, QPYs, arrays and inputs. The
index itself is bound by the committed checkpoint. Live append-only final Git
receipts and terminal checkpoint are separately inspected, not mistaken for
indexed artifacts. A queue outcome supplies no scientific admission.

Read AGENTS.md, CLAUDE.md and all 723 plan lines; the 29 October full research
handoff and current root 30 October continuation (absent on this older base);
architecture, actual dynamic source/tests/checkpoint/study script, prior
Task 6 mathematical review and analytical RUS review/admission. Required full
reads initially truncated were followed by focused chunks. No C5 work was
executed or reviewed; its separate current pilot/admission gate is untouched.

## Independent instrument derivation

Use basis |a,h,l>, with h the high color bit, and t=(1+i)/sqrt(2).
The emitted trial is H(a),T(a),CX(a,h),H(a),CX(a,h),T(a),H(a).
Starting from zero a, the two ancilla blocks after the first H,T,CX are
[I;tX]/sqrt(2). After the next H,CX they are
[I+tX;X-tI]/2. Final T,H and Z measurement give

    K0 = ((1-t²)I + 2tX)/(2sqrt(2)) = alpha U
    K1 = (1+t²)I/(2sqrt(2)) = beta I
    U = (I+i sqrt(2)X)/sqrt(3)
    alpha = (1-i)sqrt(3/8), beta = (1+i)/sqrt(8).

Thus K0†K0=3I/4, K1†K1=I/4 and their sum is I. Neither outcome probability
depends on data or an entangled reference. These are exact ideal-gate algebraic
identities; the numerical checks below are finite-precision corroboration.

The emitted extension is E=X_h CH_(h,l) S†_h. With C=H S† H and B=C T C†,
CH=(I tensor B) CZ (I tensor B†); conjugation cancels C's scalar phase.
The two T/T† occurrences are counted explicitly. V=E(U tensor I) has rows,
each divided by sqrt(3),

    (1,  1, -i/sqrt(2), -i/sqrt(2))
    (1, -1, -i/sqrt(2),  i/sqrt(2))
    (1,  0,  i sqrt(2),  0)
    (0,  1,  0,          i sqrt(2)).

All four columns are orthonormal. Its first column is uniform on 00,01,10,
with no 11 amplitude. The review compares every column rather than relying
on that preparation-only example.

For a forward loop, first success at attempt r has map
alpha beta^(r-1) V. The cap-c abort map is beta^c I. The inverse applies the
**actual expanded E† once before any trial**, even for cap=0; ZUZ supplies U†.
Its first success map is alpha beta^(r-1) V†, and its abort is beta^c E†.
Repeating E† on failure would change the data map. A fresh inverse has the
same branch scalar alpha beta^(r-1), not its complex conjugate.

For either direction s=1-4^-c is completion probability. On an arbitrary
joint data/reference density matrix rho, the completed channel is
s (V tensor I)rho(V† tensor I), or its inverse counterpart. Abort remains a
separate flagged channel with trace 1-s. Every serial branch is the ordered
product of its actual maps; execution stops at the first abort. L completed
loops have total probability s^L. No branch normalization or phase fitting
is used. Dropping the abort flag generally produces a different channel from
the intended unitary, even though the complete flagged instrument preserves
trace. This is not a static unitary certificate.

## Independent execution and evidence checks

Fresh review run, created with `new_dump_directory` in local time:
`dump/1101005148-dynamic-rus-independent-review/`.
Independent probe commit `edcaf85531994302277f776ddc99cd7485bc102b` owns
`tools/dynamic_rus_independent_review_probe.py` and its bounded runner.
No worker tests/helpers are imported to obtain reference matrices or channels.

The reviewer loads actual QPYs and interprets their standard primitive gates by
explicit little-endian bit-index summation. It checks gate classes, actual
classical conditions and nested block wire maps, projects both outcomes, and
resets the measured ancilla without renormalizing. It compares all columns
with the independently written V above, and verifies each loaded dynamic
circuit equals the current candidate builder's circuit. Four primitive QPY
matrices are reconstructed separately. Basis conversion is explicit:
zero-ancilla Qiskit rows [0,4,2,6] correspond to |h,l>=00,01,10,11.

All **75 schedules** (every forward/inverse word of length 0..3, cap 0..4)
and **1,375 branches** pass phase-sensitive map, full event trace, resource,
completion, abort and completeness comparisons. Maximum per-case enumeration
is 85 branches: 4³+1+4+4². A fresh Schmidt-rank-four input, seed **20261101**,
tests three untouched reference wires for every schedule and every branch,
including aborts. The saved pure and full-rank mixed-reference inputs are
also replayed; there are no stochastic shots or confidence intervals.

All **220 saved branch rows**, all 20 saved Kraus/effect/Choi/joint-channel
artifacts and all 10 saved entangled state artifacts agree with the QPY-derived
instrument. Event costs and probability-weighted counts are recomputed from
reached gates and records, not obtained from the candidate's expectation helper.
The saved primitive/channel arrays remain unchanged. Ten preallocation
rejections cover invalid caps, types, directions, program length and branch
budgets; zero-amplitude branches are retained.

Across **5,169 numerical comparisons**, largest absolute residual is
**2.842170943040401e-14**, below **3e-13**. This maximum includes scalar resource
sums as well as matrix/state entries; it is not a measured operator norm or
certified interval bound. The candidate's own saved maximum7.77156e-15 describes
its different comparison set. As corroboration, the candidate dynamic/RUS/
break-even regression suites pass **286 tests**, no skips/deselections, in
0.47 seconds pytest time. Independent algebra/execution supplies the admission,
not those green tests alone. Review probe Black and Ruff checks pass.

## Finite-cap resources and concrete counterexamples

Let M be reached attempts. E[M]=sum(r=0..c-1)4^-r=(4/3)(1-4^-c).
Forward expected stop T is 2E[M]+2s; inverse is 2E[M]+2 because E† is paid
before trials. These are unconditional stop costs including aborts, not
success-conditioned counts or costs per proper coloring.

| Cap per invocation | Completion probability | Forward expected stop T | Inverse expected stop T |
| --- | --- | --- | --- |
| 0 | 0 | 0 | 2 |
| 1 | 3/4 | 3.5 | 4 |
| 4 | 255/256 | 4.6484375 | 4.65625 |

Observed event sums agree with these independent formulas. Each reached
attempt has two T gates and one measurement/reset/outcome dispatch. Forward
trial has five Clifford operations, inverse seven; E or E† has two T and
15 Clifford operations. Retry counts only a subsequently reached attempt.
Every outcome resets, including final abort; fresh initial zero a is an
assumption, not an extra charged reset. Non-T costs remain null. Clifford
counts count CX/CZ once and exclude reset's physical implementation. The
unlimited 14/3 limit is analytical, with no finite worst case; no unlimited
execution or optimality is claimed. Serial loops here reuse the same vertex,
so they are not evidence for an executed multi-vertex search.

The following adverse constructions were reproduced independently:

| Incorrect use | Independent result |
| --- | --- |
| Repeat inverse prefix at retry r=2 | Frobenius map error **1.2247448713915885** |
| Place E† after U† instead of before it in time | Unitary-map Frobenius error **2.3094010767585034** |
| Adjoint a sampled forward r=1 path to obtain a fresh inverse | Frobenius map error **2.4494897427831757** |
| Naively quantum-control the trial on a pure control superposition | Discarded-record density purity **0.8124999999999994**, trace1 |

The controlled case has success probabilities1 and3/4 on the two control
sectors. Its measurement record reveals control information. This concrete
loss of coherence blocks quantum-control admission. The saved counterexample
arrays and numeric results agree with the independent derivation.

Original worker command2 failed because its test expected the **r=2** inverse
to differ from the adjoint forward path. In fact alpha beta=sqrt(3)/4 is real,
so those two maps agree. This original failure is reproduced as an equality;
the corrected r=1 counterexample really differs. This is an incorrect test
expectation, not two failed mathematical construction attempts. Worker Ruff/
mypy failures and their fixes remain recorded. Worker preliminary commands2/5/7
exceeded its stricter dense4 bound with a five-wire reference operator; those
preliminary passes are **excluded**. Final command12, saved study, and this
review use tensor action on references within dense4/dynamic6 bounds. No old
failed or partial artifact was removed, relabeled, or rerun over its outputs.

## Resources, preservation and follow-up

Budget was declared before arrays: one numerical child, 120 seconds per child,
300 seconds cumulative independent checks, 1GiB declared process memory,
dense operators/Choi matrices at most16x16 (four wires), dynamic pure states
at most64 amplitudes (six wires), at most four operator columns. Original
staticFT dense4 limit is unchanged. The two numerical children used
**1.434649s + 0.700203s = 2.134851s** boundary wall time. Largest direct-child
wait4 high-water RSS was **85,245,952 bytes**. No timeout occurred. Process-group
timeouts and fixed small allocations are safeguards; terminal wait4 RSS is
not live/group monitoring or hard memory enforcement. Static/Git commands
also have receipts and are charged to the conservative 300-second check total.

Only existing `/Users/mar/codex-work/logique/.venv/bin/python` was used, with
explicit candidate PYTHONPATH and asserted core/module paths. Compiler, BLAS,
OpenMP, Accelerate, Rayon and Qiskit parallelism are1. Prescribed native binary
SHA256 `6aa7357d2f64202584b14b0a14f8fb183379faf5907723cd24bd838b9be14a9a`
matches; no native build/invocation, sync, hardware, subagent/model/API launch,
purchase, precolored or conditional-workspace research occurred. Old128 and
new continuation queue/state remain unchanged. Root, README, pins, archives
and histories were not edited. Shared Git metadata initially denied staging;
its exit128/log is preserved and scoped automatic escalation succeeded.
No automatic approval-review rejection occurred.

Independent result SHA256:
`2b945e249a2bcc8622c59f50a047a9075c7e9ae450d400b3f62adff82c84fafc`.
Independent input SHA256:
`3b3eef3f5b71c4a187dd7eb3a2aec03da672d26a39ea05b147f193fea523b945`.
Probe SHA256:
`4a097452eb8cb775311f3466de04df6e8ec94b09e02bab021bf547ccbbe4de5e`.
Runner SHA256:
`1a5b416aba4e62468b1b34e503457c272fb908a1ccc8e53897ea4de548a21ce1`.
The run retains the actually executed runner snapshot (before removal of an
unused import), all exclusive logs/receipts, budget, source/input identities
and a final index/checkpoint. An interim commentary branch count was corrected
to the authoritative1,375; no saved scientific result used the mistaken count.

Next: `dynamic-rus-integrate-1030020413` may integrate **only the exact admitted
source/test bytes**, preserve this review and evidence scope, and perform its
own integrated checks. The dispatcher alone publishes root integration HEAD.
No worker push occurred. A separate next scientific task would assemble actual
multi-vertex marking/reflection with these completed instruments, account for
all abort prefixes and unpriced operations, and obtain independent graph-level
evidence before asserting a whole-search benefit. This bounded review is
finished; the full research/manuscript remains open.

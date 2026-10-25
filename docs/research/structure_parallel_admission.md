# Emitted parallel structure: bounded admission

Coordinator `coordinate-structure-parallel-1025081040`, 25 October 2026.
**Admitted: exact logical XOR/phase construction with emitted disjoint layer
supports, private clean comparator scratch, and explicit allocated workspace.**
No lowered resources, physical timing, saved-study comparison, superiority,
rotation extension or paper acceptance is admitted. The full paper is unfinished.

Git, the entire 33-job queue/durable state and server checkpoint were inspected
first. Worker `structure-parallel-1025081040` was complete, not blocked; only
this coordinator was running. There was no prior completed coordinator handoff
in Git, the manifest or the queue results. The original sequential coordinator
remains complete and is not redispatched.

Only worker correctness commit `fb5d072` was integrated as `4ab4235`. Its actual
source/test bytes, committed blobs, checkpoint identities and integrated bytes
match:

| File | SHA-256 |
| --- | --- |
| `src/logique/circuits/structure.py` | `8c7a999384f61a6dcd69372472030c8b8de36c04b2beb8909213140a0eaf2073` |
| `tests/test_structure.py` | `951576b4e2316ec29eb64f7015281451f61ba1c6977bcf22d3fe48a951e3ac91` |

The worker checkpoint is separately committed as `cd1a0ae`. No build or research
metrics enter this correctness integration. The older sequential decision is
preserved in [structure_oracle_admission.md](structure_oracle_admission.md).

## Predicate, exact phase and restoration

Sorted integer labels, LSB-first words and isolated vertices retain the admitted
mapping. Complete predicates require every edge inequality and x_v<k. Domain-free
predicates require edge inequalities over all binary codes; equivalence to the
coloring problem requires caller-provided valid-code preparation support.
Precolors reject. One-color complete domains accept zero only. Empty conjunctions
are true, including zero vertices. Loops retain zero flags and emit no comparator
with aliased words.

The comparator is unchanged. Its temporary right word is XNOR(left,right), its
c-1 prefix-AND bits compute equality, and X(target), CX(equality,target) toggle
inequality. Neither compute block reads target; the actual chain and XNOR
inverses restore both words and scratch for either target value. For c=1, two
CNOTs suffice. Exact X/CX/CCX/MCX gates are phase-free permutations. The
clean-scratch basis proof extends by linearity to coherent inputs and targets
entangled with data or external references. Initially dirty scratch/flags and
relative-phase substitutions remain outside scope.

Domain flags toggle mutually exclusive highest-differing prefixes for x<k,
with no comparator scratch. They run after edge layers. Let C be the actual
compute. XOR is C, flag conjunction into arbitrary target, C.inverse(). Phase
is C, conjunction, Z(target), conjunction, C.inverse(), with target initially
zero. This yields exactly (-1)^f(x) and restores every non-data wire. Tests inspect
the actual emitted inverse suffix, including barriers. A future decomposition
must establish its own phase/restoration contract.

## Emitted dependencies and workspace proof

First-fit placement admits an edge to a layer only if neither endpoint is
occupied there. Each canonical edge appears exactly once; loops occupy their
vertex without operations. The implementation maps every non-loop comparator
to distinct vertex words, its own retained flag and its own scratch slot.
Within a layer these actual operation supports are disjoint, even though the
right word is temporarily modified. Each flattened block therefore commutes
with the other blocks and can execute independently under logical wire
constraints. Full-wire barriers before/after each layer fence cross-layer slot
reuse. Domains and final conjunction follow the barriers. No scheduling
optimality is claimed.

Let c=max(1,ceil(log2(k))), n=|V|c, D=|V| for non-power-of-two complete domains
and zero otherwise, F=|E|+D, and W=max non-loop comparators per layer. Parallel
allocation is exactly n+F+W(c-1)+1; non-data allocation is F+W(c-1)+1. Sequential
allocation remains n+F+s+1, with s=c-1 if any non-loop exists and zero otherwise.
This includes retained loop flags, all reserved scratch and the output. It does
not include future lowered-MCX ancillas. Roles partition all allocated wires.

Each comparator cleans its c-1 private wires before ending. Slots are reused
only across barrier-separated layers and are clean during domain checks and
conjunction. All F flags remain reserved until the actual compute inverse;
the output is arbitrary for XOR and starts zero for phase. Scratch can carry
intermediate equality values during a comparator, so it cannot be lent to
another active comparator. No parallel-depth claim at sequential scratch width
is admitted.

The independent coordinator probe derives segments from actual barrier
instructions rather than trusting metadata ranges. It checks complete-wire
fences, actual support disjointness, output exclusion and per-wire gate arrival
times against independently calculated block times shifted by the common
layer fence. Worker tests additionally compare every mapped primitive operation
and qarg with its instruction range. These establish logical scheduling only,
not lowered depth, T-depth, routing, scheduled hardware duration or performance.

## Evidence and bounds

Run: `dump/1025173122-parallel-coordinator-triage/`. The worker checkpoint,
identity and scalar harness are preserved there. All 19 saved evidence hashes
in the worker identity were verified, as were source/committed blobs. Saved
worker failures remain intact, including its preliminary mypy failure and fix.

The integrated focused suite passed **193 tests**, without skips/deselections;
relevant Black, Ruff, one-file mypy and diff checks passed. Quantum tests have
dense operators <=4 qubits and statevectors <=5. Scalar exhaustive tests reach
nine data bits; seven k5 wide witnesses are explicitly not exhaustive. The 40
wide worker construction/dependency fixtures allocate at most 323 logical wires
without exponential quantum arrays.

The independently authored coordinator harness imports no worker tests or
maintained verification interpreter. It passed on candidate and integrated
bytes: **206 graph/policy cases**, **21,708 XOR/phase checks**, **2,728 comparator
checks** (c=1..5), **6,092 actual comparator-boundary cleanup checks**, and **400
emitted disjoint blocks**. Direct integer predicates cover palettes
1,2,3,4,5,7,9,17, loops, empty/unsatisfiable constraints, noncontiguous labels,
isolates and asymmetric words. Exhaustive coverage is <=8 data bits; ten wide
fixtures per policy use three explicitly labelled witnesses each. Maximum
allocation in these extra fixtures is 82 logical wires; there are no dense
operators/statevectors. Primitive semantics plus compositional proof support
wider words; finite enumeration alone is not that proof.

The preserved worker scalar harness was also replayed on integrated bytes:
**444 cases**, **55,512 XOR/phase checks**, **680 comparator checks**, including
222 exact sequential-default/explicit comparisons against admitted `0a56cd2`
compute, XOR, phase and metadata bytes. This supplementary replay is identified
as worker-origin evidence, not independently authored coordinator coverage.

Commands/environment/exit codes/elapsed time/RSS are in `commands.jsonl`. All
numerical/static children ran sequentially, with 180-second timeouts, existing
research Python, asserted checkout-src imports, root EPFL cache and the explicit
manifest private common-preprocessing binary. BLAS/OpenMP threads=1. Maximum
measured child RSS is **107,806,720 bytes**, below 8 GiB; this is per-command
measurement, not an enforced aggregate memory limit. No build/native invocation,
full-suite/notebook or new research-metric claim is made.

## Failures, preservation and handoff

No coordinator numerical/static check failed or timed out. `ps` was
sandbox-denied, so complete OS process visibility is not claimed. Initial
cherry-pick could not write `.git/index.lock`; scoped automatic escalation
succeeded. Worktree creation likewise used scoped Git permission. There was no
automatic approval rejection. Preliminary file-discovery references to absent
`.agents`/`.codex` paths returned a nonzero status without mutation.

All **457 protected identities** match intake, including README edits, archived
outputs, prototype backups, preserved nested histories, dependency pins,
rotations, both native binaries and worker non-owned files. External index
records are unchanged. The private binary remains
`6aa7357d2f64202584b14b0a14f8fb183379faf5907723cd24bd838b9be14a9a`;
the old root executable remains
`ea78b720327f82dd9bbc8c1eb4db63b182c87eaeb7382474ea4d3488457150fa`.
No agents, model/Codex launches, API/paid fallback, hardware, pushes, publishing,
sync, installs or dependency changes occurred.

The next isolated slice is a bounded **analytical ideal-iteration ledger** with
known M/N, explicit first-peak/tie/cap handling, independent good/bad recurrence,
random-trial accounting and unavailable-noise labels. Three unique jobs are
appended atomically without changing the queue header or any prior definition:
`ideal-iterations-1025173122` (experiments, 1800s),
`ideal-iterations-review-1025173122` (critical_review, 1200s), and
`coordinate-ideal-iterations-1025173122` (coordinator, 1200s), each four attempts.
Review/coordinator use finished-dependency triage; workers use isolated
`codex/coloring-` worktrees at `4ab4235`. Dispatcher alone launches them.

Native, restoring-MCX/controls/QPY, static FT/RUS and structure comparison
ownership remain separate. Structure still needs common restoring lowering,
workspace policy integration and independently validated saved R1/R2/R3
comparisons. The analytical iteration handoff cannot establish circuit/noise
accuracy. Full controls, post-pilot protocol freeze, nine-graph/multilevel and
five-seed routed comparisons, FT graph validation, separate RUS/break-even,
iteration/noise/scaling, full acceptance and evidence-gated manuscript/final
independent reviews remain outstanding. Every old unsafe saved artifact retains
its existing restrictions.

Rotation admission remains exactly [rotation_norm_admission.md](rotation_norm_admission.md):
reviewed source/tests hashes, defect <=64*float64_eps, original numeric/recursive
targets, norm-aware whole-search accounting, 1e-12 precision floor, bounded SK,
recursive/angle limits and explicit failures. Caller clean phase semantics,
mapping, signed S0, restoration, explicit MCX lowering, actual inverses and
scalar phases remain required. There is no interval certificate, ideal-amplitude
guarantee, RUS admission or blanket paper approval.

This bounded admission/handoff is complete only when its batch records
`bounded_batch_complete=true` with committed integration/audit identities.
On resumption verify the batch, hashes, preservation and unique jobs, then
release the assigned coordinator complete without repeating tests or dispatch.

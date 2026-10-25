# Static FT pilot: bounded coordinator admission

Coordinator `coordinate-static-ft-pilot-1025034429`, 25 October 2026.
Bounded review/integration **complete**. The fixed isolated-vertex assembly pilot
is admitted as numerical implementation evidence only. **No graph comparison,
preparation break-even, protocol freeze, dynamic/RUS or paper admission.**
Full paper remains unfinished.

The whole queue and durable dispatcher state were inspected first. This
coordinator was running its first attempt; no earlier completed integration
batch or handoff existed. Worker `static-ft-pilot-1025034429` was complete,
not blocked. Its clean worktree contains correctness commit `daf4b21` and separate
checkpoint/evidence commit `97e0c85`. Only the two correctness files were
integrated as `28413d8`; no build, metrics implementation, dependency or other
worker's source entered that commit. The worker checkpoint is preserved in the
triage run; its saved artifacts were read without rewriting them.

## Exact bytes and fixed caller contract

| Artifact | SHA-256 |
| --- | --- |
| `src/logique/benchmarks/static_ft.py` | `bc1ea4a1955d517f59c178d36d616ac67123e6e31093a8b81859534e01167c16` |
| `tests/test_static_ft.py` | `66c02665daec6f2d3b9e55c15ff455f9c70e2edb64844d6e83990459f977fe5a` |
| `src/logique/benchmarks/rotations.py` | `5e8d08c69305100bd892c25deb748415cd7de1f530b4654da4cdb801dea4e595` |
| `tests/test_rotations.py` | `88412c34913b160d1ebc857e833646bd5e7a7e527b654f7cb43bf439b776db77` |
| `rotation_norm_admission.md` | `01776d3dcc4527d7914aa1893db18eea336b76ad3518071b83eb71ce2b1c4c2d` |
| Selected private common-preprocessing executable | `6aa7357d2f64202584b14b0a14f8fb183379faf5907723cd24bd838b9be14a9a` |

The executable remains the native-contract worktree's
`dump/1025025511-native-contract/build/boolean_synthesis`, not the old root
binary. Source/test/review/import-path/binary drift rejects before the pilot.
The full [rotation admission](rotation_norm_admission.md) and its caller
obligations remain binding. Compiler bytes are unchanged. This is numerical
engineering evidence, not an interval certificate or ideal-amplitude guarantee.

The maintained method is fixed to `xag_bennett`, common preprocessing `none`.
R1 uses H and the complete k=3 predicate; R2 uses ordinary StatePreparation and
the same predicate. R3 builds colors=4 on identical two-bit vertex blocks,
removing domain checks, while proper-color decoding stays k=3. No precolors.
The edge graph's 13 native wires explicitly fail the four-qubit dense bound;
all seven rows therefore use the authorized isolated vertex 7, k=3. This has no
edge constraint and cannot establish graph-resource improvements.

Before costing, every clean data column must equal the independently specified
phase sign with zero other amplitudes. On that clean subspace this gives the
coherent action by linearity, including an external reference; no dirty-workspace
contract follows. The signed reflection is `S0=-X^n MCZ X^n`, checked against
`diag(1,-1,...,-1)`. Data mapping is explicit and asymmetric fixtures detect
bit exchange. Restoring Gray-code MCX uses no extra or borrowed scratch. Native
open-control CCX is expanded exactly; the original oracle remains the reference.

A is synthesized once per row. Initialization applies A once, followed by
O,A-inverse,S0,A per iteration. The saved inverse is the adjoint of the actual
emitted A, including scalar phase. Complete emitted circuits determine T-count;
T-depth follows dependencies, not an additive component formula. Unused j=0
O/S0 have no emitted QPY/cost. Source targets expand definitions before QPY;
this avoids the known inverse-StatePreparation bug locally and does not repair
or admit the separate main-runner controls candidate.

## Independent evidence and limits

Evidence: `dump/1025083656-static-ft-pilot-triage/`, including the independently
written `independent_review.py`, `commands.jsonl`, before/after identities,
preserved worker checkpoint, all worker-evidence hashes and review JSON/logs.
Original pilot: static-ft worktree `dump/1025082919-static-ft-pilot/`.

Candidate replay: **211 tests passed**, no skips/deselections. Integrated replay:
**24 harness tests passed**, no skips/deselections; unchanged rotation tests
were not repeated after their candidate pass. Relevant Black/Ruff and focused
one-file mypy pass in both checkouts. No full-suite/build/notebook/replay claim.

The coordinator independently reloaded **61 QPY artifacts / seven rows** in
both checkouts, verified actual hashes and raw gate counts, reconstructed
T-depth without the cost helper, compared source A with a fresh ordinary
preparation, checked **28 original oracle columns**, signed S0, actual inverse,
full assembly and direct ideal-state recurrence. Ten additional asymmetric
contract fixtures exercise both mappings and phase/scratch/sign/mapping faults.
All original-target errors satisfy the reported bound without extra tolerance
in this independent check. Largest assembly error is
`1.4763228132311763e-14`. T-count/T-depth pairs are 0/0, 42/18, 2905/2904,
8757/8730, 2905/2904, 8715/8712 and 1731/1704 in pilot order.

Proper-color success, invalid-code leakage and scratch events were recomputed
from direct two-bit decoding. R1/j=1 overshoots to essentially zero success;
R2/R3 success near one is trivial for a graph with no edges. Ideal-target gaps
are measured separately and do not extend the compiler's theorem. No choice of
optimal j, strongest-baseline advantage or break-even is inferred.

The harness uses a semantic tolerance 1e-10 and accepts original-target error
up to its compiler bound plus 1e-12 in its internal check. The stronger direct
readback above establishes the seven saved rows; it does not supply a universal
roundoff theorem or justify broader instances. Limits remain four-qubit dense
operators and five-qubit statevectors in the existing rotation regression.

Failure behavior is explicit: bounded SK failure retains trial metadata, with
no analytic replacement; timeout/preflight/validation statuses and unrun cases
are persisted. `bounded_complete` means the schedule finished, even if rows
failed. The CLI returns a run path; consumers must inspect manifest and every
row's status rather than interpret exit zero as scientific success. The fixed
seven saved rows completed, but their edge preflight explicitly failed the
resource bound. Broader graph validation remains blocked by this pilot domain.

All checks ran sequentially with existing research Python, explicit checkout
src/cache/private executable, single BLAS/OpenMP threads and 180-second external
command timeouts. Maximum recorded child RSS was **222,330,880 bytes**, below
8 GiB; this is measured high-water evidence, not OS aggregate enforcement.
No compiler build, sync/install or wider simulation ran. `ps` was sandbox-denied;
durable dispatcher state is the available process evidence. Initial cherry-pick
and worktree ref writes were sandbox-denied; scoped automatic escalation
succeeded. No automatic approval rejection or numerical failure occurred.

## Next bounded work and remaining scope

Append only a separate analytical k=3 RUS resource ledger, isolated independent
critical review and coordinator triage (including blocked status). The existing
Task 6 derivation supplies a starting point, not dynamic admission. Require
arbitrary-input Kraus/inverse reasoning, coherent/entangled checks, expected
versus capped failure accounting and explicit unpriced measurement/reset terms.
No dynamic execution or substitution into the static compiler is authorized.
No graph break-even claim may use this degenerate pilot. Existing native,
QPY-controls and parallel-structure jobs retain their scopes.

Meaningful static FT graph comparisons still need a separately justified bounded
validation method before widening; the edge failure is retained. All full-study
decomposition/workspace/routing/precision/limits controls, post-pilot protocol
freeze, nine-graph/multilevel comparisons, remaining mappings/profiles/SAT,
iteration/noise/scaling, separate preparation break-even, research acceptance,
evidence-gated manuscript and independent final reviews remain unfinished.
This completed handoff must not be dispatched repeatedly.

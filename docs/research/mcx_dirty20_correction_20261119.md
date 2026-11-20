# Fail-closed two-dirty20 MCX correction — 19 November 2026

The public lowering boundary now rejects `2_dirty_kg24` at exactly 20 controls
with a deterministic `ValueError`. This prevents the rejected installed
construction from supplying new correct-MCX costs. **Implementation complete;
exact independent source/evidence review pending. Full scientific gate BLOCK.**
No replacement decomposition or new theorem is offered.

Task `mcx-dirty20-fix-1113162936`, session
`01a1f58d-08fa-7343-9eee-dbd85b15e636`, branch
`codex/coloring-mcx-dirty20-fix-1113162936`, starting base
`f7432e3f47593b9ab0b9a7634710c34beaeb8b60`.
Correctness commit: `2ac43fd67cd5381b41b15fbc8a910679076efdc0`.
Local checkpoint: `dump/1119154507-mcx-dirty20-fail-closed/checkpoint.json`
relative to this assigned worker worktree. This distinct report is committed
separately from the correctness change; no research metrics are changed.

## Binding diagnosis and boundary

The [wider review](mcx_wider_semantic_independent_review_20261113.md), including
its superseding addendum at `3878f14`, and [final Astra review](final_quantum_claim_independent_review_20261113.md)
at `be5d36b` remain binding. Their tracked copies were authenticated against
the exact reviewer Git blobs. The 39-wire historical register has controls
0–19, target20, borrowed wires21/22 and untouched spares23–38. The input
$w=2^{22}+3=4,194,307$ has a false control conjunction. Required forward action
is identity, yet the saved action gives $w+2^{20}=5,242,883$.

The new sparse regression retains the rejected action, rather than calling
the forbidden constructor. Its two frozen primitive words are extracted from
the exact hash-checked saved QPY: 400 forward instructions and 1,097 paired
instructions, with scalar global phases and ordered operands retained.
No historical artifact is modified. Only matrices on at most three wires are
used; sparse support is capped at eight before pruning, and the sum of discarded
L2 norms must remain below `1e-11`. Comparison tolerance is `1e-11`, without
global-phase alignment. This is a bounded floating-point regression, not an
interval certificate or a full 39-wire statevector.

| Action | Newly reproduced observation | L2 error against required action |
| --- | --- | ---: |
| Forward on $w$ | output5,242,883, amplitude0.9999999999999889 | 1.4142135623730872 |
| Saved compute–Z–actual-inverse on $w$ | output$w$, amplitude−0.9999999999999655 | 1.9999999999999654 |
| Paired action on reference-correlated two-component input | opposite signs on the two restored components | 1.414213562373072 |

The last input is $(|0\rangle|0\rangle_R+|w\rangle|1\rangle_R)/\sqrt2$;
reference bit39 is never a gate operand. Both inputs require positive marking
sign, but the second component receives a negative sign. Thus cleaning the
borrowed bits and applying the actual inverse does not repair the incorrect
computed target. The relative sign cannot be discarded as a global phase.

The registry's `build` callable and cached constructor are guarded. The public
decomposer scans all selected gates before constructing even an earlier valid
template; open controls receive the same exclusion. The isolated-cost helper
rejects before allocating its source circuit. Phase lowering and the study's
`lower_block` inherit the deterministic rejection. Study source resolution can
still copy source records before reaching the guard; no general hostile-input
allocation guarantee is claimed. `mcx_study.py` itself is unchanged, including
its historical planning estimate; no new research execution is authorized by
that estimate. The existing runner records this `ValueError` as a failed row;
no cost is emitted for it. No runner or historical row is changed here.

The exclusion stays closed across dependency-version changes until a separately
reviewed correction is admitted. It concerns the reviewed installed action,
not the published Khattar–Gidney theorem. Smaller counts and other policies
retain their previous dispatch and scientific restrictions. No claim is added
for previously unreviewed widths or alternate input contracts.

## Validation and exact handoff

Final selected validation: **82 passing tests** =37 new boundary/sparse tests
+19 existing bounded cost tests+26 existing template/preflight/local-FT tests.
The earlier37-test run is retained separately, not added to that unique count.
The retained templates use seeded arbitrary complex states with an untouched
reference at three/four controls (seeds74/75). New sparse checks are deterministic.
Smaller-count delegation3..19 and other-policy20 dispatch tests use sentinels;
they do not construct excluded Gray cases or certify wider semantics.
Existing clean-tree/2-clean cost regressions retain controls3/6/20. No completed
study, full graph fixture sweep, metric recount, routing or noisy run is replayed.
Black, Ruff and Git whitespace checks pass. No full-suite certificate is claimed.

| Correctness path | SHA256 |
| --- | --- |
| `src/logique/benchmarks/costs.py` | `3500fcddd2738bdd69a6966d2d3cd06c76558bd4fdcf94ad46ccb9b4f2b89e9e` |
| `tests/test_mcx_dirty20.py` | `1ed7db40a28680a8039252bf40b52ee769c5750c7b970f6c6c97d8dc1902c2e3` |
| `tests/fixtures/mcx_dirty20_rejected.json` | `625c4c8600ba779ca464da316ce7ccd92d6b0ae14759dcc9bc17103710466f65` |

The fixture binds forward QPY `712d3bfc8a652233f2692c81fb3716b3bd0185e70abebdca12a89fcff017babe`
and paired QPY `33e5795b262cef319a94a71e69ed455871d538e9cf79436ae8f95a22c5c50793`.
The extraction source, terminal receipts/JUnit, source/evidence hash audit and
executed supervisor are preserved in the new run. Candidate imports are asserted
to this worktree. Current authoritative `costs.py` before correction and relevant
study/record/test/lockfile dependencies match the assigned inherited base;
no stale source was substituted. Qiskit2.1.1/NumPy2.2.6 are unchanged; installed
MCX Python source SHA256 is `f809504c8c0596a28a170f0e9696a33232eaf5327fbd18ec1f42891ce208a37c`.

Before numerical work, the plan declared120s/child,600s cumulative,2GiB/process,
one numerical/compile child and all configured parallelism1. Eleven supervised
children total **4.593303s**, longest **1.087972s**, largest terminal wait4
high-water **137,052,160bytes**. Darwin terminal RSS is not a hard cap or live
group peak. General statevector18/dense5 and original staticFTdense4 caps are
unchanged; actual new primitive matrices are at most8×8. The prescribed native
binary SHA256 `6aa7357d2f64202584b14b0a14f8fb183379faf5907723cd24bd838b9be14a9a`
was explicitly selected/hashed, with zero native invocations and no build.

Initial scalar inspection missed an absent attempt-JSON glob. Git staging first
hit the shared-metadata sandbox boundary; scoped automatic escalation succeeded.
The first commit lacked an author identity; command-local existing-history
identity resolved it without configuration changes. These inspection/Git exits
remain in dispatcher events, with no invented child RSS. No numerical/test
failure occurred. README's existing root edit, pins, histories, archives, old
cost rows and every rejected representation remain unchanged. No queue change,
model/subagent launch, sync/install, hardware or push occurred.

Next: dispatcher-owned `mcx-dirty20-review-1113162936` must review all three
correctness paths, this report and their complete dependency/evidence chain.
Coordinator alone may integrate whole exact independently admitted paths.
Historical1,608 completed cost rows remain historical observations, not a
correct-MCX denominator. The exact145 wider saved decisions retain144 supported
and one rejected; the1,335+84 whole-row admissions, Gray12..20 exclusions,
analytical Dutta, unpriced rotations and all final-review restrictions remain.
Any filtered cost denominator or replacement construction requires separate
reviewed work; neither is inferred from this correction's passing tests.

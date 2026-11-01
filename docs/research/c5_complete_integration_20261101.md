# Exact C5 best-fit integration — 1 November 2026

Task `c5-complete-integrate-1030020413` is **COMPLETE**. Independent review
`4fbf3d023878617cfad9236470bb3ba8f3b28e83` admits the final bounded best-fit
harness and exactly ten ideal C5/k3 observations. **The separate structure22
pilot remains PENDING/BLOCKED for independent lowered-oracle validation.**
This is no full Task7, noise, matched-cost, manuscript or general native admission.
Checkpoint: `dump/1101045255-c5-exact-integration/checkpoint.json`.
Intake HEAD `19286c4` is newer than assigned base `e90adf3`; no reset occurred.

## Exact admission and integration

Correctness commit **`2fff3ea`** imports only the final cumulative bytes of
`tools/check_c5_complete.py` and `tests/test_c5_complete.py` from candidate
`ab31ae784380e1b039b3cf5dc545f8f999597750`, unchanged at final candidate
`53176684beef47c29c244f7d329d977234a0b9a8`. Their SHA256s are respectively
`39ba9de8be5917b0c81d46331c48c2acbf425a18e45902233b5ee29a9e1dcd9d` and
`65c7300a10b8670e130080465d8f2d9a5bdf32a911cae1f368738f4fa13ae3d9`.
All corrections in `dd6432d`, `df4a232`, `ab31ae7` are present; no intermediate
failed source was integrated. Both paths were absent at root, with no conflicts,
semantic edits or inferred admission of new bytes. No library/build change.

The [verbatim independent review](c5_complete_independent_review_20261101.md)
has SHA256 `226cd36abb83df90a0c1c97103918a5a17f0910a1abbf604c135d01e13d3d13c`.
The [verbatim worker checkpoint](c5_complete_execution_20261101.md), from
separate evidence commit `5317668`, has SHA256
`5f4a36e9df3d3105c23bf90110599a70ed9b90312b74f35d4447a480ae282a01`.
Its historical “review pending” wording is retained verbatim; the new exact
review supersedes that status only within its explicit best-fit scope.
Evidence admission and this decision are committed separately from correctness.

Final best-fit manifest SHA256:
`fb2d62dde01aaddcb50250731259f440a2d120c91fa474905b8670f560634fe4`.
Shared saved oracle SHA256:
`8d1450ce9011e433b1cf95e2629d882028478bccd257c4e153e5c74499219268`.
All 50 best-fit manifest entries, 15 structure-pilot entries, 33 reviewer inventory
entries and every recorded candidate Python source identity were checked.
The unchanged prescribed native executable matches
`6aa7357d2f64202584b14b0a14f8fb183379faf5907723cd24bd838b9be14a9a`;
its build declaration and recorded private bridge source hashes also match.
This verifies preserved provenance, not a new source-to-binary build attestation.
No native invocation, build, numerical study or 22-wire replay occurred here.

## Scientific result and limitations

C5 has 30 proper three-colorings. The best-fit native allocation is 11 wires:
ten ordered data wires and one output. Complete unused-code checks remain in
both regimes. R1 has 1024 binary input words; R2 has 243 valid-code words.
With $p=M/N$, the analytical prediction is
$P_j=\sin^2((2j+1)\arcsin\sqrt p)$. All six R1 rows j0..5 and four R2 rows
j0..3 were actually executed and independently reviewed at complex128,
comparison tolerance1e-10. There are no shots or binomial confidence intervals.

R1 peaks at j4 with 0.999484622397 success, falling to 0.900260183699 at j5.
R2 peaks at j2 with 0.950509084831, falling to 0.345567160993 at j3.
The reduced domain requires fewer iterations but has a lower discrete first
peak. R1 peak unused-code probability is0.000404939543798; R2 remains below
1.98e-27 in independent checks. Independent signed residual is at most9.63e-13;
this is observed numerical agreement, not a rigorous floating-error bound.

The saved best-fit phase oracle has84,441 U/CX instructions, raw computation
42,220. Low width does not establish low cost. No routed/FT/rotation or matched
baseline comparison is licensed. Preserve the failure counterexample word8:
old zero-initialized component lowering produces nearly unit dirty-output
probability. Final harness disables that assumption and tests a coherent input.
Both failed/partial worker attempts and failed reviewer cwd invocation remain.

For the [structure22 pilot](c5_22_qubit_pilot_20261031.md), logical exhaustive
checks and four scalar j0,1 observations are consistent, but do not independently
certify its exact saved 977-instruction lowered oracle. Default zero-initialized
transpilation may be valid on its reachable clean subspace; the best-fit failure
alone does not prove otherwise. Required next action: independently establish
absolute phase and scratch restoration of QPY
`226bdb02003f5eb69ce240acf423ca12811bdf283a7dac475d348706f70ec38b`
on that reachable subspace by a compositional proof or separately authorized
bounded probes. Missing structure R1 j2..5 and R2 j2..3 remain unexecuted.
Historical18-wire exclusions and all other caps remain unchanged.

## Verification and follow-up

Candidate and integrated C5/ideal-iteration suites each passed 205 tests, with
explicit candidate/root PYTHONPATH and asserted actual import paths. Selected
Black/Ruff passed.

| Check | Boundary seconds | wait4 high-water bytes |
| --- | ---: | ---: |
| Candidate 205 tests | 1.613688 | 138,706,944 |
| Integrated 205 tests | 0.924524 | 137,003,008 |
| Black | 0.284773 | 38,338,560 |
| Ruff | 0.104685 | 19,759,104 |

Numerical test children total 2.538212s; both exited 0. No full repository/native/notebook/historical-replay check is
claimed. Root has newer admitted resolver/native/routing/iteration source;
no such source was copied or changed. Relevant integrated regression checks
pass, including reusable-component MCX and actual preparation/inverse checks.
The resolver's new >32-control path is outside this ten-data-wire harness.
Saved observations stay bound to their original candidate source and circuits.

Budget declared before arrays: 120s/child, 300s cumulative numerical time,
2GiB/process, at most 11 statevector wires, no dense Operator or density matrix,
serial children, all compiler/BLAS/OMP/Accelerate/Rayon/Qiskit parallelism 1.
Terminal wait4 high water is recorded per child; no OS hard cap or aggregate
process-group RSS monitoring is claimed. Receipts contain commands, exits,
wall times, RSS scope, seed/source/evidence identities and exact logs.
The initial Git stage failed exit 128 on sandbox index.lock permissions;
scoped escalation succeeded. No automatic approval-review rejection occurred.
Initial long inspection output truncations were followed by focused source
reads and structured identity checks; they were not scientific failures.

README, dependency pins, histories, archives, binaries, queue definitions and
all inspected evidence remain unchanged. No sync, push, model/subagent/Codex
launch, API/paid fallback, purchase or excluded research occurred. Dispatcher
alone publishes root integration HEAD. Existing full-research successor owns
the pending structure proof, separately admitted noisy execution and matched
resource comparisons. Standalone harness lowering fixes do not automatically
repair or admit downstream callers. This assigned integration ends here;
the broader manuscript evidence gate remains open/blocked.

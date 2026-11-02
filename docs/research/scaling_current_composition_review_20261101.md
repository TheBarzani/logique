# Independent current-composed scaling review — 1 November 2026

**Decision: BLOCK the whole composed scaling/native source at correctness
`f444e428d4d3c19562e4b1a36815e2f427245848`, candidate HEAD
`59aa7c1053aeb491062bfe25f39fc4f1131c4027`. No implementation path is admitted
for integration or selected execution by this review. This bounded independent
review assignment is COMPLETE.**

The runner-finalization repair passes fresh independent checks. A distinct
first-SIGINT window in the native adapter still discards genuine process
accounting after the leader has been reaped. This is an accounting-transfer
failure, not the old live-child leak or lost-row/zero-charge failure. It prevents
the complete source admission required before selected compiler measurements.

Task `scaling-current-review-1101052342`, assigned branch
`codex/coloring-scaling-current-review-1101052342`, base
`de230cce74089344343fcdf1c12d553cc4cf8607`. Candidate is the sibling
`scaling-current-compose` worktree under
`dump/1101052342-full-research-successor/worktrees/`. New reviewer evidence is
`dump/1101200646-scaling-current-independent-review/` in this review worktree.
Only this report and `tools/review_scaling_current_1101052342.py` are owned
tracked deliverables. No candidate edits, integration, compiler replay or push.

## New blocking reproduction

`src/logique/synthesis/native.py:77` copies the failed process receipt and line88
copies the successful one. Both execute after `run_bounded` has restored the
caller's SIGINT handler, without protection spanning the transfer. A first
SIGINT immediately before either dictionary update replaces the adapter's
control flow with the caller's original KeyboardInterrupt. The genuine receipt
is neither copied to `process_accounting` nor attached to that interruption.
The runner receives an empty dictionary and can only save its fallback.

The unique independent probe traces these actual source statements. It executes
one prior row, then injects one real `os.kill(self, SIGINT)` before the second
receipt copy. A shell fixture emits an explicitly specified two-input XOR
network for the success case; a real sleeping child exercises a 0.025-second
timeout. No compiler, wait result, signal denial, clock or receipt is fabricated.
The success fixture corresponds to a two-vertex edge with k=2, four input
bitstrings and two positive assignments. It is process-control evidence only.

| Second-call observation | Success | Timeout |
| --- | ---: | ---: |
| Genuine boundary seconds available in adapter | 0.111256958 | 0.026820209 |
| Runner fallback / charged seconds | 0.113394583 | 0.028278666 |
| Genuine wait4 high-water bytes | 1,982,464 | 32,768 |
| Genuine return code | 0 | -9 |
| Genuine process status | exited | timeout |
| Saved RSS | null | null |
| Saved return code / process status / cleanup / leader-reaped fields | absent | absent |

Both runs save valid `interrupted` JSON, the unchanged prior row and exactly one
current row/charge. Both propagate the identical original exception and restore
the handler. Both leaders are genuinely reaped (`wait4` then raises
ChildProcessError), no post-injection cleanup signal occurs, and no emergency
cleanup is needed. Neither loses elapsed-budget charging. Nevertheless, the
known timeout, return code, RSS, cleanup diagnosis and reaping evidence disappear
from the current row. The preserved reviewer sidecar contains the genuine
receipt copied from the adapter frame before injection; the candidate manifest
contains only the fallback. These instrumented times are not synthesis metrics.

Reproduce with the existing research interpreter, explicit candidate `src`
PYTHONPATH and a fresh nested evidence directory, passing the probe arguments
`CANDIDATE EVIDENCE native_success` or `CANDIDATE EVIDENCE native_timeout`.
Both current-candidate runs intentionally exit1 on the exact receipt-equality
assertion. Logs, source snapshots, receipts and failed manifests are retained.

**Required correction:** retain the real receipt across the complete boundary
return/exception-to-caller transfer, including cancellation before and during
both updates, and SAT timeout translation. Preserve the first interruption
object, actual process status and handler policy. Complete receipt transfer
without another native call, cleanup, wait or signal to a reaped/reusable PID.
Keep failed-call charges and atomic runner persistence. A correction must be
independently reviewed as the complete composed source, not merely as another
locally passing fragment.

## Runner and inherited rejection checks

The full final `process.py`, `native.py` and `scaling.py` source and their
composition differences were inspected against actual reviews `44ad4ba`,
`bfc440b`, and finalization review `0f8c9c7` of `a8b3606`/`92af56d`.
The earlier finalization admission remains historical and restricted; this
new failure does not relabel its passing runner observations as failures.

The finalizer computes the current charge from the prior cumulative snapshot,
assigns the current row slot, and atomically replaces the serialized manifest
through an exclusive temporary sibling. Recovery repeats these assignments,
not process execution or additive charging. Fresh independent calibration
discovers every executed source-line transition through finalization and save,
then tests each with a first SIGINT on success and timeout. Additional probes
interrupt partial manifest writes, both sides of replacement, finalizer return,
both sides of handler restoration, final run hashing/replacement, and partial
response writing. Existing body interruption takes precedence over a later
persistence signal. Prior rows, unique identities and exact cumulative sums
are checked independently.

- **99 fresh probe cases pass:** two no-signal controls and 97 first-SIGINT
  cases. Of the latter, 88 cover second-row transaction boundaries; nine cover
  whole-run persistence, existing-body interruption and partial response writes.
- **Two additional native-transfer cases fail**, as documented above. Their
  original-exception, handler, prior-row, unique-charge and reaping assertions
  pass before the receipt-preservation assertion fails.
- **172 maintained cases pass, 317 deselected.** Selection covers process,
  runner, cleanup, native contract, SAT/mapping mocks, selected preparation and
  timers. Real compiler/integration cases and compiler-dependent finalization
  fixtures were deliberately excluded; a launch sentinel prohibits accidental
  `boolean_synthesis` execution. The independent fixture probe supplies the
  fresh finalization coverage instead.
- **24 preserved independent cases pass, one deselected:** original B1/B2,
  real exit/reap/kill races, cleanup-phase SIGINT, descendants with unrelated
  group survival, missing/null/negative/NaN charges, unavailable sampling and
  cumulative budget gates. The excluded case requires a real compiler success.

The new probe observes actual waits and prohibits direct-PID signals after
reaping and any repeated cleanup after its finalization injection. No passing
case needed reviewer emergency cleanup. Passing tests do not override the
two observed whole-source failures.

## SAT coexistence and exact source identities

The current SAT implementation's response-validation suffix is byte-identical
to the assigned current base. SAT controls remain outside process JSON;
`min(caller_timeout, sat_time_seconds + 1)` validates the caller first. Without
interruption, timeout conversion preserves `TimeoutExpired` with its genuine
receipt. The maintained composition checks confirm shorter/default deadlines,
invalid callers, omitted/mismatched confirmations, and real sleeping-child
timeout/reaping. The new transfer failure is before SAT's exception translation
on the shared failure path; that path needs the same correction. No new SAT
solver, mapping, larger-domain or CEC admission is issued.

Fresh audit verifies **96 source/context identities**, **589 final candidate
evidence entries**, **12 actual candidate imports**, and **77 unchanged library,
bridge and dependency-context paths** against the base and actual root.
Seven carried process/runner/test/config files are independently byte-matched
to `a8b3606`. The composition consists of the following twelve exact paths;
**all remain withheld as a complete implementation chain**:

| Candidate path | SHA256 |
| --- | --- |
| `configs/coloring_scaling_pilot.json` | `9de032188f76097f436763d4c5a2f442470ac0aeac303f81ca7689f580057b92` |
| `docs/scaling-harness.md` | `12a54a04c8030f8da1ed3157749840289e0da9d977b186ba1dc0d24762267147` |
| `src/logique/benchmarks/scaling.py` | `4f9c15bd952af690cec181ad7e7490f9dbcd431cbe44912d383352c9141a59a1` |
| `src/logique/synthesis/native.py` | `58e30c4fe5e152975347e15252f055eed3ae6d44c262a8feba5c1c23b5ac28ff` |
| `src/logique/synthesis/process.py` | `e1d3f02bc9527c18d9d085646c6100b88ced3ec89bd16ebf319b48a92adf2968` |
| `tests/test_native_contract.py` | `3b3addc84897833768be6732f9946a63f231335d5c41b856d6498faf2adb093c` |
| `tests/test_native_mapping_strategies.py` | `be86f804f92eb573d21d9009677853248fd9ef127a6a404d7a828ffb84205c25` |
| `tests/test_native_process.py` | `e3a3a0de2771d654e002f2cf6720173cbcaee078520845ae78796bdc12527e19` |
| `tests/test_native_process_composition.py` | `eff1bd2ecb2a5dde49ed9dbba5fb7a8e94a17740bf35857b2de93f88c2f1de93` |
| `tests/test_native_sat_pebbling.py` | `ba5d4e704e3803168d123317da9a2c4a396ef9f72f743d09be8446eb172c3bc2` |
| `tests/test_scaling.py` | `3e5dd58876ac87595c37809fda485ab870bc89177110a598f37d1975e2f9ad0b` |
| `tests/test_scaling_cleanup.py` | `8bb493771894db9f658743f4a646daf1b15645bb6d7a502a1b176bc0c0e192fd` |

This review admits only its own blocking review record for coordinator use.
Candidate handoff `59aa7c1` is documentation, not implementation or metric
admission. Do not cherry-pick old withheld ancestors onto current native code
to bypass the composition gate. Already integrated input/helper/timer and SAT
source keep their existing independent scopes; this report does not roll them
back or extend them.

## Build, measurement and resource decisions

No native build or compiler invocation occurred. The immutable foundation
executable SHA256 is verified as
`6aa7357d2f64202584b14b0a14f8fb183379faf5907723cd24bd838b9be14a9a`;
the distinct previously admitted SAT build is verified as
`81bc6a786f29a5673881ef37c5fb0da02cec9d22a649b9d518d1b31db5d71571`.
These are identity checks, not new build admission or provenance repair.
Pins, binaries and the root default are unchanged.

**Zero selected compiler runs and zero new scientific scaling metrics.**
The original ledger SHA256 remains
`d650687aa6678189904c77929bab42f43332f218373eb8f641750805bc6650cc`.
Ten selected inputs plus twelve controlled settings, two profiles and five
slots give `(10 + 12) × 2 × 5 = 220` pending attempts. Actual prepared bytes and
canonical witness hashes match; eight supplied witnesses pass the independent
graph predicate, DSJC125.1/le450_5a witnesses remain unknown, and all selected
M remain unknown. Validation seeds 11/23/37/53/71 and graph seed1729 are unchanged.
BLOCK rejects before provenance lookup, output creation or compiler launch.
Unavailable stage splits remain null. No comparison, scalability, quantum
phase/restoration, C5, noise, FT/RUS, full Task8 or manuscript claim is admitted.

Declared before allocation: 120 seconds per supervised child, 300 seconds
cumulative, 2 GiB per process, serial numerical work and all compiler/BLAS/OMP/
Accelerate/Rayon/Qiskit parallelism one. Final supervised work totals
**68.875791 seconds**, including failed probes/audits; maximum wait4 high-water
is **88,391,680 bytes**. The largest explicit inherited memory fixture is64MiB.
No quantum statevector/operator/density allocation occurred. Darwin wait4 may
include reaped descendants; simultaneous group peak and hard allocation limits
are not claimed. Real ps denial is retained as null/false sampling availability.

## Preserved failures and next action

The first probe fixture omitted the required `truth` field and stopped during
its no-signal calibration. Its source, five failed fixture rows, log and receipt
are retained. A distinct corrected run passed. The first identity audit read
the candidate's earlier evidence manifest, which hashed `finish.log` before its
final print; it failed on that log. The actual later
`final-evidence-manifest.json` passes all589 entries. Neither event is attributed
to the candidate's signal correctness. The two later native-transfer failures
are genuine candidate failures and remain failed. Formatting preserves the
final probe AST; focused Black/Ruff and whitespace checks pass.

Read-only inspection commands retain tool exits but no separately measured
RSS; truncated reads were followed by focused reads. The initial reviewer turn
was interrupted before any numerical probe launched and resumed from the
unchanged checkpoint. Session/attempt identities and every subsequent command,
exit/time/RSS receipt are in the local checkpoint. All original rejections,
partial artifacts, historical metric failures, old128 history, current queue,
README and archives remain untouched.

**Next:** the dispatcher/coordinator assigns a narrowly scoped receipt-transfer
correction on the current composed source, then exact whole-chain independent
review including these two failures and the successful transaction probes.
Only whole-source ADMIT, coordinator integration and integrated checks may
precede a new dated selected execution configuration. Actual five-repeat
selected measurements and separate evidence review remain future work.
Do not rerun this completed review to poll the gate. Dispatcher alone launches
models and publishes root integration HEAD; this worker launches no models,
subagents, Codex subprocesses, API/paid fallback, hardware or excluded research.

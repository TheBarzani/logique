# Independent scaling receipt-transfer review — 20 November 2026

**Bounded review COMPLETE. BLOCK the whole composed process/native/scaling
implementation at correctness `f2f41c2dffe226dfc07551131581da11f5cb3724`, offered
HEAD `78aab2e8e33ebcefb24ec4e82367513838637dd5`. No candidate implementation path
is admitted for integration or selected execution.** The two original receipt-copy
failures are repaired, but a distinct handler-restoration tail still loses the
exception receipt and can replace an earlier body interruption. Passing runner
checks do not close that whole-source contract.

Task `scaling-transfer-review-1113162936`, assigned branch
`codex/coloring-scaling-transfer-review-1113162936`, starting base `f7432e3`.
The review branch was deliberately fast-forwarded to the entire offered candidate,
which already includes current admitted root `dcbe796dbf69b165db78c249ddf8ad99b1051a88`.
Current root remains at that identity. No semantic merge, candidate repair or root
write was performed. Only this report and
`tools/probe_scaling_transfer_review_1113162936.py` are new owned tracked changes. The diagnostic probe is committed separately as
`cf51300`; its deliberate exit1 assertions preserve the observed contract failures.

Evidence directories in this review worktree:

- `dump/1119204606-scaling-transfer-independent-review/` (R1): original probes,
  195-test shard, independent transfer matrix and retained interrupted supervisor.
- `dump/1120012004-scaling-transfer-review-closure/` (R2): resumed accounting,
  remaining inherited negatives, body-precedence reproduction, exact audit,
  source snapshots and final checkpoint/result.

## New blocking observations

At `src/logique/synthesis/process.py:100`, `_DeferredCancellation.__exit__`
restores the caller's SIGINT handler inside its `try`. Statements at lines107,
108 and109 then execute outside that handler's exception-catching region:
`if self.error is failure`, `break`, and `if failure is not None`.
A first real SIGINT at any of those statements raises directly from the restored
caller handler. It bypasses the receipt attachment at line96 and the saved-error
selection. This is inside the native call's context-manager exit, before that
call has returned to its caller.

The independent probe uses a real successful shell child and real sleeping
children stopped at a0.025-second boundary, including SAT timeout translation.
Its trace chooses only the signal point; OS waits, exits, receipts and signals
are genuine. It snapshots the completed receipt before injection, forbids further
waits/group cleanup or direct signals to reaped PIDs, verifies a subsequent real
wait raises ChildProcessError, and checks the restored handler and exception
object. No compiler, wait result, clock or child exit is fabricated.

**48 first-SIGINT cases:**30 retain the complete exception receipt at the
boundary, assignment, before/during dictionary copy and immediately before/after
handler restoration. **18 restoration-tail cases fail** the receipt equality:
three outcomes × three tail statements × dictionary supplied/omitted.
All18 propagate the identical first interruption, retain the handler and have
reaped leaders. In the nine cases with a dictionary, that dictionary remains
complete. In the nine default calls without a dictionary, the outgoing original
exception has no `accounting` attribute, so the documented exception-receipt
interface loses the completed receipt. This finding does **not** assert that
the runner's dictionary or saved row loses those fields.

| First SIGINT at tail comparison, dictionary omitted | Genuine boundary seconds | Genuine wait4 bytes | Return/status | Outgoing exception receipt |
| --- | ---: | ---: | --- | --- |
| Successful shell fixture |0.232828501|1,982,464|0 / exited|absent|
| Timeout fixture |0.033362293|32,768|−9 / timeout|absent|
| SAT timeout fixture |0.032355292|32,768|−9 / timeout|absent|

A second independent six-case probe establishes the more consequential ordering
failure. A real sleeping child's monitoring body raises a saved KeyboardInterrupt
or SystemExit object; owned cleanup reaps it and supplies genuine accounting.
The probe then sends its first real SIGINT at each of the three tail statements.
**All six propagate the later signal's KeyboardInterrupt instead of the earlier
body exception.** The caller dictionary and earlier exception retain identical
receipts; the outgoing later exception has none. Thus the candidate's claimed
body-cancellation precedence is not preserved throughout restoration. This probe
raises the body exception deliberately; it does not claim two OS signals occurred.
No case needed reviewer emergency cleanup or demonstrated a live-child leak.
These are deterministic boundary observations, not failure probabilities under
random timing, synthesis performance measurements or quantum correctness tests.

## Repairs confirmed and restrictive inherited gates

Both exact `d7b9496` native-copy reproductions now pass. Each executes one prior
row, then interrupts the second call immediately before its receipt copy. The
success fixture is a specified two-input XOR network for a two-vertex edge at
k=2: four bitstrings and two positive assignments. Timeout uses a sleeping child.

| Second call | Boundary seconds | Charged enclosing seconds | Retained wait4 bytes |
| --- | ---: | ---: | ---: |
| success |0.116923500|0.119913417|1,982,464|
| timeout |0.035150290|0.037178125|32,768|

Both save valid interrupted JSON, unchanged prior rows and one current charge;
all genuine receipt fields, original first exception and actual reaping survive.
No post-injection wait/cleanup signal or later native call occurs. Failed-call
charging and runner persistence are therefore not relabeled as the new failure.

- Fresh maintained selection: **195 passed,317 deselected**, including all23
  candidate transfer/SAT/body-precedence regressions. Compiler/integration and
  compiler-dependent finalizer fixtures are excluded; a launch sentinel denies
  `boolean_synthesis`. The candidate's earlier monitor-reap status failure remains
  historical; its cause is not established by this fresh pass.
- Fresh preserved independent selection: **24 passed,one compiler case deselected**.
  Original B1/B2, exit/reap races, denial, descendants/unrelated-group survival,
  missing/null/negative/NaN charges, unavailable sampling and cumulative gates pass.
  Copies change only candidate-path constants; original assertions remain.
- Original transaction probe saved **90 completed case records** (two controls,
  88 first-SIGINT points), and the closure's separate run passes **nine** whole-run,
  body/persistence and partial-response cases. Every saved manifest was rechecked
  for valid JSON, unique repetitions and exact cumulative sums; all recorded
  leaders were reaped and emergency-cleanup lists empty. **The90-case supervisor
  exit/time/RSS receipt is missing after the turn interruption.** Its printed
  completion and saved records are qualified observations, not a fully receipted
  successful command. No receipt was reconstructed or the completed90 cases rerun.
- The prior cleanup `44ad4ba`, cancellation `bfc440b`, finalization `0f8c9c7`
  and current-composition `d7b9496` decisions were read with the actual cumulative
  process/native/scaling source. Older finalizer ADMIT does not admit this new
  composition. SAT response validation remains AST-identical to current root;
  SAT_LIMITS and its validation suffix remain byte-identical. Ordinary bounded
  SAT keeps its existing admission, not a new solver/build/performance certificate.

## Exact whole-path decision

All15 offered whole-file identities match the candidate checkout, this composed
review branch, committed HEAD and candidate checkpoint. Ten inherited correctness
paths remain identical to `f444e42`; native/process are its two corrected paths,
with one new regression file. The two documentation paths are preserved dated
handoffs, not execution admission. **WITHHOLD every listed path as this cumulative
offer; do not integrate a fragment by appealing to an older admission.** Only
this review record and its unique bounded diagnostic probe are offered for
coordinator use. No candidate source or scientific metric is newly admitted.

| Offered path | SHA256 | Decision |
| --- | --- | --- |
| `configs/coloring_scaling_pilot.json` | `9de032188f76097f436763d4c5a2f442470ac0aeac303f81ca7689f580057b92` | WITHHOLD |
| `docs/scaling-harness.md` | `12a54a04c8030f8da1ed3157749840289e0da9d977b186ba1dc0d24762267147` | WITHHOLD |
| `src/logique/benchmarks/scaling.py` | `4f9c15bd952af690cec181ad7e7490f9dbcd431cbe44912d383352c9141a59a1` | WITHHOLD |
| `src/logique/synthesis/native.py` | `f509e8a64bd844f91431a87bcce78eaff09e54f0addc0e557a09ba495e02dcc3` | WITHHOLD |
| `src/logique/synthesis/process.py` | `0c78e92422faea191baa5570598c0bb2ce69a1707378b1c9e3f2593ac306a5f6` | WITHHOLD |
| `tests/test_native_contract.py` | `3b3addc84897833768be6732f9946a63f231335d5c41b856d6498faf2adb093c` | WITHHOLD |
| `tests/test_native_mapping_strategies.py` | `be86f804f92eb573d21d9009677853248fd9ef127a6a404d7a828ffb84205c25` | WITHHOLD |
| `tests/test_native_process.py` | `e3a3a0de2771d654e002f2cf6720173cbcaee078520845ae78796bdc12527e19` | WITHHOLD |
| `tests/test_native_process_composition.py` | `eff1bd2ecb2a5dde49ed9dbba5fb7a8e94a17740bf35857b2de93f88c2f1de93` | WITHHOLD |
| `tests/test_native_sat_pebbling.py` | `ba5d4e704e3803168d123317da9a2c4a396ef9f72f743d09be8446eb172c3bc2` | WITHHOLD |
| `tests/test_scaling.py` | `3e5dd58876ac87595c37809fda485ab870bc89177110a598f37d1975e2f9ad0b` | WITHHOLD |
| `tests/test_scaling_cleanup.py` | `8bb493771894db9f658743f4a646daf1b15645bb6d7a502a1b176bc0c0e192fd` | WITHHOLD |
| `docs/scaling-current-composition.md` | `dbc08786547d386e376204487a0e1aca04c9fd28fca1c9e121edda3474fe4a45` | WITHHOLD |
| `tests/test_native_receipt_transfer.py` | `9128717102c25936e2d77b5bf16dd756d3ffb360dc652a5e8fba328b8a150ce4` | WITHHOLD |
| `docs/research/scaling_receipt_transfer_20261119.md` | `5b912345b7b78529e6efb13244010549ea39f14cb9790dd1cdb42c45b80ae181` | WITHHOLD |

The audit binds96 current source/dependency context files,13 actual imports in
this review checkout,1,301 candidate evidence entries and589 previous candidate
entries, with zero mismatches. Root source outside the offered native replacement
is unchanged; bridge sources and dependency gitlinks match. The exact original
reviewer probe is byte-identical to its committed version. Formatting preserves
the new probe's AST; Black and Ruff pass. No native build was needed or run.
The prescribed unchanged foundation binary remains SHA256
`6aa7357d2f64202584b14b0a14f8fb183379faf5907723cd24bd838b9be14a9a`, hash-checked
with zero invocations. Root's older default and all pins remain untouched.

## Scientific scope, resources and preservation

**Zero selected compiler invocations; all220 planned slots remain pending.**
The exact original ledger remains SHA256
`d650687aa6678189904c77929bab42f43332f218373eb8f641750805bc6650cc`.
Its10 inputs plus12 controlled settings, two profiles and five repetitions give
`(10+12)×2×5=220`. Prepared hashes and canonical witness identities are bound;
eight witnesses are supplied, DSJC125.1/le450_5a witnesses and larger M remain
unknown. Seeds11/23/37/53/71 and graph1729 are unchanged. BLOCK rejects before
provenance lookup, output creation or launch. Missing native stage splits stay
null. No scalability, superiority, quantum phase/restoration, C5/noise, FT/RUS or
full-paper admission follows. Final Astra scientific BLOCK and all restrictive
C5/dirty20/partial-FT decisions remain binding; none was replayed here.

Resources were declared before allocation:120s/child,600s cumulative across both
attempts,2GiB/process, serial numerical/compile children and configured threads1.
Largest explicit inherited allocation64MiB; no quantum arrays. Measured supervised
commands total **37.140556s**, maximum terminal wait4 **89,276,416 bytes**.
A separate120s conservative reservation for the unreceipted90-case command gives
**157.140556s budget charge**, not an invented measured duration. Terminal
Darwin wait4 may include reaped descendants; simultaneous group peak and a hard
allocation cap are not claimed. Real ps denial stays null/false in receipts.
The resumed process-list check found no surviving probe process before new work.

The first new matrix run stopped at its initial expected-status assertion before
completing its matrix. Its original source, log, exit1 receipt and partial output
remain. That version did not serialize the genuine receipt before this assertion;
its exact observed status cannot be recovered from the retained record. A distinct
version moves diagnostic recording before assertions and completes48 cases with
unchanged limits and assertions, exposing the18 failures above. The first version
is not discarded or mislabeled as a clean pass. The later body-tail run exits1
on its six identity failures. Candidate's retained monitor-reap failure and all
older failed/partial artifacts remain. Initial Git metadata and resumed process
inspection sandbox denials were resolved with scoped automatic escalation; no
approval rejection. Inspection-only absent guessed paths and truncated reads
remain tool events; focused reads supplied the missing text. Read-only tool/Git
commands have tool timing, not fabricated independent RSS receipts.

## Required correction and next action

Protect receipt attachment and first-error precedence through the **entire
restoration tail**, including lines107–110 and equivalent native return/raise
handoffs. Preserve the earlier body object when a later signal arrives; attach
the completed genuine receipt to the outgoing exception even with no optional
dictionary. Do not relabel completed process status, repeat cleanup/wait/signal,
or launch another child. Retain the18 receipt and six ordering negatives plus
all now-passing transfer/transaction/SAT/denial/budget gates. Review new whole-file
bytes independently; a local green test or queue completion is insufficient.

The dispatcher/coordinator must assign that focused correction and exact review
before any selected executor opens its gate. Existing downstream execution and
evidence owners should consume this BLOCK without polling or blind runs. Only
whole-source ADMIT, exact coordinator integration and integrated checks may precede
a new dated missing-only five-repeat configuration and separate evidence review.
No model/subagent/Codex subprocess, API/paid fallback, purchase, install/sync,
hardware, excluded research, queue mutation or push occurred. Root README,
histories, archives, pins and all earlier records are preserved.

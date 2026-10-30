# Independent scaling cleanup review — 29 October 2026

**Decision: BLOCK the exact candidate process/measurement contract and selected
compiler execution. This bounded review is COMPLETE.** The old deadline,
Darwin exit/reap/kill race and cumulative-budget regressions now pass. A single
SIGINT delivered during cleanup still abandons a live owned leader and bypasses
its final receipt. Passing the focused suite does not admit these bytes.

Resumed task `scaling-cleanup-review-1028174846`; session ID not supplied.
Reviewer branch `codex/coloring-scaling-cleanup-review-1028174846`, intake
`a6a18c1`. The earlier quota interruption had produced no review document or
numerical evidence directory in this worktree; it was not a scientific rejection.
This completion uses the newly authorized 29 October bounded continuation,
`dump/1029204240-coloring-dispatch-continuation/queue.json`. The old queue and
hard128 history remain immutable; the new authorization does not relax any
scientific gate. Deadline remains 2 November 00:00 local.

Candidate:
`/Users/mar/codex-work/logique/dump/1028174846-full-research-integration/worktrees/scaling-cleanup-fix`,
clean HEAD **`7145b87485eb68bd602f65a3520c46075febfba7`**. Actual candidate source
was explicitly imported and checked against Git blobs and retained checkpoint
hashes. Main correctness `c8ea5b3b882484a8cf993f6ec9f7828a3cd5542f` and follow-up
`8cac9b3d4a33369427bb274816b14945afaa9238` were both reviewed. No candidate source
was edited or integrated.

## Blocking reproduction: cancellation inside cleanup loses ownership

`src/logique/synthesis/process.py:183–185` catches monitor exceptions, then calls
`_cleanup_owned` **outside** that handler. Its initial nonblocking reap at line30
and later cleanup operations are interruptible. A KeyboardInterrupt there skips
the group kill, mandatory reap and receipt construction at lines186–224.
`run_native` can only copy an exception receipt if one exists. The runner's
new interruption handler correctly saves an interrupted row, but cannot recover
the lost process ownership.

Independent regression `test_review_edges.py::test_sigint_during_cleanup_reaps_and_preserves_receipt`
uses a real executable Python child sleeping ten seconds and a 0.04-second
boundary deadline. A wrapper performs every real `wait4` and delivers one actual
`os.kill(os.getpid(), SIGINT)` immediately after the third WNOHANG returns zero:
first monitor poll, deadline poll, then cleanup's initial reap. Only ps output is
stubbed empty to make scheduling deterministic. No wait result, child exit or
signal denial is fabricated. This represents one cancellation arriving during
timeout cleanup, not repeated signals or an unkillable child.

Both direct-native and full-runner variants fail the ownership assertion:

| Observation | Direct native | Through scaling runner |
| --- | --- | --- |
| Child PID in saved reproduction | 4597 | 4598 |
| Leader still running after exception | true | true |
| Reaped by candidate | false | false |
| Exception accounting | absent | absent |
| Caller process receipt | empty | fallback only |

The runner saves one `interrupted` row and an `interrupted` manifest, launches no
later row, and charges **0.04302620887756348 s**. Its fallback explicitly reports
unavailable RSS; it does not fabricate a zero peak. These are improvements, but
the live child continues after the boundary has returned. No `leader_reaped`,
cleanup status, return code or wait4 measurement exists in that receipt.
This is **not** the old zero-charge bug and is not a claim that interruption
status itself remains wrong.

The reviewer terminated the two owned groups and waited for their leaders in
the tests' `finally` blocks. That emergency cleanup is not credited to the
candidate. Logs retain both failing assertions and the interrupted manifest.
The fake executable is a process-control fixture with its own checked hash,
not a native compiler result or a selected scaling experiment.

Required correction: keep ownership through cleanup and final accounting even
when cancellation first arrives in that phase. Defer or capture cancellation,
complete owned-group termination/reaping and receipt finalization, then propagate
the original interruption. Preserve timeout reason and cancellation information,
genuine unresolved permission errors, descendant ownership and no signaling of
a reaped/reused leader PID. Do not merely swallow SIGINT or mark an unreaped
leader as cleaned. Retain these two regressions plus the previous race/denial/
budget tests. Independently review the new exact hashes before integration.

## Reproduced improvements and limits

- **Original B1/B2 and cleanup race:** all 18 preserved independent regressions
  pass, including three real delayed exit-between-WNOHANG-and-kill cases and the
  cumulative ledger case. The original two regressions are byte-identical; the
  three later scripts differ from their originals only in candidate-path constants.
  A real successful native boundary reduces the next timeout to the remaining
  cumulative budget. Late completion is rejected by the monotonic observed
  deadline; cleanup latency remains additional.
- **Ordinary exception and cleanup paths:** success, timeout and monitor-phase
  KeyboardInterrupt remove tested same-group descendants while an unrelated
  group survives. Deterministic first/persistent group-signal denial tests retain
  events, reap the leader, distinguish unresolved cleanup, and block later calls.
  Direct-PID fallback is restricted to an unreaped owned leader. These tested
  paths do not cover the failing cleanup-phase cancellation above, detached
  sessions, arbitrary external reapers or a hard termination deadline.
- **Cumulative charges:** failed launched calls charge at least measured call
  time; explicit unresolved cleanup prevents later calls. New independent tests
  cover empty, null, negative and NaN wall receipts: one failed call exhausts a
  small budget, subsequent rows are `budget_exhausted`, RSS is null and fallback
  scope is explicit. A missing receipt is not evidence of a reaped child.
- **Memory and output controls:** config accepts positive integer memory strictly
  below7GiB (default6GiB), rejecting bool, zero, negative, floats and >=7GiB before
  launch. A 384MiB/1MiB fixture verifies memory/output forwarding through native
  to the process boundary, without adding either field to compiler JSON.
  Default native timeout180s and omitted compiler controls retain compatibility.
  Enforcement is sampled group RSS when available plus terminal wait4 checking,
  not a hard allocation cap. Observer-denied and unattempted sampling both retain
  null group RSS and false availability; successful empty mocked listings are
  fixture observations, not measured host group memory.
- **Darwin measurement scope:** the fresh 64MiB descendant probe reports parent
  self high-water16,089,088 bytes, descendant self82,362,368, and boundary wait4
  **82,526,208**. The label correctly allows reaped descendants and excludes
  isolated-process or simultaneous-group interpretations. Real ps was denied;
  its error and null sampled group RSS remain in the receipt.
- **Selected adapter:** the actual immutable selected ledger reproduces the
  saved candidate draft exactly: ten prepared inputs, twelve controlled settings,
  two profiles and five repetitions/220 pending rows. Seeds11/23/37/53/71 are
  validation seeds; graph seed1729 is separate, with no native random seed.
  Eight witnesses remain supplied, DSJC125.1/le450_5a witnesses unknown and all
  M unknown. Config, ledger budget/gate and prepared-input hashes are checked.
  BLOCK is preserved and rejected before output creation/compiler launch. Tests
  also reject changed prepared bytes. Zero selected compiler calls occurred.

The focused 150-test suite includes five real **tiny compatibility** repetitions
and inherited small native contract fixtures. These do not replace the planned
larger five-repeat study. Compiler Boolean checks do not prove quantum phases,
arbitrary-target action, workspace restoration or Grover behavior.

## Commit and metric admission boundaries

**No new scaling implementation/correction commit is allowed to integrate as an
admitted process contract by this review.** Keep the following complete chain
withheld until the cancellation correction and its independent review:

| Original implementation/correction | Imported candidate commit | Scope |
| --- | --- | --- |
| `5da2e1e` | `b5cb3da` | Native boundary and process tests |
| `fd62200` | `5a7c3da` | Scaling runner/config/guide/tests |
| `36e730e` | `65f091f` | Positive-branch regression |
| `4bd9a16` | `b755435` | Prior deadline/RSS correction |
| new | `c8ea5b3` | Cleanup/failure charges/memory/adapter correction |
| new | `8cac9b3` | Interrupted manifest/row follow-up |

Historical checkpoint commits `f095a5c`→`934be18`, `01935f4`→`f84e35e`, and
new checkpoint commits `7157de5`/`7145b87` are records, not scientific admissions.
Already admitted input/helper/timer preparation `c39df51`→`64e210a` and
`605c87d`→`8955a9f` is unaffected within its prior exact scope. This report may be
integrated as a blocking review record; the reviewer performs no integration.

No selected timing/RSS/network metric, scalability conclusion or full Task8
admission follows. Future metrics must distinguish encoding, combined bridge
time and enclosing observation/cleanup time. Missing optimization/mapping/
lowering stage measurements stay null. wait4 high-water remains qualified as
above; sampled memory unavailable is not zero or proof of a live cap.
No FT/RUS, ideal-amplitude, comparative-superiority or paper approval is given.

## Exact candidate identities

These actual SHA256 values match the candidate files and HEAD7145b87 Git blobs.
The full selected source/input/review/evidence identity audit is saved in
`audit-result.json`; no recursive old-results scan was performed.

| Candidate-relative path | SHA256 |
| --- | --- |
| `src/logique/synthesis/process.py` | `4183788b8569d3712bf880c9556e8b490ef3ac806857bb5dbce259190bf7e3b1` |
| `src/logique/synthesis/native.py` | `9c72836033842abff99855cf1bf87494879d57ff95f02efc683115510c50c02e` |
| `src/logique/benchmarks/scaling.py` | `19179117525499aeb52508bb3e305e324972199c64ebff8ef9236a3b4ce81f56` |
| `tests/test_scaling_cleanup.py` | `094dfddb0aae37025f8dadef01a8e013d0a9c08efade962b6faae67c053ace83` |
| `tests/test_native_process.py` | `a70f419dad10d8221b11b4e4da431814309bf534b02a892ed285ada105ebb2c5` |
| `tests/test_scaling.py` | `3e5dd58876ac87595c37809fda485ab870bc89177110a598f37d1975e2f9ad0b` |
| `tests/test_native_contract.py` | `3b3addc84897833768be6732f9946a63f231335d5c41b856d6498faf2adb093c` |
| `docs/scaling-harness.md` | `5dc78f8f499bc9afe88450c9d3e935c7edc08c6dc7c160650074925be65966af` |
| `configs/coloring_scaling_pilot.json` | `9de032188f76097f436763d4c5a2f442470ac0aeac303f81ca7689f580057b92` |
| `configs/coloring_scaling_selected.json` | `d600d499c8ab44f891297868e5a75d40fb6c80ca1c5d48c9ca3a308d0fe1319e` |

Prescribed native executable SHA256 verified before every supervised invocation:
`6aa7357d2f64202584b14b0a14f8fb183379faf5907723cd24bd838b9be14a9a`.
No native rebuild or dependency change occurred. Old incorrect dependency fields
remain historical; the inspected correction is
`/Users/mar/codex-work/logique/dump/1028174846-full-research-integration/selected-provenance-correction.json`.
It records tracked gitlinks, not newly realized build checkouts.

## Resources, retained failures and actionable handoff

Fresh evidence in this review worktree:
`dump/1029204659-scaling-cleanup-independent-review/`, created with
`new_dump_directory`. `checkpoint.json` binds commands, receipts, test scripts,
selected source/evidence hashes, this report and its commit. Every output/log
has a fresh exclusive name and every pytest basetemp is new.

| Serial supervised check | Result | Boundary seconds | wait4 high-water bytes |
| --- | --- | ---: | ---: |
| Candidate focused compatibility | 150 passed | 19.601426 | 86,753,280 |
| Four preserved independent scripts | 18 passed | 5.838134 | 82,526,208 |
| New interruption/empty-receipt edges | **2 failed, 5 passed** | 0.872420 | 43,302,912 |
| Mapping mock compatibility | 6 passed, 215 deselected | 0.476919 | 77,152,256 |
| Initial identity audit | reviewer path-expression assertion failed | 0.404530 | 27,279,360 |
| Corrected identity/selected-adapter audit | passed | 0.381249 | 27,721,728 |

Total supervised boundary **27.574678 seconds**, under300s cumulative and120s
per command. Existing research Python, actual candidate PYTHONPATH, root EPFL
cache, compiler/BLAS/OpenMP/Accelerate/Rayon threads1 and Qiskit processes1 were
explicit. Declared2GiB terminal wait4 checks and prebounded fixtures were used;
no hard allocation cap or supervisor group-RSS measurement is claimed. The
largest explicit memory probe allocates64MiB. Inherited tiny superposition tests
assert <=5 wires before execution; no dense full Operators or larger selected
study ran. All jobs completed without supervisor timeout/OOM. Deliberate timeout
and process-tree fixtures are regression evidence, not compiler performance.

The initial identity audit assumed an absolute old path where the original
scripts used a relative expression. Its source/log/receipt are retained; the
corrected audit verifies that only candidate constants changed. This reviewer
error is separate from the two real candidate failures. Candidate checkpoint
source/evidence hashes, old pilot manifest and earlier review scripts were
checked without replaying hundreds of historical artifacts. Original110 tiny
attempts,145 mapping-suite failures, B1/B2 and earlier cleanup failures, and the
prior author's overwritten attempt1 full-log/reconstructed-receipt limitation
remain explicit and untouched. Focused passes are not full-suite validation.

AGENTS.md, CLAUDE.md and the complete revamp plan were read, along with the
resumption/batch/integration matrices, their linked exact reviews, all scaling
blocks, candidate checkpoints/source and29October hard-bound handoff. Full
scientific scope remains open. No queue edit, model/subagent/Codex launch,
API/paid fallback, purchase, sync, hardware, physicalQEC, precolored research,
conditional-workspace synthesis or push occurred. Root README, histories,
archives, pins, prior evidence and candidate files were preserved.

**Next action:** assign a fresh bounded cleanup-phase cancellation correction
with these exact reproductions, then independent exact-source review. Only an
ADMIT decision can precede coordinator integration, integrated checks and a new
dated selected execution config. Actual selected five repeats and independent
evidence review remain separate work. Do not relaunch this completed review to
poll the gate. Dispatcher alone launches successors and publishes integration
HEAD. Final research/native/offline-notebook/isolated135/final Astra checks and
all remaining full-plan work stay open.

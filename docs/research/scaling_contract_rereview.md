# Independent scaling contract re-review — 28 October 2026

**Decision: BLOCK the candidate process/resource contract. This bounded review
batch is COMPLETE.** B1's late-success classification and B2's RSS label pass
their original regressions, but the cleanup correction retains an exit/reap/kill
race that loses timeout accounting and bypasses the cumulative study budget.
No implementation or pilot is admitted by this review.

Task: `scaling-contract-rereview-1028023823`; session ID not supplied.
Reviewer branch: `codex/coloring-scaling-contract-rereview-1028023823`, intake
`fc734b386449e69716d0ac3018b878a23e05ba95`.
Candidate root:
`/Users/mar/codex-work/logique/dump/1028023823-full-revision-implementation-coordinator/worktrees/scaling-fix`.
Reviewed HEAD: `01935f432fca9c10a5451e5711c3716607998d71`, correctness commit
`4bd9a16`, inherited `5da2e1e`, `fd62200`, `36e730e` and checkpoint `f095a5c`.
Ancestry and actual imported candidate source were checked. These bytes remain
unintegrated. Only this review document is committed by this worker.

The reviewer read AGENTS.md, CLAUDE.md and the entire revamp plan, then the
28 October resumption/batch documents, candidate correction checkpoint, and
integration's original scaling review/triage. Renewed full-plan authorization
supersedes historical narrow prompts. No models, subagents, Codex subprocesses,
API/paid fallback, sync, native build, hardware, push or integration was launched.

## Blocking counterexample: cleanup still races with leader exit

At `src/logique/synthesis/process.py:133`, the final nonblocking `wait4` can
report that the leader is still running. It can exit before `killpg` at line 139.
The real Darwin call then raises `PermissionError: [Errno 1] Operation not
permitted`. Only `ProcessLookupError` is caught. Control skips the final reap at
line 143, resource accounting, and the intended `ProcessLimitError("timeout")`.
The new reap-before-kill check handles a leader already exited at that check;
it does not close the interval between the check and the signal.

Independent reproduction uses a real Python child sleeping 0.08 s, a 0.02 s
budget, and a 0.15 s observer delay **after** the third actual nonblocking wait
returns zero (the cleanup wait). The read-only ps probe is stubbed to an empty
listing so scheduling follows that path. `os.killpg` and the child exit are real;
no signal error, wait result, or child completion is fabricated. The delay
models a descheduled observer. All three wait results were `(WNOHANG, 0)`.
The regression failed initially and in **three further independent invocations**
with the same `PermissionError` at line 139. See `edges.log` and
`confirmation.log`; the saved tests contain the complete reproducer.

This is consequential for the study budget. In a separate five-attempt harness
test, the same real process boundary is used through a small replacement for
`scaling.run_native`, with cumulative budget 0.04 s and the same delayed cleanup.
The expected ledger is one timeout followed by four `budget_exhausted` rows.
Actual results:

- All five calls launched, each receiving the original 0.04 s budget.
- All five rows were `failed` with the real `PermissionError`.
- Their wall durations were 0.2060010000, 0.1964744590, 0.2052728338,
  0.2046633749 and 0.2070230409 s.
- All five `native_process_seconds` fields were null. Cumulative native wall
  remained zero because `scaling.py:507` adds `accounting.get("wall_seconds", 0)`.

These are bounded synthetic compiler-boundary regressions, not native compiler
performance measurements. They show that cleanup failure bypasses the intended
resource ledger even though no late result is incorrectly labelled successful.
`scaling.py:490` catches the OSError as an ordinary failed row and continues.
The confirmation job had four failed tests: three direct reproductions and this
budget regression. Its wrapper exits zero after saving receipts; the recorded
**pytest exit code is 1**, not a green test claim.

Required next correction: make the owned-group cleanup resilient to a leader
exiting between the final check and signal, guarantee reap/accounting through
cleanup failures, and preserve timeout/interruption semantics. A genuine signal
permission failure must remain explicit; do not simply swallow EPERM or skip
surviving descendants. Ensure failed launched work consumes the cumulative
budget (or stops the study conservatively if accounting is unavailable). Add
this exact race and cumulative-ledger regression, retain interruption/success/
timeout descendant cleanup, then obtain a fresh exact-hash independent review.
No corrected implementation is proposed or silently installed by this reviewer.

## What passed and what those passes establish

The candidate process/scaling/native-contract tests plus byte-identical copies
of the **two original independent review regressions** passed **114/114**.
No tests were skipped. The suite includes the real five-repeat tiny harness
fixture, native default/override JSON compatibility, common preprocessing and
legacy default behavior, invalid controls, budget statuses, witnesses and
preallocation guards. The added process controls remain outside the native JSON
request; the default timeout remains 180 seconds. Actual native execution used
the required hash-verified private executable, with no rebuild or changed pins.

Nine further independent tests passed. They assert candidate module paths;
ordinary success and unavailable group sampling; late successful wait4 observed
past deadline; delayed watchdog/reap-before-kill when the leader is already
finished; remaining-time-capped sleep/probe arguments; owned descendants on
success, timeout and KeyboardInterrupt with an unrelated group surviving; and
small cumulative-budget exhaustion through the real process boundary.

Source inspection corroborates the monotonic deadline (`perf_counter`) from
setup to observed completion. The deadline is checked before accepting a
completed wait4 result. Probe waits and sleeps use the remaining budget.
Completion observed at/after the deadline is a conservative timeout, including
an actual exit before a delayed observation. Cleanup-only reaping leaves
`completion_observed_seconds` null. Cleanup and scheduling can exceed the budget;
this is not a precise child runtime or a hard termination deadline.

An additional **passing** real-native-then-slow-child fixture specifically checks
subtraction of prior work: a 0.4 s cumulative budget became
0.2889951249584556 s after a successful native boundary lasting
0.11100487504154444 s. The next call timed out; the three remaining rows were
`budget_exhausted`. This correct ordinary path does not cover the failing cleanup
path above.

An independent parent/reaped-descendant probe measured the immediate parent's
self peak as **16,023,552 bytes**, its 64 MiB-allocating descendant's self peak
as **82,345,984 bytes**, and boundary wait4 high-water as **82,509,824 bytes**.
The new label accurately says per-invocation OS wait4 high-water, which **may
include reaped descendants**, neither isolated-process nor simultaneous-group
RSS. The candidate's own stronger RSS regression passed too. Unavailable ps
sampling stays null with its error, rather than becoming measured zero. No
new direct-only or whole-group memory interpretation is admitted.

## Execution bounds and preserved evidence

Fresh evidence directory under this reviewer worktree:
`dump/1028025301-scaling-contract-rereview/`, created with `new_dump_directory`.
Commands, imports, limits, stdout/stderr, pytest exit codes, time/RSS receipts,
fresh generated harness artifacts and failures are saved there.

| Job | Result | Boundary wall (s) | Darwin wait4 bytes | Wall timeout (s) |
| --- | --- | ---: | ---: | ---: |
| Candidate suite + original regressions | 114 passed (17.39 s pytest) | 17.627164459 | 84,754,432 | 120 |
| Independent initial contracts | 9 passed (3.60 s pytest) | 3.776993583 | 42,614,784 | 120 |
| Cleanup/budget/RSS edges | 1 failed, 2 passed (1.20 s pytest) | 1.442569375 | 82,509,824 | 30 |
| Race confirmation + failing budget ledger | 4 failed (1.71 s pytest) | 1.847952750 | 42,909,696 | 30 |

Jobs ran serially using `/Users/mar/codex-work/logique/.venv/bin/python`, explicit
candidate `src` PYTHONPATH, `/Users/mar/codex-work/logique/.cache/epfl` and all
BLAS/OpenMP thread limits 1. The cumulative review wall budget was 240 s;
measured test-job boundaries total about 24.695 s. CPU limits were 120/30 s per
job. Each job had a 2 GiB terminal wait4 budget check; all measured peaks fit.
The largest explicit allocation fixture is 64 MiB. Existing tiny native quantum
fixtures assert at most five qubits before simulation; no dense Operator study
or large statevector study was run. These compatibility tests do not certify
quantum correctness of the scaling study.

An initial supervisor launch failed **before test execution** because Darwin
rejected RLIMIT_AS. Diagnostic probes also rejected RLIMIT_DATA/RLIMIT_RSS and
ps access; RLIMIT_CPU worked. This failure, original supervisor and empty launch
log are retained, with unknown initial wall/RSS explicitly null. The retry uses
fresh exclusive filenames. Memory enforcement is therefore **not** a hard
aggregate cap: terminal wait4 checks, prebounded small fixtures and the suite's
allocation guards were used. Simultaneous group RSS was unavailable. The saved
receipts state these limits rather than inventing measurements.

Thirty-one relevant pre-existing files (including candidate changed bytes, reused
source/tests/input, original review/triage, root README and correction attempt
receipts) were checked unchanged before/after. Fourteen inherited candidate
identities also match the original review's recorded hashes. Only fresh review
evidence was additionally hashed; the original **331-artifact verification was
not repeated**. Candidate and integration source, user README, old evidence,
archives, histories, dependency pins and binaries were not edited.

The original 110-attempt pilot remains preserved and unadmitted by completion.
Its 12.4020618736 s is boundary wall and 0.9708516220 s is the combined bridge
timer, not disjoint stages. Old RSS labels/values are historical and unchanged.
The original implementation's **145 mapping-suite failures** remain explicit;
this focused green suite is not a full-suite claim. Correction attempt 1's full
log was previously overwritten by its author; its reconstructed receipt and
transcript-tail limitation remain documented. Attempts 2–4 and this review's
new failure logs are preserved; no claim of complete attempt-1 retention is made.

## Exact identities binding this BLOCK decision

The following are actual candidate hashes, not copied assertions of identity.
The first three are the changed correctness source/test/guide. The rest bind
reused relevant code and executed tests/config/input.

| Candidate path | SHA256 |
| --- | --- |
| `src/logique/synthesis/process.py` | `9c94548e725684a3eeef1eaf85eca16672e87ee438a69f48d42e9d52942491e4` |
| `tests/test_native_process.py` | `a70f419dad10d8221b11b4e4da431814309bf534b02a892ed285ada105ebb2c5` |
| `docs/scaling-harness.md` | `ab36adee787c310b483ce5d4ad54b1b79f5cc8d1a8e6a2e6d32d625479e1aa08` |
| `src/logique/synthesis/native.py` | `24e9c4ebb6f7604956b9328490257bbdeac635374dd3c2f58cf5cb3cc63647c5` |
| `src/logique/benchmarks/scaling.py` | `43070e357be798003868db28585e648b8ba6158703eabe2f4b11cc8fe8454d1d` |
| `src/logique/coloring/encoding.py` | `000bb92b33757dbb576199f44c82003da4e12c40185ad2d99813b54427f6b837` |
| `src/logique/coloring/dimacs.py` | `9b10db884cc75828443a77f03fa22ad2ebe664990ce0474e1ef644f71bd5b2b1` |
| `src/logique/coloring/model.py` | `b99c29bf82e6767974d411dd2dd3b9d8bd7a71816253de9d707d9d3e682248fb` |
| `src/logique/verification/classical.py` | `4d7d0e4747e2e1203a35ed6069635422768a172e94dfe00518f7f40a2853928c` |
| `src/logique/verification/quantum.py` | `6ea1bb4ffaac37f18ba1b423bf4419e9e0c822d600ea2033629fa55397107cdc` |
| `src/logique/benchmarks/runner.py` | `6f08f2934833452e89d6a23c9c1debfd4ee158644e2cb4f427324cfbd0548dc4` |
| `src/logique/benchmarks/provenance.py` | `1ee14c4da081385ae6a6569e01021e103c6555e8592e4bcbde09e4eb3599c8d3` |
| `tests/test_scaling.py` | `3e5dd58876ac87595c37809fda485ab870bc89177110a598f37d1975e2f9ad0b` |
| `tests/test_native_contract.py` | `3b3addc84897833768be6732f9946a63f231335d5c41b856d6498faf2adb093c` |
| `configs/coloring_scaling_pilot.json` | `9de032188f76097f436763d4c5a2f442470ac0aeac303f81ca7689f580057b92` |
| `SCALING_CONTRACT_FIX_CHECKPOINT.md` | `c2df4c02cd51a595e29438ff977d36daa3afb46f6cd891df16346a7f7444c61c` |
| `external/native/boolean_synthesis/main.cpp` | `dcab4d7f3e6530a0071dde894776e1ae2ca4ae351807dfe27b7750ebbc375635` |
| `datasets/graphs/teaching/edge.col` | `311355d0a59e311d11919488f8ec66749566e07f43c13d08622bd67778219ed3` |

Native executable SHA256: `6aa7357d2f64202584b14b0a14f8fb183379faf5907723cd24bd838b9be14a9a`.

| Review evidence file | SHA256 |
| --- | --- |
| `test_original_review_contract_attempt2.py` | `e186cc213c8daeb31438b3e8563d77c10d70a2eb6f21e3b245a80f6090f1ec20` |
| `test_independent_contract.py` | `b4e211a6c9b61e437ab8377144b4049a0a3ea2bb05d71e86063ff27118ae9e8f` |
| `test_cleanup_budget_edges.py` | `5488a95d19e5db4daf6b1d1dc6032e3c082bc2aa3afcebd7a13e1fdb226c3d25` |
| `test_cleanup_race_confirmation.py` | `23eae7f5e608b5236311a7da366ff0708b70a2b060df4c6cee0e72bb649cddf1` |
| `fresh-evidence-protection.json` | `56776be454d9a5f93e9908469ab8e6b37e0962b70674347c3170a7a9647cc818` |

`fresh-evidence-protection.json` binds 141 fresh files, including all saved test
scripts, commands, receipts/logs and generated fixture artifacts. The final
checkpoint separately binds this report and its commit. Do not rerun saved
supervisors into their old directories: outputs use exclusive names and pytest
basetemp could clear an existing fixture directory. Replay by copying scripts
to a newly timestamped run and updating the output location; preserve candidate
PYTHONPATH and the recorded binary/cache/limits. The decisive test can be run
alone using the saved `test_cleanup_race_confirmation.py` and `-k
leader_exits_between_final_reap_check_and_group_kill` against candidate source,
under a fresh bounded supervisor.

## Bounded release handoff

The dispatcher/coordinator should retain the current integration hold and route
the concrete cleanup/accounting correction to a fresh bounded owner, followed
by independent re-review. Preserve original harness commits separately from the
next correctness correction. Do not unblock selected scaling experiments or
integrate `4bd9a16` as admitted on the strength of 114 green tests or this
completed review task. A coordinator may preserve this BLOCK report as review
evidence; the dispatcher alone publishes integration HEAD.

No general scalability, quantum marking/phase/restoration, ideal-amplitude,
FT, RUS, comparative-superiority or paper approval follows. Full selected-DIMACS
work, missing/unsupported inputs, stage timing, protocol and manuscript scope
remain open under the full plan. No hardware, physical QEC, precolored research
or conditional-workspace synthesis was performed. This review has a concrete
completed decision and does not need to be relaunched merely because the
candidate is blocked or full scope remains open.

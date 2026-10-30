# Resumed independent selected execution review — 29 October 2026

**Scientific decision: BLOCK selected compiler evidence admission. Bounded task:
COMPLETE.** Source review `44ad4ba` rejects the exact cleanup candidate because
one SIGINT during cleanup can leave an owned child running without its final
receipt. Coordinator `97fde8a` correctly withheld that source and executed zero
selected compiler invocations. No five-repeat selected pilot exists to admit.
This is a concrete source rejection, superseding the earlier *missing-review*
prerequisite; the earlier review and all failed evidence remain unchanged.

Task `review-selected-execution-1029204240`; session
`01a18a50-d0f7-70a0-86cd-820a4742b8c2`; assigned branch
`codex/coloring-selected-execution-review-1028174846`, intake
`0b0f0766a552e8151f3eab5fff8f8acd8de437cc`.
Checkpoint in this worktree:
`dump/1029205928-selected-execution-resumed-review/checkpoint.json`.

## Current evidence and exact source

The root-level `SCALING_EXECUTION_HANDOFF.md` is absent. The actual latest
handoff is `/Users/mar/codex-work/logique/docs/research/scaling_execution_handoff_20261029.md`,
byte-identical to the timestamped original under
`/Users/mar/codex-work/logique/dump/1029205426-scaling-block-execution-handoff/`.
Both that coordinator checkpoint and this continuation queue's state/results
were inspected. Queue completion does not establish scientific admission.

Root integration HEAD is **`97fde8a137fcc5807c84603963f7b179f81b04d3`**;
candidate remains clean at **`7145b87485eb68bd602f65a3520c46075febfba7`** in
`dump/1028174846-full-research-integration/worktrees/scaling-cleanup-fix`.
Candidate process, native adapter, scaling runner and the bounded associated
source/test files match the coordinator's hashes and candidate Git blobs.
Root still lacks `src/logique/synthesis/process.py` and
`src/logique/benchmarks/scaling.py`; its native adapter matches its own Git blob,
not an assumed integrated candidate. No harness correctness commit is admitted.

The actual candidate `process.py` catches monitor exceptions but calls
`_cleanup_owned` outside the handler. Cancellation during its initial reap
escapes before termination, reaping and accounting. The runner's interruption
handler saves a fallback row but cannot restore lost child ownership. I inspected
these paths and verified the saved independent test scripts, logs and receipts
against their checkpoint hashes, without rerunning the completed source review.
Both retained direct/runner observations show a live unreaped child and absent
exception receipt. The runner's fallback charge is 0.04302620887756348 seconds
with unavailable RSS. Reviewer emergency cleanup is not candidate cleanup.
The saved 150 focused passes and 18 prior regression passes do not negate the
two failing cancellation regressions; neither are selected-instance repetitions.

| Evidence | SHA256 |
| --- | --- |
| Latest handoff, tracked and timestamped copies | `9effafc1e58ca16a6c73e446d4824ba0ff1023ebfdab96f33df71a1df6e68c85` |
| Independent cleanup review, matching commit44ad4ba | `7d295c74184078d616f7452f466757449ef58bb9ae72d4bc4dbb676c8dc3c0f3` |
| Candidate process.py | `4183788b8569d3712bf880c9556e8b490ef3ac806857bb5dbce259190bf7e3b1` |
| Candidate native.py | `9c72836033842abff99855cf1bf87494879d57ff95f02efc683115510c50c02e` |
| Candidate scaling.py | `19179117525499aeb52508bb3e305e324972199c64ebff8ef9236a3b4ce81f56` |
| Original selected ledger | `d650687aa6678189904c77929bab42f43332f218373eb8f641750805bc6650cc` |
| Coordinator remaining ledger | `996e20350fbf3248e5b22f7f12aadd1e5669f5e0bb70560ff338c41e3784c7ab` |
| Retained cancellation failure log | `975919a3d5a255ef9ac437ce4134dc5b719655288ac2b735f1d5baa09e123dbc` |

Full bounded identities and actual Git commands are in `audit-result.json`.
The prescribed native binary still hashes to
`6aa7357d2f64202584b14b0a14f8fb183379faf5907723cd24bd838b9be14a9a`;
it was hashed only. No build or dependency change occurred.

## Pilot coverage and exclusions

Independent set checks confirm **220 distinct unlaunched rows**: ten selected
inputs plus twelve controlled configurations, profiles none/balanced,
method xag_bennett, five slots each. Every response/circuit/RSS and timing field
is null. Zero compiler artifacts, compiled positive/negative checks, network
measurements or five-invocation groups are supplied by this execution batch.
Unknown measurements remain unavailable, not zero. No new selected compiler
failure, timeout or OOM was observed because no selected child ran.

Validation seeds11/23/37/53/71 are distinct from graph seed1729; there is no
native randomized compiler seed. Existing input/witness evidence is reused from
the earlier independent review, whose final audit hash remains
`bb5d62790ba2219d85611d76a0a3ea2f33e157c4cdf20fa15f89dd7f75523601`.
Eight supplied witnesses establish only existence at explicit k; DSJC125.1 and
le450_5a witnesses remain unknown, and every M remains unknown. queen8_8 uses
explicit k=11 despite historical file metadata8. No input/witness study was
repeated or historical metadata rewritten.

Planned90s child/900s cumulative/6GiB budgets are not executed-enforcement
evidence. Optimization/mapping/lowering splits remain null. Combined bridge
and enclosing observation/cleanup times overlap; wait4 can include reaped
descendants, and unavailable sampled group RSS is not zero or a hard memory cap.
The old110 tiny attempts/330 networks,145 mapping failures, B1/B2 and cleanup
failures, and overwritten-log/reconstructed-receipt limitation retain their
earlier exclusions. Old incorrect dependency fields remain excluded; corrected
gitlinks are source pins, not fresh build attestations.

## Checks and next action

Only bounded metadata/hash checks ran, using existing research Python and
explicit candidate PYTHONPATH, all numerical thread settings1. No numerical
arrays, statevectors, Operators or compiler processes were allocated. The final
audit passed in0.434664167 seconds with22,609,920 bytes Darwin self high-water
RSS. It uses streaming1MiB hashes, JSON reads below2MiB, a60s internal alarm,
10s Git timeouts and a256MiB terminal self-RSS check; no hard allocation cap or
group measurement is claimed. This is well below300s cumulative independent
checks, not a new production test suite or source correctness admission.

An initial audit incorrectly requested a Git blob for an ignored candidate dump
artifact and exited1. Its unchanged script/log are retained; the final script
hash-checks dump artifacts without treating them as tracked source. Initial
tool-reported wall was0.283756333s; RSS was not measured. This reviewer
bookkeeping failure is separate from the candidate's two retained failures.

The coordinator already queued `scaling-cancel-fix-1029205426` → independent
`scaling-cancel-review-1029205426` → `scaling-cancel-execute-1029205426` →
`scaling-cancel-evidence-review-1029205426`. Do not duplicate them or redispatch
this completed review to poll admission. Correction must retain ownership
through cleanup/final accounting, propagate cancellation afterward and preserve
denial/descendant/reused-PID safeguards. Only exact independent ADMIT permits
candidate/integrated checks and five actual repeats, prioritizing queen-family-5,
queen8_8 and planted n32, followed by separate evidence review.

This BLOCK is limited to the declared selected compiler pilot. No quantum
phase/restoration/arbitrary-target, FT/RUS, general scalability, comparative or
paper admission follows. The full tasks1–8 scope and exclusions in the29October
hard-bound handoff remain open. New128-additional-batch authority supersedes
old dispatch exhaustion, not scientific gates. Old queue/history, this branch's
earlier review, root README, archives, pins and all failed/partial evidence were
preserved. No queue change, model/subagent launch, push, sync, hardware or paid
fallback occurred. Dispatcher alone launches successors and publishes integration
HEAD. This assigned review has no remaining own work.

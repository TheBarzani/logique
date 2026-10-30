# Scaling execution decision — 29 October 2026

Task `integrate-execute-scaling-1029204240` is **COMPLETE** with scientific
**BLOCK**. This is the fresh decision on completed independent review `44ad4ba`,
not a repeat of the earlier missing-review handoff. Integration intake is
`2b34f8d65e3aa988782c6d2e7632dfb9e6e64e40`, on
`coloring-paper-revamp-codex`. Session was not supplied in the environment.
Checkpoint: `dump/1029205426-scaling-block-execution-handoff/audit.json`.

The [verbatim independent review](scaling_cleanup_review_20261029.md) BLOCKS
candidate `7145b87485eb68bd602f65a3520c46075febfba7`, including corrections
`c8ea5b3` and `8cac9b3` and their imported implementation ancestors. The review
admits **no new harness correctness/build commits**. No candidate implementation
was integrated and no research metrics were produced by this task.

The actual source confirms the blocker: `run_bounded` catches monitor exceptions
then invokes `_cleanup_owned` outside that handler. A first SIGINT during the
cleanup's initial nonblocking reap escapes before group termination, mandatory
reaping and receipt finalization. The retained actual reviewer log contains two
failures, direct native and full runner: both leaders remain running, both lack
exception receipts. The runner does preserve an interrupted manifest and a
0.04302620887756348-second fallback charge. Reviewer emergency cleanup is not
candidate cleanup. This is a new ownership failure, despite 150 focused tests
and 18 earlier independent regressions passing. Those results are reviewed saved
evidence, not tests rerun by this coordinator.

The fresh metadata audit imported the actual candidate `src`, checked all paths
in the review's bounded identity audit and all checkpoint-listed review artifacts,
checked candidate tracked files against HEAD blobs, and matched the review bytes
to `44ad4ba:SCALING_CLEANUP_REVIEW.md`. It preserved an identical report copy in
the fresh dump and in the linked tracked review. The prescribed native binary's
SHA256 remains `6aa7357d2f64202584b14b0a14f8fb183379faf5907723cd24bd838b9be14a9a`;
it was hashed only. Detailed identities and Git commands are in `audit.json`.

The audit took 0.439353083 seconds internally and used 29,540,352 bytes Darwin
self high-water RSS. It streamed hashes in 1 MiB blocks, set 10-second Git child
timeouts, checked a 256 MiB terminal self budget and a 60-second internal bound.
No external overall timeout or group memory cap is claimed. Existing research
Python, explicit candidate PYTHONPATH and numerical thread limits1 were used.
No numerical/compile job, candidate suite or integrated suite ran: the source
gate prevents their use toward admission. No new experiment timeout/OOM occurred.

There are **zero selected compiler invocations**, zero new compiler artifacts or
compiled positive/negative checks, and no new network/timing/RSS measurements.
Compiler stage times and RSS are unavailable, not zero. The original ledger hash
`d650687aa6678189904c77929bab42f43332f218373eb8f641750805bc6650cc`
was rechecked; its 220 planned attempts are retained in fresh
`remaining-ledger.json` as unexecuted. Ten prepared inputs and twelve controlled
settings, two profiles and five slots remain open. Validation seeds are
11/23/37/53/71, graph seed1729 is distinct, and no native seed exists. Eight
positive witnesses remain supplied; DSJC125.1/le450_5a witnesses and all M remain
unknown. No pending manifest or tiny compatibility repetition is a selected
five-repeat result. Full DIMACS scope remains open.

Four new jobs were appended **once**, atomically, to the authorized continuation
queue `dump/1029204240-coloring-dispatch-continuation/queue.json`:

1. `scaling-cancel-fix-1029205426`: correctness/high; fresh isolated worktree
   `dump/1029205426-scaling-block-execution-handoff/worktrees/cancellation-fix`,
   branch `codex/coloring-scaling-cancel-fix-1029205426`, initialized at7145b87.
   Own cancellation-safe cleanup/final accounting and deterministic direct/runner
   regressions. Preserve timeout, original cancellation, permission errors,
   descendants, and no signaling of reaped/reused leader PIDs.
2. `scaling-cancel-review-1029205426`: independent critical_review/high; separate
   `worktrees/cancellation-review`, branch
   `codex/coloring-scaling-cancel-review-1029205426`, initialized at2b34f8d.
   Review exact new hashes/withheld chain and reproduce original and new edges.
3. `scaling-cancel-execute-1029205426`: coordinator; only exact ADMIT permits
   candidate checks, exact correctness integration, integrated verification and
   actual prioritized five-repeat selected execution.
4. `scaling-cancel-evidence-review-1029205426`: independent evidence review;
   genuine artifacts and coverage required, otherwise explicit scientific BLOCK.

Prompts and queue before/proposed snapshots are saved in the fresh checkpoint.
The queue loader validated all 11 definitions, existing seven definitions and
headers are unchanged, and no state/history file was edited. New worktrees were
created without launching workers. The original selected-evidence task remains
unchanged and can record this BLOCK; it is not a substitute for the new chain.
The batch count was2/128 when inspected. The new run retains max128 additional
batches, deadline 2 November00:00 local, included-only Standard/model gates;
old128/128 run and all old prompts/artifacts remain immutable.

After admission, the new coordinator must prioritize queen-family-5, queen8_8,
and planted n32 under <=90s child/900s cumulative, declared<=6GiB with honest
sampled/terminal memory enforcement. Retain input/witness hashes, positive and
negative compiler Boolean coverage, actual artifacts/stats, combined bridge and
boundary time separately, unavailable stage splits null, RSS scopes, timeouts
and remaining220-row status. Correctness and metrics require separate commits
and exact independent evidence review. A Boolean compiler check does not admit
quantum phase, arbitrary-target action, restoration or full-search behavior.

The review and this new audit/handoff are the only integration changes. README,
pins, histories, archives and all failed/partial evidence are preserved. Initial
worktree creation encountered a sandbox Git-lock denial; scoped escalation
succeeded, with no automatic-review rejection. No models/subagents/Codex launches,
push, sync, paid/API fallback, hardware or excluded research occurred. Dispatcher
alone launches the saved successors and publishes committed integration HEAD.
The full tasks1–8 matrix remains in the
[hard-bound handoff](full_research_bound_handoff_20261029.md); this later scaling
decision supersedes only its missing-review status. No full-paper completion,
quantum, FT/RUS or scalability admission follows.

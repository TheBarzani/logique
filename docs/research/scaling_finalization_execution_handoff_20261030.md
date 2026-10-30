# Scaling runner-finalization execution decision — 30 October 2026

Assigned task `scaling-cancel-execute-1029205426`, session
`01a18b8b-32f6-7e82-ba58-7e4978afb2bd`, integration intake `43e0533`.
**This bounded assignment is COMPLETE with scientific BLOCK.** No candidate
source was integrated and no selected compiler experiment ran. Full DIMACS,
Task8 and all tasks1–8 remain open. This decision follows the new cancellation
review; it does not repeat the completed predecessor execution handoff.

Fresh checkpoint:
`dump/1030024336-scaling-finalization-block-handoff/`.
The authorized continuation remains
`dump/1029204240-coloring-dispatch-continuation/queue.json`, max128 additional
batches and deadline 2 November 00:00 local. The snapshot records12 batches
used. Queue completion is not scientific admission.

## Exact reviewed decision and preserved evidence

Independent review **`bfc440bf074bed13cbd2e7d77f23434450ad202b` BLOCKs** exact
candidate **`6ec31ceb6c45babd7a7e65fb176254dfa0590a7b`**, correctness
`3d792e2ca2a8f2bbe2ae81ef51a993bbd2c69c13` over `7145b87`.
Candidate:
`dump/1029205426-scaling-block-execution-handoff/worktrees/cancellation-fix`.
Reviewer and evidence:
`dump/1029205426-scaling-block-execution-handoff/worktrees/cancellation-review/`,
`dump/1030023321-scaling-cancellation-independent-review/` within that worktree.

The review bytes are copied unchanged to the fresh checkpoint as
`SCALING_CANCELLATION_REVIEW.md`, SHA256
`638b1cb2b87c70b114ad3d609529e387758483dbe9f8e5134692f6b604993770`.
They match the reviewer commit blob. Candidate clean HEAD, every recorded
candidate source identity and Git blob, retained reviewer artifact hashes,
completion/checkpoint identities, prescribed native binary hash and both saved
failure observations were independently checked. `audit.json` records exact
identities. No predecessor test or pilot was rerun.

The cleanup correction passes the original live-child cancellation cases.
The new failure is in the unchanged runner's final charge/append/save block:
first SIGINT there bypasses the earlier exception handler. Both saved real
success and timeout observations have reaped leaders, preserved original
exception identity and positive process receipts; their saved manifests remain
`running`, with zero rows and no `native_wall_seconds`. This loses accounting;
the observations do not show a live-child leak. Original logs, scripts,
response artifacts, receipts and prior failures remain untouched.

Required correction: protect the entire finalization transaction, save exactly
one current row and honest charge, preserve prior rows and actual timeout/RSS/
cleanup details, set interrupted status, restore the handler and propagate the
original exception without a later call. Persistence must remain recoverable
and valid if cancellation arrives during writing. Add success/timeout and
write-boundary regressions; never double-charge, duplicate rows, retry reaping
or swallow cancellation. Independently admit new exact source before execution.

The entire dependent source chain remains withheld: `b5cb3da`, `5a7c3da`,
`65f091f`, `b755435`, `c8ea5b3`, `8cac9b3`, `3d792e2`. Checkpoint commits
`934be18`, `f84e35e`, `7157de5`, `7145b87`, `6ec31ce` and old metrics are
records, not correctness or performance admission. Existing input/helper/timer
admissions retain their previous scope only.

## One concrete successor correction and review

No equivalent runner-finalization correction existed in the43 observed queue
definitions. Exactly two new jobs were appended atomically, **43→45**, with
all prior definitions and every header field unchanged:

| Job | Fixed profile | Isolated branch / baseline |
| --- | --- | --- |
| `scaling-finalization-fix-1030024336` | correctness | `codex/coloring-scaling-finalization-fix-1030024336`, exact6ec31ce |
| `scaling-finalization-review-1030024336` | critical_review | `codex/coloring-scaling-finalization-review-1030024336`,43e0533 |

Worktrees and concrete prompts are under the fresh checkpoint. The correction
depends on this assignment; the independent review depends on the correction
with finished-predecessor triage. Each allows at most12 attempts/1800s under
the unchanged global ceiling/deadline and included-usage gates. No model was
launched. `queue-before.json`, `state-snapshot.json` and `queue-append.json`
preserve the before/after identities and scheduling receipt. The dispatcher
alone launches these workers and publishes integration HEAD.

Only a future exact ADMIT permits coordinator candidate checks, integration of
the complete admitted correctness/build chain excluding checkpoints/old metrics,
then independent verification of integrated source. Actual selected five-repeat
execution and independent evidence review still follow separately. Prioritize
queen-family-5, queen8_8 and planted n32, <=90s child/900s cumulative, declared
<=6GiB with honest enforcement qualifications. Preserve all220 requested slots,
remaining ledger, input/witness hashes, compiler artifacts/stats, Boolean
positive/negative coverage, combined bridge/boundary times, null unavailable
stage splits, RSS and timeouts. Validation seeds11/23/37/53/71 and graph1729
remain separate. Neither a pending manifest nor tiny process-control compiler
fixtures count as selected repeat evidence. No new admitted execution config,
repeat results or research-metric commit was created in this BLOCK batch.

## Resource and preservation boundary

AGENTS.md, CLAUDE.md and all740 lines of the revamp plan, both requested
research handoffs, the exact new review and candidate checkpoint were read.
Truncated combined reads were followed by focused complete reads.
Existing root `.venv/bin/python` and explicit actual candidate `src` PYTHONPATH
were used for file/identity auditing only. One serial local command at a time;
compiler/BLAS/OMP/Accelerate/Rayon threads1. Declared256MiB working-memory
budget/60s command limit; bounded file hashing and self high-water observation
are not a hard allocation cap or simultaneous process-group memory measurement.
No quantum or selected compiler allocation occurred. Audit and append receipts
record actual elapsed time and self RSS; model-session/commit/next-action
identities are retained in the checkpoint.

The prescribed native binary still hashes to
`6aa7357d2f64202584b14b0a14f8fb183379faf5907723cd24bd838b9be14a9a`;
it was neither invoked nor rebuilt. README, pins, archives, histories, candidate
sources and all failure evidence are preserved. No sync, subagent, model/Codex
subprocess, API/paid fallback, purchase, hardware, physicalQEC, precolored or
conditional-workspace work, or push occurred. Only this dated handoff is owned
as tracked source in the BLOCK batch. No scientific table, quantum/FT/RUS,
scalability, comparative-superiority or full-paper approval follows.

**Next action:** dispatcher runs the new runner-finalization correction, then
independent exact-source review. A future coordinator must inspect that actual
decision before integration or selected execution. This completed assignment
must not be relaunched merely to poll the gate.

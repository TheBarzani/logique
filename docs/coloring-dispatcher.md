# Automatic coloring-revision dispatcher

`tools/coloring_dispatcher.py` is a standard-library process that checks live
included usage and serializes bounded `codex exec`/resume jobs. It runs inside
the existing `coloring-paper` tmux session, under `caffeinate`. The dispatcher,
rather than tmux itself, starts future model batches. Waiting consumes no model
calls. Following the user's 25 October authorization, validated task changes are
committed and integrated on `coloring-paper-revamp-codex`, then pushed to
`origin/coloring-paper-revamp-codex`. It does not submit hardware or alter
dependency pins.

The initial queue is
`dump/1025021922-coloring-auto-dispatch/queue.json`. It resumes rotation repair,
requests independent Astra re-review, then runs an integration coordinator.
Scientific approval is separate from task completion: the coordinator must
verify the reviewed file hashes and review decision before admitting FT work.
It can append further bounded tasks from the full research plan. The queue is
limited to 64 tasks/128 batches and stops at the end of 1 November 2026, recording
unfinished work. A stopped/blocked queue is not overall research completion.

## Controls

Run from the integration checkout:

```bash
.venv/bin/python tools/coloring_dispatcher.py status \
  --queue dump/1025021922-coloring-auto-dispatch/queue.json

.venv/bin/python tools/coloring_dispatcher.py pause \
  --queue dump/1025021922-coloring-auto-dispatch/queue.json

.venv/bin/python tools/coloring_dispatcher.py unpause \
  --queue dump/1025021922-coloring-auto-dispatch/queue.json
```

Pause creates a `PAUSE` marker. It prevents launches and interrupts an owned
active model at the next monitor check. Unpause removes it; the ordinary loop
then resumes when live permission is available. Stop the watcher itself by
sending Ctrl-C to the `dispatcher` tmux window. Do not kill the entire tmux
session, which may contain independent numerical jobs or the interactive CLI.

`state.json` records usage windows, task states, session IDs, model/effort,
worktrees, attempts and outcomes. `attempts/` contains each batch's JSONL events,
stderr and structured result. The initial research checkpoint links to this
state file. Authentication responses, email and credentials are not saved.

## Usage and execution contract

- Authenticate as ChatGPT Plus. API-key environment overrides are removed and
  `forced_login_method="chatgpt"` is passed explicitly. Requested model IDs are
  checked before dispatch; unavailable models block rather than substitute.
- Every job explicitly selects Standard speed (`service_tier="default"`) and
  the plan's model/effort profile. Max/Ultra and recursive model delegation are
  excluded. The coordinator is `gpt-6.1-sol` at medium effort.
- Require positive live `ordinaryUsageAllowed`, known unexhausted five-hour and
  weekly windows, and applicable advertised model limits. A reset timestamp or
  a positive percentage alone is never permission. There is no reserved margin.
- Check idle usage every 60 seconds and active usage every 15 seconds. Unknown
  metadata or exhaustion interrupts owned work, preserving its session for the
  next available window. Numerical jobs launched independently in tmux remain
  independent of these model pauses.
- The user confirmed credit continuation and automatic purchases are disabled,
  and attributed observed balance changes to another session. Global credit
  balance movement therefore does not gate this queue. These account billing
  settings are user-confirmed: the metadata API does not expose or set them.
  A client poller cannot provide a transactional account-wide spending cap;
  disabled backend continuation is still required, particularly when another
  session exhausts shared usage between checks. There is no API/paid fallback.
- Free resets are authorized only at weekly exhaustion. Select the earliest
  unexpired advertised reset, save an idempotency key before consuming, and
  re-read usage rather than infer recovery. Never redeem one merely because the
  five-hour window is exhausted. No credit-purchase or notification API exists
  in this tool.

The underlying read/resume interfaces are documented in the official
[Codex App Server reference](https://learn.chatgpt.com/docs/app-server) and
[CLI reference](https://learn.chatgpt.com/docs/cli/reference). Local CLI 0.164.0
was checked, including resume argument parsing without inference.

## Isolation and recovery

A repository-wide lock under `.cache/` prevents duplicate dispatchers. Only one
queue model process runs at a time; ordinary local CLI `exec`/review workers
also block a new launch. An active interactive coordinator plus one dispatcher
worker is the normal two-model maximum. Activity on other machines/ChatGPT
surfaces cannot be enumerated by this local process and shares account limits.

Workers own separate worktrees of this exact repository, with checked branch
names and no branch reset/switch. The integration coordinator alone uses the
integration checkout. Each CLI runs without the shared daemon so its process
group is owned and can be interrupted. A bounded batch returns `complete`,
`continue` or `blocked`; this describes its task, not manuscript approval.

Only append new task IDs to `queue.json`, using atomic file replacement. Queue
headers and existing job definitions are immutable once observed. Dependencies
normally require completed tasks. Only reviewers/coordinators may use
`dependency_policy="finished"` to triage a completed or blocked predecessor.
Model profiles are fixed in the script to match the plan. A worker must never
launch another model itself; the coordinator appends work for the dispatcher.

SIGINT/SIGTERM requests a checkpointed interruption. If the process crashes or
the server reboots during launch/work, the durable state becomes `ambiguous`
on restart and is not automatically relaunched. Inspect the recorded session,
worktree and attempt logs, establish that the old worker has ended, then recover
that task deliberately. This prevents duplicate in-flight sessions. tmux does
not survive reboot; restart the watcher with its saved queue and environment:

```bash
.venv/bin/python tools/coloring_dispatcher.py run \
  --queue dump/1025021922-coloring-auto-dispatch/queue.json \
  --codex /Users/mar/.local/bin/codex
```

Restore the research tool PATH, `LOGIQUE_NATIVE_EXECUTABLE` and `LOGIQUE_CACHE`
when restarting. The saved `start-dispatcher.py` beside the queue provides that
environment and is the command used in the tmux window. No launchd service, automatic purchase or extra credit provisioning is installed.
Polling is ordinary metadata I/O, with no model calls.
Tests use fake CLI processes/metadata and do not spend inference calls.

## Commits and remote synchronization

The user-authorized `publication.json` beside the queue enables publication
without changing immutable existing task definitions. It specifies `enabled`,
`branch` (`coloring-paper-revamp-codex`), `remote` (`origin`), and the expected
`remote_url`. Removing this file disables publication. Workers receive the latest
authorization on every new or resumed batch, overriding historical no-push text.
They commit validated task-owned files explicitly; the coordinator integrates
reviewed changes and commits on the integration branch. Existing user README
edits are excluded. The dispatcher never stages files automatically.

The dispatcher pushes committed integration HEAD using an explicit branch
refspec, independently of model quota. Worker branches are never pushed.
Successful pushes are checkpointed under `state.json` → `publication`; unchanged
HEADs do not cause repeated network calls. A changed remote URL, wrong branch,
authentication failure, timeout or rejected push records `publication_error`
and retries on the ordinary polling interval; local research continues. There is no force push, automatic
pull/merge/reset, or automatic inclusion of uncommitted work. Git rejects remote
divergence. An operator pause also pauses publication. Already committed history
is synchronized when publication is first enabled.

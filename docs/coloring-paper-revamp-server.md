# Continue this conversation on the home MacBook

The full plan is in [coloring-paper-revamp-codex-plan.md](coloring-paper-revamp-codex-plan.md).
The initial server instruction is [coloring-paper-revamp-start.txt](coloring-paper-revamp-start.txt).
Only these handoff documents were added; no research implementation or server job
was started by preparing this handoff.

The source session ID is `01a156b2-ea71-7222-aca2-2a6276244f86`. Its transcript is
stored locally, so signing into the same account is not sufficient to put it on
another machine. A copied transcript was successfully discovered by Codex CLI
0.163.0 in an otherwise empty temporary Codex session store. This verified local
discovery without copying credentials or starting a model turn; it did not test
your server or guarantee cross-version migration. A fresh-session fallback below
uses the complete saved plan if resumption is incompatible.

## 1. Copy from the laptop after this reply finishes

Finish any other edits in this checkout before copying. These commands create a
**fresh** server directory and intentionally fail if it already exists. Do not
repeat the copy over a server checkout after server work has started.

Run on the current laptop, not inside SSH:

```bash
(
  set -e
  ssh mar@ssh.mergasori.com 'umask 077; mkdir -p ~/codex-work ~/.codex/sessions/2026/10/19 && mkdir ~/codex-work/logique'

  rsync -az --progress \
    --include='.env.example' \
    --exclude='.env' --exclude='.env.*' \
    --exclude='.venv/' --exclude='venv/' --exclude='env/' \
    --exclude='.cache/' --exclude='/dump/' \
    --exclude='build/' --exclude='dist/' --exclude='node_modules/' \
    --exclude='__pycache__/' --exclude='*.pyc' \
    --exclude='.pytest_cache/' --exclude='.mypy_cache/' --exclude='.ruff_cache/' \
    --exclude='.DS_Store' \
    /Users/mac/PhD/logique/ \
    mar@ssh.mergasori.com:codex-work/logique/

  scp \
    /Users/mac/.codex/sessions/2026/10/19/rollout-2026-10-19T20-25-31-01a156b2-ea71-7222-aca2-2a6276244f86.jsonl \
    mar@ssh.mergasori.com:.codex/sessions/2026/10/19/
)
```

This includes the main `.git` directory, local unpublished commits, submodule
sources/metadata, current uncommitted work, the nested manuscript/research
repositories and the new plan. It excludes the local `.env`, disposable builds,
environments and old generated runs. The transcript is copied separately; do not
copy all of `~/.codex` or its authentication cache. No GitHub push is needed.

The previous automated SSH attempt failed with `Permission denied (publickey)`.
If this also occurs in your terminal, unlock/load your configured key or fix SSH
access before retrying. Port 5900 forwarding is unnecessary for these commands.

## 2. Install and log in on the server

```bash
ssh mar@ssh.mergasori.com
```

Run the following **inside SSH**. The `brew` command assumes Homebrew is already
installed; skip installation of a tool that is already present and current.

```bash
brew install tmux
curl -fsSL https://chatgpt.com/codex/install.sh | sh
export PATH="$HOME/.local/bin:$PATH"
codex --version
codex login --device-auth
codex login status
```

Open the displayed authentication URL on your laptop and sign in to your Plus
account. Enable device-code login in ChatGPT security settings if prompted.
`codex login status` must report ChatGPT authentication. Do not supply an API key.
These are the [official installation](https://learn.chatgpt.com/docs/cli) and
[headless authentication](https://learn.chatgpt.com/docs/auth) workflows.

Use the same or a newer CLI than the source version, 0.163.0. If device-code
authentication is unavailable, the authentication documentation also describes
an SSH tunnel for the browser callback on port 1455.

## 3. Enter tmux, create the branch and resume

```bash
tmux new-session -s coloring-paper -c "$HOME/codex-work/logique"
```

In the new tmux terminal:

```bash
export PATH="$HOME/.local/bin:$PATH"
cd "$HOME/codex-work/logique"
caffeinate -is &
git status --short --branch
git switch -c coloring-paper-revamp-codex

codex resume 01a156b2-ea71-7222-aca2-2a6276244f86 \
  --cd "$HOME/codex-work/logique" \
  --model gpt-6.1-sol \
  -c 'model_reasoning_effort="medium"' \
  -c 'forced_login_method="chatgpt"' \
  --approve-for-me \
  "$(cat docs/coloring-paper-revamp-start.txt)"
```

If the desired branch already exists, inspect it and use `git switch
coloring-paper-revamp-codex`; never use `git switch -C` to overwrite it. The fresh
copy currently has no branch by that name. Existing dirty files travel with the
branch switch and must be preserved.

The explicit `--cd` replaces the laptop's old path when resuming; the prompt
loads the full plan and requests implementation. `--approve-for-me` uses automatic
approval review with workspace-write rather than disabling safeguards. Commands
that need more access may still require attention. See the
[CLI reference](https://learn.chatgpt.com/docs/cli/reference).

Before unattended work, confirm Standard speed and the account's included-usage
and credit settings. Forcing ChatGPT authentication prevents switching to API
authentication; it is not a purchased-credit spending cap. Keep the server
plugged in with its lid open. The `caffeinate` process runs inside tmux and keeps
the Mac awake while the session remains alive; it does not survive a reboot or
override closing the lid.

If the copied session cannot be resumed, start a new session with the same plan:

```bash
codex --cd "$HOME/codex-work/logique" \
  --model gpt-6.1-sol \
  -c 'model_reasoning_effort="medium"' \
  -c 'forced_login_method="chatgpt"' \
  --approve-for-me \
  "$(cat docs/coloring-paper-revamp-start.txt)"
```

This fallback has the complete scientific specification and current decisions,
but is a new conversation. Record its new ID for future resumption.

## 4. Disconnect and return

Detach without stopping Codex: press **Ctrl-b**, release, then **d**. You may then
close SSH. To reconnect from your laptop:

```bash
ssh -t mar@ssh.mergasori.com 'tmux attach-session -t coloring-paper'
```

If Codex exits, run `codex resume` with the same explicit session ID, server
directory and configuration flags. Use the new session ID if you used the
fallback. After a server reboot, recreate tmux and caffeinate first. Do not run
the copied session on both machines or copy an older transcript over the server
after it has advanced.

If quota is exhausted, resume after the reported reset and ask Codex to continue
from its saved checkpoint. `tmux` keeps running processes alive across SSH
disconnects; it does not automatically schedule another model turn, recover from
a reboot, or guarantee the one-week research schedule. The plan allows a minimal
queue if automatic resumption is needed later.

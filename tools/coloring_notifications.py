"""Deliver researcher-written briefings to one GitHub issue, without model calls."""

from __future__ import annotations

import argparse
from contextlib import contextmanager
from datetime import datetime
import fcntl
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import threading
import time


def save(path: Path, value: dict) -> None:
    """Atomically persist delivery intent or a receipt before advancing cursors."""
    temporary = path.with_suffix(".tmp")
    with temporary.open("w") as stream:
        json.dump(value, stream, indent=2)
        stream.write("\n")
        stream.flush()
        os.fsync(stream.fileno())
    temporary.replace(path)


@contextmanager
def locked(path: Path):
    """Prevent two notification senders from posting the same pending report."""
    with path.open("a+") as stream:
        fcntl.flock(stream, fcntl.LOCK_EX | fcntl.LOCK_NB)
        yield


def local_time(value) -> str:
    """Format optional saved timestamps, never infer live allowance."""
    return (
        datetime.fromtimestamp(value).astimezone().strftime("%b %d %H:%M %Z")
        if isinstance(value, (int, float))
        else "unknown"
    )


def read_context(pointer: Path) -> tuple[Path, dict]:
    """Follow the canonical active run without touching dispatcher state."""
    queue = Path(json.loads(pointer.read_text())["queue"]).resolve()
    return queue, json.loads(queue.with_name("state.json").read_text())


def research_reports(queue: Path) -> list[dict]:
    """Accept only complete CLI turns with a separately authored Markdown brief."""
    reports = []
    for brief in sorted(queue.parent.glob("attempts/*/research-brief.md")):
        result = brief.with_name("result.json")
        events = brief.with_name("events.jsonl")
        if not result.exists() or not events.exists():
            continue
        try:
            outcome = json.loads(result.read_text()).get("outcome")
            if outcome not in ("complete", "continue", "blocked"):
                continue
            with events.open("rb") as stream:
                stream.seek(max(0, events.stat().st_size - 65536))
                tail = stream.read(65536).decode(errors="replace")
            finished = any(
                json.loads(line).get("type") == "turn.completed"
                for line in tail.splitlines()
                if line.startswith("{")
            )
            if not finished:
                continue
            content = brief.read_text()
            if not 80 <= len(content) <= 18000:
                continue
            metadata_path = brief.with_name("research-brief.meta.json")
            metadata = (
                json.loads(metadata_path.read_text()) if metadata_path.exists() else {}
            )
            identity = hashlib.sha256(
                (str(brief) + "\n" + content).encode()
            ).hexdigest()
            reports.append(
                {
                    "id": identity,
                    "body": content,
                    "source": str(brief),
                    "written_at": brief.stat().st_mtime,
                    "important": metadata.get("priority") == "important",
                }
            )
        except (OSError, ValueError, TypeError):
            continue
    return sorted(reports, key=lambda row: row["written_at"])


def operational_event(state: dict, now: float) -> tuple[str, str] | None:
    """Describe material pauses/stops without presenting them as research results."""
    phase = state.get("phase", "unknown")
    usage = state.get("usage") or {}
    if (
        phase not in ("deadline_reached", "batch_limit_reached", "stopped")
        and now - state.get("updated_at", now) > 240
    ):
        return (
            "stale",
            "The research dispatcher has not refreshed its checkpoint for more than four minutes. Its last saved state may be stale; no new scientific conclusion is implied. The sender is still monitoring it, and the saved research work is retained.",
        )
    if (
        phase in ("waiting", "waiting_for_included_quota")
        and state.get("reason") == "included_quota_exhausted"
    ):
        primary = usage.get("primary") or {}
        weekly = usage.get("secondary") or {}
        reset = (
            primary.get("resetsAt")
            if primary.get("usedPercent") == 100
            else weekly.get("resetsAt")
        )
        return (
            f"quota:{reset}",
            f"Research model work is paused because the included allowance is exhausted. The last account check was {local_time(usage.get('checked_at'))}; the applicable reset is recorded as {local_time(reset)}. Saved results remain intact. The dispatcher will resume only after the backend confirms included usage is available; a reset time alone is not permission. No paid continuation is used.",
        )
    messages = {
        "deadline_reached": "The scheduled research deadline has been reached. Model dispatch has stopped and unfinished research must remain explicit. The latest research briefings below describe what the evidence supports; this stop does not mean the manuscript is finished.",
        "batch_limit_reached": "This bounded research run has reached its model-batch ceiling and stopped. Its results and remaining work are checkpointed. Further model dispatch needs another authorized bounded continuation; the manuscript is not automatically complete.",
        "queue_idle": "There is no ready research assignment in the current queue. This can reflect completed handoffs or blocked dependencies; it is not a declaration that the research or manuscript is finished.",
        "operator_paused": "The research dispatcher has been manually paused. Existing results are saved; no scientific conclusion follows from this operational pause.",
        "stopped": "The research dispatcher has stopped. Its latest checkpoint and research briefings remain available, and no manuscript-completion claim is inferred.",
    }
    if phase.startswith("blocked"):
        return (
            phase,
            "The dispatcher encountered an execution/configuration block and is not launching further work. Its checkpoint is preserved. This is an operational issue, separate from the independent scientific review decisions described in the research briefings.",
        )
    if phase in messages:
        return (phase, messages[phase])
    blocked = sorted(
        k
        for k, value in state.get("jobs", {}).items()
        if value.get("status") in ("blocked", "ambiguous")
    )
    if blocked:
        key = hashlib.sha256(json.dumps(blocked).encode()).hexdigest()
        return (
            f"blocked:{key}",
            "Some research assignments need intervention after a failed or interrupted execution. Other eligible work can continue. A failed assignment is not automatically a scientific rejection; the accompanying researcher briefing explains any actual review decision.",
        )
    return None


class GitHub:
    """Use existing gh authentication; never read, print or store its credential."""

    def __init__(self, config: dict):
        self.gh = config.get("gh", "/opt/homebrew/bin/gh")
        self.repository = config["repository"]
        self.issue = config["issue"]
        if (
            not re.fullmatch(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+", self.repository)
            or type(self.issue) is not int
            or self.issue < 1
        ):
            raise ValueError("Require an explicit OWNER/REPO and positive issue number")
        self.endpoint = f"repos/{self.repository}/issues/{self.issue}/comments"

    def api(self, *args: str, payload: Path | None = None):
        command = [self.gh, "api", *args]
        if payload:
            command += ["--input", str(payload)]
        response = subprocess.run(
            command,
            text=True,
            capture_output=True,
            timeout=45,
            check=True,
            env={**os.environ, "GH_PROMPT_DISABLED": "1"},
        )
        return json.loads(response.stdout)

    def find(self, marker: str):
        pages = self.api(self.endpoint + "?per_page=100", "--paginate", "--slurp")
        for page in pages:
            for comment in page:
                if marker in comment.get("body", ""):
                    return comment
        return None

    def post(self, payload: Path):
        return self.api("--method", "POST", self.endpoint, payload=payload)

    def verify(self, comment: dict, body: str) -> None:
        saved = self.api(f"repos/{self.repository}/issues/comments/{comment['id']}")
        if saved.get("body") != body:
            raise RuntimeError("Posted briefing read-back mismatch")


class Notifier:
    """Durable outbox, bounded cadence, and retry reconciliation after timeouts."""

    def __init__(self, config_path: Path, remote=None):
        self.config_path = config_path.resolve()
        self.config = json.loads(config_path.read_text())
        self.directory = self.config_path.parent
        self.path = self.directory / "notification-state.json"
        self.state = (
            json.loads(self.path.read_text())
            if self.path.exists()
            else {"sent_reports": [], "sent_events": [], "receipts": []}
        )
        self.remote = remote or GitHub(self.config)
        self.stop = threading.Event()
        interval = self.config.get("interval_seconds", 43200)
        if type(interval) is not int or not 300 <= interval <= 86400:
            raise ValueError("Digest interval must be 300..86400 seconds")

    def persist(self):
        save(self.path, self.state)

    def deliver_pending(self) -> None:
        pending = self.state["pending"]
        marker = pending["marker"]
        body = pending["body"]
        # Always reconcile first. A timeout may mean GitHub already accepted it.
        comment = self.remote.find(marker)
        if comment is None:
            payload = self.directory / "pending-payload.json"
            save(payload, {"body": body})
            comment = self.remote.post(payload)
        self.remote.verify(comment, body)
        self.state["sent_reports"] = sorted(
            set(self.state["sent_reports"]) | set(pending["reports"])
        )
        if pending.get("event"):
            self.state["sent_events"].append(pending["event"])
        self.state["receipts"].append(
            {
                "sent_at": time.time(),
                "url": comment["html_url"],
                "marker": marker,
                "reports": pending["reports"],
                "event": pending.get("event"),
            }
        )
        self.state["last_sent_at"] = time.time()
        if pending.get("event"):
            self.state["last_alert_at"] = time.time()
        self.state.pop("pending")
        self.state.pop("last_error", None)
        self.persist()

    def tick(self, *, now: float | None = None) -> str:
        now = time.time() if now is None else now
        if (self.directory / "PAUSE").exists():
            return "paused"
        if self.state.get("pending"):
            self.deliver_pending()
            return "sent_reconciled"
        queue, dispatcher = read_context(Path(self.config["active_pointer"]))
        reports = research_reports(queue)
        seed = self.config.get("initial_brief")
        if seed and Path(seed).exists():
            body = Path(seed).read_text()
            reports.insert(
                0,
                {
                    "id": hashlib.sha256(("initial\n" + body).encode()).hexdigest(),
                    "body": body,
                    "source": seed,
                    "written_at": Path(seed).stat().st_mtime,
                },
            )
        reports = [r for r in reports if r["id"] not in self.state["sent_reports"]]
        event = operational_event(dispatcher, now)
        if event:
            event = (str(queue) + ":" + event[0], event[1])
            if (
                event[0] in self.state["sent_events"]
                or now - self.state.get("last_alert_at", 0) < 900
            ):
                event = None
        urgent = [r for r in reports if r.get("important")]
        if urgent and event is None and now - self.state.get("last_alert_at", 0) >= 900:
            event = (
                "research:" + urgent[0]["id"],
                "The researcher has flagged a material review decision or a finding that could change the manuscript's conclusions. The briefing above explains the evidence and its limits.",
            )
        due = now - self.state.get("last_sent_at", 0) >= self.config.get(
            "interval_seconds", 43200
        )
        if not event and (not due or not reports):
            return "waiting_for_new_brief"
        chosen = reports[:3] if (due or event) else []
        if urgent and event and urgent[0] not in chosen:
            chosen = sorted(chosen[:2] + [urgent[0]], key=lambda row: row["written_at"])
        sections = [f"## Research briefing — {local_time(now)}"]
        sections += [r["body"].strip() for r in chosen]
        if event:
            sections += ["### Progress affecting the next results", event[1]]
        if not chosen:
            sections += [
                "There is no new researcher-written result briefing since the previous delivery. Scientific findings and their qualifications remain as last reported."
            ]
        body = "\n\n".join(sections)
        identity = hashlib.sha256(
            json.dumps(
                {
                    "reports": [r["id"] for r in chosen],
                    "event": event[0] if event else None,
                },
                sort_keys=True,
            ).encode()
        ).hexdigest()
        marker = f"<!-- logique-research-brief:{identity} -->"
        body += "\n\n" + marker
        self.state["pending"] = {
            "marker": marker,
            "body": body,
            "reports": [r["id"] for r in chosen],
            "event": event[0] if event else None,
            "created_at": now,
        }
        self.persist()
        self.deliver_pending()
        return "sent"

    def run(self, *, once=False):
        with locked(self.directory / "sender.lock"):
            while not self.stop.is_set():
                try:
                    outcome = self.tick()
                    self.state.pop("last_error", None)
                    self.state["last_check_at"] = time.time()
                    self.state["last_check_result"] = outcome
                    self.persist()
                except (
                    OSError,
                    ValueError,
                    KeyError,
                    TypeError,
                    RuntimeError,
                    subprocess.SubprocessError,
                ) as error:
                    # Do not copy subprocess stderr/auth data into logs or notifications.
                    self.state["last_error"] = {
                        "type": type(error).__name__,
                        "at": time.time(),
                    }
                    self.persist()
                if once:
                    break
                self.stop.wait(60)


def main() -> int:
    """Run or inspect the read-only research-report delivery process."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=("run", "status", "pause", "unpause"))
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--once", action="store_true")
    args = parser.parse_args()
    directory = args.config.resolve().parent
    if args.action == "status":
        print((directory / "notification-state.json").read_text())
    elif args.action in ("pause", "unpause"):
        path = directory / "PAUSE"
        path.touch() if args.action == "pause" else path.unlink(missing_ok=True)
    else:
        import signal

        notifier = Notifier(args.config)
        for sig in (signal.SIGINT, signal.SIGTERM):
            signal.signal(sig, lambda *_: notifier.stop.set())
        notifier.run(once=args.once)
        return int(bool(notifier.state.get("last_error")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

"""Read-only terminal dashboard for the coloring dispatcher; no network/model calls."""

from __future__ import annotations

import argparse
from collections import Counter
from datetime import datetime
import json
from pathlib import Path
import shutil
import sys
import time


def clean(value: object) -> str:
    """Keep checkpoint text on one line without terminal control sequences."""
    return " ".join("".join(c for c in str(value) if c.isprintable()).split())


def local_time(value: object) -> str:
    """Format an optional Unix timestamp using the server's local timezone."""
    try:
        return (
            datetime.fromtimestamp(float(value))
            .astimezone()
            .strftime("%b %d %H:%M:%S %Z")
        )
    except (ValueError, TypeError, OverflowError, OSError):
        return "unknown"


def duration(seconds: float) -> str:
    """Format a countdown without implying that quota permission is guaranteed."""
    seconds = max(0, int(seconds))
    hours, remainder = divmod(seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    return f"{hours}h {minutes:02d}m {seconds:02d}s"


def render(queue: Path, *, now: float, width: int, height: int) -> str:
    """Render saved state; missing/stale data is visible rather than inferred live."""
    lines = ["COLORING PAPER | DISPATCHER", f"Server time: {local_time(now)}"]
    try:
        config = json.loads(queue.read_text())
        state = json.loads((queue.parent / "state.json").read_text())
    except (OSError, ValueError) as error:
        lines += [f"Checkpoint unavailable: {type(error).__name__}", str(queue)]
    else:
        age = max(0, now - state.get("updated_at", 0))
        stale = age > max(180, config.get("poll_seconds", 60) * 3)
        phase = clean(state.get("phase", "unknown"))
        if (queue.parent / "PAUSE").exists():
            phase += " | OPERATOR PAUSE SET"
        lines += [
            f"State: {phase}" + (" | STALE CHECKPOINT" if stale else ""),
            f"Heartbeat: {local_time(state.get('updated_at'))} ({duration(age)} ago)"
            f" | PID {state.get('pid', '?')}",
        ]
        if phase.startswith("waiting") or phase.startswith("blocked"):
            lines.append(f"Reason: {clean(state.get('reason', 'not recorded'))}")
        usage = state.get("usage") or {}
        lines.append(
            f"Included permission (last poll): {usage.get('ordinary_allowed', 'unknown')}"
            f" | usage checked {local_time(usage.get('checked_at'))}"
        )
        for label, key in [("5-hour", "primary"), ("Weekly", "secondary")]:
            window = usage.get(key) or {}
            used = window.get("usedPercent")
            bar = "?" * 20
            if isinstance(used, (float, int)):
                filled = round(min(100, max(0, used)) / 5)
                bar = "#" * filled + "-" * (20 - filled)
            reset = window.get("resetsAt")
            countdown = (
                duration(reset - now) if isinstance(reset, (int, float)) else "?"
            )
            lines.append(
                f"{label:6} [{bar}] {used if used is not None else '?'}% USED"
                f" | reset {local_time(reset)} (in {countdown})"
            )
        lines.append(
            "Free weekly resets available: "
            f"{(usage.get('reset_credits') or {}).get('availableCount', '?')}"
            " | reset time alone does not authorize dispatch"
        )
        jobs = config.get("jobs", [])
        records = state.get("jobs", {})
        counts = Counter(
            records.get(j["id"], {}).get("status", "pending") for j in jobs
        )
        lines += [
            "",
            f"Queue: {len(jobs)} tasks | "
            + " | ".join(
                f"{key}: {counts[key]}"
                for key in (
                    "complete",
                    "running",
                    "launching",
                    "pending",
                    "blocked",
                    "ambiguous",
                )
            ),
            f"Model batches: {state.get('batches', 0)}/{config.get('max_batches', '?')}"
            f" | deadline {config.get('deadline', '?')}",
        ]
        active = [
            j
            for j in jobs
            if records.get(j["id"], {}).get("status") in ("running", "launching")
        ]
        ready = []
        for job in jobs:
            record = records.get(job["id"], {})
            accepted = (
                {"complete", "blocked"}
                if job.get("dependency_policy") == "finished"
                else {"complete"}
            )
            if record.get("status", "pending") == "pending" and all(
                records.get(dep, {}).get("status") in accepted
                for dep in job.get("depends_on", [])
            ):
                ready.append(job)
        for label, selected in [
            ("ACTIVE", active),
            ("NEXT READY", ready[:1] if not active else []),
        ]:
            for job in selected:
                record = records.get(job["id"], {})
                lines += [
                    f"{label}: {job['id']} | profile {job.get('profile', '?')}",
                    f"  Model: {record.get('model', 'assigned at launch')}"
                    f" | effort {record.get('effort', '?')} | Standard"
                    f" | attempts {record.get('attempts', 0)}/{job.get('max_attempts', '?')}",
                    f"  Session: {record.get('session_id') or job.get('session_id') or 'not started'}",
                ]
                if record.get("interruption"):
                    lines.append(
                        f"  Last interruption: {clean(record['interruption'])}"
                    )
        if not active and not ready:
            lines.append("No active or ready task; inspect blocked tasks/dependencies.")
        blocked = [
            j["id"]
            for j in jobs
            if records.get(j["id"], {}).get("status") in ("blocked", "ambiguous")
        ]
        if blocked:
            lines.append("Needs attention: " + ", ".join(blocked))
        publication = state.get("publication") or {}
        lines += [
            "",
            "Remote: origin/coloring-paper-revamp-codex",
            f"Last successful push: {str(publication.get('commit', 'none'))[:12]}"
            f" | {local_time(publication.get('pushed_at'))}",
        ]
        if state.get("publication_error"):
            lines.append(
                "PUSH ERROR: " + clean(state["publication_error"].get("reason"))
            )
        completed = [
            j for j in jobs if records.get(j["id"], {}).get("status") == "complete"
        ]
        if completed:
            last = completed[-1]
            lines += [
                f"Latest completed task in queue order: {last['id']}",
                "  "
                + clean(
                    (records[last["id"]].get("result") or {}).get(
                        "summary", "No summary"
                    )
                ),
            ]
        lines += [
            "Task completion is not scientific approval or full research completion."
        ]
    footer = "Read-only | refresh 2s by default | Ctrl-C closes dashboard; dispatcher continues"
    if len(lines) >= height:
        lines = lines[: max(1, height - 2)] + ["... enlarge terminal to see more ..."]
    return "\n".join(clean(line)[: max(1, width - 1)] for line in lines + [footer])


def main() -> int:
    """Display checkpoints once or refresh in a terminal without affecting workers."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--queue", type=Path, required=True)
    parser.add_argument("--once", action="store_true")
    args = parser.parse_args()
    interactive = sys.stdout.isatty() and not args.once
    try:
        if interactive:
            print("\033[?1049h\033[?25l", end="", flush=True)
        while True:
            size = shutil.get_terminal_size((120, 40))
            screen = render(
                args.queue, now=time.time(), width=size.columns, height=size.lines
            )
            print(("\033[H\033[2J" if interactive else "") + screen, flush=True)
            if not interactive:
                break
            time.sleep(2)
    except KeyboardInterrupt:
        pass
    finally:
        if interactive:
            print("\033[?25h\033[?1049l", end="", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

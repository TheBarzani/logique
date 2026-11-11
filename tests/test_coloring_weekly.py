"""Weekly reporting checks with fake publication; never invoke model jobs."""

from datetime import datetime
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
from zoneinfo import ZoneInfo

import pytest

TOOLS = Path(__file__).resolve().parents[1] / "tools"
SPEC = importlib.util.spec_from_file_location(
    "coloring_notifications", TOOLS / "coloring_notifications.py"
)
notifications = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = notifications
SPEC.loader.exec_module(notifications)
SPEC = importlib.util.spec_from_file_location(
    "coloring_weekly", TOOLS / "coloring_weekly.py"
)
weekly = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(weekly)


@pytest.mark.parametrize(
    "now,expected",
    [
        ("2026-11-12T08:59:00-05:00", None),
        ("2026-11-12T09:00:00-05:00", "2026-11-12"),
        ("2026-11-13T10:00:00-05:00", "2026-11-12"),
        ("2026-11-19T08:59:00-05:00", "2026-11-12"),
        ("2026-11-19T09:00:00-05:00", "2026-11-19"),
    ],
)
def test_thursday_morning_and_catchup(now, expected):
    config = {"timezone": "America/Montreal", "hour": 9, "start_date": "2026-11-12"}
    due = weekly.due_date(datetime.fromisoformat(now), config)
    assert (due.date().isoformat() if due else None) == expected


def test_schedule_uses_local_civil_time_across_dst():
    config = {"timezone": "America/Montreal", "hour": 9, "start_date": "2026-01-01"}
    before = weekly.due_date(
        datetime.fromisoformat("2026-10-29T13:00:00+00:00"), config
    )
    after = weekly.due_date(datetime.fromisoformat("2026-11-05T14:00:00+00:00"), config)
    assert before.hour == after.hour == 9
    assert before.utcoffset().total_seconds() == -14400
    assert after.utcoffset().total_seconds() == -18000


def report(run, name, timestamp, finished=True):
    directory = run / "attempts" / name
    directory.mkdir(parents=True)
    brief = directory / "research-brief.md"
    brief.write_text(
        "Measured success is 95%, within the small graph scope. The independent review is still pending; larger performance claims are not established."
    )
    os.utime(brief, (timestamp, timestamp))
    (directory / "result.json").write_text(json.dumps({"outcome": "complete"}))
    (directory / "events.jsonl").write_text(
        json.dumps({"type": "turn.completed" if finished else "turn.failed"}) + "\n"
    )


def test_report_window_predecessors_and_failed_turns(tmp_path):
    old = tmp_path / "old"
    new = tmp_path / "new"
    old.mkdir()
    new.mkdir()
    (old / "state.json").write_text("{}")
    (new / "state.json").write_text(json.dumps({"previous_run": str(old)}))
    report(old, "c5-old", 100)
    report(new, "c5-current", 150)
    report(new, "c5-failed", 160, finished=False)
    report(new, "c5-boundary", 200)
    results = weekly.gather_reports(new / "queue.json", 100, 200)
    assert len(results) == 2
    assert [r["written_at"] for r in results] == [100, 150]


def test_render_preserves_review_limitations_and_escapes_tex():
    reports = [
        {
            "source": "/Users/mar/project/attempts/c5-execute/research-brief.md",
            "body": "Earlier candidate only.",
            "date_label": "Monday",
        },
        {
            "source": "/Users/mar/project/attempts/c5-review/research-brief.md",
            "body": r"Measured 95% success. Scope is limited. \input{secret} /Users/mar/private/data"
            + "\n\n<details>Full calculation: p=30/243; review BLOCK remains.</details>",
            "date_label": "Tuesday",
        },
    ]
    tex, notes = weekly.render_deck(
        {
            "start_label": "start",
            "end_label": "end",
            "phase": "waiting",
            "reports": reports,
        }
    )
    assert "Earlier candidate" not in tex
    assert "Earlier candidate" in notes
    assert r"95\%" in tex
    assert r"\input{secret}" not in tex
    assert "Scope is limited" in tex
    assert "Full calculation" in notes
    assert "/Users/mar" not in tex + notes


def test_math_is_readable_without_allowing_tex_commands():
    assert (
        weekly.tex_prose(r"Error $5\times10^{-14}$ at 95%.")
        == r"Error $5\times10^{-14}$ at 95\%."
    )
    assert r"$\input{secret}$" not in weekly.tex_prose(r"$\input{secret}$")
    assert "$^^5cinput{secret}$" not in weekly.tex_prose("$^^5cinput{secret}$")
    assert weekly.chunks("A complete sentence. Another complete sentence.", 5) == [
        "A complete sentence.",
        "Another complete sentence.",
    ]


class Remote:
    def __init__(self):
        self.deliveries = {}
        self.timeout = False

    def deliver(self, pending):
        self.deliveries[pending["key"]] = pending
        if self.timeout:
            self.timeout = False
            raise subprocess.TimeoutExpired("fake-gh", 45)
        return {"url": "https://github.com/test/research/issues/1", "assets": {}}


@pytest.fixture
def configured(tmp_path):
    config = tmp_path / "weekly-config.json"
    config.write_text(
        json.dumps(
            {
                "repository": "test/research",
                "timezone": "America/Montreal",
                "hour": 9,
                "start_date": "2026-11-12",
            }
        )
    )
    return config


def test_durable_pending_and_no_duplicate_week(configured, monkeypatch):
    remote = Remote()
    sender = weekly.Weekly(configured, remote)
    builds = []

    def build(due, key):
        builds.append(key)
        return {"key": key, "directory": str(configured.parent)}

    monkeypatch.setattr(sender, "build", build)
    remote.timeout = True
    now = datetime(2026, 11, 12, 9, tzinfo=ZoneInfo("America/Montreal"))
    with pytest.raises(subprocess.TimeoutExpired):
        sender.tick(now)
    saved = json.loads(sender.path.read_text())
    assert "pending" in saved and not saved["delivered"]
    restarted = weekly.Weekly(configured, remote)
    monkeypatch.setattr(
        restarted, "build", lambda *a: pytest.fail("rebuilt pending report")
    )
    assert restarted.tick(now) == "sent_reconciled"
    assert restarted.tick(now) == "waiting_for_thursday"
    assert len(remote.deliveries) == len(builds) == 1


def test_weekly_pause_is_independent(configured):
    sender = weekly.Weekly(configured, Remote())
    (configured.parent / "WEEKLY_PAUSE").touch()
    assert sender.tick() == "paused"
    assert not sender.state["delivered"]


def test_publish_reconciles_issue_accepted_before_timeout(tmp_path, monkeypatch):
    sender = weekly.WeeklyGitHub({"repository": "test/research"})
    for suffix in ("pdf", "md", "tex"):
        (tmp_path / f"report.{suffix}").write_text("preserved bytes")
    pending = {
        "directory": str(tmp_path),
        "assets": {p.name: weekly.digest(p) for p in tmp_path.iterdir()},
        "body": "Actual researcher findings and their limits.",
        "marker": "<!-- weekly:unique -->",
        "title": "Weekly research",
    }
    issues = []
    monkeypatch.setattr(sender, "release", lambda path: {"id": 1})
    monkeypatch.setattr(sender, "asset", lambda r, p: "https://example.com/" + p.name)
    monkeypatch.setattr(sender, "find_issue", lambda marker: next(iter(issues), None))

    def api(*args, payload=None):
        if payload:
            data = json.loads(payload.read_text())
            issues.append(
                {
                    **data,
                    "number": 1,
                    "html_url": "https://github.com/test/research/issues/1",
                }
            )
            raise subprocess.TimeoutExpired("fake-gh", 45)
        return issues[0]

    monkeypatch.setattr(sender, "api", api)
    with pytest.raises(subprocess.TimeoutExpired):
        sender.deliver(pending)
    assert sender.deliver(pending)["url"].endswith("/issues/1")
    assert len(issues) == 1

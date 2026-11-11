"""Verify scheduling and delivery recovery without network, credentials or models."""

import importlib.util
import json
from pathlib import Path
import subprocess
import time

import pytest

SPEC = importlib.util.spec_from_file_location(
    "notifier", Path(__file__).resolve().parents[1] / "tools/coloring_notifications.py"
)
n = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(n)


class Remote:
    def __init__(self):
        self.comments = []
        self.posts = 0
        self.timeout = False
        self.mismatch = False

    def find(self, marker):
        return next((c for c in self.comments if marker in c["body"]), None)

    def post(self, payload):
        self.posts += 1
        c = {
            "id": self.posts,
            "html_url": f"https://github.com/test/research/issues/1#issuecomment-{self.posts}",
            "body": json.loads(payload.read_text())["body"],
        }
        self.comments.append(c)
        if self.timeout:
            raise subprocess.TimeoutExpired("gh", 45)
        return c

    def verify(self, comment, body):
        if self.mismatch or comment["body"] != body:
            raise RuntimeError("read-back mismatch")


@pytest.fixture
def configured(tmp_path):
    run = tmp_path / "run"
    run.mkdir()
    queue = run / "queue.json"
    queue.write_text("{}")
    state = {"phase": "worker_running", "updated_at": time.time(), "jobs": {}}
    (run / "state.json").write_text(json.dumps(state))
    pointer = tmp_path / "active.json"
    pointer.write_text(json.dumps({"queue": str(queue)}))
    seed = tmp_path / "initial.md"
    seed.write_text(
        "We independently checked the numerical result. The experiment supports a bounded conclusion, with larger cases still open."
    )
    config = tmp_path / "config.json"
    config.write_text(
        json.dumps(
            {
                "repository": "test/research",
                "issue": 1,
                "active_pointer": str(pointer),
                "initial_brief": str(seed),
                "interval_seconds": 14400,
            }
        )
    )
    return config, run


def completed_report(run, name="experiment", outcome="complete", finished=True):
    p = run / "attempts" / name
    p.mkdir(parents=True)
    (p / "research-brief.md").write_text(
        "The preparation changes the initial marked fraction. Our numerical calculation agrees with the analytical prediction; broader advantages remain unproven."
    )
    (p / "result.json").write_text(json.dumps({"outcome": outcome}))
    (p / "events.jsonl").write_text(
        json.dumps({"type": "turn.completed" if finished else "turn.failed"}) + "\n"
    )
    return p


def test_posts_authored_brief_then_waits_without_repeating(configured):
    config, run = configured
    remote = Remote()
    sender = n.Notifier(config, remote)
    assert sender.tick() == "sent"
    assert "We independently checked" in remote.comments[0]["body"]
    assert sender.tick() == "waiting_for_new_brief"
    assert remote.posts == 1
    assert sender.state["receipts"][0]["url"].startswith("https://github.com/")


def test_accepted_but_timed_out_post_reconciles_without_duplicate(configured):
    config, _ = configured
    remote = Remote()
    remote.timeout = True
    sender = n.Notifier(config, remote)
    with pytest.raises(subprocess.TimeoutExpired):
        sender.tick()
    assert sender.state.get("pending") and not sender.state["sent_reports"]
    restarted = n.Notifier(config, remote)
    assert restarted.tick() == "sent_reconciled"
    assert remote.posts == 1 and restarted.state["sent_reports"]


def test_read_back_mismatch_never_advances_cursor(configured):
    config, _ = configured
    remote = Remote()
    remote.mismatch = True
    sender = n.Notifier(config, remote)
    with pytest.raises(RuntimeError):
        sender.tick()
    assert not sender.state["sent_reports"] and sender.state["pending"]


def test_only_successfully_finished_cli_reports_are_eligible(configured):
    _, run = configured
    completed_report(run, "failed", finished=False)
    completed_report(run, "good")
    completed_report(run, "invalid", outcome="unknown")
    reports = n.research_reports(run / "queue.json")
    assert len(reports) == 1 and "/good/" in reports[0]["source"]


@pytest.mark.parametrize("interval", [14400, 43200])
def test_digest_cadence_and_pointer_following(configured, interval):
    config, run = configured
    settings = json.loads(config.read_text())
    settings["interval_seconds"] = interval
    config.write_text(json.dumps(settings))
    remote = Remote()
    sender = n.Notifier(config, remote)
    sender.tick()
    completed_report(run)
    last = sender.state["last_sent_at"]
    # A current checkpoint prevents a stale alert at the simulated future time.
    state = json.loads((run / "state.json").read_text())
    for elapsed in (100, interval - 1):
        state["updated_at"] = last + elapsed
        (run / "state.json").write_text(json.dumps(state))
        assert sender.tick(now=last + elapsed) == "waiting_for_new_brief"
    state["updated_at"] = last + interval + 1
    (run / "state.json").write_text(json.dumps(state))
    assert sender.tick(now=last + interval + 1) == "sent"
    assert remote.posts == 2 and "marked fraction" in remote.comments[-1]["body"]
    other = run.parent / "other"
    other.mkdir()
    (other / "queue.json").write_text("{}")
    pointer = Path(sender.config["active_pointer"])
    pointer.write_text(json.dumps({"queue": str(other / "queue.json")}))
    (other / "state.json").write_text(
        json.dumps({"phase": "deadline_reached", "updated_at": last, "jobs": {}})
    )
    assert sender.tick(now=last + interval + 1600) == "sent"
    assert "deadline has been reached" in remote.comments[-1]["body"]


def test_quota_alert_is_immediate_and_deduplicated(configured):
    config, run = configured
    remote = Remote()
    sender = n.Notifier(config, remote)
    sender.tick()
    now = time.time() + 1000
    state = {
        "phase": "waiting",
        "reason": "included_quota_exhausted",
        "updated_at": now,
        "usage": {
            "checked_at": now,
            "primary": {"usedPercent": 100, "resetsAt": now + 3000},
        },
    }
    (run / "state.json").write_text(json.dumps(state))
    assert sender.tick(now=now) == "sent"
    assert "included allowance is exhausted" in remote.comments[-1]["body"]
    assert sender.tick(now=now + 1) == "waiting_for_new_brief"


def test_stopped_run_does_not_become_a_spurious_stale_alert():
    event = n.operational_event(
        {"phase": "batch_limit_reached", "updated_at": 0}, time.time()
    )
    assert event[0] == "batch_limit_reached"
    event = n.operational_event(
        {"phase": "worker_running", "updated_at": 0}, time.time()
    )
    assert event[0] == "stale"


def test_pause_and_lock_are_read_only_controls(configured):
    config, run = configured
    remote = Remote()
    sender = n.Notifier(config, remote)
    (config.parent / "PAUSE").touch()
    assert sender.tick() == "paused" and not remote.posts
    lock = config.parent / "test.lock"
    with n.locked(lock):
        with pytest.raises(BlockingIOError):
            with n.locked(lock):
                pass


def test_invalid_destination_is_rejected():
    with pytest.raises(ValueError):
        n.GitHub({"repository": "https://unrelated.example/path", "issue": 1})
    with pytest.raises(ValueError):
        n.GitHub({"repository": "test/research", "issue": True})


def test_important_research_finding_arrives_before_digest_interval(configured):
    config, run = configured
    remote = Remote()
    sender = n.Notifier(config, remote)
    sender.tick()
    brief = completed_report(run)
    (brief / "research-brief.meta.json").write_text(
        json.dumps({"priority": "important"})
    )
    assert sender.tick() == "sent"
    assert remote.posts == 2
    assert "marked fraction" in remote.comments[-1]["body"]

"""Exercise the queue with fake metadata/models; never spend inference calls."""

from copy import deepcopy
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import time

import pytest

SPEC = importlib.util.spec_from_file_location(
    "coloring_dispatcher",
    Path(__file__).resolve().parents[1] / "tools/coloring_dispatcher.py",
)
dispatch = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(dispatch)

SPENDING = {
    "confirmed": True,
    "credit_continuation_disabled": True,
    "auto_purchase_disabled": True,
}


def snapshot(primary=0, weekly=0, allowed=True):
    return {
        "auth_type": "chatgpt",
        "plan": "plus",
        "account_fingerprint": "same-account",
        "ordinary_allowed": allowed,
        "primary": {"usedPercent": primary, "resetsAt": 2_000_000_000},
        "secondary": {"usedPercent": weekly, "resetsAt": 2_000_100_000},
        "limit_reached": None,
        "spend_control_reached": False,
        "reset_credits": {
            "availableCount": 2,
            "credits": [
                {"id": "later", "status": "available", "expiresAt": 2_000_200_000},
                {"id": "first", "status": "available", "expiresAt": 2_000_150_000},
            ],
        },
    }


class FakeClient:
    def __init__(self, usage=None):
        self.usage = usage or snapshot()
        self.calls = []

    def snapshot(self, **kwargs):
        return deepcopy(self.usage)

    def models(self):
        return {"gpt-6.1-sol", "gpt-6-astra", "gpt-6-luna"}

    def request(self, method, params):
        self.calls.append((method, deepcopy(params)))
        return {"outcome": "reset"}

    def close(self):
        pass


@pytest.fixture
def queue(tmp_path):
    root = tmp_path / "repository"
    root.mkdir()
    subprocess.run(
        ["git", "init", "-q", "-b", "coloring-paper-revamp-codex", str(root)],
        check=True,
    )
    subprocess.run(
        [
            "git",
            "-C",
            str(root),
            "-c",
            "user.name=Test",
            "-c",
            "user.email=test@example.invalid",
            "commit",
            "-q",
            "--allow-empty",
            "-m",
            "input",
        ],
        check=True,
    )
    worker = root / "worker"
    subprocess.run(
        [
            "git",
            "-C",
            str(root),
            "worktree",
            "add",
            "-q",
            "-b",
            "codex/coloring-test",
            str(worker),
        ],
        check=True,
    )
    directory = root / "dump" / "1025010101-dispatcher-test"
    directory.mkdir(parents=True)
    prompt = directory / "task.md"
    prompt.write_text("A bounded fake test; no inference.")
    path = directory / "queue.json"
    config = {
        "schema_version": 1,
        "repository": str(root),
        "spending": dict(SPENDING),
        "poll_seconds": 15,
        "monitor_seconds": 5,
        "max_batches": 4,
        "deadline": "2099-01-01T00:00:00+00:00",
        "allow_free_weekly_resets": True,
        "jobs": [
            {
                "id": "repair",
                "profile": "costs",
                "worktree": str(worker),
                "branch": "codex/coloring-test",
                "prompt_file": str(prompt),
                "depends_on": [],
                "max_seconds": 60,
                "max_attempts": 3,
            }
        ],
    }
    dispatch.atomic_json(path, config)
    return path


def runner(queue, usage=None):
    result = dispatch.Dispatcher(queue, "never-use-real-codex")
    result.client = FakeClient(usage)
    return result


@pytest.mark.parametrize(
    "field,value",
    [
        ("ordinary_allowed", None),
        ("ordinary_allowed", False),
        ("auth_type", "apiKey"),
        ("plan", "pro"),
        ("primary", None),
        ("secondary", {}),
        ("account_fingerprint", None),
        ("limit_reached", "rate_limit_reached"),
        ("spend_control_reached", True),
    ],
)
def test_unknown_or_incompatible_permission_fails_closed(field, value):
    usage = snapshot()
    usage[field] = value
    assert dispatch.usage_gate(usage, SPENDING) is not None


def test_no_reserve_margin_but_backend_permission_is_required():
    assert dispatch.usage_gate(snapshot(99, 99), SPENDING) is None
    assert (
        dispatch.usage_gate(snapshot(100, 40), SPENDING) == "included_quota_exhausted"
    )
    assert dispatch.usage_gate(snapshot(0, 100), SPENDING) == "included_quota_exhausted"
    assert dispatch.usage_gate(snapshot(0, 0, False), SPENDING) is not None
    assert dispatch.usage_gate(snapshot(), {}) == "spending_settings_unverified"


def test_model_specific_limit_is_checked_without_substitution():
    usage = snapshot()
    usage["model_limits"] = [
        {
            "normalModelSlug": "gpt-6-astra",
            "primary": {"usedPercent": 100},
            "secondary": None,
        }
    ]
    assert dispatch.usage_gate(usage, SPENDING, "gpt-6-astra")
    assert dispatch.usage_gate(usage, SPENDING, "gpt-6.1-sol") is None


def test_quota_exhaustion_then_live_recovery_controls_dispatch(queue, monkeypatch):
    launched = []
    d = runner(queue, snapshot(100, 36, False))
    monkeypatch.setattr(d, "launch", lambda *args: launched.append(args))
    d.run(once=True)
    assert not launched
    assert d.state["reason"] == "included_quota_exhausted"
    d.client = FakeClient(snapshot(0, 36, True))
    d.run(once=True)
    assert len(launched) == 1


def test_failed_usage_read_never_dispatches(queue, monkeypatch):
    d = runner(queue)
    monkeypatch.setattr(
        d, "observe", lambda **kwargs: (_ for _ in ()).throw(TimeoutError())
    )
    monkeypatch.setattr(
        d, "launch", lambda *args: pytest.fail("unknown quota launched")
    )
    d.run(once=True)
    assert d.state["phase"] == "waiting"


@pytest.mark.parametrize("bound", ["batches", "deadline"])
def test_deadline_and_batch_bound_stop_without_metadata_or_models(
    queue, monkeypatch, bound
):
    d = runner(queue)
    monkeypatch.setattr(
        d, "observe", lambda **kwargs: pytest.fail("bounded work queried")
    )
    if bound == "batches":
        d.state["batches"] = 4
    else:
        config = json.loads(queue.read_text())
        config["deadline"] = "2000-01-01T00:00:00+00:00"
        dispatch.atomic_json(queue, config)
    d.run(once=True)
    assert d.state["phase"] == (
        "batch_limit_reached" if bound == "batches" else "deadline_reached"
    )


def test_duplicate_dispatchers_exclude_each_other(queue):
    lock = queue.parent / "test.lock"
    with dispatch.exclusive_lock(lock):
        with pytest.raises(RuntimeError, match="Another dispatcher"):
            with dispatch.exclusive_lock(lock):
                pytest.fail("duplicate lock acquired")
    with dispatch.exclusive_lock(lock):
        pass


def test_crash_recovery_never_relaunches_ambiguous_task(queue, monkeypatch):
    d = runner(queue)
    job = dispatch.load_queue(queue)["jobs"][0]
    import hashlib

    d.state["jobs"]["repair"] = {
        "status": "running",
        "worker_pid": 1,
        "session_id": "interrupted-session",
        "definition_sha256": hashlib.sha256(
            json.dumps(job, sort_keys=True).encode()
        ).hexdigest(),
    }
    monkeypatch.setattr(d, "launch", lambda *args: pytest.fail("ambiguous relaunch"))
    d.run(once=True)
    assert d.state["jobs"]["repair"]["status"] == "ambiguous"


def test_foreign_worker_prevents_second_implementation_process(queue, monkeypatch):
    d = runner(queue)
    config = dispatch.load_queue(queue)
    monkeypatch.setattr(dispatch, "other_workers", lambda *args: 1)
    d.launch(config, config["jobs"][0], {"status": "pending"})
    assert d.state["phase"] == "waiting_for_other_local_worker"
    assert d.state["batches"] == 0


def test_pause_marker_stops_dispatch_without_changing_queue(queue, monkeypatch):
    d = runner(queue)
    before = queue.read_bytes()
    (queue.parent / "PAUSE").touch()
    monkeypatch.setattr(d, "launch", lambda *args: pytest.fail("paused launch"))
    d.run(once=True)
    assert d.state["phase"] == "operator_paused"
    assert queue.read_bytes() == before


def test_missing_model_blocks_instead_of_falling_back(queue, monkeypatch):
    d = runner(queue)
    config = dispatch.load_queue(queue)
    monkeypatch.setattr(dispatch, "other_workers", lambda *args: 0)
    monkeypatch.setattr(d.client, "models", lambda: {"gpt-6-luna"})
    record = {"status": "pending"}
    d.launch(config, config["jobs"][0], record)
    assert record["status"] == "blocked"
    assert record["reason"] == "requested_model_unavailable"
    assert d.state["batches"] == 0


def test_local_worker_counter_ignores_metadata_and_interactive_processes(monkeypatch):
    monkeypatch.setattr(
        subprocess,
        "check_output",
        lambda *args, **kwargs: (
            "10 /usr/bin/codex --no-daemon exec --model example\n"
            "11 /usr/bin/codex -c x=y exec resume id\n"
            "12 /usr/bin/codex app-server --stdio\n"
            "13 /usr/bin/codex resume id\n"
        ),
    )
    assert dispatch.other_workers() == 2
    assert dispatch.other_workers(10) == 1


def test_free_resets_only_at_weekly_exhaustion_and_oldest_expiry_first(queue):
    d = runner(queue)
    config = dispatch.load_queue(queue)
    assert not d.maybe_reset(config, snapshot(100, 36, False))
    assert not d.client.calls
    d.client.usage = snapshot(100, 100, False)
    assert d.maybe_reset(config, d.client.snapshot())
    method, request = d.client.calls[0]
    assert method == "account/rateLimitResetCredit/consume"
    assert request["creditId"] == "first"
    assert request["idempotencyKey"]
    assert not d.maybe_reset(config, d.client.snapshot())
    assert len(d.client.calls) == 1


def test_reset_timeout_retries_same_durable_key(queue):
    d = runner(queue, snapshot(100, 100, False))
    config = dispatch.load_queue(queue)
    original = d.client.request

    def timeout(method, params):
        d.client.calls.append((method, dict(params)))
        raise TimeoutError

    d.client.request = timeout
    with pytest.raises(TimeoutError):
        d.maybe_reset(config, d.client.snapshot())
    stored = json.loads((queue.parent / "state.json").read_text())
    key = next(iter(stored["resets"].values()))["idempotencyKey"]
    d.client.request = original
    d.maybe_reset(config, d.client.snapshot())
    assert d.client.calls[-1][1]["idempotencyKey"] == key


@pytest.mark.parametrize(
    "mutate", ["cycle", "same_worktree", "raw_model", "bad_profile"]
)
def test_invalid_queue_cannot_bypass_plan(queue, mutate):
    config = json.loads(queue.read_text())
    job = config["jobs"][0]
    if mutate == "cycle":
        job["depends_on"] = ["repair"]
    elif mutate == "same_worktree":
        job["worktree"] = config["repository"]
    elif mutate == "raw_model":
        job["model"] = "gpt-6-astra"
    else:
        job["profile"] = "ultra"
    dispatch.atomic_json(queue, config)
    with pytest.raises(ValueError):
        dispatch.load_queue(queue)


def test_command_has_standard_plus_auth_explicit_effort_and_recorded_resume(queue):
    job = dispatch.load_queue(queue)["jobs"][0]
    attempt = queue.parent / "attempts" / "repair-001"
    command = dispatch.command_for("codex", job, {"session_id": "saved-id"}, attempt)
    assert command[:3] == ["codex", "--no-daemon", "exec"]
    assert 'service_tier="default"' in command
    assert 'forced_login_method="chatgpt"' in command
    assert 'model_reasoning_effort="high"' in command
    assert command[-3:] == ["resume", "saved-id", "-"]
    assert command[command.index("--output-schema") + 1] == str(
        queue.parent / "result-schema.json"
    )


def test_api_environment_is_not_forwarded(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "fake-not-a-key")
    monkeypatch.setenv("CODEX_API_KEY", "fake-not-a-key")
    env = dispatch.child_environment()
    assert "OPENAI_API_KEY" not in env and "CODEX_API_KEY" not in env
    assert os.environ["CODEX_API_KEY"] == "fake-not-a-key"


def fake_cli(directory: Path, *, sleeping=False) -> str:
    """A local process protocol double, not an OpenAI or model call."""
    executable = directory / "fake-codex"
    body = f"""#!{sys.executable}
import json,sys,time
if 'app-server' in sys.argv:
    for line in sys.stdin:
        request=json.loads(line)
        if 'id' not in request: continue
        method=request['method']
        if method=='account/read':
            result={{'account':{{'type':'chatgpt','planType':'plus','email':'private@example.invalid','secret':'DO_NOT_SAVE_AUTH'}}}}
        elif method=='account/rateLimits/read':
            result={{'ordinaryUsageAllowed':False,'rateLimits':{{'primary':{{'usedPercent':100}},'secondary':{{'usedPercent':36}}}}}}
        else: result={{}}
        print(json.dumps({{'id':request['id'],'result':result}}),flush=True)
else:
    from pathlib import Path
    print(json.dumps({{'type':'thread.started','thread_id':'fake-session'}}),flush=True)
    sys.stdin.read()
    if {sleeping!r}: time.sleep(20)
    target=Path(sys.argv[sys.argv.index('--output-last-message')+1])
    target.write_text(json.dumps({{'outcome':'complete','summary':'fake work','checkpoint':'fake.md'}}))
"""
    executable.write_text(body)
    executable.chmod(0o755)
    return str(executable)


def test_real_stdio_metadata_transport_never_saves_authentication_response(queue):
    client = dispatch.CodexRPC(fake_cli(queue.parent))
    try:
        usage = client.snapshot()
    finally:
        client.close()
    text = json.dumps(usage)
    assert usage["auth_type"] == "chatgpt" and usage["account_fingerprint"]
    assert "private@example" not in text and "DO_NOT_SAVE_AUTH" not in text
    assert usage["ordinary_allowed"] is False


class FastEvent:
    def wait(self, seconds):
        time.sleep(0.01)
        return False

    def is_set(self):
        return False


def test_fake_worker_completion_and_duplicate_once_run(queue, monkeypatch):
    d = runner(queue)
    d.codex = fake_cli(queue.parent)
    d.stop = FastEvent()
    monkeypatch.setattr(dispatch, "other_workers", lambda *args: 0)
    d.run(once=True)
    record = d.state["jobs"]["repair"]
    assert record["status"] == "complete"
    assert record["session_id"] == "fake-session"
    assert d.state["batches"] == 1
    d.client = FakeClient()
    d.run(once=True)
    assert d.state["batches"] == 1


def test_unknown_quota_interrupts_only_owned_worker_and_keeps_session(
    queue, monkeypatch
):
    d = runner(queue)
    d.codex = fake_cli(queue.parent, sleeping=True)
    d.stop = FastEvent()
    monkeypatch.setattr(dispatch, "other_workers", lambda *args: 0)

    def observe(**kwargs):
        logs = (queue.parent / "attempts").glob("*/events.jsonl")
        if not any(dispatch.session_from_log(path) for path in logs):
            return snapshot()
        raise TimeoutError

    monkeypatch.setattr(d, "observe", observe)
    d.run(once=True)
    record = d.state["jobs"]["repair"]
    assert record["interruption"] == "quota_unknown"
    assert record["status"] == "pending"
    assert record["session_id"] == "fake-session"


def authorize_publication(queue, remote):
    config = dispatch.load_queue(queue)
    subprocess.run(
        ["git", "-C", config["repository"], "remote", "add", "origin", str(remote)],
        check=True,
    )
    dispatch.atomic_json(
        queue.parent / "publication.json",
        {
            "enabled": True,
            "branch": "coloring-paper-revamp-codex",
            "remote": "origin",
            "remote_url": str(remote),
        },
    )
    return config


def test_publication_pushes_only_committed_integration_head(queue, tmp_path):
    remote = tmp_path / "remote.git"
    subprocess.run(["git", "init", "--bare", "-q", str(remote)], check=True)
    config = authorize_publication(queue, remote)
    root = Path(config["repository"])
    (root / "README.md").write_text("Preserve user changes")
    dispatcher = dispatch.Dispatcher(queue, "unused")
    dispatcher.publish(config)
    head = subprocess.check_output(["git", "-C", str(root), "rev-parse", "HEAD"])
    pushed = subprocess.check_output(
        [
            "git",
            "--git-dir",
            str(remote),
            "rev-parse",
            "refs/heads/coloring-paper-revamp-codex",
        ]
    )
    assert head == pushed
    assert (root / "README.md").read_text() == "Preserve user changes"
    assert (
        subprocess.check_output(
            [
                "git",
                "-C",
                str(root),
                "diff",
                "--cached",
                "--name-only",
            ]
        )
        == b""
    )
    first = dict(dispatcher.state["publication"])
    dispatcher.publish(config)
    assert dispatcher.state["publication"] == first


def test_publication_rejects_changed_remote_and_wrong_branch(queue, tmp_path):
    config = authorize_publication(queue, tmp_path / "remote.git")
    dispatcher = dispatch.Dispatcher(queue, "unused")
    root = config["repository"]
    subprocess.run(
        ["git", "-C", root, "remote", "set-url", "origin", "/wrong"], check=True
    )
    with pytest.raises(ValueError, match="remote changed"):
        dispatcher.publish(config)
    subprocess.run(["git", "-C", root, "switch", "-q", "-c", "wrong"], check=True)
    with pytest.raises(ValueError, match="branch changed"):
        dispatcher.publish(config)


def test_publication_preserves_divergent_remote(queue, tmp_path):
    remote = tmp_path / "remote.git"
    subprocess.run(["git", "init", "--bare", "-q", str(remote)], check=True)
    config = authorize_publication(queue, remote)
    dispatcher = dispatch.Dispatcher(queue, "unused")
    dispatcher.publish(config)
    root = config["repository"]
    original = dispatcher.state["publication"]["commit"]
    env = dict(
        os.environ,
        GIT_AUTHOR_NAME="Test",
        GIT_AUTHOR_EMAIL="test@example.invalid",
        GIT_COMMITTER_NAME="Test",
        GIT_COMMITTER_EMAIL="test@example.invalid",
    )
    tree = subprocess.check_output(
        ["git", "-C", root, "rev-parse", "HEAD^{tree}"], text=True
    ).strip()
    foreign = subprocess.check_output(
        [
            "git",
            "-C",
            root,
            "commit-tree",
            tree,
            "-p",
            original,
            "-m",
            "remote change",
        ],
        env=env,
        text=True,
    ).strip()
    subprocess.run(
        [
            "git",
            "-C",
            root,
            "push",
            "origin",
            f"{foreign}:refs/heads/coloring-paper-revamp-codex",
        ],
        check=True,
    )
    subprocess.run(
        ["git", "-C", root, "commit", "--allow-empty", "-q", "-m", "local change"],
        env=env,
        check=True,
    )
    with pytest.raises(subprocess.CalledProcessError):
        dispatcher.publish(config)
    assert dispatcher.state["publication"]["commit"] == original
    assert (
        subprocess.check_output(
            [
                "git",
                "--git-dir",
                str(remote),
                "rev-parse",
                "refs/heads/coloring-paper-revamp-codex",
            ],
            text=True,
        ).strip()
        == foreign
    )

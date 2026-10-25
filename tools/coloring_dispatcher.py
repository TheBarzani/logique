"""Bounded ChatGPT-only queue; waiting and usage checks never invoke a model.

The user's account setting must disable purchased-credit continuation. This
client checks ordinary included-usage permission; it cannot set account billing
controls or establish a cross-machine, transactionally enforced spending cap.
"""

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
import select
import shlex
import signal
import subprocess
import threading
import time
import uuid

PROFILES = {
    "coordinator": ("gpt-6.1-sol", "medium"),
    "controls": ("gpt-6.1-sol", "medium"),
    "comparison": ("gpt-6.1-sol", "medium"),
    "experiments": ("gpt-6.1-sol", "medium"),
    "manuscript": ("gpt-6.1-sol", "medium"),
    "correctness": ("gpt-6.1-sol", "high"),
    "costs": ("gpt-6.1-sol", "high"),
    "native": ("gpt-6.1-sol", "high"),
    "structure": ("gpt-6.1-sol", "high"),
    "cleanup": ("gpt-6-luna", "high"),
    "critical_review": ("gpt-6-astra", "high"),
}
RESULT_SCHEMA = {
    "type": "object",
    "additionalProperties": False,
    "properties": {
        "outcome": {"type": "string", "enum": ["complete", "continue", "blocked"]},
        "summary": {"type": "string"},
        "checkpoint": {"type": "string"},
    },
    "required": ["outcome", "summary", "checkpoint"],
}


def atomic_json(path: Path, value: dict) -> None:
    """Replace one complete JSON document; never publish a partial checkpoint."""
    temporary = path.with_name(path.name + ".tmp")
    with temporary.open("w") as stream:
        json.dump(value, stream, indent=2)
        stream.write(chr(10))
        stream.flush()
        os.fsync(stream.fileno())
    temporary.replace(path)


@contextmanager
def exclusive_lock(path: Path):
    """Hold one repository-wide dispatcher lock, released even after a crash."""
    with path.open("a+") as stream:
        try:
            fcntl.flock(stream, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError as error:
            raise RuntimeError(
                "Another dispatcher holds the repository lock"
            ) from error
        stream.seek(0)
        stream.truncate()
        stream.write(str(os.getpid()))
        stream.flush()
        try:
            yield
        finally:
            fcntl.flock(stream, fcntl.LOCK_UN)


def child_environment() -> dict:
    """Preserve research extras while removing API authentication overrides."""
    env = dict(os.environ)
    for key in (
        "OPENAI_API_KEY",
        "CODEX_API_KEY",
        "OPENAI_ADMIN_KEY",
        "OPENAI_BASE_URL",
        "CODEX_API_BASE_URL",
    ):
        env.pop(key, None)
    return env


class CodexRPC:
    """Read Codex account metadata via stdio, with no thread/turn creation.

    Authentication responses stay in memory. Only a sanitized usage snapshot
    leaves this client. Binary reads avoid TextIO buffering/select deadlocks.
    """

    def __init__(self, codex: str, timeout: float = 15):
        self.timeout = timeout
        self.process = subprocess.Popen(
            [
                codex,
                "app-server",
                "--stdio",
                "-c",
                'forced_login_method="chatgpt"',
            ],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            env=child_environment(),
        )
        self.buffer = b""
        self.sequence = 0
        try:
            self.request(
                "initialize",
                {
                    "clientInfo": {"name": "logique-dispatcher", "version": "1"},
                    "capabilities": {"experimentalApi": True},
                },
            )
            self._send({"method": "initialized"})
        except Exception:
            self.close()
            raise

    def _send(self, message: dict) -> None:
        self.process.stdin.write((json.dumps(message) + chr(10)).encode())
        self.process.stdin.flush()

    def request(self, method: str, params: dict) -> dict:
        """Read one bounded response; do not log authentication payloads."""
        self.sequence += 1
        identifier = self.sequence
        self._send({"id": identifier, "method": method, "params": params})
        deadline = time.monotonic() + self.timeout
        while time.monotonic() < deadline:
            while bytes([10]) in self.buffer:
                line, self.buffer = self.buffer.split(bytes([10]), 1)
                response = json.loads(line)
                if response.get("id") != identifier:
                    continue
                if "error" in response:
                    raise RuntimeError(f"Codex metadata request failed: {method}")
                return response["result"]
            if self.process.poll() is not None:
                raise RuntimeError("Codex metadata process exited")
            if select.select([self.process.stdout], [], [], 0.2)[0]:
                data = os.read(self.process.stdout.fileno(), 65536)
                if not data:
                    raise RuntimeError("Codex metadata pipe closed")
                self.buffer += data
        raise TimeoutError(f"Codex metadata timed out: {method}")

    def snapshot(self, *, reset_details: bool = False) -> dict:
        """Return live Plus/ordinary-usage metadata without email or auth data."""
        account_result = self.request("account/read", {"refreshToken": False})
        account = account_result.get("account") or {}
        usage = self.request(
            "account/rateLimits/read",
            {
                "excludeResetCreditDetails": not reset_details,
                "supportsLunaReserve": False,
            },
        )
        buckets = usage.get("rateLimitsByLimitId") or {}
        bucket = buckets.get("codex") or usage.get("rateLimits") or {}
        identity = (
            (account_result.get("workspaceRouting") or {}).get("chatgptAccountId")
            or usage.get("accountId")
            or account.get("email")
        )
        return {
            "checked_at": time.time(),
            "auth_type": account.get("type"),
            "plan": account.get("planType"),
            "account_fingerprint": (
                hashlib.sha256(identity.encode()).hexdigest() if identity else None
            ),
            "ordinary_allowed": usage.get("ordinaryUsageAllowed"),
            "primary": bucket.get("primary"),
            "secondary": bucket.get("secondary"),
            "limit_reached": bucket.get("rateLimitReachedType"),
            "spend_control_reached": bucket.get("spendControlReached"),
            "reset_credits": usage.get("rateLimitResetCredits"),
            "model_limits": [
                {
                    key: value.get(key)
                    for key in (
                        "limitId",
                        "normalModelSlug",
                        "primary",
                        "secondary",
                        "rateLimitReachedType",
                        "spendControlReached",
                    )
                }
                for value in buckets.values()
                if value.get("normalModelSlug")
            ],
        }

    def models(self) -> set[str]:
        """Check requested model availability without inference or substitution."""
        available = set()
        cursor = None
        for _ in range(100):
            result = self.request(
                "model/list", {"includeHidden": False, "limit": 100, "cursor": cursor}
            )
            available.update(row["model"] for row in result["data"])
            cursor = result.get("nextCursor")
            if cursor is None:
                return available
        raise RuntimeError("Model catalog pagination did not terminate")

    def close(self) -> None:
        """Stop the metadata-only helper without touching model sessions."""
        if self.process.poll() is None:
            self.process.terminate()
            try:
                self.process.wait(timeout=3)
            except subprocess.TimeoutExpired:
                self.process.kill()
                self.process.wait()
        for stream in (self.process.stdin, self.process.stdout):
            stream.close()


def usage_gate(snapshot: dict, spending: dict, model: str | None = None) -> str | None:
    """Fail closed on unknown authentication, settings, permission or windows."""
    if not all(
        spending.get(key) is True
        for key in (
            "confirmed",
            "credit_continuation_disabled",
            "auto_purchase_disabled",
        )
    ):
        return "spending_settings_unverified"
    if snapshot.get("auth_type") != "chatgpt" or snapshot.get("plan") != "plus":
        return "chatgpt_plus_authentication_required"
    if not snapshot.get("account_fingerprint"):
        return "account_identity_unknown"
    for window in (snapshot.get("primary"), snapshot.get("secondary")):
        if not isinstance(window, dict):
            return "quota_unknown"
        used = window.get("usedPercent")
        if type(used) is not int or not 0 <= used <= 100:
            return "quota_unknown"
        if used == 100:
            return "included_quota_exhausted"
    if snapshot.get("ordinary_allowed") is not True:
        return "ordinary_usage_not_authorized"
    if snapshot.get("limit_reached") or snapshot.get("spend_control_reached") is True:
        return "backend_limit_reached"
    for bucket in snapshot.get("model_limits", []):
        if bucket.get("normalModelSlug") != model:
            continue
        windows = [bucket.get("primary"), bucket.get("secondary")]
        if not any(windows):
            return "model_quota_unknown"
        for window in filter(None, windows):
            if type(window.get("usedPercent")) is not int:
                return "model_quota_unknown"
            if not 0 <= window["usedPercent"] < 100:
                return "included_quota_exhausted"
        if bucket.get("rateLimitReachedType") or bucket.get("spendControlReached"):
            return "backend_limit_reached"
    return None


def load_queue(path: Path) -> dict:
    """Validate a finite, appendable queue and the plan's model/effort table."""
    config = json.loads(path.read_text())
    root = Path(config["repository"]).resolve()
    if not root.is_dir() or config.get("schema_version") != 1:
        raise ValueError("Require schema_version=1 and an existing repository")
    if not isinstance(config.get("spending"), dict):
        raise ValueError("Record the user's spending-setting confirmation")
    if type(config.get("allow_free_weekly_resets", False)) is not bool:
        raise ValueError("allow_free_weekly_resets must be Boolean")
    for key, low, high in (
        ("poll_seconds", 15, 300),
        ("monitor_seconds", 5, 60),
        ("max_batches", 1, 128),
    ):
        if type(config.get(key)) is not int or not low <= config[key] <= high:
            raise ValueError(f"{key} must be an integer in [{low}, {high}]")
    deadline = datetime.fromisoformat(config["deadline"])
    if deadline.tzinfo is None:
        raise ValueError("deadline must include its time zone")
    jobs = config.get("jobs")
    if not isinstance(jobs, list) or not 1 <= len(jobs) <= 64:
        raise ValueError("Queue must contain 1..64 bounded jobs")
    identifiers = [job["id"] for job in jobs]
    if len(set(identifiers)) != len(identifiers):
        raise ValueError("Duplicate task IDs")
    for job in jobs:
        if not re.fullmatch(r"[a-z][a-z0-9-]{0,63}", job["id"]):
            raise ValueError("Task IDs must be safe descriptive slugs")
        if job.get("profile") not in PROFILES:
            raise ValueError("Use an approved model/effort profile")
        if set(job) - {
            "id",
            "profile",
            "worktree",
            "branch",
            "prompt_file",
            "session_id",
            "depends_on",
            "dependency_policy",
            "max_seconds",
            "max_attempts",
        }:
            raise ValueError(
                "Unknown job fields; raw model/command overrides forbidden"
            )
        for field in ("worktree", "prompt_file"):
            target = Path(job[field]).resolve()
            if not target.is_relative_to(root) or not target.exists():
                raise ValueError(f"{field} must exist inside the repository")
        worker = job["profile"] != "coordinator"
        if worker and Path(job["worktree"]).resolve() == root:
            raise ValueError(
                "Implementation/review workers require a separate worktree"
            )
        branch = job.get("branch", "")
        if (worker and not branch.startswith("codex/coloring-")) or (
            not worker and branch != "coloring-paper-revamp-codex"
        ):
            raise ValueError("Unexpected integration/worker branch")
        if any(
            dep not in identifiers or dep == job["id"]
            for dep in job.get("depends_on", [])
        ):
            raise ValueError("Dependencies must reference other queued tasks")
        policy = job.get("dependency_policy", "complete")
        if policy not in ("complete", "finished") or (
            policy == "finished"
            and job["profile"] not in ("coordinator", "critical_review")
        ):
            raise ValueError("Only coordinators/reviewers may follow blocked tasks")
        if (
            type(job.get("max_seconds")) is not int
            or not 60 <= job["max_seconds"] <= 3600
        ):
            raise ValueError("max_seconds must be 60..3600")
        if (
            type(job.get("max_attempts")) is not int
            or not 1 <= job["max_attempts"] <= 24
        ):
            raise ValueError("max_attempts must be 1..24")
    # A cycle must not masquerade as a queue merely waiting for dependencies.
    resolved = set()
    while True:
        added = {
            job["id"] for job in jobs if set(job.get("depends_on", [])) <= resolved
        } - resolved
        if not added:
            break
        resolved.update(added)
    if resolved != set(identifiers):
        raise ValueError("Dependency cycle")
    return config


def check_worktree(root: Path, job: dict) -> None:
    """Never switch/reset branches, and reject unrelated nested Git histories."""
    worktree = Path(job["worktree"]).resolve()

    def git(*arguments):
        return subprocess.check_output(
            ["git", "-C", str(worktree), *arguments], text=True
        ).strip()

    common = Path(git("rev-parse", "--git-common-dir"))
    common = common if common.is_absolute() else worktree / common
    if common.resolve() != (root / ".git").resolve():
        raise ValueError("Task does not own a worktree of this repository")
    if git("symbolic-ref", "--short", "HEAD") != job["branch"]:
        raise ValueError("Worktree branch changed; refusing dispatch")


def other_workers(own_pid: int | None = None) -> int:
    """Count local CLI inference workers; never print other process arguments.

    One dispatcher worker plus an active interactive coordinator is the normal
    maximum. Other machines cannot be inspected; they share account allowance.
    """
    output = subprocess.check_output(["ps", "-axo", "pid=,command="], text=True)
    count = 0
    for line in output.splitlines():
        try:
            pid, command = line.strip().split(None, 1)
            argv = shlex.split(command)
        except ValueError:
            continue
        if int(pid) == own_pid or not argv:
            continue
        if Path(argv[0]).name == "codex" and any(
            word in ("exec", "review") for word in argv[1:]
        ):
            count += 1
    return count


def command_for(codex: str, job: dict, record: dict, attempt: Path) -> list[str]:
    """Build an argument vector with explicit included-plan execution settings."""
    model, effort = PROFILES[job["profile"]]
    command = [
        codex,
        "--no-daemon",
        "exec",
        "--ignore-user-config",
        "--model",
        model,
        "-c",
        f'model_reasoning_effort="{effort}"',
        "-c",
        'service_tier="default"',
        "-c",
        'forced_login_method="chatgpt"',
        "--disable",
        "multi_agent",
        "--disable",
        "multi_agent_v2",
        "--approve-for-me",
        "--cd",
        job["worktree"],
        "--json",
        "--output-schema",
        str(attempt.parent.parent / "result-schema.json"),
        "--output-last-message",
        str(attempt / "result.json"),
    ]
    if job["profile"] == "critical_review":
        command += ["-c", 'web_search="live"']
    session = record.get("session_id") or job.get("session_id")
    if session:
        command += ["resume", session]
    return [*command, "-"]


def session_from_log(path: Path) -> str | None:
    """Recover the new/resumed session ID before an interrupted process exits."""
    if not path.exists():
        return None
    with path.open() as stream:
        for _ in range(100):
            line = stream.readline()
            if not line:
                break
            try:
                event = json.loads(line)
            except ValueError:
                continue
            if event.get("type") == "thread.started":
                return event.get("thread_id")
    return None


class Dispatcher:
    """Serialize bounded tasks, checkpoint interruptions, and wait without models."""

    def __init__(self, queue: Path, codex: str):
        self.queue = queue.resolve()
        self.directory = self.queue.parent
        self.codex = codex
        self.stop = threading.Event()
        state = self.directory / "state.json"
        self.state = (
            json.loads(state.read_text())
            if state.exists()
            else {
                "schema_version": 1,
                "batches": 0,
                "jobs": {},
                "resets": {},
            }
        )
        self.client = None

    def save(self, phase: str, **fields) -> None:
        self.state.update(
            phase=phase, updated_at=time.time(), pid=os.getpid(), **fields
        )
        atomic_json(self.directory / "state.json", self.state)

    def observe(self, *, details=False) -> dict:
        if self.client is None:
            self.client = CodexRPC(self.codex)
        try:
            snapshot = self.client.snapshot(reset_details=details)
            fingerprint = snapshot.get("account_fingerprint")
            prior = self.state.get("account_fingerprint")
            if prior and fingerprint != prior:
                raise RuntimeError("Active ChatGPT account changed")
            if fingerprint:
                self.state["account_fingerprint"] = fingerprint
            self.state["usage"] = snapshot
            return snapshot
        except Exception:
            self.client.close()
            self.client = None
            raise

    def publication_policy(self) -> dict | None:
        """Read explicit user authorization separately from immutable task inputs."""
        path = self.directory / "publication.json"
        if not path.exists():
            return None
        policy = json.loads(path.read_text())
        if (
            policy.get("enabled") is not True
            or policy.get("branch") != "coloring-paper-revamp-codex"
            or policy.get("remote") != "origin"
            or not isinstance(policy.get("remote_url"), str)
            or not policy["remote_url"]
        ):
            raise ValueError("Invalid publication authorization")
        return policy

    def publish(self, config: dict) -> None:
        """Push committed integration work only; never stage files or force push."""
        policy = self.publication_policy()
        if policy is None:
            return
        root = Path(config["repository"]).resolve()
        check_worktree(root, {"worktree": str(root), "branch": policy["branch"]})

        def git(*args):
            return subprocess.check_output(
                ["git", "-C", str(root), *args],
                text=True,
                stderr=subprocess.PIPE,
                timeout=60,
                env={**os.environ, "GIT_TERMINAL_PROMPT": "0"},
            ).strip()

        urls = git("remote", "get-url", "--push", "--all", "origin").splitlines()
        if urls != [policy["remote_url"]]:
            raise ValueError("Publication remote changed")
        head = git("rev-parse", "HEAD")
        publication = self.state.get("publication", {})
        identity = hashlib.sha256(
            json.dumps(policy, sort_keys=True).encode()
        ).hexdigest()
        if publication.get("commit") == head and publication.get("policy") == identity:
            return
        # An explicit refspec avoids upstream/push.default surprises. Git rejects
        # divergence; no pull, merge, reset, force flag, or worker branch push.
        git("push", "origin", f"{head}:refs/heads/{policy['branch']}")
        self.state["publication"] = {
            "commit": head,
            "branch": policy["branch"],
            "remote": "origin",
            "policy": identity,
            "pushed_at": time.time(),
        }
        self.save("published")

    def maybe_reset(self, config: dict, snapshot: dict) -> bool:
        """Redeem a free reset only at weekly exhaustion, using a durable key."""
        weekly = snapshot.get("secondary") or {}
        if (
            not config.get("allow_free_weekly_resets")
            or weekly.get("usedPercent") != 100
            or snapshot.get("auth_type") != "chatgpt"
            or snapshot.get("plan") != "plus"
            or not all(
                config["spending"].get(key) is True
                for key in (
                    "confirmed",
                    "credit_continuation_disabled",
                    "auto_purchase_disabled",
                )
            )
        ):
            return False
        window = str(weekly.get("resetsAt"))
        if window == "None":
            return False
        pending = self.state.get("reset_pending")
        if pending and pending["window"] != window:
            # Never consume another reset before observing actual recovery.
            return False
        snapshot = self.observe(details=True)
        if (snapshot.get("secondary") or {}).get("usedPercent") != 100:
            return False
        credits = snapshot.get("reset_credits") or {}
        if not credits.get("availableCount"):
            return False
        requests = self.state["resets"]
        request = requests.get(window)
        if request and request.get("outcome"):
            return False
        if request is None:
            candidates = [
                c
                for c in credits.get("credits") or []
                if c.get("status") == "available"
                and (c.get("expiresAt") is None or c["expiresAt"] > time.time())
            ]
            candidates.sort(key=lambda c: c.get("expiresAt") or float("inf"))
            if credits.get("credits") is not None and not candidates:
                return False
            request = {"idempotencyKey": str(uuid.uuid4())}
            if candidates:
                request["creditId"] = candidates[0]["id"]
            requests[window] = request
        self.state["reset_pending"] = {"window": window}
        self.save("redeeming_free_weekly_reset")
        params = {
            key: request[key]
            for key in ("idempotencyKey", "creditId")
            if key in request
        }
        result = self.client.request("account/rateLimitResetCredit/consume", params)
        request["outcome"] = result.get("outcome") or "unknown"
        self.save("waiting_for_reset_confirmation")
        return True

    def interrupt(self, process, reason: str, record: dict) -> None:
        """Cancel only our process group; never kill an unrelated/reused PID."""
        record["interruption"] = reason
        self.save("interrupting_worker")
        if process.poll() is None:
            try:
                os.killpg(process.pid, signal.SIGINT)
            except ProcessLookupError:
                return
            try:
                process.wait(timeout=15)
            except subprocess.TimeoutExpired:
                os.killpg(process.pid, signal.SIGTERM)
                try:
                    process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    os.killpg(process.pid, signal.SIGKILL)
                    process.wait()
                    record["forced_kill"] = True

    def launch(self, config: dict, job: dict, record: dict) -> None:
        root = Path(config["repository"]).resolve()
        check_worktree(root, job)
        if other_workers():
            self.save("waiting_for_other_local_worker")
            return
        model, _ = PROFILES[job["profile"]]
        if model not in self.client.models():
            record.update(status="blocked", reason="requested_model_unavailable")
            self.save("blocked_model_unavailable")
            return
        session = record.get("session_id") or job.get("session_id")
        if session:
            thread = self.client.request(
                "thread/read", {"threadId": session, "includeTurns": False}
            ).get("thread", {})
            if Path(thread.get("cwd", "")).resolve() != Path(job["worktree"]).resolve():
                record.update(status="blocked", reason="resume_worktree_mismatch")
                self.save("blocked_resume_context")
                return
            if (thread.get("status") or {}).get("type") not in ("idle", "notLoaded"):
                self.save("waiting_for_resumed_session_to_be_idle")
                return
            record["session_id"] = session
        # Re-read live permission immediately before the single launch.
        if usage_gate(self.observe(), config["spending"], model):
            self.save("waiting_for_included_quota")
            return
        attempts = record.get("attempts", 0) + 1
        attempt = self.directory / "attempts" / f"{job['id']}-{attempts:03d}"
        attempt.mkdir(parents=True, exist_ok=False)
        record.update(status="launching", attempts=attempts, attempt=str(attempt))
        record.update(
            model=model,
            effort=PROFILES[job["profile"]][1],
            speed="Standard",
            worktree=job["worktree"],
            branch=job["branch"],
            prompt_file=job["prompt_file"],
        )
        self.state["batches"] += 1
        self.save("launching_worker")  # Crash here is ambiguous, never auto-relaunched.
        command = command_for(self.codex, job, record, attempt)
        env = child_environment()
        env.update(
            PYTHONPATH=str(Path(job["worktree"]) / "src"),
            OPENBLAS_NUM_THREADS="1",
            OMP_NUM_THREADS="1",
            PYTHONDONTWRITEBYTECODE="1",
            LOGIQUE_DISPATCH_QUEUE=str(self.queue),
            LOGIQUE_DISPATCH_JOB=job["id"],
            LOGIQUE_DISPATCH_STATE=str(self.directory / "state.json"),
        )
        publication = self.publication_policy()
        publication_rules = (
            "Latest user authorization supersedes older no-push instructions: "
            "commit validated task-owned changes using explicit file paths; never "
            "stage unrelated user edits, including existing README.md changes. "
            "Keep correctness and research-metric changes in separate commits. "
            "Workers commit on their assigned worktree branches. The coordinator "
            "integrates reviewed commits on coloring-paper-revamp-codex and commits "
            "its validated integration changes before returning. The dispatcher "
            "pushes committed integration HEAD to origin/coloring-paper-revamp-codex; "
            "do not push worker branches or run git push yourself. "
            if publication
            else "No pushes or publishing. "
        )
        prompt = Path(job["prompt_file"]).read_text() + (
            "\n\nDispatcher rules: do not launch Codex/model subprocesses or subagents. "
            "No API/credits or hardware. Preserve checkpoints. "
            + publication_rules
            + "This is one bounded batch; return the required result JSON. "
            "If scope remains, outcome=continue and leave a concrete checkpoint."
        )
        started = time.monotonic()
        interrupted = None
        with (
            (attempt / "events.jsonl").open("w") as out,
            (attempt / "stderr.log").open("w") as err,
        ):
            process = subprocess.Popen(
                command,
                cwd=job["worktree"],
                env=env,
                stdin=subprocess.PIPE,
                stdout=out,
                stderr=err,
                text=True,
                start_new_session=True,
            )
            record.update(status="running", worker_pid=process.pid)
            self.save("worker_running")
            try:
                process.stdin.write(prompt)
                process.stdin.close()
                while process.poll() is None:
                    session = session_from_log(attempt / "events.jsonl")
                    if session:
                        record["session_id"] = session
                    if self.stop.wait(config["monitor_seconds"]):
                        interrupted = "dispatcher_stopped"
                    elif (
                        time.time()
                        >= datetime.fromisoformat(config["deadline"]).timestamp()
                    ):
                        interrupted = "deadline_reached"
                    elif time.monotonic() - started >= job["max_seconds"]:
                        interrupted = "bounded_batch_timeout"
                    elif (self.directory / "PAUSE").exists():
                        interrupted = "operator_pause"
                    else:
                        try:
                            reason = usage_gate(
                                self.observe(), config["spending"], model
                            )
                            if reason:
                                interrupted = reason
                            elif other_workers(process.pid):
                                interrupted = "another_local_worker_started"
                        except Exception:
                            interrupted = "quota_unknown"
                    if interrupted:
                        self.interrupt(process, interrupted, record)
                        break
                    self.save("worker_running")
            finally:
                if process.poll() is None:
                    self.interrupt(process, "dispatcher_exception", record)
        record["exit_code"] = process.returncode
        session = session_from_log(attempt / "events.jsonl")
        if session:
            record["session_id"] = session
        record.pop("worker_pid", None)
        result_path = attempt / "result.json"
        if interrupted:
            record["status"] = "pending" if record.get("session_id") else "ambiguous"
            if record.get("forced_kill"):
                record["status"] = "ambiguous"
        elif process.returncode == 0 and result_path.exists():
            try:
                result = json.loads(result_path.read_text())
                if not isinstance(result, dict) or any(
                    not isinstance(result.get(key), str)
                    for key in ("outcome", "summary", "checkpoint")
                ):
                    raise ValueError("Incomplete result")
                record.update(
                    status={
                        "complete": "complete",
                        "continue": "pending",
                        "blocked": "blocked",
                    }.get(result["outcome"], "blocked"),
                    result=result,
                )
            except ValueError:
                record.update(status="blocked", reason="invalid_result_json")
        else:
            # A quota failure is resumable only with an explicit live denial.
            try:
                denied = (
                    usage_gate(self.observe(), config["spending"], model) is not None
                )
            except Exception:
                denied = True
            record["status"] = (
                "pending" if denied and record.get("session_id") else "blocked"
            )
            record["reason"] = "worker_failed; inspect attempt logs"
        self.save("batch_finished")

    def run(self, *, once=False) -> None:
        config = load_queue(self.queue)
        root = Path(config["repository"]).resolve()
        lock = root / ".cache" / "coloring-dispatcher.lock"
        lock.parent.mkdir(parents=True, exist_ok=True)
        with exclusive_lock(lock):
            atomic_json(self.directory / "result-schema.json", RESULT_SCHEMA)
            for record in self.state["jobs"].values():
                if record.get("status") in ("launching", "running"):
                    record.update(
                        status="ambiguous",
                        reason="dispatcher interrupted; inspect prior session before recovery",
                    )
            try:
                while not self.stop.is_set():
                    try:
                        config = load_queue(self.queue)
                    except (OSError, ValueError, KeyError, TypeError):
                        self.save("blocked_invalid_queue")
                        return
                    header = {k: v for k, v in config.items() if k != "jobs"}
                    header_hash = hashlib.sha256(
                        json.dumps(header, sort_keys=True).encode()
                    ).hexdigest()
                    prior_header = self.state.setdefault(
                        "queue_header_sha256", header_hash
                    )
                    if prior_header != header_hash:
                        self.save("blocked_configuration_changed")
                        return
                    if not (self.directory / "PAUSE").exists():
                        try:
                            self.publish(config)
                        except (OSError, ValueError, subprocess.SubprocessError):
                            self.save(
                                "waiting",
                                reason="publication_failed; inspect remote/auth/divergence",
                            )
                            if once:
                                return
                            self.stop.wait(config["poll_seconds"])
                            continue
                    if (
                        time.time()
                        >= datetime.fromisoformat(config["deadline"]).timestamp()
                    ):
                        self.save("deadline_reached")
                        return
                    if self.state["batches"] >= config["max_batches"]:
                        self.save("batch_limit_reached")
                        return
                    if (self.directory / "PAUSE").exists():
                        self.save("operator_paused")
                    else:
                        ready = None
                        for job in config["jobs"]:
                            digest = hashlib.sha256(
                                json.dumps(job, sort_keys=True).encode()
                            ).hexdigest()
                            record = self.state["jobs"].setdefault(
                                job["id"],
                                {"status": "pending", "definition_sha256": digest},
                            )
                            if record["definition_sha256"] != digest:
                                self.save("blocked_task_definition_changed")
                                return
                            if (
                                record["status"] == "pending"
                                and record.get("attempts", 0) >= job["max_attempts"]
                            ):
                                record.update(
                                    status="blocked", reason="attempt_limit_reached"
                                )
                            if record["status"] != "pending":
                                continue
                            finished = (
                                {"complete", "blocked"}
                                if job.get("dependency_policy") == "finished"
                                else {"complete"}
                            )
                            if all(
                                self.state["jobs"].get(dep, {}).get("status")
                                in finished
                                for dep in job.get("depends_on", [])
                            ):
                                ready = (job, record)
                                break
                        if ready:
                            try:
                                snapshot = self.observe()
                                reason = usage_gate(
                                    snapshot,
                                    config["spending"],
                                    PROFILES[ready[0]["profile"]][0],
                                )
                                if reason is None:
                                    if self.state.get("reset_pending"):
                                        self.state.pop("reset_pending")
                                    self.launch(config, *ready)
                                elif (
                                    reason == "included_quota_exhausted"
                                    and self.maybe_reset(config, snapshot)
                                ):
                                    self.save("waiting_for_reset_confirmation")
                                else:
                                    self.save("waiting", reason=reason)
                            except (
                                RuntimeError,
                                TimeoutError,
                                OSError,
                                ValueError,
                                KeyError,
                            ):
                                self.save(
                                    "waiting",
                                    reason="metadata_or_workspace_unavailable",
                                )
                        else:
                            self.save(
                                "queue_idle",
                                reason="no_ready_tasks; inspect dependencies or blocked jobs",
                            )
                    if once:
                        return
                    self.stop.wait(config["poll_seconds"])
            finally:
                if self.client:
                    self.client.close()
                self.save(
                    "stopped"
                    if self.stop.is_set()
                    else self.state.get("phase", "stopped")
                )


def main() -> int:
    """Run/status the local queue; no shell command or model override is accepted."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=("run", "status", "pause", "unpause"))
    parser.add_argument("--queue", type=Path, required=True)
    parser.add_argument("--codex", default="codex")
    parser.add_argument("--once", action="store_true")
    args = parser.parse_args()
    if args.action == "status":
        print((args.queue.parent / "state.json").read_text())
        return 0
    if args.action in ("pause", "unpause"):
        marker = args.queue.parent / "PAUSE"
        if args.action == "pause":
            marker.touch()
        else:
            marker.unlink(missing_ok=True)
        return 0
    dispatcher = Dispatcher(args.queue, args.codex)
    for sig in (signal.SIGINT, signal.SIGTERM):
        signal.signal(sig, lambda *_: dispatcher.stop.set())
    dispatcher.run(once=args.once)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

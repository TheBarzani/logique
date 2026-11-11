"""Publish Thursday research slide PDFs from saved briefs without model calls."""

from __future__ import annotations

import argparse
from datetime import datetime, time as wall_time, timedelta
import hashlib
import json
from pathlib import Path
import re
import signal
import subprocess
import threading
import time
from zoneinfo import ZoneInfo

from coloring_notifications import GitHub, locked, research_reports, save
from logique.paths import new_dump_directory


def due_date(now: datetime, config: dict) -> datetime | None:
    """Return the latest due Thursday, using local civil time across DST."""
    local = now.astimezone(ZoneInfo(config["timezone"]))
    day = local.date() - timedelta(days=(local.weekday() - 3) % 7)
    due = datetime.combine(day, wall_time(config["hour"], 0), local.tzinfo)
    if due > local:
        due -= timedelta(days=7)
    return due if due.date().isoformat() >= config["start_date"] else None


def gather_reports(queue: Path, start: float, end: float) -> list[dict]:
    """Follow preserved predecessor runs and retain only completed weekly briefs."""
    reports = {}
    seen = set()
    while queue not in seen:
        seen.add(queue)
        for report in research_reports(queue):
            if start <= report["written_at"] < end:
                reports[report["id"]] = report
        state = json.loads(queue.with_name("state.json").read_text())
        previous = state.get("previous_run")
        if not previous:
            break
        queue = Path(previous) / "queue.json"
    return sorted(reports.values(), key=lambda r: r["written_at"])


def topic(source: str) -> str:
    """Group authored findings by research area without inferring admission."""
    name = Path(source).parent.name
    groups = (
        ("scaling", "Scaling and reproducibility"),
        ("native", "Native synthesis and mapping"),
        ("profiles", "Optimization profiles"),
        ("mc-pass", "Multiplicative-complexity optimization"),
        ("comparison", "Controlled comparisons"),
        ("component", "Circuit lowering correctness"),
        ("c5", "C5 coloring experiments"),
        ("noisy", "Noise and success probability"),
        ("graph-ft", "Fault-tolerant search costs"),
        ("dynamic", "Measurement-assisted preparation"),
        ("mcx", "Multi-controlled gate tradeoffs"),
        ("manuscript", "Manuscript and contribution"),
    )
    return next((label for key, label in groups if key in name), "Research outlook")


def clean_text(text: str) -> str:
    """Make authored prose readable on slides and remove local home paths."""
    text = re.sub(r"/(?:Users|home)/[^\s\])<>]+", "[local evidence]", text)
    text = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", text)
    text = re.sub(r"<[^>]*>", "", text)
    text = re.sub(r"(?m)^#{1,6}\s*", "", text)
    text = text.replace("**", "").replace("`", "").replace(r"\%", "%")
    return text.strip()


def tex_escape(text: str) -> str:
    """Escape all TeX control characters; researcher text cannot execute TeX."""
    mapping = {
        "\\": r"\textbackslash{}",
        "{": r"\{",
        "}": r"\}",
        "$": r"\$",
        "&": r"\&",
        "#": r"\#",
        "%": r"\%",
        "_": r"\_",
        "~": r"\textasciitilde{}",
        "^": r"\textasciicircum{}",
    }
    return "".join(mapping.get(char, char) for char in text)


def chunks(text: str, words: int = 115) -> list[str]:
    """Keep sentences and inline calculations together on bounded slides."""
    pages = []
    current = []
    for sentence in re.split(r"(?<=[.!?])\s+(?=[A-Z])", text):
        tokens = re.findall(r"\$[^$]+\$|\S+", sentence)
        if current and len(current) + len(tokens) > words:
            pages.append(" ".join(current))
            current = []
        while len(tokens) > words:
            pages.append(" ".join(tokens[:words]))
            tokens = tokens[words:]
        current.extend(tokens)
    if current:
        pages.append(" ".join(current))
    return pages


def tex_prose(text: str) -> str:
    """Typeset bounded inline mathematics, escaping every other control token."""
    allowed = {
        "times",
        "to",
        "frac",
        "sqrt",
        "sin",
        "cos",
        "arcsin",
        "pi",
        "theta",
        "epsilon",
        "le",
        "leq",
        "ge",
        "geq",
        "approx",
        "cdot",
        "pm",
        "mathrm",
        "text",
        "left",
        "right",
        "Pr",
        "lvert",
        "rvert",
        "dagger",
    }
    parts = re.split(r"(\$[^$\n]+\$)", text)
    output = []
    for part in parts:
        expression = part[1:-1]
        commands = set(re.findall(r"\\([A-Za-z]+)", expression))
        depth = 0
        balanced = True
        for char in expression:
            depth += (char == "{") - (char == "}")
            if depth < 0:
                balanced = False
        if (
            part.startswith("$")
            and part.endswith("$")
            and len(expression) <= 600
            and balanced
            and depth == 0
            and commands <= allowed
            and re.fullmatch(r"[A-Za-z0-9\s_{}^+*/=().,|<>!:;\-\\]+", expression)
            and "^^" not in expression
        ):
            output.append(part)
        else:
            output.append(tex_escape(part))
    return "".join(output)


def render_deck(snapshot: dict) -> tuple[str, str]:
    """Render latest narratives per area, with complete weekly notes alongside."""
    latest = {}
    for report in snapshot["reports"]:
        latest[topic(report["source"])] = report
    slides = [
        (
            "Coloring-paper research briefing",
            f"{snapshot['start_label']} to {snapshot['end_label']}\n\n"
            "What the experiments and independent reviews now support, what "
            "remains unresolved, and what could change the manuscript.\n\n"
            "The following slides reproduce the latest researcher narrative in "
            "each area. Full technical notes include all completed briefings "
            "from the reporting period. No new scientific admission is implied.",
        )
    ]
    notes = [f"# Weekly research notes — {snapshot['end_label']}"]
    notes.append(
        "Latest narratives appear in the slides; every eligible briefing is "
        "included below in chronological order. Implementation claims remain "
        "subject to their stated independent-review qualifications."
    )
    for area, report in latest.items():
        # The main narrative precedes optional technical details. Preserve it
        # completely rather than truncating away conclusions or qualifications.
        main = report["body"].split("<details>", 1)[0]
        for index, part in enumerate(chunks(clean_text(main))):
            slides.append((area + (f" ({index + 1})" if index else ""), part))
    if not latest:
        slides.append(
            (
                "No new completed research briefing",
                "No eligible completed researcher report was saved in this "
                "reporting period. Existing findings retain their previous "
                "qualifications. This is not evidence that the manuscript or "
                "the research is complete.",
            )
        )
    for report in snapshot["reports"]:
        notes.extend(
            [
                f"## {topic(report['source'])} — {report['date_label']}",
                re.sub(
                    r"/(?:Users|home)/[^\s\])<>]+",
                    "[local evidence]",
                    report["body"],
                ),
            ]
        )
    slides.append(
        (
            "Reading the evidence",
            "Measured probabilities, analytical calculations, implementation "
            "checks and independent admission are different kinds of evidence. "
            "Use each finding only within its stated graph, domain, precision "
            "and workspace scope.\n\n"
            "The companion notes retain the technical calculations, losses, "
            "exclusions and source links, including earlier briefings that a "
            "later review may restrict.\n\n"
            f"Dispatcher at the snapshot: {snapshot['phase']}. "
            "Model quota pauses do not prevent this local weekly report.",
        )
    )
    tex = [
        r"\documentclass[aspectratio=169]{beamer}",
        r"\setbeamertemplate{navigation symbols}{}",
        r"\setbeamertemplate{footline}[frame number]",
        r"\setbeamercolor{structure}{fg=blue!55!black}",
        r"\begin{document}",
    ]
    for title, content in slides:
        tex.extend(
            [
                r"\begin{frame}[t]{" + tex_escape(title) + "}",
                r"\small\raggedright",
                tex_prose(content).replace("\n\n", "\n\\par\\medskip\n"),
                r"\end{frame}",
            ]
        )
    tex.append(r"\end{document}")
    return "\n".join(tex) + "\n", "\n\n".join(notes) + "\n"


def digest(path: Path) -> str:
    """Hash immutable report or hosted asset bytes."""
    return hashlib.sha256(path.read_bytes()).hexdigest()


class WeeklyGitHub(GitHub):
    """Host PDFs in one prerelease and link them in idempotent weekly issues."""

    def __init__(self, config: dict):
        super().__init__({**config, "issue": 1})
        self.tag = "coloring-research-briefing-pdfs"

    def find_issue(self, marker: str):
        pages = self.api(
            f"repos/{self.repository}/issues?state=all&per_page=100",
            "--paginate",
            "--slurp",
        )
        return next(
            (
                issue
                for page in pages
                for issue in page
                if marker in (issue.get("body") or "")
            ),
            None,
        )

    def release(self, directory: Path):
        endpoint = f"repos/{self.repository}/releases/tags/{self.tag}"
        try:
            return self.api(endpoint)
        except subprocess.CalledProcessError as error:
            if "HTTP 404" not in (error.stderr or ""):
                raise
        payload = directory / "release-payload.json"
        save(
            payload,
            {
                "tag_name": self.tag,
                "target_commitish": "coloring-paper-revamp-codex",
                "name": "Coloring research briefing PDFs",
                "body": "Document hosting for weekly research issues; not a software release or scientific approval.",
                "prerelease": True,
                "make_latest": "false",
            },
        )
        return self.api(
            "--method", "POST", f"repos/{self.repository}/releases", payload=payload
        )

    def asset(self, release: dict, path: Path) -> str:
        assets = self.api(
            f"repos/{self.repository}/releases/{release['id']}/assets?per_page=100",
            "--paginate",
            "--slurp",
        )
        existing = next(
            (a for page in assets for a in page if a["name"] == path.name), None
        )
        if existing is None:
            subprocess.run(
                [
                    self.gh,
                    "release",
                    "upload",
                    self.tag,
                    str(path),
                    "--repo",
                    self.repository,
                ],
                check=True,
                capture_output=True,
                timeout=120,
            )
            return self.asset(release, path)
        # Read back the actual uploaded bytes, including on a retry after an
        # accepted-but-timed-out upload. Never overwrite an existing asset.
        response = subprocess.run(
            [self.gh, "api", existing["url"], "-H", "Accept: application/octet-stream"],
            check=True,
            capture_output=True,
            timeout=120,
        )
        if hashlib.sha256(response.stdout).hexdigest() != digest(path):
            raise RuntimeError("Weekly asset read-back mismatch")
        return existing["browser_download_url"]

    def deliver(self, pending: dict):
        directory = Path(pending["directory"])
        urls = {}
        release = self.release(directory)
        for name, expected in pending["assets"].items():
            path = directory / name
            if digest(path) != expected:
                raise RuntimeError("Weekly artifact changed after checkpoint")
            urls[path.suffix] = self.asset(release, path)
        body = pending["body"] + (
            f"\n\n[Download the slide PDF]({urls['.pdf']}) · "
            f"[Full technical notes]({urls['.md']}) · "
            f"[LaTeX source]({urls['.tex']})\n\n{pending['marker']}"
        )
        issue = self.find_issue(pending["marker"])
        if issue is None:
            payload = directory / "issue-payload.json"
            save(
                payload,
                {"title": pending["title"], "body": body, "assignees": ["TheBarzani"]},
            )
            issue = self.api(
                "--method", "POST", f"repos/{self.repository}/issues", payload=payload
            )
        saved = self.api(f"repos/{self.repository}/issues/{issue['number']}")
        if saved.get("body") != body:
            raise RuntimeError("Weekly issue read-back mismatch")
        return {"url": saved["html_url"], "assets": urls}


class Weekly:
    """Independent civil-time scheduler with frozen artifacts and a durable outbox."""

    def __init__(self, config_path: Path, remote=None):
        self.config = json.loads(config_path.read_text())
        self.directory = config_path.resolve().parent
        self.path = self.directory / "weekly-state.json"
        self.state = (
            json.loads(self.path.read_text())
            if self.path.exists()
            else {"delivered": {}, "previews": []}
        )
        ZoneInfo(self.config["timezone"])
        if type(self.config["hour"]) is not int or not 0 <= self.config["hour"] <= 23:
            raise ValueError("Weekly hour must be 0..23")
        self.remote = remote or WeeklyGitHub(self.config)
        self.stop = threading.Event()

    def build(self, end: datetime, key: str) -> dict:
        start = end - timedelta(days=7)
        pointer = Path(self.config["active_pointer"])
        queue = Path(json.loads(pointer.read_text())["queue"])
        state = json.loads(queue.with_name("state.json").read_text())
        reports = gather_reports(queue, start.timestamp(), end.timestamp())
        for report in reports:
            report["date_label"] = datetime.fromtimestamp(
                report["written_at"], end.tzinfo
            ).strftime("%d %b %H:%M %Z")
        snapshot = {
            "start_label": start.strftime("%d %B %Y %H:%M %Z"),
            "end_label": end.strftime("%d %B %Y %H:%M %Z"),
            "phase": state.get("phase", "unknown"),
            "reports": reports,
        }
        directory = new_dump_directory(
            "weekly-research-presentation", root=Path(self.config["output_root"])
        )
        save(directory / "snapshot.json", snapshot)
        tex, notes = render_deck(snapshot)
        base = "coloring-research-" + key
        source = directory / (base + ".tex")
        source.write_text(tex)
        (directory / (base + ".md")).write_text(notes)
        with (directory / "build.log").open("w") as stream:
            subprocess.run(
                [
                    self.config["tectonic"],
                    "--only-cached",
                    "--untrusted",
                    "--keep-logs",
                    "--outdir",
                    str(directory),
                    str(source),
                ],
                check=True,
                stdout=stream,
                stderr=subprocess.STDOUT,
                timeout=180,
            )
        pdf = source.with_suffix(".pdf")
        if not pdf.read_bytes().startswith(b"%PDF-"):
            raise RuntimeError("Weekly PDF missing or invalid")
        pending = {
            "key": key,
            "directory": str(directory),
            "assets": {
                p.name: digest(p) for p in (source, pdf, source.with_suffix(".md"))
            },
            "title": f"Coloring research weekly rundown — {key}",
            "body": f"Research presentation covering **{snapshot['start_label']} to {snapshot['end_label']}**.\n\n"
            "The slides reproduce the latest researcher-written narrative in each research area. Full notes preserve every eligible completed briefing, including calculations, measured results, losses, review qualifications and next questions. Later reviews can restrict earlier implementation claims.\n\n"
            "This presentation uses saved evidence and makes no new scientific admission. If no new briefing exists, the PDF says so explicitly. Weekly delivery is Thursday at **09:00 America/Montreal**; twelve-hour summaries and urgent alerts continue separately.",
            "marker": f"<!-- logique-weekly:{key} -->",
        }
        save(directory / "presentation.json", pending)
        return pending

    def deliver_pending(self):
        pending = self.state["pending"]
        receipt = self.remote.deliver(pending)
        receipt.update(directory=pending["directory"], sent_at=time.time())
        if pending["key"].startswith("preview-"):
            self.state["previews"].append(receipt)
        else:
            self.state["delivered"][pending["key"]] = receipt
        self.state.pop("pending")
        save(self.path, self.state)
        return receipt

    def tick(self, now: datetime | None = None):
        if (self.directory / "WEEKLY_PAUSE").exists():
            return "paused"
        if "pending" in self.state:
            self.deliver_pending()
            return "sent_reconciled"
        due = due_date(now or datetime.now().astimezone(), self.config)
        if due is None or due.date().isoformat() in self.state["delivered"]:
            return "waiting_for_thursday"
        self.state["pending"] = self.build(due, due.date().isoformat())
        save(self.path, self.state)
        self.deliver_pending()
        return "sent"

    def run(self, once=False):
        with locked(self.directory / "weekly.lock"):
            while not self.stop.is_set():
                try:
                    self.state["last_check_result"] = self.tick()
                    self.state.pop("last_error", None)
                except (
                    OSError,
                    ValueError,
                    KeyError,
                    RuntimeError,
                    subprocess.SubprocessError,
                ) as error:
                    self.state["last_check_result"] = "error"
                    self.state["last_error"] = {
                        "type": type(error).__name__,
                        "at": time.time(),
                    }
                self.state["last_check_at"] = time.time()
                save(self.path, self.state)
                print(
                    datetime.now(ZoneInfo(self.config["timezone"])).isoformat(),
                    self.state["last_check_result"],
                    flush=True,
                )
                if once:
                    return
                self.stop.wait(60)


def main():
    """Build a preview or run the weekly scheduler, with independent pause control."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "action", choices=("run", "preview", "status", "pause", "unpause")
    )
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--publish", action="store_true")
    parser.add_argument("--once", action="store_true")
    args = parser.parse_args()
    if args.action in ("pause", "unpause"):
        marker = args.config.resolve().parent / "WEEKLY_PAUSE"
        marker.touch() if args.action == "pause" else marker.unlink(missing_ok=True)
        return
    weekly = Weekly(args.config)
    if args.action == "status":
        print(json.dumps(weekly.state, indent=2))
    elif args.action == "preview":
        with locked(weekly.directory / "weekly.lock"):
            if "pending" in weekly.state:
                raise RuntimeError("Resolve pending delivery before preview")
            now = datetime.now(ZoneInfo(weekly.config["timezone"]))
            pending = weekly.build(now, "preview-" + now.date().isoformat())
            if args.publish:
                weekly.state["pending"] = pending
                save(weekly.path, weekly.state)
                print(json.dumps(weekly.deliver_pending(), indent=2))
            else:
                print(pending["directory"])
    else:
        for sig in (signal.SIGINT, signal.SIGTERM):
            signal.signal(sig, lambda *_: weekly.stop.set())
        weekly.run(once=args.once)


if __name__ == "__main__":
    main()

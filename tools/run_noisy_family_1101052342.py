"""Execute fresh missing-only requests through the admitted selector/supervisor.

This task runner changes no sampling, lowering, routing or noise implementation.
It prioritizes breadth at j=0, then increasing iteration and ideal width. A
timeout blocks higher iterations of that case/seed for this bounded batch.
Every original request remains in the full status ledger, including exclusions.
"""

from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import time

from logique.benchmarks import noisy_iterations as noisy
from logique.paths import new_dump_directory

ROOT = Path("/Users/mar/codex-work/logique")
HERE = Path(__file__).resolve().parents[1]
PYTHON = ROOT / ".venv/bin/python"
NOISY = ROOT / (
    "dump/1029204240-coloring-dispatch-continuation/worktrees/"
    "noisy-channel-repair/dump/1029210538-noisy-channel-repair/"
    "runs/1029210741-noisy-iteration-study"
)
NATIVE = ROOT / (
    "dump/1025024643-coloring-integration-gate/worktrees/native-contract/"
    "dump/1025025511-native-contract/build/boolean_synthesis"
)
THREADS = {
    key: "1"
    for key in (
        "OMP_NUM_THREADS",
        "OPENBLAS_NUM_THREADS",
        "MKL_NUM_THREADS",
        "VECLIB_MAXIMUM_THREADS",
        "NUMEXPR_NUM_THREADS",
        "RAYON_NUM_THREADS",
        "QISKIT_NUM_PROCS",
        "CMAKE_BUILD_PARALLEL_LEVEL",
    )
} | {"QISKIT_PARALLEL": "FALSE"}


def digest(path: Path) -> str:
    """Hash immutable or exclusively owned bytes."""
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write(path: Path, value) -> None:
    """Atomically checkpoint task-owned JSON."""
    noisy._write(path, value)


def preparer():
    """Load the exact inherited admitted request-ledger helper."""
    spec = importlib.util.spec_from_file_location(
        "remaining", HERE / "tools/run_noisy_remaining.py"
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def resume_ledger(rows: list[dict], previous: list[dict]) -> None:
    """Carry exact statuses; reopen only budget rows with no attempted result."""

    def key(row):
        return row["name"], row["seed_transpiler"], row["iterations"]

    old = {key(row): row for row in previous}
    if len(old) != len(previous) or set(old) != {key(row) for row in rows}:
        raise ValueError("Prior ledger must contain the same unique request set")
    for row in rows:
        saved = old[key(row)]
        row.update(saved)
        if saved["status"] == "not_launched_budget":
            if saved.get("result"):
                raise ValueError(
                    "A budget-deferred row cannot have an attempted result"
                )
            row.update(
                status="unrun_requires_fresh_pre_aer_validation",
                reason="Never launched in prior batch; selected for fresh bounded continuation",
                previous_status="not_launched_budget",
            )


def prepare(config: dict, prior: Path | None = None) -> Path:
    """Authenticate frozen inputs and save all805 statuses before execution."""
    noisy.validate_config(config)
    assert Path(noisy.__file__).resolve() == (
        HERE / "src/logique/benchmarks/noisy_iterations.py"
    )
    assert digest(NATIVE) == (
        "6aa7357d2f64202584b14b0a14f8fb183379faf5907723cd24bd838b9be14a9a"
    )
    helper = preparer()
    pilot = Path(config["ideal_pilot"])
    ideal = helper.verified_manifest(pilot, noisy.PILOT_HASH)
    helper.verified_manifest(NOISY, helper.NOISY_HASH)
    rows = helper.remaining_ledger(ideal, pilot, NOISY)
    assert len(rows) == 805
    assert (
        sum(r["disposition"] == "admitted_observation_do_not_rerun" for r in rows) == 28
    )
    references = {
        c["name"]: json.loads((pilot / c["name"] / "result.json").read_text())
        for c in ideal["cases"]
    }
    for row in rows:
        row["status"] = row["disposition"]
        row["reason"] = {
            "admitted_observation_do_not_rerun": "Exact original28 observation admission",
            "excluded_21_active_wires": "Historical seed23/j2 active-width exclusion retained",
            "blocked_pending_selector_review": "Separate retry owner;120s timeout; resource admission required",
            "excluded_original_structure_width": "Original50 C5 structure exclusions; best-fit noise adapter not admitted here",
            "unrun_requires_fresh_pre_aer_validation": "Not launched in this bounded batch yet",
        }[row["disposition"]]
    if prior is not None:
        old_rows = json.loads((prior / "ledger.json").read_text())
        resume_ledger(rows, old_rows)
        for path in prior.glob("*.request.json"):
            request = json.loads(path.read_text())
            key = (request["name"], request["seed"], request["iterations"][0])
            row = next(
                r
                for r in rows
                if (r["name"], r["seed_transpiler"], r["iterations"]) == key
            )
            if row["status"] == "unrun_requires_fresh_pre_aer_validation":
                row.update(
                    status="interrupted_scope_stop",
                    reason="Attempted at controlled stop; no repeat in this batch",
                    result=str(Path(request["output"]) / "result.json"),
                )
    eligible = [
        r
        for r in rows
        if r["status"] == "unrun_requires_fresh_pre_aer_validation"
        and (
            r["name"].startswith("path")
            or r["name"].startswith("K3_k3_")
            or r["name"].startswith("P4_k3_")
        )
    ]
    eligible.sort(
        key=lambda r: (
            r["iterations"],
            references[r["name"]]["construction"]["width"],
            r["name"],
            r["seed_transpiler"],
        )
    )
    output = new_dump_directory("noisy-family-coverage")
    write(output / "config.json", config)
    write(output / "initial-ledger.json", rows)
    write(output / "plan.json", eligible)
    source_paths = list((HERE / "src/logique").rglob("*.py")) + [
        Path(__file__),
        HERE / "tools/run_noisy_remaining.py",
    ]
    write(
        output / "intake.json",
        {
            "task": "noisy-family-coverage-1101052342",
            "session": os.environ.get("CODEX_THREAD_ID"),
            "head": subprocess.check_output(
                ["git", "rev-parse", "HEAD"], text=True
            ).strip(),
            "source_hashes": {
                str(p.relative_to(HERE)): digest(p) for p in source_paths
            },
            "input_manifests": {
                str(pilot): noisy.PILOT_HASH,
                str(NOISY): helper.NOISY_HASH,
            },
            "native": {"path": str(NATIVE), "sha256": digest(NATIVE), "invoked": False},
            "limits": {
                "child_seconds": 120,
                "numerical_seconds": 900,
                "sampling_schedule_seconds": config["budget_seconds"],
                "process_bytes": 6 * 1024**3,
                "statevector_wires": 18,
                "operator_wires": 5,
                "local_channel_wires": 2,
                "density_matrix": False,
                "threads": THREADS,
                "rss": "sampled direct child kill, not hard cap/group peak; wait4 may include reaped descendants",
            },
            "ordering": "j ascending, ideal width ascending, name, five seeds ascending",
            "prior_checkpoint": str(prior) if prior else None,
            "independent_review": "pending for new runner, inheritance and observations",
        },
    )
    return output


def execute(output: Path) -> None:
    """Run serial singleton subsets without repeating completed or timed-out work."""
    config = json.loads((output / "config.json").read_text())
    rows = json.loads((output / "initial-ledger.json").read_text())
    plan = json.loads((output / "plan.json").read_text())
    index = {(r["name"], r["seed_transpiler"], r["iterations"]): r for r in rows}
    blocked = {
        (r["name"], r["seed_transpiler"])
        for r in rows
        if r["status"]
        in ("timeout", "failed", "failed_routed_validation", "compact_noise_infeasible")
    }
    receipts = []
    started = time.monotonic()
    env = (
        dict(os.environ)
        | THREADS
        | {
            "PYTHONPATH": str(HERE / "src"),
            "LOGIQUE_NATIVE_EXECUTABLE": str(NATIVE),
        }
    )
    # Probe host visibility before launching any scientific child.
    subprocess.run(
        ["ps", "-o", "rss=", "-p", str(os.getpid())], check=True, capture_output=True
    )
    from logique.benchmarks.routing import default_backend

    backend = default_backend()
    calibration = {}
    for kind, filename in (
        ("properties", backend.props_filename),
        ("configuration", backend.conf_filename),
    ):
        actual = Path(backend.dirname) / filename
        frozen = NOISY / "backend" / f"{kind}.json"
        assert digest(actual) == digest(frozen)
        calibration[kind] = digest(actual)
    write(output / "calibration-preflight.json", calibration)
    for planned in plan:
        key = (planned["name"], planned["seed_transpiler"], planned["iterations"])
        row = index[key]
        pair = key[:2]
        remaining = config["budget_seconds"] - (time.monotonic() - started)
        if pair in blocked:
            row.update(
                status="deferred_after_failed_lower_iteration",
                reason="No repeated timeout/failure loop for this case/seed",
            )
            continue
        if remaining < config["timeout_seconds"]:
            row.update(
                status="not_launched_budget",
                reason="Less than one full child window remains; fresh bounded successor required",
            )
            continue
        label = f"{key[0]}_seed{key[1]}_j{key[2]}"
        request = {
            "config": config,
            "name": key[0],
            "seed": key[1],
            "iterations": [key[2]],
            "output": str(output / label),
        }
        path = output / f"{label}.request.json"
        write(path, request)
        command = [
            str(PYTHON),
            "-m",
            "logique.benchmarks.noisy_iterations",
            "--child",
            str(path),
        ]
        receipt = noisy.supervise(
            command,
            output / f"{label}.log",
            env,
            min(120, remaining),
            config["memory_bytes"],
        )
        receipts.append(receipt)
        result_path = output / label / "result.json"
        row.update(
            status=receipt["status"],
            reason="See exclusive child receipt",
            result=str(result_path),
        )
        if result_path.exists():
            record = json.loads(result_path.read_text())
            # Keep an exact pre-reconciliation copy for timeout/partial review.
            (output / f"{label}.raw-result.json").write_bytes(result_path.read_bytes())
            noisy.finalize_result(record, receipt["status"], config["shots"])
            write(result_path, record)
            actual = record["rows"][0]
            row.update(
                status=actual["status"],
                reason=actual.get("reason", receipt["status"]),
                result_sha256=digest(result_path),
            )
        if receipt["status"] != "finished" or row["status"] != "complete":
            blocked.add(pair)
        checkpoint(output, rows, receipts, started)
        print(label, row["status"], round(receipt["seconds"], 3), flush=True)
    checkpoint(output, rows, receipts, started)


def checkpoint(
    output: Path, rows: list[dict], receipts: list[dict], started: float
) -> None:
    """Retain the777 remaining statuses plus the original28 separately."""
    write(output / "ledger.json", rows)
    write(
        output / "remaining-ledger.json",
        [r for r in rows if r["disposition"] != "admitted_observation_do_not_rerun"],
    )
    write(
        output / "checkpoint.json",
        {
            "task": "noisy-family-coverage-1101052342",
            "independent_admission": False,
            "requests": 805,
            "previously_admitted": 28,
            "new_completed_pending_review": sum(
                r["status"] == "complete" for r in rows
            ),
            "statuses": dict(Counter(r["status"] for r in rows)),
            "elapsed_seconds": time.monotonic() - started,
            "child_seconds": sum(r["seconds"] for r in receipts),
            "receipts": receipts,
            "next": "Independent exact runner/inheritance/evidence review, then missing-only successor; retry and C5 owned separately",
        },
    )


def main() -> None:
    """Prepare or execute one exclusive bounded evidence directory."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path)
    parser.add_argument("--execute", type=Path)
    parser.add_argument("--prior", type=Path)
    args = parser.parse_args()
    assert sys.executable == str(PYTHON)
    if args.execute:
        execute(args.execute.resolve())
    else:
        print(prepare(json.loads(args.config.read_text()), args.prior).resolve())


if __name__ == "__main__":
    main()

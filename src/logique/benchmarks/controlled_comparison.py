"""Serial, bounded comparison ledger and saved-circuit recount.

This supervisor launches ordinary local numerical children only. It never
launches models. Resource observations are sampled process-group RSS and wait4
OS accounting; neither is a proof of an instantaneous hard memory ceiling.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import signal
import subprocess
import sys
import time

from logique.paths import new_dump_directory

GRAPHS = (
    "K3",
    "K5",
    "myciel3",
    "grid6",
    "K10",
    "K20",
    "myciel4",
    "myciel5",
    "2-Insertions_3",
)
NATIVE_SHA256 = "6aa7357d2f64202584b14b0a14f8fb183379faf5907723cd24bd838b9be14a9a"
BUDGET = {
    "child_seconds": 30,
    "cumulative_seconds": 900,
    "group_rss_bytes": 6 * 1024**3,
    "max_data_bits": 256,
    "max_vertices": 64,
    "max_edges": 256,
    "max_component_qubits": 4096,
    "max_component_instructions": 50000,
    "max_component_depth": 50000,
    "common_max_data_bits": 21,
}


def sha256(path: Path) -> str:
    """Hash one explicitly selected input or artifact."""
    return hashlib.sha256(path.read_bytes()).hexdigest()


def witnesses(problem) -> dict:
    """Find a bounded deterministic DSATUR witness and independent negatives.

    The fixed node budget prevents an unbounded coloring search. Failure to find
    a witness is unknown, never unsatisfiability. Precolors must be removed first.
    """
    from logique.coloring import encode_coloring

    encoding = encode_coloring(problem)
    adjacency = {v: set() for v in problem.vertices}
    for u, v in problem.edges:
        adjacency[u].add(v)
        adjacency[v].add(u)
    assigned: dict[int, int] = {}
    visits = 0

    def search():
        nonlocal visits
        visits += 1
        if visits > 10000 or any(v in adjacency[v] for v in adjacency):
            return False
        if len(assigned) == len(problem.vertices):
            return True
        v = max(
            (v for v in problem.vertices if v not in assigned),
            key=lambda v: (
                len({assigned[u] for u in adjacency[v] if u in assigned}),
                len(adjacency[v]),
                -v,
            ),
        )
        forbidden = {assigned[u] for u in adjacency[v] if u in assigned}
        for color in range(min(problem.colors, max(assigned.values(), default=-1) + 2)):
            if color not in forbidden:
                assigned[v] = color
                if search():
                    return True
                del assigned[v]
        return False

    def basis(colors):
        return sum(colors[v] << wires[0] for v, wires in encoding.input_mapping.items())

    positive = basis(assigned) if search() else None
    if positive is not None and not problem.is_valid(encoding.decode(positive)):
        raise AssertionError("Witness search returned an invalid coloring")
    edge = 0 if problem.edges else None
    invalid = (
        (problem.colors << 0) if problem.colors < 1 << encoding.bits_per_color else None
    )
    return {
        "positive": positive,
        "edge_violation": edge,
        "invalid_code": invalid,
        "boundary": (1 << encoding.input_count) - 1,
        "search_nodes": visits,
        "search_node_cap": 10000,
        "positive_status": "verified" if positive is not None else "unknown",
    }


def child(request: dict) -> None:
    """Save logical components, then separately attempt admitted common lowering."""
    from logique.benchmarks.coloring_study import run_coloring_study

    config = request["config"]
    base = Path(request["directory"])
    # run_coloring_study owns timestamped creation. It must receive a new path.
    from logique.paths import dump_directory_name

    logical = run_coloring_study(
        {**config, "output": str(base / dump_directory_name("logical"))}
    )
    receipt = {
        "logical": str(logical),
        "common": None,
        "common_status": "open_outside_restoring_subset",
    }
    (base / "child.json").write_text(json.dumps(receipt, indent=2) + "\n")
    if request["common_eligible"]:
        common = run_coloring_study(
            {
                **config,
                "output": str(base / dump_directory_name("common")),
                "common_basis": True,
                "optimization_level": 0,
                "mcx_decomposition": "clean_tree",
                "mcx_workspace": "fresh_zero",
            }
        )
        receipt.update(common=str(common), common_status="attempted")
        (base / "child.json").write_text(json.dumps(receipt, indent=2) + "\n")


def supervise(command: list[str], directory: Path, seconds: float) -> dict:
    """Observe completion before deadline and clean the owned process group.

    ps failures leave group memory unavailable. wait4 high-water can include
    reaped descendants; it is never called isolated direct-child RSS.
    """
    started = time.monotonic()
    peak = None
    memory_error = None
    reason = None
    with (
        (directory / "stdout.log").open("x") as out,
        (directory / "stderr.log").open("x") as err,
    ):
        process = subprocess.Popen(
            command, stdout=out, stderr=err, start_new_session=True
        )
        while True:
            now = time.monotonic()
            pid, status, usage = os.wait4(process.pid, os.WNOHANG)
            if now - started >= seconds:
                reason = "timeout"
            if pid:
                process.returncode = os.waitstatus_to_exitcode(status)
                break
            if reason:
                os.killpg(process.pid, signal.SIGKILL)
                _, status, usage = os.wait4(process.pid, 0)
                process.returncode = os.waitstatus_to_exitcode(status)
                break
            try:
                observed = subprocess.run(
                    ["ps", "-axo", "pgid=,rss="],
                    capture_output=True,
                    text=True,
                    timeout=min(0.5, max(0.001, seconds - (now - started))),
                )
                if observed.returncode:
                    memory_error = observed.stderr.strip()
                else:
                    rss = sum(
                        int(parts[1]) * 1024
                        for line in observed.stdout.splitlines()
                        if len(parts := line.split()) == 2
                        and int(parts[0]) == process.pid
                    )
                    peak = max(peak or 0, rss)
                    if rss >= BUDGET["group_rss_bytes"]:
                        reason = "memory_budget"
            except (subprocess.TimeoutExpired, OSError) as error:
                memory_error = (
                    f"ps sampling unavailable: {type(error).__name__}: {error}"
                )
            time.sleep(min(0.02, max(0, seconds - (time.monotonic() - started))))
        # Leader was reaped above. Terminate any descendants still in our group.
        try:
            os.killpg(process.pid, signal.SIGKILL)
        except ProcessLookupError:
            pass
    elapsed = time.monotonic() - started
    if elapsed >= seconds and reason is None:
        reason = "timeout"
    return {
        "command": command,
        "seconds": elapsed,
        "timeout_seconds": seconds,
        "returncode": process.returncode,
        "status": reason or ("complete" if process.returncode == 0 else "failed"),
        "sampled_group_peak_rss_bytes": peak,
        "memory_sampling_error": memory_error,
        "wait4_high_water_bytes": int(
            usage.ru_maxrss * (1 if sys.platform == "darwin" else 1024)
        ),
        "wait4_scope": "OS waited-child high-water; may include reaped descendants; not isolated or simultaneous group RSS",
    }


def requested_ledger(manifest: dict) -> list[dict]:
    """Expand requested cases and open control axes without fabricating costs."""
    rows = []
    components = ("raw", "preparation", "oracle", "diffusion", "search")
    for entry in manifest["ledger"]:
        context = {
            key: entry[key]
            for key in (
                "benchmark",
                "input_sha256",
                "method",
                "optimization_profile",
                "iteration",
                "seed",
            )
        }
        for regime in entry["regimes"]:
            for level in ("logical", "restoring_mcx", "common_basis"):
                available = [
                    case
                    for run in entry.get("case_results", [])
                    if ("logical" in Path(run["path"]).parent.name)
                    == (level == "logical")
                    for case in run["cases"]
                    if case["regime"] == regime
                ]
                case = available[0] if available else {}
                status = (
                    entry["status"]
                    if entry["status"] != "complete"
                    else case.get("status", entry["common_status"])
                )
                reason = entry.get("reason") or case.get("reason")
                for component in components:
                    rows.append(
                        {
                            **context,
                            "regime": regime,
                            "component": component,
                            "metric_level": level,
                            "target": "unrouted",
                            "precision": "native_float_no_rotation_synthesis",
                            "mcx_method": (
                                "qiskit_default_uncontrolled"
                                if level == "logical"
                                else "clean_tree"
                            ),
                            "status": status,
                            "reason": reason,
                            "row_scope": "requested_component",
                            "evidence_directory": entry.get("directory"),
                        }
                    )
            # Open axes are obligations, not an invented Cartesian experiment.
            for profile in ("mc_reduction", "cut_esop_balancing"):
                rows.append(
                    {
                        **context,
                        "optimization_profile": profile,
                        "regime": regime,
                        "component": "all_five",
                        "metric_level": "logical_and_common_basis",
                        "status": "open_unsupported_profile",
                        "row_scope": "open_control_axis",
                    }
                )
            for seed in (11, 23, 37, 41, 53):
                rows.append(
                    {
                        **context,
                        "regime": regime,
                        "seed": seed,
                        "target": "FakeTorino",
                        "component": "all_five",
                        "metric_level": "routed",
                        "status": "open_unexecuted_target",
                        "row_scope": "open_control_axis",
                    }
                )
            for precision in (1e-2, 1e-3, 1e-4):
                rows.append(
                    {
                        **context,
                        "regime": regime,
                        "precision": precision,
                        "component": "all_five",
                        "metric_level": "static_fault_tolerant",
                        "status": "open_unexecuted_precision",
                        "row_scope": "open_control_axis",
                    }
                )
    # Unsupported-profile rows were encountered in each implemented-profile stratum.
    return list({json.dumps(row, sort_keys=True): row for row in rows}.values())


def recount(output: Path) -> dict:
    """Reproduce every published row from hash-checked saved QPY artifacts."""
    import pandas as pd
    from qiskit import qpy
    from .metrics import circuit_metrics
    from .comparison import strongest_baseline_comparison

    rows = []
    checked = 0
    batch = json.loads((output / "batch.json").read_text())
    pd.DataFrame(requested_ledger(batch)).to_csv(
        output / "requested-ledger.csv", index=False
    )
    completed = {
        entry.get("directory")
        for entry in batch["ledger"]
        if entry["status"] == "complete"
    }
    for path in sorted(output.glob("case-*/*/summary.csv")):
        if path.parent.parent.name not in completed:
            continue
        manifest = json.loads((path.parent / "run.json").read_text())
        frame = pd.read_csv(path)
        for case in manifest["cases"]:
            if case["status"] != "complete":
                continue
            for artifact, record in case["artifact_statistics"].items():
                artifact_path = path.parent / artifact
                if sha256(artifact_path) != record["sha256"]:
                    raise AssertionError(f"Changed saved artifact: {artifact_path}")
                with artifact_path.open("rb") as stream:
                    circuit = qpy.load(stream)[0]
                actual = circuit_metrics(circuit)
                if any(
                    actual[key] != record["metrics"][key]
                    for key in ("qubits", "gates", "depth", "gate_types")
                ):
                    raise AssertionError(f"Saved metric mismatch: {artifact_path}")
                selected = frame[frame.artifact == artifact]
                if len(selected) != 1 or any(
                    int(selected.iloc[0][key]) != actual[key]
                    for key in ("qubits", "gates", "depth")
                ):
                    raise AssertionError(f"CSV metric mismatch: {artifact_path}")
                checked += 1
        frame["artifact"] = frame.artifact.map(
            lambda name: str(path.parent.relative_to(output) / name)
        )
        rows.append(frame)
    if rows:
        frame = pd.concat(rows, ignore_index=True)
        frame.to_csv(output / "summary.csv", index=False)
        # Cases with no admitted baseline stay in the ledger, without an invented ratio.
        keys = [
            "benchmark",
            "regime",
            "component",
            "metric_level",
            "iteration",
            "seed",
            "optimization_profile",
            "mcx_method",
            "workspace_policy",
            "target",
            "precision",
        ]
        comparable = frame.groupby(keys, dropna=False).filter(
            lambda g: g.method.str.startswith("sb_").any()
        )
        if not comparable.empty:
            details, summary = strongest_baseline_comparison(comparable)
            details.to_csv(output / "strongest-details.csv", index=False)
            summary.to_csv(output / "strongest-summary.csv", index=False)
        unmatched = frame.merge(
            comparable[keys].drop_duplicates(), on=keys, how="left", indicator=True
        )
        unmatched[unmatched._merge == "left_only"].to_csv(
            output / "unmatched.csv", index=False
        )
    return {
        "saved_rows_recounted": checked,
        "row_count": sum(len(frame) for frame in rows),
    }


def run(root: Path) -> Path:
    """Execute the full requested ledger, retaining failures and open controls."""
    from logique.benchmarks.coloring_study import (
        STUDY_METHODS,
        STRUCTURE_METHODS,
        OPTIMIZATION_PROFILES,
    )
    from logique.coloring import ColoringProblem, read_dimacs, encode_coloring
    from .provenance import checkout_revision, environment, native_provenance

    native = native_provenance()
    if native["sha256"] != NATIVE_SHA256:
        raise ValueError("New experiments require the admitted private native hash")
    output = new_dump_directory("controlled-comparison")
    started = time.monotonic()
    ledger = []
    manifest = {
        "task": "controlled-comparison-study-1028023823",
        "budget": BUDGET,
        "native": native,
        "checkout": checkout_revision(root),
        "environment": environment(),
        "source_hashes": {
            str(path.relative_to(root)): sha256(path)
            for path in (
                root / "src/logique/benchmarks/controlled_comparison.py",
                root / "src/logique/benchmarks/coloring_study.py",
                root / "src/logique/benchmarks/comparison.py",
                root / "src/logique/benchmarks/costs.py",
                root / "src/logique/circuits/records.py",
                root / "src/logique/circuits/structure.py",
                root / "src/logique/synthesis/api.py",
                root / "src/logique/synthesis/native.py",
                root / "src/logique/synthesis/saha_belletti.py",
                root / "src/logique/coloring/encoding.py",
            )
        },
        "ledger": ledger,
        "full_study_open": {
            "profiles": ["mc_reduction", "cut_esop_balancing"],
            "targets": ["FakeTorino_five_seeds"],
            "precision": [1e-2, 1e-3, 1e-4],
            "reason": "not connected/admitted in this comparison; no substitute or default results",
        },
    }

    def save():
        (output / "batch.json").write_text(json.dumps(manifest, indent=2) + "\n")

    for graph in GRAPHS:
        source = root / f"datasets/graphs/benchmarks/{graph}.col"
        original = read_dimacs(source)
        problem = ColoringProblem(original.vertices, original.edges, original.colors)
        witness = witnesses(problem)
        n = encode_coloring(problem).input_count
        for profile in OPTIMIZATION_PROFILES:
            for method in (*STUDY_METHODS, *STRUCTURE_METHODS):
                entry = {
                    "benchmark": graph,
                    "input": str(source),
                    "input_sha256": sha256(source),
                    "method": method,
                    "optimization_profile": profile,
                    "regimes": ["R1", "R2", "R3"],
                    "iteration": 1,
                    "seed": 7,
                    "data_bits": n,
                    "witnesses": witness,
                    "removed_precolors": dict(original.precolored),
                    "input_order": "sorted vertices, contiguous LSB-first words",
                    "common_status": (
                        "eligible"
                        if n <= 21 and problem.colors <= 8
                        else "open_outside_restoring_subset"
                    ),
                }
                ledger.append(entry)
                remaining = (
                    BUDGET["cumulative_seconds"] - 120 - (time.monotonic() - started)
                )
                if (
                    n > BUDGET["max_data_bits"]
                    or len(problem.vertices) > BUDGET["max_vertices"]
                    or len(problem.edges) > BUDGET["max_edges"]
                ):
                    entry.update(
                        status="infeasible", reason="preallocation structural cap"
                    )
                elif witness["positive"] is None:
                    entry.update(
                        status="excluded",
                        reason="no verified positive witness; satisfiability unknown",
                    )
                elif remaining <= 0:
                    entry.update(
                        status="not_run_budget",
                        reason="cumulative wall deadline exhausted",
                    )
                else:
                    directory = output / f"case-{len(ledger):03d}"
                    directory.mkdir()
                    config = {
                        "kind": "coloring_study",
                        "inputs": [str(source)],
                        "methods": [method],
                        "regimes": ["R1", "R2", "R3"],
                        "iterations": [1],
                        "seeds": [7],
                        "optimization_profile": profile,
                        "remove_precolors": True,
                        "samples": 32,
                        "verification_assignments": {
                            str(source): list(
                                dict.fromkeys(
                                    v
                                    for key, v in witness.items()
                                    if key
                                    in (
                                        "positive",
                                        "edge_violation",
                                        "invalid_code",
                                        "boundary",
                                    )
                                    and v is not None
                                )
                            )
                        },
                        **{
                            key: BUDGET[key]
                            for key in (
                                "max_component_qubits",
                                "max_component_instructions",
                                "max_component_depth",
                            )
                        },
                    }
                    request = directory / "request.json"
                    request.write_text(
                        json.dumps(
                            {
                                "config": config,
                                "directory": str(directory),
                                "common_eligible": entry["common_status"] == "eligible",
                            },
                            indent=2,
                        )
                        + "\n"
                    )
                    command = [
                        sys.executable,
                        "-m",
                        "logique.benchmarks.controlled_comparison",
                        "--child",
                        str(request),
                    ]
                    entry.update(
                        directory=str(directory.relative_to(output)),
                        **supervise(
                            command, directory, min(remaining, BUDGET["child_seconds"])
                        ),
                    )
                if "directory" in entry:
                    entry["case_results"] = []
                    for result_path in sorted(
                        (output / entry["directory"]).glob("*/run.json")
                    ):
                        result = json.loads(result_path.read_text())
                        entry["case_results"].append(
                            {
                                "path": str(result_path.relative_to(output)),
                                "sha256": sha256(result_path),
                                "cases": [
                                    {
                                        key: case.get(key)
                                        for key in (
                                            "regime",
                                            "status",
                                            "reason",
                                            "oracle_construction",
                                            "validation",
                                            "profile_application",
                                        )
                                    }
                                    for case in result["cases"]
                                ],
                            }
                        )
                save()
    manifest.update(execution_seconds=time.monotonic() - started)
    save()
    recount_directory = output / "recount"
    recount_directory.mkdir()
    manifest["recount_process"] = supervise(
        [
            sys.executable,
            "-m",
            "logique.benchmarks.controlled_comparison",
            "--recount",
            str(output),
        ],
        recount_directory,
        min(
            120, max(0.001, BUDGET["cumulative_seconds"] - (time.monotonic() - started))
        ),
    )
    if manifest["recount_process"]["status"] == "complete":
        manifest["recount"] = json.loads((recount_directory / "stdout.log").read_text())
    manifest["total_seconds"] = time.monotonic() - started
    manifest["next_action"] = (
        "Independent exact-hash review; extend common lowering beyond admitted subset and connect CEC-checked optimization profiles before full freeze."
    )
    save()
    return output


def main():
    """Run the bounded study or its ordinary numerical child."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--child", type=Path)
    parser.add_argument("--recount", type=Path)
    args = parser.parse_args()
    if args.child:
        child(json.loads(args.child.read_text()))
    elif args.recount:
        print(json.dumps(recount(args.recount)))
    else:
        print(run(Path.cwd()))


if __name__ == "__main__":
    main()

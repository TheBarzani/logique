"""Private capped MC recipe adapter; independent review precedes production use."""

from __future__ import annotations

import hashlib
import json
import math
import os
from pathlib import Path
import signal
import subprocess
import time

from logique.paths import new_dump_directory

MC_PASSES = (
    "constant_fanin_1",
    "cleanup_1",
    "dont_cares_1",
    "cleanup_2",
    "refactoring",
    "cleanup_3",
    "xag_minmc_cut_rewriting",
    "cleanup_4",
    "constant_fanin_2",
    "cleanup_5",
    "dont_cares_2",
    "cleanup_6",
)
TWEEDLEDUM_REVISION = "a3cb238d132825b8e0367d5e96618c5753c1879a"


class MCOptimizationError(RuntimeError):
    """An unavailable or failed MC transformation with retained partial evidence."""

    def __init__(self, message: str, evidence: dict):
        super().__init__(message)
        self.mc_evidence = evidence


def _sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _truth(graph: dict) -> list[str]:
    """Evaluate capped positional graphs without native simulation helpers."""
    inputs, outputs, nodes = graph["inputs"], graph["outputs"], graph["nodes"]
    size = graph["size"]
    if (
        type(size) is not int
        or not 1 <= size <= 4096
        or len(nodes) > size
        or len(inputs) > 10
        or not 1 <= len(outputs) <= 16
    ):
        raise ValueError("MC graph exceeds supported caps")
    records = {n["id"]: n for n in nodes}
    if len(records) != len(nodes) or len(set(inputs)) != len(inputs):
        raise ValueError("Duplicate MC node or input")
    for node_id, node in records.items():
        if type(node_id) is not int or not 0 <= node_id < size:
            raise ValueError("Invalid MC node index")
        kind, fanins = node["kind"], node["fanins"]
        if kind not in {"constant", "input", "and", "xor"} or len(fanins) != (
            2 if kind in {"and", "xor"} else 0
        ):
            raise ValueError("Invalid MC node kind or fanin")
        if kind == "constant" and node_id != 0:
            raise ValueError("Invalid MC constant")
    if set(inputs) != {i for i, n in records.items() if n["kind"] == "input"}:
        raise ValueError("MC input list differs from input nodes")

    def edge(edge: dict) -> tuple[int, bool]:
        node_id, complement = edge["node"], edge["complement"]
        if type(node_id) is not int or node_id not in records:
            raise ValueError("Invalid MC edge")
        if type(complement) is not bool:
            raise ValueError("Invalid MC complement")
        return node_id, complement

    for node in nodes:
        for fanin in node["fanins"]:
            edge(fanin)
    for output in outputs:
        edge(output)
    # Iterative traversal supports the full node cap without Python recursion
    # depth imposing an undocumented second network-size limit.
    order: list[int] = []
    state: dict[int, int] = {}
    for output in outputs:
        pending = [(edge(output)[0], False)]
        while pending:
            node_id, expanded = pending.pop()
            if expanded:
                state[node_id] = 2
                order.append(node_id)
            elif state.get(node_id) == 2:
                continue
            elif state.get(node_id) == 1:
                raise ValueError("Cyclic MC graph")
            else:
                state[node_id] = 1
                pending.append((node_id, True))
                pending.extend((edge(f)[0], False) for f in records[node_id]["fanins"])
    tables = ["" for _ in outputs]
    for assignment in range(1 << len(inputs)):
        values = {v: bool((assignment >> i) & 1) for i, v in enumerate(inputs)}
        for node_id in order:
            node = records[node_id]
            if node["kind"] == "input":
                continue
            if node["kind"] == "constant":
                value = False
            else:
                fs = [values[i] ^ c for i, c in map(edge, node["fanins"])]
                value = fs[0] and fs[1] if node["kind"] == "and" else fs[0] ^ fs[1]
            values[node_id] = value
        for i, output in enumerate(outputs):
            node_id, complement = edge(output)
            tables[i] += str(int(values[node_id] ^ complement))
    return tables


def _validate(events: list[dict]) -> str:
    expected = ("original", *MC_PASSES)
    order = [("snapshot", "original")]
    for boundary in expected:
        if boundary != "original":
            order.append(("started", boundary))
        order.extend(
            (kind, boundary) for kind in ("snapshot", "serialization", "checked")
        )
    order.append(("complete", None))
    if (
        not all(isinstance(e, dict) for e in events)
        or [(e.get("kind"), e.get("boundary")) for e in events] != order
    ):
        raise ValueError("Incomplete or out-of-order MC recipe evidence")
    checked = [e for e in events if e.get("kind") == "checked"]
    snapshots = [e for e in events if e.get("kind") == "snapshot"]
    serialized = [e for e in events if e.get("kind") == "serialization"]
    started = [e for e in events if e.get("kind") == "started"]
    if (
        [e.get("boundary") for e in checked] != list(expected)
        or [e.get("boundary") for e in serialized] != list(expected)
        or [e.get("boundary") for e in started] != list(MC_PASSES)
        # The original snapshot precedes caps, and checkpoint saves it again.
        or [e.get("boundary") for e in snapshots] != ["original", *expected]
        or any(e.get("kind") == "failure" for e in events)
        or events[-1] != {"kind": "complete", "passes": 12}
    ):
        raise ValueError("Incomplete MC recipe evidence")
    original = _truth(snapshots[0]["graph"])
    arity = len(snapshots[0]["graph"]["inputs"])
    for record, snapshot, export in zip(checked, snapshots[1:], serialized):
        if (
            any(
                record.get(k) is not True
                for k in (
                    "equivalent_original",
                    "equivalent_previous",
                    "serialization_equivalent",
                )
            )
            or record.get("cec") != "exhaustive_positional"
            or record.get("assignments") != 1 << arity
            or record.get("truth") != original
            or not isinstance(export.get("verilog"), str)
            or len(snapshot["graph"]["inputs"]) != arity
            or len(record["readback_graph"]["inputs"]) != arity
            or _truth(snapshot["graph"]) != original
            or _truth(record["readback_graph"]) != original
        ):
            raise ValueError("MC original/pass/serialization evidence mismatch")
    return serialized[-1]["verilog"]


def reduce_mc_verilog(
    source: str | Path,
    *,
    executable: str | Path,
    artifacts: str | Path | None = None,
    timeout: float = 120,
) -> dict:
    """Run all twelve exact bundled boundaries with persisted partial evidence.

    This separate research adapter does not enable a production profile. Inputs
    are positional (including unused inputs); outputs retain order and duplicates.
    The supported existing combinational Verilog frontend is capped at ten
    inputs, 4096 nodes, sixteen outputs and one MiB source. Parsing and optimizer
    internals need an outer memory budget; these caps precede CEC truth tables.
    ``artifacts`` must be a new directory inside the caller's timestamped run.
    Timeouts kill the process group and retain flushed JSONL, source and stderr.
    """
    if (
        isinstance(timeout, bool)
        or not isinstance(timeout, (int, float))
        or not math.isfinite(timeout)
        or not 0 < timeout <= 120
    ):
        raise ValueError("timeout must be finite and in (0, 120] seconds")
    source, tool = Path(source).resolve(), Path(executable).resolve()
    if source.suffix != ".v" or not source.is_file():
        raise ValueError("source must be an existing .v file")
    if source.stat().st_size > 1048576:
        raise ValueError("MC source exceeds one MiB")
    data = source.read_bytes()
    if len(data) > 1048576:
        raise ValueError("MC source exceeds one MiB")
    build = json.loads((tool.parent / "build_provenance.json").read_text())
    if (
        build.get("tweedledum_revision") != TWEEDLEDUM_REVISION
        or build.get("dependency_sources_clean") is not True
    ):
        raise ValueError("MC build is not from the clean pinned dependency")
    destination = (
        new_dump_directory("mc-recipe")
        if artifacts is None
        else Path(artifacts).resolve()
    )
    if artifacts is not None:
        destination.mkdir(parents=True, exist_ok=False)
    request = json.dumps({"verilog": data.decode()}).encode()
    (destination / "source.v").write_bytes(data)
    (destination / "request.json").write_bytes(request)
    evidence = {
        "source_sha256": _sha(data),
        "native": {"sha256": _sha(tool.read_bytes()), "build": build},
        "artifacts": str(destination),
        "events": [],
        "timeout_seconds": timeout,
    }
    process = None
    start = time.monotonic()
    try:
        env = os.environ.copy()
        for key in (
            "OMP_NUM_THREADS",
            "OPENBLAS_NUM_THREADS",
            "MKL_NUM_THREADS",
            "VECLIB_MAXIMUM_THREADS",
            "NUMEXPR_NUM_THREADS",
            "RAYON_NUM_THREADS",
            "QISKIT_NUM_PROCS",
        ):
            env[key] = "1"
        with (
            (destination / "stdout.jsonl").open("xb") as stdout,
            (destination / "stderr.txt").open("xb") as stderr,
        ):
            process = subprocess.Popen(
                [str(tool)],
                stdin=subprocess.PIPE,
                stdout=stdout,
                stderr=stderr,
                env=env,
                start_new_session=True,
            )
            process.communicate(request, timeout=timeout)
        evidence["exit_code"] = process.returncode
        for line in (
            (destination / "stdout.jsonl").read_text(errors="replace").splitlines()
        ):
            evidence["events"].append(json.loads(line))
        if process.returncode:
            raise ValueError("Private MC tool failed; inspect retained failure events")
        evidence["verilog"] = _validate(evidence["events"])
        evidence["optimized_sha256"] = _sha(evidence["verilog"].encode())
        evidence["status"] = "complete_pending_independent_review"
    except BaseException as error:
        if process is not None and process.poll() is None:
            try:
                os.killpg(process.pid, signal.SIGKILL)
            except ProcessLookupError:
                pass
            process.wait()
        evidence["exit_code"] = process.returncode if process else None
        evidence["error"] = {"type": type(error).__name__, "message": str(error)}
        evidence["status"] = "failed"
        # Decode every complete flushed event even when the last line is partial.
        evidence["events"] = []
        for line in (
            (destination / "stdout.jsonl").read_text(errors="replace").splitlines()
        ):
            try:
                evidence["events"].append(json.loads(line))
            except json.JSONDecodeError:
                break
        if isinstance(error, (KeyboardInterrupt, SystemExit)):
            raise
        raise MCOptimizationError(str(error), evidence) from error
    finally:
        evidence["seconds"] = time.monotonic() - start
        temporary = destination / "evidence.json.tmp"
        temporary.write_text(json.dumps(evidence, indent=2))
        temporary.replace(destination / "evidence.json")
    return evidence

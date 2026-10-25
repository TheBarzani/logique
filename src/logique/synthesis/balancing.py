"""Explicit standalone Mockturtle balancing with per-pass equivalence checks."""

import hashlib
import json
import math
import os
from pathlib import Path
import shutil
import subprocess
from collections.abc import Sequence

BALANCING_PASSES = ("xag_balance", "algebraic", "esop")


def build_balancer(
    source: str | Path, *, build: str | Path | None = None, jobs: int = 1
) -> Path:
    """Build the separate pinned Mockturtle tool without touching dependencies."""
    source = Path(source).resolve()
    destination = Path(build).resolve() if build else source / "build"
    if type(jobs) is not int or jobs < 1:
        raise ValueError("jobs must be a positive integer")
    subprocess.run(
        [
            "cmake",
            "-S",
            str(source),
            "-B",
            str(destination),
            "-DCMAKE_BUILD_TYPE=Release",
        ],
        check=True,
    )
    subprocess.run(["cmake", "--build", str(destination), "-j", str(jobs)], check=True)
    return destination / "boolean_balance"


def optimize_verilog(
    source: str | Path,
    passes: Sequence[str] = ("xag_balance",),
    *,
    executable: str | Path | None = None,
    timeout: float = 180,
    cec_conflict_limit: int = 1_000_000,
) -> dict:
    """Return optimized Verilog, structural statistics and checked provenance.

    Each requested pass and the Verilog serialization are SAT-equivalence
    checked. A timeout, unknown result or changed function is a failure, never
    an optimization with zero cost. Primary inputs retain their index order;
    generated Verilog names may differ. An empty pass sequence performs only
    common dangling-node cleanup and serialization checks.
    """
    if not isinstance(passes, Sequence) or isinstance(passes, str):
        raise ValueError(f"passes must be a sequence chosen from {BALANCING_PASSES}")
    if any(p not in BALANCING_PASSES for p in passes):
        raise ValueError(f"passes must be a sequence chosen from {BALANCING_PASSES}")
    if (
        isinstance(timeout, bool)
        or not isinstance(timeout, (int, float))
        or not math.isfinite(timeout)
        or timeout <= 0
    ):
        raise ValueError("timeout must be finite and positive")
    if type(cec_conflict_limit) is not int or not 0 <= cec_conflict_limit < 1 << 32:
        raise ValueError("cec_conflict_limit must be a nonnegative 32-bit integer")
    source = Path(source).resolve()
    if source.suffix != ".v" or not source.is_file():
        raise ValueError("source must be an existing combinational Verilog .v file")
    selected = (
        executable
        or os.environ.get("LOGIQUE_BALANCER_EXECUTABLE")
        or shutil.which("boolean_balance")
    )
    if selected is None or not Path(selected).expanduser().is_file():
        raise FileNotFoundError(
            "Build with logique native balance-build --source external/native/boolean_balance; "
            "set LOGIQUE_BALANCER_EXECUTABLE to its executable"
        )
    tool = Path(selected).expanduser().resolve()
    proc = subprocess.run(
        [str(tool)],
        input=json.dumps(
            {
                "path": str(source),
                "passes": list(passes),
                "cec_conflict_limit": cec_conflict_limit,
            }
        ),
        capture_output=True,
        text=True,
        timeout=timeout,
    )
    if proc.returncode:
        raise RuntimeError(f"Boolean balancing failed: {proc.stderr.strip()}")
    try:
        response = json.loads(proc.stdout)
    except json.JSONDecodeError as error:
        raise RuntimeError("Balancing tool returned invalid JSON") from error
    evidence = response.get("passes") if isinstance(response, dict) else None
    if (
        not isinstance(response, dict)
        or not isinstance(evidence, list)
        or any(not isinstance(p, dict) for p in evidence)
        or not isinstance(response.get("verilog"), str)
        or not response.get("cleanup_equivalent")
        or not response.get("serialization_equivalent")
        or [p.get("name") for p in evidence] != list(passes)
        or any(p.get("equivalent") is not True for p in evidence)
    ):
        raise RuntimeError("Balancing tool returned incomplete equivalence evidence")
    build_record = tool.parent / "build_provenance.json"
    response.update(
        source_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),
        optimized_sha256=hashlib.sha256(response["verilog"].encode()).hexdigest(),
        native={
            "executable": str(tool),
            "sha256": hashlib.sha256(tool.read_bytes()).hexdigest(),
            "build": (
                json.loads(build_record.read_text()) if build_record.exists() else None
            ),
        },
        diagnostics=proc.stderr,
    )
    return response

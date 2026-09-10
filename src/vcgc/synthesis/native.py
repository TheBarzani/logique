"""Explicit build and JSON process boundary for the pinned native bridge."""

import json
from pathlib import Path
import subprocess
from vcgc.paths import native_executable

REFERENCE_REVISION = "4c6f766cd0ffc62d37ab45edfe80c9f1eae44764"
METHODS = ("xag", "aig_bennett", "xag_bennett", "klut_bennett", "best_fit")


def build_native(
    source: str | Path, *, build: str | Path | None = None, jobs: int = 2
) -> Path:
    """Build explicitly; the first configuration downloads pinned C++ sources."""
    source = Path(source).resolve()
    build = Path(build).resolve() if build else source / "build"
    if jobs < 1:
        raise ValueError("jobs must be positive")
    subprocess.run(
        ["cmake", "-S", str(source), "-B", str(build), "-DCMAKE_BUILD_TYPE=Release"],
        check=True,
    )
    subprocess.run(["cmake", "--build", str(build), "-j", str(jobs)], check=True)
    return build / "boolean_synthesis"


def run_native(path: str | Path, method: str, *, executable=None, **parameters) -> dict:
    """Read one response; surface native diagnostics without losing context."""
    request = {"path": str(Path(path).resolve()), "method": method, **parameters}
    proc = subprocess.run(
        [str(native_executable(executable))],
        input=json.dumps(request),
        text=True,
        capture_output=True,
        timeout=180,
    )
    if proc.returncode:
        raise RuntimeError(f"Native synthesis failed ({method}): {proc.stderr.strip()}")
    try:
        response = json.loads(proc.stdout)
    except json.JSONDecodeError as error:
        raise RuntimeError("Native synthesis returned invalid JSON") from error
    if not isinstance(response, dict) or "network" not in response:
        raise RuntimeError("Native synthesis returned an invalid response")
    return response

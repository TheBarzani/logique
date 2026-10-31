"""Explicit build and JSON process boundary for the pinned native bridge."""

import json
from pathlib import Path
import subprocess
from logique.paths import native_executable

REFERENCE_REVISION = "4c6f766cd0ffc62d37ab45edfe80c9f1eae44764"
METHODS = ("xag", "aig_bennett", "xag_bennett", "klut_bennett", "best_fit")


def build_native(
    source: str | Path, *, build: str | Path | None = None, jobs: int = 2
) -> Path:
    """Build explicitly using local C++ sources or the pinned download fallback."""
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
    timeout = 180
    if parameters.get("strategy") == "sat_pebbling":
        _sat_controls(parameters)
        # The pinned solver ignores its timeout argument. Enforce a process
        # boundary too, including parsing/output work, with one second grace.
        timeout = parameters["sat_time_seconds"] + 1
    elif any(key in parameters for key in SAT_LIMITS):
        raise ValueError("SAT budgets require strategy='sat_pebbling'")
    request = {"path": str(Path(path).resolve()), "method": method, **parameters}
    proc = subprocess.run(
        [str(native_executable(executable))],
        input=json.dumps(request),
        text=True,
        capture_output=True,
        timeout=timeout,
    )
    if proc.returncode:
        raise RuntimeError(f"Native synthesis failed ({method}): {proc.stderr.strip()}")
    try:
        response = json.loads(proc.stdout)
    except json.JSONDecodeError as error:
        raise RuntimeError("Native synthesis returned invalid JSON") from error
    if not isinstance(response, dict) or "network" not in response:
        raise RuntimeError("Native synthesis returned an invalid response")
    if "preprocessing" in parameters:
        evidence = response.get("preprocessing")
        if (
            not isinstance(evidence, dict)
            or evidence.get("common") is not True
            or evidence.get("policy") != parameters["preprocessing"]
            or not isinstance(evidence.get("before_network"), dict)
            or not isinstance(evidence.get("after_network"), dict)
        ):
            raise RuntimeError(
                "Native bridge did not confirm the requested common preprocessing"
            )
    if "strategy" in parameters:
        evidence = response.get("mapping_strategy")
        implementations = {
            "bennett": "caterpillar::bennett_mapping_strategy",
            "bennett_inplace": "caterpillar::bennett_inplace_mapping_strategy",
            "eager": "caterpillar::eager_mapping_strategy",
            "sat_pebbling": "logique::bounded_sat_pebbling",
        }
        if (
            not isinstance(evidence, dict)
            or evidence.get("explicit") is not True
            or evidence.get("name") != parameters["strategy"]
            or evidence.get("implementation")
            != implementations.get(parameters["strategy"])
            or not isinstance(response.get("steps"), list)
        ):
            raise RuntimeError("Native bridge did not confirm the requested strategy")
    if parameters.get("strategy") == "sat_pebbling":
        audit = response.get("sat_validation", {})
        search = response.get("sat_search", {})
        width = response.get("num_qubits")
        if (
            not isinstance(audit, dict)
            or not isinstance(search, dict)
            or type(width) is not int
            or not 0 <= width <= parameters["qubit_budget"]
            or audit.get("qubit_budget") != parameters["qubit_budget"]
            or search.get("max_steps") != parameters["sat_max_steps"]
            or search.get("conflict_limit_per_solve")
            != parameters["sat_conflict_limit"]
            or search.get("search_seconds_between_calls")
            != parameters["sat_time_seconds"]
            or search.get("solver_wall_timeout_supported") is not False
        ):
            raise RuntimeError(
                "Native bridge did not confirm the requested SAT budgets"
            )
    return response


SAT_LIMITS = {
    "qubit_budget": 64,
    "sat_max_steps": 128,
    "sat_conflict_limit": 100000,
    "sat_time_seconds": 30,
}


def _sat_controls(parameters: dict) -> None:
    """Require explicit bounded SAT controls before launching a native process."""
    for name, cap in SAT_LIMITS.items():
        value = parameters.get(name)
        if type(value) is not int or not 1 <= value <= cap:
            raise ValueError(f"SAT requires integer {name} between 1 and {cap}")

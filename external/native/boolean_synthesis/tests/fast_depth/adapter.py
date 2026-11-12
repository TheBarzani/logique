"""Private opt-in level mapping boundary; public synthesis dispatch is unchanged."""

import json
from pathlib import Path
import subprocess
import time

from level_value import (
    LevelValueError,
    array,
    integer,
    require,
    validate_level_response,
)


def run_level(
    path: str | Path,
    *,
    executable: str | Path,
    strategy: str,
    qubit_budget: int = 128,
    preprocessing: str = "none",
    outputs: list[int] | None = None,
) -> dict:
    """Compile with the actual private API and validate before any construction."""
    require(strategy in ("fast", "depth"), "private strategy")
    integer(qubit_budget, 128, 1)
    require(preprocessing in ("none", "refactoring"), "preprocessing policy")
    path = Path(path).resolve()
    require(path.is_file() and path.stat().st_size <= 2_000_000, "source file cap")
    request = dict(
        path=str(path),
        strategy=strategy,
        qubit_budget=qubit_budget,
        preprocessing=preprocessing,
    )
    if outputs is not None:
        array(outputs, 16)
        for output in outputs:
            integer(output, 15)
        request["outputs"] = outputs
    started = time.perf_counter()
    proc = subprocess.run(
        [str(Path(executable).resolve()), "--json"],
        input=json.dumps(request),
        text=True,
        capture_output=True,
        timeout=5,
    )
    if proc.returncode:
        raise LevelValueError("private native failed: " + proc.stderr.strip())
    try:
        data = json.loads(proc.stdout)
    except json.JSONDecodeError as error:
        raise LevelValueError("private native returned invalid JSON") from error
    require(type(data) is dict, "response object")
    implementation = (
        "caterpillar::xag_fast_lowt_mapping_strategy"
        if strategy == "fast"
        else "caterpillar::xag_low_depth_mapping_strategy"
    )
    require(data.get("implementation") == implementation, "strategy handshake")
    require(
        json.dumps(data.get("private_request"), sort_keys=True)
        == json.dumps(
            {k: v for k, v in request.items() if k != "path"}, sort_keys=True
        ),
        "request handshake",
    )
    data["level_value_validation"] = validate_level_response(
        data, qubit_budget=qubit_budget
    )
    data["method"] = "private_xag_level"
    data["parameters"] = {k: v for k, v in request.items() if k != "path"}
    data["seconds"] = time.perf_counter() - started
    data["seconds_scope"] = "native process plus private certificate boundary"
    return data


def synthesize_level(path: str | Path, **parameters):
    """Construct private wrappers only after a valid complete level replay."""
    data = run_level(path, **parameters)
    from logique.circuits.records import records_to_qiskit
    from logique.synthesis.result import SynthesisResult

    return SynthesisResult(records_to_qiskit(data["gates"], data["num_qubits"]), data)

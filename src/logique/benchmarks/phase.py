"""Reproducible coloring phase-oracle experiments at two metric levels."""

import hashlib
import json
from pathlib import Path
import time

from logique.coloring import read_dimacs, encode_coloring
from logique.paths import native_executable
from .provenance import environment, checkout_revision
from .runner import new_run_directory


def run_phase_benchmarks(config: dict, *, executable=None) -> Path:
    """Save each validated phase oracle before lowering it to a common basis.

    Failed runs retain completed rows and the failing case. Logical and lowered
    metrics never share a row, and a failed case never receives zero costs.
    """
    import pandas as pd
    from qiskit import qpy
    from logique.synthesis import synthesize
    from logique.verification import validate, verify_phase_oracle
    from .metrics import circuit_metrics, lower_circuit

    inputs = [Path(p).resolve() for p in config["inputs"]]
    if any(p.suffix != ".col" for p in inputs):
        raise ValueError("Phase benchmark inputs must be coloring .col files")
    basis = config.get("basis_gates", ["u", "cx"])
    if basis != ["u", "cx"]:
        raise ValueError("Phase benchmarks use the common basis ['u', 'cx']")
    optimization = config.get("optimization_level", 1)
    if optimization not in (0, 1, 2, 3):
        raise ValueError("optimization_level must be 0, 1, 2, or 3")
    seed = config.get("seed", 7)
    validation = config.get("validation", "auto")
    tool = native_executable(executable)
    build_info = tool.parent / "build_provenance.json"
    native = {
        "executable": str(tool),
        "sha256": hashlib.sha256(tool.read_bytes()).hexdigest(),
        "build": json.loads(build_info.read_text()) if build_info.exists() else None,
    }
    output = new_run_directory(config.get("output"))
    manifest = {
        "schema_version": 1,
        "run_id": output.name,
        "config": config,
        "versions": environment(),
        "checkout": checkout_revision(Path.cwd()),
        "native": native,
        "oracle_contract": "(-1)^f(x), clean auxiliary qubits restored",
        "status": "running",
        "cases": [],
    }
    rows = []

    def save() -> None:
        (output / "run.json").write_text(json.dumps(manifest, indent=2) + "\n")
        if rows:
            pd.DataFrame(rows).to_csv(output / "summary.csv", index=False)

    def save_circuit(circuit, filename: str) -> None:
        with (output / filename).open("wb") as stream:
            qpy.dump(circuit, stream)

    save()
    case = None
    try:
        for index, path in enumerate(inputs):
            case = None
            problem = read_dimacs(path, colors=config.get("colors"))
            encoding = encode_coloring(problem)
            for method in config.get("methods", ["xag"]):
                name = f"{index:03d}_{path.stem}_{method}"
                case = {
                    "name": name,
                    "benchmark": path.stem,
                    "method": method,
                    "input": str(path),
                    "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
                    "status": "running",
                }
                manifest["cases"].append(case)
                save()
                print(f"{path.stem}: {method}", flush=True)
                started = time.perf_counter()
                result = synthesize(
                    encoding,
                    method,
                    executable=tool,
                    **config.get("parameters", {}),
                )
                oracle = result.phase_oracle()
                if validation != "none":
                    sampled = validation == "sampled" or (
                        validation == "auto" and encoding.input_count > 12
                    )
                    options = {
                        "sampled": sampled,
                        "samples": config.get("samples", 256),
                        "seed": seed,
                    }
                    validate(result, **options)
                    verify_phase_oracle(
                        result, encoding=encoding, circuit=oracle, **options
                    )
                report = result.metadata.get("phase_validation", {"status": "not run"})
                case.update(validation=report, parameters=result.metadata["parameters"])
                (output / f"{name}.json").write_text(
                    json.dumps(result.metadata, indent=2) + "\n"
                )
                save_circuit(result.circuit, f"{name}_raw.qpy")
                save_circuit(oracle, f"{name}_phase.qpy")
                common = {
                    "benchmark": path.stem,
                    "method": method,
                    "circuit_kind": "phase_oracle",
                    "inputs": encoding.input_count,
                    "auxiliary_qubits": oracle.num_qubits - encoding.input_count,
                    "vertices": len(problem.vertices),
                    "edges": len(problem.edges),
                    "colors": problem.colors,
                    "validation": report["status"],
                    "marked_samples": report.get("marked_assignments"),
                    "seed": seed,
                    "synthesis_seconds": result.metadata["seconds"],
                }
                rows.append(
                    {
                        **common,
                        **circuit_metrics(oracle),
                        "seconds": time.perf_counter() - started,
                    }
                )
                save()
                lower_start = time.perf_counter()
                lowered = lower_circuit(
                    oracle,
                    basis_gates=basis,
                    seed=seed,
                    optimization_level=optimization,
                )
                if not set(lowered.count_ops()) <= set(basis):
                    raise AssertionError(
                        "Lowered phase oracle contains gates outside U/CX"
                    )
                save_circuit(lowered, f"{name}_phase_decomposed.qpy")
                rows.append(
                    {
                        **common,
                        **circuit_metrics(lowered),
                        "metric_level": "decomposed",
                        "basis_gates": ",".join(basis),
                        "optimization_level": optimization,
                        "lowering_seconds": time.perf_counter() - lower_start,
                        "seconds": time.perf_counter() - started,
                    }
                )
                case.update(status="complete", seconds=time.perf_counter() - started)
                save()
        manifest["status"] = "complete"
    except Exception as error:
        diagnostic = f"{type(error).__name__}: {error}"
        manifest.update(status="failed", error=diagnostic)
        if case is not None:
            case.update(status="failed", error=diagnostic)
        raise
    finally:
        save()
    return output

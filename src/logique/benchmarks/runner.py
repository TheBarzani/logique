"""Configuration-driven runs shared by the CLI and research notebooks."""

from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import time
from uuid import uuid4
from logique.coloring import read_dimacs, encode_coloring
from .provenance import environment, checkout_revision


def new_run_directory(output: str | Path | None = None) -> Path:
    """Allocate a new run directory without overwriting an existing experiment."""
    path = (
        Path(output)
        if output
        else Path("dump")
        / (
            datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
            + "-"
            + uuid4().hex[:8]
        )
    )
    path.mkdir(parents=True, exist_ok=False)
    return path.resolve()


def load_config(path: str | Path, **overrides) -> dict:
    """Resolve paths relative to the config; supplied options take precedence."""
    path = Path(path).resolve()
    config = json.loads(path.read_text())
    allowed = {
        "inputs",
        "methods",
        "parameters",
        "colors",
        "iterations",
        "seed",
        "validation",
        "samples",
        "output",
        "kind",
        "basis_gates",
        "optimization_level",
    }
    unknown = set(config) - allowed
    if unknown:
        raise ValueError(f"Unknown configuration fields: {sorted(unknown)}")
    config.update({k: v for k, v in overrides.items() if v is not None})
    if not isinstance(config.get("inputs"), list) or not config["inputs"]:
        raise ValueError("config requires a nonempty inputs list")
    config["inputs"] = [str((path.parent / p).resolve()) for p in config["inputs"]]
    if config.get("output") and overrides.get("output") is None:
        config["output"] = str((path.parent / config["output"]).resolve())
    return config


def run_benchmarks(config: dict, *, executable=None) -> Path:
    """Export each completed case and record failed runs with their diagnostics."""
    import pandas as pd
    from qiskit import qpy
    from logique.synthesis import synthesize, METHODS
    from logique.synthesis.saha_belletti import comparison_circuit, VARIANTS
    from logique.circuits.grover import grover_circuit
    from logique.verification import validate
    from .export import export_result
    from .metrics import circuit_metrics

    inputs = [Path(p).resolve() for p in config["inputs"]]
    methods = config.get("methods", ["xag"])
    known = {*METHODS, *(f"sb_{v}" for v in VARIANTS)}
    if not methods or not set(methods) <= known:
        raise ValueError(f"methods must be selected from {sorted(known)}")
    validation = config.get("validation", "exhaustive")
    if validation not in ("auto", "exhaustive", "sampled", "none"):
        raise ValueError("validation must be auto, exhaustive, sampled, or none")
    if config.get("kind", "synthesis") not in (
        "synthesis",
        "comparison",
        "phase_oracle",
    ):
        raise ValueError("kind must be synthesis, comparison, or phase_oracle")
    if config.get("kind", "synthesis") != "comparison" and any(
        m.startswith("sb_") for m in methods
    ):
        raise ValueError("Saha-Belletti returns full circuits; use kind=comparison")
    if config.get("kind") == "phase_oracle":
        from .phase import run_phase_benchmarks

        return run_phase_benchmarks(config, executable=executable)
    output = new_run_directory(config.get("output"))
    manifest = {
        "schema_version": 1,
        "run_id": output.name,
        "config": config,
        "versions": environment(),
        "checkout": checkout_revision(Path.cwd()),
        "status": "running",
        "cases": [],
    }

    def save():
        (output / "run.json").write_text(json.dumps(manifest, indent=2) + "\n")

    save()
    rows = []
    try:
        for index, path in enumerate(inputs):
            problem = (
                read_dimacs(path, colors=config.get("colors"))
                if path.suffix == ".col"
                else None
            )
            for method in methods:
                name = f"{index:03d}_{path.stem}_{method}"
                started = time.perf_counter()
                if method.startswith("sb_"):
                    if problem is None:
                        raise ValueError("Comparison methods require DIMACS inputs")
                    circuit = comparison_circuit(
                        problem, method[3:], iterations=config.get("iterations", 1)
                    )
                    row = {"validation": "not run", "preparation": "all bitstrings"}
                else:
                    encoding = encode_coloring(problem) if problem is not None else None
                    result = synthesize(
                        encoding if encoding is not None else path,
                        method,
                        executable=executable,
                        **config.get("parameters", {}),
                    )
                    if validation != "none":
                        validate(
                            result,
                            sampled=validation == "sampled"
                            or (
                                validation == "auto"
                                and len(result.metadata["input_qubits"]) > 12
                            ),
                            samples=config.get("samples", 256),
                            seed=config.get("seed", 7),
                        )
                    export_result(result, output, name)
                    circuit = result.circuit
                    if config.get("kind") == "comparison":
                        # Shared all-bitstrings preparation matches Saha-Belletti.
                        circuit = grover_circuit(
                            result, iterations=config.get("iterations", 1)
                        )
                    row = {
                        "validation": result.metadata.get("validation", {}).get(
                            "status", "not run"
                        ),
                        "preparation": (
                            "all bitstrings"
                            if config.get("kind") == "comparison"
                            else "raw computation"
                        ),
                    }
                with (output / f"{name}_circuit.qpy").open("wb") as stream:
                    qpy.dump(circuit, stream)
                row.update(
                    benchmark=path.stem,
                    method=method,
                    seconds=time.perf_counter() - started,
                    **circuit_metrics(circuit),
                )
                rows.append(row)
                manifest["cases"].append(
                    {
                        "name": name,
                        "input": str(path),
                        "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
                        **row,
                    }
                )
                pd.DataFrame(rows).to_csv(output / "summary.csv", index=False)
                save()
        manifest["status"] = "complete"
    except Exception as error:
        manifest.update(status="failed", error=f"{type(error).__name__}: {error}")
        raise
    finally:
        save()
    return output

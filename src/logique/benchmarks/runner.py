"""Configuration-driven runs shared by the CLI and research notebooks."""

import hashlib
import json
from pathlib import Path
import time
from logique.coloring import read_dimacs, encode_coloring
from logique.paths import new_dump_directory
from .provenance import environment, checkout_revision, native_provenance


def new_run_directory(
    output: str | Path | None = None,
    *,
    description: str = "benchmark",
    root: str | Path = "dump",
) -> Path:
    """Allocate a timestamped run, or use an explicit path without overwriting."""
    if output is None:
        return new_dump_directory(description, root=root)
    path = Path(output)
    path.mkdir(parents=True, exist_ok=False)
    return path.resolve()


def load_config(path: str | Path, **overrides) -> dict:
    """Resolve paths relative to the config; supplied options take precedence."""
    path = Path(path).resolve()
    config = json.loads(path.read_text())
    if config.get("kind") == "coloring_study":
        from .coloring_study import CONFIG_FIELDS

        allowed = CONFIG_FIELDS
    else:
        allowed = None
    allowed = allowed or {
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
        "verification_assignments",
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
    if config.get("kind") == "coloring_study":
        from .coloring_study import validate_study_config

        assignments = config.get("verification_assignments", {})
        if isinstance(assignments, dict):
            config["verification_assignments"] = {
                str((path.parent / p).resolve()): values
                for p, values in assignments.items()
            }
        return validate_study_config(config)
    return config


def run_benchmarks(config: dict, *, executable=None) -> Path:
    """Export each completed case and record failed runs with their diagnostics."""
    if config.get("kind") == "coloring_study":
        from .coloring_study import run_coloring_study

        return run_coloring_study(config, executable=executable)

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
    kind = config.get("kind", "synthesis").replace("_", "-")
    subject = inputs[0].stem if len(inputs) == 1 else "benchmark"
    output = new_run_directory(config.get("output"), description=f"{subject}-{kind}")
    manifest = {
        "schema_version": 1,
        "run_id": output.name,
        "config": config,
        "versions": environment(executable=executable),
        "checkout": checkout_revision(Path.cwd()),
        "status": "running",
        "cases": [],
    }
    if any(not method.startswith("sb_") for method in methods):
        manifest["native"] = native_provenance(executable)

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
                            assignments=config.get("verification_assignments"),
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

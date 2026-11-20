"""Validate the saved C5 adapter and prepare requests; never route or sample."""

from __future__ import annotations

import argparse
import importlib
import json
import math
from pathlib import Path

from logique.benchmarks import c5_noise_adapter as adapter
from logique.benchmarks import noisy_iterations as noisy


def assert_source_imports() -> dict:
    """Bind every relevant loaded module to this explicit candidate checkout."""
    source = Path(__file__).resolve().parents[1] / "src"
    imports = {}
    for name in (
        "paths",
        "benchmarks.c5_noise_adapter",
        "benchmarks.noisy_iterations",
        "benchmarks.iteration_study",
        "benchmarks.ideal_iterations",
        "benchmarks.routing",
        "benchmarks.costs",
        "benchmarks.metrics",
        "benchmarks.coloring_study",
        "circuits.grover",
        "circuits.structure",
    ):
        module = importlib.import_module(f"logique.{name}")
        actual = Path(module.__file__).resolve()
        assert actual == source / "logique" / (name.replace(".", "/") + ".py")
        imports[name] = {"path": str(actual), "sha256": adapter.digest(actual)}
    return imports


def check_calibration(output: Path, reference: Path | None = None) -> dict:
    """Save a fresh offline calibration and optionally check another process's.

    This creates only backend/channel JSON, never a circuit, route or shot.
    Each invocation needs a new directory and external <=120-second supervision.
    """
    imports = assert_source_imports()
    from qiskit_aer.noise import NoiseModel
    from logique.benchmarks.routing import default_backend

    output.mkdir(exist_ok=False)
    backend = default_backend()
    for kind, filename in (
        ("properties", backend.props_filename),
        ("configuration", backend.conf_filename),
    ):
        (output / f"{kind}.json").write_bytes(
            (Path(backend.dirname) / filename).read_bytes()
        )
    snapshot = NoiseModel.from_backend(backend).to_dict(serializable=True)
    noisy._write(output / "noise.json", snapshot)
    source = reference if reference is not None else output
    hashes = adapter.validate_calibration(
        backend, source, json.loads((source / "noise.json").read_text())
    )
    records = adapter.calibration_records(snapshot)
    result = {
        "imports": imports,
        "records": len(records),
        "reference_hashes": hashes,
        "fresh_noise_sha256": adapter.digest(output / "noise.json"),
        "scientific_shots": 0,
        "independent_reference": reference is not None,
    }
    noisy._write(output / "calibration-check.json", result)
    return result


def check(config: dict) -> dict:
    """Check actual signed oracle, A/inverse/reflection and all saved ideal rows.

    Arrays are at most 2,048 complex128 amplitudes; no dense operators. Saved
    iteration states are reconciled rather than repeating the admitted sweep.
    The caller must supervise this serial child with a 120-second deadline.
    """
    import numpy as np
    from qiskit.quantum_info import Statevector

    expected_src = Path(__file__).resolve().parents[1] / "src"
    for module in (adapter, noisy):
        assert Path(module.__file__).resolve().is_relative_to(expected_src)
    rng = np.random.default_rng(20261112)
    colors = [[(word >> (2 * v)) & 3 for v in range(5)] for word in range(1024)]
    valid = np.array([all(c < 3 for c in row) for row in colors])
    good = np.array(
        [
            valid[word] and all(row[v] != row[(v + 1) % 5] for v in range(5))
            for word, row in enumerate(colors)
        ]
    )
    assert sum(good) == 30 and sum(valid) == 243
    residuals = {}
    for regime in ("R1", "R2"):
        source = adapter.load_source(config, regime)
        preparation, oracle, reflection = source["parts"]
        amplitudes = rng.normal(size=2048) + 1j * rng.normal(size=2048)
        amplitudes /= np.linalg.norm(amplitudes)
        clean = amplitudes.copy()
        clean[1024:] = 0
        clean /= np.linalg.norm(clean)
        expected = clean.copy()
        expected[:1024][good] *= -1
        observed = Statevector(clean.copy()).evolve(oracle).data
        values = {
            "clean_coherent_oracle_signed_error": float(max(abs(observed - expected))),
            "dirty_workspace_probability": float(sum(abs(observed[1024:]) ** 2)),
        }
        if regime == "R1":
            for word in (8, 70, 71):
                probe = np.zeros(2048, dtype=complex)
                probe[word] = 1
                expected_probe = probe * (-1 if good[word] else 1)
                values[f"basis_word_{word}_signed_error"] = float(
                    max(
                        abs(
                            Statevector(probe.copy()).evolve(oracle).data
                            - expected_probe
                        )
                    )
                )
        roundtrip = (
            Statevector(amplitudes.copy())
            .evolve(preparation, range(10))
            .evolve(source["preparation_inverse"], range(10))
        )
        values["actual_A_inverse_signed_error"] = float(
            max(abs(roundtrip.data - amplitudes))
        )
        support = np.ones(1024, dtype=bool) if regime == "R1" else valid
        size = int(sum(support))
        s = support.astype(complex) / math.sqrt(size)
        expected_reflection = amplitudes.copy().reshape(2, 1024)
        for sector in expected_reflection:
            sector[:] = 2 * s * np.vdot(s, sector.copy()) - sector
        values["reflection_both_output_sectors_signed_error"] = float(
            max(
                abs(
                    Statevector(amplitudes.copy()).evolve(reflection, range(10)).data
                    - expected_reflection.ravel()
                )
            )
        )
        zero = Statevector.from_int(0, 2048).evolve(preparation, range(10)).data
        expected_zero = np.zeros(2048, dtype=complex)
        expected_zero[:1024] = s
        values["preparation_signed_error"] = float(max(abs(zero - expected_zero)))
        theta = math.asin(math.sqrt(30 / size))
        row_checks = []
        for row in source["reference"]["rows"]:
            j = row["iterations"]
            expected_state = np.zeros(2048, dtype=complex)
            expected_state[:1024][good] = math.sin((2 * j + 1) * theta) / math.sqrt(30)
            expected_state[:1024][support & ~good] = math.cos(
                (2 * j + 1) * theta
            ) / math.sqrt(size - 30)
            path = Path(config["ideal_pilot"]) / regime / f"state-j{j}.npz"
            with np.load(path) as saved:
                error = float(max(abs(saved["actual"] - expected_state)))
            assert error <= 1e-10
            row_checks.append({"iterations": j, "saved_signed_error": error})
        assert max(values.values()) <= 1e-10
        residuals[regime] = {"probes": values, "saved_rows": row_checks}
    return {"seed": 20261112, "precision": "complex128", "results": residuals}


def main() -> None:
    """Write fresh bounded validation plus unlaunched requests for review."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--calibration-output", type=Path)
    parser.add_argument("--calibration-reference", type=Path)
    args = parser.parse_args()
    if args.calibration_output is not None:
        if args.config is not None or args.output is not None:
            parser.error("Calibration diagnostics cannot prepare source requests")
        print(
            json.dumps(
                check_calibration(args.calibration_output, args.calibration_reference)
            )
        )
        return
    if args.config is None or args.output is None or args.calibration_reference:
        parser.error("--config and --output required for source checks")
    config = json.loads(args.config.read_text())
    args.output.mkdir(exist_ok=False)
    noisy._write(args.output / "validation.json", check(config))
    requests = adapter.prepare(config, root=args.output)
    noisy._write(
        args.output / "checkpoint.json",
        {
            "request_directory": str(requests),
            "scientific_noisy_shots": 0,
            "source_admission": "pending independent adapter and whole-chain review",
        },
    )


if __name__ == "__main__":
    main()

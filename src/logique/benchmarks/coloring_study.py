"""Controlled R1/R2/R3 assembly and a sequential, local coloring pilot.

Only logical and optional unrouted U/CX metrics are implemented. Validation uses
monomial records, never statevectors. Sampled coverage is evidence, not proof.
"""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
import math
from pathlib import Path
import re
import time
from typing import TYPE_CHECKING

from logique.coloring import ColoringProblem, encode_coloring, read_dimacs
from logique.synthesis.native import METHODS
from logique.synthesis.saha_belletti import VARIANTS

if TYPE_CHECKING:
    from qiskit import QuantumCircuit

STUDY_METHODS = (*METHODS, *(f"sb_{variant}" for variant in VARIANTS))
REGIMES = ("R1", "R2", "R3")
CONFIG_FIELDS = {
    "kind",
    "inputs",
    "methods",
    "regimes",
    "iterations",
    "seeds",
    "colors",
    "validation",
    "samples",
    "verification_assignments",
    "remove_precolors",
    "common_basis",
    "basis_gates",
    "optimization_level",
    "output",
}


class ExcludedCase(ValueError):
    """A scientifically unsupported construction, whose costs must be omitted."""


def _integers(values, name: str, minimum: int = 0) -> None:
    if (
        not isinstance(values, list)
        or not values
        or any(type(v) is not int or v < minimum for v in values)
        or len(set(values)) != len(values)
    ):
        raise ValueError(
            f"{name} requires a nonempty list of distinct integers >= {minimum}"
        )


def validate_study_config(config: dict) -> dict:
    """Validate every supported control before opening a run or doing synthesis.

    Verification assignments are a mapping from resolved input paths to lists of
    input-register integers. Missing inputs receive the selected default coverage.
    Exhaustive monomial checks are limited to 12 data bits; auto samples above it.
    Unknown controls (including target, precision, limits, and profiles) fail.
    """
    unknown = set(config) - CONFIG_FIELDS
    if unknown:
        raise ValueError(f"Unsupported coloring-study controls: {sorted(unknown)}")
    result = {
        "kind": "coloring_study",
        "methods": list(STUDY_METHODS),
        "regimes": list(REGIMES),
        "iterations": [1],
        "seeds": [7],
        "validation": "auto",
        "samples": 256,
        "remove_precolors": False,
        "common_basis": False,
        **config,
    }
    if result["kind"] != "coloring_study":
        raise ValueError("kind must be coloring_study")
    inputs = result.get("inputs")
    if (
        not isinstance(inputs, list)
        or not inputs
        or any(not isinstance(p, str) or Path(p).suffix != ".col" for p in inputs)
    ):
        raise ValueError("inputs requires a nonempty list of DIMACS .col paths")
    result["inputs"] = [str(Path(p).resolve()) for p in inputs]
    if len(set(result["inputs"])) != len(inputs):
        raise ValueError("inputs must be distinct")
    for key, known in (("methods", STUDY_METHODS), ("regimes", REGIMES)):
        values = result[key]
        if (
            not isinstance(values, list)
            or not values
            or any(not isinstance(v, str) or v not in known for v in values)
            or len(set(values)) != len(values)
        ):
            raise ValueError(f"{key} must be distinct selections from {known}")
    _integers(result["iterations"], "iterations")
    _integers(result["seeds"], "seeds")
    if any(seed >= 1 << 32 for seed in result["seeds"]):
        raise ValueError("seeds must be smaller than 2**32")
    for key in ("remove_precolors", "common_basis"):
        if type(result[key]) is not bool:
            raise ValueError(f"{key} must be boolean")
    if "colors" in result and (
        type(result["colors"]) is not int or result["colors"] < 2
    ):
        raise ValueError("colors must be an integer >= 2")
    if result["validation"] not in ("auto", "sampled", "exhaustive"):
        raise ValueError("validation must be auto, sampled, or exhaustive")
    if type(result["samples"]) is not int or result["samples"] < 1:
        raise ValueError("samples must be a positive integer")
    if result.get("basis_gates", ["u", "cx"]) != ["u", "cx"]:
        raise ValueError("Only the common U/CX basis ['u', 'cx'] is supported")
    optimization = result.get("optimization_level", 1)
    if type(optimization) is not int or optimization not in range(4):
        raise ValueError("optimization_level must be 0, 1, 2, or 3")
    if not result["common_basis"] and {"basis_gates", "optimization_level"} & set(
        config
    ):
        raise ValueError("basis_gates/optimization_level require common_basis=true")
    assignments = result.get("verification_assignments", {})
    if not isinstance(assignments, dict) or set(assignments) - set(result["inputs"]):
        raise ValueError(
            "verification_assignments must map resolved input paths to lists"
        )
    for values in assignments.values():
        if not isinstance(values, list) or any(
            type(v) is not int or v < 0 for v in values
        ):
            raise ValueError(
                "verification assignments must be lists of nonnegative integers"
            )
    if "output" in result and result["output"] is not None:
        if not isinstance(result["output"], (str, Path)) or not re.fullmatch(
            r"\d{10}-[a-zA-Z0-9][a-zA-Z0-9_-]*", Path(result["output"]).name
        ):
            raise ValueError("output directory must be named MMDDHHMMSS-description")
        result["output"] = str(result["output"])
    return result


def _problem_without_precolors(problem: ColoringProblem, remove: bool):
    if type(remove) is not bool:
        raise ValueError("remove_precolors must be boolean")
    if problem.precolored and not remove:
        raise ValueError("Precolors require explicit remove_precolors=true")
    transformations = []
    if problem.precolored:
        transformations.append(
            {"operation": "remove_precolors", "removed": dict(problem.precolored)}
        )
    return (
        ColoringProblem(problem.vertices, problem.edges, problem.colors),
        transformations,
    )


@dataclass
class ColoringStudyCase:
    """Reusable blocks; preparation/diffusion use the ordered data register.

    Raw/oracle/search use physical synthesis wires. ``data_qubits`` maps the
    data-only blocks onto those wires. Reflection has the positive Grover sign,
    A(2|0><0|-I)A†, and is built from the actual emitted preparation and inverse.
    """

    raw: QuantumCircuit
    preparation: QuantumCircuit
    oracle: QuantumCircuit
    diffusion: QuantumCircuit
    search: QuantumCircuit
    metadata: dict

    @property
    def circuits(self) -> dict[str, QuantumCircuit]:
        """Return the five independently saved and measured components."""
        return {
            name: getattr(self, name)
            for name in ("raw", "preparation", "oracle", "diffusion", "search")
        }


def assemble_case(
    problem: ColoringProblem,
    method: str,
    regime: str,
    *,
    iterations: int = 1,
    seed: int = 7,
    validation: str = "auto",
    samples: int = 256,
    verification_assignments: list[int] | None = None,
    remove_precolors: bool = False,
    executable=None,
) -> ColoringStudyCase:
    """Assemble and validate one controlled case without saving or simulating it.

    Native R3 compiles the complete predicate at 2**bits colors, preserving every
    vertex/input. All preparations retain the original k. Baselines use their
    clean XOR kickback wrapper. Native methods use direct kickback when both
    target sectors verify, otherwise compute-Z-inverse-compute.
    """
    # Reuse control validation even for direct callers, before importing Qiskit.
    validate_study_config(
        {
            "inputs": ["case.col"],
            "methods": [method],
            "regimes": [regime],
            "iterations": [iterations],
            "seeds": [seed],
            "validation": validation,
            "samples": samples,
            "remove_precolors": remove_precolors,
        }
    )
    problem, transformations = _problem_without_precolors(problem, remove_precolors)
    if not problem.vertices or problem.colors < 2:
        raise ValueError("Study cases require vertices and at least two colors")
    encoding = encode_coloring(problem)
    if validation == "exhaustive" and encoding.input_count > 12:
        raise ValueError("Exhaustive validation is limited to 12 data bits")
    if verification_assignments is not None and (
        not isinstance(verification_assignments, list)
        or any(
            type(v) is not int or not 0 <= v < 1 << encoding.input_count
            for v in verification_assignments
        )
    ):
        raise ValueError("verification assignment is outside the input register")
    from qiskit import QuantumCircuit
    from logique.circuits.grover import coloring_preparation, _reflection
    from logique.synthesis import synthesize, baseline_components
    from logique.verification import (
        validate,
        verify_phase_oracle,
        verify_kickback_oracle,
    )

    timings = {}
    start = time.perf_counter()
    effective = ColoringProblem(
        problem.vertices,
        problem.edges,
        (1 << encoding.bits_per_color) if regime == "R3" else problem.colors,
    )
    effective_encoding = encode_coloring(effective)
    timings["effective_encoding_seconds"] = time.perf_counter() - start
    start = time.perf_counter()
    if method.startswith("sb_"):
        try:
            result = baseline_components(
                problem,
                method[3:],
                domain_policy=("domain_free" if regime == "R3" else "complete"),
            )
        except ValueError as error:
            if method == "sb_original" and "multiple higher-index neighbors" in str(
                error
            ):
                raise ExcludedCase(str(error)) from error
            raise
        construction = "clean_xor_kickback"
    else:
        result = synthesize(effective_encoding, method, executable=executable)
        construction = "compute_Z_inverse_compute"
    timings["synthesis_seconds"] = time.perf_counter() - start
    start = time.perf_counter()
    oracle = result.phase_oracle()
    timings["oracle_wrapper_seconds"] = time.perf_counter() - start
    data = result.metadata["input_qubits"]
    if len(data) != encoding.input_count:
        raise AssertionError("Synthesis changed the coloring input register")
    start = time.perf_counter()
    options = dict(
        sampled=validation == "sampled" or (validation == "auto" and len(data) > 12),
        samples=samples,
        seed=seed,
        assignments=verification_assignments,
    )
    if method.startswith("sb_"):
        report = verify_kickback_oracle(result, encoding=effective_encoding, **options)
        report.update(
            reference="effective independent coloring predicate",
            phase_construction="X H; clean XOR; H X on target",
            phase_evidence="on checked assignments both target sectors have exact XOR and unit phase; kickback by linearity",
        )
    else:
        raw_report = validate(result, **options)
        try:
            report = verify_kickback_oracle(
                result, encoding=effective_encoding, **options
            )
        except AssertionError as error:
            report = verify_phase_oracle(
                result, encoding=effective_encoding, circuit=oracle, **options
            )
            report["direct_kickback_rejection"] = str(error)
        else:
            target = result.metadata["output_qubits"][0]
            oracle = QuantumCircuit(result.circuit.num_qubits, name="native_phase")
            oracle.x(target)
            oracle.h(target)
            oracle.compose(result.circuit, inplace=True)
            oracle.h(target)
            oracle.x(target)
            construction = "verified_clean_xor_kickback"
            report.update(
                reference="effective independent coloring predicate",
                phase_construction="X H; verified clean XOR; H X on target",
                phase_evidence="exact XOR and unit phase in both checked target sectors; kickback by linearity",
            )
        report["raw_validation"] = raw_report
    timings["validation_seconds"] = time.perf_counter() - start
    start = time.perf_counter()
    if regime == "R1":
        preparation = QuantumCircuit(len(data), name="hadamard_preparation")
        preparation.h(range(len(data)))
        preparation_label = "Hadamard_all_binary_codes"
    else:
        preparation = coloring_preparation(encoding)
        preparation_label = "unitary_StatePreparation_uniform_original_k_per_vertex"
    diffusion = _reflection(preparation)
    # _reflection implements A(I-2|0><0|)A†; correct its global sign.
    diffusion.global_phase += math.pi
    search = QuantumCircuit(oracle.num_qubits, name="coloring_search")
    search.compose(preparation, data, inplace=True)
    for _ in range(iterations):
        search.compose(oracle, inplace=True)
        search.compose(diffusion, data, inplace=True)
    timings["preparation_diffusion_search_seconds"] = time.perf_counter() - start
    if method.startswith("sb_"):
        roles = {**result.metadata["qubit_roles"], "mcx_ancilla": []}
    else:
        outputs = result.metadata["output_qubits"]
        roles = {
            "data": data,
            "output": [] if construction == "verified_clean_xor_kickback" else outputs,
            "synthesis_workspace": sorted(
                set(range(oracle.num_qubits)) - set(data) - set(outputs)
            ),
            "constraint": [],
            "kickback": (
                outputs if construction == "verified_clean_xor_kickback" else []
            ),
            "mcx_ancilla": [],
        }
    mapping = {
        v: [data[q] for q in wires] for v, wires in encoding.input_mapping.items()
    }
    metadata = {
        "method": method,
        "regime": regime,
        "iteration": iterations,
        "seed": seed,
        "colors": problem.colors,
        "effective_predicate_colors": effective.colors,
        "vertices": list(problem.vertices),
        "edges": list(problem.edges),
        "transformations": transformations,
        "input_mapping": mapping,
        "input_bit_order": "lsb_first",
        "data_qubits": data,
        "preparation_construction": preparation_label,
        "oracle_construction": construction,
        "diffusion_construction": "A(2|0><0|-I)A_dagger_from_actual_preparation",
        "search_construction": "A_then_(oracle_then_matching_diffusion)^iteration",
        "predicate": "edge_only_all_binary_codes" if regime == "R3" else "complete",
        "qubit_roles": roles,
        "role_counts": {r: len(q) for r, q in roles.items()},
        "role_notes": "Native synthesis workspace is not classified as AND-only; MCX has no explicit added ancillas",
        "validation": report,
        "composition_evidence": {
            "preparation": (
                "H tensor product gives uniform binary codes"
                if regime == "R1"
                else "per-vertex unitary StatePreparation has amplitudes 1/sqrt(k) on codes 0..k-1 and zero elsewhere"
            ),
            "reflection": "inverse of the actual preparation, zero-state reflection, actual preparation; positive Grover global sign",
            "R3_restriction": (
                "edge-only equals complete predicate on the valid-color preparation support; diffusion preserves that support"
                if regime == "R3"
                else None
            ),
            "search": "composition of validated oracle action and matching reflection; no large search statevector simulation",
        },
        "timings": timings,
        "backend_metadata": result.metadata,
        "component_registers": {
            name: "ordered_data" if name in ("preparation", "diffusion") else "physical"
            for name in ("raw", "preparation", "oracle", "diffusion", "search")
        },
    }
    return ColoringStudyCase(
        result.circuit, preparation, oracle, diffusion, search, metadata
    )


def run_coloring_study(config: dict, *, executable=None) -> Path:
    """Run cases sequentially, preserving excluded/failed cases without cost rows.

    All controls and input-specific assignments are checked before numerical work.
    QPY artifacts are the source for every metric row; common-basis artifacts are
    saved too. No routing, FT precision, memory/timeout controls or profiles exist.
    """
    config = validate_study_config(config)
    prepared = []
    for filename in config["inputs"]:
        path = Path(filename)
        problem = read_dimacs(path, colors=config.get("colors"))
        clean, _ = _problem_without_precolors(problem, config["remove_precolors"])
        n = encode_coloring(clean).input_count
        if not clean.vertices or clean.colors < 2:
            raise ValueError("Study inputs require vertices and at least two colors")
        if config["validation"] == "exhaustive" and n > 12:
            raise ValueError("Exhaustive validation is limited to 12 data bits")
        if any(
            v >= 1 << n
            for v in config.get("verification_assignments", {}).get(filename, [])
        ):
            raise ValueError(
                f"verification assignment outside input register: {filename}"
            )
        prepared.append((path, problem, hashlib.sha256(path.read_bytes()).hexdigest()))
    from qiskit import qpy
    import pandas as pd
    from .metrics import circuit_metrics, lower_circuit
    from .provenance import environment, checkout_revision, native_provenance
    from .runner import new_run_directory

    native = (
        native_provenance(executable)
        if any(m in METHODS for m in config["methods"])
        else None
    )
    output = new_run_directory(config.get("output"), description="coloring-study")
    manifest = {
        "schema_version": 1,
        "config": config,
        "status": "running",
        "cases": [],
        "versions": environment(executable=executable),
        "native": native,
        "checkout": checkout_revision(Path.cwd()),
        "source_hashes": {
            source.name: hashlib.sha256(source.read_bytes()).hexdigest()
            for source in (Path(__file__), Path(__file__).with_name("runner.py"))
        },
        "implemented_metric_levels": ["logical"]
        + (["common_basis"] if config["common_basis"] else []),
    }
    (output / "config.json").write_text(json.dumps(config, indent=2) + "\n")
    (output / "provenance.json").write_text(
        json.dumps(
            {
                key: manifest[key]
                for key in ("versions", "native", "checkout", "source_hashes")
            },
            indent=2,
        )
        + "\n"
    )
    rows = []

    def save():
        (output / "run.json").write_text(json.dumps(manifest, indent=2) + "\n")
        if rows:
            pd.DataFrame(rows).to_csv(output / "summary.csv", index=False)

    save()
    try:
        for index, (path, problem, digest) in enumerate(prepared):
            for regime in config["regimes"]:
                for method in config["methods"]:
                    for iteration in config["iterations"]:
                        for seed in config["seeds"]:
                            name = f"{index:03d}_{regime}_{method}_j{iteration}_s{seed}"
                            case = {
                                "name": name,
                                "input": str(path),
                                "sha256": digest,
                                "benchmark": path.stem,
                                "regime": regime,
                                "method": method,
                                "iteration": iteration,
                                "seed": seed,
                                "status": "running",
                            }
                            manifest["cases"].append(case)
                            save()
                            started = time.perf_counter()
                            case_rows = []
                            try:
                                assembled = assemble_case(
                                    problem,
                                    method,
                                    regime,
                                    iterations=iteration,
                                    seed=seed,
                                    validation=config["validation"],
                                    samples=config["samples"],
                                    verification_assignments=config.get(
                                        "verification_assignments", {}
                                    ).get(str(path)),
                                    remove_precolors=config["remove_precolors"],
                                    executable=executable,
                                )
                                case.update(assembled.metadata)
                                artifacts = {}
                                for component, circuit in assembled.circuits.items():
                                    for level in ["logical"] + (
                                        ["common_basis"]
                                        if config["common_basis"]
                                        else []
                                    ):
                                        lower_start = time.perf_counter()
                                        measured = (
                                            circuit
                                            if level == "logical"
                                            else lower_circuit(
                                                circuit,
                                                basis_gates=["u", "cx"],
                                                seed=seed,
                                                optimization_level=config.get(
                                                    "optimization_level", 1
                                                ),
                                            )
                                        )
                                        if level == "common_basis" and not set(
                                            measured.count_ops()
                                        ) <= {"u", "cx"}:
                                            raise AssertionError(
                                                "Common basis contains non U/CX gates"
                                            )
                                        elapsed = time.perf_counter() - lower_start
                                        artifact = f"{name}_{component}_{level}.qpy"
                                        with (output / artifact).open("wb") as stream:
                                            qpy.dump(measured, stream)
                                        artifacts[f"{component}_{level}"] = artifact
                                        case_rows.append(
                                            {
                                                "benchmark": path.stem,
                                                "regime": regime,
                                                "component": component,
                                                "method": method,
                                                "iteration": iteration,
                                                "seed": seed,
                                                **circuit_metrics(measured),
                                                "metric_level": level,
                                                "artifact": artifact,
                                                "input_sha256": digest,
                                                "validation": assembled.metadata[
                                                    "validation"
                                                ]["status"],
                                                "role_counts": (
                                                    {"data": circuit.num_qubits}
                                                    if component
                                                    in ("preparation", "diffusion")
                                                    else assembled.metadata[
                                                        "role_counts"
                                                    ]
                                                ),
                                                "lowering_seconds": (
                                                    elapsed
                                                    if level == "common_basis"
                                                    else None
                                                ),
                                                "optimization_level": (
                                                    config.get("optimization_level", 1)
                                                    if level == "common_basis"
                                                    else None
                                                ),
                                            }
                                        )
                                case.update(status="complete", artifacts=artifacts)
                                rows.extend(case_rows)
                            except ExcludedCase as error:
                                case.update(status="excluded", reason=str(error))
                            except Exception as error:
                                case.update(
                                    status="failed",
                                    reason=f"{type(error).__name__}: {error}",
                                )
                            finally:
                                case["total_seconds"] = time.perf_counter() - started
                                (output / f"{name}.json").write_text(
                                    json.dumps(case, indent=2) + "\n"
                                )
                                save()
        manifest["status"] = (
            "complete_with_failures"
            if any(c["status"] == "failed" for c in manifest["cases"])
            else "complete"
        )
    except BaseException:
        manifest["status"] = "interrupted"
        raise
    finally:
        save()
    return output

"""Bounded FakeTorino gate/readout-noise trajectories and uniform random trials.

This experimental harness requires an admitted saved ideal pilot. It preserves
physical calibration qargs under active-wire compaction, and gates noise on a
routed noiseless marginal/restoration check. Delay relaxation is not modeled.
"""

from __future__ import annotations

import argparse
from copy import deepcopy
import importlib.metadata
import json
import math
import os
from pathlib import Path
import platform
import random
import signal
import subprocess
import sys
import time

from logique.benchmarks.iteration_study import (
    _digest,
    _integer,
    _problem,
    _word_classes,
    validate_config as validate_ideal_config,
)
from logique.paths import new_dump_directory

PILOT_HASH = "0047365f6e99a4be86261fa5a8610a58e46716b48b6c5f6c131cd9d6b309f811"
MEMORY_BYTES = 6 * 1024**3


def _write(path: Path, value: dict) -> None:
    """Atomically replace owned progress files; never expose truncated JSON."""
    temporary = path.with_name(path.name + ".pending")
    temporary.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")
    temporary.replace(path)


def validate_config(config: dict) -> None:
    """Validate every resource/control field before launching children."""
    if set(config) != {
        "ideal_pilot",
        "pilot_manifest_sha256",
        "execute",
        "shots",
        "random_batches",
        "max_qubits",
        "timeout_seconds",
        "budget_seconds",
        "seed",
        "tolerance",
        "optimization_level",
        "memory_bytes",
    }:
        raise ValueError("Unknown or missing noisy-study fields")
    for key, low, high in (
        ("shots", 1, 4096),
        ("random_batches", 1, 100000),
        ("max_qubits", 1, 18),
        ("timeout_seconds", 1, 120),
        ("budget_seconds", 1, 900),
        ("seed", 0, 2**30),
        ("optimization_level", 0, 3),
        ("memory_bytes", 128 * 1024**2, MEMORY_BYTES),
    ):
        _integer(config[key], key, low, high)
    if not 0 < config["tolerance"] <= 1e-8:
        raise ValueError("Invalid tolerance")
    if config["pilot_manifest_sha256"] != PILOT_HASH:
        raise ValueError("This harness requires the exact admitted ideal pilot")
    if not config["execute"] or len(set(config["execute"])) != len(config["execute"]):
        raise ValueError("Execution selections must be unique and nonempty")


def allocation_guard(width: int, config: dict) -> int:
    """Guard BEFORE arrays: at most 18 wires, eight complex vectors plus 128 MiB."""
    _integer(width, "active width", 0, config["max_qubits"])
    estimate = 8 * 16 * (1 << width) + 128 * 1024**2
    if estimate > config["memory_bytes"]:
        raise ValueError("Statevector working-set estimate exceeds memory budget")
    return estimate


def wilson(successes: int, trials: int) -> dict:
    """Pointwise 95% Wilson binomial interval, conditional on one fixed circuit."""
    if not 0 <= successes <= trials or trials < 1:
        raise ValueError("Invalid binomial counts")
    z = 1.959963984540054
    p = successes / trials
    denominator = 1 + z * z / trials
    center = (p + z * z / (2 * trials)) / denominator
    half = z * math.sqrt(p * (1 - p) / trials + z * z / (4 * trials**2)) / denominator
    return {
        "successes": successes,
        "trials": trials,
        "estimate": p,
        "interval_95": [max(0.0, center - half), min(1.0, center + half)],
        "method": "pointwise Wilson; no multiple-comparison correction",
    }


def cost_per_success(cost: float, successes: int, trials: int, basis: str) -> dict:
    """Price an IID restart only for a nonzero measured success probability."""
    return {
        "cost": cost,
        "basis": basis,
        "cost_over_measured_p": cost * trials / successes if successes else None,
        "status": "point_estimate" if successes else "unknown_zero_observed_successes",
        "scope": "IID restart point estimate, no ratio confidence interval; resource units cannot be equated",
    }


def compact_noise_dict(snapshot: dict, physical: list[int]) -> dict:
    """Relabel only local errors on retained physical qargs, preserving order.

    Never marginalize a correlated channel. Channels touching an omitted wire
    are unused by the compact circuit and omitted in their entirety. Nonlocal
    or default errors are unsupported, rather than silently approximated.
    """
    if len(set(physical)) != len(physical):
        raise ValueError("Duplicate physical wires")
    mapping = {q: i for i, q in enumerate(physical)}
    errors = []
    for original in snapshot["errors"]:
        if (
            original["type"] not in ("qerror", "roerror")
            or "gate_qubits" not in original
        ):
            raise ValueError("Unsupported default/nonlocal noise")
        if "noise_qubits" in original:
            raise ValueError("Nonlocal noise is unsupported")
        for qargs in original["gate_qubits"]:
            if all(q in mapping for q in qargs):
                error = deepcopy(original)
                error["gate_qubits"] = [[mapping[q] for q in qargs]]
                errors.append(error)
    return {"errors": errors}


def noise_from_snapshot(snapshot: dict):
    """Decode Aer JSON matrix scalars without changing channel or qarg order.

    Aer serializes each complex scalar as [real, imag], but from_dict does
    not decode it. Only matrix-valued Kraus/unitary parameters are decoded;
    probabilities, Pauli labels and instruction/qarg order remain untouched.
    Matrix dimensions are capped before conversion (at most two local wires).
    """
    import numpy as np
    from qiskit_aer.noise import NoiseModel

    decoded = deepcopy(snapshot)
    for error in decoded["errors"]:
        if error["type"] != "qerror":
            continue
        for branch in error["instructions"]:
            for instruction in branch:
                name = instruction["name"]
                if name not in ("kraus", "unitary"):
                    if "params" in instruction and name != "pauli":
                        raise ValueError(f"Unsupported channel instruction: {name}")
                    continue
                width = len(instruction["qubits"])
                if not 1 <= width <= 2:
                    raise ValueError("Channel matrix exceeds local two-wire limit")
                dim = 1 << width
                matrices = instruction["params"]
                if not 1 <= len(matrices) <= dim * dim:
                    raise ValueError("Invalid channel matrix count")
                converted = []
                for matrix in matrices:
                    if len(matrix) != dim or any(len(row) != dim for row in matrix):
                        raise ValueError("Invalid channel matrix dimensions")
                    values = []
                    for row in matrix:
                        entries = []
                        for scalar in row:
                            if not isinstance(scalar, list) or len(scalar) != 2:
                                raise ValueError(
                                    "Expected Aer JSON complex scalar pair"
                                )
                            if any(type(x) not in (int, float) for x in scalar):
                                raise ValueError("Invalid complex scalar components")
                            value = complex(*scalar)
                            if not (
                                math.isfinite(value.real) and math.isfinite(value.imag)
                            ):
                                raise ValueError("Nonfinite channel scalar")
                            entries.append(value)
                        values.append(entries)
                    converted.append(np.asarray(values, dtype=complex))
                instruction["params"] = converted
    return NoiseModel.from_dict(decoded)


def finalize_result(record: dict, status: str, shots: int) -> None:
    """Accept completion only with a nonempty full ledger and real shot counts."""
    for row in record["rows"]:
        counts = row.get("counts", {})
        counted = (
            bool(counts)
            and all(type(v) is int and v >= 0 for v in counts.values())
            and sum(counts.values()) == shots
        )
        if row.get("status") == "complete" and not counted:
            row["status"] = "partial_without_noisy_counts"
        elif row.get("status") in ("running", "not_started"):
            row["status"] = status
    record["status"] = (
        "complete"
        if record["rows"] and all(r["status"] == "complete" for r in record["rows"])
        else "partial_with_explicit_statuses"
    )


def execute_seed(request: dict) -> dict:
    """Persist all requested rows before setup and retain failure/interruption."""
    config = request["config"]
    validate_config(config)
    output = Path(request["output"])
    reference = json.loads(
        (Path(config["ideal_pilot"]) / request["name"] / "result.json").read_text()
    )
    output.mkdir(exist_ok=False)
    record = {
        "name": request["name"],
        "seed_transpiler": request["seed"],
        "status": "running",
        "owner_pid": os.getpid(),
        "rows": [
            {"iterations": row["iterations"], "status": "not_started"}
            for row in reference["analytical_ledger"]["rows"]
        ],
    }
    _write(output / "result.json", record)
    status = "not_executed_after_failure"
    try:
        return _execute_seed(request, record)
    except BaseException as exc:
        status = (
            "interrupted"
            if isinstance(exc, (KeyboardInterrupt, SystemExit))
            else "failed"
        )
        record["error"] = repr(exc)
        raise
    finally:
        finalize_result(record, status, config["shots"])
        _write(output / "result.json", record)


def compact_circuit(routed):
    """Remove only idle physical wires; retain active delays and classical bits."""
    from qiskit import QuantumCircuit

    physical = sorted(
        {
            routed.find_bit(q).index
            for item in routed.data
            if item.operation.name not in ("barrier", "delay")
            for q in item.qubits
        }
    )
    mapping = {q: i for i, q in enumerate(physical)}
    result = QuantumCircuit(len(physical), routed.num_clbits)
    result.global_phase = routed.global_phase
    for item in routed.data:
        wires = [routed.find_bit(q).index for q in item.qubits]
        if item.operation.name == "barrier":
            continue
        if not all(q in mapping for q in wires):
            if item.operation.name != "delay":
                raise ValueError("Compaction would discard an active instruction")
            continue
        result.append(
            item.operation,
            [mapping[q] for q in wires],
            [routed.find_bit(c).index for c in item.clbits],
        )
    return result, physical


def random_trials(
    problem, regime: str, iterations: int, batches: int, seed: int
) -> dict:
    """Execute independent uniform domain draws; classify without circuit code."""
    rng = random.Random(seed)
    good, valid = _word_classes(problem)
    bits = max(1, (problem.colors - 1).bit_length())
    n = len(problem.vertices)
    hits = leakage = 0
    trials = iterations + 1
    for _ in range(batches):
        found = False
        for _ in range(trials):
            if regime == "R1":
                word = rng.randrange(1 << (bits * n))
            else:
                word = sum(
                    rng.randrange(problem.colors) << (bits * i) for i in range(n)
                )
            found |= good[word]
            leakage += not valid[word]
        hits += found
    return {
        "seed": seed,
        "domain": "binary" if regime == "R1" else "valid_color_codes",
        "draws_per_batch": trials,
        "success_event": "at least one proper coloring in batch",
        "batch_success": wilson(hits, batches),
        "unused_code_per_draw": wilson(leakage, batches * trials),
        "analytical_batch_success": 1
        - (1 - sum(good) / (len(good) if regime == "R1" else problem.colors**n))
        ** trials,
        "cost_success": cost_per_success(
            trials, hits, batches, "uniform draw plus classical predicate evaluation"
        ),
    }


def measured_qpy_signature(circuit) -> dict:
    """Describe resolved measured/scheduled semantics without dense operators.

    Only flat standard gates, barriers, terminal measurements and delays are
    supported. Classical control, reset, opaque definitions and unbound values
    fail closed. Layout permutations retain the physical routing contract.
    """
    from qiskit.circuit import Barrier, Delay, Measure
    from logique.benchmarks.coloring_study import _qpy_standard_gate_classes

    if circuit.parameters:
        raise ValueError("Unbound QPY circuit")
    allowed = _qpy_standard_gate_classes() | {Barrier, Delay, Measure}
    phase = float(circuit.global_phase)
    if not math.isfinite(phase):
        raise ValueError("Nonfinite QPY phase")
    operations = []
    measured = set()
    for item in circuit.data:
        op = item.operation
        if op.base_class not in allowed or getattr(op, "condition", None) is not None:
            raise ValueError(f"Unsupported QPY operation: {op.name}")
        qargs = [circuit.find_bit(q).index for q in item.qubits]
        cargs = [circuit.find_bit(c).index for c in item.clbits]
        if op.name != "measure" and cargs:
            raise ValueError("Unsupported classical QPY operands")
        if op.name == "measure":
            if len(qargs) != 1 or len(cargs) != 1:
                raise ValueError("Malformed measurement")
            measured.update(qargs)
        elif op.name not in ("barrier", "delay") and measured.intersection(qargs):
            raise ValueError("Only terminal measurements are supported")
        params = []
        for param in op.params:
            value = complex(param)
            if not (math.isfinite(value.real) and math.isfinite(value.imag)):
                raise ValueError("Nonfinite QPY parameter")
            params.append([value.real.hex(), value.imag.hex()])
        operations.append(
            {
                "class": f"{op.base_class.__module__}.{op.base_class.__qualname__}",
                "name": op.name,
                "qargs": qargs,
                "cargs": cargs,
                "parameters": params,
                "unit": getattr(op, "unit", None),
                "controls": getattr(op, "num_ctrl_qubits", 0),
                "control_state": getattr(op, "ctrl_state", None),
            }
        )
    layout = circuit.layout
    return {
        "qubits": circuit.num_qubits,
        "clbits": circuit.num_clbits,
        "qregs": [
            (r.name, [circuit.find_bit(q).index for q in r]) for r in circuit.qregs
        ],
        "cregs": [
            (r.name, [circuit.find_bit(c).index for c in r]) for r in circuit.cregs
        ],
        "global_phase": phase.hex(),
        "operations": operations,
        "layout": (
            None
            if layout is None
            else {
                "initial": layout.initial_index_layout(filter_ancillas=False),
                "final": layout.final_index_layout(filter_ancillas=False),
                "routing_permutation": layout.routing_permutation(),
                "input_qubit_count": layout._input_qubit_count,
                "input_order": list(layout.input_qubit_mapping.values()),
            }
        ),
    }


def save_qpy(path: Path, circuit):
    """Save/read back measured scalar/gate/delay/layout semantics exactly."""
    from qiskit import qpy

    signature = measured_qpy_signature(circuit)
    with path.open("xb") as stream:
        qpy.dump(circuit, stream)
    with path.open("rb") as stream:
        loaded = qpy.load(stream)
    if len(loaded) != 1 or measured_qpy_signature(loaded[0]) != signature:
        raise AssertionError("QPY measured/scheduled semantics changed")
    return loaded[0]


def _components(problem, regime: str):
    from qiskit import QuantumCircuit, transpile
    from logique.circuits.structure import structure_oracle
    from logique.circuits.grover import coloring_preparation, _reflection
    from logique.coloring import encode_coloring
    from logique.benchmarks.costs import decompose_mcx
    from logique.benchmarks.routing import prelower
    from logique.benchmarks.coloring_study import _resolved_qpy_circuit

    result = structure_oracle(
        problem, domain_policy="domain_free" if regime == "R3" else "complete"
    )
    n = max(1, (problem.colors - 1).bit_length()) * len(problem.vertices)
    preparation = QuantumCircuit(n)
    if regime == "R1":
        preparation.h(range(n))
    else:
        preparation = coloring_preparation(encode_coloring(problem))
    diffusion = _reflection(preparation)
    diffusion.global_phase += math.pi
    parts = []
    policies = []
    for circuit in (preparation, result.phase_oracle(), diffusion):
        expanded, policy = decompose_mcx(circuit, "noaux_v24")
        resolved, _ = _resolved_qpy_circuit(expanded)
        parts.append(
            transpile(prelower(resolved), basis_gates=["u", "cx"], optimization_level=0)
        )
        policies.append(policy)
    return parts, policies


def _execute_seed(request: dict, record: dict) -> dict:
    """Route one case/seed sweep and execute calibration-preserving trajectories."""
    from qiskit import QuantumCircuit, qpy, transpile
    from qiskit.quantum_info import Statevector
    from qiskit_aer import AerSimulator
    from qiskit_aer.noise import NoiseModel
    import numpy as np
    from logique.benchmarks.routing import default_backend, _seed_metrics

    config = request["config"]
    validate_config(config)
    output = Path(request["output"])
    pilot = Path(config["ideal_pilot"])
    reference = json.loads((pilot / request["name"] / "result.json").read_text())
    case, regime, seed = reference["case"], reference["regime"], request["seed"]
    problem = _problem(case)
    width = reference["construction"]["width"]
    allocation_guard(width, config)
    backend = default_backend()
    snapshot_dir = output.parent / "backend"
    if not snapshot_dir.exists():
        snapshot_dir.mkdir()
        for kind, filename in (
            ("properties", backend.props_filename),
            ("configuration", backend.conf_filename),
        ):
            (snapshot_dir / f"{kind}.json").write_bytes(
                (Path(backend.dirname) / filename).read_bytes()
            )
        _write(
            snapshot_dir / "noise.json",
            NoiseModel.from_backend(backend).to_dict(serializable=True),
        )
        _write(
            snapshot_dir / "versions.json",
            {
                "backend": backend.name,
                "backend_version": backend.backend_version,
                "versions": {
                    name: importlib.metadata.version(name)
                    for name in ("qiskit", "qiskit-aer", "qiskit-ibm-runtime", "numpy")
                },
                "noise": "NoiseModel.from_backend defaults: gate_error/readout_error/thermal_relaxation True; gate-length thermal noise; no idle-delay relaxation",
            },
        )
    snapshot = json.loads((snapshot_dir / "noise.json").read_text())
    parts, policies = _components(problem, regime)
    if parts[1].num_qubits != width:
        raise AssertionError("Explicit policy changed admitted workspace width")
    n = reference["counts"]["data_bits"]
    good, valid = [np.asarray(x, dtype=bool) for x in _word_classes(problem)]
    ideal_parts = []
    for name in ("preparation", "oracle", "diffusion"):
        with (pilot / request["name"] / f"{name}.qpy").open("rb") as stream:
            ideal_parts.append(qpy.load(stream)[0])
    ideal_state = Statevector.from_int(0, 1 << width).evolve(
        ideal_parts[0], list(range(n))
    )
    record.update(
        {
            "name": request["name"],
            "seed_transpiler": seed,
            "case": case,
            "regime": regime,
            "mcx_policy": "noaux_v24; restoring static unitary, no appended scratch",
            "mcx_details": policies,
            "status": "running",
            "noise_scope": "calibrated physical gate/readout errors with per-gate thermal relaxation; scheduled idle delays noiseless; no crosstalk/drift",
            "simulator": {
                "method": "statevector",
                "device": "CPU",
                "validation_threshold": config["tolerance"],
                "zero_threshold": 1e-14,
                "enable_truncation": False,
                "shots": config["shots"],
                "max_parallel_threads": 1,
                "max_parallel_shots": 1,
                "max_parallel_experiments": 1,
                "max_memory_mb": config["memory_bytes"] // 1024**2,
            },
            "confidence_scope": "pointwise binomial shot uncertainty conditional on this fixed routed seed; seeds are distinct implementations, never pooled",
        }
    )
    logical = QuantumCircuit(width, n)
    logical.compose(parts[0], range(n), inplace=True)
    requested = {row["iterations"]: row for row in record["rows"]}
    for old in reference["rows"]:
        j = old["iterations"]
        row = requested[j]
        row["status"] = "running"
        _write(output / "result.json", record)
        if j:
            logical.compose(parts[1], inplace=True)
            logical.compose(parts[2], range(n), inplace=True)
            ideal_state = ideal_state.evolve(ideal_parts[1]).evolve(
                ideal_parts[2], list(range(n))
            )
        expected = ideal_state.probabilities(list(range(n)))
        circuit = logical.copy()
        circuit.measure(range(n), range(n))
        row_dir = output / f"j{j}"
        row_dir.mkdir()
        circuit = save_qpy(row_dir / "logical.qpy", circuit)
        routed = transpile(
            circuit,
            backend=backend,
            seed_transpiler=seed,
            optimization_level=config["optimization_level"],
            scheduling_method="alap",
        )
        routed = save_qpy(row_dir / "routed.qpy", routed)
        compact, physical = compact_circuit(routed)
        final = routed.layout.final_index_layout(filter_ancillas=True)
        metrics = _seed_metrics(routed, backend.target)
        row.update(
            {
                "iterations": j,
                "analytical_prediction": old["analytical_ledger_prediction"],
                "admitted_ideal_execution": old["simulated_valid_solution_probability"],
                "routed_metrics": metrics,
                "esp_kind": "calibration error product, not noisy success",
                "active_physical_wires": physical,
                "initial_layout": routed.layout.initial_index_layout(
                    filter_ancillas=False
                )[:width],
                "final_layout": final,
                "duration_kind": "ALAP target estimate, seconds",
                "duration_s": metrics["duration_s"],
                "random": random_trials(
                    problem,
                    regime,
                    j,
                    config["random_batches"],
                    config["seed"] + seed * 100 + j,
                ),
            }
        )
        _write(output / "result.json", record)
        if len(physical) > config["max_qubits"]:
            row.update(
                status="compact_noise_infeasible",
                reason=f"{len(physical)} active > {config['max_qubits']}",
            )
            continue
        row["working_set_estimate_bytes"] = allocation_guard(len(physical), config)
        compact = save_qpy(row_dir / "compact.qpy", compact)
        measured = {}
        for item in compact.data:
            if item.operation.name == "measure":
                measured[compact.find_bit(item.clbits[0]).index] = compact.find_bit(
                    item.qubits[0]
                ).index
        if sorted(measured) != list(range(n)):
            raise AssertionError("Measurement classification lost logical data bits")
        row["measurement_compact_wires_lsb_first"] = [measured[i] for i in range(n)]
        pure = compact.remove_final_measurements(inplace=False)
        if any(item.operation.num_qubits > 2 for item in pure.data):
            raise ValueError("No wide matrix simulation permitted")
        state = Statevector.from_instruction(pure)
        marginal = state.probabilities([measured[i] for i in range(n)])
        residual = float(np.max(np.abs(marginal - expected)))
        workspace = [physical.index(p) for p in final[n:] if p in physical]
        restored = float(state.probabilities(workspace)[0]) if workspace else 1.0
        norm = float(np.vdot(state.data, state.data).real)
        if abs(norm - 1) > config["tolerance"]:
            raise ValueError("Routed statevector norm outside declared tolerance")
        row["routed_noiseless_validation"] = {
            "state_norm_squared": norm,
            "norm_tolerance": config["tolerance"],
            "max_data_marginal_error": residual,
            "restored_workspace_probability": restored,
            "success": float(marginal[good].sum()),
            "unused_code_leakage": float(marginal[~valid].sum()),
            "comparison": "independent admitted saved U/CX components, all data words and mapped final workspace",
        }
        # Reconstruct the complete routed pure state in final physical order.
        # Probabilities alone do not establish coherent routing equivalence.
        full_expected = np.zeros(1 << len(physical), dtype=complex)
        for word, amplitude in enumerate(ideal_state.data):
            if abs(amplitude) == 0:
                continue
            packed = 0
            for logical_wire, physical_wire in enumerate(final):
                if (word >> logical_wire) & 1:
                    if physical_wire not in physical:
                        raise AssertionError("Nonzero ideal wire omitted by compaction")
                    packed |= 1 << physical.index(physical_wire)
            full_expected[packed] = amplitude
        overlap = np.vdot(full_expected, state.data)
        coherent_error = float(
            np.max(
                np.abs(
                    state.data
                    - full_expected * (overlap / abs(overlap) if abs(overlap) else 1)
                )
            )
        )
        row["routed_noiseless_validation"][
            "full_state_error_up_to_global_phase"
        ] = coherent_error
        del state, full_expected
        if (
            max(
                residual,
                coherent_error,
                abs(restored - 1),
                abs(
                    float(marginal[good].sum())
                    - old["simulated_valid_solution_probability"]
                ),
            )
            > config["tolerance"]
        ):
            row.update(status="failed_routed_validation", noisy_success=None)
            continue
        compact_snapshot = compact_noise_dict(snapshot, physical)
        _write(row_dir / "compact_noise.json", compact_snapshot)
        noise = noise_from_snapshot(compact_snapshot)
        sim_seed = config["seed"] + seed * 100 + j
        simulator = AerSimulator(noise_model=noise, **record["simulator"])
        row.update(stage="validated_pre_sampling", seed_simulator=sim_seed)
        # A killed/blocking sampler cannot flush anything after run(). Persist
        # validated metadata while leaving status running and counts absent.
        _write(output / "result.json", record)
        result = simulator.run(
            compact, shots=config["shots"], seed_simulator=sim_seed
        ).result()
        if not result.success:
            raise RuntimeError(str(result))
        counts = result.get_counts()
        successes = sum(
            count
            for word, count in counts.items()
            if good[int(word.replace(" ", ""), 2)]
        )
        leakage = sum(
            count
            for word, count in counts.items()
            if not valid[int(word.replace(" ", ""), 2)]
        )
        if sum(counts.values()) != config["shots"]:
            raise AssertionError("Shot accounting failure")
        row.update(
            status="complete",
            stage="sampling_complete",
            seed_simulator=sim_seed,
            counts=counts,
            noisy_success=wilson(successes, config["shots"]),
            noisy_unused_code_leakage=wilson(leakage, config["shots"]),
            cost_success=cost_per_success(
                metrics["two_qubit_count"],
                successes,
                config["shots"],
                "routed native two-qubit gates per measured proper output; excludes classical validation",
            ),
            aer_metadata=result.results[0].metadata,
        )
        _write(output / "result.json", record)
    record["status"] = (
        "complete"
        if all(r["status"] == "complete" for r in record["rows"])
        else "partial_with_explicit_statuses"
    )
    _write(output / "result.json", record)
    return record


def supervise(
    command: list[str], log: Path, env: dict, seconds: float, memory_bytes: int
) -> dict:
    """Own, reap and receipt one thread-only child with conservative deadlines.

    Missing RSS visibility stops safely before accepting results. Sampled RSS
    is not a hard allocation cap; wait4 high-water may include descendants.
    A sidecar receipt is written even for setup, sampling and cleanup failures.
    """
    start = time.monotonic()
    deadline = start + seconds
    child = None
    pid = 0
    status = usage = None
    peak = 0
    reason = None
    errors = []
    sampling = "not_sampled"
    receipt_path = log.with_suffix(log.suffix + ".receipt.json")
    # Refuse existing evidence before taking ownership of any process.
    with log.open("x") as stream, receipt_path.open("x") as receipt_stream:
        try:
            child = subprocess.Popen(
                command,
                env=env,
                stdout=stream,
                stderr=subprocess.STDOUT,
                start_new_session=True,
            )
            while True:
                if time.monotonic() >= deadline:
                    reason = "timeout"
                    break
                pid, status, usage = os.wait4(child.pid, os.WNOHANG)
                if time.monotonic() >= deadline:
                    reason = "timeout"
                if pid or reason:
                    break
                try:
                    remaining = deadline - time.monotonic()
                    if remaining <= 0:
                        reason = "timeout"
                        break
                    probe = subprocess.run(
                        ["ps", "-o", "rss=", "-p", str(child.pid)],
                        capture_output=True,
                        text=True,
                        timeout=min(0.2, remaining),
                    )
                    if probe.returncode == 0 and probe.stdout.strip():
                        peak = max(peak, int(probe.stdout.strip()) * 1024)
                        sampling = "available"
                    else:
                        # An exited child can disappear between wait4 and ps.
                        pid, status, usage = os.wait4(child.pid, os.WNOHANG)
                        if pid:
                            if time.monotonic() >= deadline:
                                reason = "timeout"
                            break
                        sampling = "unavailable"
                        reason = "memory_sampling_unavailable"
                        errors.append(probe.stderr.strip())
                        break
                    if peak > memory_bytes:
                        reason = "memory_limit"
                        break
                except subprocess.TimeoutExpired:
                    # No unobserved work is admitted; another bounded probe may retry.
                    if time.monotonic() >= deadline:
                        reason = "timeout"
                        break
                except (OSError, ValueError) as exc:
                    sampling = "unavailable"
                    reason = "memory_sampling_unavailable"
                    errors.append(repr(exc))
                    break
                time.sleep(min(0.05, max(0, deadline - time.monotonic())))
        except BaseException as exc:
            reason = (
                "interrupted"
                if isinstance(exc, (KeyboardInterrupt, SystemExit))
                else ("supervision_failed" if child is not None else "launch_failed")
            )
            errors.append(repr(exc))
        finally:
            try:
                if child is not None and not pid:
                    # Reap before signaling: the child may have exited after observation.
                    pid, status, usage = os.wait4(child.pid, os.WNOHANG)
                    if not pid:
                        try:
                            os.killpg(child.pid, signal.SIGKILL)
                        except ProcessLookupError:
                            pass
                        except OSError as exc:
                            errors.append(repr(exc))
                            # killpg may race leader exit. Retry reap before direct kill.
                            pid, status, usage = os.wait4(child.pid, os.WNOHANG)
                            if not pid:
                                child.kill()
                        if not pid:
                            pid, status, usage = os.wait4(child.pid, 0)
            except Exception as exc:
                errors.append(f"cleanup failed: {exc!r}")
                reason = "cleanup_failed"
            if child is not None and status is not None:
                child.returncode = os.waitstatus_to_exitcode(status)
            elapsed = time.monotonic() - start
            if reason is None and elapsed >= seconds:
                reason = "timeout"
            receipt = {
                "command": command,
                "seconds": elapsed,
                "limit_seconds": seconds,
                "memory_limit_bytes": memory_bytes,
                "returncode": child.returncode if child else None,
                "status": reason or ("finished" if child.returncode == 0 else "failed"),
                "child_pid": child.pid if child else None,
                "reaped": bool(pid),
                "errors": errors,
                "rss_sampling": sampling,
                "sampled_direct_child_peak_rss_bytes": peak or None,
                "wait4_invocation_high_water_bytes": (
                    None
                    if usage is None
                    else int(
                        usage.ru_maxrss * (1 if sys.platform == "darwin" else 1024)
                    )
                ),
                "rss_scope": "sampled direct child only; unavailable sampling stops safely; wait4 may include reaped descendants; not group RSS or a hard allocation cap",
            }
            json.dump(receipt, receipt_stream, indent=2)
            receipt_stream.write("\n")
    return receipt


def _requested_scope(
    admitted: dict, pilot: Path, selected: list[str], seeds: tuple[int, ...]
) -> list[dict]:
    """Build every analytical iteration/seed request before taking child ownership."""
    entries = []
    for case in admitted["cases"]:
        result = json.loads((pilot / case["name"] / "result.json").read_text())
        iterations = [r["iterations"] for r in result["analytical_ledger"]["rows"]]
        status = (
            "ideal_infeasible"
            if result["status"] == "infeasible"
            else (
                "not_launched"
                if case["name"] in selected
                else "not_executed_bounded_pilot"
            )
        )
        entries.append(
            {
                "name": case["name"],
                "ideal_status": result["status"],
                "width": result["construction"]["width"],
                "analytical_ledger": result["analytical_ledger"],
                "noise_status": ("scheduled" if case["name"] in selected else status),
                "reason": result.get("reason"),
                "next_action": "retain complete requested domain; extend bounded routed/noisy sweep after independent review; C5 R1/R2 need separately admitted lower workspace",
                "seeds": [
                    {
                        "seed": seed,
                        "requested_iterations": iterations.copy(),
                        "iteration_statuses": [
                            {"iterations": j, "status": status} for j in iterations
                        ],
                        "process_status": status,
                        "result_status": None,
                        "completed_iterations": [],
                    }
                    for seed in seeds
                ],
            }
        )
    return entries


def _reconcile_scope(manifest: dict, output: Path, shots: int) -> None:
    """Reconcile terminal ownership without dropping unexecuted analytical rows."""
    children = {c["name"]: c for c in manifest["children"]}
    for entry in manifest["scope_ledger"]:
        for seed in entry["seeds"]:
            label = f"{entry['name']}_seed{seed['seed']}"
            child = children.get(label)
            if child is None:
                continue
            if child["status"] == "launching":
                child["status"] = "interrupted_without_receipt"
            result_path = output / label / "result.json"
            result = None
            if result_path.exists():
                result = json.loads(result_path.read_text())
                finalize_result(result, child["status"], shots)
                _write(result_path, result)
            elif child["status"] == "finished":
                child["status"] = "empty_child_result"
            seed["process_status"] = child["status"]
            seed["result_status"] = result["status"] if result else None
            rows = {r["iterations"]: r for r in result["rows"]} if result else {}
            seed["iteration_statuses"] = [
                {
                    "iterations": j,
                    "status": (
                        rows[j]["status"]
                        if j in rows
                        else (
                            "missing_child_row"
                            if child["status"] == "finished"
                            else child["status"]
                        )
                    ),
                }
                for j in seed["requested_iterations"]
            ]
            seed["completed_iterations"] = [
                r["iterations"]
                for r in seed["iteration_statuses"]
                if r["status"] == "complete"
            ]
        if entry["name"] in manifest["config"]["execute"]:
            entry["noise_status"] = (
                "complete"
                if all(
                    s["process_status"] == "finished"
                    and s["result_status"] == "complete"
                    and s["requested_iterations"]
                    and s["completed_iterations"] == s["requested_iterations"]
                    for s in entry["seeds"]
                )
                else "partial_or_failed"
            )


def run_study(config: dict, root: Path = Path("dump")) -> Path:
    """Verify ideal evidence, retain full requested ledger, then run serial pilot."""
    from logique.benchmarks.routing import SEEDS

    validate_config(config)
    pilot = Path(config["ideal_pilot"])
    if _digest(pilot / "manifest.json") != config["pilot_manifest_sha256"]:
        raise ValueError("Admitted pilot manifest hash mismatch")
    admitted = json.loads((pilot / "manifest.json").read_text())
    for name, digest in admitted["evidence_hashes"].items():
        if _digest(pilot / name) != digest:
            raise ValueError(f"Admitted pilot evidence mismatch: {name}")
    validate_ideal_config(admitted["config"])
    names = {r["name"] for r in admitted["cases"]}
    if not set(config["execute"]) <= names:
        raise ValueError("Unknown selected pilot case")
    scope = _requested_scope(admitted, pilot, config["execute"], SEEDS)
    output = new_dump_directory("noisy-iteration-study", root=root)
    source = Path(__file__).resolve().parents[2]
    env = dict(os.environ, PYTHONPATH=str(source), QISKIT_PARALLEL="FALSE")
    for key in (
        "OMP_NUM_THREADS",
        "OPENBLAS_NUM_THREADS",
        "MKL_NUM_THREADS",
        "VECLIB_MAXIMUM_THREADS",
        "NUMEXPR_NUM_THREADS",
        "RAYON_NUM_THREADS",
    ):
        env[key] = "1"
    manifest = {
        "status": "running",
        "config": config,
        "source": str(source),
        "module": str(Path(__file__).resolve()),
        "python": sys.executable,
        "platform": platform.platform(),
        "seeds": list(SEEDS),
        "git_head": None,
        "task": "noisy-channel-repair-1029204240",
        "session": os.environ.get("CODEX_THREAD_ID"),
        "admitted_ideal_manifest": str(pilot / "manifest.json"),
        "admitted_ideal_hash": PILOT_HASH,
        "source_hashes": {},
        "scope_ledger": scope,
        "children": [
            {"name": f"{e['name']}_seed{s['seed']}", "status": s["process_status"]}
            for e in scope
            if e["name"] in config["execute"]
            for s in e["seeds"]
        ],
        "thread_environment": {
            k: v
            for k, v in env.items()
            if k.endswith("THREADS") or k == "QISKIT_PARALLEL"
        },
        "memory_contract": "6GiB maximum config; preallocation working-set guards plus sampled direct child RSS kill; no full density matrices or full Operators; at most18 active wires",
        "noise_contract": "physical gate/readout channel remapping; idle delay relaxation excluded; independent review required",
    }
    started = time.monotonic()
    interruption = None
    try:
        _write(output / "config.json", config)
        _write(output / "manifest.json", manifest)
        manifest["git_head"] = subprocess.check_output(
            ["git", "rev-parse", "HEAD"], text=True
        ).strip()
        for name in (
            "noisy_iterations.py",
            "iteration_study.py",
            "ideal_iterations.py",
            "routing.py",
            "costs.py",
            "coloring_study.py",
        ):
            path = Path(__file__).with_name(name)
            manifest["source_hashes"][str(path)] = _digest(path)
        for path in (
            source / "logique/circuits/grover.py",
            source / "logique/circuits/structure.py",
        ):
            manifest["source_hashes"][str(path)] = _digest(path)
        native = env.get("LOGIQUE_NATIVE_EXECUTABLE")
        manifest["native"] = {
            "invoked": False,
            "path": native,
            "sha256": _digest(Path(native)) if native else None,
        }
        if (
            native
            and manifest["native"]["sha256"]
            != "6aa7357d2f64202584b14b0a14f8fb183379faf5907723cd24bd838b9be14a9a"
        ):
            raise ValueError("Unexpected native provenance")
        _write(output / "manifest.json", manifest)
        for name in config["execute"]:
            for seed in SEEDS:
                remaining = config["budget_seconds"] - (time.monotonic() - started)
                label = f"{name}_seed{seed}"
                ownership = next(c for c in manifest["children"] if c["name"] == label)
                if ownership["status"] == "ideal_infeasible":
                    continue
                request = {
                    "config": config,
                    "name": name,
                    "seed": seed,
                    "output": str(output / label),
                }
                path = output / f"{label}_request.json"
                _write(path, request)
                if remaining <= 0:
                    next(c for c in manifest["children"] if c["name"] == label).update(
                        status="budget_excluded"
                    )
                    _write(output / "manifest.json", manifest)
                    continue
                command = [
                    sys.executable,
                    "-m",
                    "logique.benchmarks.noisy_iterations",
                    "--child",
                    str(path),
                ]
                ownership.update(status="launching", request=str(path))
                _write(output / "manifest.json", manifest)
                receipt = supervise(
                    command,
                    output / f"{label}.log",
                    env,
                    min(remaining, config["timeout_seconds"]),
                    config["memory_bytes"],
                )
                receipt["name"] = label
                ownership.update(receipt)
                _write(output / "manifest.json", manifest)
                if receipt["status"] == "interrupted":
                    raise KeyboardInterrupt("Owned child interrupted")
    except BaseException as exc:
        interruption = repr(exc)
    manifest["interruption"] = interruption
    _reconcile_scope(manifest, output, config["shots"])
    manifest.update(
        status=(
            "interrupted_schedule_not_scientific_admission"
            if interruption
            else "finished_schedule_not_scientific_admission"
        ),
        seconds=time.monotonic() - started,
    )
    manifest["evidence_hashes"] = {
        str(p.relative_to(output)): _digest(p)
        for p in sorted(output.rglob("*"))
        if p.is_file() and p.name != "manifest.json"
    }
    _write(output / "manifest.json", manifest)
    return output


def main() -> None:
    """Run the serial bounded pilot or its one owned child."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path)
    parser.add_argument("--child", type=Path, help=argparse.SUPPRESS)
    args = parser.parse_args()

    def interrupted(signum, frame):
        raise KeyboardInterrupt(f"Received signal {signum}")

    signal.signal(signal.SIGTERM, interrupted)
    if args.child:
        execute_seed(json.loads(args.child.read_text()))
    elif args.config:
        print(run_study(json.loads(args.config.read_text())))
    else:
        parser.error("--config required")


if __name__ == "__main__":
    main()

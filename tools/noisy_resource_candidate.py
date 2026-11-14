"""Analyze the selected saved request; run only synthetic trajectory fixtures.

No command in this tool executes a saved scientific circuit. The prospective
change is dense statevector trajectories with fusion disabled, retaining the
frozen noise decoder. Exact here means no added model approximation; complex128
roundoff and the inherited Aer noise implementation still require review.
"""

from __future__ import annotations

import argparse
from collections import Counter
from copy import deepcopy
import hashlib
import importlib.metadata
import json
from pathlib import Path
import time

from logique.benchmarks.noisy_iterations import noise_from_snapshot

SELECTED = Path("prepared/1101145422-noisy-remaining-requests/K3_k3_R2_seed37")
MEMORY_BYTES = 2 * 1024**3


def source_contract() -> dict:
    """Assert candidate imports and bind the two current inherited modules."""
    from logique.benchmarks import iteration_study, noisy_iterations

    source = Path(__file__).resolve().parents[1] / "src"
    hashes = {}
    for module, expected in (
        (
            noisy_iterations,
            "0630dc70ecd0a8490acdff8dd661c2e939644be18bd500dd8be91dbae5e22385",
        ),
        (
            iteration_study,
            "c941aef068bb848174652644530d9f3fafc8e4e55c872f34b619753f76bd22c5",
        ),
    ):
        relative = module.__name__.replace(".", "/") + ".py"
        path = Path(module.__file__).resolve()
        if path != source / relative or digest(path) != expected:
            raise ValueError(f"Candidate source identity mismatch: {relative}")
        hashes[relative] = expected
    return hashes


def digest(path: Path) -> str:
    """Return an exact saved-byte identity."""
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_new(path: Path, value: dict) -> None:
    """Write new evidence exclusively, preserving every previous artifact."""
    with path.open("x") as stream:
        json.dump(value, stream, indent=2, sort_keys=True)
        stream.write("\n")


def trajectory_options(*, fusion: bool = False) -> dict:
    """Describe the fixed64-shot serial candidate without changing channels.

    Fusion changes evaluation grouping, not the physical input instruction
    sequence. Disabling it avoids fused channel matrices wider than the local
    two-wire inventory. No alternate unraveling or MPS is substituted.
    """
    return {
        "method": "statevector",
        "device": "CPU",
        "precision": "double",
        "enable_truncation": False,
        "validation_threshold": 1e-10,
        "zero_threshold": 1e-14,
        "shots": 64,
        "max_parallel_threads": 1,
        "max_parallel_shots": 1,
        "max_parallel_experiments": 1,
        "max_memory_mb": MEMORY_BYTES // 1024**2,
        "fusion_enable": fusion,
        "shot_branching_enable": False,
        "shot_branching_sampling_enable": False,
    }


def channel_inventory(snapshot: dict, circuit) -> dict:
    """Count local channel applications in original ordered operand context."""
    applications = Counter(
        (item.operation.name, tuple(circuit.find_bit(q).index for q in item.qubits))
        for item in circuit.data
    )
    entries = []
    keys = set()
    for error in snapshot["errors"]:
        if error["type"] not in ("qerror", "roerror") or "noise_qubits" in error:
            raise ValueError("Unsupported noise scope")
        for qargs in error["gate_qubits"]:
            if not 1 <= len(qargs) <= 2 or len(set(qargs)) != len(qargs):
                raise ValueError("Only ordered local one/two-wire channels supported")
            if any(
                type(q) is not int or not 0 <= q < circuit.num_qubits for q in qargs
            ):
                raise ValueError("Channel operand outside compact circuit")
            for operation in error["operations"]:
                key = (error["type"], operation, tuple(qargs))
                if key in keys:
                    raise ValueError(
                        "Duplicate channel key requires explicit composition"
                    )
                keys.add(key)
                entries.append(
                    {
                        "type": error["type"],
                        "operation": operation,
                        "ordered_compact_qargs": qargs,
                        "applications_per_shot": applications[
                            (operation, tuple(qargs))
                        ],
                        "payload_sha256": hashlib.sha256(
                            json.dumps(error, sort_keys=True).encode()
                        ).hexdigest(),
                    }
                )
    return {
        "records": len(snapshot["errors"]),
        "entries": entries,
        "quantum_applications_per_shot": sum(
            e["applications_per_shot"] for e in entries if e["type"] == "qerror"
        ),
        "readout_applications_per_shot": sum(
            e["applications_per_shot"] for e in entries if e["type"] == "roerror"
        ),
    }


def analyze_saved(evidence: Path, config: dict) -> dict:
    """Inspect exact QPY/JSON bytes without evolving or sampling saved inputs."""
    from qiskit import qpy

    evidence = evidence.resolve()
    for relative, expected in config["inputs"].items():
        path = (evidence / relative).resolve()
        if not path.is_relative_to(evidence) or digest(path) != expected:
            raise ValueError(f"Input identity mismatch: {relative}")
    manifest = json.loads((evidence / "manifest.json").read_text())
    for relative, expected in manifest["files"].items():
        path = (evidence / relative).resolve()
        if not path.is_relative_to(evidence) or digest(path) != expected:
            raise ValueError(f"Manifest identity mismatch: {relative}")
    record = json.loads((evidence / SELECTED / "result.json").read_text())
    row = record["rows"][0]
    if (
        record["name"] != "K3_k3_R2"
        or record["seed_transpiler"] != 37
        or record["requested_iterations"] != [2]
        or len(record["rows"]) != 1
        or record["simulator"]["shots"] != 64
        or row["seed_simulator"] != 74730
        or row["stage"] != "validated_pre_sampling"
        or "counts" in row
    ):
        raise ValueError("Frozen caller contract mismatch")
    with (evidence / SELECTED / "j2/compact.qpy").open("rb") as stream:
        circuits = qpy.load(stream)
    if len(circuits) != 1 or circuits[0].num_qubits != 18:
        raise ValueError("Expected one saved18-wire circuit")
    circuit = circuits[0]
    measured = {}
    terminal = False
    for item in circuit.data:
        if item.operation.name == "measure":
            terminal = True
            cbit = circuit.find_bit(item.clbits[0]).index
            if cbit in measured:
                raise ValueError("Repeated measurement")
            measured[cbit] = circuit.find_bit(item.qubits[0]).index
        elif item.operation.name != "barrier":
            if terminal or item.operation.num_qubits > 2:
                raise ValueError("Unexpected circuit operation/order")
    if measured != dict(enumerate([4, 5, 1, 3, 6, 10])):
        raise ValueError("Frozen LSB measurement ordering changed")
    snapshot = json.loads((evidence / SELECTED / "j2/compact_noise.json").read_text())
    inventory = channel_inventory(snapshot, circuit)
    if inventory["records"] != 126:
        raise ValueError("Expected126 unchanged local channel records")
    counts = dict(circuit.count_ops())
    return {
        "kind": "static_saved_input_analysis_not_execution",
        "input_hashes": config["inputs"],
        "verified_manifest_entries": len(manifest["files"]),
        "width": circuit.num_qubits,
        "instructions": len(circuit.data),
        "operation_counts": counts,
        "measurement_compact_wires_lsb_first": [measured[i] for i in range(6)],
        "active_physical_wires": row["active_physical_wires"],
        "initial_layout": row["initial_layout"],
        "final_layout": row["final_layout"],
        "saved_coherent_validation_attributed_only": row["routed_noiseless_validation"],
        "channels": inventory,
        "resource_arithmetic": {
            "complex128_vector_bytes": 16 * 2**18,
            "inherited_eight_vector_plus128MiB_estimate_bytes": 8 * 16 * 2**18
            + 128 * 1024**2,
            "full_density_bytes_forbidden": 16 * 4**18,
            "two_qubit_gates_times64": 2590 * 64,
            "deadline_seconds_per_requested_shot_before_setup": 120 / 64,
        },
        "candidate_options": trajectory_options(),
        "scientific_sampling": "BLOCK_pending_independent_method_and_resource_review",
        "runtime_forecast_seconds": None,
        "timeout_stage_attribution": "No internal Aer timing in prior receipt",
    }


def synthetic_fixture(width: int, layers: int):
    """Build a fixed non-observation with asymmetric ordered local noise."""
    from qiskit import QuantumCircuit
    from qiskit_aer.noise import NoiseModel, ReadoutError, amplitude_damping_error

    if width not in (3, 18) or layers != 4:
        raise ValueError("Only prebounded synthetic fixtures are permitted")
    circuit = QuantumCircuit(width, 2)
    for layer in range(layers):
        for wire in range(width):
            circuit.ry(0.13 * (wire + 1), wire)
            circuit.rz(0.31 + layer * 0.07, wire)
        for wire in range(width - 1, 0, -1):
            circuit.cx(wire, wire - 1)
        circuit.sx(0)
    circuit.measure(width - 1, 0)
    circuit.measure(0, 1)
    noise = NoiseModel()
    noise.add_quantum_error(amplitude_damping_error(0.17), "sx", [0])
    pair = amplitude_damping_error(0.13).tensor(amplitude_damping_error(0.31))
    noise.add_quantum_error(pair, "cx", [width - 1, width - 2])
    noise.add_readout_error(ReadoutError([[0.83, 0.17], [0.09, 0.91]]), [0])
    return circuit, noise.to_dict(serializable=True)


def profile_fixture(output: Path, width: int, fusion: bool) -> dict:
    """Time only generated fixtures, persisting stages before blocking calls.

    run() submission can itself block. These API boundaries do not distinguish
    compiler versus sampling internals. Aer metadata is retained verbatim.
    """
    from qiskit_aer import AerSimulator

    start = time.monotonic()
    stages = []

    def stamp(stage: str) -> None:
        entry = {"stage": stage, "elapsed_seconds": time.monotonic() - start}
        stages.append(entry)
        write_new(output / f"stage-{len(stages):02}.json", entry)

    circuit, snapshot = synthetic_fixture(width, 4)
    stamp("synthetic_fixture_built")
    noise = noise_from_snapshot(snapshot)
    stamp("noise_decoded")
    simulator = AerSimulator(noise_model=noise, **trajectory_options(fusion=fusion))
    stamp("simulator_constructed")
    stamp("before_run_submission")
    job = simulator.run(circuit, shots=64, seed_simulator=74730)
    stamp("run_returned_before_result_wait")
    result = job.result()
    stamp("result_returned")
    counts = result.get_counts()
    if not result.success or sum(counts.values()) != 64:
        raise RuntimeError("Synthetic shot accounting failed")
    report = {
        "kind": "synthetic_fixture_non_observation",
        "width": width,
        "layers": 4,
        "instructions": len(circuit.data),
        "options": trajectory_options(fusion=fusion),
        "seed_simulator": 74730,
        "shots": 64,
        "counts": counts,
        "stages": stages,
        "aer_time_taken_seconds": result.time_taken,
        "metadata": result.results[0].metadata,
        "versions": {
            name: importlib.metadata.version(name)
            for name in ("qiskit", "qiskit-aer", "numpy")
        },
        "snapshot": deepcopy(snapshot),
        "scope": "No frozen scientific gates/channels executed; not a runtime forecast",
    }
    write_new(output / "fixture.json", report)
    return report


def main() -> None:
    """Analyze saved bytes or profile a generated fixture; never replay science."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    subs = parser.add_subparsers(dest="command", required=True)
    analyze = subs.add_parser("analyze")
    analyze.add_argument("--evidence-root", type=Path, required=True)
    analyze.add_argument("--config", type=Path, required=True)
    probe = subs.add_parser("fixture")
    probe.add_argument("--width", type=int, choices=(3, 18), required=True)
    probe.add_argument("--fusion", action="store_true")
    args = parser.parse_args()
    inherited = source_contract()
    args.output.mkdir(exist_ok=False)
    write_new(args.output / "inherited-source-contract.json", inherited)
    if args.command == "analyze":
        write_new(
            args.output / "analysis.json",
            analyze_saved(args.evidence_root, json.loads(args.config.read_text())),
        )
    else:
        profile_fixture(args.output, args.width, args.fusion)


if __name__ == "__main__":
    main()

"""Routed NISQ metrics on a recorded device model with fixed transpiler seeds."""

import math
import statistics

from qiskit import QuantumCircuit, transpile
from qiskit.circuit import ControlledGate
from qiskit.circuit.library import RCCXGate

from .costs import is_mcx, weighted_depth

SEEDS = (11, 23, 37, 41, 53)
_IGNORED = ("barrier", "delay")


def default_backend():
    """The FakeTorino snapshot, matching the device of the archived experiments."""
    from qiskit_ibm_runtime.fake_provider import FakeTorino

    return FakeTorino()


def prelower(circuit: QuantumCircuit) -> QuantumCircuit:
    """Rewrite controlled Rx(±pi) gates with a relative-phase Toffoli and a CZ.

    CC-Rx(pi) equals a relative-phase Toffoli followed by CZ on its first
    control and target, which costs four two-qubit gates instead of the
    generic multi-controlled rotation synthesis. Multi-controlled X gates must
    already be expanded, so the decomposition policy stays explicit.
    """
    result = circuit.copy_empty_like()
    for inst in circuit.data:
        operation = inst.operation
        if is_mcx(operation, 3):
            raise ValueError("Expand multi-controlled X gates with decompose_mcx()")
        rotation = (
            isinstance(operation, ControlledGate)
            and operation.base_gate.name == "rx"
            and operation.num_ctrl_qubits == 2
            and math.isclose(
                abs(float(operation.base_gate.params[0])), math.pi, abs_tol=1e-12
            )
        )
        if not rotation:
            result.append(operation, inst.qubits, inst.clbits, copy=False)
            continue
        first, second, target = inst.qubits
        opened = [
            q
            for i, q in enumerate((first, second))
            if not (operation.ctrl_state >> i) & 1
        ]
        if opened:
            result.x(opened)
        if float(operation.base_gate.params[0]) > 0:
            result.append(RCCXGate(), [first, second, target])
            result.cz(first, target)
        else:
            result.cz(first, target)
            result.append(RCCXGate().inverse(), [first, second, target])
        if opened:
            result.x(opened)
    return result


def _seed_metrics(routed: QuantumCircuit, target) -> dict:
    two_qubit = {
        inst.operation.name
        for inst in routed.data
        if len(inst.qubits) == 2 and inst.operation.name not in _IGNORED
    }
    active = {
        routed.find_bit(q).index
        for inst in routed.data
        if inst.operation.name not in _IGNORED
        for q in inst.qubits
    }
    success = 1.0
    for inst in routed.data:
        name = inst.operation.name
        if name in _IGNORED or name not in target.operation_names:
            continue
        qargs = tuple(routed.find_bit(q).index for q in inst.qubits)
        properties = target[name].get(qargs)
        if properties is not None and properties.error is not None:
            success *= 1 - properties.error
    counts = {
        name: count
        for name, count in routed.count_ops().items()
        if name not in _IGNORED
    }
    return {
        "two_qubit_count": sum(counts.get(name, 0) for name in two_qubit),
        "two_qubit_depth": weighted_depth(routed, {name: 1 for name in two_qubit}),
        "depth": weighted_depth(routed, {}, default=1),
        "gates": sum(counts.values()),
        "active_qubits": len(active),
        "duration_s": routed.estimate_duration(target, unit="s"),
        "esp": success,
    }


def routed_metrics(
    circuit: QuantumCircuit,
    *,
    backend=None,
    seeds=SEEDS,
    optimization_level: int = 3,
) -> dict:
    """Route with each fixed seed and report the median and the best seed.

    Circuits wider than the device receive an explicit infeasibility label
    instead of routed values. The estimated success probability (ESP) is the
    product of one minus each calibrated gate error, readout included only
    when the circuit measures.
    """
    backend = default_backend() if backend is None else backend
    record = {
        "backend": backend.name,
        "backend_version": getattr(backend, "backend_version", None),
        "seeds": list(seeds),
        "optimization_level": optimization_level,
        "metric_level": "routed",
    }
    if circuit.num_qubits > backend.num_qubits:
        return {
            **record,
            "routed": False,
            "reason": f"needs {circuit.num_qubits} qubits; device has {backend.num_qubits}",
        }
    logical = prelower(circuit)
    per_seed = []
    for seed in seeds:
        routed = transpile(
            logical,
            backend=backend,
            optimization_level=optimization_level,
            seed_transpiler=seed,
            scheduling_method="alap",
        )
        per_seed.append({"seed": seed, **_seed_metrics(routed, backend.target)})
    summary = {
        key: statistics.median(row[key] for row in per_seed)
        for key in per_seed[0]
        if key != "seed"
    }
    best = min(per_seed, key=lambda row: (row["two_qubit_count"], row["depth"]))
    return {
        **record,
        "routed": True,
        **summary,
        "best_seed": best["seed"],
        "best_two_qubit_count": best["two_qubit_count"],
        "per_seed": per_seed,
    }

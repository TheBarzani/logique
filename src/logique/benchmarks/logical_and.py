"""Measurement-assisted uncomputation of temporary logical-AND gates.

Gidney's temporary logical-AND (arXiv:1709.06648) computes the AND of two
qubits into a clean qubit with four T gates and uncomputes it with an X-basis
measurement followed by a classically controlled CZ, which needs no T gate.
This module finds compute–uncompute pairs in a Toffoli-level circuit, rewrites
them as a dynamic circuit for verification, and prices them through a static
counting skeleton.
"""

from bisect import bisect_right
import math

from qiskit import ClassicalRegister, QuantumCircuit
from qiskit.circuit import ControlledGate
from qiskit.circuit.library import RXGate

from .costs import clifford_t, decompose_mcx, ft_metrics, is_mcx

_DIAGONAL = {
    "id",
    "z",
    "s",
    "sdg",
    "t",
    "tdg",
    "rz",
    "p",
    "u1",
    "cz",
    "cp",
    "crz",
    "cu1",
    "ccz",
    "cs",
    "csdg",
    "rzz",
    "mcphase",
}
_IGNORED = ("barrier", "delay")


def _and_gate(circuit: QuantumCircuit, inst):
    """Return (controls with polarity, target) for a two-control AND, else None."""
    operation = inst.operation
    wires = [circuit.find_bit(q).index for q in inst.qubits]
    if operation.name in ("rccx", "rccx_dg"):
        return frozenset({(wires[0], True), (wires[1], True)}), wires[2]
    if not isinstance(operation, ControlledGate) or operation.num_ctrl_qubits != 2:
        return None
    base = operation.base_gate
    if base.name == "rx" and not math.isclose(
        abs(float(base.params[0])), math.pi, abs_tol=1e-12
    ):
        return None
    if base.name not in ("x", "rx"):
        return None
    polarity = [bool((operation.ctrl_state >> i) & 1) for i in range(2)]
    return frozenset(zip(wires[:2], polarity)), wires[2]


def _written(circuit: QuantumCircuit, inst) -> set[int]:
    """Qubits whose computational-basis value the instruction may change."""
    operation = inst.operation
    wires = [circuit.find_bit(q).index for q in inst.qubits]
    name = operation.name
    if name in _IGNORED:
        return set()
    if name in ("rccx", "rccx_dg"):
        return {wires[2]}
    if isinstance(operation, ControlledGate):
        base = operation.base_gate.name
        return set() if base in _DIAGONAL else set(wires[operation.num_ctrl_qubits :])
    if name.split("_o")[0] in _DIAGONAL:
        return set()
    return set(wires)


def find_and_pairs(circuit: QuantumCircuit, *, clean_wires=(), restored_wires=None):
    """Pair each AND computed into a clean qubit with its uncomputation.

    ``clean_wires`` start in |0>; ``restored_wires`` (default: the clean wires)
    are guaranteed by the caller to end in |0>, as phase and restoration
    checks establish for synthesized oracles. A pair (i, j) needs the target of
    gate i to be clean before it and gate j to be the next write to that
    target, with the same controls and polarities. The target then holds the
    AND of the controls at i, and measuring it uncomputes correctly when that
    AND still equals the AND of the controls at j: the controls are unchanged
    in between, a classical simulation shows equal values, or j is the last
    write to a restored wire.
    """
    return _analyse(circuit, clean_wires, restored_wires)[0]


_SAMPLES = 1 << 16


def _simulate(circuit: QuantumCircuit, clean: set[int], candidates: dict):
    """Compare AND values at each candidate's computation and uncomputation.

    Wires outside ``clean`` take every value pattern when there are at most
    16 of them and 65,536 random patterns otherwise. Gates that leave the
    computational basis make their written wires unknown, and candidates that
    read an unknown wire are not confirmed.
    """
    import numpy as np

    free = [q for q in range(circuit.num_qubits) if q not in clean]
    exhaustive = len(free) <= 16
    count = max(1 << len(free), 64) if exhaustive else _SAMPLES
    rng = np.random.default_rng(7)
    values: dict[int, np.ndarray | None] = {}
    for position, q in enumerate(free):
        bits = (
            (np.arange(count) >> position) & 1
            if exhaustive
            else rng.integers(0, 2, count)
        )
        values[q] = np.packbits(bits.astype(bool))
    for q in clean:
        values[q] = np.zeros(count // 8, dtype=np.uint8)

    def conjunction(controls):
        result = None
        for q, positive in controls:
            if values[q] is None:
                return None
            value = values[q] if positive else ~values[q]
            result = value if result is None else result & value
        return result

    pending = {j: i for i, j in candidates.items()}
    stored = {}
    equal = set()
    for k, inst in enumerate(circuit.data):
        operation = inst.operation
        wires = [circuit.find_bit(q).index for q in inst.qubits]
        if k in candidates:
            stored[k] = conjunction(_and_gate(circuit, inst)[0])
        if k in pending:
            first = stored.pop(pending[k])
            last = conjunction(_and_gate(circuit, inst)[0])
            if first is not None and last is not None and np.array_equal(first, last):
                equal.add(pending[k])
        gate = _and_gate(circuit, inst)
        if gate is not None:
            flip = conjunction(gate[0])
            target = gate[1]
        elif isinstance(operation, ControlledGate) and operation.base_gate.name == "x":
            count_controls = operation.num_ctrl_qubits
            polarity = [
                bool((operation.ctrl_state >> i) & 1) for i in range(count_controls)
            ]
            flip = conjunction(list(zip(wires[:count_controls], polarity)))
            target = wires[-1]
        elif operation.name == "x":
            flip, target = np.full(count // 8, 255, dtype=np.uint8), wires[0]
        elif operation.name == "swap":
            values[wires[0]], values[wires[1]] = values[wires[1]], values[wires[0]]
            continue
        elif operation.name == "reset":
            values[wires[0]] = np.zeros(count // 8, dtype=np.uint8)
            continue
        else:
            for q in _written(circuit, inst):
                values[q] = None
            continue
        if flip is None or values[target] is None:
            values[target] = None
        else:
            values[target] = values[target] ^ flip
    return equal, "exhaustive" if exhaustive else f"sampled ({_SAMPLES} inputs)"


def _analyse(circuit: QuantumCircuit, clean_wires, restored_wires):
    if any(is_mcx(inst.operation, 3) for inst in circuit.data):
        raise ValueError("Expand multi-controlled X gates with decompose_mcx()")
    index = {q: circuit.find_bit(q).index for q in circuit.qubits}
    clean = {index[q] if not isinstance(q, int) else q for q in clean_wires}
    restored = (
        set(clean)
        if restored_wires is None
        else {index[q] if not isinstance(q, int) else q for q in restored_wires}
    )
    writes: dict[int, list[int]] = {}
    for k, inst in enumerate(circuit.data):
        for q in _written(circuit, inst):
            writes.setdefault(q, []).append(k)

    def next_write(q: int, k: int) -> int | None:
        positions = writes.get(q, [])
        found = bisect_right(positions, k)
        return positions[found] if found < len(positions) else None

    def unchanged(q: int, start: int, stop: int) -> bool:
        positions = writes.get(q, [])
        return bisect_right(positions, start) == bisect_right(positions, stop - 1)

    # Structural candidates: the next write to an AND's target is the same AND.
    candidates = {}
    for k, inst in enumerate(circuit.data):
        gate = _and_gate(circuit, inst)
        if gate is None:
            continue
        j = next_write(gate[1], k)
        if j is not None and _and_gate(circuit, circuit.data[j]) == gate:
            candidates[k] = j
    simulated, check = _simulate(circuit, set(clean), candidates)

    pairs = {}
    uncomputes = set()
    for k, inst in enumerate(circuit.data):
        gate = _and_gate(circuit, inst)
        if k in uncomputes:
            clean.add(gate[1])
            continue
        if k in candidates and gate[1] in clean:
            j = candidates[k]
            if (
                all(unchanged(q, k, j) for q, _ in gate[0])
                or k in simulated
                or (writes[gate[1]][-1] == j and gate[1] in restored)
            ):
                pairs[k] = j
                uncomputes.add(j)
                clean.discard(gate[1])
                continue
        clean.difference_update(_written(circuit, inst))
    return pairs, check


def measurement_assisted(
    circuit: QuantumCircuit, *, clean_wires=(), restored_wires=None
) -> tuple[QuantumCircuit, QuantumCircuit, dict]:
    """Rewrite paired ANDs with measurement-based uncomputation.

    Returns the dynamic circuit, a static counting skeleton in which each
    measurement and classically controlled CZ is replaced by an unconditional
    Clifford stand-in, and a summary. Each paired computation becomes an exact
    logical-AND, a doubly controlled Rx(pi) followed by S on the clean target,
    which costs four T gates.
    """
    pairs, check = _analyse(circuit, clean_wires, restored_wires)
    uncomputes = set(pairs.values())
    dynamic = circuit.copy_empty_like()
    skeleton = circuit.copy_empty_like()
    bits = ClassicalRegister(len(pairs), "and_uncompute") if pairs else None
    if bits is not None:
        dynamic.add_register(bits)
    measured = 0
    level = [0] * circuit.num_qubits
    for k, inst in enumerate(circuit.data):
        wires = [circuit.find_bit(q).index for q in inst.qubits]
        if inst.operation.name not in _IGNORED and wires:
            step = max(level[w] for w in wires) + (k in uncomputes)
            for w in wires:
                level[w] = step
        if k not in pairs and k not in uncomputes:
            dynamic.append(inst.operation, inst.qubits, inst.clbits, copy=False)
            skeleton.append(inst.operation, inst.qubits, inst.clbits, copy=False)
            continue
        controls, target = _and_gate(circuit, inst)
        controls = sorted(controls)
        opened = [circuit.qubits[q] for q, positive in controls if not positive]
        first, second = (circuit.qubits[q] for q, _ in controls)
        qubit = circuit.qubits[target]
        if k in pairs:
            for out in (dynamic, skeleton):
                if opened:
                    out.x(opened)
                out.append(RXGate(math.pi).control(2), [first, second, qubit])
                out.s(qubit)
                if opened:
                    out.x(opened)
            continue
        dynamic.h(qubit)
        dynamic.measure(qubit, bits[measured])
        with dynamic.if_test((bits[measured], 1)):
            if opened:
                dynamic.x(opened)
            dynamic.cz(first, second)
            if opened:
                dynamic.x(opened)
            dynamic.x(qubit)
        measured += 1
        skeleton.h(qubit)
        if opened:
            skeleton.x(opened)
        skeleton.cz(first, second)
        if opened:
            skeleton.x(opened)
    info = {
        "and_pairs": len(pairs),
        "measurements": len(pairs),
        "classically_controlled_cz": len(pairs),
        "reaction_depth": max(level, default=0),
        "pair_check": check,
    }
    return dynamic, skeleton, info


def measurement_assisted_metrics(
    circuit: QuantumCircuit,
    *,
    clean_wires=(),
    restored_wires=None,
    rotation_t: int | None = None,
) -> dict:
    """Fault-tolerant counts when paired ANDs are uncomputed by measurement.

    Reported separately from static costs: these circuits need mid-circuit
    measurement, classically controlled gates and a reaction time per
    feedforward step, which ``reaction_depth`` counts on the critical path.
    """
    _, skeleton, info = measurement_assisted(
        circuit, clean_wires=clean_wires, restored_wires=restored_wires
    )
    metrics = ft_metrics(clifford_t(skeleton), rotation_t=rotation_t)
    return {**metrics, **info, "metric_level": "fault-tolerant, measurement-assisted"}


def isolated_mcx_assisted_costs(method: str, controls: int) -> dict:
    """Cost one decomposed MCX gate when its clean ancillas are measured away.

    Uses the same circuit as ``costs.isolated_mcx_costs``: the controls, the
    target and controls - 2 spare wires. Only appended ancillas count as
    clean, so conditionally clean wires keep their unitary uncomputation.
    """
    circuit = QuantumCircuit(2 * controls - 1)
    circuit.mcx(list(range(controls)), controls)
    decomposed, info = decompose_mcx(circuit, method)
    ancillas = list(range(circuit.num_qubits, decomposed.num_qubits))
    metrics = measurement_assisted_metrics(decomposed, clean_wires=ancillas)
    return {
        "method": f"{method} + measurement",
        "controls": controls,
        "workspace": info["mcx_workspace"],
        "ancillas": info["appended_ancillas"] + info["borrowed_dirty_wires"],
        **{
            key: metrics[key]
            for key in (
                "t_count",
                "t_depth",
                "rotation_count",
                "cx_count",
                "and_pairs",
                "measurements",
                "reaction_depth",
                "pair_check",
            )
        },
        "reference": f"{info['mcx_reference']}; Gidney, arXiv:1709.06648",
        "metric_level": "explicit, measurement-assisted",
    }
